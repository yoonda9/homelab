import os
import yaml
import sys

def check_suppress_nag_task():
    tasks_path = "ansible/roles/pve_base/tasks/main.yml"
    if not os.path.exists(tasks_path):
        print(f"FAIL: '{tasks_path}' is missing.")
        return False
        
    try:
        with open(tasks_path, 'r') as f:
            tasks = yaml.safe_load(f)
            found_suppress_nag = False
            found_handler_notify = False
            success = True
            
            def check_tasks(task_list):
                nonlocal found_suppress_nag, found_handler_notify, success
                for task in task_list:
                    if not isinstance(task, dict):
                        continue
                    name = task.get('name', '')
                    
                    if 'Suppress' in name and 'Subscription Nag' in name:
                        found_suppress_nag = True
                        if 'notify' in task:
                            notify = task.get('notify')
                            if isinstance(notify, list):
                                if 'restart_pveproxy' in notify:
                                    found_handler_notify = True
                            elif notify == 'restart_pveproxy':
                                found_handler_notify = True
                        
                        # Verify robust regex and backup
                        replace_task = task.get('ansible.builtin.replace', {})
                        regexp = replace_task.get('regexp', '')
                        # Handle both literal and escaped dots/parens for robustness check
                        if 'res' in regexp and 'status' in regexp and 'toLowerCase' in regexp:
                            print("OK: Robust regex found.")
                        else:
                            print(f"FAIL: Regex '{regexp}' is not robust enough.")
                            success = False
                            
                        if replace_task.get('backup') is True:
                            print("OK: 'backup: yes' found.")
                        else:
                            print("FAIL: 'backup: yes' missing from replace task.")
                            success = False
                    
                    if 'block' in task:
                        check_tasks(task['block'])

            check_tasks(tasks)
                    
            if not found_suppress_nag:
                print("FAIL: Task 'Suppress Subscription Nag' missing.")
                success = False
            if not found_handler_notify:
                print("FAIL: Task should notify 'restart_pveproxy' handler.")
                success = False
            
            return success
    except Exception as e:
        print(f"FAIL: Error reading tasks: {e}")
        return False

def check_handlers():
    handlers_path = "ansible/roles/pve_base/handlers/main.yml"
    if not os.path.exists(handlers_path):
        print(f"FAIL: '{handlers_path}' is missing.")
        return False
    
    try:
        with open(handlers_path, 'r') as f:
            handlers = yaml.safe_load(f)
            found_handler = False
            for handler in handlers:
                if handler.get('name') == 'restart_pveproxy':
                    found_handler = True
                    if handler.get('ansible.builtin.service', {}).get('name') == 'pveproxy':
                        if handler.get('ansible.builtin.service', {}).get('state') == 'restarted':
                            print("OK: 'restart_pveproxy' handler found and correct.")
                            return True
            
            if not found_handler:
                print("FAIL: 'restart_pveproxy' handler missing.")
            else:
                print("FAIL: 'restart_pveproxy' handler configuration incorrect.")
            return False
    except Exception as e:
        print(f"FAIL: Error reading handlers: {e}")
        return False

if __name__ == "__main__":
    c1 = check_suppress_nag_task()
    c2 = check_handlers()
    if c1 and c2:
        print("\nSUCCESS: Suppress Subscription Nag structure is correctly implemented.")
        sys.exit(0)
    else:
        sys.exit(1)
