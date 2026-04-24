import os
import re
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/pve_base/tasks/main.yml"
)
VARS_PATH = os.environ.get(
    "VARS_PATH", "ansible/group_vars/all.yml"
)
EXPECTED_MODULE = "community.proxmox.proxmox_node_network"
EXPECTED_BRIDGE_NAME = "vmbr0"
EXPECTED_TYPE = "bridge"


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


def find_bridge_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        if EXPECTED_MODULE in task:
            results.append(task)
    return results


def test_bridge_task_exists(tasks):
    bridge_tasks = find_bridge_tasks(tasks)
    if not bridge_tasks:
        print(
            f"FAIL: No task using '{EXPECTED_MODULE}' module found."
        )
        return False
    print(
        f"OK: Found {len(bridge_tasks)} task(s) using "
        f"'{EXPECTED_MODULE}'."
    )
    return True


def test_bridge_name(tasks):
    bridge_tasks = find_bridge_tasks(tasks)
    if not bridge_tasks:
        return False
    for task in bridge_tasks:
        params = task.get(EXPECTED_MODULE, {})
        name = params.get("iface", "")
        name_str = str(name)
        if name_str == EXPECTED_BRIDGE_NAME:
            print(
                f"OK: Bridge task uses iface '{name}'."
            )
            return True
        if "pve_bridge_name" in name_str:
            default_match = re.search(
                r"default\(['\"]?(\w+)['\"]?\)", name_str
            )
            if default_match:
                default_val = default_match.group(1)
                if default_val != EXPECTED_BRIDGE_NAME:
                    print(
                        f"FAIL: Bridge name default is "
                        f"'{default_val}', expected "
                        f"'{EXPECTED_BRIDGE_NAME}'."
                    )
                    return False
            print(
                f"OK: Bridge task uses variable with "
                f"default '{EXPECTED_BRIDGE_NAME}'."
            )
            return True
    print(
        f"FAIL: No bridge task sets iface to "
        f"'{EXPECTED_BRIDGE_NAME}' or uses "
        f"pve_bridge_name variable."
    )
    return False


def test_bridge_type(tasks):
    bridge_tasks = find_bridge_tasks(tasks)
    if not bridge_tasks:
        return False
    for task in bridge_tasks:
        params = task.get(EXPECTED_MODULE, {})
        iface_type = params.get("iface_type", "")
        if iface_type == EXPECTED_TYPE:
            print(f"OK: Bridge task type is '{EXPECTED_TYPE}'.")
            return True
    print(
        f"FAIL: No bridge task sets iface_type to '{EXPECTED_TYPE}'. "
        f"Found types: "
        f"{[t.get(EXPECTED_MODULE, {}).get('iface_type', '') for t in bridge_tasks]}"
    )
    return False


def test_autostart_enabled(tasks):
    bridge_tasks = find_bridge_tasks(tasks)
    if not bridge_tasks:
        return False
    for task in bridge_tasks:
        params = task.get(EXPECTED_MODULE, {})
        autostart = params.get("autostart")
        if autostart is True:
            print("OK: Bridge task has autostart enabled.")
            return True
    print(
        "FAIL: No bridge task has autostart: true."
    )
    return False


def test_state_present(tasks):
    bridge_tasks = find_bridge_tasks(tasks)
    if not bridge_tasks:
        return False
    for task in bridge_tasks:
        params = task.get(EXPECTED_MODULE, {})
        state = params.get("state", "")
        if state == "present":
            print("OK: Bridge task state is 'present'.")
            return True
    print(
        "FAIL: No bridge task sets state to 'present'."
    )
    return False


def test_apply_task_exists(tasks):
    bridge_tasks = find_bridge_tasks(tasks)
    if not bridge_tasks:
        return False
    for task in bridge_tasks:
        params = task.get(EXPECTED_MODULE, {})
        state = params.get("state", "")
        if state == "apply":
            print(
                "OK: Found network apply task "
                "(state: apply)."
            )
            return True
    print(
        "FAIL: No task with state 'apply' found. "
        "Network changes must be explicitly applied."
    )
    return False


def test_vars_have_bridge_defaults(variables):
    required_vars = [
        "pve_bridge_name",
        "pve_bridge_ports",
        "pve_bridge_cidr",
    ]
    missing = []
    for var in required_vars:
        if var not in variables:
            missing.append(var)
    if missing:
        print(
            f"FAIL: Missing bridge variables in all.yml: "
            f"{', '.join(missing)}"
        )
        return False
    name = variables.get("pve_bridge_name", "")
    if name != EXPECTED_BRIDGE_NAME:
        print(
            f"FAIL: pve_bridge_name default is '{name}', "
            f"expected '{EXPECTED_BRIDGE_NAME}'."
        )
        return False
    print(
        f"OK: all.yml has bridge variables with "
        f"pve_bridge_name='{EXPECTED_BRIDGE_NAME}'."
    )
    return True


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        ("Bridge task exists", lambda: test_bridge_task_exists(tasks)),
        ("Bridge name is vmbr0", lambda: test_bridge_name(tasks)),
        ("Bridge type is 'bridge'", lambda: test_bridge_type(tasks)),
        ("Autostart enabled", lambda: test_autostart_enabled(tasks)),
        ("State is present", lambda: test_state_present(tasks)),
        ("Apply task exists", lambda: test_apply_task_exists(tasks)),
        (
            "Bridge vars in all.yml",
            lambda: test_vars_have_bridge_defaults(variables),
        ),
    ]

    results = []
    for label, check_fn in checks:
        passed = check_fn()
        results.append((label, passed))

    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(results)} bridge checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
