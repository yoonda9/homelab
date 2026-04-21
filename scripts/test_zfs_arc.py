import os
import re
import sys

import yaml

TASKS_PATH = "ansible/roles/pve_base/tasks/main.yml"
EXPECTED_DEST = "/etc/modprobe.d/zfs.conf"
EXPECTED_DEFAULT_BYTES = 2147483648  # 2 GB
EXPECTED_CONTENT_PATTERN = r"options zfs zfs_arc_max="


def load_tasks():
    if not os.path.exists(TASKS_PATH):
        print(f"FAIL: '{TASKS_PATH}' is missing.")
        sys.exit(1)
    with open(TASKS_PATH, "r") as f:
        return yaml.safe_load(f)


def flatten_tasks(task_list):
    for task in task_list:
        if not isinstance(task, dict):
            continue
        yield task
        for key in ("block", "tasks"):
            if key in task:
                yield from flatten_tasks(task[key])


def find_zfs_arc_task(tasks):
    for task in flatten_tasks(tasks):
        if "ZFS ARC" in task.get("name", ""):
            return task
    return None


def test_zfs_arc_task_exists(tasks):
    task = find_zfs_arc_task(tasks)
    if task is None:
        print("FAIL: No task with 'ZFS ARC' in its name found.")
        return False
    print(f"OK: Found ZFS ARC task: {task['name']}")
    return True


def test_uses_copy_module(tasks):
    task = find_zfs_arc_task(tasks)
    if task is None:
        return False
    if "ansible.builtin.copy" not in task:
        print(
            "FAIL: ZFS ARC task does not use ansible.builtin.copy. "
            f"Keys: {list(task.keys())}"
        )
        return False
    print("OK: ZFS ARC task uses ansible.builtin.copy module.")
    return True


def test_dest_is_modprobe_d(tasks):
    task = find_zfs_arc_task(tasks)
    if task is None:
        return False
    copy_params = task.get("ansible.builtin.copy", {})
    dest = copy_params.get("dest", "")
    if dest != EXPECTED_DEST:
        print(
            f"FAIL: ZFS ARC dest is '{dest}', "
            f"expected '{EXPECTED_DEST}'."
        )
        return False
    print(f"OK: ZFS ARC dest is '{EXPECTED_DEST}'.")
    return True


def test_content_format(tasks):
    task = find_zfs_arc_task(tasks)
    if task is None:
        return False
    copy_params = task.get("ansible.builtin.copy", {})
    content = copy_params.get("content", "")
    if not re.search(EXPECTED_CONTENT_PATTERN, content):
        print(
            f"FAIL: ZFS ARC content does not match expected format. "
            f"Got: '{content}'"
        )
        return False
    print(f"OK: ZFS ARC content matches 'options zfs zfs_arc_max=...' format.")
    return True


def test_default_value_is_2gb(tasks):
    task = find_zfs_arc_task(tasks)
    if task is None:
        return False
    copy_params = task.get("ansible.builtin.copy", {})
    content = copy_params.get("content", "")
    match = re.search(
        r"default\((\d+)\)", content
    )
    if not match:
        print(
            f"FAIL: Could not find default() value in ZFS ARC content. "
            f"Got: '{content}'"
        )
        return False
    default_val = int(match.group(1))
    if default_val != EXPECTED_DEFAULT_BYTES:
        print(
            f"FAIL: ZFS ARC default is {default_val} "
            f"({default_val / (1024**3):.1f} GB), "
            f"expected {EXPECTED_DEFAULT_BYTES} (2.0 GB)."
        )
        return False
    print(
        f"OK: ZFS ARC default is {EXPECTED_DEFAULT_BYTES} "
        f"(2.0 GB)."
    )
    return True


def test_notifies_initramfs(tasks):
    task = find_zfs_arc_task(tasks)
    if task is None:
        return False
    notify = task.get("notify", "")
    if "initramfs" not in str(notify).lower():
        print(
            f"FAIL: ZFS ARC task does not notify initramfs update. "
            f"Got notify: '{notify}'"
        )
        return False
    print("OK: ZFS ARC task notifies initramfs update.")
    return True


def main():
    tasks = load_tasks()
    checks = [
        ("Task exists", test_zfs_arc_task_exists),
        ("Uses copy module", test_uses_copy_module),
        ("Dest is /etc/modprobe.d/zfs.conf", test_dest_is_modprobe_d),
        ("Content format (options zfs zfs_arc_max=...)", test_content_format),
        ("Default value is 2GB (2147483648)", test_default_value_is_2gb),
        ("Notifies initramfs update", test_notifies_initramfs),
    ]

    results = []
    for label, check_fn in checks:
        passed = check_fn(tasks)
        results.append((label, passed))

    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(results)} ZFS ARC checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
