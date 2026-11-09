"""Shape tests for the gitlab-runner prune timer and Docuum (gitlab-runner Step 8).

Templates are rendered through Ansible (the gate Python has no jinja2). Mutants
edit the rendered script or the tasks text and re-run the same checkers.
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "gitlab_runner"
T = ROLE / "templates"
DEFAULTS = ROLE / "defaults" / "main.yml"


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def _read(rel: str) -> str:
    p = ROLE / rel
    return p.read_text() if p.is_file() else ""


def _render(name: str, extra: str = "") -> str | None:
    ans = ["mise", "exec", "--", "ansible"] if shutil.which("mise") else ["ansible"]
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "out"
        cmd = ans + ["localhost", "-c", "local", "-m", "ansible.builtin.template",
                     "-a", f"src={T / name} dest={out}", "-e", f"@{DEFAULTS}"]
        if extra:
            cmd += ["-e", extra]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, check=False)
        return out.read_text() if proc.returncode == 0 and out.is_file() else None


def check_label_volume(s: str) -> bool:
    return bool(re.search(r"^docker volume prune -af --filter label=com\.gitlab\.gitlab-runner\.managed=true$", s, re.M))


def check_no_image_all(s: str) -> bool:
    code = "\n".join(ln for ln in s.splitlines() if not ln.lstrip().startswith("#"))
    return not re.search(r"image prune\b[^\n]*(\s-\w*a|\s--all)", code)


def check_until_from_var(s: str, keep: str = "168h") -> bool:
    untils = re.findall(r"--filter until=(\S+)", s)
    return bool(untils) and all(u == "$KEEP" for u in untils) and f'KEEP="{keep}"' in s


def check_timer(s: str) -> bool:
    return (bool(re.search(r"^OnCalendar=\*-\*-\* 04:00:00$", s, re.M))
            and bool(re.search(r"^Persistent=true$", s, re.M)))


def check_get_url(t: str) -> bool:
    m = re.search(r"ansible\.builtin\.get_url:(.*?)(?=\n- name:|\Z)", t, re.S)
    b = m.group(1) if m else ""
    return ("checksum: \"sha256:{{ gitlab_runner_docuum_sha256 }}\"" in b
            and "{{ gitlab_runner_docuum_version }}" in b
            and "x86_64-unknown-linux-musl" in b)


def check_unit(s: str) -> bool:
    return (bool(re.search(r"^ExecStart=/usr/local/bin/docuum --threshold 60% --min-age 1d$", s, re.M))
            and bool(re.search(r"^After=.*\bdocker\.service\b", s, re.M)))


def test_script_arms() -> bool:
    s = _render("ci-docker-prune.sh.j2")
    if s is None:
        return _report(False, "ci-docker-prune.sh.j2 renders")
    checks = {"label-filtered volume prune -a": check_label_volume(s),
              "no image prune -a": check_no_image_all(s),
              "until= from var": check_until_from_var(s)}
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"prune script arms (failed: {bad})")


def test_vars_flow() -> bool:
    s = _render("ci-docker-prune.sh.j2", "gitlab_runner_prune_keep=72h")
    u = _render("docuum.service.j2", "gitlab_runner_docuum_threshold=75% gitlab_runner_docuum_min_age=3d")
    return _report(bool(s) and check_until_from_var(s, "72h") and bool(u)
                   and "--threshold 75% --min-age 3d" in u,
                   "keep, threshold and min-age come from variables")


def test_timer_and_units() -> bool:
    tm = _render("ci-docker-prune.timer.j2") or ""
    sv = _render("ci-docker-prune.service.j2") or ""
    un = _render("docuum.service.j2") or ""
    checks = {
        "timer daily + Persistent": check_timer(tm) and "RandomizedDelaySec=30m" in tm,
        "service oneshot runs the script": "Type=oneshot" in sv and "ExecStart=/usr/local/sbin/ci-docker-prune" in sv,
        "docuum unit": check_unit(un),
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"units (failed: {bad})")


def test_tasks() -> bool:
    t, main, defs = _read("tasks/prune.yml"), _read("tasks/main.yml"), DEFAULTS.read_text()
    checks = {
        "get_url pinned with checksum": check_get_url(t),
        "binary dest": "dest: /usr/local/bin/docuum" in t,
        "timer enabled": "ci-docker-prune.timer" in t and "enabled: true" in t,
        "docuum enabled and started": "name: docuum" in t and "state: started" in t,
        "version pinned exactly": bool(re.search(r'^gitlab_runner_docuum_version: "\d+\.\d+\.\d+"', defs, re.M)),
        "sha256 is 64 hex": bool(re.search(r'^gitlab_runner_docuum_sha256: "[0-9a-f]{64}"', defs, re.M)),
        "imported after docker": 0 <= main.find("docker.yml") < main.find("prune.yml"),
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"prune.yml shape (failed: {bad})")


def test_mutants() -> bool:
    s = _render("ci-docker-prune.sh.j2") or ""
    t = _read("tasks/prune.yml")
    mutants = {
        "add image prune -a --filter until=": (check_no_image_all, s + "docker image prune -a --filter until=$KEEP\n"),
        "add image prune -af": (check_no_image_all, s + "docker image prune -af\n"),
        "drop label filter": (check_label_volume, s.replace(" --filter label=com.gitlab.gitlab-runner.managed=true", "")),
        "hardcode until": (check_until_from_var, s.replace("until=$KEEP", "until=24h")),
        "delete checksum": (check_get_url, re.sub(r"\n\s*checksum:[^\n]*", "", t)),
        "unpin version": (check_get_url, t.replace("{{ gitlab_runner_docuum_version }}", "latest")),
    }
    survived = [k for k, (fn, m) in mutants.items() if fn(m)]
    unchanged = [k for k, (_, m) in mutants.items() if m in (s, t)]
    return _report(not survived and not unchanged, f"mutants killed (survived: {survived}, no-op: {unchanged})")


def main() -> int:
    results = [fn() for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    passed, total = sum(results), len(results)
    print(f"PASS: {passed}/{total}" if passed == total else f"FAIL: {total - passed}/{total} checks failed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
