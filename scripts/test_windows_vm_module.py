"""Adversarial smoke test for the OpenTofu windows_vm module under
`tofu/modules/windows_vm/`.

Mirrors the convention in `scripts/test_tofu_linux_vm_module.py`:
text-based HCL assertions, stdlib-only, plain `if __name__ == "__main__"`
runner with PASS/FAIL counts. The module ships a four-resource pipeline
(local_file -> null_resource genisoimage -> proxmox_virtual_environment_file
-> proxmox_virtual_environment_vm) with OVMF/UEFI + TPM 2.0.

Per DEC-007: bpg/proxmox v0.104.0 caps `cdrom` blocks at MaxItems=1 on
the legacy `proxmox_virtual_environment_vm` resource. The spec's three
ISO requirement is met by:

  - 1 `cdrom` block for the Windows install ISO (boot media)
  - `kvm_arguments` passing two extra `-drive ...,media=cdrom` lines
    to qemu for the autounattend ISO and virtio-win.iso

This file asserts that semantic shape (1 cdrom + kvm_arguments
referencing both extra ISOs).

Two adversarial mutations are designed for this test (per the Step 2
plan in `.agents/scratchpad/implementation/dev-vms-design/progress.md`,
adjusted for DEC-007):

1. Drop the `tpm_state { ... }` block -> trips
   `test_module_main_tpm_state_v2`.
2. Drop `virtio-win.iso` from `kvm_arguments` -> trips
   `test_module_main_extra_isos_via_kvm_arguments` with a precise
   message naming the missing ISO reference.
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOFU_DIR = os.environ.get("TOFU_DIR", os.path.join(REPO_ROOT, "tofu"))
MODULE_DIR = os.environ.get(
    "MODULE_DIR", os.path.join(TOFU_DIR, "modules", "windows_vm")
)
MODULE_VERSIONS_PATH = os.environ.get(
    "MODULE_VERSIONS_PATH", os.path.join(MODULE_DIR, "versions.tf")
)
MODULE_VARIABLES_PATH = os.environ.get(
    "MODULE_VARIABLES_PATH", os.path.join(MODULE_DIR, "variables.tf")
)
MODULE_MAIN_PATH = os.environ.get(
    "MODULE_MAIN_PATH", os.path.join(MODULE_DIR, "main.tf")
)
MODULE_OUTPUTS_PATH = os.environ.get(
    "MODULE_OUTPUTS_PATH", os.path.join(MODULE_DIR, "outputs.tf")
)
TEMPLATE_PATH = os.environ.get(
    "TEMPLATE_PATH",
    os.path.join(MODULE_DIR, "templates", "autounattend.xml.tftpl"),
)

REQUIRED_MODULE_VARIABLES = (
    "name",
    "vmid",
    "iso_file",
    "memory",
    "cores",
    "disk_gb",
    "bridge",
    "template_node",
    "default_user",
    "default_password",
    "ssh_authorized_keys",
    "tags",
)

REQUIRED_RESOURCES = (
    ("local_file", "autounattend XML rendered from templatefile()"),
    ("null_resource", "genisoimage local-exec wrapper"),
    (
        "proxmox_virtual_environment_file",
        "uploads the per-VM autounattend ISO to local:iso/",
    ),
    (
        "proxmox_virtual_environment_vm",
        "the Windows VM itself (bios=ovmf + UEFI + TPM 2.0 + 3 cdroms)",
    ),
)

REQUIRED_TEMPLATE_INTERPOLATIONS = (
    "${name}",
    "${default_user}",
    "${default_password}",
    "${ssh_authorized_keys}",
)


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_module_dir_exists():
    if os.path.isdir(MODULE_DIR):
        print(f"OK: windows_vm module directory exists at '{MODULE_DIR}'.")
        return True
    print(f"FAIL: windows_vm module directory '{MODULE_DIR}' is missing.")
    return False


def test_module_versions_pins_bpg_proxmox():
    text = read_text(MODULE_VERSIONS_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_VERSIONS_PATH}' is missing.")
        return False
    if not re.search(r'source\s*=\s*"bpg/proxmox"', text):
        print(
            f"FAIL: '{MODULE_VERSIONS_PATH}' must pin "
            f"`source = \"bpg/proxmox\"` "
            f"(provider source identifier; matches linux_vm module)."
        )
        return False
    if not re.search(r'version\s*=\s*"~>\s*0\.104\.0"', text):
        print(
            f"FAIL: '{MODULE_VERSIONS_PATH}' must pin "
            f"`version = \"~> 0.104.0\"` "
            f"(matches the linux_vm module + root pin)."
        )
        return False
    print(
        f"OK: '{MODULE_VERSIONS_PATH}' pins bpg/proxmox ~> 0.104.0."
    )
    return True


def test_module_variables_declares_required_inputs():
    text = read_text(MODULE_VARIABLES_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_VARIABLES_PATH}' is missing.")
        return False
    missing = []
    for name in REQUIRED_MODULE_VARIABLES:
        if not re.search(
            r'variable\s+"' + re.escape(name) + r'"\s*\{', text
        ):
            missing.append(name)
    if missing:
        print(
            f"FAIL: '{MODULE_VARIABLES_PATH}' missing variable "
            f"declarations: {', '.join(missing)} "
            f"(module must accept "
            f"{', '.join(REQUIRED_MODULE_VARIABLES)})."
        )
        return False
    # disk_gb must be a number type (per mem-1777494071-85b5: bpg's
    # disk.size attribute is a Number on v0.104.0; Builder must NOT
    # smuggle the broken string-with-G form through this module).
    block = re.search(
        r'variable\s+"disk_gb"\s*\{(?P<body>[\s\S]*?)\n\}', text
    )
    if not block or not re.search(r"type\s*=\s*number\b", block.group("body")):
        print(
            f"FAIL: '{MODULE_VARIABLES_PATH}' variable \"disk_gb\" must "
            f"declare `type = number` "
            f"(disk.size is a Number on bpg/proxmox v0.104.0; the "
            f"string-with-G form fails plan)."
        )
        return False
    print(
        f"OK: '{MODULE_VARIABLES_PATH}' declares all "
        f"{len(REQUIRED_MODULE_VARIABLES)} required module inputs "
        f"(disk_gb typed as number)."
    )
    return True


def test_module_main_declares_pipeline_resources():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    missing = []
    for resource_type, purpose in REQUIRED_RESOURCES:
        if not re.search(
            r'resource\s+"' + re.escape(resource_type) + r'"\s+"[^"]+"\s*\{',
            text,
        ):
            missing.append(f"{resource_type} ({purpose})")
    if missing:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' missing required resource "
            f"declarations: {'; '.join(missing)}."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' declares the four-resource pipeline: "
        f"{', '.join(r for r, _ in REQUIRED_RESOURCES)}."
    )
    return True


def test_module_main_local_file_renders_template():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    block = re.search(
        r'resource\s+"local_file"\s+"[^"]+"\s*\{(?P<body>[\s\S]*?)\n\}',
        text,
    )
    if not block:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare "
            f"resource \"local_file\" \"...\" {{...}} "
            f"(renders templates/autounattend.xml.tftpl via templatefile())."
        )
        return False
    body = block.group("body")
    if not re.search(
        r"templatefile\s*\(\s*\"\$\{path\.module\}/templates/autounattend\.xml\.tftpl\"",
        body,
    ):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' local_file must call "
            f"templatefile(\"${{path.module}}/templates/autounattend.xml.tftpl\", ...) "
            f"(renders the per-VM XML; path.module-relative path keeps "
            f"the module self-contained)."
        )
        return False
    for var in ("name", "default_user", "default_password", "ssh_authorized_keys"):
        if not re.search(r"var\." + re.escape(var) + r"\b", body):
            print(
                f"FAIL: '{MODULE_MAIN_PATH}' local_file templatefile() "
                f"call must reference var.{var} "
                f"(the template needs all four interpolations to render "
                f"a valid autounattend.xml)."
            )
            return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' local_file renders "
        f"templates/autounattend.xml.tftpl with name + default_user + "
        f"default_password + ssh_authorized_keys."
    )
    return True


def test_module_main_null_resource_runs_genisoimage():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    block = re.search(
        r'resource\s+"null_resource"\s+"[^"]+"\s*\{(?P<body>[\s\S]*?)\n\}',
        text,
    )
    if not block:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare "
            f"resource \"null_resource\" \"...\" "
            f"(local-exec wrapper around genisoimage)."
        )
        return False
    body = block.group("body")
    if not re.search(r"local-exec", body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' null_resource must contain a "
            f"`provisioner \"local-exec\" {{...}}` block."
        )
        return False
    if not re.search(r"\bgenisoimage\b", body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' null_resource local-exec "
            f"command must invoke genisoimage to build the per-VM "
            f"autounattend ISO."
        )
        return False
    if not re.search(r"\btriggers\b", body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' null_resource must declare a "
            f"`triggers = {{ ... }}` map keyed on the rendered XML's "
            f"hash so the ISO rebuilds whenever the rendered XML changes."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' null_resource runs genisoimage with "
        f"a triggers map for change-detection."
    )
    return True


def test_module_main_vm_uses_ovmf_uefi():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    if not re.search(r'bios\s*=\s*"ovmf"', text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must set "
            f"`bios = \"ovmf\"` on the VM resource "
            f"(Win 11 requires UEFI; OVMF is the QEMU UEFI firmware)."
        )
        return False
    if not re.search(r"efi_disk\s*\{", text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare "
            f"`efi_disk {{ ... }}` block "
            f"(persists UEFI variables; required when bios = \"ovmf\")."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' VM uses bios=\"ovmf\" with "
        f"efi_disk block."
    )
    return True


def test_module_main_tpm_state_v2():
    """Adversarial target: drop this block -> this assertion trips with
    a precise 'tpm_state with version = "v2.0" missing' message."""
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    block = re.search(
        r"tpm_state\s*\{(?P<body>[^{}]*)\}", text
    )
    if not block:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' tpm_state with version = \"v2.0\" "
            f"missing — Win 11 requires a vTPM 2.0 device."
        )
        return False
    body = block.group("body")
    if not re.search(r'version\s*=\s*"v2\.0"', body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' tpm_state with version = \"v2.0\" "
            f"missing — block exists but version != \"v2.0\" "
            f"(Win 11 mandates TPM 2.0)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' VM declares "
        f"tpm_state {{ version = \"v2.0\" }}."
    )
    return True


def _count_cdrom_blocks(text):
    """Count top-level cdrom { ... } blocks in the VM resource body.

    Uses a brace-depth scanner so nested constructs (e.g. interpolation
    ${...} that contain literal braces) don't inflate the count.
    """
    count = 0
    pos = 0
    while True:
        match = re.search(r"\bcdrom\s*\{", text[pos:])
        if match is None:
            break
        i = pos + match.end()
        depth = 1
        while i < len(text) and depth > 0:
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        count += 1
        pos = i
    return count


def test_module_main_single_cdrom_for_install_iso():
    """The bpg/proxmox v0.104.0 legacy resource caps `cdrom` blocks at
    MaxItems=1. The single block carries the Windows install ISO; the
    other two ISOs land via `kvm_arguments` (see
    test_module_main_extra_isos_via_kvm_arguments). Per DEC-007."""
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    found = _count_cdrom_blocks(text)
    if found != 1:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' expected exactly 1 cdrom "
            f"block, found {found} "
            f"(bpg/proxmox v0.104.0 enforces MaxItems=1 on cdrom; "
            f"the other two ISOs must land via kvm_arguments)."
        )
        return False
    if not re.search(r"local:iso/\$\{var\.iso_file\}", text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' missing install-ISO cdrom "
            f"reference `local:iso/${{var.iso_file}}` "
            f"(the single cdrom block must carry the Windows install "
            f"media so the VM can boot from it)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' has exactly 1 cdrom block "
        f"(install ISO via local:iso/${{var.iso_file}})."
    )
    return True


def _extract_kvm_arguments_value(text):
    """Return the raw RHS of `kvm_arguments = ...`.

    The RHS may span multiple lines (e.g. a `join(" ", [ ... ])` call
    or a heredoc). Extract from the `=` to the end of the balanced
    expression. Returns None if the assignment is absent.
    """
    head = re.search(r"\bkvm_arguments\s*=\s*", text)
    if head is None:
        return None
    # Walk forward consuming a balanced expression. Track parens,
    # brackets, and braces; bail when depth is zero and we hit a newline
    # OR a top-level closing brace (the surrounding resource block).
    i = head.end()
    paren = bracket = brace = 0
    in_str = None  # None | '"' | "'"
    start = i
    end = None
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\" and i + 1 < len(text):
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ('"', "'"):
            in_str = c
            i += 1
            continue
        if c == "(":
            paren += 1
        elif c == ")":
            paren -= 1
        elif c == "[":
            bracket += 1
        elif c == "]":
            bracket -= 1
        elif c == "{":
            brace += 1
        elif c == "}":
            if brace == 0:
                # Top-level closing brace → end of the resource body.
                end = i
                break
            brace -= 1
        elif c == "\n" and paren == 0 and bracket == 0 and brace == 0:
            end = i
            break
        i += 1
    if end is None:
        end = len(text)
    return text[start:end]


def test_module_main_extra_isos_via_kvm_arguments():
    """Adversarial target: drop virtio-win.iso (or autounattend.iso)
    from `kvm_arguments` -> this test trips with a precise message
    naming the missing ISO. Per DEC-007.

    Substring checks scope to the kvm_arguments RHS only so a comment
    elsewhere in the file mentioning `virtio-win.iso` or
    `autounattend.iso` cannot mask a real omission (mem-1777478162-68e8).
    """
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    rhs = _extract_kvm_arguments_value(text)
    if rhs is None:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' missing `kvm_arguments = ...` "
            f"on the VM resource (per DEC-007, the autounattend ISO + "
            f"virtio-win.iso must be attached via qemu's -drive flag "
            f"because bpg/proxmox v0.104.0 caps cdrom blocks at 1)."
        )
        return False
    if not re.search(r"\$\{var\.name\}-autounattend\.iso", rhs):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' kvm_arguments value must "
            f"reference the autounattend ISO via the "
            f"`${{var.name}}-autounattend.iso` filename "
            f"(Windows Setup auto-discovers autounattend.xml from any "
            f"attached media; without this -drive, install falls back "
            f"to interactive)."
        )
        return False
    if not re.search(r"\bvirtio-win\.iso\b", rhs):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' kvm_arguments value must "
            f"reference `virtio-win.iso` (provides paravirtualised "
            f"drivers + the qemu-guest-agent MSI consumed by "
            f"FirstLogonCommands)."
        )
        return False
    drive_count = len(re.findall(r"-drive\s+file=", rhs))
    if drive_count < 2:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' kvm_arguments must include at "
            f"least two `-drive file=...` flags (one per extra ISO); "
            f"found {drive_count}."
        )
        return False
    if len(re.findall(r"media=cdrom", rhs)) < 2:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' kvm_arguments -drive flags "
            f"must include `media=cdrom` so qemu mounts the ISOs as "
            f"CD-ROM drives (not raw disks)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' attaches autounattend.iso + "
        f"virtio-win.iso via kvm_arguments (-drive ...,media=cdrom)."
    )
    return True


def test_module_main_disk_uses_number_size_and_discard_ssd():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    open_match = re.search(r"^\s*disk\s*\{\s*$", text, flags=re.MULTILINE)
    if not open_match:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare a disk {{...}} "
            f"block on its own line (size driven by var.disk_gb)."
        )
        return False
    after = text[open_match.end():]
    close_match = re.search(r"^\s*\}\s*$", after, flags=re.MULTILINE)
    if not close_match:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' disk block has no matching "
            f"closing brace on its own line."
        )
        return False
    body = after[: close_match.start()]
    # Must use the Number form `size = var.disk_gb`. The string-with-G
    # form (e.g. "${var.disk_gb}G") passes validate but fails plan on
    # bpg/proxmox v0.104.0 — see mem-1777494071-85b5.
    if not re.search(r"size\s*=\s*var\.disk_gb\b", body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' disk block must set "
            f"`size = var.disk_gb` (Number form). "
            f"On bpg/proxmox v0.104.0, the string form `\"${{var.disk_gb}}G\"` "
            f"passes validate but fails plan with "
            f"\"Inappropriate value for attribute 'size': a number is required\"."
        )
        return False
    if re.search(r'size\s*=\s*"\$\{var\.disk_gb\}G"', body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' disk block uses the broken "
            f"string-with-G form. Replace with `size = var.disk_gb`."
        )
        return False
    if not re.search(r'discard\s*=\s*"on"', body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' disk block must set "
            f"`discard = \"on\"` (returns freed blocks to the LVM-thin pool)."
        )
        return False
    if not re.search(r"ssd\s*=\s*true\b", body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' disk block must set "
            f"`ssd = true` "
            f"(advertises the disk as an SSD to the guest; Windows uses "
            f"this hint to disable defrag and enable trim)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' disk block uses size=var.disk_gb "
        f"(Number form), discard=\"on\", ssd=true."
    )
    return True


def test_module_main_agent_enabled():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    if not re.search(r"agent\s*\{[^{}]*enabled\s*=\s*true", text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare "
            f"`agent {{ enabled = true }}` "
            f"(qemu-guest-agent ships via virtio-win drivers; lets Tofu "
            f"read back the VM's IP after first boot)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' VM declares agent {{ enabled = true }}."
    )
    return True


def test_module_outputs_file_exposes_expected_outputs():
    text = read_text(MODULE_OUTPUTS_PATH)
    if text is None:
        print(
            f"FAIL: '{MODULE_OUTPUTS_PATH}' is missing "
            f"(module must declare outputs.tf — name, vmid, node_name, "
            f"ipv4_address are consumed by the root ansible_inventory output)."
        )
        return False
    expected_outputs = ("name", "vmid", "node_name", "ipv4_address")
    missing = []
    for out in expected_outputs:
        if not re.search(
            r'output\s+"' + re.escape(out) + r'"\s*\{', text
        ):
            missing.append(out)
    if missing:
        print(
            f"FAIL: '{MODULE_OUTPUTS_PATH}' missing output(s): "
            f"{', '.join(missing)} "
            f"(must mirror linux_vm/outputs.tf shape: {expected_outputs})."
        )
        return False
    if not re.search(
        r"try\s*\(\s*[^,]+\.ipv4_addresses\[1\]\[0\]\s*,\s*null\s*\)", text
    ):
        print(
            f"FAIL: '{MODULE_OUTPUTS_PATH}' ipv4_address output must "
            f"wrap `<vm>.ipv4_addresses[1][0]` in try(..., null) so "
            f"plan stays valid before the qemu-guest-agent reports a lease."
        )
        return False
    print(
        f"OK: '{MODULE_OUTPUTS_PATH}' declares "
        f"{', '.join(expected_outputs)} (ipv4_address wrapped in try)."
    )
    return True


def test_template_exists_and_has_required_interpolations():
    text = read_text(TEMPLATE_PATH)
    if text is None:
        print(
            f"FAIL: '{TEMPLATE_PATH}' is missing "
            f"(autounattend.xml.tftpl is required for unattended install)."
        )
        return False
    missing = [
        token for token in REQUIRED_TEMPLATE_INTERPOLATIONS
        if token not in text
    ]
    if missing:
        print(
            f"FAIL: '{TEMPLATE_PATH}' missing required interpolation(s): "
            f"{', '.join(missing)} "
            f"(template must reference all four module inputs literally)."
        )
        return False
    # Sanity-check the template is XML-shaped (root <unattend> element)
    # so a placeholder file doesn't slip through.
    if "<unattend" not in text:
        print(
            f"FAIL: '{TEMPLATE_PATH}' is not XML-shaped "
            f"(missing `<unattend` root element). "
            f"Windows Setup needs a valid autounattend.xml schema."
        )
        return False
    print(
        f"OK: '{TEMPLATE_PATH}' exists, is XML-shaped, and references "
        f"all four required interpolations."
    )
    return True


def main():
    checks = [
        ("windows_vm module directory exists", test_module_dir_exists),
        ("module versions.tf pins bpg/proxmox ~> 0.104.0",
         test_module_versions_pins_bpg_proxmox),
        ("module variables.tf declares all required inputs (disk_gb=number)",
         test_module_variables_declares_required_inputs),
        ("module main.tf declares the four-resource pipeline",
         test_module_main_declares_pipeline_resources),
        ("module main.tf local_file renders autounattend.xml.tftpl",
         test_module_main_local_file_renders_template),
        ("module main.tf null_resource runs genisoimage with triggers",
         test_module_main_null_resource_runs_genisoimage),
        ("module main.tf VM uses bios=\"ovmf\" with efi_disk",
         test_module_main_vm_uses_ovmf_uefi),
        ("module main.tf VM declares tpm_state version=\"v2.0\"",
         test_module_main_tpm_state_v2),
        ("module main.tf VM has exactly 1 cdrom block (install ISO)",
         test_module_main_single_cdrom_for_install_iso),
        ("module main.tf attaches autounattend + virtio-win ISOs via "
         "kvm_arguments (per DEC-007)",
         test_module_main_extra_isos_via_kvm_arguments),
        ("module main.tf disk uses Number size + discard=on + ssd=true",
         test_module_main_disk_uses_number_size_and_discard_ssd),
        ("module main.tf VM declares agent { enabled = true }",
         test_module_main_agent_enabled),
        ("module outputs.tf exposes name/vmid/node_name/ipv4_address",
         test_module_outputs_file_exposes_expected_outputs),
        ("templates/autounattend.xml.tftpl exists with all 4 interpolations",
         test_template_exists_and_has_required_interpolations),
    ]
    results = [(label, fn()) for label, fn in checks]
    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    print(
        f"SUCCESS: All {len(results)} tofu windows_vm module checks passed."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
