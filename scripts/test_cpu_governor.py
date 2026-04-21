import os
import re
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/pve_base/tasks/main.yml"
)
EXPECTED_GOVERNOR = "performance"
EXPECTED_PACKAGE = "linux-cpupower"
EXPECTED_COMMAND = "cpupower frequency-set -g"


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


def find_task_by_name(tasks, pattern):
    for task in flatten_tasks(tasks):
        if re.search(pattern, task.get("name", ""), re.IGNORECASE):
            return task
    return None


def get_shell_cmd(task):
    shell_val = task.get("ansible.builtin.shell", "")
    if isinstance(shell_val, dict):
        return shell_val.get("cmd", "")
    return str(shell_val)


def test_cpupower_package_installed(tasks):
    task = find_task_by_name(tasks, r"cpupower|cpu.?power")
    if task is None:
        for t in flatten_tasks(tasks):
            apt_params = t.get("ansible.builtin.apt", {})
            if isinstance(apt_params, dict):
                name = apt_params.get("name", [])
                if isinstance(name, list) and EXPECTED_PACKAGE in name:
                    task = t
                    break
                if isinstance(name, str) and name == EXPECTED_PACKAGE:
                    task = t
                    break
    if task is None:
        print(
            f"FAIL: No task installs '{EXPECTED_PACKAGE}' package."
        )
        return False
    print(f"OK: Found task installing '{EXPECTED_PACKAGE}': {task['name']}")
    return True


def test_governor_task_uses_cpupower(tasks):
    task = find_task_by_name(tasks, r"CPU Governor")
    if task is None:
        print("FAIL: No task with 'CPU Governor' in name found.")
        return False
    cmd = get_shell_cmd(task)
    if EXPECTED_COMMAND not in cmd:
        print(
            f"FAIL: CPU Governor task does not use "
            f"'{EXPECTED_COMMAND}'. Got: '{cmd}'"
        )
        return False
    print(f"OK: CPU Governor task uses '{EXPECTED_COMMAND}'.")
    return True


def test_governor_default_is_performance(tasks):
    task = find_task_by_name(tasks, r"CPU Governor")
    if task is None:
        print("FAIL: No task with 'CPU Governor' in name found.")
        return False
    cmd = get_shell_cmd(task)
    match = re.search(r"default\(['\"]?(\w+)['\"]?\)", cmd)
    if not match:
        if EXPECTED_GOVERNOR in cmd:
            print(
                f"OK: CPU Governor command contains "
                f"'{EXPECTED_GOVERNOR}' (hardcoded)."
            )
            return True
        print(
            f"FAIL: Could not find governor default value in "
            f"command. Got: '{cmd}'"
        )
        return False
    governor = match.group(1)
    if governor != EXPECTED_GOVERNOR:
        print(
            f"FAIL: CPU Governor default is '{governor}', "
            f"expected '{EXPECTED_GOVERNOR}'."
        )
        return False
    print(
        f"OK: CPU Governor default is '{EXPECTED_GOVERNOR}'."
    )
    return True


def test_cron_persistence_exists(tasks):
    cron_task = None
    for task in flatten_tasks(tasks):
        if "ansible.builtin.cron" in task:
            cron_params = task.get("ansible.builtin.cron", {})
            job = cron_params.get("job", "")
            if "cpupower" in job or "cpu" in job.lower():
                cron_task = task
                break
    if cron_task is None:
        print(
            "FAIL: No cron task found for CPU governor persistence."
        )
        return False
    print(f"OK: Found cron persistence task: {cron_task['name']}")
    return True


def test_cron_runs_at_reboot(tasks):
    for task in flatten_tasks(tasks):
        if "ansible.builtin.cron" not in task:
            continue
        cron_params = task.get("ansible.builtin.cron", {})
        job = cron_params.get("job", "")
        if "cpupower" not in job:
            continue
        special_time = cron_params.get("special_time", "")
        if special_time != "reboot":
            print(
                f"FAIL: CPU governor cron special_time is "
                f"'{special_time}', expected 'reboot'."
            )
            return False
        print("OK: CPU governor cron runs at reboot.")
        return True
    print("FAIL: No cpupower cron task found to check reboot timing.")
    return False


def test_cron_governor_matches_default(tasks):
    for task in flatten_tasks(tasks):
        if "ansible.builtin.cron" not in task:
            continue
        cron_params = task.get("ansible.builtin.cron", {})
        job = cron_params.get("job", "")
        if "cpupower" not in job:
            continue
        match = re.search(r"default\(['\"]?(\w+)['\"]?\)", job)
        if match:
            governor = match.group(1)
        elif EXPECTED_GOVERNOR in job:
            governor = EXPECTED_GOVERNOR
        else:
            print(
                f"FAIL: Cron job does not contain governor "
                f"'{EXPECTED_GOVERNOR}'. Got: '{job}'"
            )
            return False
        if governor != EXPECTED_GOVERNOR:
            print(
                f"FAIL: Cron governor default is '{governor}', "
                f"expected '{EXPECTED_GOVERNOR}'."
            )
            return False
        print(
            f"OK: Cron job governor default is "
            f"'{EXPECTED_GOVERNOR}'."
        )
        return True
    print("FAIL: No cpupower cron task found to check governor value.")
    return False


def test_cron_uses_cpupower_command(tasks):
    for task in flatten_tasks(tasks):
        if "ansible.builtin.cron" not in task:
            continue
        cron_params = task.get("ansible.builtin.cron", {})
        job = cron_params.get("job", "")
        if "cpupower" not in job:
            continue
        if EXPECTED_COMMAND not in job:
            print(
                f"FAIL: Cron job does not use "
                f"'{EXPECTED_COMMAND}'. Got: '{job}'"
            )
            return False
        print(f"OK: Cron job uses '{EXPECTED_COMMAND}'.")
        return True
    print("FAIL: No cpupower cron task found to check command.")
    return False


def main():
    tasks = load_tasks()
    checks = [
        ("linux-cpupower package installed", test_cpupower_package_installed),
        ("Governor task uses cpupower command", test_governor_task_uses_cpupower),
        ("Governor default is 'performance'", test_governor_default_is_performance),
        ("Cron persistence task exists", test_cron_persistence_exists),
        ("Cron runs at reboot", test_cron_runs_at_reboot),
        ("Cron governor default matches 'performance'", test_cron_governor_matches_default),
        ("Cron uses cpupower frequency-set command", test_cron_uses_cpupower_command),
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
        print(f"SUCCESS: All {len(results)} CPU governor checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
