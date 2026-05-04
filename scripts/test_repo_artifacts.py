"""Repo-tracking shape test for the cloud-image flow (Step 4a).

Settles the cloud-image flow into git. The Linux Packer templates now
read seed files from ``packer/seed/<os>/{user-data,meta-data}`` and the
runner delegates one-time-per-cloud-image bootstrap to
``scripts/bootstrap_cloud_template.sh``. None of that is durable until
those files are tracked. Symmetrically, the proxmox plugin downloads
cloud images into ``packer/downloaded_iso_path/`` (multi-GB qcow2/iso
artifacts), which must NOT enter git history.

Asserts (against ``git ls-files`` and ``git check-ignore --no-index``):

(1a) ``git ls-files packer/http`` is empty — the autoinstall/kickstart
     remnants are no longer tracked.
(1b) ``git ls-files`` includes all four NoCloud seed files
     (``packer/seed/{ubuntu26,fedora}/{user-data,meta-data}``).
(1c) ``git ls-files`` includes ``scripts/bootstrap_cloud_template.sh``
     and ``scripts/test_pkr_cloud_seed.py``.
(1d) ``git check-ignore --no-index -q packer/downloaded_iso_path/foo.qcow2``
     exits 0 — a synthetic path under the cache directory matches an
     ignore rule.
(1e) ``git check-ignore --no-index -q packer/downloaded_iso_path`` exits 0
     — the directory itself is covered.
(1f) Negative: ``git check-ignore --no-index -q
     packer/seed/ubuntu26/user-data`` exits 1 — the ignore rule must
     be path-scoped, not over-broad enough to swallow the seed.
(1g) Negative: ``git check-ignore --no-index -q
     scripts/bootstrap_cloud_template.sh`` exits 1.

Per ``mem-1777480918-6c5f``, ``git check-ignore`` without ``--no-index``
short-circuits to exit 1 for tracked paths regardless of whether a
matching pattern exists. Always pass ``--no-index`` so the gitignore
evaluation is independent of tracking state — otherwise an over-broad
pattern can slip past a tracked-file check.
"""

import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

SEED_FILES = (
    "packer/seed/ubuntu26/user-data",
    "packer/seed/ubuntu26/meta-data",
    "packer/seed/fedora/user-data",
    "packer/seed/fedora/meta-data",
)
SCRIPT_FILES = (
    "scripts/bootstrap_cloud_template.sh",
    "scripts/test_pkr_cloud_seed.py",
)
IGNORED_PATHS = (
    "packer/downloaded_iso_path/foo.qcow2",
    "packer/downloaded_iso_path",
)
NOT_IGNORED_PATHS = (
    "packer/seed/ubuntu26/user-data",
    "scripts/bootstrap_cloud_template.sh",
)


def git_ls_files(*paths: str) -> list[str]:
    """Return ``git ls-files <paths...>`` output as a list of lines."""
    result = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def git_check_ignore(path: str) -> int:
    """Return the exit code of ``git check-ignore --no-index -q <path>``.

    ``--no-index`` evaluates rules independent of tracking state per
    ``mem-1777480918-6c5f``.
    """
    return subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", path],
        cwd=REPO_ROOT,
    ).returncode


def test_packer_http_not_tracked() -> bool:
    tracked = git_ls_files("packer/http")
    ok = tracked == []
    print(
        f"{'OK' if ok else 'FAIL'}: 1a: git ls-files packer/http empty "
        f"(found {len(tracked)} entries: {tracked})"
    )
    return ok


def test_seed_files_tracked() -> bool:
    tracked = set(git_ls_files(*SEED_FILES))
    missing = [p for p in SEED_FILES if p not in tracked]
    ok = not missing
    if ok:
        print(f"OK: 1b: all 4 seed files tracked: {list(SEED_FILES)}")
    else:
        print(f"FAIL: 1b: seed files not tracked: {missing}")
    return ok


def test_scripts_tracked() -> bool:
    tracked = set(git_ls_files(*SCRIPT_FILES))
    missing = [p for p in SCRIPT_FILES if p not in tracked]
    ok = not missing
    if ok:
        print(f"OK: 1c: scripts tracked: {list(SCRIPT_FILES)}")
    else:
        print(f"FAIL: 1c: scripts not tracked: {missing}")
    return ok


def test_download_cache_file_ignored() -> bool:
    rc = git_check_ignore(IGNORED_PATHS[0])
    ok = rc == 0
    print(
        f"{'OK' if ok else 'FAIL'}: 1d: git check-ignore --no-index "
        f"{IGNORED_PATHS[0]} (exit {rc}, want 0)"
    )
    return ok


def test_download_cache_dir_ignored() -> bool:
    rc = git_check_ignore(IGNORED_PATHS[1])
    ok = rc == 0
    print(
        f"{'OK' if ok else 'FAIL'}: 1e: git check-ignore --no-index "
        f"{IGNORED_PATHS[1]} (exit {rc}, want 0)"
    )
    return ok


def test_seed_file_not_ignored() -> bool:
    rc = git_check_ignore(NOT_IGNORED_PATHS[0])
    ok = rc == 1
    print(
        f"{'OK' if ok else 'FAIL'}: 1f: git check-ignore --no-index "
        f"{NOT_IGNORED_PATHS[0]} (exit {rc}, want 1 — NOT ignored)"
    )
    return ok


def test_bootstrap_script_not_ignored() -> bool:
    rc = git_check_ignore(NOT_IGNORED_PATHS[1])
    ok = rc == 1
    print(
        f"{'OK' if ok else 'FAIL'}: 1g: git check-ignore --no-index "
        f"{NOT_IGNORED_PATHS[1]} (exit {rc}, want 1 — NOT ignored)"
    )
    return ok


TESTS = (
    test_packer_http_not_tracked,
    test_seed_files_tracked,
    test_scripts_tracked,
    test_download_cache_file_ignored,
    test_download_cache_dir_ignored,
    test_seed_file_not_ignored,
    test_bootstrap_script_not_ignored,
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
