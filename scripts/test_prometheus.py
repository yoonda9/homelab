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


def find_prometheus_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "prometheus" in name:
            results.append(task)
    return results


def test_prometheus_task_exists(tasks):
    prom_tasks = find_prometheus_tasks(tasks)
    if prom_tasks:
        print("OK: Prometheus task exists in pve_base.")
        return True
    print(
        "FAIL: No Prometheus task found in pve_base role. "
        "Expected a task with 'prometheus' in the name."
    )
    return False


def test_prometheus_install(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "prometheus" not in name:
            continue
        apt_params = task.get("ansible.builtin.apt", {})
        if not apt_params:
            continue
        pkgs = apt_params.get("name", [])
        if isinstance(pkgs, str):
            pkgs = [pkgs]
        if any("prometheus" in str(p).lower() for p in pkgs):
            print("OK: Prometheus is installed via apt.")
            return True
    print(
        "FAIL: No apt task installs prometheus. "
        "Expected ansible.builtin.apt with 'prometheus' "
        "in package list."
    )
    return False


def test_prometheus_scrape_config(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "prometheus" not in name:
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
            if (
                "prometheus" in dest.lower()
                and "scrape_configs" in content.lower()
            ):
                print(
                    "OK: Prometheus scrape configuration "
                    "is deployed."
                )
                return True
    print(
        "FAIL: No Prometheus scrape configuration found. "
        "Expected a copy/template task deploying "
        "prometheus config with scrape settings."
    )
    return False


def test_proxmox_exporter_scrape_target(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        if "prometheus" not in name:
            continue
        for module_key in (
            "ansible.builtin.template",
            "ansible.builtin.copy",
        ):
            params = task.get(module_key, {})
            if not params:
                continue
            content = str(params.get("content", ""))
            if (
                "pve" in content.lower()
                or "proxmox" in content.lower()
                or "9221" in content
            ):
                print(
                    "OK: Proxmox exporter scrape target "
                    "configured."
                )
                return True
    print(
        "FAIL: No proxmox-exporter scrape target found "
        "in Prometheus config. Expected 'pve', "
        "'proxmox', or port 9221 in scrape config "
        "content."
    )
    return False


def test_proxmox_exporter_install(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        name = task.get("name", "").lower()
        task_str = str(task).lower()
        if (
            "exporter" in name
            or "pve-exporter" in task_str
            or "proxmox-exporter" in task_str
            or "prometheus-pve-exporter" in task_str
        ):
            for module_key in (
                "ansible.builtin.apt",
                "ansible.builtin.pip",
                "ansible.builtin.shell",
            ):
                if task.get(module_key):
                    print(
                        "OK: Proxmox exporter is installed."
                    )
                    return True
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        apt_params = task.get("ansible.builtin.apt", {})
        if not apt_params:
            continue
        pkgs = apt_params.get("name", [])
        if isinstance(pkgs, str):
            pkgs = [pkgs]
        if any(
            "pve-exporter" in str(p).lower()
            or "proxmox-exporter" in str(p).lower()
            for p in pkgs
        ):
            print("OK: Proxmox exporter is installed.")
            return True
    print(
        "FAIL: No proxmox-exporter installation found. "
        "Expected apt/pip/shell task installing "
        "pve-exporter or prometheus-pve-exporter."
    )
    return False


def test_prometheus_vars_exist(variables):
    required_vars = {
        "prometheus_port": int,
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
            "OK: all.yml has prometheus variables "
            "with correct types."
        )
    return all_ok


def test_prometheus_service_enabled(tasks):
    for task in flatten_tasks(tasks):
        if "block" in task:
            continue
        svc_params = task.get(
            "ansible.builtin.systemd_service", {}
        ) or task.get("ansible.builtin.service", {})
        if not svc_params:
            continue
        svc_name = str(svc_params.get("name", ""))
        if "prometheus" in svc_name.lower():
            if svc_params.get("enabled") or svc_params.get(
                "state"
            ) in ("started", "restarted"):
                print(
                    "OK: Prometheus service is enabled/"
                    "started."
                )
                return True
    print(
        "FAIL: No systemd service task enables/starts "
        "prometheus. Expected ansible.builtin."
        "systemd_service or ansible.builtin.service "
        "with 'prometheus' in name."
    )
    return False


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Prometheus task exists in pve_base",
            lambda: test_prometheus_task_exists(tasks),
        ),
        (
            "Prometheus installed via apt",
            lambda: test_prometheus_install(tasks),
        ),
        (
            "Prometheus scrape config deployed",
            lambda: test_prometheus_scrape_config(tasks),
        ),
        (
            "Proxmox exporter scrape target",
            lambda: test_proxmox_exporter_scrape_target(
                tasks
            ),
        ),
        (
            "Proxmox exporter installed",
            lambda: test_proxmox_exporter_install(tasks),
        ),
        (
            "Prometheus vars in all.yml",
            lambda: test_prometheus_vars_exist(variables),
        ),
        (
            "Prometheus service enabled",
            lambda: test_prometheus_service_enabled(tasks),
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
            f"SUCCESS: All {len(results)} Prometheus "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
