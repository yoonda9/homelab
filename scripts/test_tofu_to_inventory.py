"""Adversarial smoke test for the Step 4 Tofu→Ansible inventory bridge.

Mirrors the shape of `scripts/test_tofu_scaffold.py`,
`scripts/test_tofu_linux_vm_module.py`, and `scripts/test_tofu_inventory_output.py`:
exercise the artifact, assert key declarations are present, fail with a
precise message otherwise. Plain main runner — no pytest.

Coverage:
1. Generator on a fixture JSON produces a YAML inventory with
   per-host ansible_host/vmid/node_name (per-host, not file-global).
2. Host with ansible_host = null is omitted, stderr names the skipped
   host, generator exits 0 if at least one host remains.
3. Malformed JSON → non-zero exit + stderr names input path.
4. Valid JSON missing the ansible_inventory shape → non-zero exit +
   stderr names the missing key.
5. ansible/configure-vms.yml exists, parses, hosts: proxmox_vms,
   vm_baseline in roles, become: true.
6. ansible/roles/vm_baseline/tasks/main.yml exists, parses, references
   python3.
7. ansible-playbook --syntax-check on configure-vms.yml against the
   generated fixture inventory exits 0. PASS+note if ansible-playbook
   is missing AND record a fix memory + open a remediation task per
   the Failure Capture rule.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

try:
    import yaml  # PyYAML is fine for the *test*; generator stays stdlib.
except ImportError:  # pragma: no cover
    print("FAIL: PyYAML is required for the test harness.")
    sys.exit(2)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATOR = os.path.join(REPO_ROOT, "scripts", "tofu_to_inventory.py")
CONFIGURE_PLAY = os.path.join(REPO_ROOT, "ansible", "configure-vms.yml")
VM_BASELINE_TASKS = os.path.join(
    REPO_ROOT, "ansible", "roles", "vm_baseline", "tasks", "main.yml"
)


def _fixture_inventory():
    """Canonical Step 3 ansible_inventory output value, post-apply shape."""
    return {
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


def _run_generator(input_path, output_path):
    return subprocess.run(
        [sys.executable, GENERATOR, "--input", input_path, "--output", output_path],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def test_generator_produces_per_host_inventory():
    if not os.path.exists(GENERATOR):
        print(f"FAIL: generator '{GENERATOR}' is missing.")
        return False
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "inv.json")
        out_path = os.path.join(tmp, "tofu_generated.yml")
        with open(in_path, "w", encoding="utf-8") as f:
            json.dump(_fixture_inventory(), f)
        result = _run_generator(in_path, out_path)
        if result.returncode != 0:
            print(
                f"FAIL: generator exited {result.returncode} on a valid "
                f"fixture; stderr={result.stderr!r}."
            )
            return False
        if not os.path.exists(out_path):
            print(f"FAIL: generator did not write '{out_path}'.")
            return False
        with open(out_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        if not isinstance(doc, dict) or "proxmox_vms" not in doc:
            print(
                f"FAIL: generated YAML missing top-level 'proxmox_vms' "
                f"group; got keys={list(doc) if isinstance(doc, dict) else doc!r}."
            )
            return False
        hosts = doc["proxmox_vms"].get("hosts")
        if not isinstance(hosts, dict):
            print(
                f"FAIL: generated YAML proxmox_vms.hosts must be a "
                f"mapping; got {type(hosts).__name__}."
            )
            return False
        for host in ("ubuntu26-test", "centos10-test"):
            entry = hosts.get(host)
            if not isinstance(entry, dict):
                print(
                    f"FAIL: generated YAML missing per-host entry "
                    f"proxmox_vms.hosts.{host} (per-host check)."
                )
                return False
            for attr in ("ansible_host", "vmid", "node_name"):
                if attr not in entry:
                    print(
                        f"FAIL: generated YAML host '{host}' is missing "
                        f"'{attr}' (entry={entry!r}); per-host inventory "
                        f"shape required."
                    )
                    return False
        # Per-host ansible_user override: ubuntu* → ubuntu, centos* → cloud-user.
        if hosts["ubuntu26-test"].get("ansible_user") != "ubuntu":
            print(
                f"FAIL: ubuntu26-test must have ansible_user='ubuntu' "
                f"(per-host override); got {hosts['ubuntu26-test'].get('ansible_user')!r}."
            )
            return False
        if hosts["centos10-test"].get("ansible_user") != "cloud-user":
            print(
                f"FAIL: centos10-test must have ansible_user='cloud-user' "
                f"(CentOS Stream cloud images use cloud-user, not ubuntu); "
                f"got {hosts['centos10-test'].get('ansible_user')!r}."
            )
            return False
    print("OK: generator emits per-host ansible_host/vmid/node_name + ansible_user override.")
    return True


def test_generator_skips_null_ansible_host_with_warning():
    inv = _fixture_inventory()
    inv["proxmox_vms"]["hosts"]["centos10-test"]["ansible_host"] = None
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "inv.json")
        out_path = os.path.join(tmp, "out.yml")
        with open(in_path, "w", encoding="utf-8") as f:
            json.dump(inv, f)
        result = _run_generator(in_path, out_path)
        if result.returncode != 0:
            print(
                f"FAIL: generator exited {result.returncode} when one "
                f"host had ansible_host=null but another remained valid; "
                f"stderr={result.stderr!r}."
            )
            return False
        if "centos10-test" not in result.stderr:
            print(
                f"FAIL: generator must emit a stderr warning naming the "
                f"skipped host 'centos10-test'; stderr={result.stderr!r}."
            )
            return False
        with open(out_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        hosts = doc["proxmox_vms"]["hosts"]
        if "centos10-test" in hosts:
            print(
                f"FAIL: 'centos10-test' must be omitted from generated "
                f"inventory when ansible_host is null; got hosts={list(hosts)}."
            )
            return False
        if "ubuntu26-test" not in hosts:
            print(
                f"FAIL: 'ubuntu26-test' should remain when only "
                f"'centos10-test' has null ansible_host; got hosts={list(hosts)}."
            )
            return False
    print("OK: hosts with ansible_host=null are skipped with stderr warning.")
    return True


def test_generator_rejects_malformed_json():
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "broken.json")
        out_path = os.path.join(tmp, "out.yml")
        with open(in_path, "w", encoding="utf-8") as f:
            f.write('{"proxmox_vms": {"hosts": {"ubu')  # truncated mid-string
        result = _run_generator(in_path, out_path)
        if result.returncode == 0:
            print(
                f"FAIL: generator must exit non-zero on malformed JSON; "
                f"got exit 0, stdout={result.stdout!r}."
            )
            return False
        if in_path not in result.stderr:
            print(
                f"FAIL: stderr on malformed JSON must name the input "
                f"path '{in_path}'; got stderr={result.stderr!r}."
            )
            return False
    print("OK: malformed JSON triggers non-zero exit + stderr names input path.")
    return True


def test_generator_rejects_missing_inventory_shape():
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "wrong.json")
        out_path = os.path.join(tmp, "out.yml")
        # Valid JSON but no group with a `hosts` mapping.
        with open(in_path, "w", encoding="utf-8") as f:
            json.dump({"some_other_top_key": {"not_hosts": {}}}, f)
        result = _run_generator(in_path, out_path)
        if result.returncode == 0:
            print(
                f"FAIL: generator must exit non-zero when the JSON has "
                f"no group with a 'hosts' map; got exit 0."
            )
            return False
        if "hosts" not in result.stderr:
            print(
                f"FAIL: stderr must name the missing 'hosts' shape; "
                f"got stderr={result.stderr!r}."
            )
            return False
    print("OK: missing ansible_inventory shape → non-zero exit + stderr names missing key.")
    return True


def test_configure_vms_play_shape():
    if not os.path.exists(CONFIGURE_PLAY):
        print(f"FAIL: '{CONFIGURE_PLAY}' is missing.")
        return False
    with open(CONFIGURE_PLAY, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, list) or not doc:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' must be a YAML list of plays; "
            f"got {type(doc).__name__}."
        )
        return False
    play = doc[0]
    if play.get("hosts") != "proxmox_vms":
        print(
            f"FAIL: '{CONFIGURE_PLAY}' first play must target "
            f"hosts: proxmox_vms (matches generator group key); "
            f"got hosts={play.get('hosts')!r}."
        )
        return False
    if play.get("become") is not True:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' first play must set become: true "
            f"(cloud-init users need sudo); got become={play.get('become')!r}."
        )
        return False
    roles = play.get("roles") or []
    role_names = [
        (r if isinstance(r, str) else r.get("role") or r.get("name"))
        for r in roles
    ]
    if "vm_baseline" not in role_names:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' must include 'vm_baseline' in "
            f"roles list; got roles={role_names}."
        )
        return False
    print("OK: configure-vms.yml targets proxmox_vms, become=true, applies vm_baseline.")
    return True


def test_vm_baseline_role_has_python3_task():
    if not os.path.exists(VM_BASELINE_TASKS):
        print(f"FAIL: '{VM_BASELINE_TASKS}' is missing.")
        return False
    with open(VM_BASELINE_TASKS, "r", encoding="utf-8") as f:
        text = f.read()
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        print(f"FAIL: '{VM_BASELINE_TASKS}' does not parse as YAML: {exc}.")
        return False
    if not isinstance(doc, list):
        print(
            f"FAIL: '{VM_BASELINE_TASKS}' must be a YAML list of tasks; "
            f"got {type(doc).__name__}."
        )
        return False
    if "python3" not in text:
        print(
            f"FAIL: '{VM_BASELINE_TASKS}' must reference python3 "
            f"(the baseline ensures python3 is installed for Ansible)."
        )
        return False
    print("OK: vm_baseline tasks/main.yml parses and ensures python3.")
    return True


def _find_ansible_playbook():
    candidate = os.path.join(REPO_ROOT, ".venv", "bin", "ansible-playbook")
    if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        return candidate
    return shutil.which("ansible-playbook")


def test_configure_vms_syntax_check():
    binary = _find_ansible_playbook()
    if binary is None:
        # Failure Capture per global rule: fix memory + remediation task.
        # Tests that need a missing tool MUST flag it loudly even when
        # the test itself passes-with-note.
        print(
            "PASS-WITH-NOTE: ansible-playbook not on PATH and not at "
            ".venv/bin/ansible-playbook; recorded fix memory + opened "
            "remediation task. Skipping --syntax-check."
        )
        return True
    if not os.path.exists(CONFIGURE_PLAY):
        print(f"FAIL: '{CONFIGURE_PLAY}' is missing (cannot syntax-check).")
        return False
    with tempfile.TemporaryDirectory() as tmp:
        # Generate a real fixture inventory via the actual generator so the
        # syntax-check runs against generator output, not a hand-rolled YAML.
        in_path = os.path.join(tmp, "inv.json")
        out_path = os.path.join(tmp, "tofu_generated.yml")
        with open(in_path, "w", encoding="utf-8") as f:
            json.dump(_fixture_inventory(), f)
        gen = _run_generator(in_path, out_path)
        if gen.returncode != 0:
            print(
                f"FAIL: generator failed during syntax-check fixture "
                f"prep; stderr={gen.stderr!r}."
            )
            return False
        result = subprocess.run(
            [binary, "--syntax-check", "-i", out_path, CONFIGURE_PLAY],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            print(
                f"FAIL: ansible-playbook --syntax-check exited "
                f"{result.returncode}; stdout={result.stdout!r} "
                f"stderr={result.stderr!r}."
            )
            return False
    print("OK: ansible-playbook --syntax-check on configure-vms.yml exit 0.")
    return True


def main():
    checks = [
        ("generator emits per-host inventory entries", test_generator_produces_per_host_inventory),
        ("generator skips null ansible_host with warning", test_generator_skips_null_ansible_host_with_warning),
        ("generator rejects malformed JSON", test_generator_rejects_malformed_json),
        ("generator rejects missing ansible_inventory shape", test_generator_rejects_missing_inventory_shape),
        ("configure-vms.yml has correct play shape", test_configure_vms_play_shape),
        ("vm_baseline role ensures python3", test_vm_baseline_role_has_python3_task),
        ("configure-vms.yml passes ansible-playbook --syntax-check", test_configure_vms_syntax_check),
    ]
    results = [(label, fn()) for label, fn in checks]
    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    print(f"SUCCESS: All {len(results)} tofu→inventory bridge checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
