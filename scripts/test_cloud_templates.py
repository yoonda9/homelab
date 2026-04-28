import os
import sys

import yaml

TASKS_PATH = os.environ.get(
    "TASKS_PATH", "ansible/roles/pve_base/tasks/templates.yml"
)
VARS_PATH = os.environ.get(
    "VARS_PATH", "ansible/group_vars/all.yml"
)
KVM_MODULE = "community.proxmox.proxmox_kvm"


def load_yaml(path):
    if not os.path.exists(path):
        print(f"FAIL: '{path}' is missing.")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)


def flatten_tasks(task_list):
    for task in task_list:
        if not isinstance(task, dict):
            continue
        yield task
        for key in ("block", "tasks"):
            if key in task:
                yield from flatten_tasks(task[key])


def find_tasks_by_module(tasks, module):
    results = []
    for task in flatten_tasks(tasks):
        if module in task:
            results.append(task)
    return results


def find_shell_tasks(tasks):
    results = []
    for task in flatten_tasks(tasks):
        if "ansible.builtin.shell" in task:
            results.append(task)
        elif "shell" in task and not any(
            k.startswith("community.") for k in task
        ):
            results.append(task)
    return results


def test_download_task_exists(tasks):
    for task in flatten_tasks(tasks):
        if "ansible.builtin.get_url" not in task:
            continue
        params = task.get("ansible.builtin.get_url", {})
        url = str(params.get("url", ""))
        if "pve_cloud_images" in url or "item" in url:
            print(
                "OK: Cloud image download task exists "
                "(uses get_url with loop item)."
            )
            return True
    print(
        "FAIL: No cloud image download task found using "
        "ansible.builtin.get_url with pve_cloud_images."
    )
    return False


def test_download_loops_over_cloud_images(tasks):
    for task in flatten_tasks(tasks):
        if "ansible.builtin.get_url" not in task:
            continue
        loop_expr = task.get("loop") or task.get("with_items")
        if loop_expr and "pve_cloud_images" in str(loop_expr):
            print(
                "OK: Download task loops over "
                "pve_cloud_images."
            )
            return True
    print(
        "FAIL: No download task loops over "
        "pve_cloud_images variable."
    )
    return False


def test_import_disk_task_exists(tasks):
    shell_tasks = find_shell_tasks(tasks)
    for task in shell_tasks:
        cmd = task.get("ansible.builtin.shell", "")
        if isinstance(cmd, dict):
            cmd = str(cmd.get("cmd", ""))
        cmd = str(cmd)
        if "qm" in cmd and ("importdisk" in cmd or "disk import" in cmd):
            print(
                "OK: Disk import task exists "
                "(uses qm importdisk/disk import)."
            )
            return True
    print(
        "FAIL: No disk import task found using "
        "'qm importdisk' or 'qm disk import'."
    )
    return False


def test_vm_creation_task_exists(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    for task in kvm_tasks:
        params = task.get(KVM_MODULE, {})
        if params.get("state", "") == "present":
            print(
                f"OK: VM creation task exists "
                f"(uses {KVM_MODULE} with state: present)."
            )
            return True
        if "template" not in params or not params["template"]:
            print(
                f"OK: VM creation task exists "
                f"(uses {KVM_MODULE})."
            )
            return True
    print(
        f"FAIL: No VM creation task found using "
        f"'{KVM_MODULE}'."
    )
    return False


def test_template_conversion_task_exists(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    for task in kvm_tasks:
        params = task.get(KVM_MODULE, {})
        template_val = params.get("template")
        if template_val is True or str(template_val) == "true":
            print(
                f"OK: Template conversion task exists "
                f"(uses {KVM_MODULE} with template: true)."
            )
            return True
    print(
        f"FAIL: No template conversion task found. "
        f"Expected '{KVM_MODULE}' with 'template: true'."
    )
    return False


def test_template_conversion_uses_update(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    for task in kvm_tasks:
        params = task.get(KVM_MODULE, {})
        template_val = params.get("template")
        if template_val is True or str(template_val) == "true":
            update_val = params.get("update")
            if update_val is True or str(update_val) == "true":
                print(
                    "OK: Template conversion uses "
                    "update: true (modifies existing VM)."
                )
                return True
            if params.get("state") in (
                "present", None
            ):
                print(
                    "OK: Template conversion task will "
                    "convert the VM to a template."
                )
                return True
    print(
        "FAIL: Template conversion task must use "
        "'update: true' or 'state: present' to modify "
        "the existing VM."
    )
    return False


def test_delegate_to_localhost(tasks):
    kvm_tasks = find_tasks_by_module(tasks, KVM_MODULE)
    if not kvm_tasks:
        print(
            f"FAIL: No {KVM_MODULE} tasks found to "
            f"check delegate_to."
        )
        return False
    for task in kvm_tasks:
        delegate = task.get("delegate_to", "")
        if str(delegate) != "localhost":
            name = task.get("name", "unnamed")
            print(
                f"FAIL: KVM task '{name}' missing "
                f"delegate_to: localhost (API module must "
                f"run on control node)."
            )
            return False
    print(
        f"OK: All {KVM_MODULE} tasks delegate to "
        f"localhost."
    )
    return True


def test_vars_have_cloud_image_defaults(variables):
    if "pve_cloud_images" not in variables:
        print(
            "FAIL: Missing 'pve_cloud_images' in all.yml."
        )
        return False
    images = variables["pve_cloud_images"]
    if not isinstance(images, list) or len(images) == 0:
        print(
            "FAIL: 'pve_cloud_images' must be a non-empty "
            "list in all.yml."
        )
        return False
    for idx, img in enumerate(images):
        if not isinstance(img, dict):
            print(
                f"FAIL: pve_cloud_images[{idx}] must be a "
                f"dict with url, name, vmid."
            )
            return False
        for key in ("url", "name", "vmid"):
            if key not in img:
                print(
                    f"FAIL: pve_cloud_images[{idx}] missing "
                    f"'{key}' field."
                )
                return False
    print(
        f"OK: all.yml has pve_cloud_images list with "
        f"{len(images)} image(s), each having url/name/vmid."
    )
    return True


def main():
    tasks = load_yaml(TASKS_PATH)
    variables = load_yaml(VARS_PATH)

    checks = [
        (
            "Cloud image download task exists",
            lambda: test_download_task_exists(tasks),
        ),
        (
            "Download loops over pve_cloud_images",
            lambda: test_download_loops_over_cloud_images(
                tasks
            ),
        ),
        (
            "Disk import task exists (qm importdisk)",
            lambda: test_import_disk_task_exists(tasks),
        ),
        (
            "VM creation task exists (proxmox_kvm)",
            lambda: test_vm_creation_task_exists(tasks),
        ),
        (
            "Template conversion (template: true)",
            lambda: test_template_conversion_task_exists(
                tasks
            ),
        ),
        (
            "Template conversion uses update/present",
            lambda: test_template_conversion_uses_update(
                tasks
            ),
        ),
        (
            "All KVM tasks delegate to localhost",
            lambda: test_delegate_to_localhost(tasks),
        ),
        (
            "Cloud image vars in all.yml",
            lambda: test_vars_have_cloud_image_defaults(
                variables
            ),
        ),
    ]

    results = []
    for label, check_fn in checks:
        passed = check_fn()
        results.append((label, passed))

    print()
    failed = [
        label for label, passed in results if not passed
    ]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    else:
        print(
            f"SUCCESS: All {len(results)} cloud template "
            f"checks passed."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
