"""Win11 install-time CD-ROM shape tests (C-10)."""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKR = REPO_ROOT / "packer" / "windows11.pkr.hcl"


def find_blocks(body: str, kind: str) -> list[str]:
    blocks: list[str] = []
    for m in re.finditer(rf'\b{re.escape(kind)}\s*\{{', body):
        start, depth, i = m.end(), 1, m.end()
        while i < len(body) and depth > 0:
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
            i += 1
        blocks.append(body[start:i - 1])
    return blocks


def test_one_boot_iso_two_additional() -> bool:
    if not PKR.is_file():
        print(f"FAIL: {PKR.name} missing")
        return False
    body = PKR.read_text()
    n_boot = len(find_blocks(body, "boot_iso"))
    n_addl = len(find_blocks(body, "additional_iso_files"))
    ok = n_boot == 1 and n_addl == 2
    print(
        f"{'OK' if ok else 'FAIL'}: boot_iso count={n_boot} (expect 1), "
        f"additional_iso_files count={n_addl} (expect 2)"
    )
    return ok


def test_boot_iso_is_win11() -> bool:
    if not PKR.is_file():
        print(f"FAIL: {PKR.name} missing")
        return False
    body = PKR.read_text()
    blocks = find_blocks(body, "boot_iso")
    if not blocks:
        print("FAIL: no boot_iso block")
        return False
    ok = (
        "iso_file" in blocks[0]
        and "local:iso/Win11_24H2_EnglishInternational_x64.iso" in blocks[0]
        and re.search(r'\btype\s*=\s*"sata"', blocks[0])
    )
    print(f"{'OK' if ok else 'FAIL'}: boot_iso targets local:iso/Win11_24H2_EnglishInternational_x64.iso on SATA")
    return bool(ok)


def test_one_additional_is_virtio() -> bool:
    if not PKR.is_file():
        print(f"FAIL: {PKR.name} missing")
        return False
    body = PKR.read_text()
    blocks = find_blocks(body, "additional_iso_files")
    hits = [
        b for b in blocks
        if "local:iso/virtio-win-0.1.262.iso" in b
        and re.search(r'\btype\s*=\s*"sata"', b)
    ]
    ok = len(hits) == 1
    print(f"{'OK' if ok else 'FAIL'}: exactly one additional_iso_files for virtio-win-0.1.262.iso on SATA (found {len(hits)})")
    return ok


def test_one_additional_is_autounattend_via_upload() -> bool:
    if not PKR.is_file():
        print(f"FAIL: {PKR.name} missing")
        return False
    body = PKR.read_text()
    blocks = find_blocks(body, "additional_iso_files")
    hits = [
        b for b in blocks
        if "iso_url" in b
        and "autounattend-win11.iso" in b
        and re.search(r'iso_storage_pool\s*=\s*"local"', b)
        and re.search(r'iso_download_pve\s*=\s*true', b)
        and re.search(r'\btype\s*=\s*"sata"', b)
    ]
    ok = len(hits) == 1
    print(f"{'OK' if ok else 'FAIL'}: exactly one additional_iso_files uses iso_url+iso_download_pve for autounattend-win11.iso (found {len(hits)})")
    return ok


def test_q35_ovmf_tpm_efi() -> bool:
    if not PKR.is_file():
        print(f"FAIL: {PKR.name} missing")
        return False
    body = PKR.read_text()
    checks = {
        'bios = "ovmf"':                bool(re.search(r'\bbios\s*=\s*"ovmf"', body)),
        'machine = "q35"':              bool(re.search(r'\bmachine\s*=\s*"q35"', body)),
        'tpm_config version v2.0':      bool(re.search(r'tpm_config\s*\{[^}]*version\s*=\s*"v2\.0"', body, re.DOTALL)),
        'efi_config pre_enrolled_keys': bool(re.search(r'efi_config\s*\{[^}]*pre_enrolled_keys\s*=\s*true', body, re.DOTALL)),
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def main() -> int:
    results = [
        test_one_boot_iso_two_additional(),
        test_boot_iso_is_win11(),
        test_one_additional_is_virtio(),
        test_one_additional_is_autounattend_via_upload(),
        test_q35_ovmf_tpm_efi(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
