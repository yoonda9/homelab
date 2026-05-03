"""Per-OS template seal step tests (C-8)."""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKER_DIR = REPO_ROOT / "packer"


def find_provisioner_blocks(body: str, kind: str) -> list[str]:
    """Brace-balanced extraction of all `provisioner "<kind>" { ... }` blocks
    in the order they appear in the file."""
    blocks: list[str] = []
    pattern = rf'provisioner\s+"{re.escape(kind)}"\s*\{{'
    for m in re.finditer(pattern, body):
        start = m.end()
        depth = 1
        i = start
        while i < len(body) and depth > 0:
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
            i += 1
        blocks.append(body[start:i - 1])
    return blocks


def assert_linux_seal(path: pathlib.Path, name: str) -> bool:
    if not path.is_file():
        print(f"OK (skip): {path.name} not yet implemented")
        return True
    body = path.read_text()
    shells = find_provisioner_blocks(body, "shell")
    if not shells:
        print(f"FAIL: {name}: no shell provisioner blocks")
        return False
    last = shells[-1]
    checks = {
        "cloud-init clean":            "cloud-init clean" in last,
        "machine-id truncate":         bool(re.search(r'truncate\s+-s\s+0\s+/etc/machine-id', last)),
        "ssh host keys removal":       bool(re.search(r'rm\s+-f\s+/etc/ssh/ssh_host_\*', last)),
    }
    ok = all(checks.values())
    for what, c in checks.items():
        print(f"{'OK' if c else 'FAIL'}: {name} last-shell: {what}")
    return ok


def assert_fedora_dnf_install(path: pathlib.Path) -> bool:
    if not path.is_file():
        print("OK (skip): fedora.pkr.hcl not yet implemented")
        return True
    body = path.read_text()
    shells = find_provisioner_blocks(body, "shell")
    ok = any("dnf install -y cloud-init" in s for s in shells[:-1])  # not the seal step
    print(f"{'OK' if ok else 'FAIL'}: fedora has earlier 'dnf install -y cloud-init' provisioner")
    return ok


def assert_win11_seal(path: pathlib.Path) -> bool:
    if not path.is_file():
        print("OK (skip): windows11.pkr.hcl not yet implemented")
        return True
    body = path.read_text()
    ps = find_provisioner_blocks(body, "powershell")
    if not ps:
        print("FAIL: windows11: no powershell provisioner blocks")
        return False
    sysprep_idx = next((i for i, b in enumerate(ps) if "sysprep.exe /generalize /oobe /shutdown" in b), -1)
    if sysprep_idx == -1:
        print("FAIL: windows11: no sysprep generalize step")
        return False
    verifier_idx = next(
        (i for i, b in enumerate(ps[:sysprep_idx])
         if re.search(r"\(Get-Service\s+sshd\)\.Status\s*-eq\s*'Running'", b)),
        -1,
    )
    ok = verifier_idx != -1
    print(f"{'OK' if ok else 'FAIL'}: windows11: pre-sysprep sshd verifier (idx={verifier_idx}) precedes sysprep (idx={sysprep_idx})")
    return ok


def main() -> int:
    results = [
        assert_linux_seal(PACKER_DIR / "ubuntu26.pkr.hcl", "ubuntu26"),
        assert_linux_seal(PACKER_DIR / "fedora.pkr.hcl", "fedora"),
        assert_fedora_dnf_install(PACKER_DIR / "fedora.pkr.hcl"),
        assert_win11_seal(PACKER_DIR / "windows11.pkr.hcl"),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
