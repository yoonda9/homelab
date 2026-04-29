"""Adversarial smoke test for the OpenTofu vm module under `tofu/modules/vm/`.

Mirrors the shape of `scripts/test_tofu_scaffold.py`: load the artifact,
assert key declarations are present, fail with a precise message
otherwise. Intentionally text-based so we don't add an HCL parser
dependency for a focused module check.
"""

import os
import re
import sys

TOFU_DIR = os.environ.get("TOFU_DIR", "tofu")
MODULE_DIR = os.environ.get(
    "MODULE_DIR", os.path.join(TOFU_DIR, "modules", "vm")
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
    "vmid",
    "clone_from",
    "memory",
    "cores",
    "bridge",
    "template_node",
)
# Ubuntu 26 cloud-image template vmid from
# ansible/group_vars/all.yml (pve_cloud_images entry "ubuntu-26.04-cloud").
UBUNTU_26_TEMPLATE_VMID = 9001


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_module_dir_exists():
    if os.path.isdir(MODULE_DIR):
        print(f"OK: vm module directory exists at '{MODULE_DIR}'.")
        return True
    print(f"FAIL: vm module directory '{MODULE_DIR}' is missing.")
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
    # The clone block must reference var.clone_from so the module is
    # parameterized rather than pinned to a single template vmid.
    clone_block = re.search(
        r"clone\s*\{(?P<body>[^}]*)\}", text
    )
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


def test_module_main_wires_dhcp_ip_config():
    text = read_text(MODULE_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{MODULE_MAIN_PATH}' is missing.")
        return False
    # Cloud-init DHCP wiring per bpg/proxmox v0.104.0:
    #   initialization {
    #     ip_config {
    #       ipv4 { address = "dhcp" }
    #       ipv6 { address = "auto" }
    #     }
    #   }
    # Match the nested blocks across newlines so formatting is free.
    pattern = (
        r"initialization\s*\{[^{}]*"
        r"ip_config\s*\{[^{}]*"
        r"ipv4\s*\{[^{}]*address\s*=\s*\"dhcp\"[^{}]*\}[\s\S]*?"
        r"ipv6\s*\{[^{}]*address\s*=\s*\"auto\"[^{}]*\}"
    )
    if not re.search(pattern, text):
        print(
            f"FAIL: '{MODULE_MAIN_PATH}' must wire DHCP via "
            f"initialization.ip_config with "
            f"ipv4 {{ address = \"dhcp\" }} and "
            f"ipv6 {{ address = \"auto\" }} "
            f"(matches the existing ipconfig0=\"ip=dhcp,ip6=auto\" convention)."
        )
        return False
    print(
        f"OK: '{MODULE_MAIN_PATH}' wires "
        f"initialization.ip_config for IPv4 dhcp + IPv6 auto."
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


def test_root_main_calls_vm_module_for_ubuntu26():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    # Match a module block that points at ./modules/vm. There may be
    # several module blocks in the future, so scan all and check at
    # least one wires the Ubuntu 26 template vmid (9001).
    module_blocks = re.findall(
        r'module\s+"[^"]+"\s*\{(?P<body>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
        text,
    )
    if not module_blocks:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must contain at least one "
            f"module \"...\" block "
            f"(root config must invoke the vm module)."
        )
        return False
    vm_module_blocks = [
        body for body in module_blocks
        if re.search(r'source\s*=\s*"\./modules/vm"', body)
    ]
    if not vm_module_blocks:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' has module blocks but none "
            f"set source = \"./modules/vm\" "
            f"(root config must invoke the vm module from "
            f"./modules/vm)."
        )
        return False
    if not any(
        re.search(
            r"clone_from\s*=\s*" + str(UBUNTU_26_TEMPLATE_VMID) + r"\b",
            body,
        )
        for body in vm_module_blocks
    ):
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must invoke the vm module "
            f"with clone_from = {UBUNTU_26_TEMPLATE_VMID} "
            f"(Ubuntu 26 cloud-image template vmid from "
            f"ansible/group_vars/all.yml)."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' invokes the vm module "
        f"(source=./modules/vm) and clones from vmid "
        f"{UBUNTU_26_TEMPLATE_VMID} (Ubuntu 26)."
    )
    return True


def main():
    checks = [
        ("vm module directory exists", test_module_dir_exists),
        (
            "module main.tf declares proxmox_virtual_environment_vm",
            test_module_main_declares_vm_resource,
        ),
        (
            "module main.tf clones from var.clone_from",
            test_module_main_clones_from_template_var,
        ),
        (
            "module main.tf wires DHCP via initialization.ip_config",
            test_module_main_wires_dhcp_ip_config,
        ),
        (
            "module variables.tf declares vmid/clone_from/memory/"
            "cores/bridge/template_node",
            test_module_variables_declares_required_inputs,
        ),
        (
            "module outputs.tf declares at least one output",
            test_module_outputs_file_exists,
        ),
        (
            "root main.tf invokes the vm module for Ubuntu 26",
            test_root_main_calls_vm_module_for_ubuntu26,
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
        f"SUCCESS: All {len(results)} tofu vm module checks passed."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
