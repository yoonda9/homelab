"""Shape tests for the Plex watchdog's apt dependencies (Step 1c).

Per .agents/planning/2026-08-07-plex-blip-manual-triage/implementation/plan.md
Step 1 and context.md §1 — `fuser(1)` ships in **psmisc**, and the
`_run_cmd(["fuser", "-v"] + targets)` probe at
ansible/roles/plex/files/plex_blip_watchdog.py:405 has never once been able to
run because no play installs it. This file pins the fix and, more importantly,
pins WHERE the fix lands.

WHY A CONTAINMENT TEST AND NOT A GREP. `ansible/roles/plex/tasks/main.yml`
holds FOUR apt name lists, and psmisc installs the binary from any of them —
so a bare `"psmisc" in main.yml` grep is green for every placement and
discriminates nothing:

    :36  "Install the Intel iHD media driver and VA-API tooling"
         -> name: "{{ plex_media_packages }}"  (the QSV driver set; the list
            literal is in defaults/main.yml:13-16, NOT here)
    :237 "Install Plex watchdog and diagnostic dependencies"
         -> inline list: sysstat, lsof, procps, sqlite3   <-- psmisc's home
    plus "Install the deb822 source manager dependency" (python3-debian) and
    "Install Plex Media Server" (plexmediaserver).

The role is therefore parsed as YAML and psmisc is located by its CONTAINING
TASK. That also immunises the check against a false positive a regex would
take: `sqlite3` appears again at :339 inside a `command: argv:` list, so
"package name appears in the file" is not even a reliable proxy for "package
is installed".

The negative row reads `plex_media_packages` from **defaults/main.yml**. This
is the row's whole point and the reason it is not written against
tasks/main.yml: that file carries only the template string
`{{ plex_media_packages }}` and literally cannot answer "is psmisc in that
list?" — a negative written there is vacuously green at BOTH placements, i.e.
it recreates the exact failure this file exists to prevent.

PyYAML (6.0.3) is importable under the gate interpreter — run_gate.py:56 runs
each shape test as `[sys.executable, path]` and `just test` invokes the repo
`.venv` python, which carries it. There is deliberately NO try/except skip
around the import: the repo idiom `OK (skip): not installed` would turn a
missing parser into a green badge over an unrun check, which is the vacuous
pass this file is built to refuse. A missing PyYAML must be a loud ImportError.

Dual-mode (module-level test_*()->bool + main()->int), mirroring
scripts/test_ansible_layout_shape.py. The real gate is the standalone exit code.
"""

import pathlib
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PLEX_ROLE = REPO_ROOT / "ansible" / "roles" / "plex"
PLEX_TASKS = PLEX_ROLE / "tasks" / "main.yml"
PLEX_DEFAULTS = PLEX_ROLE / "defaults" / "main.yml"

WATCHDOG_DEPS_TASK = "Install Plex watchdog and diagnostic dependencies"
MEDIA_PACKAGES_VAR = "plex_media_packages"
PACKAGE = "psmisc"

# The four packages the watchdog-deps task already installed before this row.
# Asserted alongside psmisc because the change is ADDITIVE: `lsof` and `procps`
# back the lsof and `ps aux -T` probes in the same snapshot, and plan.md:45-47
# calls losing an lsof measurement "the regression that matters most" — so a
# list REPLACED by [psmisc] would satisfy "psmisc is installed" while removing
# the two binaries the rest of Step 1 is about.
WATCHDOG_DEPS_INCUMBENTS = ["sysstat", "lsof", "procps", "sqlite3"]

# Both spellings of the apt module, so a `apt:` <-> `ansible.builtin.apt:`
# rename cannot silently empty the census below and make the one-home row pass
# by finding nothing anywhere.
APT_KEYS = ("ansible.builtin.apt", "apt")

# All THREE spellings of the apt module's package parameter. ansible-core 2.21.1
# modules/apt.py:1274 is
#     package=dict(type='list', elements='str', aliases=['pkg', 'name'])
# — the CANONICAL parameter is `package`, and `name` is merely one of three legal
# synonyms. Reading `name:` alone censuses a third of the surface: a second
# psmisc home spelled `pkg:` or `package:` installs the binary just as well and
# is invisible. That is the identical hazard APT_KEYS above exists to close, one
# level down, and it was measurably open (logs/builder-f02c-r2-red.txt: B2 and B3
# both left all four rows green).
APT_NAME_KEYS = ("name", "pkg", "package")

# block/rescue/always each carry a task list of their own, so a walk over the
# top-level list alone cannot see an apt task nested inside one. Armed by repo
# usage rather than hypothesis: ansible/roles/docker_host/tasks/main.yml:357
# already uses a block, and B1 in the same log missed for the same reason.
BLOCK_KEYS = ("block", "rescue", "always")

# The apt states that actually put a package on the host. The choice list is
# CLOSED — modules/apt.py:1268 is
#     state=dict(type='str', default='present',
#                choices=['absent', 'build-dep', 'fixed', 'latest', 'present'])
# — so enumerating the two installing states is a complete test rather than a
# spot check. `build-dep` installs a package's BUILD dependencies and not the
# package; `fixed` repairs broken dependencies; `absent` removes it.
APT_INSTALLING_STATES = ("present", "latest")
APT_DEFAULT_STATE = "present"


def _load(path: pathlib.Path):
    return yaml.safe_load(path.read_text()) if path.is_file() else None


def _iter_tasks(tasks):
    """Every task in a task list, with block/rescue/always flattened into it.

    Recursive because blocks nest. See BLOCK_KEYS for why a top-level-only walk
    is not enough.
    """
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        yield task
        for section in BLOCK_KEYS:
            yield from _iter_tasks(task.get(section))


def _apt_tasks():
    """Every apt task in tasks/main.yml as (task name, packages, apt state).

    The package parameter may be a single string or a list under any of its
    three spellings; all are normalised to a list so a one-package task is
    censused the same way as a multi-package one. `state` is reported with the
    module's own default applied, so callers never have to distinguish "no
    state key" from "state: present".
    """
    census = []
    for task in _iter_tasks(_load(PLEX_TASKS)):
        for key in APT_KEYS:
            args = task.get(key)
            if not isinstance(args, dict):
                continue
            names = args.get("name") or args.get("pkg") or args.get("package")
            if isinstance(names, str):
                names = [names]
            census.append(
                (
                    task.get("name"),
                    list(names or []),
                    args.get("state", APT_DEFAULT_STATE),
                )
            )
    return census


def _watchdog_deps():
    """(packages, state) for the watchdog-deps task, or None if it is not there."""
    for task_name, packages, state in _apt_tasks():
        if task_name == WATCHDOG_DEPS_TASK:
            return packages, state
    return None


def test_watchdog_deps_task_carries_an_inline_package_list() -> bool:
    """Anti-vacuity: the task this file addresses by NAME must actually exist.

    Every other row here locates its subject through that string. If the task
    is renamed, the lookup returns nothing and a naive membership check reads
    "psmisc is not in the wrong place" — passing precisely because it found
    nothing to check. This row is what makes the other three mean something.
    """
    entry = _watchdog_deps()
    found = entry is not None
    packages = entry[0] if entry else None
    inline = bool(packages) and not any("{{" in pkg for pkg in packages)
    ok = found and inline
    print(
        f"{'OK' if ok else 'FAIL'}: task {WATCHDOG_DEPS_TASK!r} exists with an "
        f"inline apt name list (found={found} packages={packages})"
    )
    return ok


def test_psmisc_is_installed_by_the_watchdog_deps_task() -> bool:
    """POSITIVE: psmisc lands in the watchdog-deps list, beside the incumbents.

    The row is named "is INSTALLED by", so it also reads `state:` — under
    `state: absent` the task removes psmisc and this row's own name is false
    while membership alone stays green (logs/builder-f02c-r2-red.txt, A1). The
    state check is complete rather than a spot check because apt's choice list
    is closed; see APT_INSTALLING_STATES.

    `when:` is deliberately NOT read, and this row makes no claim about the task
    RUNNING. A `when:` value is an arbitrary Jinja expression that cannot be
    decided statically, so a guard here could only catch the literal `false` —
    a sentence stronger than the guard, which is the defect this file was
    rejected for once already. No task in this role carries one today.
    """
    entry = _watchdog_deps()
    packages, state = entry if entry else ([], None)
    has_psmisc = PACKAGE in packages
    kept = [pkg for pkg in WATCHDOG_DEPS_INCUMBENTS if pkg in packages]
    additive = kept == WATCHDOG_DEPS_INCUMBENTS
    installing = state in APT_INSTALLING_STATES
    ok = has_psmisc and additive and installing
    print(
        f"{'OK' if ok else 'FAIL'}: {PACKAGE} installed by {WATCHDOG_DEPS_TASK!r} "
        f"(psmisc={has_psmisc} incumbents_kept={kept} of "
        f"{WATCHDOG_DEPS_INCUMBENTS} state={state!r} installing={installing}) "
        f"-> packages={packages}"
    )
    return ok


def test_psmisc_is_not_in_plex_media_packages() -> bool:
    """NEGATIVE: psmisc is not smuggled into the QSV driver set.

    Read from defaults/main.yml, where the list LITERAL lives. tasks/main.yml
    holds only `{{ plex_media_packages }}`, so it cannot answer this.

    The anti-vacuity half is the wiring check: an empty or deleted
    `plex_media_packages` would make `psmisc not in [...]` trivially true, so
    the list must be real AND the tasks file must still consume it through the
    template — otherwise this row is asserting a fact about a variable nobody
    installs.
    """
    defaults = _load(PLEX_DEFAULTS) or {}
    media_packages = defaults.get(MEDIA_PACKAGES_VAR)
    real_list = isinstance(media_packages, list) and bool(media_packages)
    wired = any(
        f"{{{{ {MEDIA_PACKAGES_VAR} }}}}" in pkg
        for _, packages, _ in _apt_tasks()
        for pkg in packages
    )
    absent = real_list and PACKAGE not in media_packages
    ok = real_list and wired and absent
    print(
        f"{'OK' if ok else 'FAIL'}: {PACKAGE} absent from {MEDIA_PACKAGES_VAR} "
        f"in defaults/main.yml (real_list={real_list} consumed_by_an_apt_task="
        f"{wired} absent={absent}) -> {media_packages}"
    )
    return ok


def test_psmisc_has_exactly_one_apt_home_in_the_role() -> bool:
    """The terminating form of the negative: ONE home, and it is the right one.

    The row's stated negative names `plex_media_packages`, but that is one of
    three wrong homes — psmisc bolted onto the python3-debian or
    plexmediaserver task installs the binary just as well and reads just as
    green. Censusing every apt task closes all of them at once.

    WHAT THE CENSUS ACTUALLY REACHES, stated exactly, because the previous
    spelling of this sentence ("including any apt task added after this file was
    written") claimed a closure the walk did not have and was rejected for it.
    It reads `ansible/roles/plex/tasks/main.yml` — the role's ONLY task file, and
    the role contains no include_tasks/import_tasks/include_role — walking every
    task with block/rescue/always flattened, under both spellings of the module
    (APT_KEYS) and all three of its package parameter (APT_NAME_KEYS).

    It does NOT reach the free-form `action:`/`local_action:` invocation, nor
    package names produced by a `loop:`. Neither is closed here because neither
    is armed: there is no `action:`/`local_action:` in any first-party YAML in
    this repo, and no `loop:` anywhere in this role. They are named so the
    sentence stays weaker than the guard rather than stronger.

    `state:` is deliberately NOT filtered here. A second task naming psmisc with
    `state: absent` is a real conflict with this row's subject, not a false
    alarm, so it should red — unlike the positive row, which reads state because
    its own name is a claim about installation.
    """
    homes = [
        task_name for task_name, packages, _ in _apt_tasks() if PACKAGE in packages
    ]
    ok = homes == [WATCHDOG_DEPS_TASK]
    print(
        f"{'OK' if ok else 'FAIL'}: {PACKAGE} appears in exactly one apt task, "
        f"the watchdog deps task (homes={homes})"
    )
    return ok


def main() -> int:
    results = [
        test_watchdog_deps_task_carries_an_inline_package_list(),
        test_psmisc_is_installed_by_the_watchdog_deps_task(),
        test_psmisc_is_not_in_plex_media_packages(),
        test_psmisc_has_exactly_one_apt_home_in_the_role(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
