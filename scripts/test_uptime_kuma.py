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


def find_uptimekuma_task(tasks):
    lxc_tasks = find_tasks_by_module(tasks, LXC_MODULE)
    for task in lxc_tasks:
        name = task.get("name", "").lower()
        if "uptime" in name or "kuma" in name:
            return task
    return None


def find_copy_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        for mod in ("ansible.builtin.copy", "copy"):
            if mod in task:
                results.append(task)
                break
        for mod in ("ansible.builtin.template", "template"):
            if mod in task:
                results.append(task)
                break
    return results


def find_monitors_config_task(tasks):
    copy_tasks = find_copy_tasks(tasks)
    for task in copy_tasks:
        name = task.get("name", "").lower()
        if "uptime" in name or "kuma" in name or "monitor" in name:
            return task
    return None


def get_task_content(task):
    for mod in (
        "ansible.builtin.copy", "copy",
        "ansible.builtin.template", "template",
    ):
        if mod in task:
            params = task[mod]
            if isinstance(params, dict):
                return params.get("content", "")
    return ""


def test_uptimekuma_lxc_task_exists(tasks):
    task = find_uptimekuma_task(tasks)
    if task:
        print(
            f"OK: Uptime Kuma LXC task exists "
            f"(uses {LXC_MODULE})."
        )
        return True
    print(
        f"FAIL: No Uptime Kuma LXC task found using "
        f"'{LXC_MODULE}' with 'uptime' or 'kuma' "
        f"in task name."
    )
    return False


def test_uptimekuma_lightweight_resources(tasks):
    task = find_uptimekuma_task(tasks)
    if not task:
        print("FAIL: No Uptime Kuma task found.")
        return False
    params = task.get(LXC_MODULE, {})
    memory_str = str(params.get("memory", ""))
    import re
    default_match = re.search(
        r"default\((\d+)\)", memory_str
    )
    if default_match:
        mem_val = int(default_match.group(1))
    elif memory_str.isdigit():
        mem_val = int(memory_str)
    elif "uptimekuma_memory" in memory_str:
        print(
            "OK: Uptime Kuma LXC uses variable for "
            "memory (checked via all.yml)."
        )
        return True
    else:
        print(
            "FAIL: Uptime Kuma LXC missing 'memory' "
            "parameter."
        )
        return False
    if mem_val <= 1024:
        print(
            f"OK: Uptime Kuma LXC is lightweight "
            f"(memory={mem_val}MB <= 1024MB)."
        )
        return True
    print(
        f"FAIL: Uptime Kuma LXC memory {mem_val}MB "
        f"exceeds 1024MB (should be lightweight)."
    )
    return False


def test_uptimekuma_has_vmid(tasks):
    task = find_uptimekuma_task(tasks)
    if not task:
        print("FAIL: No Uptime Kuma task found.")
        return False
    params = task.get(LXC_MODULE, {})
    vmid = str(params.get("vmid", ""))
    if "uptimekuma_vmid" in vmid or vmid.isdigit():
        print(
            "OK: Uptime Kuma LXC uses a dedicated VMID."
        )
        return True
    print(
        "FAIL: Uptime Kuma LXC missing 'vmid' parameter."
    )
    return False


def test_uptimekuma_delegates_to_localhost(tasks):
    task = find_uptimekuma_task(tasks)
    if not task:
        print("FAIL: No Uptime Kuma task found.")
        return False
    delegate = task.get("delegate_to", "")
    if str(delegate) == "localhost":
        print(
            "OK: Uptime Kuma LXC delegates to localhost."
        )
        return True
    print(
        "FAIL: Uptime Kuma LXC missing "
        "delegate_to: localhost."
    )
    return False


def test_monitors_config_exists(tasks):
    config_task = find_monitors_config_task(tasks)
    if not config_task:
        print(
            "FAIL: No Uptime Kuma monitors config task "
            "found (expected copy/template task with "
            "'uptime', 'kuma', or 'monitor' in name)."
        )
        return False
    content = get_task_content(config_task)
    if not content:
        print(
            "FAIL: Monitors config task has no 'content' "
            "parameter."
        )
        return False
    services = ["plex", "bitwarden", "pihole"]
    found = []
    content_lower = content.lower()
    for svc in services:
        if svc in content_lower or svc.replace("-", "") in content_lower:
            found.append(svc)
    if len(found) >= 3:
        print(
            f"OK: Monitors config references all "
            f"services: {', '.join(found)}."
        )
        return True
    print(
        f"FAIL: Monitors config only references "
        f"{found} (need plex, bitwarden, pihole)."
    )
    return False


def test_notifications_disabled(tasks):
    config_task = find_monitors_config_task(tasks)
    if not config_task:
        print(
            "FAIL: No monitors config task found."
        )
        return False
    content = get_task_content(config_task)
    content_lower = content.lower()
    disabled_indicators = [
        '"notificationIDList": []' in content,
        "'notificationIDList': []" in content,
    ]
    if any(disabled_indicators):
        print(
            "OK: Notifications are disabled in "
            "monitors config."
        )
        return True
    print(
        "FAIL: Notifications not explicitly disabled "
        "in monitors config (expected "
        "'notificationIDList': [] or similar "
        "disabled indicator)."
    )
    return False


def test_vars_exist(variables):
    required_vars = {
        "uptimekuma_vmid": int,
        "uptimekuma_memory": int,
        "uptimekuma_disk": (int, str),
        "uptimekuma_storage": str,
        "uptimekuma_ostemplate": str,
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
            "OK: all.yml has all Uptime Kuma variables "
            "with correct types."
        )
    return all_ok


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Uptime Kuma LXC task exists",
            lambda: test_uptimekuma_lxc_task_exists(tasks),
        ),
        (
            "Uptime Kuma has lightweight resources",
            lambda: test_uptimekuma_lightweight_resources(
                tasks
            ),
        ),
        (
            "Uptime Kuma uses dedicated VMID",
            lambda: test_uptimekuma_has_vmid(tasks),
        ),
        (
            "Uptime Kuma delegates to localhost",
            lambda: test_uptimekuma_delegates_to_localhost(
                tasks
            ),
        ),
        (
            "Monitors config references all services",
            lambda: test_monitors_config_exists(tasks),
        ),
        (
            "Notifications disabled in config",
            lambda: test_notifications_disabled(tasks),
        ),
        (
            "Uptime Kuma vars in all.yml",
            lambda: test_vars_exist(variables),
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
            f"SUCCESS: All {len(results)} Uptime Kuma "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
