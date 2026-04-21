import os
import yaml
import sys

def check_all_yml():
    all_yml_path = "ansible/group_vars/all.yml"
    if not os.path.exists(all_yml_path):
        print(f"FAIL: '{all_yml_path}' is missing.")
        return False
    try:
        with open(all_yml_path, 'r') as f:
            data = yaml.safe_load(f)
            release = data.get('pve_debian_release')
            if release != 'trixie':
                print(f"FAIL: 'pve_debian_release' is set to '{release}', expected 'trixie' for PVE 9.1.")
                return False
            print("OK: 'pve_debian_release' is set to 'trixie'.")
            return True
    except Exception as e:
        print(f"FAIL: Error reading all.yml: {e}")
        return False

def check_modernize_repositories_tasks():
    tasks_path = "ansible/roles/pve_base/tasks/main.yml"
    if not os.path.exists(tasks_path):
        print(f"FAIL: '{tasks_path}' is missing.")
        return False
        
    try:
        with open(tasks_path, 'r') as f:
            tasks = yaml.safe_load(f)
            found_python_debian = False
            found_enterprise_disabled = False
            found_no_sub_list_disabled = False
            found_no_subscription_enabled = False
            found_keyring_correct = False
            found_keyring_download = False
            keyring_url_ok = False
            deb822_uris_ok = False

            apt_update_index = -1
            disable_legacy_indices = []
            keyring_download_index = -1
            
            current_index = 0
            
            def check_tasks(task_list):
                nonlocal found_python_debian, found_enterprise_disabled, found_no_sub_list_disabled, found_no_subscription_enabled, found_keyring_correct, found_keyring_download
                nonlocal apt_update_index, disable_legacy_indices, keyring_download_index, current_index
                for task in task_list:
                    if not isinstance(task, dict):
                        continue
                    name = task.get('name', '')
                    
                    if 'python3-debian' in name:
                        found_python_debian = True
                        if task.get('ansible.builtin.apt', {}).get('update_cache', False):
                            apt_update_index = current_index
                    
                    if 'Disable' in name and 'enterprise' in name.lower():
                        if task.get('ansible.builtin.file', {}).get('state') == 'absent':
                            found_enterprise_disabled = True
                            disable_legacy_indices.append(current_index)
                            
                    if 'Disable' in name and 'no-subscription.list' in name.lower():
                        if task.get('ansible.builtin.file', {}).get('state') == 'absent':
                            found_no_sub_list_disabled = True
                            disable_legacy_indices.append(current_index)
                            
                    if 'Enable' in name and 'no-subscription' in name.lower() and 'DEB822' in name:
                        found_no_subscription_enabled = True
                        repo = task.get('ansible.builtin.deb822_repository', {})
                        signed_by = repo.get('signed_by', '')
                        if '/usr/share/keyrings/proxmox-archive-keyring.gpg' in signed_by:
                            found_keyring_correct = True
                        uris = repo.get('uris', '')
                        if 'download.proxmox.com' in uris:
                            nonlocal deb822_uris_ok
                            deb822_uris_ok = True
                        elif 'enterprise.proxmox.com' in uris:
                            print(f"FAIL: DEB822 uris uses enterprise endpoint. Must use 'download.proxmox.com'.")
                            deb822_uris_ok = False
                            
                    if 'Download Proxmox archive keyring' in name:
                        found_keyring_download = True
                        keyring_download_index = current_index
                        url = task.get('ansible.builtin.get_url', {}).get('url', '')
                        if 'enterprise.proxmox.com' in url:
                            print(f"FAIL: Keyring URL uses enterprise endpoint '{url}'. Must use 'download.proxmox.com'.")
                            nonlocal keyring_url_ok
                            keyring_url_ok = False
                        elif 'download.proxmox.com' in url:
                            keyring_url_ok = True
                        else:
                            print(f"FAIL: Keyring URL '{url}' is unrecognized. Expected 'download.proxmox.com'.")
                            keyring_url_ok = False
                    
                    current_index += 1
                    if 'block' in task:
                        check_tasks(task['block'])

            check_tasks(tasks)
                    
            success = True
            if not found_python_debian:
                print("FAIL: Task to install 'python3-debian' missing.")
                success = False
            if not found_enterprise_disabled:
                print("FAIL: Disable enterprise repository task missing or incorrect.")
                success = False
            if not found_no_sub_list_disabled:
                print("FAIL: Disable pve-no-subscription.list (legacy) task missing.")
                success = False
            if not found_no_subscription_enabled:
                print("FAIL: Enable no-subscription DEB822 repository task missing.")
                success = False
            if not found_keyring_correct:
                print("FAIL: Keyring path in 'signed_by' should be '/usr/share/keyrings/proxmox-archive-keyring.gpg'.")
                success = False
            if not found_keyring_download:
                print("FAIL: Task to download Proxmox archive keyring missing.")
                success = False
            elif not keyring_url_ok:
                print("FAIL: Keyring download URL validation failed (see above).")
                success = False
            else:
                print("OK: Keyring download URL uses 'download.proxmox.com'.")

            if not deb822_uris_ok:
                print("FAIL: DEB822 repository 'uris' must use 'download.proxmox.com'.")
                success = False
            else:
                print("OK: DEB822 repository 'uris' uses 'download.proxmox.com'.")

            # Order check
            if apt_update_index != -1 and disable_legacy_indices:
                for idx in disable_legacy_indices:
                    if idx > apt_update_index:
                        print(f"FAIL: Disable legacy repository task (index {idx}) must come BEFORE 'apt update' (index {apt_update_index}).")
                        success = False
            
            if keyring_download_index != -1 and apt_update_index != -1:
                if keyring_download_index > apt_update_index:
                    print(f"FAIL: Keyring download (index {keyring_download_index}) must come BEFORE 'apt update' (index {apt_update_index}).")
                    success = False
                else:
                    print("OK: Keyring download occurs before apt update.")
            
            return success
    except Exception as e:
        print(f"FAIL: Error reading tasks: {e}")
        return False

if __name__ == "__main__":
    c1 = check_all_yml()
    c2 = check_modernize_repositories_tasks()
    if c1 and c2:
        print("\nSUCCESS: Modernize repositories structure is correctly updated for PVE 9.1.")
        sys.exit(0)
    else:
        sys.exit(1)
