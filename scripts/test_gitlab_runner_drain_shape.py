"""Shape tests for the gitlab-runner drain drop-in (gitlab-runner Step 5a).

The drop-in value must come from gitlab_runner_drain_timeout_sec, so it is a
template; arms render it through Ansible (the gate Python has no jinja2).
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "gitlab_runner"
TEMPLATE = ROLE / "templates" / "gitlab-runner-drain.conf.j2"
DEFAULTS = ROLE / "defaults" / "main.yml"


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def _read(rel: str) -> str:
    p = ROLE / rel
    return p.read_text() if p.is_file() else ""


def _render(extra: str = "", template: pathlib.Path = TEMPLATE) -> str | None:
    ans = ["mise", "exec", "--", "ansible"] if shutil.which("mise") else ["ansible"]
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "drain.conf"
        cmd = ans + ["localhost", "-c", "local", "-m", "ansible.builtin.template",
                     "-a", f"src={template} dest={out}", "-e", f"@{DEFAULTS}"]
        if extra:
            cmd += ["-e", extra]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, check=False)
        return out.read_text() if proc.returncode == 0 and out.is_file() else None


def _timeout(text: str | None) -> int:
    m = re.search(r"^TimeoutStopSec=(\d+)$", text or "", re.M)
    return int(m.group(1)) if m else -1


def test_default_var_above_max_job() -> bool:
    m = re.search(r"^gitlab_runner_drain_timeout_sec:\s*(\d+)", _read("defaults/main.yml"), re.M)
    return _report(bool(m) and int(m.group(1)) > 5400, f"gitlab_runner_drain_timeout_sec default > 5400 ({m.group(1) if m else 'absent'})")


def test_dropin_values() -> bool:
    t = _render()
    ok = t is not None and re.search(r"^\[Service\]$", t, re.M) is not None \
        and re.search(r"^KillSignal=SIGQUIT$", t, re.M) is not None \
        and re.search(r"^KillMode=mixed$", t, re.M) is not None and _timeout(t) > 5400
    return _report(ok, "drop-in renders [Service] KillSignal=SIGQUIT, KillMode=mixed, TimeoutStopSec > 5400")


def test_timeout_read_from_var() -> bool:
    return _report(_timeout(_render("gitlab_runner_drain_timeout_sec=12345")) == 12345,
                   "TimeoutStopSec follows gitlab_runner_drain_timeout_sec")


def test_drain_tasks() -> bool:
    t = _read("tasks/drain.yml")
    h = _read("handlers/main.yml")
    main = _read("tasks/main.yml")
    checks = {
        "dest drain.conf drop-in dir": "/etc/systemd/system/gitlab-runner.service.d" in t and "drain.conf" in t,
        "template src": "src: gitlab-runner-drain.conf.j2" in t,
        "root 0644": 'mode: "0644"' in t and "owner: root" in t,
        "dir created": "state: directory" in t,
        "notifies daemon-reload": "notify: Reload systemd for gitlab-runner" in t,
        "daemon-reload handler": bool(re.search(r"- name: Reload systemd for gitlab-runner\n\s+ansible\.builtin\.systemd:\n\s+daemon_reload: true", h)),
        "imported after install": 0 <= main.find("install.yml") < main.find("drain.yml") < main.find("config.yml"),
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"drain.yml shape (failed: {bad})")


def test_mutant_hardcoded_timeout_caught() -> bool:
    if not TEMPLATE.is_file():
        return _report(False, "mutant: template missing")
    d = pathlib.Path(tempfile.mkdtemp()) / TEMPLATE.name
    d.write_text(re.sub(r"TimeoutStopSec=.*", "TimeoutStopSec=6000", TEMPLATE.read_text()))
    return _report(_timeout(_render("gitlab_runner_drain_timeout_sec=12345", d)) != 12345,
                   "mutant: hardcoded TimeoutStopSec turns the var arm red")


def main() -> int:
    results = [fn() for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    passed, total = sum(results), len(results)
    print(f"PASS: {passed}/{total}" if passed == total else f"FAIL: {total - passed}/{total} checks failed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
