import yaml
import os
import sys
import requests

def verify_keyring_fix():
    tasks_path = "ansible/roles/pve_base/tasks/main.yml"
    if not os.path.exists(tasks_path):
        print(f"FAIL: {tasks_path} not found")
        return False

    with open(tasks_path, 'r') as f:
        tasks = yaml.safe_load(f)

    # Find the "Modernize Repositories (DEB822)" block
    modernize_block = None
    for task in tasks:
        if task.get('name') == 'Modernize Repositories (DEB822)':
            modernize_block = task.get('block', [])
            break
    
    if not modernize_block:
        print("FAIL: 'Modernize Repositories (DEB822)' block not found")
        return False

    # Find the keyring download task
    download_task = None
    for task in modernize_block:
        if task.get('name') == 'Download Proxmox archive keyring':
            download_task = task
            break

    if not download_task:
        print("FAIL: 'Download Proxmox archive keyring' task not found")
        return False

    # Check 1: Correct URL
    url = download_task.get('ansible.builtin.get_url', {}).get('url', '')
    expected_url = "https://enterprise.proxmox.com/debian/proxmox-release-{{ pve_debian_release | default('trixie') }}.gpg"
    
    if url != expected_url:
        print(f"FAIL: URL '{url}' does not match expected '{expected_url}'")
        return False
    print(f"OK: URL matches expected pattern: {url}")

    # Check 2: Reachability
    # We test with 'trixie'
    test_url = "https://enterprise.proxmox.com/debian/proxmox-release-trixie.gpg"
    try:
        response = requests.head(test_url, timeout=10)
        if response.status_code == 200:
            print(f"OK: URL '{test_url}' is reachable (200 OK)")
        else:
            print(f"FAIL: URL '{test_url}' returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Error reaching URL '{test_url}': {e}")
        return False

    # Check 3: Conditional execution
    # Look for the check task
    check_pkg_task = None
    for task in modernize_block:
        if task.get('name') == 'Check if proxmox-archive-keyring is installed':
            check_pkg_task = task
            break
    
    if not check_pkg_task:
        print("FAIL: 'Check if proxmox-archive-keyring is installed' task not found")
        return False
    
    register_var = check_pkg_task.get('register')
    if not register_var:
        print("FAIL: Check task does not register a variable")
        return False

    when_clause = download_task.get('when')
    expected_when = f"{register_var}.rc != 0"
    if when_clause != expected_when:
        print(f"FAIL: 'when' clause '{when_clause}' does not match expected '{expected_when}'")
        return False
    
    print(f"OK: 'when' clause is correct: {when_clause}")
    
    return True

if __name__ == "__main__":
    if verify_keyring_fix():
        print("\nSUCCESS: Keyring fix verified in tasks and URL is reachable.")
        sys.exit(0)
    else:
        sys.exit(1)
