#!/usr/bin/env python3
"""Fix Verifier harness — plex iHD-driver apt cache_valid_time footgun.

Re-runs the ORIGINAL reproduction path against the EXACT bundled ansible-core
apt.py cache-update decision (branch at apt.py:1448-1451), but drives it with the
params parsed LIVE from the fixed role YAML so it exercises the actual fix rather
than a hardcoded assumption.

Sequence that sets the trap (ansible/roles/plex/tasks/main.yml):
  L16 python3-debian apt task (update_cache:true) stamps the apt cache ~= now
  L23 deb822 'debian-extra-components' adds the Debian non-free repo (home of
      intel-media-va-driver-non-free) AFTER that stamp
  L36 'Install the Intel iHD media driver and VA-API tooling' apt installs
      {{ plex_media_packages }} -> if it carries cache_valid_time the refresh is
      SKIPPED on the fresh cache and the non-free repo is never indexed.

Real engine decision (apt.py:1448-1451, verified byte-exact in the bundled module):
    if p['update_cache'] or p['cache_valid_time']:
        now = datetime.datetime.now()
        tdelta = datetime.timedelta(seconds=p['cache_valid_time'])
        if not mtimestamp + tdelta >= now:
            cache.update()   # the refresh that indexes the just-added repo
cache_valid_time default is 0 (apt.py:1272 argument_spec).
"""
import datetime
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ROLE = REPO / "ansible" / "roles" / "plex" / "tasks" / "main.yml"
APT_MODULE = Path(
    "/home/user/.local/share/mise/installs/pipx-ansible/14.1.0/venvs/ansible/"
    "lib/python3.14/site-packages/ansible/modules/apt.py"
)

IHD_TASK_NAME = "Install the Intel iHD media driver and VA-API tooling"


def real_branch_runs_refresh(update_cache, cache_valid_time, cache_age_seconds):
    """Faithful replay of the real apt.py:1448-1451 decision.

    Returns True iff cache.update() would run for a cache stamped
    `cache_age_seconds` ago. mtimestamp is the cache mtime; now is current time.
    """
    now = datetime.datetime.now()
    mtimestamp = now - datetime.timedelta(seconds=cache_age_seconds)
    # Outer guard (apt.py:1448): the block is entered if either is truthy.
    cvt = int(cache_valid_time or 0)
    if not (bool(update_cache) or cvt):
        return False
    tdelta = datetime.timedelta(seconds=cvt)
    # apt.py:1451 — refresh runs only when the cache is OLDER than the window.
    return not (mtimestamp + tdelta >= now)


def confirm_branch_matches_module():
    """Guard: the live bundled apt.py still carries the exact branch we replay."""
    src = APT_MODULE.read_text()
    needed = [
        "if p['update_cache'] or p['cache_valid_time']:",
        "tdelta = datetime.timedelta(seconds=p['cache_valid_time'])",
        "if not mtimestamp + tdelta >= now:",
        "cache_valid_time=dict(type='int', default=0)",
    ]
    missing = [n for n in needed if n not in src]
    if missing:
        print(f"FAIL: bundled apt.py branch drifted, missing: {missing}")
        return False
    print("OK: bundled apt.py cache-update branch matches the replayed decision")
    return True


def parse_ihd_task_params():
    """Parse the LIVE role and return (update_cache, cache_valid_time) for the
    iHD-driver apt task, exactly as ansible would resolve them."""
    tasks = yaml.safe_load(ROLE.read_text())
    for t in tasks:
        if t.get("name") == IHD_TASK_NAME:
            apt = t.get("ansible.builtin.apt") or t.get("apt") or {}
            uc = apt.get("update_cache", False)
            cvt = apt.get("cache_valid_time", 0)  # ansible default is 0
            return uc, cvt, "cache_valid_time" in apt
    raise SystemExit(f"FAIL: iHD-driver task '{IHD_TASK_NAME}' not found in role")


FRESH_AGES = [1, 5, 30, 120]   # cache stamped seconds ago by the prior L16 task
STALE_AGES = [3700, 7200]      # genuinely older than a 3600s window


def main():
    print("== Fix Verifier: plex iHD-driver cache_valid_time footgun ==")
    print(f"Role: {ROLE}")
    print(f"Engine: real bundled ansible-core apt.py branch (apt.py:1448-1451)\n")

    branch_ok = confirm_branch_matches_module()

    uc, cvt, has_cvt = parse_ihd_task_params()
    print(
        f"\nLIVE iHD-driver task params (parsed from fixed role): "
        f"update_cache={uc!r} cache_valid_time={cvt!r} (cache_valid_time key present={has_cvt})"
    )

    # ---- CHECK 1: ORIGINAL REPRO re-run on the FIXED code ----
    # On the fixed task (update_cache:true, NO cache_valid_time -> cvt resolves 0),
    # the refresh must RUN for every fresh cache age -> non-free repo indexed ->
    # intel-media-va-driver-non-free installable. (Pre-fix this was SKIPPED.)
    print("\n-- CHECK 1: original repro path on the LIVE FIXED iHD task --")
    fixed_runs = []
    for age in FRESH_AGES:
        runs = real_branch_runs_refresh(uc, cvt, age)
        fixed_runs.append(runs)
        print(
            f"  fresh cache age {age:>4}s  update_cache={uc} cvt={cvt}"
            f"  -> cache.update RUNS={runs}"
            + ("  (INDEXED -> intel-media-va-driver-non-free installable)" if runs
               else "  (SKIPPED -> repo NOT indexed -> BUG)")
        )
    check1 = all(fixed_runs)
    print(f"  => fixed task refreshes on every fresh age: {check1}")

    # ---- CHECK 2: ORIGINAL BROKEN variant still reproduces the bug ----
    # Re-add cache_valid_time:3600 (the pre-fix state) and confirm the refresh is
    # SKIPPED on the same fresh cache -> proves CHECK 1 is non-vacuous.
    print("\n-- CHECK 2: pre-fix broken variant (cvt=3600) still reproduces the SKIP --")
    broken_skips = []
    for age in FRESH_AGES:
        runs = real_branch_runs_refresh(True, 3600, age)
        broken_skips.append(not runs)
        print(
            f"  fresh cache age {age:>4}s  update_cache=True cvt=3600"
            f"  -> cache.update RUNS={runs}"
            + ("  (SKIPPED -> 'No package matching intel-media-va-driver-non-free')" if not runs
               else "  (unexpectedly RAN)")
        )
    check2 = all(broken_skips)
    print(f"  => broken variant skips on every fresh age (bug reproduces): {check2}")

    # ---- CHECK 3: ADVERSARIAL NEIGHBOR — isolate the fresh-stamp trigger ----
    # cvt=3600 BUT cache genuinely STALE (>3600s) must RUN -> proves the FRESH L16
    # stamp is the trigger, not cvt:3600 alone.
    print("\n-- CHECK 3: adversarial neighbor (cvt=3600 + STALE cache) must RUN --")
    stale_runs = []
    for age in STALE_AGES:
        runs = real_branch_runs_refresh(True, 3600, age)
        stale_runs.append(runs)
        print(
            f"  stale cache age {age:>4}s  update_cache=True cvt=3600"
            f"  -> cache.update RUNS={runs}"
            + ("  (RUNS -> fresh L16 stamp is the sole trigger, not cvt alone)" if runs
               else "  (unexpectedly SKIPPED)")
        )
    check3 = all(stale_runs)
    print(f"  => stale-cache neighbor runs even with cvt=3600 (variable isolated): {check3}")

    # ---- CHECK 4: the fix is actually applied (no cache_valid_time on the task) ----
    print("\n-- CHECK 4: fix applied — iHD task carries update_cache, no cache_valid_time --")
    check4 = bool(uc) and not has_cvt
    print(f"  update_cache truthy={bool(uc)}  cache_valid_time absent={not has_cvt}  => {check4}")

    print("\n== CLASSIFICATION ==")
    print(f"  branch matches real module:          {branch_ok}")
    print(f"  CHECK1 fixed-task refresh runs:      {check1}")
    print(f"  CHECK2 broken variant reproduces:    {check2}")
    print(f"  CHECK3 adversarial isolates trigger: {check3}")
    print(f"  CHECK4 fix applied (no cvt):         {check4}")
    verdict = branch_ok and check1 and check2 and check3 and check4
    print(f"  VERDICT: {'FIX VERIFIED' if verdict else 'FIX FAILED'}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
