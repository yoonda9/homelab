"""Adversarial smoke test for the root `tofu/outputs.tf` ansible_inventory
aggregation.

Step 1b pivoted root `main.tf` from per-VM module blocks to a single
`module "linux_vm" { for_each = local.linux_vms ... }`. The associated
`output "ansible_inventory"` rewrites itself as a for-expression over
`module.linux_vm[*]`. The legacy per-module-block assertions live in
`scripts/test_dev_vms_main.py` now (which inspects `local.linux_vms` and
the for_each module). This file's job is the OUTPUTS half:

- root `outputs.tf` declares `output "ansible_inventory"`.
- the value contains a `proxmox_vms` group with a `hosts` map.
- the `hosts` map is built by a `for k, v in module.linux_vm` expression
  whose value sets `ansible_host`, `vmid`, and `node_name`.
- the group's `vars.ansible_user` references `var.default_user`
  (no hard-coded "user" literal — keeps the username overridable).

Text-based — no HCL parser dependency.
"""

import os
import re
import sys

TOFU_DIR = os.environ.get("TOFU_DIR", "tofu")
ROOT_OUTPUTS_PATH = os.environ.get(
    "ROOT_OUTPUTS_PATH", os.path.join(TOFU_DIR, "outputs.tf")
)

EXPECTED_GROUP_KEY = "proxmox_vms"
EXPECTED_HOST_ATTRS = ("ansible_host", "vmid", "node_name")


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _for_expression_body(text):
    """Return the body of `for k, v in module.linux_vm : k => { ... }`.

    Tolerates whitespace/newlines and any single-letter key/value names.
    Returns None if the for-expression is missing (e.g. someone reverted
    to per-module-block aggregation).
    """
    match = re.search(
        r"for\s+(?P<k>\w+)\s*,\s*(?P<v>\w+)\s+in\s+module\.linux_vm"
        r"\s*:\s*(?P=k)\s*=>\s*\{"
        r"(?P<body>(?:[^{}]|\{[^{}]*\})*)"
        r"\}",
        text,
    )
    return match.group("body") if match else None


def test_root_outputs_declares_ansible_inventory():
    text = read_text(ROOT_OUTPUTS_PATH)
    if text is None:
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing "
            f"(root outputs.tf must declare "
            f"output \"ansible_inventory\")."
        )
        return False
    if not re.search(r'output\s+"ansible_inventory"\s*\{', text):
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' must declare a top-level "
            f"output \"ansible_inventory\" block "
            f"(consumed by scripts/tofu_to_inventory.py)."
        )
        return False
    print(
        f"OK: '{ROOT_OUTPUTS_PATH}' declares "
        f"output \"ansible_inventory\"."
    )
    return True


def test_ansible_inventory_has_group_with_hosts_map():
    text = read_text(ROOT_OUTPUTS_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing.")
        return False
    if not re.search(
        re.escape(EXPECTED_GROUP_KEY) + r"\s*=\s*\{", text
    ):
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' ansible_inventory value must "
            f"contain a group key \"{EXPECTED_GROUP_KEY}\" mapping to "
            f"a block (e.g. {EXPECTED_GROUP_KEY} = {{ hosts = {{ ... }} }})."
        )
        return False
    if not re.search(r"hosts\s*=\s*\{", text):
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' ansible_inventory value must "
            f"include a \"hosts\" map under the group "
            f"(matching Ansible inventory shape)."
        )
        return False
    print(
        f"OK: '{ROOT_OUTPUTS_PATH}' ansible_inventory contains "
        f"\"{EXPECTED_GROUP_KEY}\" group with a \"hosts\" map."
    )
    return True


def test_hosts_built_via_module_linux_vm_for_expression():
    text = read_text(ROOT_OUTPUTS_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing.")
        return False
    body = _for_expression_body(text)
    if body is None:
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' must build "
            f"proxmox_vms.hosts via a for-expression "
            f"`for k, v in module.linux_vm : k => {{ ... }}` "
            f"(Step 1b aggregates over the for_each-induced map; "
            f"per-module-block aggregation is gone)."
        )
        return False
    missing = [a for a in EXPECTED_HOST_ATTRS if not re.search(
        r"\b" + re.escape(a) + r"\s*=", body
    )]
    if missing:
        print(
            f"FAIL: for-expression in '{ROOT_OUTPUTS_PATH}' is missing "
            f"attribute(s): {missing}. Each host entry must set "
            f"{EXPECTED_HOST_ATTRS} (per-host inventory shape consumed "
            f"by scripts/tofu_to_inventory.py)."
        )
        return False
    if not re.search(r"try\s*\(\s*\w+\.ipv4_address\s*,\s*null\s*\)", body):
        print(
            f"FAIL: for-expression in '{ROOT_OUTPUTS_PATH}' must wrap "
            f"`<v>.ipv4_address` in try(..., null) so plan stays valid "
            f"before the qemu-guest-agent reports a lease."
        )
        return False
    print(
        f"OK: '{ROOT_OUTPUTS_PATH}' builds proxmox_vms.hosts via "
        f"`for k, v in module.linux_vm` and sets "
        f"{EXPECTED_HOST_ATTRS} on every entry."
    )
    return True


def test_group_vars_ansible_user_references_default_user_var():
    text = read_text(ROOT_OUTPUTS_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing.")
        return False
    if not re.search(
        r"ansible_user\s*=\s*var\.default_user\b", text
    ):
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' must set "
            f"`vars.ansible_user = var.default_user` "
            f"(uniform username plumbed from var.default_user; "
            f"no hard-coded literal — keeps it overridable in tfvars)."
        )
        return False
    print(
        f"OK: '{ROOT_OUTPUTS_PATH}' group vars.ansible_user references "
        f"var.default_user."
    )
    return True


def main():
    checks = [
        (
            "root outputs.tf declares output \"ansible_inventory\"",
            test_root_outputs_declares_ansible_inventory,
        ),
        (
            "ansible_inventory exposes proxmox_vms group with hosts map",
            test_ansible_inventory_has_group_with_hosts_map,
        ),
        (
            "hosts map built via for k, v in module.linux_vm",
            test_hosts_built_via_module_linux_vm_for_expression,
        ),
        (
            "group vars.ansible_user references var.default_user",
            test_group_vars_ansible_user_references_default_user_var,
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
        f"SUCCESS: All {len(results)} tofu inventory output checks passed."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
