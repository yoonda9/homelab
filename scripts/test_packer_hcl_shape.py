"""Shape + packer-validate tests for each packer/*.pkr.hcl file.

Per design §7.2 — asserts full `packer validate` succeeds (with
PKR_VAR_* stubs; no `-syntax-only` so plugin schema bugs surface)
and that each per-template file declares template_name = "pkr-<key>"
and a fixed vm_id literal. The required_plugins.proxmox block at
version "~> 1.2" is checked once at directory level (packer treats
the dir as one config root and rejects duplicate required_plugins
blocks across files).
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
    "ubuntu26.pkr.hcl":   ("pkr-ubuntu26",            9100, "proxmox-iso.ubuntu26"),
    "fedora.pkr.hcl":     ("pkr-fedora-workstation", 9101, "proxmox-iso.fedora"),
    "windows11.pkr.hcl":  ("pkr-win11",               9102, "proxmox-iso.windows11"),
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
        diag = (init.stdout + init.stderr).strip().replace("\n", " | ") or "(no output)"
        print(f"FAIL: packer init: {diag}")
        return False
    all_ok = True
    for fname, (_name, _vmid, source) in EXPECTED.items():
        path = PACKER_DIR / fname
        if not path.is_file():
            print(f"FAIL: {fname} does not exist")
            all_ok = False
            continue
        # `-only=<source> .` validates the directory (so shared variables
        # and required_plugins resolve) but exercises only this template's
        # source. Per-file `packer validate <file>` skips other files in
        # the directory and fails to resolve shared symbols.
        v = subprocess.run(
            ["packer", "validate", f"-only={source}", "."],
            cwd=PACKER_DIR, env=env, capture_output=True, text=True,
        )
        ok = v.returncode == 0
        status = "OK" if ok else "FAIL"
        diag = (v.stdout + v.stderr).strip().replace("\n", " | ") or "clean"
        print(f"{status}: packer validate -only={source} . ({diag})")
        all_ok = all_ok and ok
    return all_ok


def test_per_file_literals() -> bool:
    if not PACKER_DIR.is_dir():
        print(f"FAIL: packer dir missing at {PACKER_DIR}")
        return False
    all_ok = True
    for fname, (expected_name, expected_id, _source) in EXPECTED.items():
        path = PACKER_DIR / fname
        if not path.is_file():
            print(f"FAIL: {fname} missing")
            all_ok = False
            continue
        body = path.read_text()
        checks = {
            f'template_name = "{expected_name}"': bool(
                re.search(rf'template_name\s*=\s*"{expected_name}"', body)
            ),
            f"vm_id = {expected_id}": bool(re.search(rf'\bvm_id\s*=\s*{expected_id}\b', body)),
        }
        for what, ok in checks.items():
            status = "OK" if ok else "FAIL"
            print(f"{status}: {fname}: {what}")
            all_ok = all_ok and ok
    return all_ok


def test_required_plugins_declared_once() -> bool:
    """`required_plugins.proxmox` at "~> 1.2" must appear exactly once
    across packer/*.pkr.hcl. Packer rejects duplicate blocks across
    files, so the canonical home is a single shared file.
    """
    if not PACKER_DIR.is_dir():
        print(f"FAIL: packer dir missing at {PACKER_DIR}")
        return False
    pattern = re.compile(
        r'required_plugins\s*\{[^}]*proxmox\s*=\s*\{[^}]*~>\s*1\.2',
        re.DOTALL,
    )
    hits = [p.name for p in sorted(PACKER_DIR.glob("*.pkr.hcl")) if pattern.search(p.read_text())]
    ok = len(hits) == 1
    status = "OK" if ok else "FAIL"
    print(f"{status}: required_plugins.proxmox ~> 1.2 declared in {hits} (want exactly 1)")
    return ok


def main() -> int:
    results = [
        test_packer_init_and_validate(),
        test_per_file_literals(),
        test_required_plugins_declared_once(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
