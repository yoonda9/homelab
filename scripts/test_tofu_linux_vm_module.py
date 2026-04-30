"""Adversarial smoke test for the OpenTofu linux_vm module under
`tofu/modules/linux_vm/`.

Renamed and extended from `scripts/test_tofu_vm_module.py`. Asserts the
new dev-VMs design: `disk_gb` (required), `static_ip`/`gateway` nullable
pair with a precondition, `default_user`/`default_password`/
`ssh_authorized_keys` plumbed to `initialization.user_account`, and a
cloud-init `user_data` snippet that drops a `sudoers.d` entry granting
passwordless sudo so Ansible's `become: true` works without prompts.

Intentionally text-based so we don't add an HCL parser dependency for a
focused module check.
"""

import os
import re
import sys

TOFU_DIR = os.environ.get("TOFU_DIR", "tofu")
MODULE_DIR = os.environ.get(
    "MODULE_DIR", os.path.join(TOFU_DIR, "modules", "linux_vm")
)
MODULE_MAIN_PATH = os.environ.get(
    "MODULE_MAIN_PATH", os.path.join(MODULE_DIR, "main.tf")
)
MODULE_VARIABLES_PATH = os.environ.get(
    "MODULE_VARIABLES_PATH", os.path.join(MODULE_DIR, "variables.tf")
)
MODULE_OUTPUTS_PATH = os.environ.get(
    "MODULE_OUTPUTS_PATH", os.path.join(MODULE_DIR, "outputs.tf")
)
ROOT_MAIN_PATH = os.environ.get(
    "ROOT_MAIN_PATH", os.path.join(TOFU_DIR, "main.tf")
)

EXPECTED_RESOURCE_TYPE = "proxmox_virtual_environment_vm"
REQUIRED_MODULE_VARIABLES = (
    "name",
    "vmid",
    "clone_from",
    "memory",
    "cores",
    "bridge",
    "template_node",
    "disk_gb",
    "static_ip",
    "gateway",
    "default_user",
    "default_password",
    "ssh_authorized_keys",
)
NULLABLE_MODULE_VARIABLES = ("static_ip", "gateway")
# Ubuntu 26 cloud-image template vmid from
# ansible/group_vars/all.yml (pve_cloud_images entry "ubuntu-26.04-cloud").
UBUNTU_26_TEMPLATE_VMID = 9001
MODULE_SOURCE_PATH = "./modules/linux_vm"
SUDOERS_NOPASSWD_SNIPPET = "%sudo ALL=(ALL) NOPASSWD:ALL"


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_module_dir_exists():
    if os.path.isdir(MODULE_DIR):
        print(f"OK: linux_vm module directory exists at '{MODULE_DIR}'.")
        return True
    print(f"FAIL: linux_vm module directory '{MODULE_DIR}' is missing.")
    return False


def test_module_main_declares_vm_resource():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    if not re.search(
        r'resource\s+"' + re.escape(EXPECTED_RESOURCE_TYPE) + r'"\s+"[^"]+"\s*\{',
        text,
    ):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare "
            f"resource \"{EXPECTED_RESOURCE_TYPE}\" "
            f"(bpg/proxmox VM resource)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' declares "
        f"resource \"{EXPECTED_RESOURCE_TYPE}\"."
    )
    return True


def test_module_main_clones_from_template_var():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    clone_block = re.search(r"clone\s*\{(?P<body>[^}]*)\}", text)
    if not clone_block:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must contain a clone {{...}} "
            f"block to clone the template VM."
        )
        return False
    if not re.search(
        r"vm_id\s*=\s*var\.clone_from", clone_block.group("body")
    ):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' clone block must set "
            f"vm_id = var.clone_from "
            f"(template vmid must come from the module input)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' clone block uses "
        f"vm_id = var.clone_from."
    )
    return True


def test_module_main_wires_ip_config_dhcp_or_static():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    # Static-vs-DHCP branch: the module must reference both var.static_ip
    # (the static path) and the literal "dhcp" (the fallback). The
    # ip_config.ipv4 block exists either way.
    if not re.search(r"ip_config\s*\{[\s\S]*?ipv4\s*\{", text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare "
            f"initialization.ip_config.ipv4 {{...}} block."
        )
        return False
    if not re.search(r"var\.static_ip\b", text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must reference var.static_ip "
            f"in the ip_config branch (static IP path)."
        )
        return False
    if not re.search(r'"dhcp"', text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must reference \"dhcp\" "
            f"as the fallback ipv4 address when static_ip is null."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' wires ip_config.ipv4 with both "
        f"static (var.static_ip) and DHCP fallback."
    )
    return True


def test_module_main_disk_uses_disk_gb_var():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    # Body capture can't naively `[^{}]*` because the size value
    # `"${var.disk_gb}G"` contains literal `{` and `}` from the HCL
    # interpolation. Anchor on the opening `disk {` line and assert the
    # required attributes appear before the matching closing brace
    # (located by scanning for the first un-nested `}` on its own line).
    open_match = re.search(r"^\s*disk\s*\{\s*$", text, flags=re.MULTILINE)
    if not open_match:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare a disk {{...}} "
            f"block to size the boot disk via var.disk_gb."
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
    if not re.search(r'size\s*=\s*"\$\{var\.disk_gb\}G"', body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' disk block must set "
            f"size = \"${{var.disk_gb}}G\" "
            f"(boot disk size driven by the disk_gb input)."
        )
        return False
    if not re.search(r'discard\s*=\s*"on"', body):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' disk block must set "
            f"discard = \"on\" "
            f"(returns freed blocks to the LVM-thin pool on fstrim)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' disk block uses size=\"${{var.disk_gb}}G\" "
        f"and discard=\"on\"."
    )
    return True


def test_module_main_precondition_for_static_ip_pair():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    # Precondition must reference both var.static_ip and var.gateway,
    # so half-configured static IP (one set, one null) trips at plan time.
    pre = re.search(
        r"precondition\s*\{(?P<body>[\s\S]*?)\}", text
    )
    if not pre:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare a precondition "
            f"block guarding static_ip + gateway as a paired (both-or-"
            f"neither) input."
        )
        return False
    body = pre.group("body")
    if not (re.search(r"var\.static_ip\b", body) and
            re.search(r"var\.gateway\b", body)):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' precondition must reference "
            f"both var.static_ip and var.gateway "
            f"(half-configured pair must trip plan)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' precondition guards the "
        f"static_ip/gateway pair."
    )
    return True


def test_module_main_user_account_plumbing():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    block = re.search(
        r"user_account\s*\{(?P<body>[\s\S]*?)\n\s*\}", text
    )
    if not block:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must declare "
            f"initialization.user_account {{...}} block to override "
            f"the cloud-init image's default user."
        )
        return False
    body = block.group("body")
    missing = []
    if not re.search(r"username\s*=\s*var\.default_user\b", body):
        missing.append("username = var.default_user")
    if not re.search(r"password\s*=\s*var\.default_password\b", body):
        missing.append("password = var.default_password")
    if not re.search(r"keys\s*=\s*var\.ssh_authorized_keys\b", body):
        missing.append("keys = var.ssh_authorized_keys")
    if missing:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' user_account block missing "
            f"required plumbing: {', '.join(missing)}."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' user_account plumbs default_user, "
        f"default_password, ssh_authorized_keys."
    )
    return True


def test_module_main_user_data_drops_sudoers_snippet():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    if SUDOERS_NOPASSWD_SNIPPET not in text:
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must embed the cloud-init "
            f"user_data sudoers snippet "
            f"'{SUDOERS_NOPASSWD_SNIPPET}' "
            f"(grants passwordless sudo so Ansible's become: true works)."
        )
        return False
    if not re.search(r"user_data_file_id\s*=", text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must wire "
            f"initialization.user_data_file_id to the rendered "
            f"snippet so the cloud-init user_data takes effect."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' embeds sudoers NOPASSWD snippet "
        f"in cloud-init user_data and wires user_data_file_id."
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
    print(
        f"OK: '{MODULE_VARIABLES_PATH}' declares all "
        f"{len(REQUIRED_MODULE_VARIABLES)} required module inputs."
    )
    return True


def test_module_variables_static_ip_pair_nullable():
    text = read_text(MODULE_VARIABLES_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_VARIABLES_PATH}' is missing.")
        return False
    for name in NULLABLE_MODULE_VARIABLES:
        block = re.search(
            r'variable\s+"' + re.escape(name) + r'"\s*\{(?P<body>[\s\S]*?)\n\}',
            text,
        )
        if not block:
            print(
                f"FAIL: '{MODULE_VARIABLES_PATH}' missing variable "
                f"\"{name}\" declaration (expected nullable with "
                f"default = null)."
            )
            return False
        body = block.group("body")
        if not re.search(r"default\s*=\s*null\b", body):
            print(
                f"FAIL: '{MODULE_VARIABLES_PATH}' variable \"{name}\" "
                f"must default to null so callers can opt out of static "
                f"IP and fall through to DHCP."
            )
            return False
    print(
        f"OK: '{MODULE_VARIABLES_PATH}' declares "
        f"{', '.join(NULLABLE_MODULE_VARIABLES)} with default = null."
    )
    return True


def test_module_outputs_file_exists():
    text = read_text(MODULE_OUTPUTS_PATH)
    if text is None:
        print(
            f"FAIL: '{MODULE_OUTPUTS_PATH}' is missing "
            f"(module must declare outputs.tf, even if minimal)."
        )
        return False
    if not re.search(r'output\s+"[^"]+"\s*\{', text):
        print(
            f"FAIL: '{MODULE_OUTPUTS_PATH}' must declare at least "
            f"one output {{...}} block."
        )
        return False
    print(f"OK: '{MODULE_OUTPUTS_PATH}' declares at least one output.")
    return True


def test_root_main_calls_linux_vm_module_for_ubuntu26():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    module_blocks = re.findall(
        r'module\s+"[^"]+"\s*\{(?P<body>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
        text,
    )
    if not module_blocks:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must contain at least one "
            f"module \"...\" block "
            f"(root config must invoke the linux_vm module)."
        )
        return False
    linux_vm_module_blocks = [
        body for body in module_blocks
        if re.search(
            r'source\s*=\s*"' + re.escape(MODULE_SOURCE_PATH) + r'"', body
        )
    ]
    if not linux_vm_module_blocks:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' has module blocks but none "
            f"set source = \"{MODULE_SOURCE_PATH}\" "
            f"(root config must invoke the linux_vm module from "
            f"{MODULE_SOURCE_PATH})."
        )
        return False
    if not any(
        re.search(
            r"clone_from\s*=\s*" + str(UBUNTU_26_TEMPLATE_VMID) + r"\b",
            body,
        )
        for body in linux_vm_module_blocks
    ):
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must invoke the linux_vm module "
            f"with clone_from = {UBUNTU_26_TEMPLATE_VMID} "
            f"(Ubuntu 26 cloud-image template vmid from "
            f"ansible/group_vars/all.yml)."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' invokes the linux_vm module "
        f"(source={MODULE_SOURCE_PATH}) and clones from vmid "
        f"{UBUNTU_26_TEMPLATE_VMID} (Ubuntu 26)."
    )
    return True


def main():
    checks = [
        ("linux_vm module directory exists", test_module_dir_exists),
        (
            "module main.tf declares proxmox_virtual_environment_vm",
            test_module_main_declares_vm_resource,
        ),
        (
            "module main.tf clones from var.clone_from",
            test_module_main_clones_from_template_var,
        ),
        (
            "module main.tf wires ip_config (DHCP fallback + static branch)",
            test_module_main_wires_ip_config_dhcp_or_static,
        ),
        (
            "module main.tf disk block uses ${var.disk_gb}G + discard=on",
            test_module_main_disk_uses_disk_gb_var,
        ),
        (
            "module main.tf precondition guards static_ip/gateway pair",
            test_module_main_precondition_for_static_ip_pair,
        ),
        (
            "module main.tf plumbs user_account "
            "(default_user/default_password/ssh_authorized_keys)",
            test_module_main_user_account_plumbing,
        ),
        (
            "module main.tf cloud-init user_data drops "
            "sudoers.d NOPASSWD snippet",
            test_module_main_user_data_drops_sudoers_snippet,
        ),
        (
            "module variables.tf declares all required inputs "
            "(legacy + new dev-VM inputs)",
            test_module_variables_declares_required_inputs,
        ),
        (
            "module variables.tf declares static_ip/gateway with "
            "default = null",
            test_module_variables_static_ip_pair_nullable,
        ),
        (
            "module outputs.tf declares at least one output",
            test_module_outputs_file_exists,
        ),
        (
            "root main.tf invokes the linux_vm module for Ubuntu 26",
            test_root_main_calls_linux_vm_module_for_ubuntu26,
        ),
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
        f"SUCCESS: All {len(results)} tofu linux_vm module checks passed."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
