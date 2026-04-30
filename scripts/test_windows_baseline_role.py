"""Adversarial smoke test for the Step 3 windows_baseline Ansible role.

Mirrors `scripts/test_firewall.py`'s allow-list / deny-list / raw-grep
shape, scoped to `ansible.windows.*` modules. Plain main runner — no
pytest.

Coverage:
1. Allow-list: every task in the role uses a module in
   ALLOWED_MODULES (no `ansible.builtin.*` or `ansible.posix.*`).
2. Deny-list: no task references any name in HALLUCINATED_MODULES.
3. Raw-file scan: HALLUCINATED_MODULES strings absent from the file
   body, including comments — a stale typo in a `# TODO` comment is
   still a hazard.

The HALLUCINATED_MODULES list catches plausible-sounding but
non-existent module names that an LLM autocomplete could slip in:
- `ansible.windows.win_static_ip` (doesn't exist; static IP is set
  via `win_powershell` running `New-NetIPAddress`).
- `ansible.windows.win_netipaddress` (doesn't exist).
- `community.windows.win_static_ip` (community.windows is real but
  this module isn't).
- `ansible.windows.win_dnsclient` (real one is `win_dns_client` —
  underscore difference, easy typo).
"""

import os
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("FAIL: PyYAML is required for the test harness.")
    sys.exit(2)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_PATH = os.path.join(
    REPO_ROOT, "ansible", "roles", "windows_baseline", "tasks", "main.yml"
)
META_PATH = os.path.join(
    REPO_ROOT, "ansible", "roles", "windows_baseline", "meta", "main.yml"
)

# Conservative allow-list scoped to ansible.windows.*. The role today
# uses only win_copy + win_powershell; the broader set is allowed so a
# narrow Builder addition (e.g. win_command) doesn't trip this gate.
# MUST NOT include any ansible.builtin.* or ansible.posix.* — those are
# Linux-only and would silently fail (or silently no-op) on Windows.
ALLOWED_MODULES = {
    "ansible.windows.win_copy",
    "ansible.windows.win_powershell",
    "ansible.windows.win_command",
    "ansible.windows.win_shell",
    "ansible.windows.win_get_url",
}

# Plausible-sounding but non-existent module names (verified absent
# from ansible.windows 3.5.0 module index 2026-04-30).
HALLUCINATED_MODULES = {
    "ansible.windows.win_static_ip",
    "ansible.windows.win_netipaddress",
    "community.windows.win_static_ip",
    "ansible.windows.win_dnsclient",
}


def load_tasks():
    with open(TASKS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def flatten_tasks(task_list):
    """Recursively flatten tasks including block contents."""
    result = []
    for task in task_list or []:
        if not isinstance(task, dict):
            continue
        result.append(task)
        if "block" in task:
            result.extend(flatten_tasks(task["block"]))
        if "rescue" in task:
            result.extend(flatten_tasks(task["rescue"]))
        if "always" in task:
            result.extend(flatten_tasks(task["always"]))
    return result


def get_module_name(task):
    """Extract the Ansible module name from a task dict."""
    skip_keys = {
        "name", "block", "rescue", "always", "when", "register",
        "changed_when", "failed_when", "notify", "delegate_to", "tags",
        "vars", "become", "become_user", "ignore_errors", "no_log",
        "environment", "loop", "with_items", "until", "retries", "delay",
    }
    for key in task:
        if key not in skip_keys and "." in key:
            return key
    return None


def test_role_files_exist():
    """tasks/main.yml + meta/main.yml must exist and parse."""
    failures = []
    for path in (TASKS_PATH, META_PATH):
        if not os.path.exists(path):
            failures.append(f"missing role file '{path}'")
            continue
        with open(path, "r", encoding="utf-8") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as exc:
                failures.append(f"YAML parse error in '{path}': {exc}")
    return failures


def test_only_allowed_modules():
    """Every task uses a module name in ALLOWED_MODULES."""
    if not os.path.exists(TASKS_PATH):
        return [f"missing '{TASKS_PATH}' (cannot scan modules)"]
    tasks = load_tasks()
    if not isinstance(tasks, list):
        return [
            f"'{TASKS_PATH}' must be a YAML list of tasks; "
            f"got {type(tasks).__name__}."
        ]
    flat = flatten_tasks(tasks)
    failures = []
    for task in flat:
        module = get_module_name(task)
        if module is None:
            # Block-only nodes (no module) are valid; their children
            # are picked up by flatten_tasks.
            if "block" in task:
                continue
            failures.append(
                f"task '{task.get('name', 'unnamed')}' has no recognizable "
                f"module key (expected one of {sorted(ALLOWED_MODULES)})."
            )
            continue
        if module not in ALLOWED_MODULES:
            failures.append(
                f"Unknown module '{module}' in task "
                f"'{task.get('name', 'unnamed')}'. Allowed Windows-only "
                f"modules: {sorted(ALLOWED_MODULES)}. (No ansible.builtin.* "
                f"or ansible.posix.* allowed — Linux-only.)"
            )
    return failures


def test_no_hallucinated_modules_in_tasks():
    """No parsed task references a name in HALLUCINATED_MODULES."""
    if not os.path.exists(TASKS_PATH):
        return [f"missing '{TASKS_PATH}' (cannot scan tasks)"]
    flat = flatten_tasks(load_tasks() or [])
    failures = []
    for task in flat:
        module = get_module_name(task)
        if module in HALLUCINATED_MODULES:
            failures.append(
                f"Hallucinated module '{module}' in task "
                f"'{task.get('name', 'unnamed')}' — module does not "
                f"exist in ansible.windows or community.windows."
            )
    return failures


def test_no_hallucinated_modules_in_raw_file():
    """Substring scan over the full file body, including comments.

    Mirrors `test_firewall.test_no_hallucinated_modules_grep`. Catches
    a stale module name in a comment that the YAML parser would skip.
    """
    if not os.path.exists(TASKS_PATH):
        return [f"missing '{TASKS_PATH}' (cannot scan raw file)"]
    with open(TASKS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    failures = []
    for mod in HALLUCINATED_MODULES:
        if mod in content:
            failures.append(
                f"Hallucinated module '{mod}' found in raw file "
                f"'{TASKS_PATH}' (even in a comment, this is a smell — "
                f"delete the reference)."
            )
    return failures


def main():
    if not os.path.exists(TASKS_PATH):
        print(
            f"FAIL: '{TASKS_PATH}' is missing. The windows_baseline "
            f"role must exist with at least tasks/main.yml + meta/main.yml."
        )
        sys.exit(1)

    tests = [
        ("Role files exist and parse", test_role_files_exist),
        ("Only allowed ansible.windows.* modules", test_only_allowed_modules),
        ("No hallucinated modules (parsed tasks)", test_no_hallucinated_modules_in_tasks),
        ("No hallucinated modules (raw file)", test_no_hallucinated_modules_in_raw_file),
    ]

    all_passed = True
    for name, test_fn in tests:
        failures = test_fn()
        if failures:
            all_passed = False
            for f in failures:
                print(f"FAIL [{name}]: {f}")
        else:
            print(f"OK: {name}")

    if all_passed:
        print(f"\nSUCCESS: All {len(tests)} windows_baseline checks passed.")
        sys.exit(0)
    else:
        print("\nFAILURE: Some windows_baseline checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
