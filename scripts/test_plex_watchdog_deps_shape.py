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


def _load(path: pathlib.Path):
    return yaml.safe_load(path.read_text()) if path.is_file() else None


def _apt_tasks():
    """Every apt task in the role as (task name, package names it installs).

    `name:` may be a single string or a list; both are normalised to a list so
    a one-package task is censused the same way as a multi-package one.
    """
    census = []
    for task in _load(PLEX_TASKS) or []:
        if not isinstance(task, dict):
            continue
        for key in APT_KEYS:
            args = task.get(key)
            if not isinstance(args, dict):
                continue
            names = args.get("name")
            if isinstance(names, str):
                names = [names]
            census.append((task.get("name"), list(names or [])))
    return census


def _watchdog_deps_packages():
    for task_name, packages in _apt_tasks():
        if task_name == WATCHDOG_DEPS_TASK:
            return packages
    return None


def test_watchdog_deps_task_carries_an_inline_package_list() -> bool:
    """Anti-vacuity: the task this file addresses by NAME must actually exist.

    Every other row here locates its subject through that string. If the task
    is renamed, the lookup returns nothing and a naive membership check reads
    "psmisc is not in the wrong place" — passing precisely because it found
    nothing to check. This row is what makes the other three mean something.
    """
    packages = _watchdog_deps_packages()
    found = packages is not None
    inline = bool(packages) and not any("{{" in pkg for pkg in packages)
    ok = found and inline
    print(
        f"{'OK' if ok else 'FAIL'}: task {WATCHDOG_DEPS_TASK!r} exists with an "
        f"inline apt name list (found={found} packages={packages})"
    )
    return ok


def test_psmisc_is_installed_by_the_watchdog_deps_task() -> bool:
    """POSITIVE: psmisc lands in the watchdog-deps list, beside the incumbents."""
    packages = _watchdog_deps_packages() or []
    has_psmisc = PACKAGE in packages
    kept = [pkg for pkg in WATCHDOG_DEPS_INCUMBENTS if pkg in packages]
    additive = kept == WATCHDOG_DEPS_INCUMBENTS
    ok = has_psmisc and additive
    print(
        f"{'OK' if ok else 'FAIL'}: {PACKAGE} installed by {WATCHDOG_DEPS_TASK!r} "
        f"(psmisc={has_psmisc} incumbents_kept={kept} of "
        f"{WATCHDOG_DEPS_INCUMBENTS}) -> packages={packages}"
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
        for _, packages in _apt_tasks()
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
    green. Censusing every apt task closes all of them at once, including any
    apt task added after this file was written.
    """
    homes = [task_name for task_name, packages in _apt_tasks() if PACKAGE in packages]
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
