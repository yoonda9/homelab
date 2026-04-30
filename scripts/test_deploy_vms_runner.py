"""Adversarial focused test for scripts/deploy_vms.sh — Step 4 wave.

Asserts the runner has:
1. ``genisoimage`` preflight (``command -v genisoimage``) BEFORE
   ``tofu apply -auto-approve``. The Windows module's ``null_resource``
   local-exec depends on ``genisoimage``; failing fast at the runner
   boundary surfaces the missing dependency before ``tofu apply``.
2. Wait gate between ``tofu apply -auto-approve`` and the inventory
   generator (``scripts/tofu_to_inventory.py``):
   - polling-loop construct (``while`` keyword in code lines),
   - ``tofu -chdir=tofu refresh`` invocation each iteration,
   - ``sleep`` between iterations,
   - 30-minute timeout literal (``1800`` seconds).
3. ``shellcheck scripts/deploy_vms.sh`` exit 0 (PASS-WITH-NOTE if the
   tool is missing on the loop env, per ``mem-1777477382-ce4f``).

Mirrors the plain main-runner pattern of
``scripts/test_step5_runner_and_removal.py`` (no pytest).

Honors mem-1777478162-68e8: scans code lines (skips lines whose
``lstrip()`` starts with ``#``) so a comment-only mention of any
marker can't satisfy the check.
"""

import os
import shutil
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY_SCRIPT = os.path.join(REPO_ROOT, "scripts", "deploy_vms.sh")


def _code_lines(path):
    """Return ``[(idx, raw_line), ...]`` for non-comment, non-blank lines.

    Skips lines whose ``lstrip()`` starts with ``#`` (per
    mem-1777478162-68e8). Indices are 0-based source-line indices so
    error messages can render 1-based line numbers.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw_lines = f.read().splitlines()
    out = []
    for idx, line in enumerate(raw_lines):
        stripped = line.lstrip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        out.append((idx, line))
    return out


def _first_line_with(code_lines, predicate):
    """Return the 0-based source index of the first matching code line, or None."""
    for idx, line in code_lines:
        if predicate(line):
            return idx
    return None


def _has_token(line, token):
    """``token`` appears as a whitespace-bounded word in ``line``.

    Bounded by start-of-line, whitespace, ``;``, or ``)`` to avoid
    matching ``while`` inside ``meanwhile`` or ``sleep`` inside
    ``oversleep`` etc. (defensive — none of those appear today, but
    cheap insurance).
    """
    if token not in line:
        return False
    surrounded_by = {"", " ", "\t", ";", "(", ")", "&", "|"}
    pos = 0
    while True:
        found = line.find(token, pos)
        if found == -1:
            return False
        before = line[found - 1] if found > 0 else ""
        after = line[found + len(token)] if found + len(token) < len(line) else ""
        if before in surrounded_by and after in surrounded_by:
            return True
        pos = found + 1


def test_preflight_genisoimage_present():
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"FAIL: '{DEPLOY_SCRIPT}' is missing.")
        return False
    code = _code_lines(DEPLOY_SCRIPT)
    preflight_idx = _first_line_with(code, lambda l: "command -v genisoimage" in l)
    if preflight_idx is None:
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' is missing the genisoimage preflight "
            f"marker 'command -v genisoimage' (in code lines, ignoring "
            f"comments). The Windows module's null_resource local-exec "
            f"depends on genisoimage; the runner must fail fast before "
            f"tofu apply if the binary is absent. Add a 'command -v "
            f"genisoimage' check that exits non-zero with an apt/brew "
            f"installation hint."
        )
        return False
    print(
        f"OK: deploy_vms.sh preflights 'command -v genisoimage' "
        f"(line {preflight_idx + 1})."
    )
    return True


def test_preflight_runs_before_tofu_apply():
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"FAIL: '{DEPLOY_SCRIPT}' is missing.")
        return False
    code = _code_lines(DEPLOY_SCRIPT)
    preflight_idx = _first_line_with(code, lambda l: "command -v genisoimage" in l)
    apply_idx = _first_line_with(
        code,
        lambda l: "tofu" in l and "apply" in l and "-auto-approve" in l,
    )
    if preflight_idx is None:
        print(
            f"FAIL: cannot verify ordering — preflight marker "
            f"'command -v genisoimage' missing from code lines."
        )
        return False
    if apply_idx is None:
        print(
            f"FAIL: cannot verify ordering — 'tofu apply -auto-approve' "
            f"line missing from code lines."
        )
        return False
    if preflight_idx >= apply_idx:
        print(
            f"FAIL: preflight 'command -v genisoimage' (line "
            f"{preflight_idx + 1}) must run BEFORE 'tofu apply "
            f"-auto-approve' (line {apply_idx + 1}); failing fast at the "
            f"runner boundary surfaces the missing dependency before "
            f"tofu plans/applies."
        )
        return False
    print(
        f"OK: preflight (line {preflight_idx + 1}) runs before "
        f"'tofu apply -auto-approve' (line {apply_idx + 1})."
    )
    return True


def test_wait_gate_polling_block_present():
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"FAIL: '{DEPLOY_SCRIPT}' is missing.")
        return False
    code = _code_lines(DEPLOY_SCRIPT)
    refresh_idx = _first_line_with(
        code, lambda l: "tofu -chdir=tofu refresh" in l
    )
    while_idx = _first_line_with(code, lambda l: _has_token(l, "while"))
    sleep_idx = _first_line_with(code, lambda l: _has_token(l, "sleep"))
    timeout_idx = _first_line_with(code, lambda l: "1800" in l)
    missing = []
    if refresh_idx is None:
        missing.append(
            "'tofu -chdir=tofu refresh' (the gate must refresh state each "
            "iteration so qemu-guest-agent IPs become observable)"
        )
    if while_idx is None:
        missing.append(
            "'while' polling-loop keyword (the gate must loop until every "
            "host reports ansible_host or the timeout fires)"
        )
    if sleep_idx is None:
        missing.append(
            "'sleep' between iterations (the gate must back off, not "
            "spin)"
        )
    if timeout_idx is None:
        missing.append(
            "'1800' (the 30-minute timeout literal in seconds — the "
            "gate must give up after 30 minutes)"
        )
    if missing:
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' wait-gate markers missing from "
            f"code lines: " + "; ".join(missing) + "."
        )
        return False
    print(
        f"OK: wait-gate markers present — refresh (line "
        f"{refresh_idx + 1}), while (line {while_idx + 1}), "
        f"sleep (line {sleep_idx + 1}), 1800 (line "
        f"{timeout_idx + 1})."
    )
    return True


def test_wait_gate_runs_between_tofu_apply_and_inventory_generator():
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"FAIL: '{DEPLOY_SCRIPT}' is missing.")
        return False
    code = _code_lines(DEPLOY_SCRIPT)
    apply_idx = _first_line_with(
        code,
        lambda l: "tofu" in l and "apply" in l and "-auto-approve" in l,
    )
    generator_idx = _first_line_with(
        code, lambda l: "scripts/tofu_to_inventory.py" in l
    )
    refresh_idx = _first_line_with(
        code, lambda l: "tofu -chdir=tofu refresh" in l
    )
    while_idx = _first_line_with(code, lambda l: _has_token(l, "while"))
    sleep_idx = _first_line_with(code, lambda l: _has_token(l, "sleep"))
    timeout_idx = _first_line_with(code, lambda l: "1800" in l)
    if apply_idx is None or generator_idx is None:
        print(
            f"FAIL: cannot verify wait-gate ordering — surrounding "
            f"pipeline steps missing (tofu apply line={apply_idx}, "
            f"inventory generator line={generator_idx})."
        )
        return False
    out_of_range = []
    for label, idx in (
        ("'tofu -chdir=tofu refresh'", refresh_idx),
        ("'while' polling-loop", while_idx),
        ("'sleep' backoff", sleep_idx),
        ("'1800' 30-min timeout", timeout_idx),
    ):
        if idx is None:
            out_of_range.append(f"{label} marker missing")
            continue
        if not (apply_idx < idx < generator_idx):
            out_of_range.append(
                f"{label} (line {idx + 1}) is not strictly between "
                f"'tofu apply -auto-approve' (line {apply_idx + 1}) "
                f"and 'scripts/tofu_to_inventory.py' (line "
                f"{generator_idx + 1})"
            )
    if out_of_range:
        print(
            f"FAIL: '{DEPLOY_SCRIPT}' wait-gate ordering invariant "
            f"violated: " + "; ".join(out_of_range) + ". The gate must "
            f"sit between provisioning and inventory regen so the "
            f"generator only runs after every host has an "
            f"ansible_host."
        )
        return False
    print(
        f"OK: wait-gate markers all sit strictly between 'tofu apply' "
        f"(line {apply_idx + 1}) and 'scripts/tofu_to_inventory.py' "
        f"(line {generator_idx + 1})."
    )
    return True


def test_shellcheck_clean():
    """Run shellcheck on deploy_vms.sh; PASS-WITH-NOTE if absent."""
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"FAIL: '{DEPLOY_SCRIPT}' is missing; cannot lint.")
        return False
    shellcheck = shutil.which("shellcheck")
    if shellcheck is None:
        print(
            "PASS-WITH-NOTE: shellcheck not on PATH; per "
            "mem-1777477382-ce4f precedent, recording the absence and "
            "moving on. Install via 'apt install shellcheck' or "
            "'brew install shellcheck' to enable strict checking."
        )
        return True
    result = subprocess.run(
        [shellcheck, DEPLOY_SCRIPT],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        print(
            f"FAIL: shellcheck on '{DEPLOY_SCRIPT}' exited "
            f"{result.returncode}: stdout={result.stdout!r} "
            f"stderr={result.stderr!r}."
        )
        return False
    print("OK: shellcheck on deploy_vms.sh clean.")
    return True


def main():
    checks = [
        ("Preflight 'command -v genisoimage' present", test_preflight_genisoimage_present),
        ("Preflight runs before 'tofu apply -auto-approve'", test_preflight_runs_before_tofu_apply),
        ("Wait-gate polling block present (refresh + while + sleep + 1800)", test_wait_gate_polling_block_present),
        ("Wait-gate sits between 'tofu apply' and inventory generator", test_wait_gate_runs_between_tofu_apply_and_inventory_generator),
        ("shellcheck deploy_vms.sh exit 0 (PASS-WITH-NOTE if missing)", test_shellcheck_clean),
    ]
    results = [(label, fn()) for label, fn in checks]
    print()
    failed = [label for label, passed in results if not passed]
    if failed:
        print(f"FAILED {len(failed)}/{len(results)} checks:")
        for label in failed:
            print(f"  - {label}")
        sys.exit(1)
    print(f"SUCCESS: All {len(results)} Step 4 deploy_vms.sh runner checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
