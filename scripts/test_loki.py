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


def find_loki_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "loki" in name:
            results.append(task)
    return results


def find_promtail_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "promtail" in name:
            results.append(task)
    return results


def test_loki_task_exists(tasks):
    loki_tasks = find_loki_tasks(tasks)
    if loki_tasks:
        print("OK: Loki task exists in pve_base.")
        return True
    print(
        "FAIL: No Loki task found in pve_base role. "
        "Expected a task with 'loki' in the name."
    )
    return False


def test_loki_install(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "loki" not in name:
            continue
        for module_key in (
            "ansible.builtin.apt",
            "ansible.builtin.get_url",
            "ansible.builtin.shell",
            "ansible.builtin.pip",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            if module_key == "ansible.builtin.apt":
                pkgs = params.get("name", [])
                if isinstance(pkgs, str):
                    pkgs = [pkgs]
                if any("loki" in str(p).lower() for p in pkgs):
                    print("OK: Loki is installed via apt.")
                    return True
            elif module_key == "ansible.builtin.get_url":
                url = str(params.get("url", "")).lower()
                if "loki" in url:
                    print(
                        "OK: Loki is installed via "
                        "binary download."
                    )
                    return True
            elif module_key in (
                "ansible.builtin.shell",
                "ansible.builtin.pip",
            ):
                cmd = str(
                    params.get("cmd", params.get("name", ""))
                ).lower()
                if "loki" in cmd:
                    print(
                        "OK: Loki is installed via "
                        "shell/pip."
                    )
                    return True
    print(
        "FAIL: No task installs Loki. Expected "
        "ansible.builtin.apt, get_url, shell, or pip "
        "with 'loki' reference."
    )
    return False


def test_loki_config_deployed(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "loki" not in name:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            dest = str(params.get("dest", "")).lower()
            content = str(params.get("content", "")).lower()
            if "loki" in dest and (
                "schema_config" in content
                or "storage_config" in content
            ):
                print(
                    "OK: Loki configuration with "
                    "schema/storage config is deployed."
                )
                return True
    print(
        "FAIL: No Loki configuration deployed. "
        "Expected a copy/template task deploying "
        "loki config with schema_config or "
        "storage_config sections."
    )
    return False


def test_promtail_install(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "promtail" not in name:
            continue
        for module_key in (
            "ansible.builtin.apt",
            "ansible.builtin.get_url",
            "ansible.builtin.shell",
            "ansible.builtin.pip",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            if module_key == "ansible.builtin.apt":
                pkgs = params.get("name", [])
                if isinstance(pkgs, str):
                    pkgs = [pkgs]
                if any(
                    "promtail" in str(p).lower()
                    for p in pkgs
                ):
                    print(
                        "OK: Promtail is installed via apt."
                    )
                    return True
            elif module_key == "ansible.builtin.get_url":
                url = str(params.get("url", "")).lower()
                if "promtail" in url:
                    print(
                        "OK: Promtail is installed via "
                        "binary download."
                    )
                    return True
            elif module_key in (
                "ansible.builtin.shell",
                "ansible.builtin.pip",
            ):
                cmd = str(
                    params.get("cmd", params.get("name", ""))
                ).lower()
                if "promtail" in cmd:
                    print(
                        "OK: Promtail is installed via "
                        "shell/pip."
                    )
                    return True
    print(
        "FAIL: No task installs Promtail. Expected "
        "ansible.builtin.apt, get_url, shell, or pip "
        "with 'promtail' reference."
    )
    return False


def test_promtail_config_deployed(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "promtail" not in name:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            dest = str(params.get("dest", "")).lower()
            content = str(params.get("content", "")).lower()
            if "promtail" in dest and (
                "scrape_configs" in content
                and "clients" in content
            ):
                print(
                    "OK: Promtail configuration with "
                    "scrape_configs and clients is "
                    "deployed."
                )
                return True
    print(
        "FAIL: No Promtail configuration deployed. "
        "Expected a copy/template task deploying "
        "promtail config with scrape_configs and "
        "clients sections."
    )
    return False


def test_promtail_ships_logs(tasks):
    log_sources = ["syslog", "journal", "var/log"]
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "promtail" not in name:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            content = str(
                params.get("content", "")
            ).lower()
            found = [
                s for s in log_sources if s in content
            ]
            if found:
                print(
                    f"OK: Promtail ships logs from "
                    f"({', '.join(found)})."
                )
                return True
    print(
        "FAIL: Promtail config does not reference log "
        "sources. Expected at least one of: syslog, "
        "journal, /var/log in config content."
    )
    return False


def test_loki_vars_exist(variables):
    required_vars = {
        "loki_http_port": int,
        "loki_retention_period": str,
        "promtail_http_port": int,
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
            "OK: all.yml has loki variables "
            "with correct types."
        )
    return all_ok


def test_loki_service_enabled(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        svc_params = task.get(
            "ansible.builtin.systemd_service", {}
        ) or task.get("ansible.builtin.service", {})
        if not svc_params:
            continue
        svc_name = str(svc_params.get("name", ""))
        if "loki" in svc_name.lower():
            if svc_params.get("enabled") or svc_params.get(
                "state"
            ) in ("started", "restarted"):
                print(
                    "OK: Loki service is enabled/"
                    "started."
                )
                return True
    print(
        "FAIL: No systemd service task enables/starts "
        "loki. Expected ansible.builtin."
        "systemd_service or ansible.builtin.service "
        "with 'loki' in name."
    )
    return False


def test_promtail_service_enabled(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        svc_params = task.get(
            "ansible.builtin.systemd_service", {}
        ) or task.get("ansible.builtin.service", {})
        if not svc_params:
            continue
        svc_name = str(svc_params.get("name", ""))
        if "promtail" in svc_name.lower():
            if svc_params.get("enabled") or svc_params.get(
                "state"
            ) in ("started", "restarted"):
                print(
                    "OK: Promtail service is enabled/"
                    "started."
                )
                return True
    print(
        "FAIL: No systemd service task enables/starts "
        "promtail. Expected ansible.builtin."
        "systemd_service or ansible.builtin.service "
        "with 'promtail' in name."
    )
    return False


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Loki task exists in pve_base",
            lambda: test_loki_task_exists(tasks),
        ),
        (
            "Loki installed",
            lambda: test_loki_install(tasks),
        ),
        (
            "Loki config deployed with schema/storage",
            lambda: test_loki_config_deployed(tasks),
        ),
        (
            "Promtail installed",
            lambda: test_promtail_install(tasks),
        ),
        (
            "Promtail config with scrape_configs+clients",
            lambda: test_promtail_config_deployed(tasks),
        ),
        (
            "Promtail ships logs from host",
            lambda: test_promtail_ships_logs(tasks),
        ),
        (
            "Loki vars in all.yml",
            lambda: test_loki_vars_exist(variables),
        ),
        (
            "Loki service enabled",
            lambda: test_loki_service_enabled(tasks),
        ),
        (
            "Promtail service enabled",
            lambda: test_promtail_service_enabled(tasks),
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
            f"SUCCESS: All {len(results)} Loki/Promtail "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
