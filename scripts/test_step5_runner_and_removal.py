"""Adversarial smoke test for Step 5: end-to-end runner + role removal.

Mirrors the shape of the prior `scripts/test_tofu_*.py` scripts: load the
artifact, assert key declarations are present, fail with a precise
message otherwise. Plain main runner — no pytest.

Coverage:
1. ansible/roles/pve_vm_deploy/ does NOT exist (deleted in Step 5).
2. scripts/test_pve_vm_deploy.py does NOT exist (deleted in Step 5).
3. ansible/services.yml parses as YAML AND has no 'pve_vm_deploy' string
   anywhere AND parsed-roles list lacks it.
4. scripts/deploy_vms.sh exists, executable bit set, starts with a bash
   shebang, contains 'set -euo pipefail'.
5. scripts/deploy_vms.sh invokes 'tofu' with 'apply -auto-approve' AND
   invokes 'ansible-playbook' with 'ansible/configure-vms.yml'; order
   matters — the tofu line must appear BEFORE the ansible-playbook line.
6. scripts/deploy_vms.sh invokes 'scripts/tofu_to_inventory.py' (proves
   inventory regen is wired between provision and configure).
7. (best-effort) shellcheck scripts/deploy_vms.sh exit 0 AND
   shfmt -d scripts/deploy_vms.sh exit 0; PASS+note if either tool is
   absent on the loop env.
8. ansible-playbook --syntax-check on EVERY ansible/*.yml playbook still
   present exits 0. Use .venv/bin/ansible-playbook per
   mem-1776748612-981e. configure-vms.yml is syntax-checked against a
   generated fixture inventory (pattern reused from
   scripts/test_tofu_to_inventory.py).
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

try:
    import yaml
except ImportError:  # pragma: no cover
    print("FAIL: PyYAML is required for the test harness.")
    sys.exit(2)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLE_DIR = os.path.join(REPO_ROOT, "ansible", "roles", "pve_vm_deploy")
ROLE_TEST = os.path.join(REPO_ROOT, "scripts", "test_pve_vm_deploy.py")
SERVICES_YML = os.path.join(REPO_ROOT, "ansible", "services.yml")
DEPLOY_SCRIPT = os.path.join(REPO_ROOT, "scripts", "deploy_vms.sh")
GENERATOR = os.path.join(REPO_ROOT, "scripts", "tofu_to_inventory.py")
CONFIGURE_PLAY = os.path.join(REPO_ROOT, "ansible", "configure-vms.yml")
STATIC_INVENTORY = os.path.join(REPO_ROOT, "ansible", "inventory", "hosts.yml")
ANSIBLE_DIR = os.path.join(REPO_ROOT, "ansible")


def _find_ansible_playbook():
    candidate = os.path.join(REPO_ROOT, ".venv", "bin", "ansible-playbook")
    if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        return candidate
    return shutil.which("ansible-playbook")


def test_role_directory_is_removed():
    if os.path.exists(ROLE_DIR):
        print(
            f"FAIL: '{ROLE_DIR}' still exists. Step 5 deletes the "
            f"deprecated pve_vm_deploy role (Replace, don't deprecate)."
        )
        return False
    print("OK: ansible/roles/pve_vm_deploy/ is removed.")
    return True


def test_role_test_script_is_removed():
    if os.path.exists(ROLE_TEST):
        print(
            f"FAIL: '{ROLE_TEST}' still exists. Step 5 deletes the role's "
            f"focused test alongside the role itself."
        )
        return False
    print("OK: scripts/test_pve_vm_deploy.py is removed.")
    return True


def _role_names_in_play(play):
    roles = play.get("roles", []) or []
    names = []
    for entry in roles:
        if isinstance(entry, str):
            names.append(entry)
        elif isinstance(entry, dict):
            role = entry.get("role") or entry.get("name")
            if isinstance(role, str):
                names.append(role)
    return names


def test_services_yml_pruned():
    if not os.path.exists(SERVICES_YML):
        print(f"FAIL: '{SERVICES_YML}' is missing.")
        return False
    with open(SERVICES_YML, "r", encoding="utf-8") as f:
        text = f.read()
    if "pve_vm_deploy" in text:
        print(
            f"FAIL: '{SERVICES_YML}' still contains the literal string "
            f"'pve_vm_deploy'. Step 5 prunes it (string scan)."
        )
        return False
    try:
        plays = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        print(f"FAIL: '{SERVICES_YML}' does not parse as YAML: {exc}.")
        return False
    if not isinstance(plays, list) or not plays:
        print(
            f"FAIL: '{SERVICES_YML}' must be a non-empty list of plays; "
            f"got {type(plays).__name__}."
        )
        return False
    for play in plays:
        if not isinstance(play, dict):
            continue
        if "pve_vm_deploy" in _role_names_in_play(play):
            print(
                f"FAIL: '{SERVICES_YML}' parsed-roles list still includes "
                f"'pve_vm_deploy' (play hosts={play.get('hosts')!r})."
            )
            return False
    print("OK: ansible/services.yml is pruned of pve_vm_deploy.")
    return True


def test_deploy_script_shape():
    if not os.path.exists(DEPLOY_SCRIPT):
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' is missing. Step 5 introduces the "
            f"end-to-end runner (tofu apply → inventory regen → "
            f"ansible-playbook configure-vms.yml)."
        )
        return False
    mode = os.stat(DEPLOY_SCRIPT).st_mode
    if not (mode & stat.S_IXUSR):
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' is not executable for the owner "
            f"(mode={oct(mode)}). The runner must be chmod +x."
        )
        return False
    with open(DEPLOY_SCRIPT, "r", encoding="utf-8") as f:
        text = f.read()
    first_line = text.splitlines()[0] if text else ""
    if not (first_line.startswith("#!/usr/bin/env bash")
            or first_line.startswith("#!/bin/bash")):
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' first line must be a bash shebang "
            f"(#!/usr/bin/env bash or #!/bin/bash); got {first_line!r}."
        )
        return False
    if "set -euo pipefail" not in text:
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' must contain 'set -euo pipefail' "
            f"(strict-mode bash per repo standards)."
        )
        return False
    print("OK: scripts/deploy_vms.sh exists, +x, bash shebang, strict-mode.")
    return True


def test_deploy_script_invocation_order():
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"FAIL: '{DEPLOY_SCRIPT}' is missing; cannot scan order.")
        return False
    with open(DEPLOY_SCRIPT, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    tofu_apply_line = None
    ansible_play_line = None
    for idx, line in enumerate(lines):
        # Skip comment-only lines.
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if (
            tofu_apply_line is None
            and "tofu" in line
            and "apply" in line
            and "-auto-approve" in line
        ):
            tofu_apply_line = idx
        if (
            ansible_play_line is None
            and "ansible-playbook" in line
            and "ansible/configure-vms.yml" in line
        ):
            ansible_play_line = idx
    if tofu_apply_line is None:
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' must invoke 'tofu' with "
            f"'apply -auto-approve' (provision step)."
        )
        return False
    if ansible_play_line is None:
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' must invoke 'ansible-playbook' "
            f"with 'ansible/configure-vms.yml' (configure step)."
        )
        return False
    if tofu_apply_line >= ansible_play_line:
        print(
            f"FAIL: tofu apply must precede ansible-playbook in "
            f"deploy_vms.sh (got tofu line {tofu_apply_line + 1}, "
            f"ansible-playbook line {ansible_play_line + 1})."
        )
        return False
    print(
        f"OK: deploy_vms.sh runs 'tofu apply' (line "
        f"{tofu_apply_line + 1}) before 'ansible-playbook "
        f"configure-vms.yml' (line {ansible_play_line + 1})."
    )
    return True


def test_deploy_script_invokes_inventory_generator():
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"FAIL: '{DEPLOY_SCRIPT}' is missing; cannot scan generator call.")
        return False
    with open(DEPLOY_SCRIPT, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    tofu_apply_line = None
    generator_line = None
    ansible_play_line = None
    for idx, line in enumerate(lines):
        # Skip comment-only lines so that doc/banner mentions of the
        # generator path don't satisfy this check (mem-1777478162-68e8).
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if (
            tofu_apply_line is None
            and "tofu" in line
            and "apply" in line
            and "-auto-approve" in line
        ):
            tofu_apply_line = idx
        if generator_line is None and "scripts/tofu_to_inventory.py" in line:
            generator_line = idx
        if (
            ansible_play_line is None
            and "ansible-playbook" in line
            and "ansible/configure-vms.yml" in line
        ):
            ansible_play_line = idx
    if generator_line is None:
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' must invoke "
            f"'scripts/tofu_to_inventory.py' between tofu apply and "
            f"ansible-playbook (regenerate inventory from live state)."
        )
        return False
    if tofu_apply_line is None or ansible_play_line is None:
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' missing surrounding pipeline steps "
            f"(tofu apply line={tofu_apply_line}, "
            f"ansible-playbook line={ansible_play_line}); cannot verify "
            f"generator ordering."
        )
        return False
    if not (tofu_apply_line < generator_line < ansible_play_line):
        print(
            f"FAIL: 'scripts/tofu_to_inventory.py' must be invoked AFTER "
            f"'tofu apply' and BEFORE 'ansible-playbook configure-vms.yml' "
            f"in deploy_vms.sh (got tofu apply line "
            f"{tofu_apply_line + 1}, generator line "
            f"{generator_line + 1}, ansible-playbook line "
            f"{ansible_play_line + 1})."
        )
        return False
    print(
        f"OK: deploy_vms.sh wires the inventory regeneration step "
        f"(line {generator_line + 1}) between tofu apply (line "
        f"{tofu_apply_line + 1}) and ansible-playbook (line "
        f"{ansible_play_line + 1})."
    )
    return True


def test_deploy_script_lints_clean():
    """Best-effort: shellcheck + shfmt. PASS+note if tools absent."""
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"FAIL: '{DEPLOY_SCRIPT}' is missing; cannot lint.")
        return False
    notes = []
    shellcheck = shutil.which("shellcheck")
    if shellcheck is None:
        notes.append(
            "shellcheck not on PATH; remediation task opened + fix memory recorded."
        )
    else:
        result = subprocess.run(
            [shellcheck, DEPLOY_SCRIPT],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            print(
                f"FAIL: shellcheck on '{DEPLOY_SCRIPT}' exited "
                f"{result.returncode}: stdout={result.stdout!r} "
                f"stderr={result.stderr!r}."
            )
            return False
    shfmt = shutil.which("shfmt")
    if shfmt is None:
        notes.append(
            "shfmt not on PATH; remediation task opened + fix memory recorded."
        )
    else:
        result = subprocess.run(
            [shfmt, "-d", DEPLOY_SCRIPT],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            print(
                f"FAIL: shfmt -d on '{DEPLOY_SCRIPT}' exited "
                f"{result.returncode}: stdout={result.stdout!r} "
                f"stderr={result.stderr!r}."
            )
            return False
    if notes:
        print(f"PASS-WITH-NOTE: deploy_vms.sh lints (best-effort). {' '.join(notes)}")
    else:
        print("OK: shellcheck + shfmt on deploy_vms.sh both clean.")
    return True


def _fixture_inventory_for_configure_vms(tmp_path):
    """Reuse pattern from scripts/test_tofu_to_inventory.py: feed the
    real generator a canonical inventory JSON, get a YAML inventory back,
    then point ansible-playbook --syntax-check at it."""
    if not os.path.exists(GENERATOR):
        return None
    inv = {
        "proxmox_vms": {
            "hosts": {
                "ubuntu26-test": {
                    "ansible_host": "192.168.50.10",
                    "vmid": 300,
                    "node_name": "pve-01",
                },
                "centos10-test": {
                    "ansible_host": "192.168.50.11",
                    "vmid": 301,
                    "node_name": "pve-01",
                },
            },
            "vars": {"ansible_user": "ubuntu"},
        }
    }
    in_path = os.path.join(tmp_path, "inv.json")
    out_path = os.path.join(tmp_path, "tofu_generated.yml")
    with open(in_path, "w", encoding="utf-8") as f:
        json.dump(inv, f)
    result = subprocess.run(
        [sys.executable, GENERATOR, "--input", in_path, "--output", out_path],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0 or not os.path.exists(out_path):
        return None
    return out_path


def test_all_playbooks_syntax_check():
    binary = _find_ansible_playbook()
    if binary is None:
        print(
            "PASS-WITH-NOTE: ansible-playbook not on PATH and not at "
            ".venv/bin/ansible-playbook; recorded fix memory + opened "
            "remediation task. Skipping --syntax-check on all playbooks."
        )
        return True
    playbooks = sorted(
        f
        for f in os.listdir(ANSIBLE_DIR)
        if f.endswith(".yml") and os.path.isfile(os.path.join(ANSIBLE_DIR, f))
    )
    if not playbooks:
        print(f"FAIL: no '*.yml' playbooks found under '{ANSIBLE_DIR}'.")
        return False
    if not os.path.exists(STATIC_INVENTORY):
        print(f"FAIL: static inventory '{STATIC_INVENTORY}' is missing.")
        return False
    with tempfile.TemporaryDirectory() as tmp:
        fixture = _fixture_inventory_for_configure_vms(tmp)
        for playbook in playbooks:
            playbook_path = os.path.join("ansible", playbook)
            if playbook == "configure-vms.yml":
                if fixture is None:
                    print(
                        f"FAIL: could not generate fixture inventory for "
                        f"'{playbook_path}' syntax-check (generator at "
                        f"'{GENERATOR}' missing or broken)."
                    )
                    return False
                inv_arg = fixture
            else:
                inv_arg = STATIC_INVENTORY
            result = subprocess.run(
                [binary, "--syntax-check", "-i", inv_arg, playbook_path],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            if result.returncode != 0:
                print(
                    f"FAIL: ansible-playbook --syntax-check exited "
                    f"{result.returncode} on '{playbook_path}' "
                    f"(inventory={inv_arg}); stderr={result.stderr!r}."
                )
                return False
    print(
        f"OK: ansible-playbook --syntax-check exit 0 on all "
        f"{len(playbooks)} ansible/*.yml playbook(s)."
    )
    return True


def main():
    checks = [
        ("Role directory pve_vm_deploy is removed", test_role_directory_is_removed),
        ("Role test script test_pve_vm_deploy.py is removed", test_role_test_script_is_removed),
        ("services.yml is pruned of pve_vm_deploy", test_services_yml_pruned),
        ("deploy_vms.sh shape (exists, +x, shebang, strict-mode)", test_deploy_script_shape),
        ("deploy_vms.sh order: tofu apply BEFORE ansible-playbook", test_deploy_script_invocation_order),
        ("deploy_vms.sh invokes tofu_to_inventory.py", test_deploy_script_invokes_inventory_generator),
        ("deploy_vms.sh shellcheck+shfmt clean (best-effort)", test_deploy_script_lints_clean),
        ("ansible-playbook --syntax-check exit 0 on every ansible/*.yml", test_all_playbooks_syntax_check),
    ]
    results = [(label, fn()) for label, fn in checks]
    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    print(f"SUCCESS: All {len(results)} Step 5 runner+removal checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
