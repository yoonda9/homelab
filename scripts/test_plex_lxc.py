import os
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/pve_provision/tasks/main.yml"
)
VARS_PATH = os.environ.get(
    "VARS_PATH", "ansible/group_vars/all.yml"
)
LXC_MODULE = "community.proxmox.proxmox"


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


def test_plex_lxc_task_exists(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    for task in lxc_tasks:
        name = task.get("name", "").lower()
        if "plex" in name:
            print(
                f"OK: Plex LXC task exists "
                f"(uses {LXC_MODULE})."
            )
            return True
    print(
        f"FAIL: No Plex LXC task found using "
        f"'{LXC_MODULE}' with 'plex' in task name."
    )
    return False


def test_plex_uses_vmid(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    for task in lxc_tasks:
        name = task.get("name", "").lower()
        if "plex" not in name:
            continue
        params = task.get(LXC_MODULE, {})
        vmid = str(params.get("vmid", ""))
        if "plex_vmid" in vmid or vmid.isdigit():
            print(
                "OK: Plex LXC task uses a dedicated VMID."
            )
            return True
    print(
        "FAIL: Plex LXC task missing 'vmid' parameter "
        "(must use plex_vmid variable or a dedicated ID)."
    )
    return False


def test_plex_has_igpu_passthrough(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    for task in lxc_tasks:
        name = task.get("name", "").lower()
        if "plex" not in name:
            continue
        params = task.get(LXC_MODULE, {})
        task_str = str(params)
        if "/dev/dri" in task_str:
            print(
                "OK: Plex LXC has iGPU passthrough "
                "(/dev/dri mount point found)."
            )
            return True
    print(
        "FAIL: Plex LXC missing iGPU passthrough. "
        "Expected '/dev/dri' device mount in task "
        "parameters (e.g., mp0 or features with mount)."
    )
    return False


def test_plex_has_memory(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    for task in lxc_tasks:
        name = task.get("name", "").lower()
        if "plex" not in name:
            continue
        params = task.get(LXC_MODULE, {})
        memory = str(params.get("memory", ""))
        if "plex_memory" in memory or memory.isdigit():
            print(
                "OK: Plex LXC has memory configured."
            )
            return True
    print(
        "FAIL: Plex LXC task missing 'memory' parameter."
    )
    return False


def test_plex_has_disk(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    for task in lxc_tasks:
        name = task.get("name", "").lower()
        if "plex" not in name:
            continue
        params = task.get(LXC_MODULE, {})
        disk = str(params.get("disk", ""))
        if "plex_disk" in disk or disk.isdigit():
            print(
                "OK: Plex LXC has disk size configured."
            )
            return True
    print(
        "FAIL: Plex LXC task missing 'disk' parameter."
    )
    return False


def test_plex_has_ostemplate(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    for task in lxc_tasks:
        name = task.get("name", "").lower()
        if "plex" not in name:
            continue
        params = task.get(LXC_MODULE, {})
        ostemplate = str(params.get("ostemplate", ""))
        if "plex_ostemplate" in ostemplate or ostemplate:
            print(
                "OK: Plex LXC has ostemplate configured."
            )
            return True
    print(
        "FAIL: Plex LXC task missing 'ostemplate' "
        "parameter."
    )
    return False


def test_delegate_to_localhost(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    if not lxc_tasks:
        print(
            f"FAIL: No {LXC_MODULE} tasks found to "
            f"check delegate_to."
        )
        return False
    for task in lxc_tasks:
        delegate = task.get("delegate_to", "")
        if str(delegate) != "localhost":
            name = task.get("name", "unnamed")
            print(
                f"FAIL: LXC task '{name}' missing "
                f"delegate_to: localhost (API module must "
                f"run on control node)."
            )
            return False
    print(
        f"OK: All {LXC_MODULE} tasks delegate to "
        f"localhost."
    )
    return True


def test_vars_have_plex_defaults(variables):
    required_vars = {
        "plex_vmid": int,
        "plex_memory": int,
        "plex_disk": (int, str),
        "plex_storage": str,
        "plex_ostemplate": str,
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
                f"FAIL: '{var_name}' in all.yml has wrong "
                f"type (got {type(val).__name__}, expected "
                f"{expected_type})."
            )
            all_ok = False
    if all_ok:
        print(
            "OK: all.yml has all Plex LXC variables "
            "(plex_vmid, plex_memory, plex_disk, "
            "plex_storage, plex_ostemplate)."
        )
    return all_ok


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Plex LXC task exists",
            lambda: test_plex_lxc_task_exists(tasks),
        ),
        (
            "Plex uses dedicated VMID",
            lambda: test_plex_uses_vmid(tasks),
        ),
        (
            "Plex has iGPU passthrough (/dev/dri)",
            lambda: test_plex_has_igpu_passthrough(tasks),
        ),
        (
            "Plex has memory configured",
            lambda: test_plex_has_memory(tasks),
        ),
        (
            "Plex has disk configured",
            lambda: test_plex_has_disk(tasks),
        ),
        (
            "Plex has ostemplate configured",
            lambda: test_plex_has_ostemplate(tasks),
        ),
        (
            "All LXC tasks delegate to localhost",
            lambda: test_delegate_to_localhost(tasks),
        ),
        (
            "Plex vars in all.yml",
            lambda: test_vars_have_plex_defaults(variables),
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
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    else:
        print(
            f"SUCCESS: All {len(results)} Plex LXC "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
