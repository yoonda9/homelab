"""Shape test for Step 6 — DAS/ZFS migration runbook.

Per design §3 (storage), §6 (mountpoint=/tank decision), §"Risks" (ZFS-on-USB
rows) and the canonical plan Step 6 — verifies the manual, discovery-based
DAS → ZFS migration runbook at `docs/runbooks/das-zfs-migration.md` documents
the import procedure and operational caveats an operator needs:

  * import **by `/dev/disk/by-id`** (USB `/dev/sdX` reorders on replug),
  * a **force import** (`zpool import -f`) for the foreign-hostid case,
  * the host **`mountpoint`** step (`zfs set mountpoint=/tank`),
  * **verify media intact** — the migration acceptance gate,
  * **`autotrim=off`** over USB and a periodic **scrub**,
  * the **`/tank/Media` → `/media`** bind target the Step 7 Plex CT consumes.

The migration itself (physically moving the DAS, importing the single-vdev
pool, verifying media) is manual and explicitly outside the automation "done"
scope; this test only gates that the runbook is present, non-empty, and carries
the required operational anchors.

Follows the repo's dual-mode shape-test convention (see
`test_provider_auth_shape.py`, `test_traefik_config_shape.py`): module-level
`test_<name>() -> bool` functions that print `OK` / `FAIL: ...` (no `assert`),
plus `main() -> int` that sums the booleans and `sys.exit`s non-zero on any
failure. Stdlib only. Regexes anchor on the inner content (mem-1781892715-142d).
The real gate is the standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "das-zfs-migration.md"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def test_runbook_exists_and_nonempty() -> bool:
    body = _read(RUNBOOK)
    ok = len(body.strip()) > 0
    print(
        f"{'OK' if ok else 'FAIL'}: docs/runbooks/das-zfs-migration.md exists "
        f"and is non-empty (chars={len(body)})"
    )
    return ok


def test_runbook_documents_import_procedure() -> bool:
    body = _read(RUNBOOK)
    checks = {
        # Import by stable USB-safe paths, not /dev/sdX.
        "by-id import": re.search(r'/dev/disk/by-id', body) is not None,
        # Force import for the foreign-hostid case — anchored on the zpool
        # import invocation so a stray dash elsewhere can't satisfy it.
        "force import (-f)": re.search(
            r'zpool\s+import[^\n]*\s-f\b', body
        )
        is not None,
        # Host mountpoint set to /tank.
        "mountpoint=/tank": re.search(
            r'mountpoint\s*=\s*/tank\b', body
        )
        is not None,
        # Persist auto-import across reboot via the cachefile.
        "cachefile": "cachefile" in body,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook documents discovery-based import "
        f"(missing={missing})"
    )
    return ok


def test_runbook_verifies_media_intact() -> bool:
    body = _read(RUNBOOK)
    # The migration acceptance gate — allow the research phrasings.
    ok = (
        re.search(r'media\s+intact', body, re.IGNORECASE) is not None
        or re.search(r'raw\s+data\s+intact', body, re.IGNORECASE) is not None
        or re.search(r'verify\b[^\n]*\bmedia', body, re.IGNORECASE) is not None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: runbook documents the verify-media-intact "
        f"acceptance gate"
    )
    return ok


def test_runbook_documents_usb_caveats() -> bool:
    body = _read(RUNBOOK)
    checks = {
        # Keep autotrim off over USB.
        "autotrim off": re.search(
            r'autotrim\s*=?\s*off', body, re.IGNORECASE
        )
        is not None,
        # Periodic scrub.
        "scrub": re.search(r'\bscrub\b', body, re.IGNORECASE) is not None,
        # USB pool-suspend risk + zpool clear recovery.
        "pool-suspend/clear": re.search(r'suspend', body, re.IGNORECASE)
        is not None
        and re.search(r'zpool\s+clear', body) is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook documents USB/ZFS operational "
        f"caveats (missing={missing})"
    )
    return ok


def test_runbook_wires_tank_media_to_plex() -> bool:
    body = _read(RUNBOOK)
    # The host /tank/Media path bound into the CT as /media (Step 7 consumes it),
    # plus the interim empty-placeholder note. The capital-M `Media` matches the
    # pre-existing dataset directory on the pool — the regexes are case-exact so
    # a lowercase regression is caught.
    # ct-side anchor: the bind_mounts snippet's ct_path (a bare `\b/media\b`
    # cannot match here — `\b` needs a word char before the `/`, which only the
    # old lowercase /tank/media ever provided).
    has_bind = re.search(r'/tank/Media', body) is not None and re.search(
        r'ct_path\s*=\s*"/media"', body
    ) is not None
    has_placeholder = re.search(
        r'mkdir\s+-p\s+/tank/Media', body
    ) is not None
    ok = has_bind and has_placeholder
    print(
        f"{'OK' if ok else 'FAIL'}: runbook wires /tank/Media -> /media bind "
        f"with interim placeholder (bind={has_bind}, placeholder={has_placeholder})"
    )
    return ok


TESTS = (
    test_runbook_exists_and_nonempty,
    test_runbook_documents_import_procedure,
    test_runbook_verifies_media_intact,
    test_runbook_documents_usb_caveats,
    test_runbook_wires_tank_media_to_plex,
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
