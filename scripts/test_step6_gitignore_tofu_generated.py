"""Adversarial smoke test for Step 6: gitignore the regenerated inventory.

Mirrors the shape of the prior `scripts/test_tofu_*.py` scripts and
`scripts/test_step5_runner_and_removal.py`: invoke `git` against the
working tree, assert the expected exit codes, fail with a precise
message otherwise. Plain main runner — no pytest.

Coverage:
1. `git check-ignore --no-index -q ansible/inventory/tofu_generated.yml`
   exits 0 (the regenerated artifact must be ignored so `bash
   scripts/deploy_vms.sh` does not dirty `git status`).
2. `git check-ignore --no-index -q ansible/inventory/hosts.yml` exits 1
   (the static inventory must NOT be matched by the rule — defends
   against an over-broad pattern such as `*.yml`).
3. `git ls-files ansible/inventory/hosts.yml` is non-empty (hosts.yml
   is and stays tracked).

`--no-index` is required for the negative check: without it,
`git check-ignore` short-circuits to exit 1 for any path already in the
index (tracked files are never reported as ignored), so an over-broad
pattern like `*.yml` would slip past a tracked-file check. With
`--no-index` the gitignore rules are evaluated independent of tracking
state, which is what we actually want to test.

Failure messages name the path, the expected exit code, and the actual
exit code so a regression pinpoints exactly which check slipped.
"""

import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOFU_GENERATED = os.path.join("ansible", "inventory", "tofu_generated.yml")
STATIC_INVENTORY = os.path.join("ansible", "inventory", "hosts.yml")


def _git_check_ignore(path):
    """Return the exit code of `git check-ignore --no-index -q <path>`.

    Exit 0 = path matches an ignore rule. Exit 1 = path does NOT match.
    `--no-index` evaluates the rules independent of whether the path is
    currently tracked, which is what we want to test (a tracked file
    short-circuits to exit 1 without it, hiding over-broad patterns).
    Any other exit code indicates a fatal git error.
    """
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stderr


def _git_ls_files(path):
    result = subprocess.run(
        ["git", "ls-files", "--", path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def test_tofu_generated_inventory_is_gitignored():
    code, stderr = _git_check_ignore(TOFU_GENERATED)
    assert code == 0, (
        f"{TOFU_GENERATED} must be gitignored: expected "
        f"`git check-ignore -q` exit 0 (ignored), got exit {code}. "
        f"stderr={stderr!r}. The regenerated inventory artifact must "
        "not dirty `git status` after `bash scripts/deploy_vms.sh`."
    )


def test_static_hosts_inventory_is_not_gitignored():
    code, stderr = _git_check_ignore(STATIC_INVENTORY)
    assert code == 1, (
        f"{STATIC_INVENTORY} must NOT be gitignored: expected "
        f"`git check-ignore -q` exit 1 (not ignored), got exit {code}. "
        f"stderr={stderr!r}. An over-broad pattern (e.g. `*.yml`) "
        "would catch the static inventory; the rule must be path-scoped."
    )


def test_static_hosts_inventory_is_tracked():
    code, stdout, stderr = _git_ls_files(STATIC_INVENTORY)
    assert code == 0, (
        f"`git ls-files {STATIC_INVENTORY}` exited {code}: stderr={stderr!r}"
    )
    assert stdout.strip(), (
        f"{STATIC_INVENTORY} must remain tracked: `git ls-files` "
        "returned an empty result. The static inventory is the source "
        "of truth for non-Tofu-managed hosts and must stay in the repo."
    )


TESTS = (
    test_tofu_generated_inventory_is_gitignored,
    test_static_hosts_inventory_is_not_gitignored,
    test_static_hosts_inventory_is_tracked,
)


def main():
    passed = 0
    failed = 0
    for test in TESTS:
        try:
            test()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL: {test.__name__}: {exc}")
        else:
            passed += 1
            print(f"PASS: {test.__name__}")
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
