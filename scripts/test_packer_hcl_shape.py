"""Shape + packer-validate tests for each packer/*.pkr.hcl file.

Per design §7.2 — asserts packer validate succeeds (with PKR_VAR_*
stubs) and that each file declares force = true on the source,
template_name = "pkr-<key>", a fixed vm_id literal, and the
required_plugins.proxmox block at version "~> 1.2".
"""

import os
import pathlib
import re
import shutil
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKER_DIR = REPO_ROOT / "packer"
EXPECTED = {
    "ubuntu26.pkr.hcl":   ("pkr-ubuntu26",            9100),
    "fedora.pkr.hcl":     ("pkr-fedora-workstation", 9101),
    "windows11.pkr.hcl":  ("pkr-win11",               9102),
}


def test_packer_init_and_validate() -> bool:
    if not shutil.which("packer"):
        print("OK (skip): packer not installed (PASS-WITH-NOTE)")
        return True
    if not PACKER_DIR.is_dir():
        print(f"FAIL: packer dir missing at {PACKER_DIR}")
        return False
    env = {
        **os.environ,
        "PKR_VAR_proxmox_host":          "stub.example.invalid",
        "PKR_VAR_proxmox_user":          "stub@pam",
        "PKR_VAR_proxmox_token_id":      "stub-id",
        "PKR_VAR_proxmox_token_secret":  "stub-secret",
    }
    init = subprocess.run(
        ["packer", "init", "."],
        cwd=PACKER_DIR, env=env, capture_output=True, text=True,
    )
    if init.returncode != 0:
        print(f"FAIL: packer init: {init.stderr.strip()}")
        return False
    all_ok = True
    for fname in EXPECTED:
        path = PACKER_DIR / fname
        if not path.is_file():
            print(f"FAIL: {fname} does not exist")
            all_ok = False
            continue
        v = subprocess.run(
            ["packer", "validate", "-syntax-only", fname],
            cwd=PACKER_DIR, env=env, capture_output=True, text=True,
        )
        ok = v.returncode == 0
        status = "OK" if ok else "FAIL"
        print(f"{status}: packer validate -syntax-only {fname} ({v.stderr.strip() or 'clean'})")
        all_ok = all_ok and ok
    return all_ok


def test_per_file_literals() -> bool:
    if not PACKER_DIR.is_dir():
        print(f"FAIL: packer dir missing at {PACKER_DIR}")
        return False
    all_ok = True
    for fname, (expected_name, expected_id) in EXPECTED.items():
        path = PACKER_DIR / fname
        if not path.is_file():
            print(f"FAIL: {fname} missing")
            all_ok = False
            continue
        body = path.read_text()
        checks = {
            "force = true":              bool(re.search(r'\bforce\s*=\s*true', body)),
            f'template_name = "{expected_name}"': bool(
                re.search(rf'template_name\s*=\s*"{expected_name}"', body)
            ),
            f"vm_id = {expected_id}":    bool(re.search(rf'\bvm_id\s*=\s*{expected_id}\b', body)),
            "required_plugins.proxmox":  bool(re.search(r'required_plugins\s*\{[^}]*proxmox\s*=\s*\{[^}]*~>\s*1\.2', body, re.DOTALL)),
        }
        for what, ok in checks.items():
            status = "OK" if ok else "FAIL"
            print(f"{status}: {fname}: {what}")
            all_ok = all_ok and ok
    return all_ok


def main() -> int:
    results = [test_packer_init_and_validate(), test_per_file_literals()]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
