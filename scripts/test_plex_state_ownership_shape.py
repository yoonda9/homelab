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
    emits a collapsed `uid == gid` chown.

Follows the repo's dual-mode shape-test convention (see
`test_ansible_layout_shape.py`, `test_traefik_config_shape.py`): module-level
`test_<name>() -> bool` functions that print `OK` / `FAIL: ...` (no `assert`),
plus `main() -> int` that sums the booleans and `sys.exit`s non-zero on any
failure. Stdlib only (the gate pythons have no PyYAML — mem-1782133401-4307).
Regexes anchor on the inner content (mem-1781892715-142d), so a comment or an
empty stub cannot satisfy a check. The real gate is the standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PLEX_ROLE = REPO_ROOT / "ansible" / "roles" / "plex"
PLEX_DEFAULTS = PLEX_ROLE / "defaults" / "main.yml"
PLEX_TASKS = PLEX_ROLE / "tasks" / "main.yml"
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "plex-claim.md"

INSTALL_TASK = "Install Plex Media Server"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _scalar(text: str, key: str):
    """Return the int value of a top-level `key: <int>` line, else None."""
    match = re.search(rf"^{re.escape(key)}:\s*(\d+)\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def _task_index(text: str, name: str):
    """Return the character offset of the `- name: <name>` task header, else None."""
    match = re.search(rf"^-\s+name:\s*{re.escape(name)}\s*$", text, re.MULTILINE)
    return match.start() if match else None


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


def main() -> int:
    checks = [
        test_plex_uid_and_gid_pinned_independently(),
        test_uid_gid_pinned_before_package_install(),
        test_state_dir_ownership_asserted(),
        test_ownership_gate_precedes_install(),
        test_fail_msg_names_the_host_side_chown(),
        test_runbook_reads_uid_and_gid_separately(),
        test_runbook_has_no_uid_equals_gid_chown(),
    ]
    passed = sum(checks)
    total = len(checks)
    print(f"\n{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
