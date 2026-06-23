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
DOCKER_HOST_TASKS = ANSIBLE / "roles" / "docker_host" / "tasks" / "main.yml"
DOCKER_HOST_META = ANSIBLE / "roles" / "docker_host" / "meta" / "main.yml"
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


def test_plex_install_refreshes_after_repo() -> bool:
    """The 'Install Plex Media Server' apt task must refresh the cache after the repo.

    Root cause of the "No package matching 'plexmediaserver'" failure: the prior
    iHD-driver apt task freshly stamps the apt cache, so a cache_valid_time on the
    plexmediaserver install makes the apt module SKIP the refresh (it only updates
    when the cache is OLDER than the window) and the Plex deb822 repo added just
    above is never indexed. The fix: keep update_cache:true and DROP
    cache_valid_time on that task (same footgun as the docker-ce bug).

    Anchors on the install task BLOCK (from its `- name:` to the next task) and
    asserts it has update_cache:true and NO cache_valid_time, so a leftover
    cache_valid_time anywhere else in the file cannot mask a regression here.
    """
    if not PLEX_TASKS.is_file():
        print("FAIL: plex install task refreshes cache after repo (tasks/main.yml missing)")
        return False
    body = PLEX_TASKS.read_text()
    # Slice the 'Install Plex Media Server' task block: from its name line to the
    # next top-level task (- name:) or EOF.
    m = re.search(
        r'(?ms)^-\s+name:\s*Install Plex Media Server\b.*?(?=^-\s+name:|\Z)', body
    )
    if not m:
        print("FAIL: plex install task refreshes cache after repo ('Install Plex Media Server' task not found)")
        return False
    task = m.group(0)
    refreshes = re.search(r'(?m)^\s*update_cache\s*:\s*(?:true|yes)\b', task) is not None
    no_cvt = re.search(r'(?m)^\s*cache_valid_time\s*:', task) is None
    ok = refreshes and no_cvt
    print(
        f"{'OK' if ok else 'FAIL'}: plex install task refreshes cache after repo "
        f"(update_cache={refreshes} no_cache_valid_time={no_cvt})"
    )
    return ok


def test_plex_ihd_install_refreshes_after_repo() -> bool:
    """The iHD-driver apt task must refresh the cache after the non-free repo.

    Root cause of the "No package matching 'intel-media-va-driver-non-free'"
    failure: the prior python3-debian apt task freshly stamps the apt cache
    BEFORE the Debian non-free deb822 source is added, so a cache_valid_time on
    the 'Install the Intel iHD media driver and VA-API tooling' task makes the
    apt module SKIP the refresh (it only updates when the cache is OLDER than the
    window) and the non-free repo — where intel-media-va-driver-non-free lives —
    is never indexed. The fix: keep update_cache:true and DROP cache_valid_time
    on that task (same footgun as the plexmediaserver and docker-ce bugs).

    Anchors on the iHD-driver task BLOCK (from its `- name:` to the next task)
    and asserts it has update_cache:true and NO cache_valid_time, so a leftover
    cache_valid_time anywhere else in the file cannot mask a regression here.
    """
    if not PLEX_TASKS.is_file():
        print("FAIL: plex iHD-driver task refreshes cache after repo (tasks/main.yml missing)")
        return False
    body = PLEX_TASKS.read_text()
    # Slice the 'Install the Intel iHD media driver ...' task block: from its name
    # line to the next top-level task (- name:) or EOF.
    m = re.search(
        r'(?ms)^-\s+name:\s*Install the Intel iHD media driver\b.*?(?=^-\s+name:|\Z)', body
    )
    if not m:
        print("FAIL: plex iHD-driver task refreshes cache after repo ('Install the Intel iHD media driver' task not found)")
        return False
    task = m.group(0)
    refreshes = re.search(r'(?m)^\s*update_cache\s*:\s*(?:true|yes)\b', task) is not None
    no_cvt = re.search(r'(?m)^\s*cache_valid_time\s*:', task) is None
    ok = refreshes and no_cvt
    print(
        f"{'OK' if ok else 'FAIL'}: plex iHD-driver task refreshes cache after repo "
        f"(update_cache={refreshes} no_cache_valid_time={no_cvt})"
    )
    return ok


def test_plex_repo_trusted_scoped_to_plex() -> bool:
    """The Plex deb822 source must carry trusted:true; Debian non-free must not.

    Root cause of the "Plex InRelease is not signed" failure: Plex's signing key
    self-signs its uid (0x13) + subkey-binding (0x18) with SHA1, which Debian
    trixie's sqv crypto policy rejects since 2026-02-01, so the Plex InRelease
    counts as unsigned and apt refuses the repo. The fix scopes an unconditional
    trust (trusted:true) to ONLY the Plex deb822_repository task; the Debian
    non-free source keeps full signature verification.

    Slices each deb822 task by its `- name:` block so a trusted:true on the wrong
    source (or a global relax) cannot satisfy this check.
    """
    if not PLEX_TASKS.is_file():
        print("FAIL: plex repo trusted scoped to plex (tasks/main.yml missing)")
        return False
    body = PLEX_TASKS.read_text()

    def _block(name: str) -> str:
        m = re.search(
            r'(?ms)^-\s+name:\s*' + re.escape(name) + r'\b.*?(?=^-\s+name:|\Z)',
            body,
        )
        return m.group(0) if m else ""

    plex_repo = _block("Add the Plex apt repository")
    debian_repo = _block("Enable the Debian non-free components")
    trusted_re = re.compile(r'(?m)^\s*trusted\s*:\s*(?:true|yes)\b')

    plex_trusted = bool(plex_repo) and trusted_re.search(plex_repo) is not None
    debian_not_trusted = bool(debian_repo) and trusted_re.search(debian_repo) is None
    ok = plex_trusted and debian_not_trusted
    print(
        f"{'OK' if ok else 'FAIL'}: plex repo trusted scoped to plex "
        f"(plex_trusted={plex_trusted} debian_non_free_verified={debian_not_trusted})"
    )
    return ok


def test_plex_source_trusted_before_baseline_apt() -> bool:
    """The baseline play must trust a pre-existing Plex apt source in pre_tasks,
    BEFORE the common role's apt update_cache re-verifies it.

    Root cause (mem-1782146780-fa20): site.yml PLAY 1 (hosts: all) runs the common
    role's `apt update_cache` on the plex host first; it re-verifies a pre-existing
    *untrusted* Plex source (SHA1 PlexSign.key, sqv-rejected) and fails before the
    plex play (PLAY 3, hosts: plex) can rewrite the source with trusted:true. The
    plex-role fix is structurally too late. The fix marks the Plex source Trusted
    in pre_tasks of the baseline play — pre_tasks always run before roles, so the
    baseline apt update no longer chokes on the stale source. Scoped to the one
    Plex source (plexmediaserver.sources); Debian sources keep full sqv.

    Slices the FIRST play (hosts: all) so a pre_tasks block in a later play cannot
    satisfy this check, and requires the Plex source path + a Trusted marker inside
    that play's pre_tasks.
    """
    site = ANSIBLE / "site.yml"
    if not site.is_file():
        print("FAIL: plex source trusted before baseline apt (site.yml missing)")
        return False
    body = site.read_text()

    # The first play runs to just before the second top-level `- name:` play.
    plays = re.split(r'(?m)^-\s+name:', body)
    # plays[0] is the YAML preamble; plays[1] is the first play body.
    first_play = plays[1] if len(plays) > 1 else ""
    is_baseline = "hosts: all" in first_play and re.search(
        r'(?m)^\s*pre_tasks\s*:', first_play
    ) is not None

    pre_tasks = ""
    m = re.search(r'(?ms)^\s*pre_tasks\s*:.*?(?=^\s*roles\s*:|\Z)', first_play)
    if m:
        pre_tasks = m.group(0)
    references_plex_source = "plexmediaserver.sources" in pre_tasks
    trusts_it = re.search(r'(?mi)Trusted\s*:\s*yes', pre_tasks) is not None

    ok = is_baseline and references_plex_source and trusts_it
    print(
        f"{'OK' if ok else 'FAIL'}: plex source trusted before baseline apt "
        f"(baseline_pre_tasks={is_baseline} references_source={references_plex_source} "
        f"trusts_it={trusts_it})"
    )
    return ok


def test_plex_render_video_groups_non_unique() -> bool:
    """The render/video group tasks must set non_unique:true so a re-run converges.

    Root cause (mem-1782150377-4384): the render-group task hard-pins gid=993 with no
    collision handling. On a second `just play`, the earlier package installs in this
    role may already have created `render` at a non-993 system GID while GID 993 is held
    by another auto-allocated group ("play already ran once" — host GIDs allocate
    descending from 999). ansible then runs `groupmod -g 993 render`, which aborts with
    "groupmod: GID '993' already exists" (changed=false) and never converges. The fix
    adds non_unique:true so the group is forced onto the host GID even when shared; the
    repro confirmed the same task with non_unique:true succeeds under the collision. The
    symmetric video task (gid=44) needs the same treatment.

    Slices each group task by its `- name:` block so a non_unique on the wrong task (or
    elsewhere in the file) cannot satisfy this check.
    """
    if not PLEX_TASKS.is_file():
        print("FAIL: plex render/video groups non_unique (tasks/main.yml missing)")
        return False
    body = PLEX_TASKS.read_text()

    def _block(name: str) -> str:
        m = re.search(
            r'(?ms)^-\s+name:\s*' + re.escape(name) + r'\b.*?(?=^-\s+name:|\Z)',
            body,
        )
        return m.group(0) if m else ""

    render_task = _block("Ensure the render group maps to the host render GID")
    video_task = _block("Ensure the video group maps to the host video GID")
    non_unique_re = re.compile(r'(?m)^\s*non_unique\s*:\s*(?:true|yes)\b')

    render_non_unique = bool(render_task) and non_unique_re.search(render_task) is not None
    video_non_unique = bool(video_task) and non_unique_re.search(video_task) is not None
    ok = render_non_unique and video_non_unique
    print(
        f"{'OK' if ok else 'FAIL'}: plex render/video groups non_unique "
        f"(render_non_unique={render_non_unique} video_non_unique={video_non_unique})"
    )
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


def test_docker_install_delegated_to_geerlingguy_role() -> bool:
    """docker_host delegates Docker install to the upstream geerlingguy.docker role.

    Step 2 (wire-role) replaced the former custom install -- keyring dir,
    python3-debian, Docker GPG, a deb822 Docker repo, an apt install of
    `docker_host_packages`, and the systemd enable -- with the vendored
    geerlingguy.docker role (pinned in requirements.yml, resolved offline via
    roles_path). This asserts the NEW reality:

    1. geerlingguy.docker is wired -- as a meta dependency (meta/main.yml) OR an
       include_role in tasks/main.yml -- WITH the compose-plugin var mapping
       (docker_install_compose_plugin: true) so `docker compose` is present for
       the Traefik stack rendered by this role's own tasks.
    2. the custom install primitives are ABSENT from tasks/main.yml: no
       'Install Docker CE' task, no deb822 Docker repo, no `docker_host_packages`
       reference, no python3-debian prereq.

    Anchors on the actual wiring + var lines (a role/name key, not a comment) and
    on the absence of the old primitives, so neither a stub nor a leftover comment
    can satisfy it (mem-1781892715-142d).
    """
    for path in (DOCKER_HOST_TASKS, DOCKER_HOST_META):
        if not path.is_file():
            print(f"FAIL: docker install delegated to geerlingguy.docker ({path.name} missing)")
            return False
    tasks = DOCKER_HOST_TASKS.read_text()
    # The role may be wired via a meta dependency or an include_role in tasks; scan both.
    wiring = DOCKER_HOST_META.read_text() + "\n" + tasks

    # 1a. geerlingguy.docker referenced on a role/name key (meta dep short form
    #     "- role: geerlingguy.docker" or include_role's "name: geerlingguy.docker"),
    #     not merely named in a comment.
    role_wired = re.search(
        r'(?m)^\s*(?:-\s+role|name)\s*:\s*["\']?geerlingguy\.docker(?:["\']|\s|$)', wiring
    ) is not None
    # 1b. the compose-plugin var mapping travels with the wiring.
    compose_plugin = re.search(
        r'(?m)^\s*docker_install_compose_plugin\s*:\s*(?:true|yes)\b', wiring
    ) is not None

    # 2. the custom install primitives are gone from tasks/main.yml.
    no_install_task = re.search(r'(?mi)^-\s+name:\s*Install Docker CE', tasks) is None
    no_docker_repo = "deb822_repository" not in tasks
    no_packages_var = "docker_host_packages" not in tasks
    no_python3_debian = "python3-debian" not in tasks
    custom_gone = no_install_task and no_docker_repo and no_packages_var and no_python3_debian

    # 3. the galaxy_info description no longer claims THIS role installs Docker CE
    #    (Step 3 doc alignment): the install is delegated to geerlingguy.docker, so
    #    a description advertising the role's own "Install Docker CE" is misleading.
    #    Anchored on the `description:` value line so the migration comment block
    #    (which names the FORMER custom install) cannot satisfy or redden it.
    desc_match = re.search(r'(?m)^\s*description:\s*(.+)$', DOCKER_HOST_META.read_text())
    desc = desc_match.group(1) if desc_match else ""
    description_aligned = "Install Docker CE" not in desc

    ok = role_wired and compose_plugin and custom_gone and description_aligned
    print(
        f"{'OK' if ok else 'FAIL'}: docker install delegated to geerlingguy.docker "
        f"(role_wired={role_wired} compose_plugin={compose_plugin} "
        f"custom_install_gone={custom_gone} description_aligned={description_aligned} "
        f"[install_task={not no_install_task} "
        f"deb822={not no_docker_repo} packages_var={not no_packages_var} "
        f"python3_debian={not no_python3_debian}])"
    )
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
        test_plex_install_refreshes_after_repo(),
        test_plex_ihd_install_refreshes_after_repo(),
        test_plex_repo_trusted_scoped_to_plex(),
        test_plex_source_trusted_before_baseline_apt(),
        test_plex_render_video_groups_non_unique(),
        test_site_applies_plex_play(),
        test_gen_inventory_renders_plex_group(),
        test_docker_install_delegated_to_geerlingguy_role(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
