import os
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/docker_host/tasks/main.yml"
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


def find_docker_task(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    for task in kvm_tasks:
        name = task.get("name", "").lower()
        if "docker" in name:
            return task
    return None


def test_docker_vm_task_exists(tasks):
    task = find_docker_task(tasks)
    if task:
        print(
            f"OK: Docker VM task exists "
            f"(uses {KVM_MODULE})."
        )
        return True
    print(
        f"FAIL: No Docker VM task found using "
        f"'{KVM_MODULE}' with 'docker' in task name."
    )
    return False


def test_docker_uses_clone(tasks):
    task = find_docker_task(tasks)
    if not task:
        print("FAIL: No Docker task found.")
        return False
    params = task.get(KVM_MODULE, {})
    if "clone" in params:
        print(
            "OK: Docker VM clones from a template."
        )
        return True
    print(
        "FAIL: Docker VM task missing 'clone' "
        "parameter (must clone from cloud template)."
    )
    return False


def test_docker_has_vmid(tasks):
    task = find_docker_task(tasks)
    if not task:
        print("FAIL: No Docker task found.")
        return False
    params = task.get(KVM_MODULE, {})
    vmid = str(params.get("vmid", ""))
    if "docker_vmid" in vmid or vmid.isdigit():
        print(
            "OK: Docker VM uses a dedicated VMID."
        )
        return True
    print(
        "FAIL: Docker VM task missing 'vmid' parameter "
        "(must use docker_vmid variable or a dedicated "
        "ID)."
    )
    return False


def test_docker_delegates_to_localhost(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    provision_kvm = [
        t for t in kvm_tasks
        if "docker" in t.get("name", "").lower()
    ]
    if not provision_kvm:
        print(
            "FAIL: No Docker KVM task found to "
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
        "OK: Docker VM task delegates to localhost."
    )
    return True


def test_vars_have_docker_defaults(variables):
    required_vars = {
        "docker_vmid": int,
        "docker_memory": int,
        "docker_clone_vmid": int,
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
            "OK: all.yml has all Docker VM variables "
            "(docker_vmid, docker_memory, "
            "docker_clone_vmid)."
        )
    return all_ok


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Docker VM task exists",
            lambda: test_docker_vm_task_exists(tasks),
        ),
        (
            "Docker VM clones from template",
            lambda: test_docker_uses_clone(tasks),
        ),
        (
            "Docker VM uses dedicated VMID",
            lambda: test_docker_has_vmid(tasks),
        ),
        (
            "Docker VM delegates to localhost",
            lambda: test_docker_delegates_to_localhost(
                tasks
            ),
        ),
        (
            "Docker vars in all.yml",
            lambda: test_vars_have_docker_defaults(
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
            f"SUCCESS: All {len(results)} Docker VM "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
