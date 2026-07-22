"""Shape test for Step 2 — Plex transcode ramdisk host-tmpfs runbook.

Per `.agents/planning/2026-07-22-plex-ramdisk-transcoding/` (plan.md Step 2,
design/detailed-design.md §"Host tmpfs") — verifies the manual, OPERATOR-run
procedure at `docs/runbooks/plex-ramdisk.md` documents the host-level `tmpfs`
that Step 3 later bind-mounts into CT 110 as `/transcode`:

  * the exact `/etc/fstab` line — a **`tmpfs`** at **`/mnt/plex-transcode`**,
    **`size=4G`** (fixed cap), owned by the **shifted** IDs
    **`uid=100999,gid=100991`**,
  * the **shifted-id rationale**: the unprivileged CT's `+100000` idmap offset
    maps in-CT `plex` (`999:991`) to host `100999:100991`, and a mount owned by
    anything else surfaces as `nobody` inside the container,
  * the **size-cap / host-stability rationale**: a fixed `size=4G` caps the RAM
    a transcode storm can consume, so the mount fills (ENOSPC) instead of OOMing
    the host,
  * the split of responsibilities — the host `ssh pve` + `/etc/fstab` edit +
    `mount -a` is an **OPERATOR** step (this repo/agent does not touch host
    fstab), while the repo-side deliverable is this runbook,
  * the **verification** anchors: `findmnt /mnt/plex-transcode` shows a `tmpfs`,
    and `stat` shows `Uid`/`Gid` `100999`/`100991`.

Step 2's host apply is operator/live-ops and outside the automation gate; this
test only gates that the runbook is present, non-empty, and carries the required
operational anchors — the same scope as the other `*_runbook_shape.py` tests.

Follows the repo's dual-mode shape-test convention (see `test_runbook_shape.py`,
`test_tailscale_split_dns_runbook_shape.py`): module-level `test_<name>() -> bool`
functions that print `OK` / `FAIL: ...` (no `assert`), plus `main() -> int` that
sums the booleans and `sys.exit`s non-zero on any failure. Stdlib only. Regexes
anchor on the inner content (mem-1781892715-142d). The gate discovers this file
by glob (`scripts/run_gate.py`), and `main()` sums the `TESTS` tuple — a function
not listed there would be green-by-omission (mem-1784137124-c346), so every
`test_*` below is registered in `TESTS`.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "plex-ramdisk.md"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _flat(body: str) -> str:
    # Collapse whitespace so assertions are robust to markdown line-wrapping.
    return " ".join(body.split())


def test_runbook_exists_and_nonempty() -> bool:
    body = _read(RUNBOOK)
    ok = len(body.strip()) > 0
    print(
        f"{'OK' if ok else 'FAIL'}: docs/runbooks/plex-ramdisk.md exists and is "
        f"non-empty (chars={len(body)})"
    )
    return ok


def test_fstab_tmpfs_line() -> bool:
    """The load-bearing artifact: the exact fstab tmpfs entry, in one line.

    Anchored as a single fstab record (fs_spec=tmpfs, fs_file=/mnt/plex-transcode,
    fs_vfstype=tmpfs, then the options) so a stray `tmpfs` or `size=4G` mentioned
    elsewhere in prose cannot satisfy it — the source, mountpoint, type, size cap
    and BOTH shifted ids must co-occur on the same fstab line.
    """
    body = _read(RUNBOOK)
    flat = _flat(body)
    # tmpfs  /mnt/plex-transcode  tmpfs  <opts incl size=4G,uid=100999,gid=100991>
    line = re.search(
        r'\btmpfs\s+/mnt/plex-transcode\s+tmpfs\s+(\S+)',
        flat,
    )
    opts = line.group(1) if line else ""
    checks = {
        "fstab record (tmpfs /mnt/plex-transcode tmpfs …)": line is not None,
        "size=4G cap in opts": re.search(r'\bsize=4G\b', opts) is not None,
        "uid=100999 in opts": re.search(r'\buid=100999\b', opts) is not None,
        "gid=100991 in opts": re.search(r'\bgid=100991\b', opts) is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook carries the exact fstab tmpfs line "
        f"(opts={opts!r}, missing={missing})"
    )
    return ok


def test_shifted_id_rationale() -> bool:
    """Why 100999:100991 and not 999:991 — the +100000 idmap shift.

    Requires the offset, the in-CT plex ids, the shifted host ids, AND the
    failure mode (wrong owner -> nobody), so a bare number dump cannot pass.
    """
    body = _read(RUNBOOK)
    flat = _flat(body)
    checks = {
        "+100000 offset": re.search(r'\b100000\b', flat) is not None,
        "unprivileged CT": re.search(
            r'unprivileged', flat, re.IGNORECASE
        )
        is not None,
        "in-CT plex 999/991": re.search(r'\b999\b', flat) is not None
        and re.search(r'\b991\b', flat) is not None,
        "shifted host 100999/100991": re.search(r'\b100999\b', flat) is not None
        and re.search(r'\b100991\b', flat) is not None,
        # The consequence of getting ownership wrong: the CT sees nobody/nogroup.
        "nobody failure mode": re.search(
            r'\bnobody\b|\bnogroup\b|\b65534\b', flat, re.IGNORECASE
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook explains the shifted-id "
        f"(+100000) ownership rationale (missing={missing})"
    )
    return ok


def test_size_cap_host_stability_rationale() -> bool:
    """Why a FIXED size=4G — it caps RAM so the host cannot be OOM'd."""
    body = _read(RUNBOOK)
    flat = _flat(body)
    mentions_cap = re.search(
        r'\bcap\w*\b|\bfixed[- ]size\b|\bsize=4G\b', flat, re.IGNORECASE
    ) is not None
    # The stability argument: bounded RAM / no OOM / host stability paramount,
    # near a mention of memory or the host.
    stability = (
        re.search(
            r'(?:cap|bound|fixed|limit)\w*.{0,160}?(?:RAM|memory|OOM|host)',
            flat,
            re.IGNORECASE,
        )
        is not None
        or re.search(
            r'(?:RAM|memory|OOM|host)\b.{0,160}?(?:cap|bound|fixed|limit)\w*',
            flat,
            re.IGNORECASE,
        )
        is not None
    )
    # Overflow is graceful: ENOSPC / "no space left", not a crash.
    graceful = re.search(
        r'ENOSPC|no space left|full', flat, re.IGNORECASE
    ) is not None
    ok = mentions_cap and stability and graceful
    print(
        f"{'OK' if ok else 'FAIL'}: runbook justifies the fixed size=4G cap for "
        f"host stability (cap={mentions_cap}, stability={stability}, "
        f"graceful={graceful})"
    )
    return ok


def test_operator_host_apply_boundary() -> bool:
    """The apply is an OPERATOR step on `pve`; the agent/repo does not do it.

    Requires the concrete host commands (mkdir + mount -a on pve, editing
    /etc/fstab) AND an explicit operator/manual boundary marker.
    """
    body = _read(RUNBOOK)
    flat = _flat(body)
    checks = {
        "targets pve host": re.search(r'\bpve\b', flat) is not None,
        "edits /etc/fstab": re.search(r'/etc/fstab', flat) is not None,
        "mkdir mount point": re.search(
            r'mkdir\s+-p\s+/mnt/plex-transcode', flat
        )
        is not None,
        "mount -a apply": re.search(r'\bmount\s+-a\b', flat) is not None,
        # This is a human step, not agent-run — the runbook must say so.
        "operator/manual boundary": re.search(
            r'\boperator\b|\bmanual(?:ly)?\b|\bby hand\b', flat, re.IGNORECASE
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook scopes the host apply as an operator "
        f"step (mkdir/fstab/mount -a on pve) (missing={missing})"
    )
    return ok


def test_verification_anchors() -> bool:
    """Post-apply checks: findmnt shows tmpfs; stat shows the shifted ids."""
    body = _read(RUNBOOK)
    flat = _flat(body)
    checks = {
        "findmnt /mnt/plex-transcode": re.search(
            r'findmnt\s+/mnt/plex-transcode', flat
        )
        is not None,
        "stat for ownership": re.search(
            r'\bstat\b.{0,120}?/mnt/plex-transcode'
            r'|/mnt/plex-transcode.{0,40}?\bstat\b',
            flat,
        )
        is not None,
        # Verify the resulting owner is the shifted pair (Uid 100999 / Gid 100991).
        "verify shifted owner": re.search(r'\b100999\b', flat) is not None
        and re.search(r'\b100991\b', flat) is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook documents findmnt/stat verification "
        f"of the mounted tmpfs + shifted owner (missing={missing})"
    )
    return ok


TESTS = (
    test_runbook_exists_and_nonempty,
    test_fstab_tmpfs_line,
    test_shifted_id_rationale,
    test_size_cap_host_stability_rationale,
    test_operator_host_apply_boundary,
    test_verification_anchors,
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
