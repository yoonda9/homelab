import os
import yaml
import sys

def check_stability_tasks():
    tasks_path = "ansible/roles/pve_base/tasks/main.yml"
    if not os.path.exists(tasks_path):
        print(f"FAIL: '{tasks_path}' is missing.")
        return False
        
    try:
        with open(tasks_path, 'r') as f:
            content = f.read()
            # Reload to parse properly if it was a block
            f.seek(0)
            tasks = yaml.safe_load(f)
            
            found_dist_upgrade = False
            found_firmware = False
            
            def find_tasks(task_list):
                nonlocal found_dist_upgrade, found_firmware
                for task in task_list:
                    if not isinstance(task, dict):
                        continue
                    name = task.get('name', '')
                    
                    if 'Stability Updates' in name or 'dist-upgrade' in name.lower():
                        found_dist_upgrade = True
                        
                    if 'Firmware Management' in name or 'microcode' in name.lower() or 'fwupd' in name.lower():
                        found_firmware = True
                        if 'fwupd' in str(task.get('ansible.builtin.apt', {}).get('name', '')):
                            print("OK: 'fwupd' package installation found.")
                        if 'fwupdmgr' in str(task.get('ansible.builtin.shell', {}).get('cmd', '')):
                            print("OK: 'fwupdmgr' update command found.")
                    
                    if 'block' in task:
                        find_tasks(task.get('block', []))
                    if 'tasks' in task:
                        find_tasks(task.get('tasks', []))

            find_tasks(tasks)
            
            success = True
            if not found_dist_upgrade:
                print("FAIL: Stability Updates (dist-upgrade) task missing.")
                success = False
            else:
                print("OK: Stability Updates task found.")
                
            if not found_firmware:
                print("FAIL: Firmware Management (microcode) task missing.")
                success = False
            else:
                print("OK: Firmware Management task found.")
                
            return success
    except Exception as e:
        print(f"FAIL: Error reading tasks: {e}")
        return False

if __name__ == "__main__":
    if check_stability_tasks():
        print("\nSUCCESS: Stability Updates and Firmware Management tasks are implemented.")
        sys.exit(0)
    else:
        sys.exit(1)
