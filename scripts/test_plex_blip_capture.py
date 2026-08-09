"""Tests for scripts/plex_blip_capture.sh — Step 8a (design §4.3 / §5.4).

Stdlib-only shape + behaviour guard, auto-globbed by scripts/run_gate.py (the
gate has no shell-linter step — Step 8 premise 1). The shell-lint idiom
(shebang, `set -euo pipefail`, shellcheck-if-present, shfmt-if-present,
exists+executable) is the `scripts/test_build_template_runner.py` convention
reused verbatim (mem-1777477382-ce4f / mem-1777478162-68e8).

The behavioural test drives the script through a STUB transport
(`PLEX_BLIP_CAPTURE_SSH`) into a temp `PLEX_BLIP_CAPTURE_OUTDIR`, so it needs
NO reachable CT 110 / PVE host (Step 8 premise 2 — `sqlite3` absent, remote
transport must be stub-overridable). This file owns 8a's schema obligation
(T2): every `manifest.json` entry has EXACTLY `{command, host, exit_code,
elapsed_ms, output_file}` with the right types. The `exit_code`/`elapsed_ms`
identity pin (8b, T1), the full §4.3 command set + `-readonly` shape guard
(8c, T3), and one-host-unreachable (8d, T4) are their own rows.
"""

import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "plex_blip_capture.sh"
JUSTFILE = REPO_ROOT / "justfile"

MANIFEST_KEYS = {"command", "host", "exit_code", "elapsed_ms", "output_file"}


def code_lines(body: str) -> list[str]:
    """Body lines minus blank-and-comment-only lines (per mem-1777478162-68e8)."""
    return [ln for ln in body.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


def code_text(body: str) -> str:
    return "\n".join(code_lines(body))


def test_exists_and_executable() -> bool:
    if not SCRIPT.is_file():
        print("FAIL: scripts/plex_blip_capture.sh missing")
        return False
    ok = bool(SCRIPT.stat().st_mode & stat.S_IXUSR)
    print(f"{'OK' if ok else 'FAIL'}: scripts/plex_blip_capture.sh executable bit set")
    return ok


def test_shebang_and_set() -> bool:
    if not SCRIPT.is_file():
        print("FAIL: shebang/set check skipped — script missing")
        return False
    lines = SCRIPT.read_text().splitlines()
    shebang_ok = lines[0].strip() == "#!/usr/bin/env bash"
    set_ok = any("set -euo pipefail" in ln for ln in lines[:10])
    print(f"{'OK' if shebang_ok else 'FAIL'}: shebang #!/usr/bin/env bash")
    print(f"{'OK' if set_ok else 'FAIL'}: set -euo pipefail in first 10 lines")
    return shebang_ok and set_ok


def test_shellcheck() -> bool:
    if not shutil.which("shellcheck"):
        print("OK (skip): shellcheck not installed")
        return True
    if not SCRIPT.is_file():
        print("FAIL: shellcheck skipped — script missing")
        return False
    r = subprocess.run(["shellcheck", str(SCRIPT)], capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"{'OK' if ok else 'FAIL'}: shellcheck ({r.stdout.strip() or 'clean'})")
    return ok


def test_shfmt_format_clean() -> bool:
    if not shutil.which("shfmt"):
        print("OK (skip): shfmt not installed (PASS-WITH-NOTE)")
        return True
    if not SCRIPT.is_file():
        print("FAIL: shfmt skipped — script missing")
        return False
    r = subprocess.run(["shfmt", "-i", "2", "-d", str(SCRIPT)], capture_output=True, text=True)
    ok = r.returncode == 0 and not r.stdout.strip()
    print(f"{'OK' if ok else 'FAIL'}: shfmt -i 2 -d clean")
    return ok


def test_just_target_present() -> bool:
    """`just plex-blip-capture` must exist and invoke the script."""
    if not JUSTFILE.is_file():
        print("FAIL: justfile missing")
        return False
    body = JUSTFILE.read_text()
    lines = body.splitlines()
    recipe_idx = next(
        (i for i, ln in enumerate(lines) if ln.rstrip().startswith("plex-blip-capture:")),
        -1,
    )
    if recipe_idx == -1:
        print("FAIL: no 'plex-blip-capture:' recipe in justfile")
        return False
    # The recipe body (indented lines below the header) must call the script.
    tail = "\n".join(lines[recipe_idx + 1 : recipe_idx + 6])
    invokes = "scripts/plex_blip_capture.sh" in tail
    print(f"{'OK' if invokes else 'FAIL'}: 'plex-blip-capture' recipe invokes scripts/plex_blip_capture.sh")
    return invokes


def _run_capture(tmp: pathlib.Path) -> tuple[pathlib.Path, subprocess.CompletedProcess]:
    """Drive the script with a stub transport into a temp bundle dir."""
    outdir = tmp / "bundle"
    stub = tmp / "stub_ssh.sh"
    # Stub receives (host, command); it echoes deterministic output and exits 0,
    # so the run needs no reachable host and no real ssh/curl/sqlite3.
    stub.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'echo "stub-transport host=$1"\n'
        'echo "cmd=$2"\n'
    )
    stub.chmod(0o755)
    env = dict(os.environ)
    env["PLEX_BLIP_CAPTURE_OUTDIR"] = str(outdir)
    env["PLEX_BLIP_CAPTURE_SSH"] = str(stub)
    env["PLEX_BLIP_CAPTURE_CT110_HOST"] = "fake-ct110"
    env["PLEX_BLIP_CAPTURE_PVE_HOST"] = "fake-pve"
    r = subprocess.run(
        ["bash", str(SCRIPT)], capture_output=True, text=True, env=env
    )
    return outdir, r


def test_runs_and_writes_schema_valid_manifest() -> bool:
    """T2: end-to-end run produces a schema-valid manifest.json — every entry
    has EXACTLY the five documented keys, with the right types, and each
    output_file it names exists in the bundle."""
    if not SCRIPT.is_file():
        print("FAIL: run check skipped — script missing")
        return False
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        outdir, r = _run_capture(tmp)

        checks: dict[str, bool] = {}
        checks["script exits 0 (vertical slice runs to completion)"] = r.returncode == 0
        if r.returncode != 0:
            print(f"  script stderr:\n{r.stderr}")

        manifest_path = outdir / "manifest.json"
        checks["manifest.json written"] = manifest_path.is_file()

        entries = None
        if manifest_path.is_file():
            try:
                entries = json.loads(manifest_path.read_text())
                checks["manifest.json is valid JSON"] = True
            except json.JSONDecodeError as exc:
                checks["manifest.json is valid JSON"] = False
                print(f"  JSON decode error: {exc}")

        checks["manifest is a non-empty list of entries"] = (
            isinstance(entries, list) and len(entries) > 0
        )

        if isinstance(entries, list):
            all_keys_exact = True
            all_types_ok = True
            all_outputs_exist = True
            hosts_seen = set()
            for e in entries:
                if not isinstance(e, dict) or set(e.keys()) != MANIFEST_KEYS:
                    all_keys_exact = False
                    continue
                hosts_seen.add(e.get("host"))
                # Types: str/str/int/number/str; bool must NOT satisfy the
                # numeric slots (isinstance(True, int) is True in Python).
                if not (
                    isinstance(e["command"], str)
                    and isinstance(e["host"], str)
                    and isinstance(e["exit_code"], int)
                    and not isinstance(e["exit_code"], bool)
                    and isinstance(e["elapsed_ms"], (int, float))
                    and not isinstance(e["elapsed_ms"], bool)
                    and isinstance(e["output_file"], str)
                ):
                    all_types_ok = False
                out = outdir / e["output_file"]
                if not out.is_file():
                    all_outputs_exist = False
            checks["every entry has EXACTLY {command,host,exit_code,elapsed_ms,output_file}"] = all_keys_exact
            checks["entry field types are str/str/int/number/str (no bool in numeric slots)"] = all_types_ok
            checks["every output_file named exists in the bundle"] = all_outputs_exist
            # Host is recorded per entry from the (overridden) targets, not hardcoded.
            checks["per-entry host reflects the configured targets"] = hosts_seen == {"fake-ct110", "fake-pve"}

        for what, ok in checks.items():
            print(f"{'OK' if ok else 'FAIL'}: {what}")
        return all(checks.values())


def main() -> int:
    results = [
        test_exists_and_executable(),
        test_shebang_and_set(),
        test_shellcheck(),
        test_shfmt_format_clean(),
        test_just_target_present(),
        test_runs_and_writes_schema_valid_manifest(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
