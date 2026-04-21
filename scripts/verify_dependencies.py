import sys
import subprocess

def check_python_lib(lib_name):
    try:
        __import__(lib_name)
        print(f"OK: Python library '{lib_name}' is installed.")
        return True
    except ImportError:
        print(f"FAIL: Python library '{lib_name}' is NOT installed.")
        return False

def check_ansible_collection(collection_name):
    import shutil
    import os
    
    # Try to find ansible-galaxy in the PATH or near the python executable
    ansible_galaxy = shutil.which("ansible-galaxy")
    if not ansible_galaxy:
        # Check if we are in a venv
        venv_bin = os.path.dirname(sys.executable)
        potential_path = os.path.join(venv_bin, "ansible-galaxy")
        if os.path.exists(potential_path):
            ansible_galaxy = potential_path
            
    if not ansible_galaxy:
        print("FAIL: 'ansible-galaxy' command not found.")
        return False
        
    try:
        result = subprocess.run(
            [ansible_galaxy, "collection", "list", collection_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and collection_name in result.stdout:
            print(f"OK: Ansible collection '{collection_name}' is installed.")
            return True
        else:
            print(f"FAIL: Ansible collection '{collection_name}' is NOT installed.")
            return False
    except Exception as e:
        print(f"FAIL: Error running {ansible_galaxy}: {e}")
        return False

libs_ok = all([
    check_python_lib("proxmoxer"),
    check_python_lib("requests")
])

ansible_ok = check_ansible_collection("community.proxmox")

if not (libs_ok and ansible_ok):
    sys.exit(1)
