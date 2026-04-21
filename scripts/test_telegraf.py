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


def find_telegraf_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "telegraf" in name:
            results.append(task)
    return results


def test_telegraf_task_exists(tasks):
    tg_tasks = find_telegraf_tasks(tasks)
    if tg_tasks:
        print("OK: Telegraf task exists in pve_base.")
        return True
    print(
        "FAIL: No Telegraf task found in pve_base role. "
        "Expected a task with 'telegraf' in the name."
    )
    return False


def test_telegraf_install(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "telegraf" not in name:
            continue
        apt_params = task.get("ansible.builtin.apt", {})
        if not apt_params:
            continue
        pkgs = apt_params.get("name", [])
        if isinstance(pkgs, str):
            pkgs = [pkgs]
        if any("telegraf" in str(p).lower() for p in pkgs):
            print("OK: Telegraf is installed via apt.")
            return True
    print(
        "FAIL: No apt task installs telegraf. "
        "Expected ansible.builtin.apt with 'telegraf' "
        "in package list."
    )
    return False


def test_telegraf_config_deployed(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "telegraf" not in name:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            dest = str(params.get("dest", ""))
            content = str(params.get("content", ""))
            src = str(params.get("src", ""))
            if "telegraf" in dest.lower() and (
                "[[inputs." in content.lower()
                or "[[inputs." in src.lower()
            ):
                print(
                    "OK: Telegraf configuration with "
                    "inputs is deployed."
                )
                return True
    print(
        "FAIL: No Telegraf configuration deployed. "
        "Expected a copy/template task deploying "
        "telegraf config with input plugins "
        "(CPU/RAM/disk)."
    )
    return False


def test_telegraf_collects_system_metrics(tasks):
    required_inputs = ["cpu", "mem", "disk"]
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "telegraf" not in name:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            content = str(params.get("content", "")).lower()
            if not content:
                continue
            found = [
                m for m in required_inputs
                if f"inputs.{m}" in content
            ]
            if len(found) >= 2:
                print(
                    f"OK: Telegraf collects system metrics "
                    f"({', '.join(found)})."
                )
                return True
    print(
        "FAIL: Telegraf config does not collect system "
        "metrics. Expected at least 2 of: "
        "[[inputs.cpu]], [[inputs.mem]], [[inputs.disk]] "
        "in config content."
    )
    return False


def test_telegraf_outputs_configured(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "telegraf" not in name:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            content = str(params.get("content", "")).lower()
            if "[[outputs." in content:
                print(
                    "OK: Telegraf output plugin configured."
                )
                return True
    print(
        "FAIL: No output plugin in Telegraf config. "
        "Expected [[outputs.*]] section in config "
        "content (e.g. outputs.prometheus_client or "
        "outputs.influxdb)."
    )
    return False


def test_telegraf_vars_exist(variables):
    required_vars = {
        "telegraf_output_port": int,
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
            "OK: all.yml has telegraf variables "
            "with correct types."
        )
    return all_ok


def test_telegraf_service_enabled(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        svc_params = task.get(
            "ansible.builtin.systemd_service", {}
        ) or task.get("ansible.builtin.service", {})
        if not svc_params:
            continue
        svc_name = str(svc_params.get("name", ""))
        if "telegraf" in svc_name.lower():
            if svc_params.get("enabled") or svc_params.get(
                "state"
            ) in ("started", "restarted"):
                print(
                    "OK: Telegraf service is enabled/"
                    "started."
                )
                return True
    print(
        "FAIL: No systemd service task enables/starts "
        "telegraf. Expected ansible.builtin."
        "systemd_service or ansible.builtin.service "
        "with 'telegraf' in name."
    )
    return False


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Telegraf task exists in pve_base",
            lambda: test_telegraf_task_exists(tasks),
        ),
        (
            "Telegraf installed via apt",
            lambda: test_telegraf_install(tasks),
        ),
        (
            "Telegraf config deployed with inputs",
            lambda: test_telegraf_config_deployed(tasks),
        ),
        (
            "Telegraf collects system metrics",
            lambda: test_telegraf_collects_system_metrics(
                tasks
            ),
        ),
        (
            "Telegraf output plugin configured",
            lambda: test_telegraf_outputs_configured(tasks),
        ),
        (
            "Telegraf vars in all.yml",
            lambda: test_telegraf_vars_exist(variables),
        ),
        (
            "Telegraf service enabled",
            lambda: test_telegraf_service_enabled(tasks),
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
            f"SUCCESS: All {len(results)} Telegraf "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
