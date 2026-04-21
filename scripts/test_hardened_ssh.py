import os
import yaml
import sys

def check_ssh_tasks():
    tasks_path = "ansible/roles/pve_base/tasks/main.yml"
    if not os.path.exists(tasks_path):
        print(f"FAIL: '{tasks_path}' is missing.")
        return False
        
    try:
        with open(tasks_path, 'r') as f:
            tasks = yaml.safe_load(f)
            
            found_hardening_block = False
            found_permit_root = False
            found_password_auth = False
            found_notify = False
            
            def find_tasks(task_list):
                nonlocal found_hardening_block, found_permit_root, found_password_auth, found_notify
                for task in task_list:
                    if not isinstance(task, dict):
                        continue
                    name = task.get('name', '')
                    
                    if 'Hardened SSH' in name:
                        found_hardening_block = True
                    
                    if 'PermitRootLogin' in name:
                        found_permit_root = True
                        if 'notify' in task and 'restart_sshd' in str(task.get('notify')):
                            found_notify = True
                            
                    if 'PasswordAuthentication' in name:
                        found_password_auth = True
                        if 'notify' in task and 'restart_sshd' in str(task.get('notify')):
                            found_notify = True

                    if 'block' in task:
                        find_tasks(task.get('block', []))

            find_tasks(tasks)
            
            success = True
            if not found_hardening_block:
                print("FAIL: Hardened SSH Configuration block missing.")
                success = False
            else:
                print("OK: Hardened SSH block found.")
                
            if not found_permit_root:
                print("FAIL: Task to disable PermitRootLogin missing.")
                success = False
            if not found_password_auth:
                print("FAIL: Task to disable PasswordAuthentication missing.")
                success = False
            if not found_notify:
                print("FAIL: SSH hardening tasks should notify 'restart_sshd'.")
                success = False
                
            return success
    except Exception as e:
        print(f"FAIL: Error reading tasks: {e}")
        return False

def check_handlers():
    handlers_path = "ansible/roles/pve_base/handlers/main.yml"
    try:
        with open(handlers_path, 'r') as f:
            handlers = yaml.safe_load(f)
            for h in handlers:
                if h.get('name') == 'restart_sshd':
                    print("OK: 'restart_sshd' handler found.")
                    return True
            print("FAIL: 'restart_sshd' handler missing.")
            return False
    except Exception as e:
        print(f"FAIL: Error reading handlers: {e}")
        return False

if __name__ == "__main__":
    c1 = check_ssh_tasks()
    c2 = check_handlers()
    if c1 and c2:
        print("\nSUCCESS: SSH Hardening structure is correctly implemented.")
        sys.exit(0)
    else:
        sys.exit(1)
