"""Shape tests for node-exporter inside CT 110 (Step 4c, design §4.5).

Per `.agents/planning/2026-08-07-plex-blip-manual-triage/design/detailed-design.md`
§4.5 and `implementation/plan.md` Step 4 — node-exporter is deployed as a systemd
unit with `Nice=10` / `CPUSchedulingPolicy=idle` "mirroring the watchdog unit",
its `--collector.textfile.directory` points at the directory the watchdog writes
into, and collectors that are meaningless in an unprivileged LXC are disabled
rather than fought (R17).

WHAT THIS ROW CANNOT MEASURE, SAID PLAINLY. `prometheus-node-exporter` is a
Debian package and this is a Fedora dev box, so nothing here installs, starts or
scrapes anything. The behavioural half belongs to the operator row
(`code-assist:plex-blip-manual-triage:step-04:operator-demo-grafana`). What this
file proves is the SHAPE of what the role will hand systemd, plus the relations
that keep the three artifacts from drifting apart — and one of those is
measurable here after all: see the render note below.

A MINI-RENDERER, AND WHY THE PRECONDITION IS SCORED AGAINST THE RENDER. The
sibling `test_plex_watchdog_unit_shape.py` reads its `ExecStart` as raw text and
`shlex`-splits it, pinning "no `%`, no backslash" ON THE TEMPLATE. The Step 4b
finalization measured that against real systemd and found the gap: every
interesting token arrives through a VARIABLE, so a `%` reaching the argv through
`plex_state_dir` renders clean, leaves the template `%`-free, and systemd still
expands it (`logs/finalizer-4b-systemd-argv.log`, mem-1786165277-450b). This
file's drop-in is worse off again — it carries a Jinja `{% for %}`, so the
template text contains `%` that is NOT an argv character at all.

So `_render_exec_start()` resolves the line against `defaults/main.yml` first and
every precondition is scored on the RESULT. It understands exactly two
constructs — `{{ scalar }}` and `{% for x in <list> %}...{% endfor %}` — and
returns `None` for anything else, so a template that grows a conditional or a
filter REDS here instead of being read wrong. It is not Jinja and does not claim
to be; it is checked against real Jinja out of band (`ansible-core`'s own venv
carries jinja 3.1.6 — the gate interpreter does not, mem-1786160157-88f1) and
against real systemd's argv, both by the Builder rather than by the gate.

EVERY CROSS-ARTIFACT CLAIM IS A RELATION, NEVER A SECOND LITERAL. This wave's
declared purpose is deleting agreements-by-coincidence (`task-1786153086-9f13`:
two hardcoded strings in two languages that matched to the byte and were pinned
by nothing). So:

    Nice / CPUSchedulingPolicy  read OUT OF plex_blip_watchdog.service.j2
    the collector directory     read OUT OF that unit's --textfile-dir
    the drop-in path            derived from the SAME service variable the
                                systemd task starts
    the disabled collectors     generated from the defaults LIST, not typed
    the listen address          a variable, so Step 4d's scrape job has a
                                second end to pin against

THE ONE LITERAL THAT IS HONEST, and it is `task-1786159051-cb29`. node-exporter's
textfile collector globs `*.prom` and nothing else; a `.metrics` file in the
collector directory is read by nobody, and `mem-1786159649-6e78` measured that an
ABSENT Prometheus series cannot match the `==`/`!=` alert expressions design §5.3
writes over these metrics — so the failure is silent by construction. That suffix
is an UPSTREAM constant: it lives in node-exporter's source, not in this repo,
and there is no second end to relate it to. Pinning it here as a literal with the
rationale named is therefore the truthful instrument rather than a shortcut, and
the row reads `TEXTFILE_NAME` OUT OF the watchdog module rather than restating
it. Typing the suffix a second time in the ROLE would have been the coincidence
this wave exists to delete, so the role does not mention it at all — the role
passes a DIRECTORY and the module owns the name.

Dual-mode (module-level `test_*() -> bool` + `main() -> int`), mirroring
`scripts/test_plex_watchdog_unit_shape.py`. PyYAML (6.0.3) is importable under
the gate interpreter and there is deliberately NO `try/except` around the import:
a missing parser must be a loud ImportError, never a green badge over an unrun
check.
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
WATCHDOG_UNIT = PLEX_ROLE / "templates" / "plex_blip_watchdog.service.j2"
OVERRIDE_TEMPLATE = PLEX_ROLE / "templates" / "prometheus_node_exporter_override.conf.j2"
WATCHDOG_SOURCE = PLEX_ROLE / "files" / "plex_blip_watchdog.py"

# The variables this row's relations are built out of.
TEXTFILE_DIR_VAR = "plex_watchdog_textfile_dir"
PACKAGE_VAR = "plex_node_exporter_package"
SERVICE_VAR = "plex_node_exporter_service"
BIN_VAR = "plex_node_exporter_bin"
LISTEN_VAR = "plex_node_exporter_listen_address"
DISABLED_VAR = "plex_node_exporter_disabled_collectors"

# Task names, read as the census key the way the sibling shape tests do.
INSTALL_TASK = "Install node-exporter for the Plex watchdog textfile collector"
OVERRIDE_DIR_TASK = "Ensure the node-exporter systemd override directory exists"
OVERRIDE_TASK = "Restrain node-exporter and point it at the watchdog textfile directory"
SERVICE_TASK = "Ensure node-exporter is enabled and running"
# Read-only: this task belongs to Step 4b and this row is fenced off editing it.
# It is named so the ORDER row can require the directory to exist before the
# collector is started against it.
COLLECTOR_DIR_TASK = "Ensure the Plex watchdog Prometheus textfile directory exists"

# block/rescue/always each carry a task list of their own. Armed by
# `task-1786148389-ffe4`, which measured that nesting a task in a block with
# `when: false` leaves the WAL guard's 14 rows all GREEN — a top-level-only walk
# cannot see either the task or the gate it inherits.
BLOCK_KEYS = ("block", "rescue", "always")
WHEN_KEY = "when"

APT_KEYS = ("ansible.builtin.apt", "apt")
FILE_KEYS = ("ansible.builtin.file", "file")
TEMPLATE_KEYS = ("ansible.builtin.template", "template")
SYSTEMD_KEYS = ("ansible.builtin.systemd", "ansible.builtin.systemd_service", "systemd")

# The two restraint directives design §4.5 says mirror the watchdog unit. Named
# here as KEYS only — their VALUES are read out of that unit, never typed.
RESTRAINT_KEYS = ("Nice", "CPUSchedulingPolicy")

# systemd's own drop-in layout: a unit's overrides live in `<unit>.d/` beside it
# and each is a `.conf`. Upstream spelling with no in-repo second end, same class
# as TEXTFILE_SUFFIX below.
DROP_IN_ROOT = "/etc/systemd/system"
DROP_IN_SUFFIX = ".service.d"
DROP_IN_FILE = "override.conf"

# node-exporter's textfile collector reads `*.prom` and NOTHING else. An upstream
# constant: it is a glob in node-exporter's source, so this repo holds no second
# end to relate it to and a literal with its rationale stated is the honest pin.
# `task-1786159051-cb29` is the filing this closes — mutating the module's
# TEXTFILE_NAME to "plex_blip.metrics" left the whole suite green over a file
# the collector would never open.
TEXTFILE_SUFFIX = ".prom"
TEXTFILE_NAME_CONST = "TEXTFILE_NAME"

# Collectors that cannot mean anything inside an unprivileged LXC (R17): they
# read host firmware, host sensors, host power and host storage layers, none of
# which are namespaced into CT 110. Required as a SUBSET of the role's list, so
# disabling more is fine and disabling fewer is the defect. Design §9.4 assigns
# kernel and storage evidence to the PVE host (Step 6), which is why the storage
# collectors are here rather than kept for their own sake.
REQUIRED_DISABLED = frozenset(
    {
        "hwmon",
        "thermal_zone",
        "rapl",
        "edac",
        "dmi",
        "nvme",
        "powersupplyclass",
        "infiniband",
        "cpufreq",
        "zfs",
        "btrfs",
        "xfs",
        "mdadm",
    }
)

# The collectors this deployment EXISTS for, which no tidying pass may switch
# off. `textfile` is the delivery mechanism for the whole of design §5.2 —
# disabling it publishes nothing while the unit stays green — and the other five
# are the class-C blind spot plan.md Step 4 names by hand: load average, D-state
# count, PSI, disk I/O latency.
FORBIDDEN_DISABLED = frozenset(
    {"textfile", "loadavg", "stat", "meminfo", "pressure", "diskstats", "filesystem"}
)

# A collector name as node-exporter spells it: the token after `--no-collector.`.
COLLECTOR_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

# The two Jinja constructs `_render_exec_start` understands. Anything else makes
# it return None and every row that depends on it reds.
FOR_RE = re.compile(
    r"\{%-?\s*for\s+(\w+)\s+in\s+(\w+)\s*-?%\}(.*?)\{%-?\s*endfor\s*-?%\}", re.S
)
VAR_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _load(path: pathlib.Path):
    return yaml.safe_load(path.read_text()) if path.is_file() else None


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


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
        if isinstance(args, str):
            return {"_free_form": args}
    return None


def _defaults():
    return _load(PLEX_DEFAULTS) or {}


def _ref(var: str) -> str:
    """The canonical spelling of a Jinja reference to `var`."""
    return "{{ " + var + " }}"


def _normalise_refs(text: str) -> str:
    """Collapse Jinja whitespace so `{{plex_x}}` and `{{  plex_x  }}` compare equal.

    Whitespace inside the braces is not semantic to Jinja, so an exact string
    equality without this would red on a reformat that changed nothing.
    """
    return VAR_RE.sub(r"{{ \1 }}", text)


def _exec_start_lines(path: pathlib.Path):
    """Every `ExecStart=` line in a unit or drop-in, raw and in order."""
    return [
        line.strip()
        for line in _read(path).splitlines()
        if line.strip().startswith("ExecStart=")
    ]


def _directive(path: pathlib.Path, key: str):
    """The single value of a `Key=` directive in a unit file, or None.

    None when the directive is absent OR set more than once, because a repeated
    directive is a different question from an absent one and no caller here may
    silently take the last.
    """
    values = [
        line.strip().split("=", 1)[1]
        for line in _read(path).splitlines()
        if line.strip().startswith(key + "=")
    ]
    return values[0] if len(values) == 1 else None


def _render(text: str, defaults: dict):
    """`text` with the two supported Jinja constructs resolved, or None.

    Not Jinja. It expands `{% for x in <list-variable> %}...{% endfor %}` and
    `{{ scalar-variable }}` against the role defaults and REFUSES everything
    else — a filter, a conditional, a dotted lookup or an undefined name all
    return None rather than a partially-resolved string that would be scored as
    if it were an argv. The refusal is the point: a reader that guesses is worse
    than one that reds, because it agrees with the program on a unit that is
    already wrong.
    """
    guard = 0
    while True:
        match = FOR_RE.search(text)
        if match is None:
            break
        guard += 1
        if guard > 8:
            return None
        loop_var, list_var, body = match.group(1), match.group(2), match.group(3)
        items = defaults.get(list_var)
        if not isinstance(items, list) or not all(
            isinstance(item, str) for item in items
        ):
            return None
        expanded = "".join(
            VAR_RE.sub(
                lambda m, item=item: item if m.group(1) == loop_var else m.group(0),
                body,
            )
            for item in items
        )
        text = text[: match.start()] + expanded + text[match.end() :]

    def _scalar(match):
        value = defaults.get(match.group(1))
        return str(value) if isinstance(value, (str, int)) else "\x00"

    # Substituted to a FIXED POINT, not once: role defaults reference each other
    # (`plex_library_db` is `{{ plex_state_dir }}/Library/...`), which is how the
    # watchdog unit's own ExecStart is built. A single pass leaves `{{` behind and
    # would make this reader refuse the very line it is here to compare against.
    for _ in range(8):
        replaced = VAR_RE.sub(_scalar, text)
        if replaced == text:
            break
        text = replaced
    if "\x00" in text or "{{" in text or "{%" in text:
        return None
    return text


def _render_exec_start(path: pathlib.Path):
    """The LAST `ExecStart=` value of a unit, rendered against the role defaults.

    The last and not the only one: a drop-in resets the packaged unit's
    `ExecStart` with an empty assignment and then respells it, so two is the
    correct count here and the reset row below is what pins that shape.
    """
    lines = _exec_start_lines(path)
    if not lines:
        return None
    return _render(lines[-1].split("=", 1)[1], _defaults())


def _argv(path: pathlib.Path):
    """The rendered ExecStart as argv, or None when it cannot be split safely."""
    rendered = _render_exec_start(path)
    if rendered is None:
        return None
    try:
        return shlex.split(rendered)
    except ValueError:
        return None


def _flag_value(argv, flag: str):
    """The value of a long flag in either spelling, or None when absent.

    node-exporter spells its flags `--flag=value`; systemd unit files in this
    repo also use `--flag value`. Both are read so the row scores the VALUE
    rather than the spelling.
    """
    for index, token in enumerate(argv or []):
        if token == flag:
            return argv[index + 1] if index + 1 < len(argv) else ""
        if token.startswith(flag + "="):
            return token.split("=", 1)[1]
    return None


def _disabled_collectors(argv):
    """Every collector the rendered argv switches off, in order."""
    prefix = "--no-collector."
    return [token[len(prefix) :] for token in argv or [] if token.startswith(prefix)]


def _watchdog_textfile_dir():
    """The directory the watchdog WRITES into, read out of its own unit.

    Rendered the same way, so this row compares two resolved paths rather than
    two spellings of a reference — a drop-in pointing at
    `{{ plex_state_dir }}/textfile` would carry a perfectly good variable and
    still be a different directory.
    """
    return _flag_value(_argv(WATCHDOG_UNIT), "--textfile-dir")


def _textfile_name():
    """`TEXTFILE_NAME` out of `files/plex_blip_watchdog.py`, or None.

    Read with `ast` and not imported: the module is a standalone script this repo
    cannot take as a test dependency, and importing it would run module-level
    code inside the gate. This row is the reason the fence says the module may be
    READ — restating the name here instead would be the second literal the whole
    file argues against.
    """
    if not WATCHDOG_SOURCE.is_file():
        return None
    tree = ast.parse(WATCHDOG_SOURCE.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Name)
                and target.id == TEXTFILE_NAME_CONST
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                return node.value.value
    return None


def test_the_role_installs_node_exporter_and_starts_it_ungated() -> bool:
    """The package goes on, the service comes up, and neither can be skipped.

    BY REFERENCE on both ends: the `apt` name and the `systemd` name are read as
    variables, so the package this role installs and the unit it starts cannot
    become two strings that merely happen to agree — which is `9f13`'s shape and
    this wave's declared subject.

    UNGATED is read as the `when:` KEY at the census's reach, so a gate inherited
    from an enclosing `block:` counts (`task-1786148389-ffe4` measured that
    nesting a task under `when: false` leaves a 14-row guard entirely green).

    ORDER: the textfile directory Step 4b ships must exist before the collector
    that reads it is started. Converging eventually is not the same as converging
    on the first play, and a node-exporter started against a missing directory
    logs a collector error on every scrape.
    """
    install, install_gates = _named(INSTALL_TASK)
    service, service_gates = _named(SERVICE_TASK)
    package = (_module_args(install, *APT_KEYS) or {}).get("name")
    package_ref = isinstance(package, str) and _normalise_refs(package) == _ref(
        PACKAGE_VAR
    )
    present = (_module_args(install, *APT_KEYS) or {}).get("state") == "present"
    unit = (_module_args(service, *SYSTEMD_KEYS) or {}).get("name")
    unit_ref = isinstance(unit, str) and _normalise_refs(unit) == _ref(SERVICE_VAR)
    args = _module_args(service, *SYSTEMD_KEYS) or {}
    running = args.get("state") == "started" and args.get("enabled") is True
    ungated = not install_gates and not service_gates
    dir_index = _task_index(COLLECTOR_DIR_TASK)
    service_index = _task_index(SERVICE_TASK)
    ordered = (
        dir_index is not None
        and service_index is not None
        and dir_index < service_index
    )
    defaults = _defaults()
    declared = all(
        isinstance(defaults.get(var), str) and defaults.get(var)
        for var in (PACKAGE_VAR, SERVICE_VAR)
    )
    ok = (
        package_ref
        and present
        and unit_ref
        and running
        and ungated
        and ordered
        and declared
    )
    print(
        f"{'OK' if ok else 'FAIL'}: the role installs {_ref(PACKAGE_VAR)} and "
        f"starts {_ref(SERVICE_VAR)}, ungated, after the textfile directory "
        f"exists (package={package!r} package_ref={package_ref} present={present} "
        f"unit={unit!r} unit_ref={unit_ref} running={running} ungated={ungated} "
        f"gates={list(install_gates) + list(service_gates)} ordered={ordered} "
        f"dir={dir_index} service={service_index} declared={declared})"
    )
    return ok


def test_the_override_is_a_drop_in_for_the_unit_the_role_starts() -> bool:
    """The drop-in lands under the unit the `systemd` task actually starts.

    A drop-in is only read if it sits in `<unit>.service.d/` beside the unit
    systemd resolves, so a `dest:` that names the service by a LITERAL while the
    `systemd` task names it by a variable is a file systemd will never open — the
    package's own defaults then run with no restraint, no textfile directory and
    no disabled collectors, and every other row in this file stays green because
    every other row reads the template rather than its destination. So both ends
    are required to carry the SAME reference.

    The parent directory is required too, and by the same reference: `template:`
    does not create it, and a missing `<unit>.service.d/` is a failed play rather
    than a silent one — but a directory task naming a second literal path is the
    same drift one step earlier.
    """
    override, override_gates = _named(OVERRIDE_TASK)
    directory, directory_gates = _named(OVERRIDE_DIR_TASK)
    args = _module_args(override, *TEMPLATE_KEYS) or {}
    dest = args.get("dest")
    expected_dir = f"{DROP_IN_ROOT}/{_ref(SERVICE_VAR)}{DROP_IN_SUFFIX}"
    expected_dest = f"{expected_dir}/{DROP_IN_FILE}"
    dest_ok = isinstance(dest, str) and _normalise_refs(dest) == expected_dest
    src_ok = args.get("src") == OVERRIDE_TEMPLATE.name
    dir_args = _module_args(directory, *FILE_KEYS) or {}
    dir_path = dir_args.get("path")
    dir_ok = isinstance(dir_path, str) and _normalise_refs(dir_path) == expected_dir
    is_directory = dir_args.get("state") == "directory"
    dir_index = _task_index(OVERRIDE_DIR_TASK)
    override_index = _task_index(OVERRIDE_TASK)
    ordered = (
        dir_index is not None
        and override_index is not None
        and dir_index < override_index
    )
    ungated = not override_gates and not directory_gates
    exists = OVERRIDE_TEMPLATE.is_file()
    ok = (
        dest_ok
        and src_ok
        and dir_ok
        and is_directory
        and ordered
        and ungated
        and exists
    )
    print(
        f"{'OK' if ok else 'FAIL'}: the drop-in is written to {expected_dest!r} "
        f"under a directory created by the same reference (dest={dest!r} "
        f"dest_ok={dest_ok} src_ok={src_ok} dir_path={dir_path!r} dir_ok={dir_ok} "
        f"directory={is_directory} ordered={ordered} ungated={ungated} "
        f"template_exists={exists})"
    )
    return ok


def test_the_drop_in_resets_exec_start_and_this_reader_can_render_it() -> bool:
    """Anti-vacuity, and the precondition for `shlex` standing in for systemd.

    THE RESET IS NOT COSMETIC. systemd APPENDS `ExecStart=` in a drop-in unless
    the list is first cleared with an empty assignment, and a `Type=simple` unit
    with two `ExecStart=` settings fails to load outright. The empty line is
    therefore load-bearing shape, and it is why `_render_exec_start` reads the
    LAST of the two rather than requiring exactly one.

    SCORED AGAINST THE RENDER, WHICH IS THE CORRECTION THIS FILE EXISTS AFTER.
    The sibling watchdog guard pins "no `%`, no backslash" on the TEMPLATE, and
    the Step 4b finalization measured with real systemd that this is the wrong
    boundary: a `%` arriving through a variable renders into the argv, systemd
    expands it (`%h` -> a home directory), and the template-side check stays
    green (`mem-1786165277-450b`). This drop-in also carries a Jinja `{% for %}`,
    so its template text contains `%` that is not an argv character at all —
    checking the source here would be doubly wrong. Every precondition below is
    read off the RESOLVED string.

    The four preconditions are the ways this line could diverge between POSIX
    splitting and systemd's own: a `%` specifier, a backslash, a trailing
    continuation, and a prefix character (`-@:+!`) that changes execution
    semantics and would make the first token something other than the program.
    """
    lines = _exec_start_lines(OVERRIDE_TEMPLATE)
    reset = len(lines) == 2 and lines[0] == "ExecStart="
    rendered = _render_exec_start(OVERRIDE_TEMPLATE)
    argv = _argv(OVERRIDE_TEMPLATE)
    renders = rendered is not None
    no_specifier = renders and "%" not in rendered
    no_escape = renders and "\\" not in rendered
    unprefixed = bool(rendered) and rendered[0] not in "-@:+!"
    binary = _defaults().get(BIN_VAR)
    runs_exporter = bool(argv) and argv[0] == binary
    ok = (
        reset
        and renders
        and argv is not None
        and no_specifier
        and no_escape
        and unprefixed
        and runs_exporter
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {OVERRIDE_TEMPLATE.name} clears ExecStart and "
        f"respells it as {binary!r}, and the RENDERED line is safe to split "
        f"(exec_start_lines={len(lines)} reset={reset} renders={renders} "
        f"no_specifier={no_specifier} no_escape={no_escape} "
        f"unprefixed={unprefixed} runs_exporter={runs_exporter} argv={argv})"
    )
    return ok


def test_the_drop_in_mirrors_the_watchdog_unit_s_restraint() -> bool:
    """`Nice` and `CPUSchedulingPolicy`, READ OUT OF the watchdog unit.

    Design §4.5 does not say "Nice=10"; it says the exporter is restrained
    "mirroring the watchdog unit". Typing `10` and `idle` here would score
    today's agreement and stay green the day the watchdog's restraint is retuned
    and the exporter's is not — the agreement-by-coincidence shape `9f13` records
    one artifact over. So the VALUES come from `plex_blip_watchdog.service.j2` and
    only the DIRECTIVE NAMES are named here.

    Both artifacts are required to declare each directive exactly once:
    `_directive` returns None for a repeated key, so a second `Nice=` in either
    file reds rather than being silently resolved to the first — systemd takes
    the last, and this reader must not disagree with it quietly.

    WHY RESTRAINT AT ALL, since a guard that cannot say why is a guard nobody may
    retune: R8 prices every addition by the load it puts on Plex. node-exporter
    walks `/proc` and `/sys` on every 15 s scrape inside the container whose
    stalls this project exists to remove, so it runs at the same idle scheduling
    class as the watchdog that watches for those stalls.
    """
    mirrored, defects = {}, []
    for key in RESTRAINT_KEYS:
        source = _directive(WATCHDOG_UNIT, key)
        target = _directive(OVERRIDE_TEMPLATE, key)
        mirrored[key] = (source, target)
        if source is None:
            defects.append(f"{key}: not declared exactly once in the watchdog unit")
        elif target is None:
            defects.append(f"{key}: not declared exactly once in the drop-in")
        elif source != target:
            defects.append(f"{key}: watchdog {source!r} != drop-in {target!r}")
    ok = not defects
    print(
        f"{'OK' if ok else 'FAIL'}: the drop-in mirrors {WATCHDOG_UNIT.name}'s "
        f"restraint (mirrored={mirrored} defects={defects})"
    )
    return ok


def test_the_collector_directory_is_the_one_the_watchdog_writes_into() -> bool:
    """One directory, reached from both ends, compared AFTER resolution.

    This is the join the whole step turns on: the watchdog writes its `.prom`
    into `--textfile-dir` and node-exporter serves whatever is in
    `--collector.textfile.directory`. Two directories that differ produce no
    error anywhere — the watchdog writes happily, the exporter serves an empty
    collector, and design §5.3's alert expressions match an absent series, which
    `mem-1786159649-6e78` measured as unfirable rather than firing.

    Compared as RESOLVED PATHS and not as spellings: both ends carrying a
    variable reference is necessary and not sufficient, because two different
    variables are two different directories. Both must ALSO be
    `{{ plex_watchdog_textfile_dir }}` and that variable must be an absolute path
    in the defaults — a reference to an undefined name renders empty under
    ansible's default templating, and `--collector.textfile.directory=` is a
    collector that reads nothing while the unit stays green.
    """
    exporter_dir = _flag_value(_argv(OVERRIDE_TEMPLATE), "--collector.textfile.directory")
    watchdog_dir = _watchdog_textfile_dir()
    declared = _defaults().get(TEXTFILE_DIR_VAR)
    absolute = isinstance(declared, str) and declared.startswith("/")
    agree = (
        exporter_dir is not None
        and watchdog_dir is not None
        and exporter_dir == watchdog_dir
    )
    follows = absolute and exporter_dir == declared
    raw = _exec_start_lines(OVERRIDE_TEMPLATE)
    exporter_ref = bool(raw) and (
        f"--collector.textfile.directory={_ref(TEXTFILE_DIR_VAR)}"
        in _normalise_refs(raw[-1])
    )
    ok = agree and follows and exporter_ref
    print(
        f"{'OK' if ok else 'FAIL'}: node-exporter serves the directory the "
        f"watchdog writes into, by {_ref(TEXTFILE_DIR_VAR)} (exporter="
        f"{exporter_dir!r} watchdog={watchdog_dir!r} agree={agree} "
        f"declared={declared!r} absolute={absolute} follows={follows} "
        f"by_reference={exporter_ref})"
    )
    return ok


def test_the_disabled_collectors_come_from_the_role_s_list() -> bool:
    """R17's disabled set is DATA, and it is neither empty nor self-defeating.

    Generated rather than typed, and BOTH halves of that are scored — the second
    one because a mutant found the sentence over-claiming. The rendered argv's
    `--no-collector.` tokens must equal the defaults list exactly, in order, so
    the flags cannot drift from the list that documents why each one is off; an
    emptied list therefore reds here rather than quietly shipping an exporter
    that logs a collector error on every scrape for hardware CT 110 cannot see.
    But that equality alone stays GREEN over the flags TYPED OUT by hand to match
    the list (measured, `logs/builder-4c-mutants.log` M10), which is the
    two-strings-that-agree shape this wave exists to delete — the two would drift
    the moment the list changed, and the file would be claiming a mechanism it
    does not have. So the template is also required to carry the LOOP: a `for`
    over this variable whose body is the flag prefix joined to the loop
    variable.

    THE SUBSET IS REQUIRED AND THE SUPERSET IS ALLOWED. `REQUIRED_DISABLED` is
    the host firmware / sensors / power / storage set an unprivileged LXC has no
    view of (R17, and design §9.4 assigns storage evidence to the PVE host).
    Disabling more than that is a judgement a later row may make; disabling less
    is the defect this row exists for.

    AND THE FORBIDDEN SET IS THE HALF NOBODY LOOKS FOR. `--no-collector.textfile`
    would switch off the entire delivery mechanism for design §5.2 while every
    other row in this file stayed green — the drop-in would still be a drop-in,
    still point at the right directory, still be restrained, and publish nothing.
    The other six are the class-C blind spot plan.md Step 4 names by hand.
    """
    listed = _defaults().get(DISABLED_VAR)
    is_list = isinstance(listed, list) and all(
        isinstance(item, str) for item in listed
    )
    rendered = _disabled_collectors(_argv(OVERRIDE_TEMPLATE))
    generated = is_list and rendered == listed
    raw = _exec_start_lines(OVERRIDE_TEMPLATE)
    looped = False
    for match in FOR_RE.finditer(raw[-1] if raw else ""):
        loop_var, list_var, body = match.group(1), match.group(2), match.group(3)
        if list_var == DISABLED_VAR and f"--no-collector.{_ref(loop_var)}" in (
            _normalise_refs(body)
        ):
            looped = True
    nonempty = bool(is_list and listed)
    names = set(listed or [])
    unique = is_list and len(names) == len(listed)
    well_formed = sorted(n for n in names if not COLLECTOR_NAME_RE.match(n))
    missing = sorted(REQUIRED_DISABLED - names)
    forbidden = sorted(FORBIDDEN_DISABLED & names)
    ok = (
        is_list
        and generated
        and looped
        and nonempty
        and unique
        and not well_formed
        and not missing
        and not forbidden
    )
    print(
        f"{'OK' if ok else 'FAIL'}: the ExecStart's --no-collector flags are "
        f"generated from {DISABLED_VAR} and cover R17's set without disabling "
        f"the ones this deployment exists for (is_list={is_list} "
        f"generated={generated} looped={looped} nonempty={nonempty} "
        f"unique={unique} malformed={well_formed} missing={missing} "
        f"forbidden={forbidden} rendered={rendered})"
    )
    return ok


def test_the_listen_address_is_a_variable_the_scrape_job_can_pin() -> bool:
    """The port is shipped BY THE ROLE, so Step 4d has a second end to pin.

    `code-assist:plex-blip-manual-triage:step-04:prometheus-scrape-job` is
    required to pin its target port "by relation to what the plex role ships". If
    the role passed no listen address at all, that row would have nothing to
    relate to and would type node-exporter's upstream default as a literal — a
    scrape job and an exporter agreeing by coincidence, one wave after this one
    was cut to delete exactly that.

    So the flag is passed, its value is the variable, and the variable is a
    `host:port` this row can hand a scrape job. The address half is checked only
    for being present and specifier-free; the PORT is checked as an integer in
    range, because that is the token 4d will reuse.
    """
    argv = _argv(OVERRIDE_TEMPLATE)
    value = _flag_value(argv, "--web.listen-address")
    declared = _defaults().get(LISTEN_VAR)
    raw = _exec_start_lines(OVERRIDE_TEMPLATE)
    by_reference = bool(raw) and f"--web.listen-address={_ref(LISTEN_VAR)}" in (
        _normalise_refs(raw[-1])
    )
    host, _, port = (declared or "").rpartition(":")
    numeric = port.isdigit() and 0 < int(port) < 65536
    resolved = value is not None and value == declared
    ok = by_reference and resolved and bool(host) and numeric
    print(
        f"{'OK' if ok else 'FAIL'}: --web.listen-address follows "
        f"{_ref(LISTEN_VAR)}={declared!r}, a host:port Step 4d can pin against "
        f"(value={value!r} by_reference={by_reference} resolved={resolved} "
        f"host={host!r} port={port!r} numeric={numeric})"
    )
    return ok


def test_the_watchdog_s_collector_file_is_named_what_node_exporter_reads() -> bool:
    """`task-1786159051-cb29` — the `.prom` NAME CONTRACT, first expressible here.

    node-exporter's textfile collector globs `*.prom` in its directory and opens
    nothing else. `TEXTFILE_NAME` in `files/plex_blip_watchdog.py` is the only
    place this repo decides that name, and mutating it to `plex_blip.metrics`
    left the whole suite GREEN — a watchdog writing a file the collector never
    reads, which is silent by construction: `mem-1786159649-6e78` measured that
    an ABSENT series cannot match the `==`/`!=` expressions design §5.3 writes
    over these metrics, so the alert written to catch a dead diagnostic is
    exactly the alert a missing file is invisible to.

    WHY A LITERAL IS THE HONEST INSTRUMENT HERE, stated because this file rejects
    literals everywhere else. The glob lives in node-exporter's source; this repo
    holds no second end, and inventing one — typing the suffix into the role, or
    into the drop-in — would manufacture the two-strings-that-agree defect the
    wave exists to delete. So the ROLE never mentions the name at all (it passes
    a DIRECTORY; the module owns the file), the suffix is pinned once HERE with
    its provenance, and the value is READ OUT OF the module rather than restated.

    The name is also required to be a bare filename: a `TEXTFILE_NAME` carrying a
    separator would write outside the directory the drop-in serves while still
    ending in the right suffix.

    THE SILENCE IS SCORED OVER EFFECTIVE TEXT, NOT OVER PROSE, and the difference
    is measured rather than assumed. The Step 4b task that creates the collector
    directory already names the file in a COMMENT ("the watchdog writes
    plex_blip.prom here as root") — which is why this row strips comments before
    asking. A comment cannot drift the program: nothing renders it, nothing parses
    it, and it fails loudly in review rather than silently in production. A YAML
    VALUE or a rendered unit directive carrying the suffix is the second end that
    would matter, and that is what this row forbids. The prose hits are printed
    rather than hidden, so the next hat can see what the assertion is stepping
    over instead of taking this paragraph on trust.
    """
    name = _textfile_name()
    read = isinstance(name, str) and bool(name)
    suffixed = read and name.endswith(TEXTFILE_SUFFIX)
    bare = read and "/" not in name and name != TEXTFILE_SUFFIX
    prose, effective = [], []
    for source in (PLEX_TASKS, OVERRIDE_TEMPLATE):
        for number, line in enumerate(_read(source).splitlines(), 1):
            if TEXTFILE_SUFFIX not in line:
                continue
            where = f"{source.name}:{number}"
            (prose if line.lstrip().startswith("#") else effective).append(where)
    role_silent = not effective
    ok = read and suffixed and bare and role_silent
    print(
        f"{'OK' if ok else 'FAIL'}: {TEXTFILE_NAME_CONST}={name!r} ends in "
        f"{TEXTFILE_SUFFIX!r}, the only suffix node-exporter's textfile collector "
        f"reads, and the role respells it in no effective line (read={read} "
        f"suffixed={suffixed} bare={bare} role_silent={role_silent} "
        f"effective={effective} in_comments={prose})"
    )
    return ok


def test_every_test_function_is_registered_in_tests() -> bool:
    """A `test_*` missing from `TESTS` is green by omission.

    Asserted rather than eyeballed: the module's own namespace is the census, and
    this row is in `TESTS` too, so it cannot exempt itself.
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
    test_the_role_installs_node_exporter_and_starts_it_ungated,
    test_the_override_is_a_drop_in_for_the_unit_the_role_starts,
    test_the_drop_in_resets_exec_start_and_this_reader_can_render_it,
    test_the_drop_in_mirrors_the_watchdog_unit_s_restraint,
    test_the_collector_directory_is_the_one_the_watchdog_writes_into,
    test_the_disabled_collectors_come_from_the_role_s_list,
    test_the_listen_address_is_a_variable_the_scrape_job_can_pin,
    test_the_watchdog_s_collector_file_is_named_what_node_exporter_reads,
    test_every_test_function_is_registered_in_tests,
)


def main() -> int:
    results = [fn() for fn in TESTS]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
