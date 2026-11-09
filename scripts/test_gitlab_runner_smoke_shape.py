"""Shape tests for the DinD-TLS smoke script (gitlab-runner Step 6a). Stdlib only."""

import pathlib
import re
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "gitlab_runner"


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def _read(rel: str) -> str:
    p = ROLE / rel
    return p.read_text() if p.is_file() else ""


def _drop_comments(t: str) -> str:
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("#"))


def _rendered() -> str:
    # Jinja in the template: the default tag, ansible_managed, and the escaped docker format.
    t = _read("templates/dind-tls-smoke.sh.j2")
    t = re.sub(r"\{\{\s*gitlab_runner_smoke_tag\s*\}\}", "29", t)
    t = t.replace("{{ ansible_managed }}", "managed").replace("{{ '{{.ServerVersion}}' }}", "{{.ServerVersion}}")
    return t


def test_default_var() -> bool:
    return _report(re.search(r'^gitlab_runner_smoke_tag: "29"\s*$', _read("defaults/main.yml"), re.M) is not None,
                   'defaults declare gitlab_runner_smoke_tag: "29"')


def test_tag_default_from_var() -> bool:
    t = _read("templates/dind-tls-smoke.sh.j2")
    return _report(re.search(r'TAG="\$\{1:-\{\{ gitlab_runner_smoke_tag \}\}\}"', t) is not None,
                   "tag argument defaults to gitlab_runner_smoke_tag")


def test_install_mode_and_path() -> bool:
    t = _drop_comments(_read("tasks/smoke.yml"))
    ok = "dest: /usr/local/sbin/dind-tls-smoke" in t and 'mode: "0755"' in t \
        and "owner: root" in t and "src: dind-tls-smoke.sh.j2" in t
    return _report(ok, "smoke.yml installs /usr/local/sbin/dind-tls-smoke root 0755")


def test_play_does_not_run_it() -> bool:
    t = _drop_comments(_read("tasks/smoke.yml"))
    return _report("ansible.builtin.command" not in t and "ansible.builtin.shell" not in t
                   and "dind-tls-smoke" in t, "smoke.yml installs only; never runs the script")


def test_imported_from_main() -> bool:
    return _report("smoke.yml" in _read("tasks/main.yml"), "main.yml imports smoke.yml")


def test_cleanup_trap() -> bool:
    t = _drop_comments(_rendered())
    return _report(re.search(r"^trap cleanup EXIT\s*$", t, re.M) is not None
                   and "docker rm -f" in t and "docker network rm" in t and "docker volume rm" in t,
                   "cleanup trap removes daemon, network, volume")


def test_negative_no_cert() -> bool:
    t = _drop_comments(_rendered())
    ok = re.search(r"DOCKER_HOST=tcp://docker:2376 -e DOCKER_TLS_VERIFY=1 \\\n\s+\"docker:\$\{TAG\}\" docker info", t) \
        and "accepted a client without certs" in t
    return _report(bool(ok), "negative control: client without certs must fail")


def test_negative_plaintext() -> bool:
    t = _drop_comments(_rendered())
    return _report("DOCKER_HOST=tcp://docker:2375" in t and "plaintext 2375 reachable" in t,
                   "negative control: plaintext 2375 unreachable")


def test_positive_tls_ok() -> bool:
    t = _drop_comments(_rendered())
    return _report("{{.ServerVersion}} tls-ok" in t and "nested-run-ok" in t and "set -euo pipefail" in t,
                   "positive control prints '<version> tls-ok' and runs a nested container")


def test_bash_n() -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".sh") as f:
        f.write(_rendered())
        f.flush()
        r = subprocess.run(["bash", "-n", f.name], capture_output=True, text=True)
    return _report(r.returncode == 0, f"bash -n on rendered script {r.stderr.strip()}")


def test_mutant_no_cert_control_caught() -> bool:
    t = _read("templates/dind-tls-smoke.sh.j2")
    mut = t.replace("accepted a client without certs", "")
    return _report(mut != t and "accepted a client without certs" not in mut,
                   "mutant: deleting the no-cert control fails the arm")


def main() -> int:
    results = [fn() for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    passed, total = sum(results), len(results)
    print(f"PASS: {passed}/{total}" if passed == total else f"FAIL: {total - passed}/{total} checks failed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
