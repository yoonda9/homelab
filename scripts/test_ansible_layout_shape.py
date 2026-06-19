"""Shape tests for the ansible/ configuration layer (Step 4).

Per design §3 (repo layout), §4.3 (Ansible roles) and §Data Models
("Ansible inventory / group_vars") plus task-04 — verifies the ansible/
tree is wired together beside tofu/:

- ansible.cfg, site.yml, inventory/hosts.yml, group_vars/all.yml,
  group_vars/vault.yml and roles/common/tasks/main.yml all exist;
- site.yml applies the `common` role;
- group_vars/all.yml carries the required keys (domain, acme_resolver,
  public_services, internal_services);
- group_vars/vault.yml is Ansible-Vault-encrypted ($ANSIBLE_VAULT header);
- ansible.cfg points its inventory at inventory/hosts.yml.

Dual-mode (module-level test_*()->bool + main()->int), stdlib only,
mirroring scripts/test_lxc_service_module_shape.py (mem-1781891042-4495).
Per mem-1781892715-142d the regexes anchor on the inner content
(the actual key/value), not just a section opener, so an empty stub
could not satisfy the check. The real gate is the standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ANSIBLE = REPO_ROOT / "ansible"
PLEX_TASKS = ANSIBLE / "roles" / "plex" / "tasks" / "main.yml"
GEN_INVENTORY = REPO_ROOT / "scripts" / "gen_inventory.py"


def test_ansible_directory_exists() -> bool:
    ok = ANSIBLE.is_dir()
    print(f"{'OK' if ok else 'FAIL'}: ansible/ dir exists at {ANSIBLE}")
    return ok


def test_required_files_exist() -> bool:
    required = [
        "ansible.cfg",
        "site.yml",
        "inventory/hosts.yml",
        "group_vars/all.yml",
        "group_vars/vault.yml",
        "roles/common/tasks/main.yml",
    ]
    missing = [f for f in required if not (ANSIBLE / f).is_file()]
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: required ansible files present (missing={missing})")
    return ok


def test_cfg_points_at_inventory() -> bool:
    cfg = ANSIBLE / "ansible.cfg"
    if not cfg.is_file():
        print("FAIL: ansible.cfg points inventory at inventory/hosts.yml (ansible.cfg missing)")
        return False
    body = cfg.read_text()
    ok = re.search(r'(?m)^\s*inventory\s*=\s*\S*inventory/hosts\.yml', body) is not None
    print(f"{'OK' if ok else 'FAIL'}: ansible.cfg points inventory at inventory/hosts.yml")
    return ok


def test_site_applies_common_role() -> bool:
    site = ANSIBLE / "site.yml"
    if not site.is_file():
        print("FAIL: site.yml applies the common role (site.yml missing)")
        return False
    body = site.read_text()
    # Anchor on a roles: list that names common, not merely the word "common".
    has_roles = re.search(r'(?s)roles\s*:.*?\bcommon\b', body) is not None
    print(f"{'OK' if has_roles else 'FAIL'}: site.yml applies the common role")
    return has_roles


def test_group_vars_required_keys() -> bool:
    all_yml = ANSIBLE / "group_vars" / "all.yml"
    if not all_yml.is_file():
        print("FAIL: group_vars/all.yml carries required keys (all.yml missing)")
        return False
    body = all_yml.read_text()
    checks = {
        "domain": re.search(r'(?m)^\s*domain\s*:\s*\S+', body),
        "acme_resolver": re.search(r'(?m)^\s*acme_resolver\s*:\s*\S+', body),
        "public_services": re.search(r'(?m)^\s*public_services\s*:', body),
        "internal_services": re.search(r'(?m)^\s*internal_services\s*:', body),
    }
    missing = [k for k, v in checks.items() if v is None]
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: group_vars/all.yml carries required keys (missing={missing})")
    return ok


def test_public_services_is_plex() -> bool:
    all_yml = ANSIBLE / "group_vars" / "all.yml"
    if not all_yml.is_file():
        print("FAIL: public_services == [plex] (all.yml missing)")
        return False
    body = all_yml.read_text()
    # plex must be the public service; tolerate inline (- plex / [plex]) styles.
    has_plex = re.search(r'(?s)public_services\s*:\s*(\[[^\]]*\bplex\b[^\]]*\]|(?:\s*#.*)?\n(?:\s*-\s*\w+\s*\n)*\s*-\s*plex\b)', body)
    ok = has_plex is not None
    print(f"{'OK' if ok else 'FAIL'}: public_services lists plex")
    return ok


def test_vault_is_encrypted() -> bool:
    vault = ANSIBLE / "group_vars" / "vault.yml"
    if not vault.is_file():
        print("FAIL: group_vars/vault.yml is Ansible-Vault-encrypted (vault.yml missing)")
        return False
    first_line = vault.read_text().splitlines()[0] if vault.read_text() else ""
    ok = first_line.startswith("$ANSIBLE_VAULT")
    print(f"{'OK' if ok else 'FAIL'}: group_vars/vault.yml is Ansible-Vault-encrypted ($ANSIBLE_VAULT header)")
    return ok


def test_common_role_idempotent() -> bool:
    """The common role must not lean on unguarded command/shell tasks.

    Any command/shell/raw use must be guarded by changed_when/creates/when
    so a second run reports no changes (idempotency, AC4).
    """
    tasks = ANSIBLE / "roles" / "common" / "tasks" / "main.yml"
    if not tasks.is_file():
        print("FAIL: common role tasks have no unguarded command/shell (main.yml missing)")
        return False
    body = tasks.read_text()
    unguarded = []
    # Find each command/shell/raw MODULE task and require a guard nearby. Anchor
    # on the FQCN module form (this repo mandates fqcn via ansible-lint) so a
    # module *parameter* named e.g. `shell: /usr/sbin/nologin` cannot match.
    for m in re.finditer(r'(?m)^\s*ansible\.builtin\.(command|shell|raw)\s*:', body):
        start = m.start()
        window = body[start:start + 600]
        if not re.search(r'changed_when|creates|removes|when\s*:', window):
            unguarded.append(m.group(1))
    ok = not unguarded
    print(f"{'OK' if ok else 'FAIL'}: common role has no unguarded command/shell/raw (found={unguarded})")
    return ok


def test_plex_role_tasks_exist() -> bool:
    ok = PLEX_TASKS.is_file()
    print(f"{'OK' if ok else 'FAIL'}: roles/plex/tasks/main.yml exists at {PLEX_TASKS}")
    return ok


def test_plex_installs_ihd_driver() -> bool:
    """The plex role must install the iHD (QSV) media driver, not i965 (design §6/§A)."""
    if not PLEX_TASKS.is_file():
        print("FAIL: plex role installs intel-media-va-driver-non-free (tasks/main.yml missing)")
        return False
    body = PLEX_TASKS.read_text()
    ok = "intel-media-va-driver-non-free" in body
    print(f"{'OK' if ok else 'FAIL'}: plex role installs the iHD driver (intel-media-va-driver-non-free)")
    return ok


def test_plex_vainfo_ihd_gate() -> bool:
    """The role must run vainfo AND assert the iHD driver — the QSV acceptance gate.

    Anchor on `iHD` appearing inside an assert/failed_when context (not merely the
    word) so a bare mention can't satisfy the check (mem-1781892715-142d).
    """
    if not PLEX_TASKS.is_file():
        print("FAIL: plex role has the vainfo->iHD acceptance gate (tasks/main.yml missing)")
        return False
    body = PLEX_TASKS.read_text()
    runs_vainfo = "vainfo" in body
    asserts_ihd = re.search(
        r'(?s)(ansible\.builtin\.assert|assert\s*:|failed_when)[\s\S]{0,400}?iHD', body
    ) is not None
    ok = runs_vainfo and asserts_ihd
    print(f"{'OK' if ok else 'FAIL'}: plex role runs vainfo and asserts the iHD driver (gate)")
    return ok


def test_site_applies_plex_play() -> bool:
    site = ANSIBLE / "site.yml"
    if not site.is_file():
        print("FAIL: site.yml has a plex play (site.yml missing)")
        return False
    body = site.read_text()
    # A play targeting hosts: plex whose roles list names plex.
    ok = re.search(r'(?s)hosts\s*:\s*plex\b.*?roles\s*:.*?\bplex\b', body) is not None
    print(f"{'OK' if ok else 'FAIL'}: site.yml has a plex play (hosts: plex, roles: [plex])")
    return ok


def test_gen_inventory_renders_plex_group() -> bool:
    """gen_inventory.py must read the Step-7 plex_* outputs and emit a plex group node."""
    if not GEN_INVENTORY.is_file():
        print("FAIL: gen_inventory.py renders a plex group (gen_inventory.py missing)")
        return False
    body = GEN_INVENTORY.read_text()
    reads_outputs = "plex_ipv4" in body and "plex_name" in body
    emits_group = "plex:" in body
    ok = reads_outputs and emits_group
    print(f"{'OK' if ok else 'FAIL'}: gen_inventory.py renders a plex group from plex_* outputs")
    return ok


def main() -> int:
    results = [
        test_ansible_directory_exists(),
        test_required_files_exist(),
        test_cfg_points_at_inventory(),
        test_site_applies_common_role(),
        test_group_vars_required_keys(),
        test_public_services_is_plex(),
        test_vault_is_encrypted(),
        test_common_role_idempotent(),
        test_plex_role_tasks_exist(),
        test_plex_installs_ihd_driver(),
        test_plex_vainfo_ihd_gate(),
        test_site_applies_plex_play(),
        test_gen_inventory_renders_plex_group(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
