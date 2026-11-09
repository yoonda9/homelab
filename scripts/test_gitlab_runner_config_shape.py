"""Shape tests for ansible/roles/gitlab_runner/templates/config.toml.j2 (gitlab-runner Step 4b).

The template uses Ansible filters (to_json, selectattr), and the gate's Python
has no jinja2, so each arm renders through Ansible itself:
``ansible localhost -c local -m ansible.builtin.template`` into a temp dir,
then ``tomllib`` parses the output. Mutant arms render an edited copy of the
template and require the matching assertion to turn red.
"""

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import tomllib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "gitlab_runner"
TEMPLATE = ROLE / "templates" / "config.toml.j2"
DEFAULTS = ROLE / "defaults" / "main.yml"

TOKENS = {"vault_gitlab_runner_tokens": {"r-here": "glrt-aaaa", "r-other": "glrt-bbbb"}}
RUNNERS = [
    {"name": "r-here", "host": "localhost", "id": 11, "limit": 2},
    {"name": "r-other", "host": "elsewhere", "id": 22},
]


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def _ansible() -> list[str]:
    return ["mise", "exec", "--", "ansible"] if shutil.which("mise") else ["ansible"]


def _render(runners, template: pathlib.Path = TEMPLATE):
    """Render the template through Ansible; return (parsed toml | None, raw text)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = pathlib.Path(tmp)
        fixture = tmp_p / "fixture.json"
        fixture.write_text(json.dumps({**TOKENS, "gitlab_runner_runners": runners, "ansible_host": "10.0.0.5"}))
        out = tmp_p / "config.toml"
        cmd = _ansible() + [
            "localhost", "-c", "local", "-m", "ansible.builtin.template",
            "-a", f"src={template} dest={out}",
            "-e", f"@{DEFAULTS}", "-e", f"@{fixture}",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, check=False)
        if proc.returncode != 0 or not out.is_file():
            return None, proc.stdout + proc.stderr
        text = out.read_text()
        try:
            return tomllib.loads(text), text
        except tomllib.TOMLDecodeError as exc:
            return None, f"{exc}\n{text}"


def _runner(runners=RUNNERS, template: pathlib.Path = TEMPLATE):
    cfg, text = _render(runners, template)
    rs = (cfg or {}).get("runners", [])
    return cfg, text, (rs[0] if rs else {})


def test_template_exists() -> bool:
    return _report(TEMPLATE.is_file(), "templates/config.toml.j2 exists")


def test_empty_list_zero_runners() -> bool:
    cfg, text = _render([])
    ok = cfg is not None and "runners" not in cfg
    return _report(ok, f"an empty runner list renders valid TOML with zero [[runners]] ({text[:80] if cfg is None else 'ok'})")


def test_global_settings() -> bool:
    cfg, _ = _render([])
    ok = bool(cfg) and cfg.get("concurrent") == 4 and cfg.get("check_interval") == 3 \
        and cfg.get("listen_address") == "10.0.0.5:9252" and cfg.get("shutdown_timeout") == 30
    return _report(ok, "concurrent/check_interval/listen_address/shutdown_timeout rendered")


def test_only_current_host_rendered() -> bool:
    cfg, _ = _render(RUNNERS)
    names = [r.get("name") for r in (cfg or {}).get("runners", [])]
    return _report(names == ["r-here"], f"only the current host's runner is rendered (got {names})")


def test_runner_fields() -> bool:
    _, _, r = _runner()
    ok = r.get("url") == "https://gitlab.com" and r.get("id") == 11 and r.get("token") == "glrt-aaaa" \
        and r.get("executor") == "docker" and r.get("limit") == 2 and r.get("request_concurrency") == 2
    return _report(ok, "runner url/id/token/executor/limit/request_concurrency")


def test_docker_section() -> bool:
    _, _, r = _runner()
    d = r.get("docker", {})
    ok = d.get("image") == "alpine:3.22" and d.get("shm_size") == 2147483648 \
        and d.get("pull_policy") == ["if-not-present"] \
        and d.get("allowed_pull_policies") == ["always", "if-not-present"] \
        and d.get("disable_cache") is False
    return _report(ok, "docker image/shm_size/pull_policy/allowed_pull_policies")


def test_volumes_exact() -> bool:
    _, _, r = _runner()
    v = r.get("docker", {}).get("volumes")
    return _report(v == ["/certs/client", "/cache"] and all(":" not in x for x in v or [":"]),
                   f"volumes exactly [/certs/client, /cache], no host bind (got {v})")


def test_privilege_split() -> bool:
    _, _, r = _runner()
    d = r.get("docker", {})
    ok = d.get("privileged") is False and d.get("services_privileged") is True \
        and d.get("allowed_privileged_services") == ["docker:*-dind"]
    return _report(ok, "privileged=false, services_privileged=true, dind pattern")


def test_feature_flags() -> bool:
    _, _, r = _runner()
    ff = r.get("feature_flags", {})
    return _report(ff.get("FF_NETWORK_PER_BUILD") is True and ff.get("FF_ENABLE_JOB_CLEANUP") is True,
                   "both feature flags true")


def test_forbidden_keys_absent() -> bool:
    cfg, text, r = _runner()
    ok = cfg is not None and not any(k in text for k in ("disable_entrypoint_overwrite", "token_expires_at", "token_obtained_at"))
    return _report(ok, "disable_entrypoint_overwrite and token_*_at absent")


def test_no_register_in_role() -> bool:
    offenders = [str(p.relative_to(ROLE)) for p in ROLE.rglob("*")
                 if p.is_file() and "gitlab-runner register" in p.read_text(errors="ignore")]
    return _report(not offenders, f"no 'gitlab-runner register' anywhere in the role (offenders: {offenders})")


def _mutant(old: str, new: str) -> pathlib.Path | None:
    text = TEMPLATE.read_text() if TEMPLATE.is_file() else ""
    if old not in text:
        return None
    d = pathlib.Path(tempfile.mkdtemp())
    p = d / "config.toml.j2"
    p.write_text(text.replace(old, new, 1))
    return p


def test_mutants_are_caught() -> bool:
    """Each mutant must turn the matching assertion red (checked on the mutant render)."""
    results = []
    m = _mutant("privileged = false", "privileged = true")
    _, _, r = _runner(template=m) if m else (None, "", {})
    results.append(("privileged=true", bool(m) and r.get("docker", {}).get("privileged") is not False))
    m = _mutant('{{ gitlab_runner_volumes | to_json }}', '["/var/run/docker.sock:/var/run/docker.sock", "/cache"]')
    _, _, r = _runner(template=m) if m else (None, "", {})
    results.append(("host bind", bool(m) and any(":" in x for x in r.get("docker", {}).get("volumes", []))))
    m = _mutant("  executor =", '  token_expires_at = "2099-01-01T00:00:00Z"\n  executor =')
    cfg, text, _r = _runner(template=m) if m else (None, "", {})
    results.append(("token_expires_at", bool(m) and "token_expires_at" in text))
    bad = [n for n, caught in results if not caught]
    return _report(not bad, f"mutants privileged=true, host bind, token_expires_at each turn an arm red (uncaught: {bad})")


def main() -> int:
    results = [fn() for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
