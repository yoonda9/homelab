import os
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/pve_vm_deploy/tasks/main.yml"
)
WINDOWS_TASKS_PATH = os.environ.get(
    "WINDOWS_TASKS_PATH",
    "ansible/roles/pve_vm_deploy/tasks/windows.yml",
)
VARS_PATH = os.environ.get(
    "VARS_PATH", "ansible/group_vars/all.yml"
)
SERVICES_PLAYBOOK_PATH = os.environ.get(
    "SERVICES_PLAYBOOK_PATH", "ansible/services.yml"
)
KVM_MODULE = "community.proxmox.proxmox_kvm"
ROLE_NAME = "pve_vm_deploy"
SERVICES_TARGET_HOSTS = "proxmox_hosts"
REQUIRED_VM_KEYS = ("name", "vmid", "clone_from_vmid")


def load_yaml(path):
    if not os.path.exists(path):
        print(f"FAIL: '{path}' is missing.")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)


def flatten_tasks(task_list):
    for task in task_list:
        if not isinstance(task, dict):
            continue
        yield task
        for key in ("block", "tasks"):
            if key in task:
                yield from flatten_tasks(task[key])


def find_tasks_by_module(tasks, module):
    return [t for t in flatten_tasks(tasks) if module in t]


def test_role_tasks_file_exists():
    if os.path.exists(TASKS_PATH):
        print(f"OK: Role tasks file exists at '{TASKS_PATH}'.")
        return True
    print(f"FAIL: Role tasks file '{TASKS_PATH}' is missing.")
    return False


def test_uses_proxmox_kvm(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    if kvm_tasks:
        print(
            f"OK: Role uses '{KVM_MODULE}' "
            f"({len(kvm_tasks)} task(s))."
        )
        return True
    print(f"FAIL: Role does not use '{KVM_MODULE}'.")
    return False


def test_delegates_to_localhost(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    if not kvm_tasks:
        print("FAIL: No proxmox_kvm task found to check delegate_to.")
        return False
    for task in kvm_tasks:
        delegate = str(task.get("delegate_to", ""))
        if delegate != "localhost":
            name = task.get("name", "unnamed")
            print(
                f"FAIL: KVM task '{name}' missing "
                f"delegate_to: localhost (API module must "
                f"run on control node)."
            )
            return False
    print("OK: All proxmox_kvm tasks delegate to localhost.")
    return True


def test_iterates_over_pve_vms(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    if not kvm_tasks:
        print("FAIL: No proxmox_kvm task found to check loop.")
        return False
    for task in kvm_tasks:
        loop_val = task.get("loop")
        if loop_val is None:
            name = task.get("name", "unnamed")
            print(
                f"FAIL: KVM task '{name}' missing 'loop:' "
                f"(role must iterate over pve_vms list)."
            )
            return False
        loop_str = str(loop_val)
        if "pve_vms" not in loop_str:
            print(
                f"FAIL: KVM task loop does not reference "
                f"'pve_vms' (got: {loop_str!r})."
            )
            return False
    print("OK: Role iterates via 'loop:' over pve_vms.")
    return True


def test_ipconfig0_is_dhcp(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    if not kvm_tasks:
        print("FAIL: No proxmox_kvm task found to check ipconfig0.")
        return False
    for task in kvm_tasks:
        params = task.get(KVM_MODULE, {})
        ipconfig0 = params.get("ipconfig0")
        if ipconfig0 is None:
            name = task.get("name", "unnamed")
            print(
                f"FAIL: KVM task '{name}' missing "
                f"'ipconfig0' (DHCP cloud-init must be "
                f"declared explicitly)."
            )
            return False
        ipconfig0_str = str(ipconfig0)
        if "ip=dhcp" not in ipconfig0_str:
            print(
                f"FAIL: ipconfig0 does not contain 'ip=dhcp' "
                f"(got: {ipconfig0_str!r}). DHCP is the "
                f"contract this role enforces."
            )
            return False
    print("OK: ipconfig0 is set and requests DHCP.")
    return True


def test_multi_os_coverage(variables):
    pve_cloud_images = variables.get("pve_cloud_images", [])
    pve_vms = variables.get("pve_vms", [])
    if not isinstance(pve_cloud_images, list):
        print(
            f"FAIL: 'pve_cloud_images' must be a list "
            f"(got {type(pve_cloud_images).__name__})."
        )
        return False
    if not isinstance(pve_vms, list):
        print(
            f"FAIL: 'pve_vms' must be a list "
            f"(got {type(pve_vms).__name__})."
        )
        return False
    cloud_vmids = {
        img.get("vmid")
        for img in pve_cloud_images
        if isinstance(img, dict)
    }
    cloud_vmids.discard(None)
    if len(cloud_vmids) < 2:
        print(
            f"FAIL: 'pve_cloud_images' must contain >=2 distinct "
            f"vmid entries for multi-OS coverage "
            f"(got {sorted(cloud_vmids)})."
        )
        return False
    clone_targets = {
        vm.get("clone_from_vmid")
        for vm in pve_vms
        if isinstance(vm, dict)
    }
    clone_targets.discard(None)
    if len(clone_targets) < 2:
        print(
            f"FAIL: 'pve_vms' must reference >=2 distinct "
            f"clone_from_vmid values for multi-OS coverage "
            f"(got {sorted(clone_targets)})."
        )
        return False
    missing = clone_targets - cloud_vmids
    if missing:
        print(
            f"FAIL: pve_vms.clone_from_vmid references vmid(s) "
            f"not present in pve_cloud_images: {sorted(missing)}."
        )
        return False
    print(
        f"OK: multi-OS coverage: {len(cloud_vmids)} cloud "
        f"template(s), {len(clone_targets)} distinct clone "
        f"target(s), all references resolve."
    )
    return True


def test_windows_branch_knobs():
    if not os.path.exists(WINDOWS_TASKS_PATH):
        print(
            f"FAIL: Windows tasks file '{WINDOWS_TASKS_PATH}' is "
            f"missing (Windows 11 ISO-based branch must live here)."
        )
        return False
    win_tasks = load_yaml(WINDOWS_TASKS_PATH)
    if not isinstance(win_tasks, list):
        print(
            f"FAIL: '{WINDOWS_TASKS_PATH}' must be a list of tasks "
            f"(got {type(win_tasks).__name__})."
        )
        return False
    kvm_tasks = find_tasks_by_module(win_tasks, KVM_MODULE)
    if not kvm_tasks:
        print(
            f"FAIL: '{WINDOWS_TASKS_PATH}' must contain at least "
            f"one '{KVM_MODULE}' task."
        )
        return False
    for task in kvm_tasks:
        delegate = str(task.get("delegate_to", ""))
        if delegate != "localhost":
            name = task.get("name", "unnamed")
            print(
                f"FAIL: Windows KVM task '{name}' missing "
                f"delegate_to: localhost."
            )
            return False
        loop_val = task.get("loop")
        if loop_val is None or "pve_windows_vms" not in str(loop_val):
            name = task.get("name", "unnamed")
            print(
                f"FAIL: Windows KVM task '{name}' must loop over "
                f"'pve_windows_vms' (got: {loop_val!r})."
            )
            return False
        params = task.get(KVM_MODULE, {})
        ostype = str(params.get("ostype", ""))
        if ostype != "win11":
            print(
                f"FAIL: Windows KVM ostype must equal 'win11' "
                f"(got: {ostype!r})."
            )
            return False
        bios = str(params.get("bios", ""))
        if bios != "ovmf":
            print(
                f"FAIL: Windows KVM bios must equal 'ovmf' "
                f"for UEFI/TPM support (got: {bios!r})."
            )
            return False
        if not params.get("efidisk0"):
            print(
                "FAIL: Windows KVM missing 'efidisk0' "
                "(EFI vars disk required for OVMF)."
            )
            return False
        if not params.get("tpmstate0"):
            print(
                "FAIL: Windows KVM missing 'tpmstate0' "
                "(TPM 2.0 required by Win11)."
            )
            return False
        scsihw = str(params.get("scsihw", ""))
        if not scsihw.startswith("virtio-scsi"):
            print(
                f"FAIL: Windows KVM scsihw must start with "
                f"'virtio-scsi' (got: {scsihw!r})."
            )
            return False
        cdrom_slots = [
            v
            for k, v in params.items()
            if k.startswith(("ide", "sata", "scsi"))
            and isinstance(v, str)
            and "media=cdrom" in v
        ]
        if len(cdrom_slots) < 2:
            print(
                f"FAIL: Windows KVM must mount 2 ISOs as "
                f"cdrom (install ISO + virtio-win drivers); "
                f"found {len(cdrom_slots)}."
            )
            return False
    print(
        f"OK: Windows branch knobs present in "
        f"'{WINDOWS_TASKS_PATH}' ({len(kvm_tasks)} KVM task(s))."
    )
    return True


def _role_names_in_play(play):
    roles = play.get("roles", []) or []
    names = []
    for entry in roles:
        if isinstance(entry, str):
            names.append(entry)
        elif isinstance(entry, dict):
            role = entry.get("role") or entry.get("name")
            if isinstance(role, str):
                names.append(role)
    return names


def test_services_yml_wires_role():
    if not os.path.exists(SERVICES_PLAYBOOK_PATH):
        print(
            f"FAIL: services playbook '{SERVICES_PLAYBOOK_PATH}' is "
            f"missing (Step 4 wiring)."
        )
        return False
    plays = load_yaml(SERVICES_PLAYBOOK_PATH)
    if not isinstance(plays, list) or not plays:
        print(
            f"FAIL: '{SERVICES_PLAYBOOK_PATH}' must be a non-empty "
            f"list of plays (got {type(plays).__name__})."
        )
        return False
    matching = []
    for play in plays:
        if not isinstance(play, dict):
            continue
        hosts = str(play.get("hosts", ""))
        if hosts != SERVICES_TARGET_HOSTS:
            continue
        if ROLE_NAME in _role_names_in_play(play):
            matching.append(play)
    if not matching:
        print(
            f"FAIL: '{SERVICES_PLAYBOOK_PATH}' must contain a play "
            f"with hosts: {SERVICES_TARGET_HOSTS} that includes "
            f"'{ROLE_NAME}' in its roles list."
        )
        return False
    print(
        f"OK: '{SERVICES_PLAYBOOK_PATH}' wires '{ROLE_NAME}' into "
        f"a {SERVICES_TARGET_HOSTS} play "
        f"({len(matching)} matching play(s))."
    )
    return True


def test_pve_vms_in_all_yml(variables):
    if "pve_vms" not in variables:
        print("FAIL: 'pve_vms' missing from all.yml.")
        return False
    pve_vms = variables["pve_vms"]
    if not isinstance(pve_vms, list):
        print(
            f"FAIL: 'pve_vms' in all.yml must be a list "
            f"(got {type(pve_vms).__name__})."
        )
        return False
    if not pve_vms:
        print(
            "FAIL: 'pve_vms' in all.yml is empty; expected "
            "at least one example VM entry."
        )
        return False
    for idx, vm in enumerate(pve_vms):
        if not isinstance(vm, dict):
            print(
                f"FAIL: pve_vms[{idx}] is not a dict "
                f"(got {type(vm).__name__})."
            )
            return False
        missing = [k for k in REQUIRED_VM_KEYS if k not in vm]
        if missing:
            print(
                f"FAIL: pve_vms[{idx}] missing required "
                f"keys: {', '.join(missing)}."
            )
            return False
    print(
        f"OK: all.yml defines pve_vms with "
        f"{len(pve_vms)} entry(ies) and required keys."
    )
    return True


def main():
    if not test_role_tasks_file_exists():
        sys.exit(1)

    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        ("Uses community.proxmox.proxmox_kvm", lambda: test_uses_proxmox_kvm(tasks)),
        ("Delegates to localhost", lambda: test_delegates_to_localhost(tasks)),
        ("Iterates over pve_vms via loop:", lambda: test_iterates_over_pve_vms(tasks)),
        ("ipconfig0 contains ip=dhcp", lambda: test_ipconfig0_is_dhcp(tasks)),
        ("pve_vms list defined in all.yml", lambda: test_pve_vms_in_all_yml(variables)),
        ("Multi-OS coverage in pve_cloud_images and pve_vms", lambda: test_multi_os_coverage(variables)),
        ("Windows 11 ISO branch knobs in windows.yml", lambda: test_windows_branch_knobs()),
        ("services.yml wires pve_vm_deploy under proxmox_hosts", lambda: test_services_yml_wires_role()),
    ]

    results = [(label, fn()) for label, fn in checks]

    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    print(f"SUCCESS: All {len(results)} pve_vm_deploy checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
