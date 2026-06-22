"""Shape test for the vendored, offline-resolvable geerlingguy.docker role.

Step 1 (`resolvable`) of adopting geerlingguy.ansible-role-docker: the role
pinned in `ansible/requirements.yml` must be resolvable ON DISK so the OFFLINE
gate (`ansible-lint --offline` + `ansible-playbook --syntax-check`) can find it
once `docker_host` references it in Step 2 — the gate never reaches Galaxy.

This test guards the "make it resolvable" wiring:

- `ansible/ansible.cfg` `roles_path` includes a dedicated `galaxy_roles` dir
  (alongside the existing `roles` dir, so our own roles still resolve);
- the pinned role is vendored on disk at
  `ansible/galaxy_roles/geerlingguy.docker` as a real role (has `tasks/main.yml`);
- the vendored version matches the EXACT pin in `ansible/requirements.yml`
  (read from the role's `meta/.galaxy_install_info`), so the committed copy can
  never silently drift from the declared pin;
- `ansible/.ansible-lint` excludes `galaxy_roles/` — the vendored third-party
  role does not pass our production lint profile (FQCN/octal/etc.), and it is
  not ours to fix, so it must be excluded or it reddens the gate;
- a `just galaxy` recipe documents/refreshes the install
  (`ansible-galaxy role install -r requirements.yml -p galaxy_roles`).

Dual-mode (module-level test_*()->bool + main()->int), stdlib only, mirroring
scripts/test_galaxy_requirements_shape.py / test_ansible_layout_shape.py
(mem-1781891042-4495). The gate pythons lack PyYAML, so all parsing is plain
regex over the file text. Per mem-1781892715-142d the regexes anchor on the
actual inner content, not just a section opener. The real gate is the
standalone __main__ exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ANSIBLE_DIR = REPO_ROOT / "ansible"
ANSIBLE_CFG = ANSIBLE_DIR / "ansible.cfg"
REQUIREMENTS = ANSIBLE_DIR / "requirements.yml"
ANSIBLE_LINT_CFG = ANSIBLE_DIR / ".ansible-lint"
JUSTFILE = REPO_ROOT / "justfile"
GALAXY_DIR_NAME = "galaxy_roles"
ROLE = "geerlingguy.docker"
VENDORED_ROLE = ANSIBLE_DIR / GALAXY_DIR_NAME / ROLE
INSTALL_INFO = VENDORED_ROLE / "meta" / ".galaxy_install_info"


def _roles_path_entries() -> list[str]:
    """Return the colon-separated roles_path entries from ansible.cfg, or []."""
    if not ANSIBLE_CFG.is_file():
        return []
    m = re.search(r"(?m)^\s*roles_path\s*=\s*(?P<val>.+?)\s*$", ANSIBLE_CFG.read_text())
    if not m:
        return []
    return [p.strip() for p in m.group("val").split(":") if p.strip()]


def _pinned_version() -> str:
    """Return the exact version pinned for geerlingguy.docker in requirements.yml."""
    if not REQUIREMENTS.is_file():
        return ""
    body = REQUIREMENTS.read_text()
    for item in re.findall(r"(?ms)^[ \t]*-[ \t]+.*?(?=^[ \t]*-[ \t]+|\Z)", body):
        if re.search(r"""(?m)(?:src|name)\s*:\s*["']?geerlingguy\.docker["']?\s*$""", item):
            m = re.search(r"""(?m)^\s*version\s*:\s*["']?(?P<v>[^"'\s#]+)""", item)
            return m.group("v") if m else ""
    return ""


def _installed_version() -> str:
    """Return the version recorded in the vendored role's galaxy install info."""
    if not INSTALL_INFO.is_file():
        return ""
    m = re.search(r"""(?m)^\s*version\s*:\s*["']?(?P<v>[^"'\s#]+)""", INSTALL_INFO.read_text())
    return m.group("v") if m else ""


def test_roles_path_includes_galaxy_dir() -> bool:
    """ansible.cfg roles_path must include galaxy_roles AND keep the local roles dir."""
    entries = _roles_path_entries()
    has_galaxy = GALAXY_DIR_NAME in entries
    has_local = "roles" in entries
    ok = has_galaxy and has_local
    print(
        f"{'OK' if ok else 'FAIL'}: ansible.cfg roles_path includes both 'roles' and "
        f"'{GALAXY_DIR_NAME}' (entries={entries})"
    )
    return ok


def test_role_vendored_on_disk() -> bool:
    """The pinned role must be vendored as a real role (has tasks/main.yml)."""
    tasks_main = VENDORED_ROLE / "tasks" / "main.yml"
    ok = VENDORED_ROLE.is_dir() and tasks_main.is_file()
    print(
        f"{'OK' if ok else 'FAIL'}: {ROLE} vendored at "
        f"ansible/{GALAXY_DIR_NAME}/{ROLE} with tasks/main.yml"
    )
    return ok


def test_vendored_version_matches_pin() -> bool:
    """The vendored role version must equal the exact pin in requirements.yml."""
    pinned = _pinned_version()
    installed = _installed_version()
    ok = bool(pinned) and pinned == installed
    print(
        f"{'OK' if ok else 'FAIL'}: vendored {ROLE} version matches requirements.yml pin "
        f"(pinned={pinned!r} installed={installed!r})"
    )
    return ok


def test_ansible_lint_excludes_galaxy_roles() -> bool:
    """ansible/.ansible-lint must exclude galaxy_roles/ (third-party, unlinted)."""
    if not ANSIBLE_LINT_CFG.is_file():
        print("FAIL: ansible/.ansible-lint excludes galaxy_roles/ (file missing)")
        return False
    body = ANSIBLE_LINT_CFG.read_text()
    has_key = re.search(r"(?m)^\s*exclude_paths\s*:", body) is not None
    excludes_galaxy = re.search(rf"(?m){re.escape(GALAXY_DIR_NAME)}/?", body) is not None
    ok = has_key and excludes_galaxy
    print(
        f"{'OK' if ok else 'FAIL'}: ansible/.ansible-lint exclude_paths covers "
        f"{GALAXY_DIR_NAME}/ (exclude_paths={has_key} galaxy_listed={excludes_galaxy})"
    )
    return ok


def test_just_galaxy_recipe() -> bool:
    """justfile must define a `galaxy` recipe installing the pinned role on disk."""
    if not JUSTFILE.is_file():
        print("FAIL: justfile defines a galaxy recipe (file missing)")
        return False
    body = JUSTFILE.read_text()
    # Recipe header `galaxy:` (optionally preceded by attribute lines), then a
    # body line that installs from requirements.yml into the galaxy_roles dir.
    has_recipe = re.search(r"(?m)^galaxy\s*:", body) is not None
    installs = re.search(
        r"ansible-galaxy\s+role\s+install\b.*\brequirements\.yml\b.*\b" + re.escape(GALAXY_DIR_NAME) + r"\b",
        body,
    ) is not None
    ok = has_recipe and installs
    print(
        f"{'OK' if ok else 'FAIL'}: justfile `galaxy` recipe installs requirements.yml "
        f"into {GALAXY_DIR_NAME} (recipe={has_recipe} install_cmd={installs})"
    )
    return ok


def main() -> int:
    results = [
        test_roles_path_includes_galaxy_dir(),
        test_role_vendored_on_disk(),
        test_vendored_version_matches_pin(),
        test_ansible_lint_excludes_galaxy_roles(),
        test_just_galaxy_recipe(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
