import os
import re
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/pve_provision/tasks/main.yml"
)
VARS_PATH = os.environ.get(
    "VARS_PATH", "ansible/group_vars/all.yml"
)
KVM_MODULE = "community.proxmox.proxmox_kvm"


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
    results = []
    for task in flatten_tasks(tasks):
        if module in task:
            results.append(task)
    return results


def find_bitwarden_task(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    for task in kvm_tasks:
        name = task.get("name", "").lower()
        if "bitwarden" in name:
            return task
    return None


def test_bitwarden_vm_task_exists(tasks):
    task = find_bitwarden_task(tasks)
    if task:
        print(
            f"OK: Bitwarden VM task exists "
            f"(uses {KVM_MODULE})."
        )
        return True
    print(
        f"FAIL: No Bitwarden VM task found using "
        f"'{KVM_MODULE}' with 'bitwarden' in task name."
    )
    return False


def test_bitwarden_uses_clone(tasks):
    task = find_bitwarden_task(tasks)
    if not task:
        print("FAIL: No Bitwarden task found.")
        return False
    params = task.get(KVM_MODULE, {})
    if "clone" in params:
        print(
            "OK: Bitwarden VM clones from a template."
        )
        return True
    print(
        "FAIL: Bitwarden VM task missing 'clone' "
        "parameter (must clone from cloud template)."
    )
    return False


def test_bitwarden_has_sufficient_ram(tasks):
    task = find_bitwarden_task(tasks)
    if not task:
        print("FAIL: No Bitwarden task found.")
        return False
    params = task.get(KVM_MODULE, {})
    memory_val = str(params.get("memory", ""))
    match = re.search(r"default\((\d+)\)", memory_val)
    if match:
        default_mb = int(match.group(1))
    elif memory_val.isdigit():
        default_mb = int(memory_val)
    else:
        print(
            "FAIL: Bitwarden VM memory parameter is not "
            "a recognizable integer or Jinja default."
        )
        return False
    if default_mb >= 4096:
        print(
            f"OK: Bitwarden VM has sufficient RAM "
            f"(default {default_mb}MB >= 4096MB)."
        )
        return True
    print(
        f"FAIL: Bitwarden VM default RAM is "
        f"{default_mb}MB, must be >= 4096MB "
        f"(official on-premise requirement)."
    )
    return False


def test_bitwarden_has_docker_compose_cloudinit(tasks):
    task = find_bitwarden_task(tasks)
    if not task:
        print("FAIL: No Bitwarden task found.")
        return False
    params = task.get(KVM_MODULE, {})
    if "cicustom" not in params:
        print(
            "FAIL: Bitwarden VM task missing 'cicustom' "
            "parameter in module params (required for "
            "Docker Compose provisioning via cloud-init)."
        )
        return False
    print(
        "OK: Bitwarden VM has cloud-init "
        "provisioning for Docker Compose "
        "(cicustom parameter present)."
    )
    return True


def test_bitwarden_has_vmid(tasks):
    task = find_bitwarden_task(tasks)
    if not task:
        print("FAIL: No Bitwarden task found.")
        return False
    params = task.get(KVM_MODULE, {})
    vmid = str(params.get("vmid", ""))
    if "bitwarden_vmid" in vmid or vmid.isdigit():
        print(
            "OK: Bitwarden VM uses a dedicated VMID."
        )
        return True
    print(
        "FAIL: Bitwarden VM task missing 'vmid' "
        "parameter (must use bitwarden_vmid variable "
        "or a dedicated ID)."
    )
    return False


def test_bitwarden_delegates_to_localhost(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    provision_kvm = [
        t for t in kvm_tasks
        if "bitwarden" in t.get("name", "").lower()
    ]
    if not provision_kvm:
        print(
            "FAIL: No Bitwarden KVM task found to "
            "check delegate_to."
        )
        return False
    for task in provision_kvm:
        delegate = task.get("delegate_to", "")
        if str(delegate) != "localhost":
            name = task.get("name", "unnamed")
            print(
                f"FAIL: KVM task '{name}' missing "
                f"delegate_to: localhost (API module "
                f"must run on control node)."
            )
            return False
    print(
        "OK: Bitwarden VM task delegates to localhost."
    )
    return True


def test_vars_have_bitwarden_defaults(variables):
    required_vars = {
        "bitwarden_vmid": int,
        "bitwarden_memory": int,
        "bitwarden_clone_vmid": int,
    }
    all_ok = True
    for var_name, expected_type in required_vars.items():
        if var_name not in variables:
            print(
                f"FAIL: Missing '{var_name}' in all.yml."
            )
            all_ok = False
            continue
        val = variables[var_name]
        if not isinstance(val, expected_type):
            print(
                f"FAIL: '{var_name}' in all.yml has "
                f"wrong type (got "
                f"{type(val).__name__}, expected "
                f"{expected_type})."
            )
            all_ok = False
    if all_ok:
        print(
            "OK: all.yml has all Bitwarden VM variables "
            "(bitwarden_vmid, bitwarden_memory, "
            "bitwarden_clone_vmid)."
        )
    return all_ok


def test_bitwarden_memory_var_sufficient(variables):
    mem = variables.get("bitwarden_memory")
    if mem is None:
        print(
            "FAIL: Missing 'bitwarden_memory' in "
            "all.yml."
        )
        return False
    if not isinstance(mem, int):
        print(
            f"FAIL: 'bitwarden_memory' is not an int "
            f"(got {type(mem).__name__})."
        )
        return False
    if mem >= 4096:
        print(
            f"OK: bitwarden_memory in all.yml is "
            f"{mem}MB (>= 4096MB required)."
        )
        return True
    print(
        f"FAIL: bitwarden_memory in all.yml is "
        f"{mem}MB, must be >= 4096MB "
        f"(official on-premise requirement)."
    )
    return False


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Bitwarden VM task exists",
            lambda: test_bitwarden_vm_task_exists(tasks),
        ),
        (
            "Bitwarden VM clones from template",
            lambda: test_bitwarden_uses_clone(tasks),
        ),
        (
            "Bitwarden VM has sufficient RAM (>= 4GB)",
            lambda: test_bitwarden_has_sufficient_ram(
                tasks
            ),
        ),
        (
            "Bitwarden VM has Docker Compose cloud-init",
            lambda: test_bitwarden_has_docker_compose_cloudinit(
                tasks
            ),
        ),
        (
            "Bitwarden VM uses dedicated VMID",
            lambda: test_bitwarden_has_vmid(tasks),
        ),
        (
            "Bitwarden VM delegates to localhost",
            lambda: test_bitwarden_delegates_to_localhost(
                tasks
            ),
        ),
        (
            "Bitwarden vars in all.yml",
            lambda: test_vars_have_bitwarden_defaults(
                variables
            ),
        ),
        (
            "Bitwarden memory var >= 4096MB",
            lambda: test_bitwarden_memory_var_sufficient(
                variables
            ),
        ),
    ]

    results = []
    for label, check_fn in checks:
        passed = check_fn()
        results.append((label, passed))

    print()
    failed = [
        label for label, passed in results if not passed
    ]
    if failed:
        print(
            f"FAILED {len(failed)}/{len(results)} checks:"
        )
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    else:
        print(
            f"SUCCESS: All {len(results)} Bitwarden VM "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
