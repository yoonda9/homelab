"""Tests for scripts/build_template.sh (per design §7.2).

Comment-line-skipping body scan (per mem-1777478162-68e8) so substring
checks don't false-pass on bare comments. shellcheck enforced; shfmt
PASS-WITH-NOTE if missing (per mem-1777477382-ce4f).
"""

import pathlib
import re
import shutil
import stat
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "build_template.sh"
BOOTSTRAP = REPO_ROOT / "scripts" / "bootstrap_cloud_template.sh"


def code_lines(body: str) -> list[str]:
    """Body lines minus blank-and-comment-only lines (per mem-1777478162-68e8)."""
    return [ln for ln in body.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


def code_text(body: str) -> str:
    return "\n".join(code_lines(body))


def test_exists_and_executable() -> bool:
    if not RUNNER.is_file():
        print("FAIL: scripts/build_template.sh missing")
        return False
    mode = RUNNER.stat().st_mode
    ok = bool(mode & stat.S_IXUSR)
    print(f"{'OK' if ok else 'FAIL'}: scripts/build_template.sh executable bit set")
    return ok


def test_shebang_and_set() -> bool:
    if not RUNNER.is_file():
        print("FAIL: shebang/set check skipped — runner missing")
        return False
    body = RUNNER.read_text()
    lines = body.splitlines()
    shebang_ok = lines[0].strip() == "#!/usr/bin/env bash"
    set_ok = any("set -euo pipefail" in ln for ln in lines[:10])
    print(f"{'OK' if shebang_ok else 'FAIL'}: shebang #!/usr/bin/env bash")
    print(f"{'OK' if set_ok else 'FAIL'}: set -euo pipefail in first 10 lines")
    return shebang_ok and set_ok


def test_shellcheck() -> bool:
    if not shutil.which("shellcheck"):
        print("OK (skip): shellcheck not installed")
        return True
    if not RUNNER.is_file():
        print("FAIL: shellcheck skipped — runner missing")
        return False
    r = subprocess.run(["shellcheck", str(RUNNER)], capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"{'OK' if ok else 'FAIL'}: shellcheck ({r.stdout.strip() or 'clean'})")
    return ok


def test_shfmt_format_clean() -> bool:
    if not shutil.which("shfmt"):
        print("OK (skip): shfmt not installed (PASS-WITH-NOTE)")
        return True
    if not RUNNER.is_file():
        print("FAIL: shfmt skipped — runner missing")
        return False
    r = subprocess.run(["shfmt", "-i", "2", "-d", str(RUNNER)], capture_output=True, text=True)
    ok = r.returncode == 0 and not r.stdout.strip()
    print(f"{'OK' if ok else 'FAIL'}: shfmt -i 2 -d clean")
    return ok


def test_arg_validation_and_envvar_preflight() -> bool:
    if not RUNNER.is_file():
        print("FAIL: arg/env preflight skipped — runner missing")
        return False
    body = RUNNER.read_text()
    ct = code_text(body)
    checks = {
        "PROXMOX_HOST preflight":         "PROXMOX_HOST" in ct,
        "PROXMOX_USER preflight":         "PROXMOX_USER" in ct,
        "PROXMOX_TOKEN_ID preflight":     "PROXMOX_TOKEN_ID" in ct,
        "PROXMOX_TOKEN_SECRET preflight": "PROXMOX_TOKEN_SECRET" in ct,
        "ubuntu26 case branch":           bool(re.search(r"\bubuntu26\b", ct)),
        "fedora case branch":             bool(re.search(r"\bfedora\b", ct)),
        "windows11 case branch":          bool(re.search(r"\bwindows11\b", ct)),
        "usage / error on unknown OS":    bool(re.search(r"(usage|Usage|UNKNOWN|unknown)", ct)),
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def test_windows11_specific_steps() -> bool:
    if not RUNNER.is_file():
        print("FAIL: windows11 steps skipped — runner missing")
        return False
    body = RUNNER.read_text()
    ct = code_text(body)
    checks = {
        "command -v genisoimage preflight":   bool(re.search(r"command\s+-v\s+genisoimage", ct)),
        "genisoimage invocation":              bool(re.search(r"\bgenisoimage\b[^|&;]*-volid\s+[\"']?Unattend", ct, re.DOTALL)),
        "autounattend.iso output path":        "autounattend-win11.iso" in ct,
        "packer/autounattend/windows11 input": "packer/autounattend/windows11" in ct,
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def test_packer_init_then_build_force() -> bool:
    if not RUNNER.is_file():
        print("FAIL: packer init/build ordering skipped — runner missing")
        return False
    body = RUNNER.read_text()
    lines = code_lines(body)
    ct = "\n".join(lines)
    init_idx = next((i for i, ln in enumerate(lines) if re.search(r"\bpacker\s+init\b", ln)), -1)
    build_idx = next((i for i, ln in enumerate(lines) if re.search(r"\bpacker\s+build\b", ln)), -1)
    ordered = init_idx != -1 and build_idx != -1 and init_idx < build_idx
    build_uses_force = bool(re.search(r"packer\s+build[^|&;\n]*-force", ct))
    print(f"{'OK' if ordered else 'FAIL'}: packer init (line {init_idx}) precedes packer build (line {build_idx})")
    print(f"{'OK' if build_uses_force else 'FAIL'}: packer build uses -force")
    return ordered and build_uses_force


def test_packer_build_uses_directory_form() -> bool:
    """Regression: packer build must use directory form '-only=<source> .' so
    _variables.pkr.hcl siblings are loaded (per mem-1777854396-6d9e). Single-file
    form 'packer build foo.pkr.hcl' does NOT load directory siblings, leaving
    var.* references undeclared at HCL parse → 8x 'Unsupported attribute' errors.

    The per-OS source mapping (proxmox-clone vs proxmox-iso) is asserted in
    test_per_os_only_flag_mapping; this test stays source-agnostic.
    """
    if not RUNNER.is_file():
        print("FAIL: packer build directory-form check skipped — runner missing")
        return False
    body = RUNNER.read_text()
    lines = code_lines(body)
    # Match the actual command line, not log/echo strings that mention 'packer build'.
    build_lines = [ln for ln in lines if re.search(r"^\s*packer\s+build\b", ln)]
    if not build_lines:
        print("FAIL: no 'packer build' command line found")
        return False
    build_line = build_lines[0]
    uses_only = bool(re.search(r"-only=", build_line))
    # Directory form: trailing '.' as positional arg, NOT a single-file 'X.pkr.hcl'.
    uses_dir = bool(re.search(r"\s\.\s*$", build_line))
    no_single_file = not re.search(r"\b[\w$\"'{}]+\.pkr\.hcl\b", build_line)
    print(f"{'OK' if uses_only else 'FAIL'}: packer build uses -only=...")
    print(f"{'OK' if uses_dir else 'FAIL'}: packer build targets directory '.' (not a single .pkr.hcl file)")
    print(f"{'OK' if no_single_file else 'FAIL'}: packer build line has no '<name>.pkr.hcl' positional arg")
    return uses_only and uses_dir and no_single_file


def test_per_os_only_flag_mapping() -> bool:
    """DEC-019 Q1: ubuntu26 + fedora → proxmox-clone (cloud-image flow);
    windows11 stays on proxmox-iso. The negative assertion `proxmox-iso.fedora`
    NOT present catches accidental reverts of fedora back to ISO.
    """
    if not RUNNER.is_file():
        print("FAIL: per-os only flag check skipped — runner missing")
        return False
    body = RUNNER.read_text()
    ct = code_text(body)
    checks = {
        "ubuntu26 → proxmox-clone.ubuntu26 (DEC-019 cloud-image flow)":  "proxmox-clone.ubuntu26" in ct,
        "fedora → proxmox-clone.fedora (DEC-019 cloud-image flow)":      "proxmox-clone.fedora" in ct,
        "windows11 → proxmox-iso.windows11 (stays on ISO)":              "proxmox-iso.windows11" in ct,
        "fedora NOT pinned to proxmox-iso.fedora (no revert)":           "proxmox-iso.fedora" not in ct,
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def test_ubuntu26_invokes_bootstrap_cloud_template() -> bool:
    """DEC-020 (option b): ubuntu26 build path MUST invoke
    scripts/bootstrap_cloud_template.sh as a precondition. proxmox-clone
    requires the source template tpl-cloud-ubuntu26 to already exist on
    PVE; the bootstrap script is the idempotent one-time-per-cloud-image
    creator. Substring presence with comment-skipping is sufficient — the
    bootstrap script's own shape + shellcheck cleanliness is checked
    separately.
    """
    if not RUNNER.is_file():
        print("FAIL: bootstrap invocation check skipped — runner missing")
        return False
    body = RUNNER.read_text()
    ct = code_text(body)
    refs_bootstrap = bool(re.search(r"bootstrap_cloud_template\.sh\W+ubuntu26", ct))
    print(f"{'OK' if refs_bootstrap else 'FAIL'}: build_template.sh invokes bootstrap_cloud_template.sh ubuntu26")
    return refs_bootstrap


def test_fedora_invokes_bootstrap_cloud_template() -> bool:
    """DEC-020 (option b) + DEC-019 Q4 carry-forward: fedora build path MUST
    invoke scripts/bootstrap_cloud_template.sh fedora as a precondition.
    proxmox-clone.fedora requires tpl-cloud-fedora44 to already exist on PVE;
    the bootstrap script is the idempotent one-time-per-cloud-image creator.
    Per DEC-019 Q2 the fedora arm does NOT pre-bake a cidata seed via
    genisoimage — Packer's additional_iso_files{cd_files=[...]} generates the
    NoCloud seed on-the-fly, so only windows11 keeps the genisoimage pre-bake.
    """
    if not RUNNER.is_file():
        print("FAIL: fedora bootstrap invocation check skipped — runner missing")
        return False
    body = RUNNER.read_text()
    ct = code_text(body)
    refs_bootstrap = bool(re.search(r"bootstrap_cloud_template\.sh\W+fedora", ct))
    print(f"{'OK' if refs_bootstrap else 'FAIL'}: build_template.sh invokes bootstrap_cloud_template.sh fedora")
    return refs_bootstrap


def test_bootstrap_script_exists_and_shape() -> bool:
    """scripts/bootstrap_cloud_template.sh: shebang, set -euo pipefail in
    first 10 lines (per mem-1777856290-3a6f), executable bit, and the
    qm create / importdisk / qm template chain from research.md:55-68 with
    an idempotent qm-status guard so re-runs are safe.
    """
    if not BOOTSTRAP.is_file():
        print("FAIL: scripts/bootstrap_cloud_template.sh missing")
        return False
    body = BOOTSTRAP.read_text()
    lines = body.splitlines()
    shebang_ok = lines[0].strip() == "#!/usr/bin/env bash"
    set_ok = any("set -euo pipefail" in ln for ln in lines[:10])
    mode_ok = bool(BOOTSTRAP.stat().st_mode & stat.S_IXUSR)
    ct = code_text(body)
    checks = {
        "shebang #!/usr/bin/env bash":                shebang_ok,
        "set -euo pipefail in first 10 lines":        set_ok,
        "executable bit set":                         mode_ok,
        "references 'qm create' for source VM":       "qm create" in ct,
        "references 'qm importdisk' for cloud image": "qm importdisk" in ct,
        "references 'qm template' to flag golden":    "qm template" in ct,
        "idempotent guard via 'qm status'":           "qm status" in ct,
        "tpl-cloud-ubuntu26 source name":             "tpl-cloud-ubuntu26" in ct,
        "tpl-cloud-fedora44 source name":             "tpl-cloud-fedora44" in ct,
        "PROXMOX_HOST referenced for ssh target":     "PROXMOX_HOST" in ct,
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def test_bootstrap_guard_verifies_name_template_scsi0() -> bool:
    """Regression for VMID-collision bug (mem-1777893372-f3b2). The
    idempotency guard at scripts/bootstrap_cloud_template.sh must verify the
    existing VM is *actually* TPL_NAME (with template:1 and scsi0:) — not
    just that some VM exists at SRC_VMID. A bare 'qm status $SRC_VMID' check
    silently skips bootstrap when VMIDs 9000/9001 are occupied by pre-existing
    manual cloud templates with different names, after which Packer's
    proxmox-clone fails because clone_vm is resolved by NAME.

    Mutate the guard back to the weak form (drop the qm config / name /
    template / scsi0 verification) and this test must fail.
    """
    if not BOOTSTRAP.is_file():
        print("FAIL: guard regression check skipped — script missing")
        return False
    body = BOOTSTRAP.read_text()
    ct = code_text(body)
    checks = {
        "guard reads 'qm config' (not just qm status)":     "qm config" in ct,
        "guard parses '^name:' line from qm config":        "^name:" in ct,
        "guard checks '^template:' line":                   "^template:" in ct,
        "guard checks '^scsi0:' line":                      "^scsi0:" in ct,
        "guard compares existing name to $TPL_NAME":        bool(
            re.search(r"==\s*\"?\$\{?TPL_NAME\}?\"?", ct)
        ),
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def test_bootstrap_scsi0_uses_parsed_imported_disk() -> bool:
    """Regression for disk-slot collision bug (mem-1777897177-6c8f). The
    'qm set --scsi0 ...' line in bootstrap_cloud_template.sh must reference
    a captured/parsed disk name from 'qm importdisk' stdout, NOT the literal
    'vm-${SRC_VMID}-disk-0'. Step 3's '--efidisk0 local-lvm:0,...' allocates
    vm-${SRC_VMID}-disk-0, so importdisk lands on disk-1; hardcoding disk-0
    attaches the EFI disk to scsi0 and 'qm template' then leaves efidisk0's
    reference dangling, breaking proxmox-clone with 'no such logical volume
    pve/vm-NNNN-disk-0'.

    Mutate L111 back to 'qm set $SRC_VMID --scsi0 local-lvm:vm-${SRC_VMID}-disk-0,...'
    and this test must fail.
    """
    if not BOOTSTRAP.is_file():
        print("FAIL: scsi0 parsed-disk regression check skipped — script missing")
        return False
    body = BOOTSTRAP.read_text()
    ct = code_text(body)
    # The fix captures the imported disk name from 'qm importdisk' output and
    # references it through a shell variable on the scsi0 attach.
    captures_import = bool(
        re.search(r"=\s*\"\$\(\s*ssh_pve\s+\"qm\s+importdisk\b", ct)
    )
    parses_disk_name = bool(re.search(r"unused[^']*local-lvm[^']*vm-", ct))
    # The scsi0 attach must NOT contain the literal 'vm-${SRC_VMID}-disk-0' or
    # 'vm-9000-disk-0' / 'vm-9001-disk-0' — that was the bug.
    scsi0_lines = [ln for ln in code_lines(body) if re.search(r"--scsi0\b", ln)]
    has_hardcoded_disk0 = any(
        re.search(r"local-lvm:vm-(\$\{?SRC_VMID\}?|9000|9001)-disk-0\b", ln)
        for ln in scsi0_lines
    )
    references_imported_var = any(
        re.search(r"local-lvm:[\"']?\$\{?imported_disk\}?", ln) for ln in scsi0_lines
    )
    checks = {
        "captures 'qm importdisk' stdout into a shell variable":  captures_import,
        "parses imported disk name (unused*:local-lvm:vm-*)":     parses_disk_name,
        "scsi0 attach does NOT hardcode 'vm-...-disk-0' literal": not has_hardcoded_disk0,
        "scsi0 attach references the parsed disk variable":       references_imported_var,
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def test_bootstrap_does_not_attach_ide2_cloudinit() -> bool:
    """Regression for dual-cidata SSH timeout (mem-1777927418-a0b3, DEBUG.md
    task-1777857784-fb79). The bootstrap script MUST NOT pre-bake an ide2
    cloud-init drive on the source template via 'qm set --ide2 local-lvm:cloudinit'.

    Why: packer's proxmox-clone attaches its own NoCloud seed via
    additional_iso_files (ide0, label=cidata). If the source template ALSO has
    an ide2 cloud-init drive (Proxmox auto-generated, label=cidata, no
    cipassword), the clone inherits both. cloud-init's NoCloud datasource
    resolves /dev/disk/by-label/cidata to one of them; if it picks the empty
    Proxmox seed, our user-data (ssh_pwauth:true, user unlock) never runs,
    sshd keeps PasswordAuthentication=no, and packer's SSH hangs 30m.

    The bpg/proxmox provider's initialization{} block on Tofu clones generates
    its own cidata drive too, so downstream consumers don't need ide2 baked
    into the template either.

    Mutate the script to re-add 'qm set $SRC_VMID --ide2 local-lvm:cloudinit'
    and this test must fail.
    """
    if not BOOTSTRAP.is_file():
        print("FAIL: ide2-cloudinit regression check skipped — script missing")
        return False
    body = BOOTSTRAP.read_text()
    ct = code_text(body)
    # Match an ide2 attach where the value resolves to 'cloudinit', allowing
    # quoting / interpolation variants (--ide2 local-lvm:cloudinit, --ide2
    # "local-lvm:cloudinit", etc.) but ignoring any '--delete ide2' cleanup
    # line that mentions 'ide2' without attaching.
    has_ide2_cloudinit_attach = bool(
        re.search(r"--ide2[\s=]+[\"']?[^\"'\s]*:cloudinit\b", ct)
    )
    print(
        f"{'OK' if not has_ide2_cloudinit_attach else 'FAIL'}: "
        "bootstrap does NOT attach '--ide2 <storage>:cloudinit' (dual-cidata SSH-timeout regression)"
    )
    return not has_ide2_cloudinit_attach


def test_bootstrap_shellcheck() -> bool:
    if not shutil.which("shellcheck"):
        print("OK (skip): shellcheck not installed")
        return True
    if not BOOTSTRAP.is_file():
        print("FAIL: bootstrap shellcheck skipped — script missing")
        return False
    r = subprocess.run(["shellcheck", str(BOOTSTRAP)], capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"{'OK' if ok else 'FAIL'}: bootstrap shellcheck ({r.stdout.strip() or 'clean'})")
    return ok


def test_bootstrap_importdisk_parses_pve8_and_pve9_formats() -> bool:
    """Regression for PVE 9 importdisk parser bug (mem-1777899105-4193).
    'qm importdisk' output format changed between PVE 8 and PVE 9:

      PVE 9 (Trixie): "unused0: successfully imported disk 'local-lvm:vm-NNNN-disk-X'"
                      (unusedN: OUTSIDE quotes; only the volid is quoted)
      PVE 8 legacy:   "Successfully imported disk as 'unused0:local-lvm:vm-NNNN-disk-X'"
                      (whole unusedN:local-lvm:... INSIDE single quotes)

    The original single sed pattern only matched the PVE 8 form, so the script
    aborted on PVE 9 with 'could not parse imported disk name' (DEBUG.md repro).
    The fix uses two -e patterns; this test extracts the actual sed pipeline
    from bootstrap_cloud_template.sh and runs it against verbatim PVE 9 input,
    PVE 8 legacy input, a multi-line noisy stream, and an adversarial mid-line
    'unused0' lookalike that must NOT yield a false positive.

    Mutate L120-124 back to the single sed pattern (drop the PVE 9 anchored
    form) and this test must fail on the PVE 9 case.
    """
    if not BOOTSTRAP.is_file():
        print("FAIL: importdisk parser regression check skipped — script missing")
        return False
    body = BOOTSTRAP.read_text()
    # Locate the sed pipeline that captures imported_disk from qm importdisk
    # output. Pull all '-e "..."' arguments verbatim and replay them with
    # /bin/sh so the test exercises exactly the live command shape.
    block = re.search(
        r"imported_disk=.*?\| tail -n1\)\"",
        body,
        re.DOTALL,
    )
    if block is None:
        print("FAIL: could not locate imported_disk sed pipeline in bootstrap")
        return False
    sed_args = re.findall(r'-e\s+"([^"]+)"', block.group(0))
    if not sed_args:
        print("FAIL: no '-e <pattern>' args found in imported_disk sed block")
        return False
    # Reconstruct the sed invocation: sed -n -e "..." -e "..." | tail -n1
    sed_cmd = ["sed", "-n"]
    for pat in sed_args:
        sed_cmd.extend(["-e", pat])

    cases = [
        (
            "PVE 9 verbatim DEBUG.md line",
            "unused0: successfully imported disk 'local-lvm:vm-9001-disk-1'\n",
            "vm-9001-disk-1",
        ),
        (
            "PVE 8 legacy form",
            "Successfully imported disk as 'unused0:local-lvm:vm-9001-disk-1'\n",
            "vm-9001-disk-1",
        ),
        (
            "multi-line noisy stream with PVE 9 result buried at end",
            (
                "transferred: 1.0 GiB of 5.0 GiB ( 20.00%)\n"
                "transferred: 5.0 GiB of 5.0 GiB (100.00%)\n"
                "unused0: successfully imported disk 'local-lvm:vm-9001-disk-1'\n"
            ),
            "vm-9001-disk-1",
        ),
        (
            "adversarial mid-line 'unused0' lookalike (must NOT match)",
            "some progress: see unused0 below for status\n",
            "",
        ),
    ]
    all_ok = True
    for label, stdin, expected in cases:
        sed_run = subprocess.run(sed_cmd, input=stdin, capture_output=True, text=True)
        tail_run = subprocess.run(
            ["tail", "-n1"], input=sed_run.stdout, capture_output=True, text=True
        )
        got = tail_run.stdout.strip()
        ok = got == expected
        all_ok = all_ok and ok
        print(f"{'OK' if ok else 'FAIL'}: {label} → got={got!r} expected={expected!r}")
    return all_ok


def main() -> int:
    results = [
        test_exists_and_executable(),
        test_shebang_and_set(),
        test_shellcheck(),
        test_shfmt_format_clean(),
        test_arg_validation_and_envvar_preflight(),
        test_windows11_specific_steps(),
        test_packer_init_then_build_force(),
        test_packer_build_uses_directory_form(),
        test_per_os_only_flag_mapping(),
        test_ubuntu26_invokes_bootstrap_cloud_template(),
        test_fedora_invokes_bootstrap_cloud_template(),
        test_bootstrap_script_exists_and_shape(),
        test_bootstrap_guard_verifies_name_template_scsi0(),
        test_bootstrap_scsi0_uses_parsed_imported_disk(),
        test_bootstrap_does_not_attach_ide2_cloudinit(),
        test_bootstrap_shellcheck(),
        test_bootstrap_importdisk_parses_pve8_and_pve9_formats(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
