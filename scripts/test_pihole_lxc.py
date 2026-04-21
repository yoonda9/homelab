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


def find_pihole_task(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    for task in lxc_tasks:
        name = task.get("name", "").lower()
        if "pi-hole" in name or "pihole" in name:
            return task
    return None


def test_pihole_lxc_task_exists(tasks):
    task = find_pihole_task(tasks)
    if task:
        print(
            f"OK: Pi-hole LXC task exists "
            f"(uses {LXC_MODULE})."
        )
        return True
    print(
        f"FAIL: No Pi-hole LXC task found using "
        f"'{LXC_MODULE}' with 'pi-hole' or 'pihole' "
        f"in task name."
    )
    return False


def test_pihole_has_minimal_memory(tasks):
    task = find_pihole_task(tasks)
    if not task:
        print("FAIL: No Pi-hole task found.")
        return False
    params = task.get(LXC_MODULE, {})
    memory_str = str(params.get("memory", ""))
    if not memory_str:
        print(
            "FAIL: Pi-hole LXC task missing 'memory' "
            "parameter."
        )
        return False
    import re
    default_match = re.search(
        r"default\((\d+)\)", memory_str
    )
    if default_match:
        default_val = int(default_match.group(1))
        if default_val <= 512:
            print(
                f"OK: Pi-hole LXC has minimal memory "
                f"(default {default_val}MB <= 512MB)."
            )
            return True
        print(
            f"FAIL: Pi-hole LXC memory default "
            f"{default_val}MB exceeds 512MB "
            f"(should be minimal)."
        )
        return False
    try:
        memory_val = int(memory_str)
        if memory_val <= 512:
            print(
                f"OK: Pi-hole LXC has minimal memory "
                f"({memory_val}MB <= 512MB)."
            )
            return True
        print(
            f"FAIL: Pi-hole LXC memory {memory_val}MB "
            f"exceeds 512MB (should be minimal)."
        )
        return False
    except ValueError:
        pass
    print(
        "FAIL: Pi-hole LXC task missing 'memory' "
        "parameter (expected <= 512MB or pihole_memory "
        "variable with default <= 512)."
    )
    return False


def test_pihole_has_minimal_disk(tasks):
    task = find_pihole_task(tasks)
    if not task:
        print("FAIL: No Pi-hole task found.")
        return False
    params = task.get(LXC_MODULE, {})
    disk_str = str(params.get("disk", ""))
    if "pihole_disk" in disk_str:
        print(
            "OK: Pi-hole LXC uses pihole_disk variable."
        )
        return True
    try:
        disk_val = int(disk_str)
        if disk_val <= 8:
            print(
                f"OK: Pi-hole LXC has minimal disk "
                f"({disk_val}GB <= 8GB)."
            )
            return True
        print(
            f"FAIL: Pi-hole LXC disk {disk_val}GB "
            f"exceeds 8GB (should be minimal)."
        )
        return False
    except ValueError:
        pass
    print(
        "FAIL: Pi-hole LXC task missing 'disk' "
        "parameter (expected <= 8GB or pihole_disk "
        "variable)."
    )
    return False


def test_pihole_has_vmid(tasks):
    task = find_pihole_task(tasks)
    if not task:
        print("FAIL: No Pi-hole task found.")
        return False
    params = task.get(LXC_MODULE, {})
    vmid = str(params.get("vmid", ""))
    if "pihole_vmid" in vmid or vmid.isdigit():
        print(
            "OK: Pi-hole LXC task uses a dedicated VMID."
        )
        return True
    print(
        "FAIL: Pi-hole LXC task missing 'vmid' parameter "
        "(must use pihole_vmid variable or a dedicated ID)."
    )
    return False


def test_pihole_has_dns_config(tasks):
    task = find_pihole_task(tasks)
    if not task:
        print("FAIL: No Pi-hole task found.")
        return False
    params = task.get(LXC_MODULE, {})
    if "nameserver" in params:
        ns_val = str(params["nameserver"])
        if "pihole_dns" in ns_val or ns_val.strip():
            print(
                "OK: Pi-hole LXC has 'nameserver' "
                "parameter in module params."
            )
            return True
    print(
        "FAIL: Pi-hole LXC missing 'nameserver' key in "
        "module parameters. The nameserver parameter must "
        "be set directly on the community.proxmox.proxmox "
        "module (not just referenced in description)."
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


def test_pihole_has_ostemplate(tasks):
    task = find_pihole_task(tasks)
    if not task:
        print("FAIL: No Pi-hole task found.")
        return False
    params = task.get(LXC_MODULE, {})
    ostemplate = str(params.get("ostemplate", ""))
    if "pihole_ostemplate" in ostemplate or ostemplate:
        print(
            "OK: Pi-hole LXC has ostemplate configured."
        )
        return True
    print(
        "FAIL: Pi-hole LXC task missing 'ostemplate' "
        "parameter."
    )
    return False


def test_vars_have_pihole_defaults(variables):
    required_vars = {
        "pihole_vmid": int,
        "pihole_memory": int,
        "pihole_disk": (int, str),
        "pihole_storage": str,
        "pihole_ostemplate": str,
        "pihole_dns_upstream": (str, list),
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
            "OK: all.yml has all Pi-hole LXC variables "
            "(pihole_vmid, pihole_memory, pihole_disk, "
            "pihole_storage, pihole_ostemplate, "
            "pihole_dns_upstream)."
        )
    return all_ok


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Pi-hole LXC task exists",
            lambda: test_pihole_lxc_task_exists(tasks),
        ),
        (
            "Pi-hole has minimal memory (<=512MB)",
            lambda: test_pihole_has_minimal_memory(tasks),
        ),
        (
            "Pi-hole has minimal disk (<=8GB)",
            lambda: test_pihole_has_minimal_disk(tasks),
        ),
        (
            "Pi-hole uses dedicated VMID",
            lambda: test_pihole_has_vmid(tasks),
        ),
        (
            "Pi-hole has DNS config reference",
            lambda: test_pihole_has_dns_config(tasks),
        ),
        (
            "Pi-hole has ostemplate configured",
            lambda: test_pihole_has_ostemplate(tasks),
        ),
        (
            "All LXC tasks delegate to localhost",
            lambda: test_delegate_to_localhost(tasks),
        ),
        (
            "Pi-hole vars in all.yml",
            lambda: test_vars_have_pihole_defaults(
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
            f"SUCCESS: All {len(results)} Pi-hole LXC "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
