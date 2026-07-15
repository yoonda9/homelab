"""Shape tests for the Plex state-dir bind-mount ownership under the CT 110 idmap.

Regression guard for the confirmed root cause behind DEBUG.md's "Plex service
failure": the read-write state-dir bind mount (`tofu/main.tf` module "plex",
`/tank/Server/AppData/plex` -> `/var/lib/plexmediaserver`) was backed by a host
directory carrying **raw in-CT ownership** (base `0:0`, Library subtree
`999:991`) instead of idmap-shifted ownership. CT 110 is unprivileged and its
uid map is a single offset tile (`u 0 100000 65536`), so the mapped uid range is
`[100000, 165536)`; both `0:0` and `999:991` fall outside it and surface in-CT
as `65534:65534` (nobody). (The *gid* map is tiled rather than single —
`tofu/locals.tf` punches the GPU GIDs 44/993 through 1:1 — but `991` sits in an
offset tile, so the same +100000 shift applies to it.) In-CT `plex` (uid=999
**gid=991**) is then neither
owner nor group on mode `0755`, keeps only `other` `r-x`, and PMS aborts in
~17ms with "Read/write access is required for path: ...".

The load-bearing detail this file exists to pin: **uid and gid are allocated
independently and are NOT equal here** (999 vs 991). `docs/runbooks/plex-claim.md`
§5 used to say `chown -R $((100000 + 999)):$((100000 + 999))` and
`# e.g. uid=999(plex) gid=999(plex)`, both of which assume `uid == gid` and so
reproduce this very bug when followed literally.

Verified surfaces:

  * `roles/plex/defaults/main.yml` carries `plex_uid` and `plex_gid` as separate
    integer keys (neither derived from the other);
  * `roles/plex/tasks/main.yml` pins the group GID from `plex_gid` and the user
    UID from `plex_uid` **before** the `plexmediaserver` package install, so the
    package cannot auto-allocate drifting ids;
  * that role asserts the state dir's uid AND gid independently, and does so
    **before** the package install / service start, so a raw-ownership host dir
    fails the play loudly with the host-side `chown` to run instead of leaving
    PMS crash-looping;
  * `docs/runbooks/plex-claim.md` reads `id -u` and `id -g` separately and never
    emits a collapsed `uid == gid` chown;
  * the id-migration machinery (design §4.2): the early `stat` and the stop
    precede the id pins, the `chown -R` precedes the ownership gate, and the
    `plex_chown_needed` derivation answers the §6.3 state table correctly — the
    last of these evaluated BEHAVIOURALLY, through ansible-core's own Jinja2,
    because every ordering assertion above also passes against the rejected
    design that wedges (§7.1).

Follows the repo's dual-mode shape-test convention (see
`test_ansible_layout_shape.py`, `test_traefik_config_shape.py`): module-level
`test_<name>() -> bool` functions that print `OK` / `FAIL: ...` (no `assert`),
plus `main() -> int` that sums the booleans and `sys.exit`s non-zero on any
failure. Regexes anchor on the inner content (mem-1781892715-142d), so a comment
or an empty stub cannot satisfy a check. The real gate is the standalone exit
code.

The shape/ordering checks are stdlib-only, per the repo rule that the gate
pythons have no PyYAML (mem-1782133401-4307). The behavioural half is the
documented exception: it needs ansible-core's real Templar, which the gate's
python cannot import, so this file RE-EXECS itself under a discovered
ansible-capable interpreter (which ships PyYAML) rather than skipping. It must
never skip — see the C-2 block below for why that would be green-but-vacuous.
"""

import os
import pathlib
import re
import subprocess
import sys

# --- C-2: this file re-execs itself; it MUST NOT skip -----------------------
# The behavioural half below (the §6.3 state table) evaluates the role's real
# Jinja2 through ansible-core's own Templar, but `run_gate.py:56` runs every
# shape-test as `[sys.executable, path]` — the repo `.venv` python. ansible-core
# is a pipx install (`mise.toml:24`) and pipx venvs are isolated (only their CLIs
# reach PATH), so that interpreter CANNOT import ansible.
#
# The repo idiom for an absent tool is `OK (skip): not installed -> return True`
# (`test_build_template_runner.py:52-57`). It does NOT transfer here, and reaching
# for it would make this file green while proving nothing about R9 — the same
# vacuous-green failure this file already suffered once (mem-1784124801-dc35),
# reintroduced inside the very test written to end it. The argument is measurable,
# not principled: `shellcheck`/`shfmt` are genuinely absent from `[tools]` and
# optional, whereas ansible-core is PINNED and the gate ALREADY hard-depends on it
# (`run_gate.py:67-68`) — any env without it already fails `just test`. A skip here
# buys zero portability, so this hard-FAILs at no cost.
#
# The import is keyed on `ansible.template`, NEVER on a bare `import ansible`:
# `ansible` is a PEP-420 namespace-package trap — whenever the repo root is on
# sys.path, `import ansible` SUCCEEDS, resolving to this repo's own `ansible/`
# CONFIG directory (`__file__=None`), and only then fails on `ansible.template`. A
# guard keyed on the bare import would not fire — a check passing over the very
# condition it guards, inside its own fix.
# `ansible.template` is imported FIRST, deliberately: it is the symbol §7.1
# actually needs, so the guard keys on it and its failure names the real
# condition. (PyYAML rides along with ansible-core, but if it were checked first
# the guard would report a missing `yaml` — inviting the next reader to "fix"
# that with a stdlib fallback and quietly stop the guard firing on the import
# that matters.)
try:
    from ansible.template import Templar, trust_as_template
    from ansible.parsing.dataloader import DataLoader
    import yaml

    ANSIBLE_IMPORT_ERROR = None
except ImportError as exc:  # pragma: no cover - exercised by the gate's python
    ANSIBLE_IMPORT_ERROR = str(exc)

REEXEC_FLAG = "_PLEX_SHAPE_REEXEC"

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PLEX_ROLE = REPO_ROOT / "ansible" / "roles" / "plex"
PLEX_DEFAULTS = PLEX_ROLE / "defaults" / "main.yml"
PLEX_TASKS = PLEX_ROLE / "tasks" / "main.yml"
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "plex-claim.md"

INSTALL_TASK = "Install Plex Media Server"

# The migration machinery (design §4.2). Named here so a task rename is a single
# edit and so the ordering checks below read as the sequence they assert.
EARLY_STAT_TASK = "Stat the Plex state directory before the id pins"
DERIVE_TASK = "Derive whether the state directory needs an ownership migration"
STOP_TASK = "Stop Plex Media Server before an id migration"
CHOWN_TASK = "Migrate state dir ownership to the pinned ids"
GROUP_PIN_TASK = "Pin the plex group GID ahead of the package install"
USER_PIN_TASK = "Pin the plex user UID ahead of the package install"
GATE_STAT_TASK = "Stat the Plex state directory (the host bind mount lands here)"
GATE_ASSERT_TASK = "Assert the Plex state directory carries idmap-shifted ownership"

PREDICATE_FACT = "plex_chown_needed"
EARLY_STAT_REGISTER = "plex_state_premigration_stat"

# The migration's target ids (design §A.1). The §6.3/§7.1 state table is written
# against these, NOT against whatever `defaults/main.yml` currently pins: its rows
# are labelled "999:991 = migration run" and "64000:64000 = steady state", which
# only hold when plex_uid/plex_gid ARE the target. Binding the ids from the
# fixture (rather than from defaults) is what keeps this table meaningful in
# Step 1 — where defaults are still 999/991, so a defaults-bound table would
# invert — and unchanged through Step 2's flip. The defaults are read and pinned
# by test_predicate_is_inert_at_the_current_defaults() instead.
TARGET_UID = 64000
TARGET_GID = 64000

# TARGET_UID == TARGET_GID, so every row of that table binds `plex_uid` and
# `plex_gid` to the SAME integer and no row can tell the two names apart: collapse
# the predicate's gid half onto plex_uid — this repo's signature historic defect,
# the one test_runbook_has_no_uid_equals_gid_chown exists to prevent — and the
# whole table stays green. These ids are the fixture that CAN tell them apart, and
# they are literals for a reason. The only other asymmetric binding in this file
# reads plex_uid/plex_gid LIVE from defaults/main.yml, which makes its
# discrimination an accident of today's values: Step 2's entire content is flipping
# those to 64000/64000, and the collapse then goes green (verified by execution —
# RED 16/17 at 999/991, GREEN 17/17 at 64000/64000, same test, no edit). A guard
# whose fixture comes from config is armed only until the config moves.
PROBE_UID = 64000
PROBE_GID = 991


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _ansible_python():
    """Discover the interpreter that can import ansible-core, else (None, why).

    Asks the toolchain rather than hardcoding: `mise.toml:24` pins ansible-core to
    `latest`, so the version component of the pipx venv path ROTATES (this box
    already carries two). A hardcoded path is the de-numbering mistake (§4.2.2) in
    filesystem form.
    """
    try:
        out = subprocess.run(
            ["mise", "exec", "--", "ansible", "--version"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_ROOT,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"could not run `ansible --version`: {exc}"
    # `ansible --version` prints: python version = 3.14.6 (...) (/path/to/python)
    match = re.search(
        r"^\s*python version\s*=.*\((/\S*python[0-9.]*)\)\s*$", out, re.MULTILINE
    )
    if not match:
        return None, "could not parse the interpreter from `ansible --version`"
    return match.group(1), None


def _reexec_under_ansible_python() -> int:
    """Re-run this file under an ansible-capable interpreter; propagate its code."""
    if os.environ.get(REEXEC_FLAG):
        print(
            f"FAIL: re-exec loop — `ansible.template` still unimportable under "
            f"{sys.executable} ({ANSIBLE_IMPORT_ERROR})"
        )
        return 1
    interpreter, error = _ansible_python()
    if interpreter is None:
        # The load-bearing choice: FAIL, never `return True`. See the header.
        print(f"FAIL: no ansible-core interpreter found — {error}")
        return 1
    print(f"re-exec: {sys.executable}\n     ->  {interpreter}")
    env = dict(os.environ)
    env[REEXEC_FLAG] = "1"
    return subprocess.run(
        [interpreter, str(pathlib.Path(__file__).resolve())], env=env
    ).returncode


def _scalar(text: str, key: str):
    """Return the int value of a top-level `key: <int>` line, else None."""
    match = re.search(rf"^{re.escape(key)}:\s*(\d+)\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def _task_index(text: str, name: str):
    """Return the character offset of the `- name: <name>` task header, else None."""
    match = re.search(rf"^-\s+name:\s*{re.escape(name)}\s*$", text, re.MULTILINE)
    return match.start() if match else None


def _task_body(text: str, name: str):
    """Return the source of one task: its `- name:` header to the next task's."""
    start = _task_index(text, name)
    if start is None:
        return None
    rest = text[start + 1:]
    following = re.search(r"^-\s+name:", rest, re.MULTILINE)
    return text[start: start + 1 + following.start()] if following else text[start:]


def _ordered(text: str, earlier: str, later: str):
    """Return (ok, detail) for `earlier` preceding `later` in file order."""
    first, second = _task_index(text, earlier), _task_index(text, later)
    if first is None or second is None:
        missing = [n for n, i in ((earlier, first), (later, second)) if i is None]
        return None, f"task(s) not found: {missing}"
    return first < second, f"{earlier!r}@{first} vs {later!r}@{second}"


# --- Behavioural half: resolve the REAL predicate (§7.1) --------------------
# PyYAML ships with ansible-core, so it is importable only after the re-exec
# above — which is exactly where these helpers run. The stdlib-only rule
# (mem-1782133401-4307) exists because the GATE pythons lack PyYAML; the four
# shape/ordering checks above stay stdlib+regex and are bound by it.


def _role_tasks():
    """Parse the role's task list from the real file."""
    return yaml.safe_load(_read(PLEX_TASKS)) or []


def _named(tasks, name):
    for task in tasks:
        if isinstance(task, dict) and task.get("name") == name:
            return task
    return None


def _set_fact_expression():
    """Read the expression defining plex_chown_needed from its single site.

    The chown's real `when:` is the bare token `plex_chown_needed`, so evaluating
    THAT proves nothing (R13). DEC-007 gives the derivation exactly one address —
    this reads it, rather than restating it in Python, because a restated
    predicate tests the test.
    """
    task = _named(_role_tasks(), DERIVE_TASK)
    if task is None:
        return None
    return (task.get("ansible.builtin.set_fact") or {}).get(PREDICATE_FACT)


def _when_expression(name: str):
    """Return a task's real `when:` as a single expression string."""
    task = _named(_role_tasks(), name)
    if task is None or "when" not in task:
        return None
    when = task["when"]
    # A list `when:` is ANDed by Ansible; join so it evaluates identically.
    if isinstance(when, list):
        return " and ".join(f"({item})" for item in when)
    return when


def _evaluate(expression: str, variables: dict):
    """Evaluate a role expression through ansible-core's own Jinja2.

    `trust_as_template` is mandatory, not ceremony: under ansible-core 2.19+ data
    tagging, Templar.template() SILENTLY RETURNS THE RAW STRING for an untrusted
    template — it neither renders nor raises — so an untrusted call yields the
    truthy CONSTANT "{{ ... }}" on every fixture row (mem-1784135461-a8eb).
    Variables bind at CONSTRUCTION; template() takes no `variables=` kwarg
    (mem-1784136261-1371).
    """
    templar = Templar(loader=DataLoader(), variables=variables)
    return templar.template(trust_as_template(expression))


def _evaluate_condition(expression: str, variables: dict):
    """Evaluate a `when:` the way Ansible does — as an IMPLICIT expression.

    A `when:` carries no `{{ }}`: it *is* the expression, so it must be wrapped
    before templating. Templating it bare returns the raw string, which is TRUTHY
    — and therefore reads as a pass on every row that expects True, while only the
    False rows expose it. That is the same vacuous-green shape as the untrusted
    template above, and it is why the state table asserts BOTH polarities and
    demands real bools rather than truthiness.
    """
    return _evaluate("{{ " + expression + " }}", variables)


def _passwd(uid: int, gid: int):
    """A getent passwd entry as the module really returns it (verified live).

    `ansible.builtin.getent` drops the name and returns the REMAINING fields, so
    index 1 is the uid — not index 2.
    """
    return ["x", str(uid), str(gid), "", "/var/lib/plexmediaserver", "/usr/sbin/nologin"]


def _fixture_vars(stat: dict, passwd, uid: int, gid: int) -> dict:
    """Bind a fixture the way the role's own early stat and getent register it.

    Both facts are bound for BOTH predicates, deliberately: it is what lets the
    getent-keyed derivation (the rejected design) resolve to a real FALSE at the
    64000:991 row rather than raising an undefined-variable error. The table must
    fail that design on its ANSWER, not on a missing binding.
    """
    return {
        EARLY_STAT_REGISTER: {"stat": stat},
        "plex_uid": uid,
        "plex_gid": gid,
        "plex_service_user": "plex",
        "ansible_facts": {"getent_passwd": {"plex": passwd}},
    }


def _resolve_chown_needed(stat: dict, passwd, uid: int, gid: int):
    """Evaluate the role's real set_fact expression against a fixture."""
    expression = _set_fact_expression()
    if expression is None:
        return None, f"no `{PREDICATE_FACT}` set_fact found in task {DERIVE_TASK!r}"
    try:
        return _evaluate(expression, _fixture_vars(stat, passwd, uid, gid)), None
    except Exception as exc:  # noqa: BLE001 - the absent row asserts "does not raise"
        return None, f"{type(exc).__name__}: {exc}"


# The design §6.3 state table, verbatim, evaluated at the migration's target ids:
# (label, getent entry for plex (None = user absent), dir stat, chown_needed, stop).
# §7.1's four-row chown_needed table is the `chown_needed` column of this one.
STATE_TABLE = [
    (
        "fresh rebuild (user absent, dir 64000:64000)",
        None,
        {"exists": True, "uid": TARGET_UID, "gid": TARGET_GID},
        False,
        False,
    ),
    (
        "steady state (user 64000, dir 64000:64000)",
        _passwd(TARGET_UID, TARGET_GID),
        {"exists": True, "uid": TARGET_UID, "gid": TARGET_GID},
        False,
        False,
    ),
    (
        "migration run (user 999, dir 999:991)",
        _passwd(999, 991),
        {"exists": True, "uid": 999, "gid": 991},
        True,
        True,
    ),
    (
        # The row that tells the accepted design from the rejected one: the user's
        # uid ALREADY reads 64000, so a getent-keyed predicate answers FALSE here
        # and wedges a half-migrated dir at 64000:991 permanently.
        "interrupted recovery (user 64000, dir 64000:991)",
        _passwd(TARGET_UID, 991),
        {"exists": True, "uid": TARGET_UID, "gid": 991},
        True,
        True,
    ),
    (
        # The ONLY row where composition and substitution DISAGREE, and the sole
        # thing guarding the stop's `or plex_chown_needed` widening: the dir is
        # already at the target while the user is NOT, so chown_needed is FALSE
        # and a stop substituted with the bare fact skips — leaving PMS live for
        # a `usermod -u` that then refuses (F1) and fails the play. Without this
        # row every other row has stop == chown_needed, so the rejected design
        # passes too.
        #
        # Reachable by the CAUTIOUS operator's path — snapshot, migrate, roll back:
        # `docs/runbooks/plex-claim.md:88` records that Proxmox vzdump EXCLUDES bind
        # mounts from CT backups, so a rollback reverts /etc/passwd (rootfs) to 999
        # while the bind mount KEEPS the migrated 64000:64000. That is this row
        # exactly. It is NOT reachable via the host-side chown of `fail_msg`, which
        # an earlier version of this comment claimed: that message sits downstream
        # of the UNCONDITIONAL user pin, so anyone who reads it already has plex at
        # plex_uid and their re-run lands on steady state. Stated precisely because
        # this comment is the row's only reason to exist, and the row is the sole
        # guard against the rejected design — a maintainer who checks a false
        # citation deletes the row in two minutes.
        "host-side recovery (user 999, dir already 64000:64000)",
        _passwd(999, 991),
        {"exists": True, "uid": TARGET_UID, "gid": TARGET_GID},
        False,
        True,
    ),
    (
        # Must be FALSE *and* must not raise (R12): `| default(0)` answers TRUE
        # here and a bare `stat.uid != ...` raises.
        "state dir absent (bind mount missing)",
        _passwd(TARGET_UID, TARGET_GID),
        {"exists": False},
        False,
        False,
    ),
]


def _chown_spec(line: str):
    """Return the `owner:group` argument of a `chown` command line, else None.

    Reads the argument as a shell token rather than as a run of non-space
    characters: a `$(( ... ))` / `$( ... )` group is opaque, so the spaces the
    runbook writes inside its arithmetic stay part of the token. The predecessor
    guard keyed on `(\\S+?):(\\S+?)`, which cannot span those spaces, so it
    matched neither the defect nor the fix and only ever compared bare-numeric
    chowns — it went vacuously green over the exact line it was written to
    reject. Parsing the token is what makes the spelling irrelevant.
    """
    match = re.search(r"\bchown\b", line)
    if not match:
        return None
    rest = line[match.end():]
    index, end = 0, len(rest)
    # Skip the option flags (-R, -h, --reference=..., ...) ahead of the spec.
    while index < end:
        while index < end and rest[index].isspace():
            index += 1
        if index < end and rest[index] == "-":
            while index < end and not rest[index].isspace():
                index += 1
            continue
        break
    start, depth = index, 0
    while index < end:
        char = rest[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char.isspace() and depth == 0:
            break
        index += 1
    return rest[start:index] or None


def _normalise_half(half: str) -> str:
    """Strip quoting and insignificant whitespace so spellings compare equal."""
    return re.sub(r"\s+", "", half).strip("\"'")


def _chown_halves(line: str):
    """Return a chown's (owner, group) halves, normalised for comparison."""
    spec = _chown_spec(line)
    if spec is None:
        return None
    depth = 0
    for index, char in enumerate(spec):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == ":" and depth == 0:
            # Split on the top-level colon only: the one inside `$(( ))` (if a
            # spec ever grows one) is arithmetic, not the owner/group separator.
            return (
                _normalise_half(spec[:index]),
                _normalise_half(spec[index + 1:]),
            )
    return None


def test_plex_uid_and_gid_pinned_independently() -> bool:
    """defaults carry plex_uid and plex_gid as separate ints (uid != gid is real here)."""
    text = _read(PLEX_DEFAULTS)
    uid = _scalar(text, "plex_uid")
    gid = _scalar(text, "plex_gid")
    # Both keys must exist as literal ints. We deliberately do NOT assert the
    # exact 999/991 values (a CT rebuild may re-pin them) — only that the two are
    # independent knobs, which is what the uid==gid bug collapsed.
    ok = uid is not None and gid is not None
    independent = ok and not re.search(
        r"^plex_gid:\s*.*plex_uid", text, re.MULTILINE
    )
    if ok and independent:
        print(f"OK: plex_uid={uid} and plex_gid={gid} pinned as independent ints")
        return True
    print(
        f"FAIL: defaults must pin plex_uid and plex_gid as separate ints "
        f"(uid={uid}, gid={gid}, independent={independent})"
    )
    return False


def test_uid_gid_pinned_before_package_install() -> bool:
    """The group/user pins precede the plexmediaserver apt task, so ids cannot drift."""
    text = _read(PLEX_TASKS)
    install_at = _task_index(text, INSTALL_TASK)
    if install_at is None:
        print(f"FAIL: task '{INSTALL_TASK}' not found in {PLEX_TASKS.name}")
        return False
    head = text[:install_at]
    # Anchor on the module + the value actually wired, not just a task name.
    group_pinned = re.search(
        r"ansible\.builtin\.group:.*?\n(?:\s+.*\n)*?\s+gid:\s*[\"']?\{\{\s*plex_gid\s*\}\}",
        head,
    )
    user_pinned = re.search(
        r"ansible\.builtin\.user:.*?\n(?:\s+.*\n)*?\s+uid:\s*[\"']?\{\{\s*plex_uid\s*\}\}",
        head,
    )
    if group_pinned and user_pinned:
        print("OK: plex gid/uid pinned before the plexmediaserver install")
        return True
    print(
        f"FAIL: plex gid/uid must be pinned BEFORE '{INSTALL_TASK}' "
        f"(group_pinned={bool(group_pinned)}, user_pinned={bool(user_pinned)})"
    )
    return False


def test_state_dir_ownership_asserted() -> bool:
    """The role asserts the state dir's uid AND gid against the pinned ids."""
    text = _read(PLEX_TASKS)
    has_stat = re.search(
        r"ansible\.builtin\.stat:\s*\n\s+path:\s*[\"']?\{\{\s*plex_state_dir\s*\}\}",
        text,
    )
    # Both comparisons must be present and must key off the SEPARATE vars — an
    # assert that only checked uid (or compared gid against plex_uid) would let
    # the original bug through.
    uid_checked = re.search(
        r"stat\.uid\s*\|\s*int\s*==\s*plex_uid\s*\|\s*int", text
    )
    gid_checked = re.search(
        r"stat\.gid\s*\|\s*int\s*==\s*plex_gid\s*\|\s*int", text
    )
    if has_stat and uid_checked and gid_checked:
        print("OK: state-dir ownership asserted on uid AND gid independently")
        return True
    print(
        f"FAIL: role must stat plex_state_dir and assert uid==plex_uid and "
        f"gid==plex_gid (stat={bool(has_stat)}, uid={bool(uid_checked)}, "
        f"gid={bool(gid_checked)})"
    )
    return False


def test_ownership_gate_precedes_install() -> bool:
    """The ownership assert runs before the install/start, so the play fails fast."""
    text = _read(PLEX_TASKS)
    install_at = _task_index(text, INSTALL_TASK)
    assert_at = _task_index(
        text, "Assert the Plex state directory carries idmap-shifted ownership"
    )
    if install_at is None or assert_at is None:
        print(
            f"FAIL: need both the ownership assert and '{INSTALL_TASK}' tasks "
            f"(assert={assert_at is not None}, install={install_at is not None})"
        )
        return False
    if assert_at < install_at:
        print("OK: the state-dir ownership gate precedes the plexmediaserver install")
        return True
    print("FAIL: the ownership gate must run BEFORE the plexmediaserver install")
    return False


def test_fail_msg_names_the_host_side_chown() -> bool:
    """The fail_msg prints the shifted chown, built from BOTH ids, for the host."""
    text = _read(PLEX_TASKS)
    # The remediation is host-side only (in-CT root cannot chown unmapped ids),
    # so the message has to hand the operator the exact command.
    #
    # `| int` on every operand is load-bearing, not decoration: `that:` coerces
    # its own comparisons, but this arithmetic is the ONLY place fail_msg does
    # math, and fail_msg renders ONLY on the failing-ownership path. A string
    # override (`-e plex_uid=999`, or a quoted group_vars value) would raise
    # "unsupported operand type(s) for +" exactly when the operator needs the
    # chown, turning the gate's payload into a template crash.
    chown_uid = re.search(
        r"plex_idmap_base\s*\|\s*int\s*\)?\s*\+\s*\(?\s*plex_uid\s*\|\s*int", text
    )
    chown_gid = re.search(
        r"plex_idmap_base\s*\|\s*int\s*\)?\s*\+\s*\(?\s*plex_gid\s*\|\s*int", text
    )
    names_host_path = re.search(r"\{\{\s*plex_state_host_path\s*\}\}", text)
    mentions_chown = "chown -R" in text
    if chown_uid and chown_gid and names_host_path and mentions_chown:
        print("OK: fail_msg names the host-side chown with both shifted ids")
        return True
    print(
        f"FAIL: fail_msg must name `chown -R <base+uid>:<base+gid> "
        f"<plex_state_host_path>` (uid={bool(chown_uid)}, gid={bool(chown_gid)}, "
        f"path={bool(names_host_path)}, chown={mentions_chown})"
    )
    return False


def test_runbook_reads_uid_and_gid_separately() -> bool:
    """plex-claim.md §5 reads `id -u` and `id -g` rather than one `id plex`."""
    text = _read(RUNBOOK)
    reads_uid = re.search(r"id\s+-u\s+plex", text)
    reads_gid = re.search(r"id\s+-g\s+plex", text)
    if reads_uid and reads_gid:
        print("OK: plex-claim.md reads the uid and the gid separately")
        return True
    print(
        f"FAIL: plex-claim.md must read `id -u plex` and `id -g plex` separately "
        f"(uid={bool(reads_uid)}, gid={bool(reads_gid)})"
    )
    return False


def test_runbook_has_no_uid_equals_gid_chown() -> bool:
    """No chown in the runbook may reuse one id for both owner and group.

    This is the exact defect: `chown -R $((100000 + 999)):$((100000 + 999))`
    silently assumes uid == gid, which is false for CT 110 (999 vs 991), so an
    operator following the runbook literally reproduces the bug.
    """
    text = _read(RUNBOOK)
    parsed, offenders = [], []
    for line in text.splitlines():
        # Compare the owner and group halves textually: identical halves are the
        # uid==gid collapse, whatever the spelling ($(( )) arithmetic, shell
        # vars, or bare numerics).
        halves = _chown_halves(line)
        if halves is None:
            continue
        parsed.append(line.strip())
        if halves[0] == halves[1]:
            offenders.append(line.strip())
    # Non-vacuous on BOTH counts: the runbook must still carry a chown to gate
    # on, and this check must have actually parsed its halves. Requiring a real
    # parse is the load-bearing half — a parser that silently matches nothing is
    # precisely how the predecessor guard stayed green over the defect line.
    if parsed and not offenders:
        print(f"OK: no uid==gid chown remains in plex-claim.md ({len(parsed)} parsed)")
        return True
    print(
        f"FAIL: plex-claim.md chown must use the uid and gid independently "
        f"(parsed={parsed}, offenders={offenders})"
    )
    return False


# --- Step 1: the id-migration machinery (design §4.2, §7.1) -----------------


def test_early_stat_precedes_the_id_pins() -> bool:
    """The predicate's stat runs BEFORE the pins rewrite what it reads (§4.2)."""
    text = _read(PLEX_TASKS)
    body = _task_body(text, EARLY_STAT_TASK)
    if body is None:
        print(f"FAIL: task '{EARLY_STAT_TASK}' not found in {PLEX_TASKS.name}")
        return False
    # Anchor on the module + the register actually wired, not the task name alone.
    stats_the_dir = re.search(
        r"ansible\.builtin\.stat:\s*\n\s+path:\s*[\"']?\{\{\s*plex_state_dir\s*\}\}",
        body,
    )
    registers = re.search(rf"register:\s*{re.escape(EARLY_STAT_REGISTER)}\s*$", body, re.MULTILINE)
    before_group, group_detail = _ordered(text, EARLY_STAT_TASK, GROUP_PIN_TASK)
    before_user, user_detail = _ordered(text, EARLY_STAT_TASK, USER_PIN_TASK)
    if stats_the_dir and registers and before_group and before_user:
        print("OK: the early stat of plex_state_dir precedes both id pins")
        return True
    print(
        f"FAIL: the early stat must stat plex_state_dir, register "
        f"{EARLY_STAT_REGISTER}, and precede BOTH pins — `usermod -u` auto-chowns "
        f"the home tree, so a stat after the pins reads a fact the guarded "
        f"operation already rewrote (stat={bool(stats_the_dir)}, "
        f"register={bool(registers)}, {group_detail}, {user_detail})"
    )
    return False


def test_stop_precedes_the_id_pins() -> bool:
    """PMS is stopped before the pins: usermod refuses while the user owns procs (F1)."""
    text = _read(PLEX_TASKS)
    body = _task_body(text, STOP_TASK)
    if body is None:
        print(f"FAIL: task '{STOP_TASK}' not found in {PLEX_TASKS.name}")
        return False
    stops_service = re.search(
        r"ansible\.builtin\.service:.*?\n(?:\s+.*\n)*?\s+state:\s*stopped", body
    )
    before_group, group_detail = _ordered(text, STOP_TASK, GROUP_PIN_TASK)
    before_user, user_detail = _ordered(text, STOP_TASK, USER_PIN_TASK)
    if stops_service and before_group and before_user:
        print("OK: the stop task precedes both id pins (F1)")
        return True
    print(
        f"FAIL: the stop must use ansible.builtin.service state=stopped and precede "
        f"BOTH pins — usermod refuses while the user owns running processes "
        f"(stops={bool(stops_service)}, {group_detail}, {user_detail})"
    )
    return False


def test_chown_precedes_the_ownership_gate() -> bool:
    """The chown lands before the gate, so the migration run survives it (F2)."""
    text = _read(PLEX_TASKS)
    after_user_pin, pin_detail = _ordered(text, USER_PIN_TASK, CHOWN_TASK)
    before_stat, stat_detail = _ordered(text, CHOWN_TASK, GATE_STAT_TASK)
    before_assert, assert_detail = _ordered(text, CHOWN_TASK, GATE_ASSERT_TASK)
    if after_user_pin and before_stat and before_assert:
        print("OK: the chown sits after the uid pin and before the ownership gate")
        return True
    print(
        f"FAIL: the chown must run AFTER the uid pin and BEFORE the gate's "
        f"stat/assert — during a migration run the dir is still at the old ids "
        f"while the pins are new, so a chown after the gate fails the play on its "
        f"own gate ({pin_detail}, {stat_detail}, {assert_detail})"
    )
    return False


def test_migration_tasks_carry_their_predicate() -> bool:
    """Both guarded tasks carry a `when:` — without one the play acts every run (R6)."""
    text = _read(PLEX_TASKS)
    findings = {}
    for name in (STOP_TASK, CHOWN_TASK):
        body = _task_body(text, name)
        findings[name] = bool(body) and bool(
            re.search(rf"^\s+when:.*?{re.escape(PREDICATE_FACT)}", body, re.MULTILINE | re.DOTALL)
        )
    if all(findings.values()):
        print(f"OK: the stop and the chown both carry a {PREDICATE_FACT} predicate")
        return True
    print(
        f"FAIL: both guarded tasks must carry a `when:` referencing "
        f"{PREDICATE_FACT} — an unguarded stop takes PMS down on every run "
        f"({findings})"
    )
    return False


def test_chown_is_post_order_recursive_command() -> bool:
    """The chown MUST be `command: chown -R`, never `file: recurse` (R11).

    This is the only thing standing between R9 and a well-intentioned module swap:
    the swap leaves every other assertion in this file green and ansible-lint does
    not flag it (§7.5). `ansible.builtin.file` with `recurse: yes` sets the
    top-level attrs FIRST and then walks pre-order, so an interrupted run leaves
    the top level already correct with the tree beneath it un-chowned ->
    plex_chown_needed reads FALSE -> the re-run skips -> permanently wedged. GNU
    `chown -R` is post-order (top level chowned LAST), which is the entire basis of
    R9's recovery guarantee.
    """
    text = _read(PLEX_TASKS)
    body = _task_body(text, CHOWN_TASK)
    if body is None:
        print(f"FAIL: task '{CHOWN_TASK}' not found in {PLEX_TASKS.name}")
        return False
    uses_command = re.search(r"ansible\.builtin\.(command|shell):", body)
    recursive_chown = re.search(
        r"chown\s+-R\s+[\"']?\{\{\s*plex_uid\s*\}\}:\{\{\s*plex_gid\s*\}\}", body
    )
    # The regression this guard exists for, asserted directly.
    swapped_to_file_module = re.search(
        r"ansible\.builtin\.file:.*?\n(?:\s+.*\n)*?\s+recurse:\s*(yes|true)", body
    )
    # C-1: `command` is not idempotent by declaration, so production lint fails it
    # fatally (no-changed-when) and the role's own invariant (`tasks/main.yml:3-4`)
    # requires it: "declared state, or a guarded command (changed_when)".
    has_changed_when = re.search(r"^\s+changed_when:", body, re.MULTILINE)
    ok = bool(uses_command and recursive_chown and has_changed_when and not swapped_to_file_module)
    if ok:
        print("OK: the chown is the post-order `command: chown -R` form with changed_when")
        return True
    print(
        f"FAIL: the chown must be `command:`/`shell:` running "
        f"`chown -R {{{{ plex_uid }}}}:{{{{ plex_gid }}}}` with changed_when, and MUST "
        f"NOT be ansible.builtin.file recurse (pre-order -> wedges R9) "
        f"(command={bool(uses_command)}, chown_-R={bool(recursive_chown)}, "
        f"changed_when={bool(has_changed_when)}, "
        f"file_recurse_swap={bool(swapped_to_file_module)})"
    )
    return False


def test_chown_needed_provenance() -> bool:
    """The derivation reads the DIR's stat, never the getent user (R13).

    Keyed on the set_fact, NOT on the chown's `when:`. The obvious form — "the
    chown's when: must not name the getent register" — is VACUOUS and was rejected
    for it: the design requires the fact to be named and reused, so the chown's
    when: is the bare token `plex_chown_needed`, which cannot contain "getent"
    however it was derived. That guard passes for the rejected design too. A bare
    name carries no provenance; DEC-007 gives the derivation an address.

    This guard adds NO coverage the state table lacks (the 64000:991 row already
    fails the getent-keyed design). It buys a precise failure message, nothing
    more. R9 is held by the table, not by this.
    """
    expression = _set_fact_expression()
    if expression is None:
        print(f"FAIL: no `{PREDICATE_FACT}` set_fact found in task {DERIVE_TASK!r}")
        return False
    reads_the_dir = EARLY_STAT_REGISTER in expression
    reads_the_user = "getent" in expression
    if reads_the_dir and not reads_the_user:
        print(f"OK: {PREDICATE_FACT} derives from {EARLY_STAT_REGISTER}, not from getent")
        return True
    print(
        f"FAIL: the {PREDICATE_FACT} derivation must read the DIR "
        f"({EARLY_STAT_REGISTER}) and must NOT read the getent user — keying it on "
        f"the user reads 'done' from the uid while the dir is still half-migrated, "
        f"which is the rejected design that wedges at 64000:991 "
        f"(reads_dir={reads_the_dir}, reads_getent={reads_the_user}); "
        f"expression={expression!r}"
    )
    return False


def test_chown_needed_matches_the_state_table() -> bool:
    """The role's REAL predicate, through ansible's own Jinja2, vs design §6.3.

    Shape assertions are not sufficient and that is a requirement, not a nicety:
    every ordering check above ALSO passes against the rejected design, which had a
    predicate on both tasks and was still permanently wedged. The 64000:991 row is
    the one that tells them apart.
    """
    failures = []
    for label, passwd, stat, expected, _stop in STATE_TABLE:
        actual, error = _resolve_chown_needed(stat, passwd, TARGET_UID, TARGET_GID)
        if error is not None:
            # The absent row asserts "does not raise", so an exception is a result.
            failures.append(f"{label}: raised {error}")
            continue
        if actual is not expected:
            failures.append(f"{label}: expected {expected}, got {actual!r}")
        else:
            print(f"    chown_needed {label} -> {actual}")
    if not failures:
        print(
            f"OK: {PREDICATE_FACT} matches the §6.3 state table on all "
            f"{len(STATE_TABLE)} rows at {TARGET_UID}:{TARGET_GID}"
        )
        return True
    print(f"FAIL: {PREDICATE_FACT} does not match the §6.3 state table: {failures}")
    return False


def test_chown_needed_discriminates() -> bool:
    """Anti-vacuity: the predicate must actually discriminate, and return bools.

    A trivially always-TRUE predicate passes nothing useful and breaks R6; a
    trivially always-FALSE one never migrates. This also catches the
    trust_as_template trap by construction: an untrusted template returns the raw
    "{{ ... }}" string — truthy, CONSTANT on every row, and not a bool.
    """
    results = []
    for label, passwd, stat, _expected, _stop in STATE_TABLE:
        actual, error = _resolve_chown_needed(stat, passwd, TARGET_UID, TARGET_GID)
        if error is not None:
            print(f"FAIL: {PREDICATE_FACT} raised on {label}: {error}")
            return False
        results.append((label, actual))
    non_bool = [(label, type(value).__name__) for label, value in results if not isinstance(value, bool)]
    distinct = {value for _, value in results if isinstance(value, bool)}
    if not non_bool and len(distinct) > 1:
        print(f"OK: {PREDICATE_FACT} returns real bools and discriminates across the table")
        return True
    print(
        f"FAIL: {PREDICATE_FACT} must resolve to real bools that DISCRIMINATE — a "
        f"constant passes the rows it happens to match while breaking R6, and a raw "
        f"string is the untrusted-template trap (non_bool={non_bool}, "
        f"distinct={distinct}, results={results})"
    )
    return False


def test_predicate_is_inert_at_the_current_defaults() -> bool:
    """R6/Step-1 inertness, bound to the ids `defaults/main.yml` really pins.

    Reads the live defaults rather than a literal, so it stays honest through
    Step 2's flip: a dir ALREADY at the pinned ids is the steady state and must
    never re-fire the migration.
    """
    text = _read(PLEX_DEFAULTS)
    uid, gid = _scalar(text, "plex_uid"), _scalar(text, "plex_gid")
    if uid is None or gid is None:
        print(f"FAIL: could not read plex_uid/plex_gid from {PLEX_DEFAULTS.name}")
        return False
    steady = {"exists": True, "uid": uid, "gid": gid}
    actual, error = _resolve_chown_needed(steady, _passwd(uid, gid), uid, gid)
    if error is not None:
        print(f"FAIL: {PREDICATE_FACT} raised at the current defaults {uid}:{gid}: {error}")
        return False
    if actual is False:
        print(f"OK: {PREDICATE_FACT} is FALSE at the pinned defaults {uid}:{gid} (inert)")
        return True
    print(
        f"FAIL: {PREDICATE_FACT} must be FALSE when the dir already carries the "
        f"pinned ids {uid}:{gid} — otherwise the migration re-fires every run (R6); "
        f"got {actual!r}"
    )
    return False


def test_predicate_reads_uid_and_gid_independently() -> bool:
    """The uid and gid halves are pinned SEPARATELY, at ids no later step can flatten.

    The state table cannot make this assertion: it binds plex_uid and plex_gid to
    the same integer (TARGET_UID == TARGET_GID), so the uid==gid collapse — this
    repo's signature historic defect — passes every row of it. Only
    test_predicate_is_inert_at_the_current_defaults() ever bound the two names to
    different values, and it reads them live from defaults/main.yml, so its
    discrimination expires on a DATE: Step 2 flips those defaults to 64000/64000
    and the collapse turns green there, while Step 3 retires this harness. Armed
    only while the machinery is inert, unarmed exactly when it fires.

    So the ids here are LITERALS (PROBE_UID != PROBE_GID by construction) and the
    rows below pin each half against its OWN name. No config change can disarm
    this; that is the entire point of it, and the reason the equality check below
    is a real check rather than a comment. Every mutation named in the rows was
    executed, not argued.
    """
    if PROBE_UID == PROBE_GID:
        print(
            f"FAIL: PROBE_UID/PROBE_GID must stay ASYMMETRIC ({PROBE_UID}:{PROBE_GID}) — "
            f"equal ids cannot tell plex_uid from plex_gid, which makes this guard "
            f"vacuous by construction and is the defect it exists to catch"
        )
        return False
    rows = [
        # Exact match on BOTH halves => nothing to do. Reddens the gid-half
        # collapse (gid 991 != plex_uid 64000 -> True) and the uid/gid swap.
        (
            "dir already at the probe ids",
            {"exists": True, "uid": PROBE_UID, "gid": PROBE_GID},
            False,
        ),
        # The state the historic defect PRODUCES: `chown -R 64000:64000` applied
        # where the gid should still be 991. Reddens dropping the gid half.
        (
            "only the gid is stale (the uid==gid chown's own leftovers)",
            {"exists": True, "uid": PROBE_UID, "gid": PROBE_UID},
            True,
        ),
        # Reddens dropping the uid half — which NOTHING else in this file catches:
        # substitute the uid half with the gid half and all 17 other checks stay
        # green in both defaults worlds. Verified by probe, not assumed.
        (
            "only the uid is stale",
            {"exists": True, "uid": 999, "gid": PROBE_GID},
            True,
        ),
    ]
    failures = []
    for label, stat, expected in rows:
        actual, error = _resolve_chown_needed(
            stat, _passwd(PROBE_UID, PROBE_GID), PROBE_UID, PROBE_GID
        )
        if error is not None:
            failures.append(f"{label}: raised {error}")
            continue
        if actual is not expected:
            failures.append(f"{label}: expected {expected}, got {actual!r}")
        else:
            print(f"    chown_needed {label} -> {actual}")
    if not failures:
        print(
            f"OK: {PREDICATE_FACT} reads uid against plex_uid and gid against plex_gid "
            f"independently at {PROBE_UID}:{PROBE_GID} (defaults-independent)"
        )
        return True
    print(
        f"FAIL: {PREDICATE_FACT} must test the dir's uid against plex_uid and its gid "
        f"against plex_gid SEPARATELY — collapsing them onto one id is the defect that "
        f"leaves the state dir at {PROBE_UID}:{PROBE_UID} when the gid must be "
        f"{PROBE_GID}: {failures}"
    )
    return False


def test_stop_predicate_composes_chown_needed() -> bool:
    """The stop's real `when:`, evaluated — the `or plex_chown_needed` widening.

    Reuse by composition is REQUIRED; substitution is the rejected defect (§4.2,
    §4.7). The stop's when: has two halves and the table pins BOTH, because a
    docstring asserting composition is worth nothing without a row where the two
    designs DISAGREE — this test carried that claim for a full cycle while a bare
    `when: plex_chown_needed` passed it, and the whole gate, green:

    - Drop the getent half (substitute the bare fact) and the HOST-SIDE RECOVERY
      row reddens: dir already 64000:64000 while the user is still 999, so
      chown_needed is FALSE, the stop skips, and `usermod -u` then refuses while
      plex owns live PMS processes (F1).
    - Drop the `or plex_chown_needed` half (key on the user alone) and the
      INTERRUPTED RECOVERY row reddens: at 64000:991 the uid ALREADY reads 64000,
      so the stop returns FALSE and PMS stays live while the chown rewrites its
      state dir underneath it.

    Both directions verified by probe, not by argument. Neither half can be
    removed without a red row; keep it that way.
    """
    expression = _when_expression(STOP_TASK)
    if expression is None:
        print(f"FAIL: task '{STOP_TASK}' has no `when:` to evaluate")
        return False
    failures = []
    for label, passwd, stat, _expected_chown, expected in STATE_TABLE:
        # Bind the name to the value the role's own set_fact really derives, so
        # this covers the WIRING and not a Python restatement of it.
        chown_needed, error = _resolve_chown_needed(stat, passwd, TARGET_UID, TARGET_GID)
        if error is not None:
            failures.append(f"{label}: deriving {PREDICATE_FACT} raised {error}")
            continue
        variables = _fixture_vars(stat, passwd, TARGET_UID, TARGET_GID)
        variables[PREDICATE_FACT] = chown_needed
        try:
            actual = _evaluate_condition(expression, variables)
        except Exception as exc:  # noqa: BLE001 - the absent-user row must not raise
            failures.append(f"{label}: raised {type(exc).__name__}: {exc}")
            continue
        # Demand a real bool, never truthiness: a raw string is truthy and would
        # read as a pass on every row expecting True.
        if not isinstance(actual, bool):
            failures.append(f"{label}: expected a bool, got {type(actual).__name__} {actual!r}")
        elif actual is not expected:
            failures.append(f"{label}: expected {expected}, got {actual!r}")
        else:
            print(f"    stop {label} -> {actual}")
    if not failures:
        print("OK: the stop's real when: composes plex_chown_needed across the state table")
        return True
    print(f"FAIL: the stop predicate does not match design §6.3: {failures}")
    return False


def main() -> int:
    # C-2: hard-FAIL or re-exec — never skip. See the module header.
    if ANSIBLE_IMPORT_ERROR is not None:
        return _reexec_under_ansible_python()
    checks = [
        test_plex_uid_and_gid_pinned_independently(),
        test_uid_gid_pinned_before_package_install(),
        test_state_dir_ownership_asserted(),
        test_ownership_gate_precedes_install(),
        test_fail_msg_names_the_host_side_chown(),
        test_runbook_reads_uid_and_gid_separately(),
        test_runbook_has_no_uid_equals_gid_chown(),
        # Step 1 — the id-migration machinery (design §4.2, §7.1).
        test_early_stat_precedes_the_id_pins(),
        test_stop_precedes_the_id_pins(),
        test_chown_precedes_the_ownership_gate(),
        test_migration_tasks_carry_their_predicate(),
        test_chown_is_post_order_recursive_command(),
        test_chown_needed_provenance(),
        test_chown_needed_matches_the_state_table(),
        test_chown_needed_discriminates(),
        test_predicate_is_inert_at_the_current_defaults(),
        test_predicate_reads_uid_and_gid_independently(),
        test_stop_predicate_composes_chown_needed(),
    ]
    passed = sum(checks)
    total = len(checks)
    print(f"\n{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
