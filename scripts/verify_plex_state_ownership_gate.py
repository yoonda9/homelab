"""Fix-verification harness for the Plex state-dir ownership gate (debug:verify).

Runs the role's REAL ownership gate against the LIVE CT 110 without installing,
starting, or chowning anything. The tasks are SLICED VERBATIM out of
`ansible/roles/plex/tasks/main.yml` (never hand-copied), and the vars come from
the role's real `defaults/main.yml`, so this exercises the actual fix rather
than a restatement of it. If the fix changes, this harness follows it.

Why this harness exists: the operator-side `chown -R 100999:100991
/tank/Server/AppData/plex` is destructive on a live 1.2GB library and is
deliberately NOT run by the loop, so PMS stays failed and the original repro
cannot be driven to green here. What CAN be verified live, non-destructively,
is the fix's actual repo-side claim: that the gate detects the raw-ownership
state dir and fails the play loudly with the exact host-side chown, BEFORE the
install/start, instead of leaving PMS crash-looping.

  CHECK1  real gate + real live (broken) state -> assert FAILS, and the message
          names the exact shifted chown and the host path.
  CHECK2  same gate, same live dir, expected ids overridden to the 65534 the dir
          actually carries -> assert PASSES. Non-tautology proof: the gate reads
          the real stat and is not a hardcoded failure.
  CHECK3  adversarial neighbour — expected uid correct (999) but gid wrong ->
          assert FAILS. Isolates the gid as independently load-bearing, which is
          the exact defect (uid==gid) the fix exists to prevent.

Not a `test_*.py`, so it does not join the `run_gate` glob (mem-1782229877-301c).
"""

import json
import pathlib
import re
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ANSIBLE_DIR = REPO_ROOT / "ansible"
PLEX_TASKS = ANSIBLE_DIR / "roles" / "plex" / "tasks" / "main.yml"
PLEX_DEFAULTS = ANSIBLE_DIR / "roles" / "plex" / "defaults" / "main.yml"

START_TASK = "Stat the Plex state directory (the host bind mount lands here)"
END_TASK = "Install Plex Media Server"


def slice_gate_tasks() -> str:
    """Cut the stat+assert tasks verbatim from the real role file."""
    text = PLEX_TASKS.read_text()
    start = re.search(rf"^-\s+name:\s*{re.escape(START_TASK)}\s*$", text, re.MULTILINE)
    end = re.search(rf"^-\s+name:\s*{re.escape(END_TASK)}\s*$", text, re.MULTILINE)
    if not start or not end:
        raise SystemExit(
            f"FAIL: could not slice the gate (start={bool(start)}, end={bool(end)}). "
            "The role's task names changed — update this harness."
        )
    block = text[start.start() : end.start()]
    if "ansible.builtin.assert" not in block or "stat.gid" not in block:
        raise SystemExit("FAIL: sliced block is missing the stat/assert — refusing to run a vacuous check.")
    return block


def run_gate(block: str, extra_vars: dict) -> tuple[int, str]:
    """Run the sliced gate against the live plex host. Returns (rc, output)."""
    play = (
        "---\n"
        "- hosts: plex\n"
        "  gather_facts: false\n"
        "  vars_files:\n"
        f"    - {PLEX_DEFAULTS}\n"
        "  tasks:\n"
    )
    # Indent the verbatim block into the play's task list.
    play += "".join(f"    {line}\n" if line.strip() else "\n" for line in block.splitlines())

    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, dir="/var/tmp") as fh:
        fh.write(play)
        play_path = fh.name

    cmd = ["mise", "exec", "--", "ansible-playbook", "-i", "inventory/hosts.yml", play_path]
    if extra_vars:
        # JSON form, NOT `-e key=value`: the k=v form makes every value a STRING,
        # which does not exercise the real role (defaults/main.yml yields ints)
        # and instead trips the fail_msg's uncoerced `plex_idmap_base + plex_uid`.
        cmd += ["-e", json.dumps(extra_vars)]
    proc = subprocess.run(cmd, cwd=ANSIBLE_DIR, capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


def run_gate_kv(block: str, extra_vars: dict) -> tuple[int, str]:
    """Same gate, but with `-e key=value` so every value arrives as a STRING.

    Used only by CHECK4 to characterise the fail_msg coercion gap.
    """
    play = (
        "---\n"
        "- hosts: plex\n"
        "  gather_facts: false\n"
        "  vars_files:\n"
        f"    - {PLEX_DEFAULTS}\n"
        "  tasks:\n"
    )
    play += "".join(f"    {line}\n" if line.strip() else "\n" for line in block.splitlines())
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, dir="/var/tmp") as fh:
        fh.write(play)
        play_path = fh.name
    cmd = ["mise", "exec", "--", "ansible-playbook", "-i", "inventory/hosts.yml", play_path]
    for key, value in extra_vars.items():
        cmd += ["-e", f"{key}={value}"]
    proc = subprocess.run(cmd, cwd=ANSIBLE_DIR, capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    block = slice_gate_tasks()
    print(f"Sliced gate ({len(block.splitlines())} lines) verbatim from {PLEX_TASKS.relative_to(REPO_ROOT)}\n")
    results = []

    # CHECK1 — real gate, real live state, real expected ids from defaults.
    rc, out = run_gate(block, {})
    failed = rc != 0
    names_chown = "chown -R 100999:100991" in out
    names_path = "/tank/Server/AppData/plex" in out
    saw_nobody = "65534" in out
    ok1 = failed and names_chown and names_path and saw_nobody
    print(
        f"CHECK1 real live state -> gate FAILS the play: rc={rc} failed={failed} "
        f"names_exact_chown={names_chown} names_host_path={names_path} reports_nobody={saw_nobody}"
    )
    print("  OK\n" if ok1 else "  FAIL\n")
    results.append(ok1)

    # CHECK2 — non-tautology: expect the ids the dir REALLY has -> must pass.
    rc, out = run_gate(block, {"plex_uid": 65534, "plex_gid": 65534})
    ok2 = rc == 0
    print(
        f"CHECK2 expected ids = the 65534 the dir actually carries -> gate PASSES: "
        f"rc={rc} (proves the assert reads the real stat, not a hardcoded fail)"
    )
    print("  OK\n" if ok2 else "  FAIL\n")
    results.append(ok2)

    # CHECK3 — adversarial neighbour: correct uid, wrong gid -> must still fail.
    rc, out = run_gate(block, {"plex_uid": 65534, "plex_gid": 991})
    ok3 = rc != 0
    print(
        f"CHECK3 adversarial: uid matches (65534) but gid does not (991) -> gate FAILS: "
        f"rc={rc} (proves gid is independently load-bearing — the uid==gid defect)"
    )
    print("  OK\n" if ok3 else "  FAIL\n")
    results.append(ok3)

    # CHECK4 — now BLOCKING. This started life as a characterisation probe: `that:`
    # coerced both sides with `| int` but fail_msg's `plex_idmap_base + plex_uid`
    # did not, so a string-valued override (`-e plex_uid=999`, or a quoted
    # group_vars value) crashed the template on the ONE path that renders fail_msg
    # — the failing-ownership path, i.e. exactly when the operator needs the chown.
    # fail_msg now coerces every operand, so the crash is gone and this asserts it
    # stays gone. It must still name the chown, not merely avoid raising.
    rc, out = run_gate_kv(block, {"plex_uid": 999, "plex_gid": 991})
    crashes = "unsupported operand type" in out
    ok4 = not crashes and "chown -R 100999:100991" in out
    print(
        f"CHECK4 string-valued override (`-e plex_uid=999`) -> fail_msg renders the "
        f"chown instead of crashing: crashes={crashes} names_chown="
        f"{'chown -R 100999:100991' in out} (rc={rc})"
    )
    print("  OK\n" if ok4 else "  FAIL\n")
    results.append(ok4)

    passed = sum(results)
    total = len(results)
    print(f"{passed}/{total} blocking checks passed")
    print("VERDICT: GATE VERIFIED LIVE" if passed == total else "VERDICT: GATE NOT VERIFIED")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
