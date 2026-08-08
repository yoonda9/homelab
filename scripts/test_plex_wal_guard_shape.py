"""Shape + behavioural tests for the Plex SQLite WAL-size guard (Step 3b).

Per `.agents/planning/2026-08-07-plex-blip-manual-triage/implementation/plan.md`
Step 3 — CT 110's write-ahead log is **41.71 MiB against a 40.9 MiB database**,
43x SQLite's default checkpoint threshold, byte-identical for 42.5 hours, and the
role's only audit asked `PRAGMA journal_mode;` and compared it to `'wal'`. That
answer is **true** while the fault is live, so the guard has been green over the
open root cause since the day it was written. This file pins the replacement.

WHAT THE ROW ACTUALLY CHANGED, because plan.md:152 names the wrong mechanism.
It says "today's audit asserts journal_mode == 'wal'". It is not an
`ansible.builtin.assert` — it is `ansible.builtin.command` + `failed_when`, and
the only `assert` near it is the iHD/QSV gate. Anyone grepping the role for
`assert` edits the wrong task. The audit is now three tasks: the journal-mode
command (unchanged in kind, now carrying `-readonly`), an `ansible.builtin.stat`
of the WAL, and an `ansible.builtin.assert` over the stat.

WHY THE GUARD IS SPLIT, AND IT IS A MEASUREMENT RATHER THAN A PREFERENCE.
`sqlite3` is **not installed on the dev box** — running the journal-mode task
locally dies `rc=2, "sqlite3: command not found"`, which reads as a guard failure
and is a missing binary. A size condition hanging off the registered sqlite3
output is therefore undemonstrable anywhere but a deployed host, which puts the
whole of Step 3's evidence behind an operator gate. Standing the size half on
`ansible.builtin.stat` alone is what makes the red below reproducible here.
`test_the_size_guard_does_not_depend_on_the_sqlite3_audit` pins that split, since
it is the property the other three behavioural rows silently rely on.

WHY THE BEHAVIOURAL ROWS DRIVE THE REAL TASKS AND NEVER A COPY OF THEM. The
condition under test is one Jinja expression. Re-spelling it in Python — or
hand-writing a probe playbook beside the role — produces a **second spelling**
of the thing under test, and a second spelling cannot fail with the first: edit
the role's `<` to `>` and a hand-kept probe stays green. So `_guard_playbook()`
parses `ansible/roles/plex/tasks/main.yml`, lifts the stat and assert tasks out
**by their containing task name**, and writes those dicts verbatim into a scratch
playbook. `test_the_behavioural_harness_runs_the_role_s_own_tasks` asserts the
lift is verbatim (round-tripped equality against the role, both tasks present,
a non-empty `that:`) — without it the three runs below could be scoring an empty
playbook and reading green.

Located by CONTAINING TASK, never by grep, following
`scripts/test_plex_watchdog_deps_shape.py`. That file's reason applies here
verbatim and then some: `sqlite3` appears in this role both as a package name and
inside a `command: argv:` list, and now `-readonly` has to be attributed to the
*right* one of those.

The threshold the behavioural rows run against is read from
`ansible/roles/plex/defaults/main.yml`, not from a literal here — a guard that
hardcodes its own figures pins a number nobody re-derives (mem-1786144467-87d6).
The two SIZES are literals, because they are the fixture: 43,735,168 is the live
WAL and 2,097,152 is a healthy one, and the pair is a **differential** — the same
playbook, the same threshold, one number apart. Neither run means anything
without the other.

WHY FOUR ROWS GUARD THE MESSAGE'S ACTIONABLE HALF AND NOT ONLY ITS NUMBERS.
This sentence has now been wrong twice, the same way twice: it ordered something
that does not work in the state the guard fires in.

Round 1 named both numbers and then ordered "Run the checkpoint in
docs/runbooks/plex-sqlite-maintenance.md" — a file with no checkpoint in it, and
`wal_checkpoint` appeared nowhere in this repo (Critic, DEC-242). Every word
telling a human what to DO was unpinned in every direction: repoint the sentence
at a nonexistent file, delete it, or replace it with "Reboot CT 110." and all
three stayed green.

Round 2 named the statement INLINE, which fixed the pointer and left the command
inert (Critic, DEC-244). This guard is red only while the WAL is large, the WAL
is large only while Plex holds a read transaction, and that is exactly when
`wal_checkpoint(TRUNCATE)` comes back `busy` and moves nothing — see
`CHECKPOINT_STMT` for the measurement. So the remedy is not one statement, it is
three ORDERED steps, and the lesson the third round encodes is that naming a
remedy is not the same as naming a remedy that runs.

`test_the_fail_msg_orders_a_remedy_this_repo_can_obey` pins the statement's own
runnability (binary, database by variable, and no `-readonly` on a write), and
`test_the_fail_msg_orders_the_checkpoint_with_its_precondition` pins the sequence
around it against the unit read out of the ROLE — which is what makes deletion,
substitution and reordering all red.
`test_every_file_the_fail_msg_points_at_carries_what_it_promises` reads the paths
back OUT of the message rather than being told them, and asserts of EACH that the
target exists and carries the claim words the message hands it. Those last two
are standing laws, not repairs of one sentence: each parent defect is
reconstructed as an in-row probe and must be rejected.

PyYAML is importable under the gate interpreter (`run_gate.py:56` runs each file
as `[sys.executable, path]` and `just test` uses the repo `.venv`). There is
deliberately no try/except skip around the import or around `mise`: the repo
idiom `OK (skip): not installed` would turn a missing tool into a green badge
over an unrun guard, which is the vacuous pass this file exists to refuse.

Dual-mode (module-level `test_*() -> bool` + `main() -> int`), and every function
is registered in `TESTS` — one omitted from that tuple is green by omission
(mem-1784137124-c346).
"""

import copy
import json
import pathlib
import re
import subprocess
import sys
import tempfile

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PLEX_ROLE = REPO_ROOT / "ansible" / "roles" / "plex"
PLEX_TASKS = PLEX_ROLE / "tasks" / "main.yml"
PLEX_DEFAULTS = PLEX_ROLE / "defaults" / "main.yml"

AUDIT_TASK = "Verify Plex SQLite DB is in WAL mode (read-only audit)"
STAT_TASK = "Stat the Plex SQLite write-ahead log"
ASSERT_TASK = "Assert the Plex SQLite WAL is below the checkpoint threshold"
SERVICE_TASK = "Ensure Plex Media Server is enabled and running"

DB_VAR = "plex_library_db"
THRESHOLD_VAR = "plex_wal_max_bytes"
STATE_DIR_VAR = "plex_state_dir"
WAL_REGISTER = "plex_wal"
AUDIT_REGISTER = "plex_sqlite_wal"

# plan.md Step 3: `plex_wal_max_bytes` default 8388608 (8 MiB). SQLite's own
# wal_autocheckpoint is 1000 pages; at Plex's 4 KiB page size that is ~4 MiB, so
# 8 MiB is one doubling of headroom over the checkpoint the engine already tries
# to take on its own, and 41.71 MiB is 43x it.
THRESHOLD_DEFAULT = 8388608

# The fixture, and the two halves are each other's control.
LIVE_WAL_BYTES = 43735168  # 41.71 MiB, CT 110 as measured 2026-08-07
HEALTHY_WAL_BYTES = 2097152  # 2 MiB

READONLY_FLAG = "-readonly"
SQLITE_BIN = "sqlite3"

# The checkpoint, which is the MIDDLE of the remedy and not the whole of it.
#
# Round 2 shipped this statement alone and justified the mode with a claim that
# is measurably false (Critic, DEC-244; re-measured at
# `logs/builder-3b-r3-sqlite-probe.txt` against libsqlite3 3.51.2, the same
# library the CLI links). It said "PASSIVE gives up the moment any reader is
# attached and Plex always is, so PASSIVE would not end the condition". With a
# reader holding an open read transaction:
#
#     PASSIVE   busy=0 log=806 ckpt=806   WAL 3320752 -> 3320752
#     TRUNCATE  busy=1 log=806 ckpt=806   WAL 3320752 -> 3320752
#
# PASSIVE did not give up — it checkpointed all 806 frames. It is TRUNCATE that
# comes back `busy` under a reader, and neither mode moves the WAL FILE, which is
# the only number this guard reads. `busy=1` is a result row, not an error: the
# CLI prints `1|806|806` and exits 0, so an operator copy-pasting the statement
# at 03:00 sees three numbers, no diagnostic, and a guard that is still red.
#
# So the mode survives, for the opposite reason, and only behind a stop. With no
# reader attached:
#
#     PASSIVE   busy=0 log=806 ckpt=806   WAL 3320752 -> 3320752
#     FULL      busy=0 log=806 ckpt=806   WAL 3320752 -> 3320752
#     TRUNCATE  busy=0 log=0   ckpt=0     WAL 3320752 -> 0
#
# PASSIVE and FULL checkpoint the frames and leave the file at its high-water
# mark; TRUNCATE is the ONLY mode that moves `stat.size`. The stop is what makes
# it non-busy, the mode is what makes the file shrink, and the guard needs both.
# This must be run READ-WRITE; see `test_the_fail_msg_orders_a_remedy_this_repo_can_obey`.
CHECKPOINT_STMT = "PRAGMA wal_checkpoint(TRUNCATE);"

# The precondition, spelled against the unit the ROLE itself manages rather than
# a literal here — `_managed_unit()` reads it out of `SERVICE_TASK`, so renaming
# the unit in the role without rewording the message reds this file instead of
# shipping an order naming a unit that no longer exists.
#
# Only `plexmediaserver` is stopped. The role manages a second unit
# (`plex-watchdog`), and it was checked rather than assumed: the watchdog resolves
# the database glob and hands the paths to `fuser`/`lsof`
# (`plex_blip_watchdog.py:471-474`) — it never opens the database, so it holds no
# read transaction and stopping it would buy the checkpoint nothing.
STOP_FMT = "systemctl stop {unit}"
START_FMT = "systemctl start {unit}"

# A repo-relative path inside the message: at least one directory segment and a
# real extension. This scans the RAW `fail_msg` as YAML parses it, where the
# database is still `{{ plex_library_db }}` — the absolute path only exists after
# templating, so the only slashes here are ones a human typed.
PATH_RE = re.compile(r"(?:[\w.-]+/)+[\w.-]+\.(?:md|yml|yaml|py|sh|json|txt)")

# A clause ends at sentence punctuation or a closing quote, either one followed
# by whitespace. `'PRAGMA wal_checkpoint(TRUNCATE);' See the ...` is two clauses
# and only the second is talking about the file that follows it; without this the
# inline remedy would be read as a promise about the runbook.
CLAUSE_END_RE = re.compile(r"(?:[.;:]|['\"])\s")

WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# Words shorter than this are articles and prepositions ("see", "the", "in");
# words this long or longer are the claim. There is deliberately NO stopword
# list: a stopword list is a knob, and the first thing it would ever be turned to
# is exempting the one word that made a promise false. The cost is that the
# pointer clause must be worded in the target's own vocabulary, which is the
# point of it.
CLAIM_WORD_MIN = 4

BLOCK_KEYS = ("block", "rescue", "always")


def _load(path: pathlib.Path):
    return yaml.safe_load(path.read_text()) if path.is_file() else None


def _iter_tasks(tasks):
    """Every task in a task list, with block/rescue/always flattened.

    Recursive because blocks nest, and because a top-level-only walk is the
    documented miss in `test_plex_watchdog_deps_shape.py` (`docker_host`'s role
    already nests apt tasks inside one).
    """
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        yield task
        for section in BLOCK_KEYS:
            yield from _iter_tasks(task.get(section))


def _role_tasks():
    return list(_iter_tasks(_load(PLEX_TASKS)))


def _named(name: str):
    """The one task with this `name:`, or None. Ambiguity is not None."""
    hits = [task for task in _role_tasks() if task.get("name") == name]
    return hits[0] if len(hits) == 1 else None


def _module_args(task, *keys):
    """The first present module's args dict, under any of its spellings."""
    for key in keys:
        args = (task or {}).get(key)
        if isinstance(args, dict):
            return args
    return None


def _assert_that():
    """The assert task's `that:` conditions, normalised to a list of strings."""
    args = _module_args(_named(ASSERT_TASK), "ansible.builtin.assert", "assert")
    that = (args or {}).get("that")
    if isinstance(that, str):
        that = [that]
    return [str(item) for item in (that or [])]


def _defaults():
    return _load(PLEX_DEFAULTS) or {}


def _fail_msg():
    """The assert task's `fail_msg`, raw — before Jinja, as the file carries it."""
    args = _module_args(_named(ASSERT_TASK), "ansible.builtin.assert", "assert")
    return str((args or {}).get("fail_msg", ""))


def _managed_unit():
    """The systemd unit the role itself manages, or None. Read, never declared."""
    args = _module_args(
        _named(SERVICE_TASK),
        "ansible.builtin.systemd",
        "systemd",
        "ansible.builtin.service",
        "service",
    )
    return str((args or {}).get("name", "")) or None


def _remedy_defects(message: str, unit: str):
    """Every way the ordered remedy is not runnable as written. [] is honest.

    The checkpoint alone is not a remedy — it is the middle of one. Two failure
    modes, and round 2's shipped message had the first: a step missing entirely,
    and the three steps present but in an order that does not work. Order IS the
    content here, so it is checked positionally rather than by presence.
    """
    defects = []
    stop, start = STOP_FMT.format(unit=unit), START_FMT.format(unit=unit)
    steps = (("stop", stop), ("checkpoint", CHECKPOINT_STMT), ("start", start))
    for label, needle in steps:
        if needle not in message:
            defects.append(f"no {label}: {needle!r} absent")
    if not defects:
        at = [message.index(needle) for _, needle in steps]
        if not at[0] < at[1] < at[2]:
            defects.append(
                "out of order: "
                + " ".join(f"{label}@{index}" for (label, _), index in zip(steps, at))
            )
    return defects


def _named_paths(message: str):
    """Every repo path the message points at, first occurrence order, deduped."""
    found = []
    for match in PATH_RE.finditer(message):
        if match.group(0) not in found:
            found.append(match.group(0))
    return found


def _pointer_clause(message: str, path: str) -> str:
    """The clause that introduces `path` — what the message promises OF it.

    Everything between the last clause boundary before the path and the path
    itself. Read out of the message rather than declared here, so a reworded
    pointer is re-checked rather than grandfathered.
    """
    head = message.split(path, 1)[0]
    ends = [match.end() for match in CLAUSE_END_RE.finditer(head)]
    return head[ends[-1]:] if ends else head


def _pointer_defects(message: str):
    """Every way `message` orders something this repo cannot obey. [] is honest.

    Two failure modes, and the shipped round-1 message had the second one: a path
    that does not resolve, and a path that resolves to a file not carrying what
    the sentence around it claims. Both are checked against the working tree, so
    this stays true as the pointed-at files change under later rows.
    """
    defects = []
    for path in _named_paths(message):
        target = REPO_ROOT / path
        if not target.is_file():
            defects.append(f"{path}: no such file")
            continue
        text = target.read_text().lower()
        clause = _pointer_clause(message, path)
        missing = [
            word
            for word in WORD_RE.findall(clause)
            if len(word) >= CLAIM_WORD_MIN and word.lower() not in text
        ]
        if missing:
            defects.append(f"{path}: does not carry {missing}")
    return defects


# --- Static rows -----------------------------------------------------------


def test_the_wal_guard_is_three_tasks_and_all_three_exist() -> bool:
    """Anti-vacuity: every other row locates its subject through these names.

    A rename makes `_named()` return None, at which point "the condition does not
    mention the sqlite3 register" and "the fail_msg has no positional pointer"
    are both true of nothing, and the behavioural harness lifts an empty task
    list. This row is what makes the rest mean anything.

    It also pins the SPLIT as a shape: the journal-mode audit is a `command`, the
    WAL measurement is a `stat`, and the threshold check is an `assert`. Collapse
    any two and this reds.
    """
    audit = _module_args(_named(AUDIT_TASK), "ansible.builtin.command", "command")
    stat = _module_args(_named(STAT_TASK), "ansible.builtin.stat", "stat")
    check = _module_args(_named(ASSERT_TASK), "ansible.builtin.assert", "assert")
    ok = all(part is not None for part in (audit, stat, check))
    print(
        f"{'OK' if ok else 'FAIL'}: the WAL audit is three tasks "
        f"(command={audit is not None} stat={stat is not None} "
        f"assert={check is not None})"
    )
    return ok


def test_the_size_guard_does_not_depend_on_the_sqlite3_audit() -> bool:
    """The split, asserted where it is load-bearing: in the CONDITION.

    `sqlite3` is absent from the dev box, so any `that:` clause reaching for
    `plex_sqlite_wal` makes the whole guard undemonstrable off a deployed host —
    the condition would then be scored against a task that died rc=2 on a missing
    binary rather than on WAL size. The three behavioural rows below run the stat
    and assert tasks WITHOUT the command task, which is only a faithful
    reproduction of the role while this holds.

    The `stat` task is checked too: a `when:` on it (its own) would leave
    `plex_wal` undefined and turn the assert into an error rather than a verdict.
    """
    conditions = _assert_that()
    clean = bool(conditions) and not any(AUDIT_REGISTER in c for c in conditions)
    stat_task = _named(STAT_TASK) or {}
    assert_task = _named(ASSERT_TASK) or {}
    ungated = "when" not in stat_task and "when" not in assert_task
    ok = clean and ungated
    print(
        f"{'OK' if ok else 'FAIL'}: the size condition stands on {WAL_REGISTER} "
        f"alone (mentions_{AUDIT_REGISTER}={not clean} ungated={ungated}) "
        f"-> that={conditions}"
    )
    return ok


def test_the_journal_mode_audit_opens_the_database_readonly() -> bool:
    """The `-readonly` charge, carried by the row that rewrites this invocation.

    A lock-contention audit that opens the library database read-write is the
    diagnostic taking part in the fault it measures. plan.md Step 8 makes "every
    sqlite3 invocation carries -readonly" a shape test five steps out; the
    cheapest moment to fix an invocation is inside the edit that touches it.

    Read off the parsed `argv:`, not the file text — `sqlite3` is also a package
    name in this role, so "the string is in the file" attributes nothing.
    """
    args = _module_args(_named(AUDIT_TASK), "ansible.builtin.command", "command")
    argv = [str(item) for item in (args or {}).get("argv") or []]
    is_sqlite = bool(argv) and argv[0] == SQLITE_BIN
    readonly = READONLY_FLAG in argv
    ok = is_sqlite and readonly
    print(
        f"{'OK' if ok else 'FAIL'}: the journal-mode audit runs "
        f"{SQLITE_BIN} {READONLY_FLAG} (argv[0]={argv[0] if argv else None!r} "
        f"readonly={readonly}) -> argv={argv}"
    )
    return ok


def test_the_stat_measures_the_wal_of_the_audited_database() -> bool:
    """PAIRING: the file that is stat'ed must be the WAL of the file audited.

    Two independent greps are not this check. A stat of some other `-wal`, or of
    a path built from a second spelling of the database location, is green under
    "a stat task exists" and measures a file the audit never opens. So both paths
    are read from the parsed tasks and required to be the SAME variable, with the
    stat's path exactly that variable plus SQLite's own `-wal` suffix.

    The variable itself is pinned to the state dir, so a `plex_state_dir`
    override moves the audit and the guard together.
    """
    audit = _module_args(_named(AUDIT_TASK), "ansible.builtin.command", "command")
    stat = _module_args(_named(STAT_TASK), "ansible.builtin.stat", "stat")
    argv = [str(item) for item in (audit or {}).get("argv") or []]
    db_ref = "{{ " + DB_VAR + " }}"
    audited = db_ref in argv
    stat_path = str((stat or {}).get("path", ""))
    paired = stat_path == f"{db_ref}-wal"
    declared = str(_defaults().get(DB_VAR, ""))
    derived = "{{ " + STATE_DIR_VAR + " }}" in declared and declared.endswith(".db")
    ok = audited and paired and derived
    print(
        f"{'OK' if ok else 'FAIL'}: the stat measures {db_ref}-wal, the WAL of "
        f"the audited db (audited={audited} paired={paired} "
        f"derived_from_{STATE_DIR_VAR}={derived}) -> stat.path={stat_path!r}"
    )
    return ok


def test_the_threshold_is_a_role_default_and_the_condition_reads_it() -> bool:
    """`plex_wal_max_bytes: 8388608` in defaults, and the guard uses the NAME.

    Both halves, because either alone is vacuous: a default nothing reads is
    dead config, and a condition comparing against a literal 8388608 is a
    threshold no override can move — `-e plex_wal_max_bytes=...` would silently
    do nothing, and that is the knob the runbook tells an operator to turn.
    """
    default = _defaults().get(THRESHOLD_VAR)
    declared = isinstance(default, int) and default == THRESHOLD_DEFAULT
    conditions = _assert_that()
    by_name = any(THRESHOLD_VAR in c for c in conditions)
    literal = any(str(THRESHOLD_DEFAULT) in c for c in conditions)
    ok = declared and by_name and not literal
    print(
        f"{'OK' if ok else 'FAIL'}: {THRESHOLD_VAR} defaults to "
        f"{THRESHOLD_DEFAULT} and the condition reads it by name "
        f"(declared={default!r} by_name={by_name} hardcoded={literal})"
    )
    return ok


def test_the_fail_msg_names_the_observed_size_and_the_threshold() -> bool:
    """plan.md:157-158 — the failure must name BOTH numbers.

    "The WAL is too big" sends an operator to measure what the play already
    measured. The message carries the observed size and the threshold it broke,
    and both by VARIABLE: a message quoting 8388608 as text goes stale the first
    time the default moves, which is the same hardcode the row above forbids in
    the condition.

    The observed size is required to be `default()`-guarded, and that is a
    measured requirement rather than a stylistic one. `fail_msg` is templated
    during task-arg finalization — BEFORE the assertion is evaluated and
    regardless of its verdict — so a bare `{{ plex_wal.stat.size }}` reds the
    play on a host with NO WAL, where `stat.exists` is false and `stat` carries
    no `size` at all: "Error while resolving value for 'fail_msg': object of type
    'dict' has no attribute 'size'". That is the absent-WAL polarity failing
    through the message rather than through the condition, which is why
    test_an_absent_wal_does_not_fail_the_play runs the real tasks instead of
    reasoning about them.
    """
    args = _module_args(_named(ASSERT_TASK), "ansible.builtin.assert", "assert")
    message = str((args or {}).get("fail_msg", ""))
    size_ref = f"{WAL_REGISTER}.stat.size"
    observed = size_ref in message
    threshold = THRESHOLD_VAR in message
    literal = str(THRESHOLD_DEFAULT) in message
    guarded = observed and "default(" in message.split(size_ref, 1)[1].split("}}")[0]
    ok = observed and threshold and guarded and not literal
    print(
        f"{'OK' if ok else 'FAIL'}: fail_msg names the observed size and the "
        f"threshold, both by variable (observed={observed} threshold={threshold} "
        f"size_default_guarded={guarded} hardcoded={literal}) -> {message!r}"
    )
    return ok


def test_the_fail_msg_orders_a_remedy_this_repo_can_obey() -> bool:
    """The half of the message an operator ACTS on, pinned as a literal.

    A guard that fires at 03:00 has one job past naming the numbers: say what to
    do. Round 1 said "Run the checkpoint in <runbook>" and there is no checkpoint
    in that runbook, nor anywhere in this repo. The fix is not a better pointer —
    it is that the remedy is ONE STATEMENT and therefore belongs in the message,
    where it is true today and depends on no other row landing.

    Three things, and each is a way the sentence stops being runnable: the binary
    (`sqlite3`), the database BY VARIABLE (so the printed command names the same
    file the guard just stat'ed, rather than a second spelling of its path), and
    the statement itself.

    And `-readonly` must NOT appear: the audit above carries it because a read is
    all it needs, but a checkpoint WRITES — a copy-pasted `-readonly` checkpoint
    dies "attempt to write a readonly database", which is the same guard handing
    an operator a command that cannot work.
    """
    message = _fail_msg()
    binary = SQLITE_BIN in message
    db_ref = "{{ " + DB_VAR + " }}"
    by_variable = db_ref in message
    statement = CHECKPOINT_STMT in message
    writable = READONLY_FLAG not in message
    ok = binary and by_variable and statement and writable
    print(
        f"{'OK' if ok else 'FAIL'}: fail_msg names a runnable remedy "
        f"({SQLITE_BIN}={binary} db_by_variable={by_variable} "
        f"checkpoint={statement} not_readonly={writable}) -> {message!r}"
    )
    return ok


def test_the_fail_msg_orders_the_checkpoint_with_its_precondition() -> bool:
    """The checkpoint is INERT in the only state this guard is ever red.

    Round 2 fixed a pointer at nothing by naming the statement inline, and the
    statement is right. But the guard fires only while the WAL is large, and the
    WAL is large only while Plex holds a read transaction — which is exactly the
    condition under which `wal_checkpoint(TRUNCATE)` returns `busy` and moves
    nothing (Critic, DEC-244; re-measured at
    `logs/builder-3b-r3-sqlite-probe.txt`, see `CHECKPOINT_STMT`). `busy` is a
    result row and the CLI exits 0, so round 1 handed the operator a pointer to
    nothing and round 2 handed them a command that reports success and does
    nothing. Same operator, same 03:00.

    So the remedy is three ordered steps and the pin closes over all three: stop
    the unit THE ROLE MANAGES, checkpoint, start it again. Order is the content —
    a message carrying all three tokens with the checkpoint outside the stop is
    the same inert command with more words — so it is checked positionally.

    ARMED IN-ROW against both, neither probe worded like the shipped message:
    round 2's own message reconstructed (the checkpoint with no stop at all), and
    a message with every step present but the checkpoint running live. If either
    reads clean the checker cannot see the bug it was written for.
    """
    message = _fail_msg()
    unit = _managed_unit()
    defects = _remedy_defects(message, unit) if unit else ["no unit: role manages none"]
    probes = {
        "round 2's checkpoint with no stop": (
            f"""Checkpoint it: sqlite3 "{{{{ {DB_VAR} }}}}" '{CHECKPOINT_STMT}'"""
        ),
        "all three steps, checkpoint outside the stop": (
            f"Run '{CHECKPOINT_STMT}', then {STOP_FMT.format(unit=unit)} "
            f"and {START_FMT.format(unit=unit)}."
        ),
    }
    caught = {label: _remedy_defects(probe, unit or "") for label, probe in probes.items()}
    armed = bool(unit) and all(bool(found) for found in caught.values())
    ok = bool(unit) and not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: fail_msg orders the checkpoint between a stop "
        f"and a start of the role's own unit (unit={unit!r} defects={defects} "
        f"probes_caught={ {label: len(found) for label, found in caught.items()} })"
    )
    return ok


def test_every_file_the_fail_msg_points_at_carries_what_it_promises() -> bool:
    """Read the paths back OUT of the message; hold each to its own sentence.

    This row is told nothing. It extracts whatever the message points at, and for
    each one requires (1) the file exists and (2) it carries every claim word of
    the clause that introduces it. A message may still point at a document — it
    may just not lie about what is in there.

    ARMED IN-ROW, because the honest case alone would be green over a broken
    extractor. Two probes, neither of them worded like the shipped message:

      * the parent's exact defect, reconstructed against the SAME file the
        message names today — promising a `wal_checkpoint` procedure the runbook
        does not contain. If this passes, the checker cannot see the bug it was
        written for.
      * a pointer at a file that is not there — Critic mutant N1.

    Requiring at least one path is the third half of the anti-vacuity: a message
    that points nowhere would satisfy "every path resolves" by having none.
    """
    message = _fail_msg()
    named = _named_paths(message)
    defects = _pointer_defects(message)
    probes = {
        "promises a remedy the target does not carry": (
            f"Run the wal_checkpoint procedure in {named[0]}." if named else ""
        ),
        "points at a file that is not there": (
            "See the checkpoint in docs/runbooks/does-not-exist.md."
        ),
    }
    caught = {label: _pointer_defects(probe) for label, probe in probes.items()}
    armed = all(bool(found) for found in caught.values())
    ok = bool(named) and not defects and armed
    print(
        f"{'OK' if ok else 'FAIL'}: every file fail_msg points at exists and "
        f"carries its promise (named={named} defects={defects} "
        f"probes_caught={ {label: len(found) for label, found in caught.items()} })"
    )
    return ok


def test_the_stat_does_not_checksum_the_wal() -> bool:
    """`get_checksum: false` — the diagnostic must not read what it measures.

    `ansible.builtin.stat` defaults `get_checksum: true`. Every other stat in
    this repo stats a DIRECTORY (`site.yml:19`, `tasks/main.yml:102`, `:199`),
    where that default costs nothing. This is the first stat of a large regular
    file, so on CT 110 it sha1s a ~42 MiB write-ahead log Plex is actively
    appending to, on every play — the same class as this task's own `-readonly`
    charge, a lock-contention audit taking part in the fault it measures.

    Pinned as identity rather than truthiness: `get_checksum: "no"` parses to the
    string `"no"` under some spellings, and a key present with a wrong value is
    the shape this row exists to keep out. The guard reads `stat.exists` and
    `stat.size` and nothing else.
    """
    stat = _module_args(_named(STAT_TASK), "ansible.builtin.stat", "stat") or {}
    present = "get_checksum" in stat
    ok = present and stat.get("get_checksum") is False
    print(
        f"{'OK' if ok else 'FAIL'}: the WAL stat does not checksum the file "
        f"(present={present} value={stat.get('get_checksum')!r})"
    )
    return ok


# --- Behavioural rows: drive the ROLE'S OWN tasks --------------------------


def _lifted_tasks():
    """The stat and assert tasks, lifted verbatim from the role, in file order."""
    return [task for task in _role_tasks() if task.get("name") in (STAT_TASK, ASSERT_TASK)]


def _guard_playbook(tasks):
    """A localhost play whose task list IS the role's, with nothing added."""
    return [
        {
            "hosts": "localhost",
            "connection": "local",
            "gather_facts": False,
            "tasks": copy.deepcopy(tasks),
        }
    ]


def _run_guard(wal_bytes):
    """Run the role's WAL tasks against a fixture WAL of `wal_bytes`, or none.

    `wal_bytes is None` builds the fixture directory WITHOUT a `-wal` file, which
    is a fresh Plex install and the case a naive `stat.size < N` gets backwards.

    The threshold comes from the role's real defaults file (loaded as extra vars)
    so the run is scored against the shipped number; only the database path is
    overridden, and it is overridden LAST so it wins.

    Returns (rc, combined output).
    """
    tasks = _lifted_tasks()
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        database = root / "com.plexapp.plugins.library.db"
        database.write_bytes(b"")
        if wal_bytes is not None:
            wal = root / (database.name + "-wal")
            with wal.open("wb") as handle:
                handle.truncate(wal_bytes)
        playbook = root / "wal-guard.yml"
        playbook.write_text(yaml.safe_dump(_guard_playbook(tasks), sort_keys=False))
        proc = subprocess.run(
            [
                "mise", "exec", "--", "ansible-playbook",
                "-i", "localhost,",
                "-c", "local",
                "-e", f"@{PLEX_DEFAULTS}",
                "-e", json.dumps({DB_VAR: str(database)}),
                str(playbook),
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
    return proc.returncode, proc.stdout + proc.stderr


def test_the_behavioural_harness_runs_the_role_s_own_tasks() -> bool:
    """Anti-vacuity for the three runs below: the lift is VERBATIM.

    Without this, `_lifted_tasks()` returning `[]` gives an empty play that exits
    0, and both the green row and the absent row pass while measuring nothing.
    (The red row would catch it — which is the whole reason the differential is
    a pair — but a guard should not need its own sibling to notice it is empty.)

    Verbatim is asserted by identity against the parsed role, not by resemblance:
    both tasks present, in file order, each equal to the dict the role parses to,
    and the assert task carrying a non-empty `that:`.
    """
    lifted = _lifted_tasks()
    names = [task.get("name") for task in lifted]
    ordered = names == [STAT_TASK, ASSERT_TASK]
    verbatim = ordered and all(
        lifted[index] == _named(name)
        for index, name in enumerate((STAT_TASK, ASSERT_TASK))
    )
    played = _guard_playbook(lifted)[0]["tasks"] == lifted
    conditions = _assert_that()
    ok = ordered and verbatim and played and bool(conditions)
    print(
        f"{'OK' if ok else 'FAIL'}: the harness plays the role's own two tasks "
        f"(ordered={ordered} verbatim={verbatim} unmodified_in_play={played} "
        f"conditions={len(conditions)}) -> {names}"
    )
    return ok


def test_the_guard_goes_red_at_the_live_wal() -> bool:
    """RED at 43,735,168 — the number CT 110 has been carrying.

    A guard is only proven by watching it go red. The run must fail AND the
    failure must name both numbers, because a play that dies on a missing
    binary, an undefined variable or a template error also "fails" and would
    read as a catch.
    """
    rc, output = _run_guard(LIVE_WAL_BYTES)
    failed = rc != 0
    observed = str(LIVE_WAL_BYTES) in output
    threshold = str(THRESHOLD_DEFAULT) in output
    ok = failed and observed and threshold
    print(
        f"{'OK' if ok else 'FAIL'}: the WAL guard fails at {LIVE_WAL_BYTES} "
        f"bytes and names both numbers (rc={rc} observed={observed} "
        f"threshold={threshold})"
    )
    if not ok:
        print(output)
    return ok


def test_the_guard_stays_green_at_a_healthy_wal() -> bool:
    """GREEN at 2,097,152 — the other half of the differential.

    Same playbook, same threshold, same fixture layout; only the size differs.
    Without this the red row above is satisfied by a guard that fails always.
    """
    rc, output = _run_guard(HEALTHY_WAL_BYTES)
    ok = rc == 0 and "failed=0" in output
    print(
        f"{'OK' if ok else 'FAIL'}: the WAL guard passes at "
        f"{HEALTHY_WAL_BYTES} bytes (rc={rc})"
    )
    if not ok:
        print(output)
    return ok


def test_an_absent_wal_does_not_fail_the_play() -> bool:
    """A fresh install has no `-wal`, and that must not red the play.

    This is the polarity a naive guard gets backwards twice over: `stat.size < N`
    on an undefined size is an error rather than a pass, and `fail_msg` is
    templated before the verdict, so even a correctly short-circuited condition
    reds here if the message reaches for a size that does not exist. Measured,
    not reasoned: the unguarded spelling of this task dies with "object of type
    'dict' has no attribute 'size'" on exactly this fixture.
    """
    rc, output = _run_guard(None)
    ok = rc == 0 and "failed=0" in output
    print(
        f"{'OK' if ok else 'FAIL'}: an absent WAL leaves the play green "
        f"(rc={rc})"
    )
    if not ok:
        print(output)
    return ok


TESTS = (
    test_the_wal_guard_is_three_tasks_and_all_three_exist,
    test_the_size_guard_does_not_depend_on_the_sqlite3_audit,
    test_the_journal_mode_audit_opens_the_database_readonly,
    test_the_stat_measures_the_wal_of_the_audited_database,
    test_the_threshold_is_a_role_default_and_the_condition_reads_it,
    test_the_fail_msg_names_the_observed_size_and_the_threshold,
    test_the_fail_msg_orders_a_remedy_this_repo_can_obey,
    test_the_fail_msg_orders_the_checkpoint_with_its_precondition,
    test_every_file_the_fail_msg_points_at_carries_what_it_promises,
    test_the_stat_does_not_checksum_the_wal,
    test_the_behavioural_harness_runs_the_role_s_own_tasks,
    test_the_guard_goes_red_at_the_live_wal,
    test_the_guard_stays_green_at_a_healthy_wal,
    test_an_absent_wal_does_not_fail_the_play,
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
