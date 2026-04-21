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
ZONE_MODULE = "community.proxmox.proxmox_zone"
VNET_MODULE = "community.proxmox.proxmox_vnet"
EXPECTED_ZONE_NAME = "dmz"
EXPECTED_ZONE_TYPE = "simple"
EXPECTED_VNET_NAME = "vnet-dmz"


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


def test_zone_task_exists(tasks):
    zone_tasks = find_tasks_by_module(tasks, ZONE_MODULE)
    if not zone_tasks:
        print(
            f"FAIL: No task using '{ZONE_MODULE}' module found."
        )
        return False
    print(
        f"OK: Found {len(zone_tasks)} task(s) using "
        f"'{ZONE_MODULE}'."
    )
    return True


def test_zone_type_is_simple(tasks):
    zone_tasks = find_tasks_by_module(tasks, ZONE_MODULE)
    if not zone_tasks:
        return False
    for task in zone_tasks:
        params = task.get(ZONE_MODULE, {})
        zone_type = params.get("type", "")
        if zone_type == EXPECTED_ZONE_TYPE:
            print(
                f"OK: Zone type is '{EXPECTED_ZONE_TYPE}'."
            )
            return True
    print(
        f"FAIL: No zone task sets type to "
        f"'{EXPECTED_ZONE_TYPE}'. Found types: "
        f"{[t.get(ZONE_MODULE, {}).get('type', '') for t in zone_tasks]}"
    )
    return False


def test_zone_name(tasks):
    zone_tasks = find_tasks_by_module(tasks, ZONE_MODULE)
    if not zone_tasks:
        return False
    for task in zone_tasks:
        params = task.get(ZONE_MODULE, {})
        name = str(params.get("zone", ""))
        if name == EXPECTED_ZONE_NAME:
            print(
                f"OK: Zone name is '{EXPECTED_ZONE_NAME}'."
            )
            return True
        if "pve_sdn_zone_name" in name:
            default_match = re.search(
                r"default\(['\"]?([^'\")\s]+)['\"]?\)",
                name,
            )
            if default_match:
                default_val = default_match.group(1)
                if default_val != EXPECTED_ZONE_NAME:
                    print(
                        f"FAIL: Zone name default is "
                        f"'{default_val}', expected "
                        f"'{EXPECTED_ZONE_NAME}'."
                    )
                    return False
            print(
                f"OK: Zone task uses variable with "
                f"default '{EXPECTED_ZONE_NAME}'."
            )
            return True
    print(
        f"FAIL: No zone task sets zone to "
        f"'{EXPECTED_ZONE_NAME}' or uses "
        f"pve_sdn_zone_name variable."
    )
    return False


def test_vnet_task_exists(tasks):
    vnet_tasks = find_tasks_by_module(tasks, VNET_MODULE)
    if not vnet_tasks:
        print(
            f"FAIL: No task using '{VNET_MODULE}' module found."
        )
        return False
    print(
        f"OK: Found {len(vnet_tasks)} task(s) using "
        f"'{VNET_MODULE}'."
    )
    return True


def test_vnet_name(tasks):
    vnet_tasks = find_tasks_by_module(tasks, VNET_MODULE)
    if not vnet_tasks:
        return False
    for task in vnet_tasks:
        params = task.get(VNET_MODULE, {})
        name = str(params.get("vnet", ""))
        if name == EXPECTED_VNET_NAME:
            print(
                f"OK: Vnet name is '{EXPECTED_VNET_NAME}'."
            )
            return True
        if "pve_sdn_vnet_name" in name:
            default_match = re.search(
                r"default\(['\"]?([^'\")\s]+)['\"]?\)",
                name,
            )
            if default_match:
                default_val = default_match.group(1)
                if default_val != EXPECTED_VNET_NAME:
                    print(
                        f"FAIL: Vnet name default is "
                        f"'{default_val}', expected "
                        f"'{EXPECTED_VNET_NAME}'."
                    )
                    return False
            print(
                f"OK: Vnet task uses variable with "
                f"default '{EXPECTED_VNET_NAME}'."
            )
            return True
    print(
        f"FAIL: No vnet task sets vnet to "
        f"'{EXPECTED_VNET_NAME}' or uses "
        f"pve_sdn_vnet_name variable."
    )
    return False


def test_vnet_references_zone(tasks):
    vnet_tasks = find_tasks_by_module(tasks, VNET_MODULE)
    if not vnet_tasks:
        return False
    for task in vnet_tasks:
        params = task.get(VNET_MODULE, {})
        zone = str(params.get("zone", ""))
        if (
            zone == EXPECTED_ZONE_NAME
            or "pve_sdn_zone_name" in zone
        ):
            print(
                "OK: Vnet task references the SDN zone."
            )
            return True
    print(
        "FAIL: No vnet task references the zone "
        f"'{EXPECTED_ZONE_NAME}' or pve_sdn_zone_name."
    )
    return False


def test_sdn_tasks_delegate_to_localhost(tasks):
    sdn_tasks = find_tasks_by_module(
        tasks, ZONE_MODULE
    ) + find_tasks_by_module(tasks, VNET_MODULE)
    if not sdn_tasks:
        return False
    missing = []
    for task in sdn_tasks:
        task_name = task.get("name", "<unnamed>")
        if task.get("delegate_to") != "localhost":
            missing.append(task_name)
    if missing:
        print(
            f"FAIL: SDN tasks missing delegate_to: "
            f"localhost: {', '.join(missing)}"
        )
        return False
    print(
        "OK: All SDN tasks delegate to localhost."
    )
    return True


def test_sdn_tag_not_defined_in_all_yml(variables):
    if "pve_sdn_tag" in variables:
        print(
            "FAIL: pve_sdn_tag must NOT be defined in "
            "all.yml (breaks default(omit) in task). "
            "Set it in host_vars or extra-vars when needed."
        )
        return False
    print(
        "OK: pve_sdn_tag is not defined in all.yml "
        "(default(omit) will work correctly)."
    )
    return True


def test_sdn_vars_in_all_yml(variables):
    required_vars = [
        "pve_sdn_zone_name",
        "pve_sdn_vnet_name",
    ]
    missing = []
    for var in required_vars:
        if var not in variables:
            missing.append(var)
    if missing:
        print(
            f"FAIL: Missing SDN variables in all.yml: "
            f"{', '.join(missing)}"
        )
        return False
    zone_name = variables.get("pve_sdn_zone_name", "")
    if zone_name != EXPECTED_ZONE_NAME:
        print(
            f"FAIL: pve_sdn_zone_name default is "
            f"'{zone_name}', expected "
            f"'{EXPECTED_ZONE_NAME}'."
        )
        return False
    vnet_name = variables.get("pve_sdn_vnet_name", "")
    if vnet_name != EXPECTED_VNET_NAME:
        print(
            f"FAIL: pve_sdn_vnet_name default is "
            f"'{vnet_name}', expected "
            f"'{EXPECTED_VNET_NAME}'."
        )
        return False
    print(
        f"OK: all.yml has SDN variables with "
        f"pve_sdn_zone_name='{EXPECTED_ZONE_NAME}', "
        f"pve_sdn_vnet_name='{EXPECTED_VNET_NAME}'."
    )
    return True


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Zone task exists",
            lambda: test_zone_task_exists(tasks),
        ),
        (
            "Zone type is simple",
            lambda: test_zone_type_is_simple(tasks),
        ),
        (
            "Zone name is dmz",
            lambda: test_zone_name(tasks),
        ),
        (
            "Vnet task exists",
            lambda: test_vnet_task_exists(tasks),
        ),
        (
            "Vnet name is vnet-dmz",
            lambda: test_vnet_name(tasks),
        ),
        (
            "Vnet references zone",
            lambda: test_vnet_references_zone(tasks),
        ),
        (
            "SDN tasks delegate to localhost",
            lambda: test_sdn_tasks_delegate_to_localhost(
                tasks
            ),
        ),
        (
            "SDN vars in all.yml",
            lambda: test_sdn_vars_in_all_yml(variables),
        ),
        (
            "pve_sdn_tag not defined in all.yml",
            lambda: test_sdn_tag_not_defined_in_all_yml(
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
            f"SUCCESS: All {len(results)} SDN checks "
            f"passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
