import os
import yaml
import sys

def check_api_host_usage():
    files = [
        "ansible/roles/pve_base/tasks/main.yml",
        "ansible/roles/pve_provision/tasks/main.yml"
    ]
    all_ok = True
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"FAIL: '{file_path}' is missing.")
            all_ok = False
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
            if 'api_host: "{{ pve_host }}"' in content:
                print(f"FAIL: 'api_host: \"{{{{ pve_host }}}}\"' still found in {file_path}.")
                all_ok = False
            else:
                print(f"OK: No hardcoded 'pve_host' for api_host in {file_path}.")
    return all_ok

def check_monitoring_hostname():
    file_path = "ansible/roles/pve_base/tasks/main.yml"
    if not os.path.exists(file_path):
        return False
        
    with open(file_path, 'r') as f:
        tasks = yaml.safe_load(f)
        
        all_ok = True
        
        def find_tasks(task_list):
            nonlocal all_ok
            for task in task_list:
                if not isinstance(task, dict): continue
                name = task.get('name', '')
                if 'Telegraf configuration' in name:
                    content = task.get('ansible.builtin.copy', {}).get('content', '')
                    if '{{ inventory_hostname }}' in content:
                        print("FAIL: Telegraf configuration still uses 'inventory_hostname'.")
                        all_ok = False
                    elif '{{ ansible_hostname }}' in content:
                        print("OK: Telegraf configuration uses 'ansible_hostname'.")
                
                if 'Promtail configuration' in name or 'Deploy Promtail configuration' in name:
                    content = task.get('ansible.builtin.copy', {}).get('content', '')
                    if '{{ inventory_hostname }}' in content:
                        print("FAIL: Promtail configuration still uses 'inventory_hostname'.")
                        all_ok = False
                    elif '{{ ansible_hostname }}' in content:
                        print("OK: Promtail configuration uses 'ansible_hostname'.")

                if 'block' in task: find_tasks(task['block'])
        
        find_tasks(tasks)
        return all_ok

def check_snippets_dir():
    file_path = "ansible/roles/pve_base/tasks/main.yml"
    with open(file_path, 'r') as f:
        content = f.read()
        if 'path: /etc/pve/snippets' in content and 'state: directory' in content:
            print("OK: Snippets directory task found.")
            return True
        else:
            print("FAIL: Snippets directory task missing.")
            return False

if __name__ == "__main__":
    ok1 = check_api_host_usage()
    ok2 = check_monitoring_hostname()
    ok3 = check_snippets_dir()
    if ok1 and ok2 and ok3:
        print("\nSUCCESS: All rejection issues and snippets dir are verified as fixed.")
        sys.exit(0)
    else:
        sys.exit(1)
