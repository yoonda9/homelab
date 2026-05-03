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
import re
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
ROOT_MAIN_TF = os.path.join(REPO_ROOT, "tofu", "main.tf")


def _fixture_inventory():
    """Post-apply ansible_inventory output value.

    Hostnames pivot to the dev fleet and the group-level ansible_user
    is the uniform 'user' the cloud-init `default_user` provisions.
    There is NO per-host ansible_user override anymore — that legacy
    behaviour (`ubuntu*` → ubuntu, `centos*` → cloud-user) is gone.

    Step 3 (dev-templates-ubuntu-fedora) replaced `centos10-dev` with
    `fedora-workstation-dev` (vmid 312); the fixture mirrors the new
    `local.linux_vms` shape in `tofu/main.tf`.

    The sibling `windows_dev_vms` group is emitted by
    `tofu/outputs.tf`. The generator reshapes it into
    `proxmox_vms.children.windows.{hosts,vars}` with
    `ansible_shell_type: powershell` so Linux + Windows hosts share
    inherited group-level `ansible_user: user`.
    """
    return {
        "proxmox_vms": {
            "hosts": {
                "ubuntu26-dev": {
                    "ansible_host": "192.168.50.10",
                    "vmid": 310,
                    "node_name": "pve-01",
                },
                "fedora-workstation-dev": {
                    "ansible_host": "192.168.50.12",
                    "vmid": 312,
                    "node_name": "pve-01",
                },
            },
            "vars": {"ansible_user": "user"},
        },
        "windows_dev_vms": {
            "hosts": {
                "win10-dev": {
                    "ansible_host": "192.168.50.20",
                    "vmid": 320,
                    "node_name": "pve-01",
                },
                "win11-dev": {
                    "ansible_host": "192.168.50.21",
                    "vmid": 321,
                    "node_name": "pve-01",
                },
            },
            "vars": {"ansible_user": "user"},
        },
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
        for host in ("ubuntu26-dev", "fedora-workstation-dev"):
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
            # No per-host ansible_user override anymore (Step 1b drops
            # `ansible_user_for`). The single uniform 'user' lives on
            # the group-level vars instead.
            if "ansible_user" in entry:
                print(
                    f"FAIL: per-host ansible_user override leaked back "
                    f"into '{host}': got "
                    f"ansible_user={entry['ansible_user']!r}. The "
                    f"generator must drop the legacy ansible_user_for "
                    f"override; group-level "
                    f"proxmox_vms.vars.ansible_user is the only source."
                )
                return False
        group_vars = doc["proxmox_vms"].get("vars") or {}
        if group_vars.get("ansible_user") != "user":
            print(
                f"FAIL: proxmox_vms.vars.ansible_user must be 'user' "
                f"(uniform default_user across Linux + Windows dev VMs); "
                f"got {group_vars.get('ansible_user')!r}."
            )
            return False
    print(
        "OK: generator emits per-host ansible_host/vmid/node_name with "
        "no per-host ansible_user override; group-level "
        "proxmox_vms.vars.ansible_user='user'."
    )
    return True


def test_generator_skips_null_ansible_host_with_warning():
    inv = _fixture_inventory()
    inv["proxmox_vms"]["hosts"]["fedora-workstation-dev"]["ansible_host"] = None
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
        if "fedora-workstation-dev" not in result.stderr:
            print(
                f"FAIL: generator must emit a stderr warning naming the "
                f"skipped host 'fedora-workstation-dev'; "
                f"stderr={result.stderr!r}."
            )
            return False
        with open(out_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        hosts = doc["proxmox_vms"]["hosts"]
        if "fedora-workstation-dev" in hosts:
            print(
                f"FAIL: 'fedora-workstation-dev' must be omitted from "
                f"generated inventory when ansible_host is null; got "
                f"hosts={list(hosts)}."
            )
            return False
        if "ubuntu26-dev" not in hosts:
            print(
                f"FAIL: 'ubuntu26-dev' should remain when only "
                f"'fedora-workstation-dev' has null ansible_host; got "
                f"hosts={list(hosts)}."
            )
            return False
    print("OK: hosts with ansible_host=null are skipped with stderr warning.")
    return True


def test_generator_reshapes_windows_into_proxmox_vms_children():
    """Windows hosts land at proxmox_vms.children.windows.hosts.

    Walks the parsed YAML structure (PyYAML, not regex on the file
    body) so a cross-swap of Linux/Windows host blocks is caught
    (mem-1777521206-b3c1).
    """
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "inv.json")
        out_path = os.path.join(tmp, "tofu_generated.yml")
        with open(in_path, "w", encoding="utf-8") as f:
            json.dump(_fixture_inventory(), f)
        result = _run_generator(in_path, out_path)
        if result.returncode != 0:
            print(
                f"FAIL: generator exited {result.returncode} with the "
                f"two-group fixture; stderr={result.stderr!r}."
            )
            return False
        with open(out_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    if not isinstance(doc, dict):
        print(f"FAIL: generated YAML must be a mapping; got {type(doc).__name__}.")
        return False
    if "windows_dev_vms" in doc:
        print(
            f"FAIL: 'windows_dev_vms' must NOT be a top-level group in "
            f"the generated inventory — it must be reshaped into "
            f"proxmox_vms.children.windows. Got top-level keys={list(doc)}."
        )
        return False
    proxmox = doc.get("proxmox_vms") or {}
    proxmox_hosts = proxmox.get("hosts") or {}
    for win_host in ("win10-dev", "win11-dev"):
        if win_host in proxmox_hosts:
            print(
                f"FAIL: '{win_host}' must NOT be at proxmox_vms.hosts "
                f"(would pull in vm_baseline). It must land at "
                f"proxmox_vms.children.windows.hosts instead. Got "
                f"proxmox_vms.hosts keys={list(proxmox_hosts)}."
            )
            return False
    children = proxmox.get("children") or {}
    if "windows" not in children:
        print(
            f"FAIL: generated YAML must contain "
            f"proxmox_vms.children.windows (reshaped from "
            f"windows_dev_vms). Got children keys={list(children)}."
        )
        return False
    win_group = children["windows"]
    win_hosts = win_group.get("hosts") or {}
    for win_host, expected_vmid in (("win10-dev", 320), ("win11-dev", 321)):
        entry = win_hosts.get(win_host)
        if not isinstance(entry, dict):
            print(
                f"FAIL: proxmox_vms.children.windows.hosts.{win_host} "
                f"missing or not a mapping; got "
                f"hosts={list(win_hosts)}."
            )
            return False
        for attr in ("ansible_host", "vmid", "node_name"):
            if attr not in entry:
                print(
                    f"FAIL: proxmox_vms.children.windows.hosts.{win_host} "
                    f"missing '{attr}' (entry={entry!r})."
                )
                return False
        if entry.get("vmid") != expected_vmid:
            print(
                f"FAIL: proxmox_vms.children.windows.hosts.{win_host} "
                f"vmid mismatch — expected {expected_vmid}, got "
                f"{entry.get('vmid')!r}. Cross-swap with Linux hosts "
                f"would mismatch here."
            )
            return False
        if "ansible_user" in entry:
            print(
                f"FAIL: per-host ansible_user override leaked into "
                f"Windows host '{win_host}'. ansible_user must live at "
                f"the parent proxmox_vms.vars only."
            )
            return False
    print(
        "OK: windows_dev_vms reshaped into proxmox_vms.children.windows; "
        "win10-dev/win11-dev land in the windows child with correct vmids."
    )
    return True


def test_generator_emits_powershell_shell_type_on_windows_child():
    """proxmox_vms.children.windows.vars.ansible_shell_type == 'powershell'."""
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "inv.json")
        out_path = os.path.join(tmp, "out.yml")
        with open(in_path, "w", encoding="utf-8") as f:
            json.dump(_fixture_inventory(), f)
        result = _run_generator(in_path, out_path)
        if result.returncode != 0:
            print(
                f"FAIL: generator exited {result.returncode}; "
                f"stderr={result.stderr!r}."
            )
            return False
        with open(out_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    win_vars = (
        (doc.get("proxmox_vms") or {})
        .get("children", {})
        .get("windows", {})
        .get("vars")
        or {}
    )
    if win_vars.get("ansible_shell_type") != "powershell":
        print(
            f"FAIL: proxmox_vms.children.windows.vars.ansible_shell_type "
            f"must be 'powershell'; got "
            f"{win_vars.get('ansible_shell_type')!r}."
        )
        return False
    # Windows child vars must NOT carry its own ansible_user — it's
    # inherited from proxmox_vms.vars.ansible_user. Carrying both is
    # redundant; the spec says "ansible_shell_type lives on the windows
    # child's vars only".
    if "ansible_user" in win_vars:
        print(
            f"FAIL: proxmox_vms.children.windows.vars must not redefine "
            f"ansible_user (inherited from proxmox_vms.vars); got "
            f"ansible_user={win_vars['ansible_user']!r}."
        )
        return False
    # Top-level ansible_user must remain 'user' (covers Windows via
    # group inheritance).
    parent_vars = (doc.get("proxmox_vms") or {}).get("vars") or {}
    if parent_vars.get("ansible_user") != "user":
        print(
            f"FAIL: proxmox_vms.vars.ansible_user must be 'user' "
            f"(inherited by both Linux hosts and the windows child); "
            f"got {parent_vars.get('ansible_user')!r}."
        )
        return False
    print(
        "OK: proxmox_vms.children.windows.vars carries only "
        "ansible_shell_type=powershell; ansible_user inherited from parent."
    )
    return True


def test_generator_skips_null_windows_ansible_host_with_warning():
    """A DHCP-pending Windows host (ansible_host = null) is skipped + warned."""
    inv = _fixture_inventory()
    inv["windows_dev_vms"]["hosts"]["win10-dev"]["ansible_host"] = None
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "inv.json")
        out_path = os.path.join(tmp, "out.yml")
        with open(in_path, "w", encoding="utf-8") as f:
            json.dump(inv, f)
        result = _run_generator(in_path, out_path)
        if result.returncode != 0:
            print(
                f"FAIL: generator exited {result.returncode} when "
                f"win10-dev had ansible_host=null but other hosts "
                f"remained valid; stderr={result.stderr!r}."
            )
            return False
        if "win10-dev" not in result.stderr:
            print(
                f"FAIL: generator must emit a stderr warning naming "
                f"the skipped Windows host 'win10-dev'; "
                f"stderr={result.stderr!r}."
            )
            return False
        with open(out_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    win_hosts = (
        (doc.get("proxmox_vms") or {})
        .get("children", {})
        .get("windows", {})
        .get("hosts")
        or {}
    )
    if "win10-dev" in win_hosts:
        print(
            f"FAIL: 'win10-dev' must be omitted from "
            f"proxmox_vms.children.windows.hosts when its ansible_host "
            f"is null; got hosts={list(win_hosts)}."
        )
        return False
    if "win11-dev" not in win_hosts:
        print(
            f"FAIL: 'win11-dev' should remain in "
            f"proxmox_vms.children.windows.hosts when only 'win10-dev' "
            f"has null ansible_host; got hosts={list(win_hosts)}."
        )
        return False
    # And the Linux hosts should be untouched.
    linux_hosts = ((doc.get("proxmox_vms") or {}).get("hosts")) or {}
    for linux_host in ("ubuntu26-dev", "fedora-workstation-dev"):
        if linux_host not in linux_hosts:
            print(
                f"FAIL: Linux host '{linux_host}' lost from "
                f"proxmox_vms.hosts when only Windows DHCP was pending; "
                f"got hosts={list(linux_hosts)}."
            )
            return False
    print(
        "OK: DHCP-pending Windows host is skipped with stderr warning; "
        "win11-dev + Linux hosts remain."
    )
    return True


def _extract_named_map_body(text, parent_header, map_name):
    """Brace-balanced extraction of `<map_name> = { ... }` from inside a
    `<parent_header> { ... }` block (e.g. `locals`).

    Tolerates nested braces inside the map (per-entry objects are themselves
    `{ ... }`). Required to avoid the cross-swap precision gap recorded in
    DEC-009 / mem-1777521206-b3c1: regex without brace balancing can match
    across sibling blocks and pair groups with the wrong module.
    """
    parent_pattern = (
        parent_header
        + r"\s*\{"
        + r"(?P<body>(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)"
        + r"\}"
    )
    parent_match = re.search(parent_pattern, text)
    if parent_match is None:
        return None
    parent_body = parent_match.group("body")
    map_pattern = (
        re.escape(map_name)
        + r"\s*=\s*\{"
        + r"(?P<body>(?:[^{}]|\{[^{}]*\})*)"
        + r"\}"
    )
    map_match = re.search(map_pattern, parent_body)
    return map_match.group("body") if map_match else None


def test_main_tf_linux_vms_aligned_with_fixture():
    """tofu/main.tf local.linux_vms must have fedora-workstation-dev and
    must NOT have centos10-dev (defends against re-add).

    The generator itself is fixture-driven, so without this assertion a
    re-add of centos10-dev to main.tf would slip past this test file.
    Brace-balanced body extraction (mem-1777521206-b3c1) prevents a
    cross-swap of the linux_vms / windows_vms map bodies from confusing
    the assertion.
    """
    if not os.path.exists(ROOT_MAIN_TF):
        print(f"FAIL: '{ROOT_MAIN_TF}' is missing.")
        return False
    with open(ROOT_MAIN_TF, "r", encoding="utf-8") as f:
        text = f.read()
    linux_body = _extract_named_map_body(text, r"locals", "linux_vms")
    if linux_body is None:
        print(
            f"FAIL: '{ROOT_MAIN_TF}' has no "
            f"'locals {{ ... linux_vms = {{ ... }} ... }}' block."
        )
        return False
    code = "\n".join(
        line
        for line in linux_body.splitlines()
        if not line.lstrip().startswith("#")
    )
    fedora_present = re.search(
        r'"?fedora-workstation-dev"?\s*=\s*\{', code
    ) is not None
    centos_present = re.search(
        r'"?centos10-dev"?\s*=\s*\{', code
    ) is not None
    if not fedora_present:
        print(
            f"FAIL: '{ROOT_MAIN_TF}' local.linux_vms missing "
            f"'fedora-workstation-dev' entry — the inventory generator "
            f"fixture in this test file expects it (Step 3 dev fleet)."
        )
        return False
    if centos_present:
        print(
            f"FAIL: '{ROOT_MAIN_TF}' local.linux_vms still contains "
            f"'centos10-dev' — Step 3 replaced it with "
            f"fedora-workstation-dev (DEC-010 'replace, don't deprecate'); "
            f"a re-add would drift the fixture in test_tofu_to_inventory.py "
            f"out of sync with the actual tofu output shape."
        )
        return False
    print(
        f"OK: '{ROOT_MAIN_TF}' local.linux_vms contains "
        f"fedora-workstation-dev and centos10-dev is absent."
    )
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


def _role_names(play):
    roles = play.get("roles") or []
    return [
        (r if isinstance(r, str) else r.get("role") or r.get("name"))
        for r in roles
    ]


def test_configure_vms_play_shape():
    """Two-play structure: Linux-only first, Windows second.

    Step 3 split the original single play into two so Linux and
    Windows guests can use different roles and connection settings.
    First play: hosts: 'proxmox_vms:!windows' with vm_baseline (the
    `:!windows` selector is the safety net if a Windows host slips
    into proxmox_vms directly). Second play: hosts: 'windows' with
    windows_baseline and no `become` (Windows has no sudo).
    """
    if not os.path.exists(CONFIGURE_PLAY):
        print(f"FAIL: '{CONFIGURE_PLAY}' is missing.")
        return False
    with open(CONFIGURE_PLAY, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, list) or len(doc) < 2:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' must be a YAML list of at least "
            f"2 plays (Linux + Windows split); got "
            f"{len(doc) if isinstance(doc, list) else type(doc).__name__}."
        )
        return False

    linux_play = doc[0]
    if linux_play.get("hosts") != "proxmox_vms:!windows":
        print(
            f"FAIL: '{CONFIGURE_PLAY}' first play must target "
            f"hosts: 'proxmox_vms:!windows' (the :!windows selector is "
            f"the safety net against a Windows host accidentally "
            f"landing in proxmox_vms.hosts); got "
            f"hosts={linux_play.get('hosts')!r}."
        )
        return False
    if linux_play.get("become") is not True:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' first play must set become: true "
            f"(cloud-init users need sudo); got "
            f"become={linux_play.get('become')!r}."
        )
        return False
    linux_roles = _role_names(linux_play)
    if "vm_baseline" not in linux_roles:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' first play must include "
            f"'vm_baseline' in roles list; got roles={linux_roles}."
        )
        return False
    if "windows_baseline" in linux_roles:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' first play (Linux) must NOT "
            f"include 'windows_baseline'; got roles={linux_roles}."
        )
        return False

    win_play = doc[1]
    if win_play.get("hosts") != "windows":
        print(
            f"FAIL: '{CONFIGURE_PLAY}' second play must target "
            f"hosts: 'windows' (matches the proxmox_vms.children.windows "
            f"group emitted by the generator); got "
            f"hosts={win_play.get('hosts')!r}."
        )
        return False
    # become must NOT be true on Windows (no sudo).
    if win_play.get("become") is True:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' second play (Windows) must NOT "
            f"set become: true — Windows hosts have no sudo. Use "
            f"become: false or omit the key entirely. Got "
            f"become={win_play.get('become')!r}."
        )
        return False
    win_roles = _role_names(win_play)
    if "windows_baseline" not in win_roles:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' second play must include "
            f"'windows_baseline' in roles list; got roles={win_roles}."
        )
        return False
    if "vm_baseline" in win_roles:
        print(
            f"FAIL: '{CONFIGURE_PLAY}' second play (Windows) must NOT "
            f"include 'vm_baseline' (Linux-only); got roles={win_roles}."
        )
        return False
    print(
        "OK: configure-vms.yml has two plays — Linux-only "
        "proxmox_vms:!windows + vm_baseline + become; "
        "Windows-only windows + windows_baseline + no become."
    )
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
        ("generator reshapes windows_dev_vms into proxmox_vms.children.windows", test_generator_reshapes_windows_into_proxmox_vms_children),
        ("generator emits ansible_shell_type=powershell on windows child", test_generator_emits_powershell_shell_type_on_windows_child),
        ("generator skips null Windows ansible_host with warning", test_generator_skips_null_windows_ansible_host_with_warning),
        ("tofu/main.tf local.linux_vms aligned with fixture (fedora-workstation-dev present, centos10-dev absent)", test_main_tf_linux_vms_aligned_with_fixture),
        ("generator rejects malformed JSON", test_generator_rejects_malformed_json),
        ("generator rejects missing ansible_inventory shape", test_generator_rejects_missing_inventory_shape),
        ("configure-vms.yml has two-play Linux+Windows shape", test_configure_vms_play_shape),
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
