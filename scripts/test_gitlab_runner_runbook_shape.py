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


def main() -> int:
    results = [test_headings(), test_toc_lists_sections(), test_create_vm_body()]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
