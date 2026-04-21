import os
import re
import subprocess
import sys

import yaml

TASKS_PATH = "ansible/roles/pve_base/tasks/main.yml"

ALLOWED_MODULES = {
    "ansible.builtin.shell",
    "ansible.builtin.command",
    "ansible.builtin.copy",
    "ansible.builtin.file",
    "ansible.builtin.lineinfile",
    "ansible.builtin.replace",
    "ansible.builtin.apt",
    "ansible.builtin.get_url",
    "ansible.builtin.deb822_repository",
    "ansible.builtin.debug",
    "ansible.builtin.cron",
    "community.proxmox.proxmox_firewall",
    "community.proxmox.proxmox_firewall_info",
}

HALLUCINATED_MODULES = {
    "community.proxmox.proxmox_cluster_firewall",
    "community.proxmox.proxmox_node_firewall",
    "community.proxmox.proxmox_firewall_alias",
    "community.proxmox.proxmox_firewall_rule",
}


def load_tasks():
    with open(TASKS_PATH, "r") as f:
        return yaml.safe_load(f)


def flatten_tasks(task_list):
    """Recursively flatten tasks including block contents."""
    result = []
    for task in task_list:
        if not isinstance(task, dict):
            continue
        result.append(task)
        if "block" in task:
            result.extend(flatten_tasks(task["block"]))
    return result


def get_module_name(task):
    """Extract the Ansible module name from a task dict."""
    skip_keys = {
        "name", "block", "when", "register", "changed_when",
        "failed_when", "notify", "delegate_to", "tags", "vars",
        "become", "become_user", "ignore_errors", "no_log",
        "environment", "loop", "with_items",
    }
    for key in task:
        if key not in skip_keys and "." in key:
            return key
    return None


def find_firewall_block(tasks):
    """Find the Proxmox Firewall Configuration block."""
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if "Proxmox Firewall" in task.get("name", ""):
            return task
    return None


def test_no_hallucinated_modules():
    """Verify no hallucinated modules are used anywhere."""
    tasks = load_tasks()
    all_tasks = flatten_tasks(tasks)
    failures = []
    for task in all_tasks:
        module = get_module_name(task)
        if module in HALLUCINATED_MODULES:
            failures.append(
                f"Hallucinated module '{module}' in task "
                f"'{task.get('name', 'unnamed')}'"
            )
    return failures


def test_only_valid_modules_in_firewall():
    """Verify firewall block only uses known-valid modules."""
    tasks = load_tasks()
    fw_block = find_firewall_block(tasks)
    if fw_block is None:
        return ["Proxmox Firewall Configuration block not found"]

    block_tasks = flatten_tasks(fw_block.get("block", []))
    failures = []
    for task in block_tasks:
        module = get_module_name(task)
        if module and module not in ALLOWED_MODULES:
            failures.append(
                f"Unknown module '{module}' in task "
                f"'{task.get('name', 'unnamed')}'"
            )
    return failures


def test_cluster_firewall_enabled_drop_policy():
    """Verify cluster firewall is enabled with DROP inbound policy."""
    tasks = load_tasks()
    fw_block = find_firewall_block(tasks)
    if fw_block is None:
        return ["Proxmox Firewall Configuration block not found"]

    block_tasks = flatten_tasks(fw_block.get("block", []))
    found = False
    for task in block_tasks:
        name = task.get("name", "")
        if "Cluster Firewall" not in name:
            continue
        module = get_module_name(task)
        if module == "ansible.builtin.shell":
            cmd = task.get("ansible.builtin.shell", "")
            if isinstance(cmd, dict):
                cmd = cmd.get("cmd", "")
            cmd_str = str(cmd)
            if re.search(r"policy_in\s+DROP", cmd_str, re.IGNORECASE):
                found = True
            elif "policy_in" in cmd_str.lower():
                return [
                    "Cluster firewall task sets policy_in but NOT to DROP. "
                    f"Command: {cmd_str.strip()}"
                ]
        elif module == "community.proxmox.proxmox_firewall":
            params = task.get("community.proxmox.proxmox_firewall", {})
            if isinstance(params, dict):
                policy = str(params.get("policy_in", "")).upper()
                if policy == "DROP":
                    found = True
                else:
                    return [
                        f"community.proxmox.proxmox_firewall sets "
                        f"policy_in to '{policy}', expected 'DROP'"
                    ]
        if found:
            break

    if not found:
        return [
            "No task to enable cluster firewall with DROP policy found. "
            "Expected a shell/pvesh task or "
            "community.proxmox.proxmox_firewall task."
        ]
    return []


def test_host_firewall_enabled():
    """Verify node-level firewall is enabled."""
    tasks = load_tasks()
    fw_block = find_firewall_block(tasks)
    if fw_block is None:
        return ["Proxmox Firewall Configuration block not found"]

    block_tasks = flatten_tasks(fw_block.get("block", []))
    found = False
    for task in block_tasks:
        name = task.get("name", "")
        if "Host Firewall" in name or "Node Firewall" in name:
            found = True
            break

    if not found:
        return ["No task to enable host/node firewall found"]
    return []


def test_management_alias():
    """Verify a management IP alias is configured."""
    tasks = load_tasks()
    fw_block = find_firewall_block(tasks)
    if fw_block is None:
        return ["Proxmox Firewall Configuration block not found"]

    block_tasks = flatten_tasks(fw_block.get("block", []))
    found = False
    for task in block_tasks:
        name = task.get("name", "")
        task_str = str(task)
        if "Alias" in name or "alias" in name:
            if "mgmt" in task_str.lower():
                found = True
                break

    if not found:
        return ["No management IP alias task found"]
    return []


def test_firewall_rule_ports():
    """Verify firewall rules allow SSH (22) and Web UI (8006)."""
    tasks = load_tasks()
    fw_block = find_firewall_block(tasks)
    if fw_block is None:
        return ["Proxmox Firewall Configuration block not found"]

    block_tasks = flatten_tasks(fw_block.get("block", []))
    task_str = str(block_tasks)
    failures = []
    if "8006" not in task_str:
        failures.append("Port 8006 (Web UI) not found in firewall rules")
    if "22" not in task_str:
        failures.append("Port 22 (SSH) not found in firewall rules")
    return failures


def test_syntax_check():
    """Run ansible-playbook --syntax-check to verify no broken modules."""
    result = subprocess.run(
        [".venv/bin/ansible-playbook", "--syntax-check", "ansible/main.yml"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [
            f"ansible-playbook --syntax-check failed:\n"
            f"{result.stderr.strip()}"
        ]
    return []


def test_no_hallucinated_modules_grep():
    """Grep the raw file for hallucinated module strings."""
    with open(TASKS_PATH, "r") as f:
        content = f.read()
    failures = []
    for mod in HALLUCINATED_MODULES:
        if mod in content:
            failures.append(f"Hallucinated module '{mod}' found in raw file")
    return failures


def main():
    if not os.path.exists(TASKS_PATH):
        print(f"FAIL: '{TASKS_PATH}' is missing.")
        sys.exit(1)

    tests = [
        ("No hallucinated modules (YAML)", test_no_hallucinated_modules),
        ("No hallucinated modules (grep)", test_no_hallucinated_modules_grep),
        ("Valid modules in firewall block", test_only_valid_modules_in_firewall),
        ("Cluster firewall with DROP policy", test_cluster_firewall_enabled_drop_policy),
        ("Host firewall enabled", test_host_firewall_enabled),
        ("Management IP alias", test_management_alias),
        ("Firewall rules for ports 22/8006", test_firewall_rule_ports),
        ("Ansible syntax check", test_syntax_check),
    ]

    all_passed = True
    for name, test_fn in tests:
        failures = test_fn()
        if failures:
            all_passed = False
            for f in failures:
                print(f"FAIL [{name}]: {f}")
        else:
            print(f"OK: {name}")

    if all_passed:
        print("\nSUCCESS: All firewall checks passed.")
        sys.exit(0)
    else:
        print("\nFAILURE: Some firewall checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
