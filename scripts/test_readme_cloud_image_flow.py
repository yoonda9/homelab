"""README content shape test for the cloud-image flow (Step 4b).

Defends the README quickstart against drift. The Linux Packer templates
build from cloud images via ``proxmox-clone`` and a NoCloud cidata seed,
the Windows template builds from ISO via ``proxmox-iso`` with sysprep,
and ``scripts/build_template.sh`` is the single entrypoint. The README
must document that flow concretely (copy-pasteable commands, env vars,
template names) and must NOT carry stale autoinstall/kickstart language.

Eleven assertions over ``README.md`` content:

(2a) Mentions "cloud image" (case-insensitive substring) — the new flow
     is named in narrative text.
(2b) Mentions BOTH ``proxmox-clone`` AND ``proxmox-iso`` — defends
     against a half-rewrite that only covers Linux or only Windows.
(2c) Mentions ``NoCloud`` AND ``cidata`` — the seed mechanism per
     DEC-019 Q2.
(2d) References all three template literals: ``pkr-ubuntu26``,
     ``pkr-fedora-workstation``, ``pkr-windows11``.
(2e) Documents ``build_template.sh ubuntu26`` (exact substring).
(2f) Documents ``build_template.sh fedora`` (exact substring).
(2g) Documents ``build_template.sh windows11`` (exact substring).
(2h) Mentions ``bootstrap_cloud_template.sh`` AND both
     ``tpl-cloud-ubuntu26`` and ``tpl-cloud-fedora44`` — the one-time
     Cloud-Init source templates the runner clones from.
(2i) Mentions all four required env vars (``PROXMOX_HOST``,
     ``PROXMOX_USER``, ``PROXMOX_TOKEN_ID``, ``PROXMOX_TOKEN_SECRET``).
(2j) Does NOT mention any of ``autoinstall``, ``kickstart``,
     ``boot_command``, ``http_directory`` (case-insensitive) — defends
     against pasting stale ISO-flow language back in.
(2k) Top-level header ``# Home Lab Auto Deploy`` is preserved.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"


def read_readme() -> str:
    return README.read_text(encoding="utf-8")


def test_mentions_cloud_image() -> bool:
    text = read_readme().lower()
    ok = "cloud image" in text
    print(f"{'OK' if ok else 'FAIL'}: 2a: README mentions 'cloud image'")
    return ok


def test_mentions_both_source_builders() -> bool:
    text = read_readme()
    has_clone = "proxmox-clone" in text
    has_iso = "proxmox-iso" in text
    ok = has_clone and has_iso
    print(
        f"{'OK' if ok else 'FAIL'}: 2b: README mentions proxmox-clone "
        f"({has_clone}) AND proxmox-iso ({has_iso})"
    )
    return ok


def test_mentions_seed_mechanism() -> bool:
    text = read_readme()
    has_nocloud = "NoCloud" in text
    has_cidata = "cidata" in text
    ok = has_nocloud and has_cidata
    print(
        f"{'OK' if ok else 'FAIL'}: 2c: README mentions NoCloud "
        f"({has_nocloud}) AND cidata ({has_cidata})"
    )
    return ok


def test_mentions_all_three_templates() -> bool:
    text = read_readme()
    templates = ("pkr-ubuntu26", "pkr-fedora-workstation", "pkr-windows11")
    missing = [t for t in templates if t not in text]
    ok = not missing
    if ok:
        print(f"OK: 2d: README references all 3 templates: {list(templates)}")
    else:
        print(f"FAIL: 2d: README missing template literals: {missing}")
    return ok


def test_documents_ubuntu_build_command() -> bool:
    ok = "build_template.sh ubuntu26" in read_readme()
    print(f"{'OK' if ok else 'FAIL'}: 2e: README has 'build_template.sh ubuntu26'")
    return ok


def test_documents_fedora_build_command() -> bool:
    ok = "build_template.sh fedora" in read_readme()
    print(f"{'OK' if ok else 'FAIL'}: 2f: README has 'build_template.sh fedora'")
    return ok


def test_documents_windows_build_command() -> bool:
    ok = "build_template.sh windows11" in read_readme()
    print(f"{'OK' if ok else 'FAIL'}: 2g: README has 'build_template.sh windows11'")
    return ok


def test_mentions_bootstrap_and_cloud_sources() -> bool:
    text = read_readme()
    has_bootstrap = "bootstrap_cloud_template.sh" in text
    has_tpl_ubuntu = "tpl-cloud-ubuntu26" in text
    has_tpl_fedora = "tpl-cloud-fedora44" in text
    ok = has_bootstrap and has_tpl_ubuntu and has_tpl_fedora
    print(
        f"{'OK' if ok else 'FAIL'}: 2h: README mentions bootstrap_cloud_template.sh "
        f"({has_bootstrap}) + tpl-cloud-ubuntu26 ({has_tpl_ubuntu}) "
        f"+ tpl-cloud-fedora44 ({has_tpl_fedora})"
    )
    return ok


def test_mentions_required_env_vars() -> bool:
    text = read_readme()
    env_vars = (
        "PROXMOX_HOST",
        "PROXMOX_USER",
        "PROXMOX_TOKEN_ID",
        "PROXMOX_TOKEN_SECRET",
    )
    missing = [v for v in env_vars if v not in text]
    ok = not missing
    if ok:
        print(f"OK: 2i: README mentions all 4 env vars: {list(env_vars)}")
    else:
        print(f"FAIL: 2i: README missing env vars: {missing}")
    return ok


def test_no_stale_iso_flow_language() -> bool:
    text = read_readme().lower()
    forbidden = ("autoinstall", "kickstart", "boot_command", "http_directory")
    found = [tok for tok in forbidden if tok in text]
    ok = not found
    if ok:
        print(f"OK: 2j: README contains none of {list(forbidden)}")
    else:
        print(f"FAIL: 2j: README still mentions stale ISO-flow tokens: {found}")
    return ok


def test_top_level_header_preserved() -> bool:
    first_line = read_readme().splitlines()[0] if README.exists() else ""
    ok = first_line.strip() == "# Home Lab Auto Deploy"
    print(
        f"{'OK' if ok else 'FAIL'}: 2k: README first line is "
        f"'# Home Lab Auto Deploy' (got {first_line!r})"
    )
    return ok


TESTS = (
    test_mentions_cloud_image,
    test_mentions_both_source_builders,
    test_mentions_seed_mechanism,
    test_mentions_all_three_templates,
    test_documents_ubuntu_build_command,
    test_documents_fedora_build_command,
    test_documents_windows_build_command,
    test_mentions_bootstrap_and_cloud_sources,
    test_mentions_required_env_vars,
    test_no_stale_iso_flow_language,
    test_top_level_header_preserved,
)


def main() -> int:
    results = [fn() for fn in TESTS]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
