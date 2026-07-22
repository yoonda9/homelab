"""Shape test for ansible/requirements.yml (geerlingguy.docker step 1).

Step 1 of adopting geerlingguy.ansible-role-docker in the docker_host role:
before the role can be *referenced* (step 2), it must be declared as a pinned,
offline-resolvable Galaxy dependency. This test guards the declaration:

- ansible/requirements.yml exists and is valid YAML (a `roles:` mapping);
- it lists a role whose src/name is `geerlingguy.docker`;
- that role is pinned to an EXACT version (a concrete version string, not
  `latest` or empty) — mirroring the repo's exact-pin reproducibility
  convention (opentofu/packer/just are all pinned exactly).

This step only DECLARES the dependency; docker_host does not yet reference it,
so `ansible-playbook --syntax-check` is unaffected and the full gate stays
GREEN. Step 2 wires the role and retargets the docker install shape test.

Dual-mode (module-level test_*()->bool + main()->int), stdlib only, mirroring
scripts/test_ansible_layout_shape.py (mem-1781891042-4495). The .venv/mise
pythons that run the gate have no PyYAML, so the YAML check uses the real
parser only when importable and otherwise falls back to a stdlib structural
check. Per mem-1781892715-142d the regexes anchor on the inner content (the
actual src/version), not just a section opener, so an empty stub or a `latest`
pin cannot satisfy the checks. The real gate is the standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIREMENTS = REPO_ROOT / "ansible" / "requirements.yml"
ROLE = "geerlingguy.docker"
COLLECTION = "community.general"


def _try_yaml():
    """Return the yaml module if importable, else None (gate pythons lack it)."""
    try:
        import yaml  # type: ignore

        return yaml
    except Exception:
        return None


def _geerlingguy_item(body: str):
    """Return the `roles:` list item text that names geerlingguy.docker, or None.

    A list item runs from its `- ` bullet to the next bullet (or EOF), so the
    sibling `version:` key is captured alongside the `src:`/`name:` key.
    """
    for item in re.findall(r"(?ms)^[ \t]*-[ \t]+.*?(?=^[ \t]*-[ \t]+|\Z)", body):
        if re.search(
            r"""(?m)(?:src|name)\s*:\s*["']?geerlingguy\.docker["']?\s*$""", item
        ):
            return item
    return None


def _collection_item(body: str):
    """Return the `collections:` list item text naming community.general, or None.

    The search is SCOPED to the block under a top-level `collections:` key
    (from that key to the next top-level, column-0 key or EOF). Scoping matters
    for non-vacuity: it means a `roles:` entry can never satisfy a collection
    check, and the collection's `name:` (collections use `name:`, not `src:`)
    is matched against community.general specifically, not any list bullet.
    """
    m = re.search(r"(?ms)^collections\s*:\s*$(?P<block>.*?)(?=^\S|\Z)", body)
    if not m:
        return None
    block = m.group("block")
    for item in re.findall(r"(?ms)^[ \t]*-[ \t]+.*?(?=^[ \t]*-[ \t]+|\Z)", block):
        if re.search(
            r"""(?m)(?:name|src)\s*:\s*["']?community\.general["']?\s*$""", item
        ):
            return item
    return None


def test_requirements_file_exists() -> bool:
    ok = REQUIREMENTS.is_file()
    print(f"{'OK' if ok else 'FAIL'}: ansible/requirements.yml exists at {REQUIREMENTS}")
    return ok


def test_requirements_valid_yaml() -> bool:
    """requirements.yml must be valid YAML with a top-level `roles:` list."""
    if not REQUIREMENTS.is_file():
        print("FAIL: ansible/requirements.yml is valid YAML (file missing)")
        return False
    body = REQUIREMENTS.read_text()
    yaml = _try_yaml()
    if yaml is not None:
        try:
            data = yaml.safe_load(body)
        except Exception as exc:  # noqa: BLE001 - report any parse error
            print(f"FAIL: ansible/requirements.yml is valid YAML (parse error: {exc})")
            return False
        ok = isinstance(data, dict) and isinstance(data.get("roles"), list) and bool(data["roles"])
        print(f"{'OK' if ok else 'FAIL'}: ansible/requirements.yml parses as a roles: list (PyYAML)")
        return ok
    # Stdlib fallback: YAML forbids tab indentation; require a top-level
    # `roles:` key and at least one list item beneath it.
    no_tabs = "\t" not in body
    has_roles_key = re.search(r"(?m)^roles\s*:\s*$", body) is not None
    has_item = re.search(r"(?m)^[ \t]*-[ \t]+\S", body) is not None
    ok = no_tabs and has_roles_key and has_item
    print(
        f"{'OK' if ok else 'FAIL'}: ansible/requirements.yml is structurally valid YAML "
        f"(no_tabs={no_tabs} roles_key={has_roles_key} has_item={has_item})"
    )
    return ok


def test_lists_geerlingguy_docker() -> bool:
    """A roles entry must name geerlingguy.docker via src or name."""
    if not REQUIREMENTS.is_file():
        print("FAIL: requirements.yml lists geerlingguy.docker (file missing)")
        return False
    ok = _geerlingguy_item(REQUIREMENTS.read_text()) is not None
    print(f"{'OK' if ok else 'FAIL'}: requirements.yml lists a role src/name = {ROLE}")
    return ok


def test_geerlingguy_docker_exact_pin() -> bool:
    """The geerlingguy.docker entry must pin an EXACT version (not latest/empty)."""
    if not REQUIREMENTS.is_file():
        print("FAIL: geerlingguy.docker is pinned to an exact version (file missing)")
        return False
    item = _geerlingguy_item(REQUIREMENTS.read_text())
    if item is None:
        print("FAIL: geerlingguy.docker is pinned to an exact version (entry not found)")
        return False
    m = re.search(r"""(?m)^\s*version\s*:\s*["']?(?P<v>[^"'\s#]+)""", item)
    version = m.group("v") if m else ""
    # An exact pin is a concrete version (starts with a digit, optional leading
    # 'v'); `latest`, a floating range, or an empty value must NOT qualify.
    exact = bool(re.fullmatch(r"v?\d[\w.\-+]*", version)) and version.lower() != "latest"
    print(
        f"{'OK' if exact else 'FAIL'}: geerlingguy.docker pinned to an exact version "
        f"(version={version!r})"
    )
    return exact


def test_lists_community_general() -> bool:
    """A collections entry must name community.general (needed for community.general.xml)."""
    if not REQUIREMENTS.is_file():
        print("FAIL: requirements.yml lists community.general (file missing)")
        return False
    ok = _collection_item(REQUIREMENTS.read_text()) is not None
    print(f"{'OK' if ok else 'FAIL'}: requirements.yml lists a collection name = {COLLECTION}")
    return ok


def test_community_general_exact_pin() -> bool:
    """The community.general entry must pin an EXACT version (not latest/empty)."""
    if not REQUIREMENTS.is_file():
        print("FAIL: community.general is pinned to an exact version (file missing)")
        return False
    item = _collection_item(REQUIREMENTS.read_text())
    if item is None:
        print("FAIL: community.general is pinned to an exact version (entry not found)")
        return False
    m = re.search(r"""(?m)^\s*version\s*:\s*["']?(?P<v>[^"'\s#]+)""", item)
    version = m.group("v") if m else ""
    # An exact pin is a concrete version (starts with a digit, optional leading
    # 'v'); `latest`, a floating range, or an empty value must NOT qualify.
    exact = bool(re.fullmatch(r"v?\d[\w.\-+]*", version)) and version.lower() != "latest"
    print(
        f"{'OK' if exact else 'FAIL'}: community.general pinned to an exact version "
        f"(version={version!r})"
    )
    return exact


def main() -> int:
    results = [
        test_requirements_file_exists(),
        test_requirements_valid_yaml(),
        test_lists_geerlingguy_docker(),
        test_geerlingguy_docker_exact_pin(),
        test_lists_community_general(),
        test_community_general_exact_pin(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
