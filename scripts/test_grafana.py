import os
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/pve_base/tasks/main.yml"
)
HANDLERS_PATH = os.environ.get(
    "HANDLERS_PATH",
    "ansible/roles/pve_base/handlers/main.yml",
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


def find_grafana_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "grafana" in name:
            results.append(task)
    return results


def test_grafana_task_exists(tasks):
    grafana_tasks = find_grafana_tasks(tasks)
    if grafana_tasks:
        print("OK: Grafana task exists in pve_base.")
        return True
    print(
        "FAIL: No Grafana task found in pve_base role. "
        "Expected a task with 'grafana' in the name."
    )
    return False


def test_grafana_install(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "grafana" not in name:
            continue
        apt_params = task.get("ansible.builtin.apt", {})
        if not apt_params:
            continue
        pkgs = apt_params.get("name", [])
        if isinstance(pkgs, str):
            pkgs = [pkgs]
        if any("grafana" in str(p).lower() for p in pkgs):
            print("OK: Grafana is installed via apt.")
            return True
    print(
        "FAIL: No apt task installs grafana. "
        "Expected ansible.builtin.apt with 'grafana' "
        "in package list."
    )
    return False


def test_prometheus_datasource(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            content = str(params.get("content", ""))
            dest = str(params.get("dest", ""))
            if "datasource" not in dest.lower():
                continue
            if (
                "prometheus" in content.lower()
                and "9090" in content
            ):
                print(
                    "OK: Prometheus datasource configured "
                    "(localhost:9090)."
                )
                return True
    print(
        "FAIL: No Prometheus datasource provisioning "
        "found. Expected a copy/template task deploying "
        "a datasource config referencing prometheus and "
        "port 9090."
    )
    return False


def test_loki_datasource(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            content = str(params.get("content", ""))
            dest = str(params.get("dest", ""))
            if "datasource" not in dest.lower():
                continue
            if (
                "loki" in content.lower()
                and "3100" in content
            ):
                print(
                    "OK: Loki datasource configured "
                    "(localhost:3100)."
                )
                return True
    print(
        "FAIL: No Loki datasource provisioning found. "
        "Expected a copy/template task deploying a "
        "datasource config referencing loki and port "
        "3100."
    )
    return False


def test_dashboard_provisioning(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            content = str(params.get("content", ""))
            dest = str(params.get("dest", ""))
            if "dashboard" not in dest.lower():
                continue
            if "panel" not in content.lower():
                continue
            has_prom = (
                '"datasource": "Prometheus"' in content
                or "'datasource': 'Prometheus'"
                in content
            )
            has_loki = (
                '"datasource": "Loki"' in content
                or "'datasource': 'Loki'" in content
            )
            if not has_prom or not has_loki:
                missing = []
                if not has_prom:
                    missing.append("Prometheus")
                if not has_loki:
                    missing.append("Loki")
                print(
                    "FAIL: Dashboard found but missing "
                    "datasource references: "
                    f"{', '.join(missing)}. "
                    "Expected panels using both "
                    "Prometheus and Loki."
                )
                return False
            print(
                "OK: Dashboard provisioning "
                "configured with both Prometheus "
                "and Loki datasources."
            )
            return True
    print(
        "FAIL: No dashboard provisioning found. "
        "Expected a copy/template task deploying a "
        "dashboard config with panel definitions."
    )
    return False


def test_grafana_vars_exist(variables):
    required_vars = {
        "grafana_http_port": int,
        "grafana_admin_password": str,
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
            "OK: all.yml has grafana variables "
            "with correct types."
        )
    return all_ok


def test_grafana_service_enabled(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        svc_params = task.get(
            "ansible.builtin.systemd_service", {}
        ) or task.get("ansible.builtin.service", {})
        if not svc_params:
            continue
        svc_name = str(svc_params.get("name", ""))
        if "grafana" in svc_name.lower():
            if svc_params.get("enabled") or svc_params.get(
                "state"
            ) in ("started", "restarted"):
                print(
                    "OK: Grafana service is enabled/"
                    "started."
                )
                return True
    print(
        "FAIL: No systemd service task enables/starts "
        "grafana. Expected ansible.builtin."
        "systemd_service or ansible.builtin.service "
        "with 'grafana' in name."
    )
    return False


def test_grafana_handler_exists(handlers):
    if not handlers:
        print(
            "FAIL: No handlers found in handlers file."
        )
        return False
    for handler in handlers:
        if not isinstance(handler, dict):
            continue
        name = handler.get("name", "").lower()
        if "grafana" in name and "restart" in name:
            print("OK: restart_grafana handler exists.")
            return True
    print(
        "FAIL: No restart_grafana handler found. "
        "Expected a handler with 'grafana' and "
        "'restart' in the name."
    )
    return False


def test_datasources_both_present(tasks):
    found_prom = False
    found_loki = False
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            content = str(params.get("content", ""))
            dest = str(params.get("dest", ""))
            if "datasource" not in dest.lower():
                continue
            if "prometheus" in content.lower():
                found_prom = True
            if "loki" in content.lower():
                found_loki = True
    if found_prom and found_loki:
        print(
            "OK: Both Prometheus and Loki datasources "
            "present in provisioning."
        )
        return True
    missing = []
    if not found_prom:
        missing.append("Prometheus")
    if not found_loki:
        missing.append("Loki")
    print(
        f"FAIL: Missing datasources in provisioning: "
        f"{', '.join(missing)}."
    )
    return False


def main():
    tasks = load_yaml(TASKS_PATH)
    handlers = load_yaml(HANDLERS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Grafana task exists in pve_base",
            lambda: test_grafana_task_exists(tasks),
        ),
        (
            "Grafana installed via apt",
            lambda: test_grafana_install(tasks),
        ),
        (
            "Prometheus datasource configured",
            lambda: test_prometheus_datasource(tasks),
        ),
        (
            "Loki datasource configured",
            lambda: test_loki_datasource(tasks),
        ),
        (
            "Dashboard provisioning configured",
            lambda: test_dashboard_provisioning(tasks),
        ),
        (
            "Grafana vars in all.yml",
            lambda: test_grafana_vars_exist(variables),
        ),
        (
            "Grafana service enabled",
            lambda: test_grafana_service_enabled(tasks),
        ),
        (
            "restart_grafana handler exists",
            lambda: test_grafana_handler_exists(handlers),
        ),
        (
            "Both datasources present",
            lambda: test_datasources_both_present(tasks),
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
            f"SUCCESS: All {len(results)} Grafana "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
