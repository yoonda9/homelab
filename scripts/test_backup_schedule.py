import os
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/pve_base/tasks/main.yml"
)
VARS_PATH = os.environ.get(
    "VARS_PATH", "ansible/group_vars/all.yml"
)


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


def find_backup_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        name = task.get("name", "").lower()
        if "backup" in name and "vzdump" in name:
            results.append(task)
    return results


def find_backup_block(tasks):
    for task in flatten_tasks(tasks):
        name = task.get("name", "").lower()
        if "backup" in name:
            if "block" in task:
                return task
    return None


def test_backup_task_exists(tasks):
    backup_tasks = find_backup_tasks(tasks)
    if backup_tasks:
        print(
            "OK: vzdump backup task exists in pve_base."
        )
        return True
    for task in flatten_tasks(tasks):
        name = task.get("name", "").lower()
        if "backup" in name:
            print(
                "OK: Backup task exists in pve_base."
            )
            return True
    print(
        "FAIL: No backup task found in pve_base role. "
        "Expected a task with 'backup' in the name."
    )
    return False


def test_backup_has_schedule(tasks):
    scheduling_modules = (
        "ansible.builtin.cron",
        "community.proxmox.proxmox_backup",
    )
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "backup" not in name:
            continue
        for module_key in scheduling_modules:
            params = task.get(module_key, {})
            if params:
                print(
                    "OK: Backup task has scheduling "
                    f"configuration ({module_key})."
                )
                return True
    print(
        "FAIL: No backup scheduling found. Expected an "
        "ansible.builtin.cron or "
        "community.proxmox.proxmox_backup task with "
        "'backup' in the name."
    )
    return False


def test_backup_has_retention(tasks):
    for task in flatten_tasks(tasks):
        name = task.get("name", "").lower()
        if "backup" not in name and "retention" not in name:
            continue
        task_str = str(task).lower()
        if any(
            kw in task_str
            for kw in (
                "keep-daily",
                "keep_daily",
                "keep-weekly",
                "keep_weekly",
                "keep-monthly",
                "keep_monthly",
                "maxfiles",
                "retention",
                "prune-backups",
                "prune_backups",
            )
        ):
            print(
                "OK: Backup task has retention policy."
            )
            return True
    print(
        "FAIL: No retention policy found in backup "
        "tasks. Expected keep-daily, keep-weekly, "
        "keep-monthly, maxfiles, or prune-backups "
        "configuration."
    )
    return False


def test_backup_targets_storage(tasks):
    for task in flatten_tasks(tasks):
        name = task.get("name", "").lower()
        if "backup" not in name:
            continue
        task_str = str(task).lower()
        if any(
            kw in task_str
            for kw in (
                "storage",
                "nas",
                "pbs",
                "nfs",
                "backup_storage",
                "dumpdir",
            )
        ):
            print(
                "OK: Backup task targets external "
                "storage (NAS/PBS)."
            )
            return True
    print(
        "FAIL: No external storage target found in "
        "backup tasks. Expected storage, NAS, PBS, "
        "NFS, or dumpdir reference."
    )
    return False


def test_backup_uses_vzdump(tasks):
    for task in flatten_tasks(tasks):
        name = task.get("name", "").lower()
        if "backup" not in name:
            continue
        task_str = str(task).lower()
        if "vzdump" in task_str:
            print("OK: Backup uses vzdump.")
            return True
    print(
        "FAIL: No vzdump reference found in backup "
        "tasks. The backup must use Proxmox vzdump."
    )
    return False


def test_backup_vars_exist(variables):
    required_vars = {
        "backup_schedule_hour": int,
        "backup_storage": str,
        "backup_retention_daily": int,
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
                f"{expected_type.__name__})."
            )
            all_ok = False
    if all_ok:
        print(
            "OK: all.yml has backup variables "
            "(backup_schedule_hour, backup_storage, "
            "backup_retention_daily)."
        )
    return all_ok


def test_backup_retention_vars_complete(variables):
    retention_vars = [
        "backup_retention_daily",
        "backup_retention_weekly",
        "backup_retention_monthly",
    ]
    found = [
        v for v in retention_vars if v in variables
    ]
    if len(found) >= 2:
        print(
            f"OK: Retention variables configured "
            f"({', '.join(found)})."
        )
        return True
    print(
        "FAIL: Insufficient retention variables. "
        "Expected at least 2 of: "
        f"{', '.join(retention_vars)}. "
        f"Found: {', '.join(found) or 'none'}."
    )
    return False


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Backup task exists in pve_base",
            lambda: test_backup_task_exists(tasks),
        ),
        (
            "Backup has vzdump",
            lambda: test_backup_uses_vzdump(tasks),
        ),
        (
            "Backup has schedule",
            lambda: test_backup_has_schedule(tasks),
        ),
        (
            "Backup has retention policy",
            lambda: test_backup_has_retention(tasks),
        ),
        (
            "Backup targets external storage",
            lambda: test_backup_targets_storage(tasks),
        ),
        (
            "Backup vars in all.yml",
            lambda: test_backup_vars_exist(variables),
        ),
        (
            "Retention vars complete",
            lambda: test_backup_retention_vars_complete(
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
            f"FAILED {len(failed)}/{len(results)} "
            f"checks:"
        )
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    else:
        print(
            f"SUCCESS: All {len(results)} backup "
            f"schedule checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
