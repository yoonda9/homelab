"""Win11 build-time communicator tests (C-9)."""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKR = REPO_ROOT / "packer" / "windows11.pkr.hcl"
AUNT = REPO_ROOT / "packer" / "autounattend" / "windows11" / "autounattend.xml"


def find_provisioner_blocks(body: str, kind: str) -> list[str]:
    blocks: list[str] = []
    for m in re.finditer(rf'provisioner\s+"{re.escape(kind)}"\s*\{{', body):
        start, depth, i = m.end(), 1, m.end()
        while i < len(body) and depth > 0:
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
            i += 1
        blocks.append(body[start:i - 1])
    return blocks


def test_winrm_communicator_settings() -> bool:
    if not PKR.is_file():
        print(f"FAIL: {PKR.name} missing")
        return False
    body = PKR.read_text()
    checks = {
        'communicator = "winrm"':      bool(re.search(r'communicator\s*=\s*"winrm"', body)),
        "winrm_use_ssl = false":       bool(re.search(r'winrm_use_ssl\s*=\s*false', body)),
        'winrm_username = "user"':     bool(re.search(r'winrm_username\s*=\s*"user"', body)),
        'winrm_password = "password"': bool(re.search(r'winrm_password\s*=\s*"password"', body)),
        'winrm_timeout = "4h"':        bool(re.search(r'winrm_timeout\s*=\s*"4h"', body)),
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: windows11.pkr.hcl: {what}")
    return all(checks.values())


def test_autounattend_winrm_setup() -> bool:
    if not AUNT.is_file():
        print(f"FAIL: {AUNT.name} missing")
        return False
    body = AUNT.read_text()
    checks = {
        "winrm quickconfig":      "winrm quickconfig" in body,
        "TCP/5985 firewall rule": bool(re.search(r'New-NetFirewallRule[^<]*5985', body, re.IGNORECASE)),
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: autounattend.xml: {what}")
    return all(checks.values())


def test_openssh_install_then_verify_then_sysprep() -> bool:
    if not PKR.is_file():
        print(f"FAIL: {PKR.name} missing")
        return False
    body = PKR.read_text()
    ps = find_provisioner_blocks(body, "powershell")
    install_idx = next(
        (i for i, b in enumerate(ps) if "OpenSSH.Server" in b and "Add-WindowsCapability" in b), -1
    )
    verify_idx = next(
        (i for i, b in enumerate(ps) if re.search(r"\(Get-Service\s+sshd\)\.Status\s*-eq\s*'Running'", b)), -1
    )
    sysprep_idx = next(
        (i for i, b in enumerate(ps) if "sysprep.exe /generalize /oobe /shutdown" in b), -1
    )
    ok = (
        install_idx != -1
        and verify_idx != -1
        and sysprep_idx != -1
        and install_idx < verify_idx < sysprep_idx
    )
    print(
        f"{'OK' if ok else 'FAIL'}: provisioner order "
        f"install({install_idx}) < verify({verify_idx}) < sysprep({sysprep_idx})"
    )
    return ok


def main() -> int:
    results = [
        test_winrm_communicator_settings(),
        test_autounattend_winrm_setup(),
        test_openssh_install_then_verify_then_sysprep(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
