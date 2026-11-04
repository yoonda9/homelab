"""Shape tests for docs/runbooks/gitlab-runner.md (gitlab-runner Step 2e).

Pins only the sections that exist so far: the section headings, and the
create-the-VM body (pre-checks, plan/apply, guest-agent recovery). Later steps
extend REQUIRED_HEADINGS as they fill sections in. Stdlib only.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "gitlab-runner.md"

REQUIRED_HEADINGS = (
    "Create the VM",
    "Register a runner",
    "Add a project",
    "Rotate a token",
    "Upgrade",
    "Clean disk",
    "Troubleshooting",
    "Security model",
    "GitLab-side hygiene",
    "Known limits",
)


def _body() -> str:
    return RUNBOOK.read_text() if RUNBOOK.is_file() else ""


def _section(body: str, title: str) -> str:
    m = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def test_headings() -> bool:
    body = _body()
    missing = [h for h in REQUIRED_HEADINGS if not re.search(rf"^## {re.escape(h)}\s*$", body, re.M)]
    return _report(not missing, f"runbook has every required section heading (missing: {missing})")


def test_toc_lists_sections() -> bool:
    toc = _section(_body(), "Table of contents")
    missing = [h for h in REQUIRED_HEADINGS if f"[{h}]" not in toc]
    return _report(not missing, f"table of contents links every required section (missing: {missing})")


def test_create_vm_body() -> bool:
    s = _section(_body(), "Create the VM")
    checks = {
        "pvesm status": "pvesm status" in s,
        "150 GB on local-lvm": re.search(r"150\s*GB", s) is not None and "local-lvm" in s,
        ".120 free / outside DHCP": "192.168.1.120" in s and "DHCP" in s,
        "just plan": "just plan" in s,
        "just apply": "just apply" in s,
        "qm guest exec": "qm guest exec" in s,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"create-the-VM section is filled in (missing: {bad})")


def test_security_model_body() -> bool:
    s = _section(_body(), "Security model")
    checks = {
        "Developer-or-above = root claim": re.search(r"Developer", s) and re.search(r"root\s+on\s+the\s+runner\s+VM", s),
        "all its tokens": re.search(r"all\s+its\s+tokens", s) is not None,
        "trusted projects only": re.search(r"only\s+trusted\s+projects", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"security-model section states the trust boundary (missing: {bad})")


def test_hygiene_body() -> bool:
    s = _section(_body(), "GitLab-side hygiene")
    checks = {
        "runner locked to project": re.search(r"locked to (its|the) project", s) is not None,
        "fork pipelines off": re.search(r"fork pipelines", s, re.I) is not None and re.search(r"\boff\b", s) is not None,
        "max timeout 5400-5700 s": re.search(r"5400\s*[-–]\s*5700\s*s", s) is not None,
        "job-token allowlist default": "allowlist" in s and re.search(r"default", s) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"GitLab-side hygiene section lists the four settings (missing: {bad})")


def test_known_limits_body() -> bool:
    s = _section(_body(), "Known limits")
    checks = {
        "no Alertmanager": "Alertmanager" in s,
        "split manager follow-up": re.search(r"split manager", s, re.I) is not None,
        "sysbox follow-up": re.search(r"sysbox", s, re.I) is not None,
    }
    bad = [k for k, v in checks.items() if not v]
    return _report(not bad, f"known-limits section names the three limits (missing: {bad})")


def main() -> int:
    results = [
        test_headings(),
        test_toc_lists_sections(),
        test_create_vm_body(),
        test_security_model_body(),
        test_hygiene_body(),
        test_known_limits_body(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
