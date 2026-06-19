"""Cloud-image + NoCloud seed shape test for Linux packer templates.

Step 2 (packer-cloud-images) RED → GREEN contract for
``packer/ubuntu26.pkr.hcl``: the rewritten template uses the
``proxmox-clone`` source against a pre-bootstrapped Cloud-Init source
template on the PVE node and feeds first-boot config via a NoCloud
``cidata`` seed CD attached as ``additional_iso_files`` with on-the-fly
``cd_files`` generation.

Step 3 extends the same five-assertion contract to
``packer/fedora.pkr.hcl`` by parametrizing each test over a
``(os_name, pkr_path, seed_dir)`` tuple. Until Step 3b rewrites
fedora.pkr.hcl, the four content assertions for fedora are expected
to FAIL — that is the RED proof.

Asserts (per-OS, against the file under ``packer/<os>.pkr.hcl``):

(a) ZERO ``boot_command`` blocks (cloud images skip the installer
    keystroke phase entirely).
(b) ZERO ``http_directory`` attribute (no autoinstall HTTP server).
(c) Exactly ONE ``additional_iso_files`` block whose body contains
    ``cd_label = "cidata"`` (NoCloud datasource volume label).
(d) ``cd_files`` cite ``${path.root}/seed/<os>/user-data`` and
    ``${path.root}/seed/<os>/meta-data``.
(e) Seed source files exist at
    ``packer/seed/<os>/{user-data,meta-data}``.

For the negative assertions (a) and (b), per ``mem-1777478162-68e8``,
substring matches over the full file body would falsely pass when the
keyword appears only in a comment block. Scan code lines (skip lines
whose ``lstrip`` starts with ``#`` — HCL line-comment marker) so the
mutate-restore pattern (move keyword in/out of code) bites correctly.

Block extraction reuses the brace-balanced approach from
``scripts/test_pkr_seal_step.py`` and ``scripts/test_pkr_win11_iso_attachment.py``.
"""

import pathlib
import re
import sys
from dataclasses import dataclass

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKER_DIR = REPO_ROOT / "packer"
SEED_FILES = ("user-data", "meta-data")


@dataclass(frozen=True)
class OSSpec:
    """One parametrized target for the cloud-seed shape contract."""

    os_name: str
    pkr_path: pathlib.Path
    seed_dir: pathlib.Path


OS_SPECS: tuple[OSSpec, ...] = (
    OSSpec(
        os_name="ubuntu26",
        pkr_path=PACKER_DIR / "ubuntu26.pkr.hcl",
        seed_dir=PACKER_DIR / "seed" / "ubuntu26",
    ),
    OSSpec(
        os_name="fedora",
        pkr_path=PACKER_DIR / "fedora.pkr.hcl",
        seed_dir=PACKER_DIR / "seed" / "fedora",
    ),
)


def code_lines(body: str) -> list[str]:
    """Return only lines that are not blank and are not HCL line comments
    (`# ...`). Mirrors the comment-skipping invariant in
    `mem-1777478162-68e8` so substring checks over the full body can't
    falsely pass on a commented-out occurrence.
    """
    out: list[str] = []
    for raw in body.splitlines():
        stripped = raw.lstrip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        out.append(raw)
    return out


def find_blocks(body: str, kind: str) -> list[str]:
    """Brace-balanced extraction of all `<kind> { ... }` blocks in order."""
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


def test_no_boot_command(spec: OSSpec) -> bool:
    if not spec.pkr_path.is_file():
        print(f"FAIL: {spec.pkr_path.name} missing")
        return False
    body = spec.pkr_path.read_text()
    code = "\n".join(code_lines(body))
    hits = re.findall(r'\bboot_command\b', code)
    ok = len(hits) == 0
    print(
        f"{'OK' if ok else 'FAIL'}: {spec.os_name}: zero boot_command in "
        f"code lines (found {len(hits)})"
    )
    return ok


def test_no_http_directory(spec: OSSpec) -> bool:
    if not spec.pkr_path.is_file():
        print(f"FAIL: {spec.pkr_path.name} missing")
        return False
    body = spec.pkr_path.read_text()
    code = "\n".join(code_lines(body))
    hits = re.findall(r'\bhttp_directory\b', code)
    ok = len(hits) == 0
    print(
        f"{'OK' if ok else 'FAIL'}: {spec.os_name}: zero http_directory in "
        f"code lines (found {len(hits)})"
    )
    return ok


def test_one_additional_iso_files_with_cidata(spec: OSSpec) -> bool:
    if not spec.pkr_path.is_file():
        print(f"FAIL: {spec.pkr_path.name} missing")
        return False
    body = spec.pkr_path.read_text()
    blocks = find_blocks(body, "additional_iso_files")
    cidata_blocks = [
        b for b in blocks
        if re.search(r'\bcd_label\s*=\s*"cidata"', b)
    ]
    ok = len(cidata_blocks) == 1
    print(
        f"{'OK' if ok else 'FAIL'}: {spec.os_name}: exactly one "
        f"additional_iso_files block with cd_label = \"cidata\" "
        f"(found {len(cidata_blocks)} of {len(blocks)} total)"
    )
    return ok


def test_cd_files_cite_seed_paths(spec: OSSpec) -> bool:
    if not spec.pkr_path.is_file():
        print(f"FAIL: {spec.pkr_path.name} missing")
        return False
    body = spec.pkr_path.read_text()
    blocks = find_blocks(body, "additional_iso_files")
    cidata_blocks = [
        b for b in blocks
        if re.search(r'\bcd_label\s*=\s*"cidata"', b)
    ]
    if len(cidata_blocks) != 1:
        print(
            f"FAIL: {spec.os_name}: cannot inspect cd_files — need exactly "
            f"one cidata additional_iso_files block "
            f"(found {len(cidata_blocks)})"
        )
        return False
    block = cidata_blocks[0]
    expected = [
        rf'\$\{{path\.root\}}/seed/{re.escape(spec.os_name)}/user-data',
        rf'\$\{{path\.root\}}/seed/{re.escape(spec.os_name)}/meta-data',
    ]
    missing = [pat for pat in expected if not re.search(pat, block)]
    ok = not missing
    if ok:
        print(
            f"OK: {spec.os_name}: cd_files cite "
            f"${{path.root}}/seed/{spec.os_name}/{{user-data,meta-data}}"
        )
    else:
        print(
            f"FAIL: {spec.os_name}: cidata block missing cd_files entries: "
            f"{missing}"
        )
    return ok


def test_seed_source_files_exist(spec: OSSpec) -> bool:
    missing = [name for name in SEED_FILES if not (spec.seed_dir / name).is_file()]
    ok = not missing
    if ok:
        print(
            f"OK: {spec.os_name}: seed source files exist: "
            f"{spec.seed_dir}/{{{','.join(SEED_FILES)}}}"
        )
    else:
        print(
            f"FAIL: {spec.os_name}: seed source files missing under "
            f"{spec.seed_dir}: {missing}"
        )
    return ok


PER_OS_TESTS = (
    test_no_boot_command,
    test_no_http_directory,
    test_one_additional_iso_files_with_cidata,
    test_cd_files_cite_seed_paths,
    test_seed_source_files_exist,
)


def main() -> int:
    results: list[bool] = []
    for spec in OS_SPECS:
        for fn in PER_OS_TESTS:
            results.append(fn(spec))
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
