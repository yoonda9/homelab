"""Adversarial smoke test for the root `tofu/outputs.tf` ansible_inventory
aggregation.

Step 1b pivoted root `main.tf` from per-VM module blocks to a single
`module "linux_vm" { for_each = local.linux_vms ... }`. The associated
`output "ansible_inventory"` rewrites itself as a for-expression over
`module.linux_vm[*]`. Step 2 added a sibling `windows_dev_vms` group
built from `module.windows_vm[*]` with the same shape. The legacy
per-module-block assertions live in `scripts/test_dev_vms_main.py` now
(which inspects `local.linux_vms` / `local.windows_vms` and the for_each
modules). This file's job is the OUTPUTS half:

- root `outputs.tf` declares `output "ansible_inventory"`.
- the value contains both a `proxmox_vms` group AND a sibling
  `windows_dev_vms` group, each with a `hosts` map.
- each group's `hosts` map is built by a
  `for k, v in module.<linux_vm|windows_vm>` expression whose value
  sets `ansible_host`, `vmid`, and `node_name`, with `<v>.ipv4_address`
  wrapped in `try(..., null)` so plan stays valid before the
  qemu-guest-agent reports a lease.
- each group's `vars.ansible_user` references `var.default_user`
  (no hard-coded "user" literal — keeps the username overridable).
  Asserted by counting occurrences (one per group) so silently
  deleting either group's vars block trips the check.

Text-based — no HCL parser dependency.
"""

import os
import re
import sys

TOFU_DIR = os.environ.get("TOFU_DIR", "tofu")
ROOT_OUTPUTS_PATH = os.environ.get(
    "ROOT_OUTPUTS_PATH", os.path.join(TOFU_DIR, "outputs.tf")
)

EXPECTED_HOST_ATTRS = ("ansible_host", "vmid", "node_name")
EXPECTED_GROUPS = (
    ("proxmox_vms", "linux_vm"),
    ("windows_dev_vms", "windows_vm"),
)


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _for_expression_body(text, module_name):
    """Return the body of `for k, v in module.<module_name> : k => { ... }`.

    Tolerates whitespace/newlines and any single-letter key/value names.
    Returns None if the for-expression is missing (e.g. someone reverted
    to per-module-block aggregation, or deleted the corresponding group).
    """
    match = re.search(
        r"for\s+(?P<k>\w+)\s*,\s*(?P<v>\w+)\s+in\s+module\."
        + re.escape(module_name)
        + r"\s*:\s*(?P=k)\s*=>\s*\{"
        + r"(?P<body>(?:[^{}]|\{[^{}]*\})*)"
        + r"\}",
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


def _make_group_with_hosts_map_test(group_key):
    def _test():
        text = read_text(ROOT_OUTPUTS_PATH)
        if text is None:
            print(f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing.")
            return False
        if not re.search(
            re.escape(group_key) + r"\s*=\s*\{", text
        ):
            print(
                f"FAIL: '{ROOT_OUTPUTS_PATH}' ansible_inventory value "
                f"must contain a group key \"{group_key}\" mapping to "
                f"a block (e.g. {group_key} = {{ hosts = {{ ... }} }})."
            )
            return False
        if not re.search(r"hosts\s*=\s*\{", text):
            print(
                f"FAIL: '{ROOT_OUTPUTS_PATH}' ansible_inventory value "
                f"must include a \"hosts\" map under the group "
                f"(matching Ansible inventory shape)."
            )
            return False
        print(
            f"OK: '{ROOT_OUTPUTS_PATH}' ansible_inventory contains "
            f"\"{group_key}\" group with a \"hosts\" map."
        )
        return True
    return _test


def _make_hosts_for_expression_test(group_key, module_name):
    def _test():
        text = read_text(ROOT_OUTPUTS_PATH)
        if text is None:
            print(f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing.")
            return False
        body = _for_expression_body(text, module_name)
        if body is None:
            print(
                f"FAIL: '{ROOT_OUTPUTS_PATH}' must build "
                f"{group_key}.hosts via a for-expression "
                f"`for k, v in module.{module_name} : k => {{ ... }}` "
                f"(aggregates over the for_each-induced map; "
                f"per-module-block aggregation is gone)."
            )
            return False
        missing = [a for a in EXPECTED_HOST_ATTRS if not re.search(
            r"\b" + re.escape(a) + r"\s*=", body
        )]
        if missing:
            print(
                f"FAIL: for-expression over module.{module_name} in "
                f"'{ROOT_OUTPUTS_PATH}' is missing attribute(s): "
                f"{missing}. Each host entry must set "
                f"{EXPECTED_HOST_ATTRS} (per-host inventory shape "
                f"consumed by scripts/tofu_to_inventory.py)."
            )
            return False
        if not re.search(
            r"try\s*\(\s*\w+\.ipv4_address\s*,\s*null\s*\)", body
        ):
            print(
                f"FAIL: for-expression over module.{module_name} in "
                f"'{ROOT_OUTPUTS_PATH}' must wrap `<v>.ipv4_address` in "
                f"try(..., null) so plan stays valid before the "
                f"qemu-guest-agent reports a lease."
            )
            return False
        print(
            f"OK: '{ROOT_OUTPUTS_PATH}' builds {group_key}.hosts via "
            f"`for k, v in module.{module_name}` and sets "
            f"{EXPECTED_HOST_ATTRS} on every entry."
        )
        return True
    return _test


def test_group_vars_ansible_user_references_default_user_var():
    text = read_text(ROOT_OUTPUTS_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing.")
        return False
    matches = re.findall(
        r"ansible_user\s*=\s*var\.default_user\b", text
    )
    expected = len(EXPECTED_GROUPS)
    if len(matches) < expected:
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' must set "
            f"`vars.ansible_user = var.default_user` once per group "
            f"(expected at least {expected} occurrences for groups "
            f"{[g for g, _ in EXPECTED_GROUPS]}, found {len(matches)}). "
            f"Each group's vars block must plumb the username from "
            f"var.default_user — no hard-coded literal, keeps it "
            f"overridable in tfvars."
        )
        return False
    print(
        f"OK: '{ROOT_OUTPUTS_PATH}' has {len(matches)} "
        f"`ansible_user = var.default_user` references "
        f"(one per group)."
    )
    return True


def main():
    checks = [
        (
            "root outputs.tf declares output \"ansible_inventory\"",
            test_root_outputs_declares_ansible_inventory,
        ),
    ]
    for group_key, module_name in EXPECTED_GROUPS:
        checks.append((
            f"ansible_inventory exposes {group_key} group with hosts map",
            _make_group_with_hosts_map_test(group_key),
        ))
        checks.append((
            f"{group_key}.hosts built via for k, v in module.{module_name}",
            _make_hosts_for_expression_test(group_key, module_name),
        ))
    checks.append((
        "vars.ansible_user references var.default_user in every group",
        test_group_vars_ansible_user_references_default_user_var,
    ))
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
