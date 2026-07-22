"""Shape test for the vendored, offline-resolvable community.general collection.

Sibling of scripts/test_galaxy_vendored_role_shape.py, one layer over: that file
guards the vendored *role* (geerlingguy.docker), this one guards the vendored
*collection* (community.general), which a later step needs for
`community.general.xml` (Plex's Preferences.xml / TranscoderTempDirectory).

`ansible/requirements.yml` declaring the collection is necessary but NOT
sufficient. Three things must ALSO be true or the declaration is a promise the
repo cannot keep offline:

- the collection is vendored on disk under
  `ansible/galaxy_roles/ansible_collections/community/general` (where
  `ansible-galaxy collection install -p galaxy_roles` puts it), and the module
  the later step actually calls — `plugins/modules/xml.py` — is really there;
- the vendored version equals the EXACT pin in `ansible/requirements.yml`
  (read from MANIFEST.json), so the committed copy cannot silently drift;
- the vendored tree is TRACKED IN GIT. This is the check with teeth: the roles
  half of `galaxy_roles/` is tracked (28 files) while the collections half was
  untracked and NOT gitignored, so `just galaxy`'s own comment — "The result is
  committed so the offline gate (just test) and `just play` resolve them on
  disk with no network" — was false for collections on every checkout but one;
- `ansible/ansible.cfg` declares a `collections_path` covering `galaxy_roles`.
  `roles_path` does not cover collections: without this key Ansible looks only
  in `~/.ansible/collections` and `/usr/share/ansible/collections`, so a
  committed-but-unreferenced tree still would not resolve with no network.

Dual-mode (module-level test_*()->bool + main()->int), stdlib only, mirroring
scripts/test_galaxy_vendored_role_shape.py (mem-1781891042-4495). The gate
pythons lack PyYAML, so requirements.yml is parsed with plain regex, scoped to
the `collections:` block so a `roles:` entry can never satisfy a collection
check (mem-1781892715-142d). The real gate is the standalone __main__ exit code.
"""

import json
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ANSIBLE_DIR = REPO_ROOT / "ansible"
ANSIBLE_CFG = ANSIBLE_DIR / "ansible.cfg"
REQUIREMENTS = ANSIBLE_DIR / "requirements.yml"
GALAXY_DIR_NAME = "galaxy_roles"
COLLECTION = "community.general"
COLLECTIONS_ROOT = ANSIBLE_DIR / GALAXY_DIR_NAME / "ansible_collections"
VENDORED_COLLECTION = COLLECTIONS_ROOT / "community" / "general"
MANIFEST = VENDORED_COLLECTION / "MANIFEST.json"
# The one module the later Plex step actually calls (community.general.xml).
XML_MODULE = VENDORED_COLLECTION / "plugins" / "modules" / "xml.py"
# Premise anchor: the sibling vendored ROLE, tracked since the docker step.
VENDORED_ROLE_FILE = ANSIBLE_DIR / GALAXY_DIR_NAME / "geerlingguy.docker" / "tasks" / "main.yml"


def _pinned_version() -> str:
    """Return the exact version pinned for community.general in requirements.yml.

    SCOPED to the block under the top-level `collections:` key (from that key to
    the next column-0 key or EOF), so a same-named `roles:` entry cannot answer
    for the collection.
    """
    if not REQUIREMENTS.is_file():
        return ""
    body = REQUIREMENTS.read_text()
    m = re.search(r"(?ms)^collections\s*:\s*$(?P<block>.*?)(?=^\S|\Z)", body)
    if not m:
        return ""
    for item in re.findall(r"(?ms)^[ \t]*-[ \t]+.*?(?=^[ \t]*-[ \t]+|\Z)", m.group("block")):
        if re.search(rf"""(?m)(?:name|src)\s*:\s*["']?{re.escape(COLLECTION)}["']?\s*$""", item):
            v = re.search(r"""(?m)^\s*version\s*:\s*["']?(?P<v>[^"'\s#]+)""", item)
            return v.group("v") if v else ""
    return ""


def _installed_version() -> str:
    """Return the version recorded in the vendored collection's MANIFEST.json."""
    if not MANIFEST.is_file():
        return ""
    try:
        info = json.loads(MANIFEST.read_text()).get("collection_info", {})
    except (json.JSONDecodeError, AttributeError):
        return ""
    if f"{info.get('namespace')}.{info.get('name')}" != COLLECTION:
        return ""
    return str(info.get("version") or "")


def _is_tracked(path: pathlib.Path) -> bool:
    """True iff `path` is tracked by git (staged or committed), else False."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files", "--error-unmatch", "--", str(path)],
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return proc.returncode == 0


def _collections_path_entries() -> list[str]:
    """Return the collections_path(s) entries from ansible.cfg, or []."""
    if not ANSIBLE_CFG.is_file():
        return []
    m = re.search(
        r"(?m)^\s*collections_paths?\s*=\s*(?P<val>.+?)\s*$", ANSIBLE_CFG.read_text()
    )
    if not m:
        return []
    return [p.strip() for p in m.group("val").split(":") if p.strip()]


def test_collection_vendored_on_disk() -> bool:
    """The pinned collection must be vendored, including the xml module itself."""
    ok = VENDORED_COLLECTION.is_dir() and MANIFEST.is_file() and XML_MODULE.is_file()
    print(
        f"{'OK' if ok else 'FAIL'}: {COLLECTION} vendored at "
        f"ansible/{GALAXY_DIR_NAME}/ansible_collections/community/general with "
        f"MANIFEST.json + plugins/modules/xml.py"
    )
    return ok


def test_vendored_collection_version_matches_pin() -> bool:
    """The vendored collection version must equal the exact pin in requirements.yml."""
    pinned = _pinned_version()
    installed = _installed_version()
    ok = bool(pinned) and pinned == installed
    print(
        f"{'OK' if ok else 'FAIL'}: vendored {COLLECTION} version matches "
        f"requirements.yml pin (pinned={pinned!r} installed={installed!r})"
    )
    return ok


def test_vendored_collection_tracked_in_git() -> bool:
    """The vendored collection must be TRACKED, like its sibling vendored role.

    Premise sub-check: the sibling role file must read as tracked. If it does
    not, git is unavailable or this is not a checkout, and a bare "collection
    not tracked" verdict would be noise rather than the real defect.
    """
    role_tracked = _is_tracked(VENDORED_ROLE_FILE)
    manifest_tracked = _is_tracked(MANIFEST)
    xml_tracked = _is_tracked(XML_MODULE)
    ok = role_tracked and manifest_tracked and xml_tracked
    print(
        f"{'OK' if ok else 'FAIL'}: vendored {COLLECTION} tracked in git "
        f"(premise sibling_role_tracked={role_tracked} "
        f"manifest={manifest_tracked} xml_module={xml_tracked})"
    )
    return ok


def test_ansible_cfg_collections_path() -> bool:
    """ansible.cfg must declare a collections_path covering galaxy_roles/."""
    entries = _collections_path_entries()
    ok = any(
        e == GALAXY_DIR_NAME or e.rstrip("/").endswith("/" + GALAXY_DIR_NAME)
        for e in entries
    )
    print(
        f"{'OK' if ok else 'FAIL'}: ansible.cfg collections_path covers "
        f"'{GALAXY_DIR_NAME}' (entries={entries})"
    )
    return ok


def main() -> int:
    results = [
        test_collection_vendored_on_disk(),
        test_vendored_collection_version_matches_pin(),
        test_vendored_collection_tracked_in_git(),
        test_ansible_cfg_collections_path(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
