import os
import yaml
import sys
import subprocess

def check_ansible_config():
    if not os.path.exists("ansible/ansible.cfg"):
        print("FAIL: 'ansible/ansible.cfg' is missing.")
        return False
    print("OK: 'ansible/ansible.cfg' exists.")
    return True

def check_inventory():
    inventory_path = "ansible/inventory/hosts.yml"
    if not os.path.exists(inventory_path):
        print(f"FAIL: '{inventory_path}' is missing.")
        return False
        
    try:
        with open(inventory_path, 'r') as f:
            inventory = yaml.safe_load(f)
            if 'proxmox_hosts' in inventory:
                print(f"OK: 'proxmox_hosts' defined in {inventory_path}.")
                return True
            else:
                print(f"FAIL: 'proxmox_hosts' missing from {inventory_path}.")
                return False
    except Exception as e:
        print(f"FAIL: Error reading inventory: {e}")
        return False

def check_group_vars():
    vars_path = "ansible/group_vars/all.yml"
    if not os.path.exists(vars_path):
        print(f"FAIL: '{vars_path}' is missing.")
        return False
    print(f"OK: '{vars_path}' exists.")
    return True

def check_role_tasks():
    tasks_path = "ansible/roles/pve_base/tasks/main.yml"
    if not os.path.exists(tasks_path):
        print(f"FAIL: '{tasks_path}' is missing.")
        return False
        
    try:
        with open(tasks_path, 'r') as f:
            tasks = yaml.safe_load(f)
            # Find task to generate API token
            found = False
            for block in tasks:
                if isinstance(block, dict) and block.get('name') == 'Proxmox API Authentication Configuration':
                    found = True
                    break
            
            if found:
                print(f"OK: Proxmox API Authentication tasks found in {tasks_path}.")
                return True
            else:
                print(f"FAIL: Authentication configuration missing from {tasks_path}.")
                return False
    except Exception as e:
        print(f"FAIL: Error reading tasks: {e}")
        return False

def check_ansible_syntax():
    cmd = ["./.venv/bin/ansible-playbook", "--syntax-check", "ansible/main.yml"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("OK: Ansible syntax check passed.")
            return True
        else:
            print(f"FAIL: Ansible syntax check failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"FAIL: Error running syntax check: {e}")
        return False

def check_module_resolution():
    # Confirm community.proxmox.proxmox_node_info is available
    cmd = ["./.venv/bin/ansible-doc", "community.proxmox.proxmox_node_info"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("FAIL: 'community.proxmox.proxmox_node_info' module not found.")
            return False
        print("OK: 'community.proxmox.proxmox_node_info' module found.")
        
        # Confirm community.proxmox.proxmox_api_token is NOT used
        grep_cmd = ["grep", "-r", "community.proxmox.proxmox_api_token", "ansible"]
        result = subprocess.run(grep_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("FAIL: 'community.proxmox.proxmox_api_token' still found in codebase.")
            return False
        print("OK: Hallucinated module 'community.proxmox.proxmox_api_token' is NOT used.")
        return True
    except Exception as e:
        print(f"FAIL: Error checking modules: {e}")
        return False

all_ok = all([
    check_ansible_config(),
    check_inventory(),
    check_group_vars(),
    check_role_tasks(),
    check_ansible_syntax(),
    check_module_resolution()
])

if not all_ok:
    sys.exit(1)
else:
    print("\nSUCCESS: Proxmox API Authentication structure is configured and verified.")
