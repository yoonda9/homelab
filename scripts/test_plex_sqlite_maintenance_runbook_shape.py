"""Shape test for Step 3c — `docs/runbooks/plex-sqlite-maintenance.md`.

Per `.agents/planning/2026-08-07-plex-blip-manual-triage/` (plan.md Step 3,
design/detailed-design.md §4.4) — the runbook shipped TWO false claims, and a
shape test that pinned only the corrected §1 claim would declare the file
correct with §2 still promising a timer nobody ships. So this file censuses the
WHOLE runbook, and every row is a relation between the document and the artifact
it describes rather than a quotation of a number:

  * §1's claim, strengthened: WAL mode is **necessary but not sufficient**. We
    measured WAL mode enabled *and* `TX_STALL` occurring at the same time, so no
    line may say WAL mode *prevents* stalls without that qualifier.
  * §1's audit description, which went false-by-omission when Step 3b landed the
    size half: both halves named, and the threshold READ OUT OF
    `ansible/roles/plex/defaults/main.yml` rather than pinned as a literal here
    (mem-1786151204-a4c4: read a guard's figures off the artifact).
  * §1's manual command, whose heading said "(read-only)" while the command
    opened the database read-write — reconciled, and run as the service user the
    role creates, because `-readonly` alone leaves root-owned `-wal`/`-shm`
    sidecars behind (`task-1786148835-48bd`, measured).
  * §2's `VACUUM`/`REINDEX`/`03:30` timer, checked as an EQUALITY against the
    repo: the runbook's claim must match what `ansible/` actually ships, which
    is nothing. The check re-runs the grep; it does not quote its result.
  * §2's triage advice, which told an operator to ignore `SLOW_QUERY` events
    near a maintenance window that does not exist.
  * The cross-artifact obligations this document is under. The plex role's WAL
    `fail_msg` POINTS AT this runbook, and `scripts/test_plex_wal_guard_shape.py`
    reads that path back out of the message and holds this file to the promise.
    Two rows here carry that from this side, so a rewrite of the runbook reds the
    file being edited instead of silently taking another file's suite 14 -> 1.
  * Every repo path the runbook cites, resolved — with the line number.

Follows the repo's dual-mode shape-test convention (see
`test_plex_ramdisk_runbook_shape.py`, `test_plex_latency_runbook_shape.py`):
module-level `test_<name>() -> bool` printing `OK` / `FAIL: ...` (no bare
`assert`), plus `main() -> int` summing the `TESTS` tuple. Stdlib only — no
PyYAML, so the two rows that read the role parse the text themselves. NO
`try/except` skip anywhere: "OK (skip)" is right for an optional TOOL and is a
green badge over an unrun check here.

Regexes anchor on inner content, never whole-line layout (mem-1781892715-142d).
Every predicate is a `_*_defects(body)` function over the document's TEXT, so
each row can be ARMED IN-ROW against the pre-correction wording — a checker that
cannot see the bug it was written for is the failure mode this whole suite is
about. `test_every_test_function_is_registered_in_tests` closes the last hole:
a `test_*` missing from `TESTS` is green-by-omission (mem-1784137124-c346), and
that is asserted here rather than eyeballed.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
# The repo path is a FACT about the document (it is what the role's `fail_msg`
# points at) and is kept separate from `RUNBOOK`, which is only where the bytes
# under test are read from. A harness scoring the pre-correction file out of a
# tmp directory must not thereby change which path the role is promising about.
RUNBOOK_REL = "docs/runbooks/plex-sqlite-maintenance.md"
RUNBOOK = REPO_ROOT / RUNBOOK_REL
PLEX_DEFAULTS = REPO_ROOT / "ansible" / "roles" / "plex" / "defaults" / "main.yml"
PLEX_TASKS = REPO_ROOT / "ansible" / "roles" / "plex" / "tasks" / "main.yml"
WAL_GUARD = REPO_ROOT / "scripts" / "test_plex_wal_guard_shape.py"
ANSIBLE_DIR = REPO_ROOT / "ansible"

# Vendored third-party content is not "what this repo ships".
VENDORED = "galaxy_roles"

THRESHOLD_VAR = "plex_wal_max_bytes"
SERVICE_USER_VAR = "plex_service_user"

# The tokens the §2 claim is made of. If the repo ever grows one of these, the
# runbook's "not shipped" goes stale and this suite says so.
TIMER_RE = re.compile(r"VACUUM|REINDEX|03:30", re.IGNORECASE)

# A repo-relative path with an optional `:LINE` or `:LINE-LINE` suffix. Same
# shape as `test_plex_wal_guard_shape.py:182`, extended with the line ref so a
# citation is checked as a citation and not merely as a filename.
CITATION_RE = re.compile(
    r"(?:[\w.-]+/)+[\w.-]+\.(?:md|yml|yaml|py|sh|json|txt)(?::\d+(?:-\d+)?)?"
)

# A clause ends at sentence punctuation or a closing quote followed by
# whitespace — the same boundary `test_plex_wal_guard_shape.py:188` uses, because
# it is reading the same message.
CLAUSE_END_RE = re.compile(r"(?:[.;:]|['\"])\s")

WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# The document is one markdown paragraph per line, so a LINE is the claim unit.
# Splitting on `.` would shatter every `plan.md:116` citation in the file.
def _claims(body: str):
    return [line.strip() for line in body.splitlines() if line.strip()]


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _body() -> str:
    """The runbook's bytes, through the module global so a harness can redirect.

    Read at CALL time rather than at import, which is what lets the red half of
    the differential point every row at `git show <parent>:<runbook>` without
    this file carrying an env-var knob that could be pointed at a doctored file
    during the gate.
    """
    return _read(RUNBOOK)


def _defaults_scalar(name: str) -> str:
    """One top-level scalar out of the plex role defaults, by text.

    Stdlib only, so this is a regex rather than `yaml.safe_load` — anchored at
    column 0 so a commented-out or nested spelling cannot answer for the real
    one. Returns "" when absent, and every caller treats "" as a defect.
    """
    match = re.search(rf"^{re.escape(name)}:\s*(\S+)\s*$", _read(PLEX_DEFAULTS), re.M)
    return match.group(1) if match else ""


def _uncommented_role_text() -> str:
    """`tasks/main.yml` with every comment line dropped, joined into one line.

    The runbook's path appears TWICE in that file — once in the `fail_msg` and
    once in the comment block above it recounting round 1's defect. Only the
    first is a promise, so the comments go before anything is read out.
    """
    kept = [
        line.strip()
        for line in _read(PLEX_TASKS).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    return " ".join(kept)


def _claim_word_min() -> int:
    """`CLAIM_WORD_MIN`, read out of the guard that enforces the promise.

    Pinned by relation, not copied: if that row retunes the threshold, the two
    files stay in agreement instead of drifting apart quietly. 0 means "not
    found", and every caller treats that as a defect.
    """
    match = re.search(r"^CLAIM_WORD_MIN\s*=\s*(\d+)", _read(WAL_GUARD), re.M)
    return int(match.group(1)) if match else 0


def _claim_words(clause: str, minimum: int):
    return sorted({w.lower() for w in WORD_RE.findall(clause) if len(w) >= minimum})


def _clause_before(text: str, needle: str) -> str:
    head = text.split(needle, 1)[0]
    ends = [match.end() for match in CLAUSE_END_RE.finditer(head)]
    return head[ends[-1]:] if ends else head


# --- Predicates: every one a function of the document's TEXT ---------------


def _stall_claim_defects(body: str):
    """§1's corrected claim. [] is a document that says the measured thing."""
    defects = []
    flat = " ".join(body.split())
    if not re.search(r"necessary\b[^.]{0,40}\bnot\s+sufficient", flat, re.I):
        defects.append("no 'necessary but not sufficient' qualifier")
    if not re.search(r"\bitself a stall mechanism\b", flat, re.I):
        defects.append("does not say an unchecked WAL is itself a stall mechanism")
    if not re.search(r"\bTX_STALL\b", flat):
        defects.append("does not name TX_STALL")
    if not re.search(r"43,?735,?168", flat):
        defects.append("does not carry the measured WAL size 43,735,168")
    if not re.search(r"\b2026-08-07\b", flat):
        defects.append("does not date the measurement")
    for line in _claims(body):
        if re.search(r"prevent\w*", line, re.I) and re.search(r"stall", line, re.I):
            if not re.search(r"necessary\b[^.]{0,40}\bnot\s+sufficient", line, re.I):
                defects.append(f"unqualified prevention claim: {line[:72]!r}")
    return defects


def _audit_scope_defects(body: str):
    """§1 must describe BOTH halves of the shipped audit, at the shipped number."""
    defects = []
    flat = " ".join(body.split())
    threshold = _defaults_scalar(THRESHOLD_VAR)
    if not threshold:
        defects.append(f"{THRESHOLD_VAR} not declared in the role defaults")
    if "journal_mode" not in body:
        defects.append("does not name the journal_mode half")
    if not re.search(r"\bWAL size\b|\bsize half\b|`-wal`", flat, re.I):
        defects.append("does not name the WAL size half")
    if not re.search(r"\bstat\b", flat):
        defects.append("does not name the stat the size half stands on")
    if THRESHOLD_VAR not in body:
        defects.append(f"does not name {THRESHOLD_VAR}")
    if threshold and threshold not in body:
        defects.append(f"does not carry the shipped threshold {threshold}")
    if not re.search(r"fail\w*\b[^.]{0,60}\bplay\b|\bplay\b[^.]{0,60}\bfail", flat, re.I):
        defects.append("does not say the audit fails the play")
    return defects


def _sqlite_invocations(body: str):
    """Every `sqlite3` command line the runbook prints inside a fenced block."""
    found = []
    for block in re.findall(r"```(?:bash|sh|console)?\n(.*?)```", body, re.S):
        for line in block.splitlines():
            if re.search(r"\bsqlite3\b", line):
                found.append(line.strip())
    return found


def _manual_command_defects(body: str):
    """§1's manual verification: the command must match its own heading.

    `-readonly` is only half the reconciliation. A read-only connection to a WAL
    database MUST materialise the `-shm` sidecar and CANNOT run the close-time
    cleanup that removes it, so run as root it leaves root-owned files in a
    directory Plex's uid owns and the library goes silently read-only
    (`task-1786148835-48bd`, measured against libsqlite3 3.51.2). The runbook
    must therefore name the service user AND the hazard, or it is trading one
    piece of harmful advice for another.
    """
    defects = []
    flat = " ".join(body.split())
    user = _defaults_scalar(SERVICE_USER_VAR)
    if not user:
        defects.append(f"{SERVICE_USER_VAR} not declared in the role defaults")
    commands = _sqlite_invocations(body)
    if not commands:
        defects.append("no sqlite3 invocation is documented")
    for command in commands:
        if "-readonly" not in command:
            defects.append(f"invocation opens the database read-write: {command[:60]!r}")
        if user and not re.search(rf"\bsudo\b[^|]*-u\s+{re.escape(user)}\b", command):
            defects.append(f"invocation does not run as {user}: {command[:60]!r}")
        if "PRAGMA journal_mode" not in command:
            defects.append(f"invocation does not read the journal mode: {command[:60]!r}")
    if not re.search(r"read-only", flat, re.I):
        defects.append("the heading no longer calls the check read-only")
    if not re.search(r"-shm", flat):
        defects.append("does not name the -shm sidecar the read-only open materialises")
    if not re.search(r"\broot\b", flat, re.I):
        defects.append("does not say who ends up owning the residue")
    if not re.search(r"silently read-only|read-only library", flat, re.I):
        defects.append("does not name the consequence (a silently read-only library)")
    if not re.search(r"^wal$", body, re.M):
        defects.append("does not show the expected `wal` output")
    return defects


def _mutate_command(body: str, replacement: str) -> str:
    commands = _sqlite_invocations(body)
    return body.replace(commands[0], replacement) if commands else ""


def _shipped_timer_hits():
    """Every `VACUUM`/`REINDEX`/`03:30` hit this repo actually ships, as paths.

    Re-runs the census instead of quoting its result, so the day someone builds
    the timer this row goes red and points at the runbook that denies it.
    """
    hits = []
    for path in sorted(ANSIBLE_DIR.rglob("*")):
        if not path.is_file() or VENDORED in path.parts:
            continue
        text = path.read_text(errors="ignore")
        if TIMER_RE.search(text):
            hits.append(str(path.relative_to(REPO_ROOT)))
    return hits


NEGATION_RE = re.compile(
    r"not shipped|no such|never built|does not exist|there is no|zero hits"
    r"|used to claim|is false|false twice|previously claimed",
    re.I,
)


def _timer_defects(body: str, shipped):
    """An EQUALITY between §2 and the repo, in both directions."""
    defects = []
    flat = " ".join(body.split())
    mentions = [line for line in _claims(body) if TIMER_RE.search(line)]
    if not mentions:
        defects.append("§2 says nothing about the VACUUM/REINDEX timer at all")
    if shipped:
        if NEGATION_RE.search(flat):
            defects.append(f"denies a timer this repo ships: {shipped}")
        return defects
    if not NEGATION_RE.search(flat):
        defects.append("no timer is shipped and the runbook does not say so")
    for line in mentions:
        if not NEGATION_RE.search(line):
            defects.append(f"asserts an unshipped timer: {line[:72]!r}")
    return defects


def _slow_query_defects(body: str):
    """No line may send an operator away from a `SLOW_QUERY` event."""
    defects = []
    for line in _claims(body):
        if not re.search(r"SLOW_QUERY", line):
            continue
        if not re.search(r"ignor", line, re.I):
            continue
        if not re.search(r"\b(?:not|never|no longer|cannot)\b[^.]{0,40}ignor", line, re.I):
            defects.append(f"tells the operator to ignore SLOW_QUERY: {line[:72]!r}")
    return defects


def _promise_defects(body: str):
    """Hold THIS document to the clause the role's `fail_msg` introduces it with.

    The mirror of `test_plex_wal_guard_shape.py`'s
    `test_every_file_the_fail_msg_points_at_carries_what_it_promises`, run from
    the document's side: the pointer clause and the word threshold are both read
    out of those two artifacts, so a runbook rewrite that drops `journal_mode` or
    `audit` reds the file the editor has open rather than another suite.
    """
    defects = []
    relative = RUNBOOK_REL
    role = _uncommented_role_text()
    occurrences = role.count(relative)
    if occurrences != 1:
        defects.append(f"the role points at this runbook {occurrences} times, expected 1")
        return defects
    minimum = _claim_word_min()
    if not minimum:
        defects.append("CLAIM_WORD_MIN not readable out of the WAL guard")
        return defects
    clause = _clause_before(role, relative)
    words = _claim_words(clause, minimum)
    if not words:
        defects.append(f"the pointer clause carries no claim word: {clause[:72]!r}")
    lowered = body.lower()
    missing = [word for word in words if word not in lowered]
    if missing:
        defects.append(f"does not carry the promised {missing} (clause={clause.strip()!r})")
    return defects


def _arming_probe_words():
    """The claim words of the WAL guard's reconstructed-defect probe.

    Read out of the probe's own f-string, not copied, so a later row that
    re-arms it with a different word is followed rather than contradicted.
    """
    match = re.search(r'f"([^"\n]*\{named\[0\]\}[^"\n]*)"', _read(WAL_GUARD))
    if not match:
        return None
    minimum = _claim_word_min()
    if not minimum:
        return None
    return _claim_words(_clause_before(match.group(1), "{named[0]}"), minimum)


def _disarm_defects(body: str):
    """The runbook must keep the guard's arming probe CATCHABLE.

    That probe reconstructs round 1's defect — a `fail_msg` promising a remedy
    the target does not carry — and it only catches while this runbook lacks at
    least one of the probe's claim words. Documenting the checkpoint procedure
    here is the most natural thing a later row could do, and it would take
    `test_plex_wal_guard_shape.py` from 14/14 to 1/14 with `probes_caught` going
    1 -> 0. That is licensed, but only together with re-arming the probe on a
    word this runbook genuinely lacks — never by deleting it
    (mem-1785979220-8c1f). This row is what makes that trade visible in the file
    being edited.
    """
    words = _arming_probe_words()
    if words is None:
        return ["the WAL guard's arming probe is not readable"]
    if not words:
        return ["the WAL guard's arming probe carries no claim word"]
    lowered = body.lower()
    absent = [word for word in words if word not in lowered]
    if not absent:
        return [f"carries every probe word {words} — the guard's probe no longer catches"]
    return []


def _citation_defects(body: str):
    """Every repo path the runbook cites resolves, at the line it cites."""
    defects = []
    seen = []
    for match in CITATION_RE.finditer(body):
        citation = match.group(0)
        if citation in seen:
            continue
        seen.append(citation)
        path, _, line_ref = citation.partition(":")
        target = REPO_ROOT / path
        if not target.is_file():
            defects.append(f"{citation}: no such file")
            continue
        if not line_ref:
            continue
        first = int(line_ref.split("-")[0])
        last = int(line_ref.split("-")[-1])
        available = len(target.read_text().splitlines())
        if last > available:
            defects.append(f"{citation}: file has {available} lines")
        elif first < 1:
            defects.append(f"{citation}: line 0")
    if not seen:
        defects.append("cites no artifact at all")
    return defects


# --- Rows ------------------------------------------------------------------


def test_runbook_exists_and_nonempty() -> bool:
    body = _body()
    ok = len(body.strip()) > 0
    print(
        f"{'OK' if ok else 'FAIL'}: docs/runbooks/plex-sqlite-maintenance.md "
        f"exists and is non-empty (chars={len(body)})"
    )
    return ok


def test_wal_mode_is_necessary_but_not_sufficient() -> bool:
    """The correction plan.md:160-161 and design §4.4 both ask for.

    ARMED IN-ROW against the pre-correction sentence, which is the exact claim
    this row exists to keep out: WAL mode named as the thing that PREVENTS
    `TX_STALL`. If that reads clean the row cannot see the bug it was written
    for.
    """
    body = _body()
    defects = _stall_claim_defects(body)
    probes = {
        "the parent's unqualified prevention claim": (
            "To prevent transaction lock stalls (`TX_STALL`) and ensure high "
            "concurrency for reads (library queries) while writes "
            "(scans/metadata updates) are occurring, the database **must** be "
            "operating in Write-Ahead Logging (WAL) mode."
        ),
        "the qualifier without the measurement that licenses it": (
            "WAL mode is necessary but NOT sufficient; an unchecked WAL is "
            "itself a stall mechanism."
        ),
    }
    caught = {label: _stall_claim_defects(probe) for label, probe in probes.items()}
    armed = all(bool(found) for found in caught.values())
    ok = not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: §1 says WAL mode is necessary but not "
        f"sufficient, with the measurement (defects={defects} "
        f"probes_caught={ {label: len(found) for label, found in caught.items()} })"
    )
    return ok


def test_the_audit_description_names_both_halves_at_the_shipped_threshold() -> bool:
    """`:9` went false-by-omission the day Step 3b landed the size half.

    The threshold is READ OUT OF the role defaults, so the runbook is checked
    against the number the play actually enforces rather than against a literal
    typed here — a copy of `8388608` in this file would go stale in exactly the
    same way the sentence did.

    ARMED against the parent's one-half sentence and against a body that names
    both halves at the WRONG number, because the second is what a hardcoded
    figure would wave through.
    """
    body = _body()
    threshold = _defaults_scalar(THRESHOLD_VAR)
    defects = _audit_scope_defects(body)
    probes = {
        "the parent's sqlite3-only sentence": (
            "The Ansible role automatically audits this requirement during "
            "deployment using the `sqlite3` CLI."
        ),
        "both halves at a stale threshold": (
            body.replace(threshold, "1048576") if threshold else ""
        ),
    }
    caught = {label: _audit_scope_defects(probe) for label, probe in probes.items()}
    armed = bool(threshold) and all(bool(found) for found in caught.values())
    ok = not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: §1 names the journal_mode half and the size "
        f"half at the shipped {THRESHOLD_VAR}={threshold!r} (defects={defects} "
        f"probes_caught={ {label: len(found) for label, found in caught.items()} })"
    )
    return ok


def test_the_manual_verification_matches_its_read_only_heading() -> bool:
    """`:11` said "(read-only)" and `:13` ran `sqlite3` without the flag.

    ARMED against both doors that are wrong: the parent's read-write command,
    and the naive reconciliation — `-readonly` added but still run as root,
    which is the advice `task-1786148835-48bd` measured as harmful.
    """
    body = _body()
    database = (
        '"/var/lib/plexmediaserver/Library/Application Support/Plex Media '
        'Server/Plug-in Support/Databases/com.plexapp.plugins.library.db"'
    )
    defects = _manual_command_defects(body)
    probes = {
        "the parent's read-write command": _mutate_command(
            body, f'sqlite3 {database} "PRAGMA journal_mode;"'
        ),
        "-readonly but still run as root": _mutate_command(
            body, f'sqlite3 -readonly {database} "PRAGMA journal_mode;"'
        ),
    }
    caught = {label: _manual_command_defects(probe) for label, probe in probes.items()}
    armed = all(bool(found) for found in caught.values())
    ok = not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: the manual check is read-only and run as "
        f"{_defaults_scalar(SERVICE_USER_VAR)!r}, with the sidecar hazard named "
        f"(defects={defects} "
        f"probes_caught={ {label: len(found) for label, found in caught.items()} })"
    )
    return ok


def test_the_maintenance_timer_claim_matches_what_the_repo_ships() -> bool:
    """§2 promised a `03:30` `VACUUM`/`REINDEX` timer that does not exist.

    Scored as an EQUALITY and in both directions: the census is re-run here
    (`ansible/`, vendored roles excluded) rather than quoted, so a runbook that
    denies a timer someone later builds is just as red as the runbook that
    promised one nobody built.

    ARMED against the parent's §2 paragraph.
    """
    body = _body()
    shipped = _shipped_timer_hits()
    defects = _timer_defects(body, shipped)
    probes = {
        "the parent's timer paragraph": (
            "Plex Media Server has a scheduled task that performs `VACUUM` and "
            "`REINDEX` operations. This timer is configured to run at **03:30 "
            "AM** (off-peak hours) to ensure that the heavy I/O and exclusive "
            "database locks required by these operations do not interrupt media "
            "streaming or user interaction."
        ),
        "a corrected §2 scored against a repo that DID ship one": None,
    }
    caught = {
        "the parent's timer paragraph": _timer_defects(
            probes["the parent's timer paragraph"], shipped
        ),
        "a corrected §2 scored against a repo that DID ship one": _timer_defects(
            body, ["ansible/roles/plex/tasks/main.yml"]
        ),
    }
    armed = all(bool(found) for found in caught.values())
    ok = not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: §2's timer claim equals what ansible/ ships "
        f"(shipped={shipped} defects={defects} "
        f"probes_caught={ {label: len(found) for label, found in caught.items()} })"
    )
    return ok


def test_slow_query_events_are_not_dismissed_as_maintenance_collateral() -> bool:
    """`:27` told an operator to ignore the fault near a window that is not there.

    ARMED against that sentence, and against its negated form, so the row is
    keyed on the ADVICE rather than on the word `ignored` appearing at all.
    """
    body = _body()
    defects = _slow_query_defects(body)
    probes = {
        "the parent's dismissal": (
            "If you encounter `SLOW_QUERY` events near this time window, they "
            "are likely collateral from the maintenance lock and can be ignored "
            "unless they persist outside the maintenance window."
        ),
    }
    caught = {label: _slow_query_defects(probe) for label, probe in probes.items()}
    negated = _slow_query_defects(
        "A `SLOW_QUERY` event must not be ignored: there is no maintenance window."
    )
    armed = all(bool(found) for found in caught.values()) and not negated
    ok = not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: no line dismisses SLOW_QUERY as maintenance "
        f"collateral (defects={defects} negated_form_passes={not negated} "
        f"probes_caught={ {label: len(found) for label, found in caught.items()} })"
    )
    return ok


def test_the_runbook_carries_what_the_role_s_fail_msg_promises() -> bool:
    """The plex role points HERE; this row holds the document to that clause.

    `ansible/roles/plex/tasks/main.yml`'s WAL `fail_msg` says *"See the
    journal_mode audit in docs/runbooks/plex-sqlite-maintenance.md."* and
    `test_plex_wal_guard_shape.py` reads the path back out and requires every
    claim word of that clause to appear here. Both the clause and the word
    threshold are read out of those files, so this is the same obligation rather
    than a copy of today's wording.

    ARMED IN-ROW: a clause promising a word this runbook does not carry must be
    caught, or the extractor could be returning nothing and this row would be
    green over a document that promises nothing.
    """
    body = _body()
    defects = _promise_defects(body)
    minimum = _claim_word_min()
    clause = _clause_before(_uncommented_role_text(), RUNBOOK_REL)
    words = _claim_words(clause, minimum) if minimum else []
    probe_missing = [
        word
        for word in _claim_words("See the defragmentation schedule in", minimum or 4)
        if word not in body.lower()
    ]
    armed = bool(words) and bool(probe_missing)
    ok = not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: the runbook carries the role's promise "
        f"(claim_word_min={minimum} promised={words} defects={defects} "
        f"probe_missing={probe_missing})"
    )
    return ok


def test_the_runbook_does_not_disarm_the_wal_guard_s_pointer_probe() -> bool:
    """The `14/14 -> 1/14` trap, made visible from the file that springs it.

    `test_plex_wal_guard_shape.py`'s pointer row reconstructs round 1's defect
    as a promise about THIS file, and that probe only catches while this file
    lacks one of its claim words. The word is read out of the probe rather than
    named here, so re-arming it on a different word (the licensed door, taken
    together with documenting the remedy) keeps this row honest instead of
    turning it into a second thing to update.

    ARMED IN-ROW: a body that carries every probe word must be caught.
    """
    body = _body()
    words = _arming_probe_words()
    defects = _disarm_defects(body)
    probe = " ".join(words or []) + " " + body
    caught = _disarm_defects(probe)
    armed = bool(words) and bool(caught)
    ok = not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: the WAL guard's probe still catches against "
        f"this runbook (probe_words={words} absent_here="
        f"{[w for w in (words or []) if w not in body.lower()]} defects={defects} "
        f"probes_caught={len(caught)})"
    )
    return ok


def test_every_repo_path_the_runbook_cites_resolves() -> bool:
    """A runbook is a set of pointers; a stale one is the rot inside the pin.

    Checked WITH the line number, because `plan.md:116` is the whole evidence
    for §2's correction and a bare "the file exists" would survive that file
    being rewritten out from under the claim.

    ARMED against a missing file and against a real file at an impossible line.
    """
    body = _body()
    defects = _citation_defects(body)
    probes = {
        "a file that is not there": "See docs/runbooks/does-not-exist.md.",
        "a real file at an impossible line": (
            "See ansible/roles/plex/defaults/main.yml:99999."
        ),
    }
    caught = {label: _citation_defects(probe) for label, probe in probes.items()}
    armed = all(bool(found) for found in caught.values())
    ok = not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: every path the runbook cites resolves at the "
        f"line it cites (defects={defects} "
        f"probes_caught={ {label: len(found) for label, found in caught.items()} })"
    )
    return ok


def test_every_test_function_is_registered_in_tests() -> bool:
    """A `test_*` missing from `TESTS` is green by omission.

    Asserted rather than eyeballed: the module's own namespace is the census,
    and this row is in `TESTS` too, so it cannot exempt itself.
    """
    defined = sorted(
        name
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    )
    registered = sorted(fn.__name__ for fn in TESTS)
    unregistered = [name for name in defined if name not in registered]
    ok = not unregistered and len(registered) == len(set(registered))
    print(
        f"{'OK' if ok else 'FAIL'}: every test_* is registered in TESTS "
        f"(defined={len(defined)} registered={len(registered)} "
        f"unregistered={unregistered})"
    )
    return ok


TESTS = (
    test_runbook_exists_and_nonempty,
    test_wal_mode_is_necessary_but_not_sufficient,
    test_the_audit_description_names_both_halves_at_the_shipped_threshold,
    test_the_manual_verification_matches_its_read_only_heading,
    test_the_maintenance_timer_claim_matches_what_the_repo_ships,
    test_slow_query_events_are_not_dismissed_as_maintenance_collateral,
    test_the_runbook_carries_what_the_role_s_fail_msg_promises,
    test_the_runbook_does_not_disarm_the_wal_guard_s_pointer_probe,
    test_every_repo_path_the_runbook_cites_resolves,
    test_every_test_function_is_registered_in_tests,
)


def main() -> int:
    results = [fn() for fn in TESTS]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
