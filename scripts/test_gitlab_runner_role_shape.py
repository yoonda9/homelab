"""Shape tests for ansible/roles/gitlab_runner (gitlab-runner Step 3b).

Covers the skeleton and harden.yml only; later steps add the docker meta
dependency, daemon.json and handler arms. Text-based, stdlib only (PyYAML is
not guaranteed in the gate venv).
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "gitlab_runner"


def _read(rel: str) -> str:
    p = ROLE / rel
    return p.read_text() if p.is_file() else ""


def _report(ok: bool, msg: str) -> bool:
    print(f"{'OK' if ok else 'FAIL'}: {msg}")
    return ok


def test_layout() -> bool:
    missing = [f for f in ("defaults/main.yml", "meta/main.yml", "tasks/main.yml", "tasks/harden.yml") if not (ROLE / f).is_file()]
    return _report(not missing, f"role has its slice-1 files (missing: {missing})")


def test_main_imports_harden() -> bool:
    return _report(
        bool(re.search(r"import_tasks:\s*harden\.yml", _read("tasks/main.yml"))),
        "tasks/main.yml imports harden.yml",
    )


def test_sshd_dropin() -> bool:
    t = _read("tasks/harden.yml")
    ok = (
        "/etc/ssh/sshd_config.d/00-homelab-hardening.conf" in t
        and "PasswordAuthentication no" in t
        and "sshd -t" in t
        and "Restart ssh" in t
    )
    return _report(ok, "harden.yml writes the validated 00-homelab-hardening.conf drop-in (PasswordAuthentication no) and notifies Restart ssh")


def test_cloud_init_removed() -> bool:
    t = _read("tasks/harden.yml")
    ok = bool(re.search(r"/etc/ssh/sshd_config\.d/50-cloud-init\.conf\s*\n(?:\s+\S.*\n)*?\s+state:\s*absent", t))
    return _report(ok, "harden.yml removes 50-cloud-init.conf (state: absent)")


def test_user_locked() -> bool:
    t = _read("tasks/harden.yml")
    ok = bool(re.search(r"password_lock:\s*true", t)) and "gitlab_runner_admin_user" in t
    return _report(ok, "harden.yml locks the admin user's password")


def test_needrestart_exclusion() -> bool:
    t = _read("tasks/harden.yml")
    d = _read("defaults/main.yml")
    units_ok = all(u in (t + d) for u in ("docker", "containerd", "gitlab-runner"))
    ok = "/etc/needrestart/conf.d/" in t and "$nrconf{override_rc}" in (t + _read("templates/needrestart.conf.j2")) and units_ok
    stat_m = re.search(r"ansible\.builtin\.stat:\n\s+path:\s*/usr/sbin/needrestart\n\s+register:\s*(\w+)", t)
    reg = stat_m.group(1) if stat_m else None
    tmpl_m = re.search(r"ansible\.builtin\.template:\n(?:\s+\S.*\n)*?\s+dest:\s*/etc/needrestart/conf\.d/[^\n]*\n((?:\s+\S.*\n?)*)", t)
    when_m = re.search(r"^\s+when:\s*(\S+)\s*$", tmpl_m.group(1), re.M) if tmpl_m else None
    guarded = bool(reg) and bool(when_m) and when_m.group(1) == f"{reg}.stat.exists"
    return _report(ok and guarded, "needrestart exclusion names docker, containerd and gitlab-runner, only when needrestart is installed")


def test_no_cross_role_src() -> bool:
    bad = []
    for p in ROLE.rglob("*.yml"):
        if re.search(r"\bsrc:\s*\S*roles/", p.read_text()) or "../" in p.read_text():
            bad.append(p.name)
    return _report(not bad, f"no cross-role src references (offenders: {bad})")


def test_geerlingguy_dependency() -> bool:
    m = _read("meta/main.yml")
    ok = (
        bool(re.search(r"role:\s*geerlingguy\.docker", m))
        and bool(re.search(r"docker_packages_state:\s*present", m))
        and bool(re.search(r"docker_daemon_options:\s*\{\}", m))
        and bool(re.search(r"docker_restart_handler_state:\s*started", m))
        and bool(re.search(r"docker_users:\s*\[\]", m))
    )
    return _report(ok, "meta depends on geerlingguy.docker with present / {} / started / [] vars")


def test_daemon_json_notifies_drain() -> bool:
    t = _read("tasks/docker.yml")
    m = re.search(r"template:\n(?:\s+\S.*\n)*?\s+dest:\s*/etc/docker/daemon\.json\n((?:\s+\S.*\n?)*)", t)
    block = m.group(0) if m else ""
    ok = bool(m) and "src: daemon.json.j2" in block and bool(re.search(r"notify:\s*Drain and restart docker\s*$", block, re.M))
    ok = ok and not re.search(r"notify:\s*(Restart docker|restart docker)\b", t)
    return _report(ok, "daemon.json is templated by the role and notifies 'Drain and restart docker', not a bare docker restart")


def test_daemon_json_log_caps() -> bool:
    t = _read("templates/daemon.json.j2")
    ok = '"log-driver": "json-file"' in t and '"max-size": "10m"' in t and '"max-file": "3"' in t
    return _report(ok, "daemon.json.j2 caps json-file logs at 10m x 3")


def test_main_imports_docker() -> bool:
    return _report(
        bool(re.search(r"import_tasks:\s*docker\.yml", _read("tasks/main.yml"))),
        "tasks/main.yml imports docker.yml",
    )


def test_drain_handler_order() -> bool:
    h = _read("handlers/main.yml")
    names = re.findall(r"^- name:\s*(.+)$", h, re.M)
    probe = h.find("systemctl cat gitlab-runner")
    stop = re.search(r"name:\s*gitlab-runner\n\s+state:\s*stopped", h)
    restart = re.search(r"name:\s*docker\n\s+state:\s*restarted", h)
    start = re.search(r"name:\s*gitlab-runner\n\s+state:\s*started", h)
    in_order = bool(stop and restart and start) and 0 <= probe < stop.start() < restart.start() < start.start()
    listens = len(re.findall(r"listen:\s*Drain and restart docker\s*$", h, re.M))
    # stop and start are gated on the unit existing; docker restart is not
    gated = len(re.findall(r"when:\s*\S*\.rc\s*==\s*0", h)) == 2
    ok = "Drain and restart docker" in names and in_order and listens >= 3 and gated
    return _report(ok, "Drain and restart docker: probe unit, stop gitlab-runner, restart docker, start gitlab-runner (stop/start only if the unit exists)")


def test_site_play() -> bool:
    site = (REPO_ROOT / "ansible" / "site.yml").read_text()
    plays = re.split(r"(?m)^- name:", site)[1:]
    ok = any(
        re.search(r"hosts:\s*gitlab_runner\s*$", pl, re.M)
        and re.search(r"become:\s*true", pl)
        and re.search(r"roles:\s*\n\s+-\s+gitlab_runner\s*$", pl, re.M)
        for pl in plays
    )
    first_all = site.find("hosts: all")
    runner = site.find("hosts: gitlab_runner")
    return _report(ok and 0 <= first_all < runner, "site.yml has a gitlab_runner play (become, role gitlab_runner) after the common play")


def test_common_lists_ubuntu() -> bool:
    m = (REPO_ROOT / "ansible" / "roles" / "common" / "meta" / "main.yml").read_text()
    ok = bool(re.search(r"name:\s*Ubuntu\n\s+versions:\n\s+-\s+resolute", m)) and "name: Debian" in m
    return _report(ok, "common meta platforms list Ubuntu resolute beside Debian")


def test_install_yml() -> bool:
    t = _read("tasks/install.yml")
    key = re.search(r"get_url:\n(?:\s+\S.*\n)*?\s+url:\s*https://packages\.gitlab\.com/gpgkey/gpg\.key\n(?:\s+\S.*\n)*?\s+dest:\s*/etc/apt/keyrings/gitlab-runner\.asc", t)
    repo = re.search(r"deb822_repository:\n((?:\s+\S.*\n?)*)", t)
    r = repo.group(1) if repo else ""
    repo_ok = (
        "https://packages.gitlab.com/runner/gitlab-runner/ubuntu" in r
        and "ansible_facts['distribution_release']" in r
        and "signed_by: /etc/apt/keyrings/gitlab-runner.asc" in r
        and "components: main" in r
    )
    pkgs = re.search(r"ansible\.builtin\.apt:\n((?:\s+\S.*\n?)*)", t)
    p = pkgs.group(1) if pkgs else ""
    pkgs_ok = "gitlab-runner\n" in p and "gitlab-runner-helper-images" in p and "update_cache: true" in p
    env_ok = bool(re.search(r"environment:\n\s+NO_DOCKER_PRUNE:\s*[\"']?1[\"']?\s*$", t, re.M))
    return _report(bool(key) and repo_ok and pkgs_ok and env_ok, "install.yml: GitLab key + deb822 source (release suite), both packages with NO_DOCKER_PRUNE=1")


def test_main_imports_install_after_docker() -> bool:
    m = _read("tasks/main.yml")
    i, d = m.find("install.yml"), m.find("docker.yml")
    return _report(0 <= d < i, "tasks/main.yml imports install.yml after docker.yml")


def main() -> int:
    results = [fn() for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
