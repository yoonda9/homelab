"""Shape tests for the Plex watchdog systemd unit's ExecStart (Step 4b).

Per .agents/planning/2026-08-07-plex-blip-manual-triage/implementation/plan.md
Step 4 premise 3 — `templates/plex_blip_watchdog.service.j2:9` is the ONLY line
through which the collector directory can reach the watchdog, and editing it is
what arms `task-1786153086-9f13`.

WHY A REFERENCE-CHAIN TEST AND NOT A RENDERED EQUALITY. The obvious instrument
for "an override of `plex_state_dir` moves the guard AND the capture together"
is to render the template twice and compare. It cannot be a gate test: `jinja2`
is `ModuleNotFoundError` under BOTH `python3` and `.venv/bin/python` (measured
at the Step 4a->4b routing, 2026-08-10, parent 6a23d58), and `run_gate.py:54`
runs every `scripts/test_*.py` under `sys.executable`. A `try/except ImportError`
skip would turn that into `OK (skip)` over an unrun check — the vacuous green
this repo has already paid for twice. jinja 3.1.6 DOES exist inside
ansible-core's own venv, so the render survives as the by-hand Demo through
`ansible-playbook`; it is not a guard.

So the relation is pinned where it actually lives — in the RAW TEXT, as a
reference chain:

    ExecStart --db-pattern    -> `{{ plex_library_db }}*`   (a REFERENCE)
    ExecStart --textfile-dir  -> `{{ plex_watchdog_textfile_dir }}`
    tasks/main.yml WAL guard  -> `{{ plex_library_db }}`, `{{ plex_library_db }}-wal`
    defaults plex_library_db  -> `{{ plex_state_dir }}/Library/...`

That is STRICTLY STRONGER against `9f13`'s actual defect than a render would be.
`9f13` is not "the two paths disagree" — measured at `ee7c826` they AGREE, to the
byte. It is "they agree by COINCIDENCE, because they are two hardcoded strings in
two languages." A rendered equality scores today's coincidence and stays green
over it; the chain says the two halves cannot be spelled independently, so
agreement follows from the text rather than from luck. `test_the_two_halves_
follow_one_variable_rather_than_two_literals` is that row, and the mutant it
exists for is the third one in this row's acceptance: the `{{ plex_library_db }}`
reference replaced by the literal path it expands to.

A guard that only checks a flag is PRESENT is the coincidence restated. Both
flag rows therefore assert the VALUE as an exact normalised reference, not
membership — `--db-pattern "/var/lib/plexmediaserver/.../library.db*"` carries
the flag perfectly well and is `9f13` unrepaired.

FALSE CONTRACT, CLOSED IN BOTH DIRECTIONS. A unit that passes a flag `argparse`
does not define does not warn — it exits non-zero on the operator's box and
`Restart=on-failure` retries it forever. The unit and the program are in
different languages and no compiler joins them, so the last two rows read
`files/plex_blip_watchdog.py`'s `add_argument` calls with `ast` (the module is
not importable as a test dependency and must not be executed) and census the
flags BOTH WAYS:

    ExecStart -> argparse   every long flag the unit passes is one the
                            program accepts
    argparse -> ExecStart   every flag the program marks `required=True` is
                            one the unit passes

The second is not implied by the first, and leaving it out is what this file's
round-1 review charged (DEC-265, `logs/critic-4b-mutants.log` C9/C10): with
`--log-path` or `--output-dir` deleted from the ExecStart every other row here
stayed GREEN while the real program exited 2 on `parse_args`. Same symptom,
opposite cause — a permanent crash loop and a unit that has never once run.

WHAT THIS READER DOES AND DOES NOT REACH, stated exactly so the sentence stays
weaker than the guard. It reads the ONE `ExecStart=` line as text and splits it
with `shlex`, which is POSIX shell quoting and not systemd's own; the two agree
on the double-quoted, backslash-free, specifier-free argv this unit carries (no
`%`-specifier, no line continuation, no `ExecStart=` prefix character such as
`-` or `@`), and the first row pins those preconditions rather than assuming
them. It does NOT reach `Environment=`/`EnvironmentFile=` (this unit has
neither), nor flags the watchdog reads from anywhere but argv.

PyYAML (6.0.3) is importable under the gate interpreter. As in
scripts/test_plex_watchdog_deps_shape.py there is deliberately NO try/except
around the import: a missing parser must be a loud ImportError, never a green
badge over an unrun check.

Dual-mode (module-level test_*()->bool + main()->int), mirroring
scripts/test_plex_watchdog_deps_shape.py. The real gate is the standalone exit
code.
"""

import ast
import pathlib
import re
import shlex
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PLEX_ROLE = REPO_ROOT / "ansible" / "roles" / "plex"
PLEX_TASKS = PLEX_ROLE / "tasks" / "main.yml"
PLEX_DEFAULTS = PLEX_ROLE / "defaults" / "main.yml"
UNIT_TEMPLATE = PLEX_ROLE / "templates" / "plex_blip_watchdog.service.j2"
WATCHDOG_SOURCE = PLEX_ROLE / "files" / "plex_blip_watchdog.py"

WATCHDOG_BIN = "/usr/local/bin/plex_blip_watchdog.py"

# The variable names this row's chain is built out of.
STATE_DIR_VAR = "plex_state_dir"
LIBRARY_DB_VAR = "plex_library_db"
TEXTFILE_DIR_VAR = "plex_watchdog_textfile_dir"

# Task names, read as the census key the way the deps shape test does.
COLLECTOR_DIR_TASK = "Ensure the Plex watchdog Prometheus textfile directory exists"
SERVICE_TASK = "Ensure Plex watchdog service is enabled and running"
# Read-only here: these two belong to the Step 3 WAL guard and this row is
# fenced off them. They are named so the JOIN row can assert both halves name
# the same variable — it never modifies them.
JOURNAL_MODE_TASK = "Verify Plex SQLite DB is in WAL mode (read-only audit)"
STAT_TASK = "Stat the Plex SQLite write-ahead log"

# `--db-pattern` is a glob and `plex_library_db` is the file, so the ExecStart
# value is the reference plus SQLite's sibling-file wildcard. Pinned as a
# constant because the suffix is the one character of the value that is NOT the
# reference — and because dropping it narrows the LOCK-HOLDER probes off the
# sidecars, so the capture stops naming WHICH file is contended. See the
# `--db-pattern` row below for what it does and does not buy; measured with a
# real WAL-mode connection at `logs/builder-4b-r3-suffix-holder.log`.
DB_PATTERN_SUFFIX = "*"

# block/rescue/always each carry a task list of their own. Armed by
# `task-1786148389-ffe4`, which measured that nesting a task in a block with
# `when: false` leaves the WAL guard's 14 rows all GREEN — a top-level-only walk
# cannot see either the task or the gate it inherits.
BLOCK_KEYS = ("block", "rescue", "always")
WHEN_KEY = "when"

FILE_KEYS = ("ansible.builtin.file", "file")

# The mode the collector directory needs. node-exporter scrapes the `.prom` as
# its OWN uid while the watchdog (unit line 7: `User=root`) writes it as root,
# so the directory must be traversable and listable by other — `o+rx`. Read as
# the two permission BITS and not as the string "0755", so an equally correct
# `0775` or a symbolic spelling is not a false red.
OTHER_READ = 0o004
OTHER_EXEC = 0o001


def _load(path: pathlib.Path):
    return yaml.safe_load(path.read_text()) if path.is_file() else None


def _iter_tasks(tasks, inherited=()):
    """Every task in a task list, paired with the `when:` gates it sits under.

    Recursive because blocks nest, and the gate is carried DOWN: a task inside a
    gated block is gated even though it holds no `when:` of its own. See
    BLOCK_KEYS for the measurement that arms this.
    """
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        gates = inherited + (
            (f"when: on {task.get('name')!r}",) if WHEN_KEY in task else ()
        )
        yield task, gates
        for section in BLOCK_KEYS:
            yield from _iter_tasks(task.get(section), gates)


def _role_tasks():
    return list(_iter_tasks(_load(PLEX_TASKS)))


def _named(name: str):
    """The one (task, gates) with this `name:`, or (None, ()). Ambiguity is None."""
    hits = [pair for pair in _role_tasks() if pair[0].get("name") == name]
    return hits[0] if len(hits) == 1 else (None, ())


def _task_index(name: str):
    """Position of a named task in the flattened walk, or None."""
    for index, (task, _) in enumerate(_role_tasks()):
        if task.get("name") == name:
            return index
    return None


def _module_args(task, *keys):
    for key in keys:
        args = (task or {}).get(key)
        if isinstance(args, dict):
            return args
    return None


def _defaults():
    return _load(PLEX_DEFAULTS) or {}


def _ref(var: str) -> str:
    """The canonical spelling of a Jinja reference to `var`."""
    return "{{ " + var + " }}"


def _normalise_refs(text: str) -> str:
    """Collapse Jinja whitespace so `{{plex_x}}` and `{{  plex_x  }}` compare equal.

    Whitespace inside the braces is not semantic to Jinja, so an exact string
    equality without this would red on a reformat that changed nothing. Nothing
    else about the value is normalised — the point of these rows is that the
    rest of the value must be empty.
    """
    return re.sub(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}", r"{{ \1 }}", text)


def _exec_start_lines():
    """Every `ExecStart=` line in the unit template, raw."""
    if not UNIT_TEMPLATE.is_file():
        return []
    return [
        line
        for line in UNIT_TEMPLATE.read_text().splitlines()
        if line.strip().startswith("ExecStart=")
    ]


def _exec_start_value():
    """The single ExecStart's right-hand side, or None when it is not single."""
    lines = _exec_start_lines()
    if len(lines) != 1:
        return None
    return lines[0].strip().split("=", 1)[1]


def _exec_argv():
    """The ExecStart value as argv, or None when it cannot be split safely.

    `shlex` is POSIX shell quoting, not systemd's. The precondition rows below
    pin the ways the two could differ on THIS line (a `%` specifier, a
    backslash, a trailing continuation, an `ExecStart=` prefix character) rather
    than leaving the difference unstated.
    """
    value = _exec_start_value()
    if value is None:
        return None
    try:
        return shlex.split(value)
    except ValueError:
        return None


def _flag_value(flag: str):
    """The value of a long flag on the ExecStart, in either spelling.

    Returns None when the flag is absent, and the empty string when it is
    present with no value — the two are different failures and the rows print
    which one they got.
    """
    argv = _exec_argv() or []
    for index, token in enumerate(argv):
        if token == flag:
            return argv[index + 1] if index + 1 < len(argv) else ""
        if token.startswith(flag + "="):
            return token.split("=", 1)[1]
    return None


def _argparse_flag_census():
    """`(accepted, required, unreadable)` — every long option the watchdog
    defines, which of them `argparse` will refuse to start without, and which
    ones this reader could not decide.

    Read and not imported: the module is a standalone script that this repo
    cannot take as a test dependency, and importing it to interrogate its parser
    would execute module-level code inside the gate.

    `required=` counts only when it is the literal `True`, because an `ast` walk
    does not evaluate. The third set carries every flag whose `required=` is
    present but is NOT a literal bool, so the conservative direction is
    REPORTED rather than silently taken.

    That set is not tidiness, and the sentence it replaces over-claimed. Asserting
    `required` is non-empty catches a census that stopped reading `required=`
    ALTOGETHER; it does nothing about a census blinded on ONE flag, which leaves
    the set non-empty and the dropped flag invisible — measured, green over a
    program that still exits 2 (`logs/critic-4b-r2-mutants.log` V4). Non-emptiness
    is the mitigation for total blinding; this set is the mitigation for partial.
    """
    accepted, required, unreadable = set(), set(), set()
    if not WATCHDOG_SOURCE.is_file():
        return accepted, required, unreadable
    tree = ast.parse(WATCHDOG_SOURCE.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "add_argument"):
            continue
        longs = {
            arg.value
            for arg in node.args
            if isinstance(arg, ast.Constant)
            and isinstance(arg.value, str)
            and arg.value.startswith("--")
        }
        accepted |= longs
        for keyword in node.keywords:
            if keyword.arg != "required":
                continue
            literal = isinstance(keyword.value, ast.Constant) and isinstance(
                keyword.value.value, bool
            )
            if not literal:
                unreadable |= longs
            elif keyword.value.value is True:
                required |= longs
    return accepted, required, unreadable


def _value_defect(flag: str):
    """Why this flag's value is unusable to the program, or None when it is fine.

    A flag that is PRESENT is not a flag that carries a value, and the three
    ways it can be present-but-useless are three different `argparse` failures
    — measured with argv rendered by real jinja through `ansible-playbook` and
    run against the real program, with a CONTROL run that stays alive
    (`logs/critic-4b-r2-consequence.log`, re-driven 6/6 at
    `logs/builder-4b-r3-consequence-rerun.log`):

      * `--output-dir` with the next token deleted swallows the FOLLOWING flag
        as its value, so `argparse` exits 2 with `expected one argument` on
        whatever it lost; the value is not `""` but a string starting `--`,
        which is why truthiness alone cannot see it;
      * the same flag as the LAST token has no value at all (`""` here);
      * `--output-dir ""` parses, and the program then dies on the empty path.

    All three are the same crash loop as an absent flag under
    `Restart=on-failure`, and all three left this file 7/7 GREEN before this
    clause (DEC-268 charge 2, `logs/critic-4b-r2-mutants.log` V1-V3).

    It reaches the ExecStart's own argv and nothing else: a value that is a
    variable reference rendering EMPTY is a different defect, pinned by the two
    reference rows above rather than here.
    """
    value = _flag_value(flag)
    if value is None:
        return "absent"
    if not value.strip():
        return "present with no value"
    if value.startswith("--"):
        return f"swallowed the next flag ({value!r})"
    return None


def _passed_long_flags():
    """Every long flag the ExecStart passes, in either spelling."""
    return {
        token.split("=", 1)[0]
        for token in (_exec_argv() or [])
        if token.startswith("--")
    }


def test_the_unit_has_one_exec_start_this_reader_can_read() -> bool:
    """Anti-vacuity, and the precondition for `shlex` standing in for systemd.

    Every other row here reaches the unit through `_exec_argv()`. If the
    template is renamed, gains a second `ExecStart=`, or is spelled in a way
    POSIX splitting reads differently from systemd, those rows would score an
    empty argv — and `"--textfile-dir" not in []` reads exactly like a correct
    absence. This row is what makes the others mean something.

    The four preconditions are the ways THIS line could diverge between the two
    quoting rules, and they are asserted rather than assumed:
      * no `%` — systemd expands unit specifiers, `shlex` does not;
      * no backslash — the two escape differently outside double quotes;
      * no trailing `\\` continuation, which would put argv on a line this
        reader never sees;
      * no `-`/`@`/`:`/`+`/`!` prefix character between `ExecStart=` and the
        binary, which changes systemd's execution semantics and would make the
        first token something other than the program.
    """
    lines = _exec_start_lines()
    single = len(lines) == 1
    value = _exec_start_value() or ""
    argv = _exec_argv()
    no_specifier = "%" not in value
    no_escape = "\\" not in value
    unprefixed = bool(value) and value[0] not in "-@:+!"
    runs_watchdog = bool(argv) and argv[0] == WATCHDOG_BIN
    ok = (
        single
        and argv is not None
        and no_specifier
        and no_escape
        and unprefixed
        and runs_watchdog
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {UNIT_TEMPLATE.name} has exactly one "
        f"ExecStart running {WATCHDOG_BIN} and POSIX splitting is safe on it "
        f"(count={len(lines)} splittable={argv is not None} "
        f"no_specifier={no_specifier} no_escape={no_escape} "
        f"unprefixed={unprefixed} runs_watchdog={runs_watchdog})"
    )
    return ok


def test_exec_start_passes_the_textfile_dir_as_a_variable_reference() -> bool:
    """`--textfile-dir` is passed, and its value is the VARIABLE, not a path.

    4c's row says its `--collector.textfile.directory` points at "the same
    variable 4b writes into". A literal here makes that two literals that agree,
    which is `9f13` in a second container — so this row scores the value as an
    exact reference and not as membership.

    The variable must also EXIST in the role's defaults with an absolute path:
    an ExecStart naming an undefined variable renders as the empty string under
    ansible's default `jinja2_native`-off templating and hands the watchdog
    `--textfile-dir ""`, which `plex_blip_watchdog.py:720` reads as falsy and
    silently writes no metrics at all — a green unit publishing nothing.
    """
    value = _flag_value("--textfile-dir")
    is_ref = value is not None and _normalise_refs(value) == _ref(TEXTFILE_DIR_VAR)
    default = _defaults().get(TEXTFILE_DIR_VAR)
    defined = isinstance(default, str) and default.startswith("/")
    ok = is_ref and defined
    print(
        f"{'OK' if ok else 'FAIL'}: ExecStart passes --textfile-dir as "
        f"{_ref(TEXTFILE_DIR_VAR)!r} and the variable is an absolute path in "
        f"defaults (value={value!r} is_reference={is_ref} "
        f"{TEXTFILE_DIR_VAR}={default!r} defined={defined})"
    )
    return ok


def test_exec_start_passes_the_db_pattern_as_a_variable_reference() -> bool:
    """`--db-pattern` is passed, and its value is `{{ plex_library_db }}*`.

    THIS IS THE `9f13` ROW. Before this edit the ExecStart passed `--log-path`
    and `--output-dir` only, so the watchdog ran on `argparse`'s hardcoded
    default — a string that matches `plex_library_db`'s expansion today by
    coincidence and stops matching it the moment `plex_state_dir` is overridden.

    Scored as an EXACT normalised equality against the reference plus SQLite's
    sibling wildcard, which is what makes the acceptance's third mutant red: the
    reference replaced by the literal path it currently expands to carries the
    flag, carries the glob, resolves to the same file today, and is precisely
    the defect. Membership could not tell the two apart.

    THE SUFFIX IS PINNED TOO, AND FOR A REASON THAT WAS MEASURED RATHER THAN
    REASONED — the first version of this sentence was neither, and was false.
    It said dropping the `*` narrows the WAL FIGURES, on the grounds that
    `_wal_state` is fed by this glob. It is not fed by the glob's match SET:
    `capture_snapshot` hands it `_base_db(matched_dbs)`, the ONE match ending in
    `.db`, and `_wal_state` then derives `-wal`/`-shm` by string CONCATENATION
    (`_size(db_path + "-wal" ...)`, cited by ANCHOR rather than by line: this
    repo has already measured a citation whose corrected line numbers died one
    commit later, `task-1786157581-f7a7`). `glob.glob` on a metacharacter-free
    path returns that path, so `db_bytes`/`wal_bytes`/`shm_bytes` come back
    byte-identical with the suffix and without it — measured over one fixture,
    two real runs, `--dry-run` not set (`logs/builder-4b-r2-suffix.log` R1).

    What the suffix actually buys is the OTHER consumer of the same glob. The
    match set is also `targets` for the lock-holder probes (`_run_cmd(["fuser",
    "-v"] + targets)` in `capture_snapshot`), so without the `*` both probes are
    asked about the `.db` alone.

    IT DOES NOT MAKE THE HOLDER INVISIBLE, and the previous version of this
    paragraph said it did — the second false sentence this row has shipped in
    the same place, which is why it is stated here at the length it is. A SQLite
    connection holds the `.db` as well as its `-wal`, so asking about the `.db`
    alone already returns that process. Measured (DEC-268, re-measured at
    `logs/builder-4b-r3-suffix-holder.log`) with a real WAL-mode connection left
    mid-transaction and the real CLI, `--dry-run` not set: the holder pid is
    named by `fuser` AND by `lsof`, with the suffix and without it (R2). The
    round-2 fixture that produced the false claim held the `-wal` with a bare
    `open()` and nothing on the `.db`, so its narrow probe had no holder to find
    — the fixture was wrong, not the probes.

    WHAT CHANGES IS WHICH FILE THE CAPTURE NAMES, AND WITH WHAT ACCESS. With the
    `*` the probes report the sidecar itself: `lsof` emits its own FD row,
    `4u REG ... .db-wal`, mode column included, and `fuser` gives it its own
    section (R3/R4). Without it the operator gets a pid and nothing saying the
    contention is on the write-ahead log at all. That is the difference between
    "something holds the library" and "this process has the WAL open for
    writing", and the second is the question a lock-contention capture exists to
    answer.

    Both halves are worth keeping in mind for `task-1786152669-ffe0`: the `*` is
    also what lets a SECOND `.db`-ending neighbour into `base_dbs`, so this
    character is the entry point to that filing rather than a defence against it.
    """
    value = _flag_value("--db-pattern")
    expected = _ref(LIBRARY_DB_VAR) + DB_PATTERN_SUFFIX
    is_ref = value is not None and _normalise_refs(value) == expected
    print(
        f"{'OK' if is_ref else 'FAIL'}: ExecStart passes --db-pattern as "
        f"{expected!r} — the reference, not the literal it expands to "
        f"(value={value!r})"
    )
    return is_ref


def test_the_two_halves_follow_one_variable_rather_than_two_literals() -> bool:
    """THE JOIN, as a theorem about the text: ONE variable reaches both halves.

    `task-1786153086-9f13`, measured at `ee7c826` over one fabricated fault: the
    role's WAL guard and the watchdog's capture agree to the byte — and nothing
    pins the agreement, because it rests on two hardcoded strings in two
    languages. Set `plex_state_dir=/srv/plex` and the guard moves while the
    watchdog stays at `/var/lib/...`; the guard then reds correctly on the real
    WAL while every capture records `sqlite: all-null`, which is indistinguishable
    from "WAL mode is off".

    This row asserts the three consumers name ONE variable and none of them
    carries the expansion:
      * the journal-mode audit's `argv` -> `{{ plex_library_db }}`
      * the WAL `stat`'s `path`        -> `{{ plex_library_db }}-wal`
      * the ExecStart's `--db-pattern` -> `{{ plex_library_db }}*`
    plus the chain's own root: `plex_library_db` in defaults is DERIVED from
    `{{ plex_state_dir }}` rather than being a fourth literal.

    With all four true, "an override of `plex_state_dir` moves the guard AND the
    capture together" follows from the text — it is not an experiment, and it is
    not this cut's coincidence re-measured. The two Step 3 tasks are read
    strictly READ-ONLY here; this row is fenced off editing them.
    """
    audit, _ = _named(JOURNAL_MODE_TASK)
    stat, _ = _named(STAT_TASK)
    argv = (_module_args(audit, "ansible.builtin.command", "command") or {}).get("argv")
    argv = [str(item) for item in (argv or [])]
    stat_path = (_module_args(stat, "ansible.builtin.stat", "stat") or {}).get("path")
    audit_follows = any(
        _normalise_refs(item) == _ref(LIBRARY_DB_VAR) for item in argv
    )
    stat_follows = isinstance(stat_path, str) and _normalise_refs(
        stat_path
    ) == _ref(LIBRARY_DB_VAR) + "-wal"
    pattern = _flag_value("--db-pattern")
    capture_follows = pattern is not None and _normalise_refs(pattern) == _ref(
        LIBRARY_DB_VAR
    ) + DB_PATTERN_SUFFIX
    library_db = _defaults().get(LIBRARY_DB_VAR)
    rooted = isinstance(library_db, str) and _ref(STATE_DIR_VAR) in _normalise_refs(
        library_db
    )
    state_dir = _defaults().get(STATE_DIR_VAR)
    root_defined = isinstance(state_dir, str) and state_dir.startswith("/")
    ok = audit_follows and stat_follows and capture_follows and rooted and root_defined
    print(
        f"{'OK' if ok else 'FAIL'}: the WAL guard and the watchdog capture both "
        f"follow {_ref(LIBRARY_DB_VAR)}, which derives from {_ref(STATE_DIR_VAR)} "
        f"(audit={audit_follows} stat={stat_follows} capture={capture_follows} "
        f"rooted={rooted} root_defined={root_defined}) -> argv={argv} "
        f"stat_path={stat_path!r} db_pattern={pattern!r}"
    )
    return ok


def test_the_collector_directory_is_created_by_reference_and_ungated() -> bool:
    """The role creates the directory, names it by REFERENCE, and never skips.

    Three claims, and each is a way the wiring fails while the ExecStart stays
    perfect:

    BY REFERENCE — a `path:` literal here is the third spelling of the same
    directory (ExecStart, this task, and 4c's `--collector.textfile.directory`),
    and two of the three drifting apart is `9f13` again.

    OWNERSHIP AND MODE — the watchdog writes as root (unit line 7) and
    node-exporter scrapes as its own uid, so `other` needs `r-x` on the
    directory or the collector cannot even open it. Scored as the two permission
    BITS, not as the literal string `"0755"`, so a stricter-but-still-correct
    spelling is not a false red.

    UNGATED — read as the `when:` KEY and never as a VALUE, and read at the
    CENSUS's reach so a gate inherited from an enclosing `block:` counts.
    `task-1786148389-ffe4` measured exactly this: nesting a task in a
    `when: false` block leaves the WAL guard's 14 rows all GREEN. A skipped
    directory task leaves the watchdog's own `os.makedirs` (:727) to create it
    root-owned at the process umask, which is the silent divergence from the
    mode this row just argued for.

    ORDER — the directory task must precede the service task. The unit starts
    the watchdog, and 4c's node-exporter will scrape the directory; creating it
    afterwards converges eventually but leaves the first play's ordering
    dependent on `os.makedirs` rather than on the role.
    """
    task, gates = _named(COLLECTOR_DIR_TASK)
    args = _module_args(task, *FILE_KEYS) or {}
    path = args.get("path")
    by_reference = isinstance(path, str) and _normalise_refs(path) == _ref(
        TEXTFILE_DIR_VAR
    )
    is_directory = args.get("state") == "directory"
    mode = args.get("mode")
    try:
        bits = int(str(mode), 8)
    except (TypeError, ValueError):
        bits = 0
    readable = bool(bits & OTHER_READ) and bool(bits & OTHER_EXEC)
    root_owned = args.get("owner") == "root"
    ungated = not gates
    dir_index, service_index = _task_index(COLLECTOR_DIR_TASK), _task_index(SERVICE_TASK)
    ordered = (
        dir_index is not None and service_index is not None and dir_index < service_index
    )
    ok = (
        by_reference
        and is_directory
        and readable
        and root_owned
        and ungated
        and ordered
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {COLLECTOR_DIR_TASK!r} creates "
        f"{_ref(TEXTFILE_DIR_VAR)} as a root-owned world-readable directory, "
        f"ungated, before the service starts (by_reference={by_reference} "
        f"path={path!r} directory={is_directory} mode={mode!r} "
        f"other_rx={readable} root_owned={root_owned} ungated={ungated} "
        f"gates={list(gates)} ordered={ordered} dir={dir_index} "
        f"service={service_index})"
    )
    return ok


def test_every_flag_the_unit_passes_is_one_argparse_accepts() -> bool:
    """THE FALSE CONTRACT, first of the two directions: ExecStart -> argparse.

    The unit and the watchdog are different languages and nothing joins them. A
    flag `argparse` does not define is not a warning: `parse_args` exits 2, and
    unit line 10 is `Restart=on-failure`, so the operator gets a crash loop and
    a unit that has never once run. That is why this row exists and why it is
    not "`--textfile-dir` is in the source somewhere" — it censuses EVERY long
    flag on the ExecStart against every `add_argument` in the module.

    The converse — a REQUIRED flag the ExecStart stops passing — has the same
    symptom from the opposite cause and is a row of its own, immediately below.
    Neither direction implies the other, which is the whole of DEC-265.

    Read with `ast` rather than imported: the module is a standalone script this
    repo cannot depend on, and importing it would run module-level code inside
    the gate.

    It reaches long flags only. Short flags are not censused because this
    parser defines none, and the ExecStart passes none — named so the sentence
    stays weaker than the guard rather than stronger.
    """
    accepted, _, _ = _argparse_flag_census()
    passed = _passed_long_flags()
    unknown = sorted(passed - accepted)
    # Anti-vacuity: an `ast` walk that found nothing would make `unknown` empty
    # and this row green over a parser it never read.
    parser_read = bool(accepted)
    wired = {"--textfile-dir", "--db-pattern"} <= passed
    ok = parser_read and not unknown and wired
    print(
        f"{'OK' if ok else 'FAIL'}: every long flag the unit passes is defined "
        f"by plex_blip_watchdog.py's argparse (parser_read={parser_read} "
        f"unknown={unknown} passed={sorted(passed)} wired={wired})"
    )
    return ok


def test_every_flag_argparse_requires_is_one_the_unit_passes() -> bool:
    """THE FALSE CONTRACT, second direction: argparse -> ExecStart.

    A flag the program REQUIRES and the unit stops passing produces the
    identical failure to the row above, from the opposite end: `parse_args`
    prints `error: the following arguments are required: --log-path`, exits 2
    before the watchdog opens anything, and `Restart=on-failure` (unit line 10,
    `RestartSec=5`) makes that a permanent crash loop — a unit that has never
    once run.

    MEASURED, not predicted (DEC-265, `logs/critic-4b-mutants.log` C9/C10, and
    re-run at `logs/builder-4b-r2-mutants.log`): deleting `--log-path` or
    `--output-dir` from the ExecStart left the other rows in this file GREEN.
    The census above is directional, and the module docstring claimed a closed
    contract on the strength of it.

    WHY IT IS WORTH A ROW RATHER THAN A NOTE: `task-1786159639-39db` measured
    that an ABSENT Prometheus series cannot match design §5.3's
    `plex_watchdog_probe_status == 0`. A watchdog that never starts publishes no
    `.prom` at all, so the one alert written to catch a silently dead diagnostic
    is exactly the alert a crash loop is invisible to. The two defects compose
    into a telemetry path with no observer.

    PASSING IS NOT CARRYING A VALUE, and scoring only the flag NAME is the
    presence-vs-identity defect this file argues against everywhere else. Three
    mutants that keep the flag and break its value — the next token deleted, the
    flag last on the line, an explicit `""` — left this row GREEN while the real
    program exited 2 or died on the empty path (DEC-268, `logs/critic-4b-r2-
    mutants.log` V1-V3, consequence driven at `logs/critic-4b-r2-consequence.log`
    and re-run at `logs/builder-4b-r3-mutants.log`). `_value_defect` is what
    closes that, and note the shape of V1: the value is not `""` but the NEXT
    FLAG, so a truthiness test passes it.

    TWO ANTI-VACUITY CLAUSES, and they cover different blindings. `required_read`
    catches a census that stopped reading `required=` altogether — the set empties
    and the row would otherwise pass over nothing. `blinded` catches the census
    reading a `required=` it cannot evaluate, which leaves the set NON-empty and
    is invisible to the first (V4). Both costs are stated rather than hidden: if
    a later change legitimately gives every flag a default, or writes a computed
    `required=`, this row REDS and the next hat must revisit it. That is the
    intended prompt.
    """
    accepted, required, unreadable = _argparse_flag_census()
    passed = _passed_long_flags()
    missing = sorted(required - passed)
    unusable = []
    for flag in sorted(required & passed):
        defect = _value_defect(flag)
        if defect is not None:
            unusable.append(f"{flag}: {defect}")
    parser_read = bool(accepted)
    required_read = bool(required)
    blinded = sorted(unreadable)
    ok = parser_read and required_read and not blinded and not missing and not unusable
    print(
        f"{'OK' if ok else 'FAIL'}: every long flag plex_blip_watchdog.py's "
        f"argparse REQUIRES is one the ExecStart passes WITH A USABLE VALUE "
        f"(parser_read={parser_read} required_read={required_read} "
        f"blinded={blinded} missing={missing} unusable={unusable} "
        f"required={sorted(required)} passed={sorted(passed)})"
    )
    return ok


def main() -> int:
    results = [
        test_the_unit_has_one_exec_start_this_reader_can_read(),
        test_exec_start_passes_the_textfile_dir_as_a_variable_reference(),
        test_exec_start_passes_the_db_pattern_as_a_variable_reference(),
        test_the_two_halves_follow_one_variable_rather_than_two_literals(),
        test_the_collector_directory_is_created_by_reference_and_ungated(),
        test_every_flag_the_unit_passes_is_one_argparse_accepts(),
        test_every_flag_argparse_requires_is_one_the_unit_passes(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
