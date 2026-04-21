import os
import yaml
import sys

def check_fail2ban_tasks():
    tasks_path = "ansible/roles/pve_base/tasks/main.yml"
    if not os.path.exists(tasks_path):
        print(f"FAIL: '{tasks_path}' is missing.")
        return False
        
    try:
        with open(tasks_path, 'r') as f:
            tasks = yaml.safe_load(f)
            
            found_install = False
            found_config = False
            found_notify = False
            
            def find_tasks(task_list):
                nonlocal found_install, found_config, found_notify
                for task in task_list:
                    if not isinstance(task, dict):
                        continue
                    name = task.get('name', '')
                    
                    if 'Install Fail2Ban' in name:
                        found_install = True
                    
                    if 'Configure Fail2Ban' in name or 'jail.local' in str(task.get('ansible.builtin.copy', {}).get('dest', '')):
                        found_config = True
                        if 'notify' in task and 'restart_fail2ban' in str(task.get('notify')):
                            found_notify = True
                        
                        content = task.get('ansible.builtin.copy', {}).get('content', '')
                        if '[proxmox]' in content and 'port = 8006' in content:
                            print("OK: Proxmox UI jail (port 8006) found in jail.local.")
                        else:
                            print("FAIL: Proxmox UI jail (port 8006) missing from jail.local.")
                            success = False

                    if 'block' in task:
                        find_tasks(task.get('block', []))

            find_tasks(tasks)
            
            success = True
            if not found_install:
                print("FAIL: Task to install Fail2Ban missing.")
                success = False
            if not found_config:
                print("FAIL: Task to configure Fail2Ban (jail.local) missing.")
                success = False
            if not found_notify:
                print("FAIL: Fail2Ban configuration task should notify 'restart_fail2ban'.")
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
                if h.get('name') == 'restart_fail2ban':
                    print("OK: 'restart_fail2ban' handler found.")
                    return True
            print("FAIL: 'restart_fail2ban' handler missing.")
            return False
    except Exception as e:
        print(f"FAIL: Error reading handlers: {e}")
        return False

if __name__ == "__main__":
    c1 = check_fail2ban_tasks()
    c2 = check_handlers()
    if c1 and c2:
        print("\nSUCCESS: Fail2Ban structure is correctly implemented.")
        sys.exit(0)
    else:
        sys.exit(1)
