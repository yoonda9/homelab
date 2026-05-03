"""Cross-tool VM-ID contract test (per design §5).

Asserts that for each OS short-name, the vm_id literal in
packer/<file>.pkr.hcl matches the entry in tofu/locals.tf's
template_ids map. Catches cross-swap mutations via brace-balanced
extraction (per mem-1777521206-b3c1).
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOFU_LOCALS = REPO_ROOT / "tofu" / "locals.tf"
PACKER_FILES = {
    "ubuntu26": REPO_ROOT / "packer" / "ubuntu26.pkr.hcl",
    "fedora":   REPO_ROOT / "packer" / "fedora.pkr.hcl",
    "win11":    REPO_ROOT / "packer" / "windows11.pkr.hcl",
}


def extract_template_ids_map(body: str) -> dict[str, int] | None:
    """Brace-balanced extraction of the template_ids = { ... } body."""
    m = re.search(r'template_ids\s*=\s*\{', body)
    if not m:
        return None
    start = m.end()
    depth = 1
    i = start
    while i < len(body) and depth > 0:
        if body[i] == "{":
            depth += 1
        elif body[i] == "}":
            depth -= 1
        i += 1
    if depth != 0:
        return None
    inner = body[start:i - 1]
    ids: dict[str, int] = {}
    for line in inner.splitlines():
        m = re.match(r'\s*(\w+)\s*=\s*(\d+)', line)
        if m:
            ids[m.group(1)] = int(m.group(2))
    return ids


def extract_packer_vm_id(path: pathlib.Path) -> int | None:
    if not path.is_file():
        return None
    body = path.read_text()
    m = re.search(r'\bvm_id\s*=\s*(\d+)', body)
    return int(m.group(1)) if m else None


def test_locals_map_parseable() -> bool:
    if not TOFU_LOCALS.is_file():
        print(f"FAIL: tofu/locals.tf missing at {TOFU_LOCALS}")
        return False
    ids = extract_template_ids_map(TOFU_LOCALS.read_text())
    ok = ids is not None and set(ids) == {"ubuntu26", "fedora", "win11"}
    print(f"{'OK' if ok else 'FAIL'}: tofu/locals.tf template_ids = {ids}")
    return ok


def test_per_os_contract() -> bool:
    if not TOFU_LOCALS.is_file():
        print(f"FAIL: tofu/locals.tf missing at {TOFU_LOCALS}")
        return False
    ids = extract_template_ids_map(TOFU_LOCALS.read_text()) or {}
    all_ok = True
    for os_key, packer_path in PACKER_FILES.items():
        local_id = ids.get(os_key)
        packer_id = extract_packer_vm_id(packer_path)
        if packer_id is None:
            ok = False
            print(f"FAIL: {packer_path.name} missing or has no vm_id literal")
        else:
            ok = local_id == packer_id
            status = "OK" if ok else "FAIL"
            print(f"{status}: {os_key}: locals={local_id}, packer={packer_id}")
        all_ok = all_ok and ok
    return all_ok


def main() -> int:
    results = [test_locals_map_parseable(), test_per_os_contract()]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
