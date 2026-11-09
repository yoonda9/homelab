"""Shape tests for the drain-gated upgrade (gitlab-runner Step 5b). Stdlib only."""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "gitlab_runner"
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "gitlab-runner.md"


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def _read(rel: str) -> str:
    p = ROLE / rel
    return p.read_text() if p.is_file() else ""


def _drop_comments(t: str) -> str:
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("#"))


def _task(t: str, name: str) -> str:
    m = re.search(rf"^( *)- name: {re.escape(name)}\n(.*?)(?=^\1- name: |\Z)", t, re.M | re.S)
    return m.group(0) if m else ""


def test_probe() -> bool:
    t = _drop_comments(_read("tasks/upgrade.yml"))
    p = _task(t, "Probe for pending gitlab-runner upgrades")
    ok = "apt-get -s install --only-upgrade" in p and "gitlab-runner-helper-images" in p \
        and "changed_when: false" in p and "register: gitlab_runner_pending" in p
    return _report(ok, "probe is apt-get -s, changed_when false, registered")


def test_block_gate() -> bool:
    t = _drop_comments(_read("tasks/upgrade.yml"))
    ok = re.search(r"when: gitlab_runner_pending\.stdout is search\('\^Inst ', multiline=True\)\s*\n\s*block:", t) is not None \
        and "is changed" not in t
    return _report(ok, "block gated on ^Inst search, not on 'is changed'")


def test_no_check_mode_apt() -> bool:
    t = _drop_comments(_read("tasks/upgrade.yml"))
    return _report("check_mode" not in t, "no check-mode apt task")


def test_block_order_and_env() -> bool:
    t = _drop_comments(_read("tasks/upgrade.yml"))
    i, j, k = (t.find(x) for x in ("name: Drain gitlab-runner", "name: Upgrade gitlab-runner and", "name: Start gitlab-runner"))
    up = _task(t, "Upgrade gitlab-runner and its helper images")
    ok = 0 < i < j < k and "state: latest" in up and 'NO_DOCKER_PRUNE: "1"' in up \
        and "state: stopped" in _task(t, "Drain gitlab-runner") and "state: started" in _task(t, "Start gitlab-runner")
    return _report(ok, "drain -> upgrade (NO_DOCKER_PRUNE=1) -> start")


def test_async_covers_drain() -> bool:
    t = _drop_comments(_read("tasks/upgrade.yml"))
    d = _task(t, "Drain gitlab-runner")
    m = re.search(r'async: "\{\{ gitlab_runner_drain_timeout_sec \+ (\d+) \}\}"', d)
    return _report(bool(m) and int(m.group(1)) >= 0 and "poll:" in d, "async >= drain timeout (var + margin) with poll")


def test_import_order() -> bool:
    m = _read("tasks/main.yml")
    return _report(0 <= m.find("install.yml") < m.find("upgrade.yml") < m.find("config.yml"),
                   "upgrade.yml imported between install.yml and config.yml")


def test_runbook() -> bool:
    b = RUNBOOK.read_text() if RUNBOOK.is_file() else ""
    s = re.search(r"^## Upgrade\s*$(.*?)(?=^## |\Z)", b, re.M | re.S)
    s = s.group(1) if s else ""
    ok = "drain timeout" in s and "after_script" in s and "NO_DOCKER_PRUNE" in s and "Not yet written" not in s
    return _report(ok, "runbook Upgrade section states the drain-timeout invariant")


def test_mutant_is_changed_gate_caught() -> bool:
    t = _read("tasks/upgrade.yml")
    mut = re.sub(r"is search\('\^Inst ', multiline=True\)", "is changed", t)
    ok = mut != t and "is changed" in mut and re.search(r"search\('\^Inst '", _drop_comments(mut)) is None
    return _report(ok, "mutant: gate on 'is changed' fails the ^Inst arm")


def main() -> int:
    results = [fn() for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    passed, total = sum(results), len(results)
    print(f"PASS: {passed}/{total}" if passed == total else f"FAIL: {total - passed}/{total} checks failed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
