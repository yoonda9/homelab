#!/usr/bin/env python3
"""Aggregate offline backpressure gate for the proxmox-homelab repo (Step 12).

`just test` calls this. It runs, in order, the entire offline gate that
every prior step invoked by hand, and exits non-zero if ANY part fails:

  1. Every ``scripts/test_*.py`` shape-test, each via ``python <file>`` — the
     real gate is each file's standalone ``__main__`` exit code, never pytest's
     collector over the scripts directory (the pre-existing
     ``test_pkr_cloud_seed.py`` collection artifacts would break such a run;
     mem-1781891042-4495 / Step-1 AC5). The glob auto-includes any new
     shape-test file, so the gate never silently drops one.
  2. OpenTofu: ``tofu fmt -check -recursive``, then ``tofu init -backend=false``
     (root carries module blocks since Step 3/7) + ``tofu validate``, in tofu/.
  3. Ansible: ``ansible-lint --offline`` (production profile) + ``ansible-playbook
     --syntax-check site.yml``, in ansible/, with ``ANSIBLE_VAULT_PASSWORD=CHANGEME``
     exported so group_vars/vault.yml decrypts on load.

OpenTofu and Ansible run through ``mise exec --`` so the pinned toolchain is
used. Stdlib only. Aggregate-and-report: every step runs, a summary prints, and
the process exits 1 if any step failed (legible failure output over fail-fast).
"""

import os
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
TOFU_DIR = REPO_ROOT / "tofu"
ANSIBLE_DIR = REPO_ROOT / "ansible"


def _run(label: str, cmd: list[str], cwd: pathlib.Path, env=None) -> bool:
    """Run one gate step; print its command + result; return True on exit 0."""
    print(f"\n=== {label} ===")
    print(f"$ {' '.join(cmd)}  (cwd={cwd})")
    proc = subprocess.run(cmd, cwd=str(cwd), env=env)
    ok = proc.returncode == 0
    print(f"-> {'OK' if ok else 'FAIL'} (exit {proc.returncode})")
    return ok


def _steps() -> list[tuple[str, list[str], pathlib.Path, dict | None]]:
    """Build the ordered gate: all shape-tests, then tofu, then ansible."""
    # Ansible tooling decrypts the committed placeholder vault on load.
    ansible_env = dict(os.environ)
    ansible_env.setdefault("ANSIBLE_VAULT_PASSWORD", "CHANGEME")

    steps: list[tuple[str, list[str], pathlib.Path, dict | None]] = []

    # 1. Every standalone shape-test (glob auto-includes new files).
    for path in sorted(SCRIPTS_DIR.glob("test_*.py")):
        rel = path.relative_to(REPO_ROOT)
        steps.append((f"shape: {rel}", [sys.executable, str(path)], REPO_ROOT, None))

    # 2. OpenTofu fmt + validate (init first — root has module blocks).
    steps += [
        ("tofu fmt -check", ["mise", "exec", "--", "tofu", "fmt", "-check", "-recursive"], TOFU_DIR, None),
        ("tofu init", ["mise", "exec", "--", "tofu", "init", "-backend=false", "-input=false"], TOFU_DIR, None),
        ("tofu validate", ["mise", "exec", "--", "tofu", "validate"], TOFU_DIR, None),
    ]

    # 3. Ansible offline lint + syntax-check.
    steps += [
        ("ansible-lint --offline", ["mise", "exec", "--", "ansible-lint", "--offline", "--profile", "production"], ANSIBLE_DIR, ansible_env),
        ("ansible-playbook --syntax-check", ["mise", "exec", "--", "ansible-playbook", "--syntax-check", "site.yml"], ANSIBLE_DIR, ansible_env),
    ]
    return steps


def main() -> int:
    steps = _steps()
    failed = [label for label, cmd, cwd, env in steps if not _run(label, cmd, cwd, env)]

    total = len(steps)
    print("\n" + "=" * 60)
    if failed:
        print(f"GATE FAIL: {len(failed)}/{total} step(s) failed: {failed}")
        return 1
    print(f"GATE PASS: {total}/{total} steps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
