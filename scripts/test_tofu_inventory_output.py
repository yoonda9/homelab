"""Adversarial smoke test for the Step 3 multi-VM declarations + ansible_inventory output.

Mirrors the shape of `scripts/test_tofu_scaffold.py` and
`scripts/test_tofu_linux_vm_module.py`: load the artifact, assert key
declarations are present, fail with a precise message otherwise.
Intentionally text-based so we don't add an HCL parser dependency for
a focused multi-VM/output check.
"""

import os
import re
import sys

TOFU_DIR = os.environ.get("TOFU_DIR", "tofu")
ROOT_MAIN_PATH = os.environ.get(
    "ROOT_MAIN_PATH", os.path.join(TOFU_DIR, "main.tf")
)
ROOT_OUTPUTS_PATH = os.environ.get(
    "ROOT_OUTPUTS_PATH", os.path.join(TOFU_DIR, "outputs.tf")
)

# Cloud-image template vmids from
# ansible/group_vars/all.yml (pve_cloud_images).
UBUNTU_26_TEMPLATE_VMID = 9001
CENTOS_STREAM_TEMPLATE_VMID = 9002

EXPECTED_GROUP_KEY = "proxmox_vms"
EXPECTED_MODULE_NAMES = ("ubuntu26_test", "centos10_test")


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _module_blocks(text):
    """Return [(label, body)] for every top-level module "label" {...} block.

    Tolerates one level of brace nesting inside the body, which matches
    the current root config shape (clone {...}, cpu {...}, etc. live
    inside modules/linux_vm/main.tf, not the root, but defensive anyway).
    """
    return re.findall(
        r'module\s+"(?P<label>[^"]+)"\s*\{'
        r"(?P<body>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
        text,
    )


def _host_block_for(text, module_name):
    """Return the body of the (module.<module_name>.name) = { ... } host
    block from outputs.tf, or None if not present.

    Matches: `(module.<name>.name) = { ... }` and tolerates one level of
    brace nesting inside the body. Per-host extraction is required so a
    Step 3 mutation that only breaks ONE host can't slip through a
    file-global substring check (gap surfaced by Finalizer Step 3).
    """
    pattern = (
        r"\(\s*module\."
        + re.escape(module_name)
        + r"\.name\s*\)\s*=\s*\{"
        + r"(?P<body>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"
    )
    match = re.search(pattern, text)
    return match.group("body") if match else None


def test_root_main_declares_two_vm_module_blocks():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    blocks = _module_blocks(text)
    vm_blocks = [
        (label, body)
        for label, body in blocks
        if re.search(r'source\s*=\s*"\./modules/linux_vm"', body)
    ]
    if len(vm_blocks) < 2:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' must contain at least two distinct "
            f"module \"...\" blocks whose source = \"./modules/linux_vm\" "
            f"(Step 3 declares Ubuntu 26 + CentOS Stream guests via the "
            f"linux_vm module); found {len(vm_blocks)}."
        )
        return False
    labels = [label for label, _ in vm_blocks]
    if len(set(labels)) != len(labels):
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' module labels must be distinct; "
            f"got {labels}."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' declares {len(vm_blocks)} distinct "
        f"module blocks sourced from ./modules/linux_vm "
        f"({', '.join(labels)})."
    )
    return True


def test_root_main_clones_ubuntu26_and_centos_stream():
    text = read_text(ROOT_MAIN_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_MAIN_PATH}' is missing.")
        return False
    blocks = _module_blocks(text)
    # Map module label -> body for linux_vm-module callers.
    vm_blocks = {
        label: body
        for label, body in blocks
        if re.search(r'source\s*=\s*"\./modules/linux_vm"', body)
    }
    expected = {
        "ubuntu26_test": UBUNTU_26_TEMPLATE_VMID,
        "centos10_test": CENTOS_STREAM_TEMPLATE_VMID,
    }
    missing = []
    for name, vmid in expected.items():
        body = vm_blocks.get(name)
        if body is None:
            missing.append(
                f"module \"{name}\" (clone_from = {vmid})"
            )
            continue
        if not re.search(r"clone_from\s*=\s*" + str(vmid) + r"\b", body):
            missing.append(
                f"module \"{name}\" must set clone_from = {vmid}"
            )
    if missing:
        print(
            f"FAIL: '{ROOT_MAIN_PATH}' multi-VM declaration incomplete: "
            f"{'; '.join(missing)} "
            f"(canonical Tofu test fleet: ubuntu26-test vmid 300 clone "
            f"9001, centos10-test vmid 301 clone 9002)."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_PATH}' declares ubuntu26_test "
        f"(clone_from = {UBUNTU_26_TEMPLATE_VMID}) and centos10_test "
        f"(clone_from = {CENTOS_STREAM_TEMPLATE_VMID})."
    )
    return True


def test_root_outputs_declares_ansible_inventory():
    text = read_text(ROOT_OUTPUTS_PATH)
    if text is None:
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing "
            f"(Step 3 must add a top-level outputs.tf with "
            f"output \"ansible_inventory\")."
        )
        return False
    if not re.search(r'output\s+"ansible_inventory"\s*\{', text):
        print(
            f"FAIL: '{ROOT_OUTPUTS_PATH}' must declare a top-level "
            f"output \"ansible_inventory\" block "
            f"(consumed by the Step 4 inventory generator)."
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


def test_ansible_inventory_hosts_reference_per_module():
    text = read_text(ROOT_OUTPUTS_PATH)
    if text is None:
        print(f"FAIL: '{ROOT_OUTPUTS_PATH}' is missing.")
        return False
    # Per-host check (tightened in Step 4): extract each
    # (module.<name>.name) = { ... } block and assert ansible_host AND
    # vmid live INSIDE that specific block. A file-global substring
    # check would let a mutation that only breaks ONE host (e.g.
    # rename ansible_host → remote_addr on ubuntu26_test only) slip
    # through, as Finalizer Step 3 demonstrated.
    for name in EXPECTED_MODULE_NAMES:
        body = _host_block_for(text, name)
        if body is None:
            print(
                f"FAIL: '{ROOT_OUTPUTS_PATH}' ansible_inventory hosts "
                f"map missing per-host block "
                f"(module.{name}.name) = {{ ... }} "
                f"(each guest must be keyed by its module's name "
                f"attribute)."
            )
            return False
        if not re.search(r"\bansible_host\s*=", body):
            print(
                f"FAIL: '{ROOT_OUTPUTS_PATH}' host block for "
                f"module \"{name}\" is missing 'ansible_host = ...' "
                f"INSIDE the host body (per-host check). "
                f"Ansible's reserved connection-target hostvar must "
                f"be set on every host entry."
            )
            return False
        # Either a literal vmid attribute or a reference to the
        # module's vmid/ipv4_address outputs is acceptable; both
        # express per-host identity.
        per_host_module_attrs = re.findall(
            r"module\." + re.escape(name) + r"\.(\w+)", body
        )
        has_id = (
            re.search(r"\bvmid\s*=", body) is not None
            or any(
                a in per_host_module_attrs
                for a in ("vmid", "ipv4_address")
            )
        )
        if not has_id:
            print(
                f"FAIL: '{ROOT_OUTPUTS_PATH}' host block for "
                f"module \"{name}\" must include 'vmid = ...' or "
                f"reference module.{name}.vmid/.ipv4_address "
                f"(currently references: "
                f"{', '.join(per_host_module_attrs) or '<none>'})."
            )
            return False
    print(
        f"OK: '{ROOT_OUTPUTS_PATH}' per-host blocks each set "
        f"ansible_host and a vmid/ip identity inside the host body."
    )
    return True


def main():
    checks = [
        (
            "root main.tf declares two vm-module blocks",
            test_root_main_declares_two_vm_module_blocks,
        ),
        (
            "root main.tf clones Ubuntu 26 + CentOS Stream templates",
            test_root_main_clones_ubuntu26_and_centos_stream,
        ),
        (
            "root outputs.tf declares output \"ansible_inventory\"",
            test_root_outputs_declares_ansible_inventory,
        ),
        (
            "ansible_inventory exposes proxmox_vms group with hosts map",
            test_ansible_inventory_has_group_with_hosts_map,
        ),
        (
            "ansible_inventory hosts reference per-module name + "
            "ansible_host/vmid",
            test_ansible_inventory_hosts_reference_per_module,
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
