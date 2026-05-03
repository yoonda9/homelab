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
TEMPLATE_MODULE = "community.proxmox.proxmox_template"
EXPECTED_STORAGE = "local"


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


def find_template_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        if TEMPLATE_MODULE in task:
            results.append(task)
    return results


def test_lxc_template_task_exists(tasks):
    template_tasks = find_template_tasks(tasks)
    lxc_tasks = []
    for task in template_tasks:
        params = task.get(TEMPLATE_MODULE, {})
        content_type = str(params.get("content_type", ""))
        if content_type == "vztmpl":
            lxc_tasks.append(task)
    if not lxc_tasks:
        print(
            f"FAIL: No task using '{TEMPLATE_MODULE}' with "
            f"content_type 'vztmpl' found for LXC templates."
        )
        return False
    print(
        f"OK: Found {len(lxc_tasks)} LXC template task(s) "
        f"using '{TEMPLATE_MODULE}'."
    )
    return True


def test_iso_download_task_exists(tasks):
    template_tasks = find_template_tasks(tasks)
    iso_tasks = []
    for task in template_tasks:
        params = task.get(TEMPLATE_MODULE, {})
        content_type = str(params.get("content_type", ""))
        if content_type == "iso":
            iso_tasks.append(task)
    if not iso_tasks:
        print(
            f"FAIL: No task using '{TEMPLATE_MODULE}' with "
            f"content_type 'iso' found for ISO downloads."
        )
        return False
    print(
        f"OK: Found {len(iso_tasks)} ISO download task(s) "
        f"using '{TEMPLATE_MODULE}'."
    )
    return True


def test_lxc_storage_target(tasks):
    template_tasks = find_template_tasks(tasks)
    for task in template_tasks:
        params = task.get(TEMPLATE_MODULE, {})
        content_type = str(params.get("content_type", ""))
        if content_type != "vztmpl":
            continue
        storage = str(params.get("storage", ""))
        if storage == EXPECTED_STORAGE:
            print(
                f"OK: LXC template task targets storage "
                f"'{EXPECTED_STORAGE}'."
            )
            return True
        if "pve_storage" in storage:
            default_match = re.search(
                r"default\(['\"]?(\w+)['\"]?\)", storage
            )
            if default_match:
                default_val = default_match.group(1)
                if default_val != EXPECTED_STORAGE:
                    print(
                        f"FAIL: LXC template storage default is "
                        f"'{default_val}', expected "
                        f"'{EXPECTED_STORAGE}'."
                    )
                    return False
            print(
                f"OK: LXC template task uses pve_storage "
                f"variable with default '{EXPECTED_STORAGE}'."
            )
            return True
    print(
        f"FAIL: No LXC template task targets storage "
        f"'{EXPECTED_STORAGE}' or uses pve_storage variable."
    )
    return False


def test_iso_storage_target(tasks):
    template_tasks = find_template_tasks(tasks)
    for task in template_tasks:
        params = task.get(TEMPLATE_MODULE, {})
        content_type = str(params.get("content_type", ""))
        if content_type != "iso":
            continue
        storage = str(params.get("storage", ""))
        if storage == EXPECTED_STORAGE:
            print(
                f"OK: ISO download task targets storage "
                f"'{EXPECTED_STORAGE}'."
            )
            return True
        if "pve_storage" in storage:
            default_match = re.search(
                r"default\(['\"]?(\w+)['\"]?\)", storage
            )
            if default_match:
                default_val = default_match.group(1)
                if default_val != EXPECTED_STORAGE:
                    print(
                        f"FAIL: ISO download storage default is "
                        f"'{default_val}', expected "
                        f"'{EXPECTED_STORAGE}'."
                    )
                    return False
            print(
                f"OK: ISO download task uses pve_storage "
                f"variable with default '{EXPECTED_STORAGE}'."
            )
            return True
    print(
        f"FAIL: No ISO download task targets storage "
        f"'{EXPECTED_STORAGE}' or uses pve_storage variable."
    )
    return False


def test_lxc_loops_over_template_list(tasks):
    template_tasks = find_template_tasks(tasks)
    for task in template_tasks:
        params = task.get(TEMPLATE_MODULE, {})
        content_type = str(params.get("content_type", ""))
        if content_type != "vztmpl":
            continue
        loop_expr = task.get("loop") or task.get("with_items")
        if loop_expr and "pve_lxc_templates" in str(loop_expr):
            print(
                "OK: LXC template task loops over "
                "pve_lxc_templates."
            )
            return True
    print(
        "FAIL: No LXC template task loops over "
        "pve_lxc_templates variable."
    )
    return False


def test_iso_loops_over_url_list(tasks):
    template_tasks = find_template_tasks(tasks)
    for task in template_tasks:
        params = task.get(TEMPLATE_MODULE, {})
        content_type = str(params.get("content_type", ""))
        if content_type != "iso":
            continue
        loop_expr = task.get("loop") or task.get("with_items")
        if loop_expr and "pve_iso_urls" in str(loop_expr):
            print(
                "OK: ISO download task loops over "
                "pve_iso_urls."
            )
            return True
    print(
        "FAIL: No ISO download task loops over "
        "pve_iso_urls variable."
    )
    return False


def test_pve_cloud_images_includes_fedora(variables):
    images = variables.get("pve_cloud_images") or []
    expected_vmid = 9003
    for img in images:
        if not isinstance(img, dict):
            continue
        name = str(img.get("name", ""))
        if name.lower().startswith("fedora") and img.get("vmid") == expected_vmid:
            print(
                f"OK: pve_cloud_images contains fedora entry "
                f"'{name}' with vmid {expected_vmid}."
            )
            return True
    print(
        f"FAIL: pve_cloud_images is missing a fedora entry "
        f"(name starting with 'fedora' AND vmid == {expected_vmid}). "
        f"Add a Fedora Cloud Base entry to "
        f"ansible/group_vars/all.yml."
    )
    return False


def test_vars_have_image_sync_defaults(variables):
    required_vars = {
        "pve_storage": EXPECTED_STORAGE,
    }
    list_vars = ["pve_lxc_templates", "pve_iso_urls"]

    for var, expected_val in required_vars.items():
        if var not in variables:
            print(
                f"FAIL: Missing '{var}' in all.yml."
            )
            return False
        actual_val = variables[var]
        if str(actual_val) != str(expected_val):
            print(
                f"FAIL: '{var}' is '{actual_val}', "
                f"expected '{expected_val}'."
            )
            return False

    for var in list_vars:
        if var not in variables:
            print(
                f"FAIL: Missing '{var}' list in all.yml."
            )
            return False
        val = variables[var]
        if not isinstance(val, list) or len(val) == 0:
            print(
                f"FAIL: '{var}' must be a non-empty list "
                f"in all.yml."
            )
            return False

    print(
        f"OK: all.yml has pve_storage='{EXPECTED_STORAGE}', "
        f"pve_lxc_templates list, and pve_iso_urls list."
    )
    return True


def test_delegate_to_localhost(tasks):
    template_tasks = find_template_tasks(tasks)
    if not template_tasks:
        print(
            "FAIL: No template tasks found to check "
            "delegate_to."
        )
        return False
    for task in template_tasks:
        delegate = task.get("delegate_to", "")
        if str(delegate) != "localhost":
            name = task.get("name", "unnamed")
            print(
                f"FAIL: Template task '{name}' missing "
                f"delegate_to: localhost (API module must "
                f"run on control node)."
            )
            return False
    print(
        "OK: All template tasks delegate to localhost."
    )
    return True


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "LXC template task exists",
            lambda: test_lxc_template_task_exists(tasks),
        ),
        (
            "ISO download task exists",
            lambda: test_iso_download_task_exists(tasks),
        ),
        (
            "LXC storage target is 'local'",
            lambda: test_lxc_storage_target(tasks),
        ),
        (
            "ISO storage target is 'local'",
            lambda: test_iso_storage_target(tasks),
        ),
        (
            "LXC task loops over pve_lxc_templates",
            lambda: test_lxc_loops_over_template_list(tasks),
        ),
        (
            "ISO task loops over pve_iso_urls",
            lambda: test_iso_loops_over_url_list(tasks),
        ),
        (
            "Image sync vars in all.yml",
            lambda: test_vars_have_image_sync_defaults(
                variables
            ),
        ),
        (
            "All template tasks delegate to localhost",
            lambda: test_delegate_to_localhost(tasks),
        ),
        (
            "pve_cloud_images includes fedora (vmid 9003)",
            lambda: test_pve_cloud_images_includes_fedora(
                variables
            ),
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
        print(
            f"SUCCESS: All {len(results)} image sync "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
