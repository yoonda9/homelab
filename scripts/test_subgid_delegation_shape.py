"""Shape test — host `/etc/subgid` delegation prereq for the Plex CT idmap.

Regression guard for the CT110 startup failure
``newgidmap: gid range [44-45) -> [44-45) not allowed`` (DEBUG.md). Confirmed
root cause (mem-1782092977-83db, decisive real-``newgidmap`` experiment): the
unprivileged Plex CT idmap punches host GIDs **44** (`video`) and **993**
(`render`) 1:1, but Proxmox's default ``root:100000:65536`` allocation does not
delegate those two size-1 punch ranges, so ``newgidmap`` refuses to write them
and the container never starts. The tofu-generated map is correct (byte-for-byte
match) and the **uid** side needs nothing — so the fix is a HOST-SIDE prereq
outside tofu's reach: append ``root:44:1`` + ``root:993:1`` to ``/etc/subgid`` on
``pve``.

This test gates that the prereq is **documented and discoverable** — it would
have caught the original gap, where ``grep -ri subgid`` over the repo returned
nothing (undocumented + unenforced). It anchors on:

  * ``host-bootstrap.md`` (primary) — both ``root:44:1`` and ``root:993:1``
    ``/etc/subgid`` lines, an explicit note that ``/etc/subuid`` needs nothing,
    and the ``newgidmap`` failure symptom that motivates them;
  * ``das-zfs-migration.md`` (idmap-fallback note) — that the ``newgidmap``
    startup failure / ``/etc/subgid`` delegation is checked before flipping to a
    privileged CT.

Follows the repo's dual-mode shape-test convention (see
``test_runbook_shape.py``, ``test_provider_auth_shape.py``): module-level
``test_<name>() -> bool`` functions that print ``OK`` / ``FAIL: ...`` (no
``assert``), plus ``main() -> int`` that sums the booleans and ``sys.exit``s
non-zero on any failure. Stdlib only. Regexes anchor on the inner content
(mem-1781892715-142d). The real gate is the standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOKS = REPO_ROOT / "docs" / "runbooks"
HOST_BOOTSTRAP = RUNBOOKS / "host-bootstrap.md"
DAS_ZFS = RUNBOOKS / "das-zfs-migration.md"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def test_host_bootstrap_documents_subgid_lines() -> bool:
    """Both punch-GID delegations must be present, each as its own line."""
    body = _read(HOST_BOOTSTRAP)
    checks = {
        # video=44 punch delegated 1:1 to root.
        "root:44:1": re.search(r'root:44:1\b', body) is not None,
        # render=993 punch delegated 1:1 to root.
        "root:993:1": re.search(r'root:993:1\b', body) is not None,
        # Named target file so the operator knows WHERE the lines go.
        "/etc/subgid": "/etc/subgid" in body,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: host-bootstrap.md delegates the punch GIDs "
        f"in /etc/subgid (missing={missing})"
    )
    return ok


def test_host_bootstrap_notes_subuid_needs_nothing() -> bool:
    """The uid side requires no extra delegation — must be stated, not implied."""
    body = _read(HOST_BOOTSTRAP)
    # /etc/subuid mentioned in a context that says it needs nothing / no change.
    ok = re.search(
        r'/etc/subuid[^\n]*\b(?:need|nothing|no\b)', body, re.IGNORECASE
    ) is not None or re.search(
        r'subuid\s+needs\s+nothing', body, re.IGNORECASE
    ) is not None
    print(
        f"{'OK' if ok else 'FAIL'}: host-bootstrap.md states /etc/subuid needs "
        f"no extra delegation"
    )
    return ok


def test_host_bootstrap_shows_newgidmap_symptom() -> bool:
    """The motivating failure symptom must be present so the doc is findable."""
    body = _read(HOST_BOOTSTRAP)
    ok = (
        re.search(r'newgidmap', body) is not None
        and re.search(r'gid range \[44-45\)', body) is not None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: host-bootstrap.md shows the newgidmap "
        f"startup-failure symptom"
    )
    return ok


def test_das_zfs_fallback_checks_subgid_before_privileged() -> bool:
    """The idmap-fallback note must point at the subgid fix before privileged."""
    body = _read(DAS_ZFS)
    # newgidmap symptom OR /etc/subgid named in the fallback note.
    ok = (
        re.search(r'/etc/subgid', body) is not None
        or re.search(r'newgidmap', body) is not None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: das-zfs-migration.md idmap-fallback note "
        f"references the /etc/subgid delegation / newgidmap failure"
    )
    return ok


TESTS = (
    test_host_bootstrap_documents_subgid_lines,
    test_host_bootstrap_notes_subuid_needs_nothing,
    test_host_bootstrap_shows_newgidmap_symptom,
    test_das_zfs_fallback_checks_subgid_before_privileged,
)


def main() -> int:
    results = [fn() for fn in TESTS]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
