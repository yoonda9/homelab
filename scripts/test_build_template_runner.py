"""Tests for scripts/build_template.sh (per design §7.2).

Comment-line-skipping body scan (per mem-1777478162-68e8) so substring
checks don't false-pass on bare comments. shellcheck enforced; shfmt
PASS-WITH-NOTE if missing (per mem-1777477382-ce4f).
"""

import pathlib
import re
import shutil
import stat
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "build_template.sh"


def code_lines(body: str) -> list[str]:
    """Body lines minus blank-and-comment-only lines (per mem-1777478162-68e8)."""
    return [ln for ln in body.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


def code_text(body: str) -> str:
    return "\n".join(code_lines(body))


def test_exists_and_executable() -> bool:
    if not RUNNER.is_file():
        print("FAIL: scripts/build_template.sh missing")
        return False
    mode = RUNNER.stat().st_mode
    ok = bool(mode & stat.S_IXUSR)
    print(f"{'OK' if ok else 'FAIL'}: scripts/build_template.sh executable bit set")
    return ok


def test_shebang_and_set() -> bool:
    if not RUNNER.is_file():
        print("FAIL: shebang/set check skipped — runner missing")
        return False
    body = RUNNER.read_text()
    lines = body.splitlines()
    shebang_ok = lines[0].strip() == "#!/usr/bin/env bash"
    set_ok = any("set -euo pipefail" in ln for ln in lines[:10])
    print(f"{'OK' if shebang_ok else 'FAIL'}: shebang #!/usr/bin/env bash")
    print(f"{'OK' if set_ok else 'FAIL'}: set -euo pipefail in first 10 lines")
    return shebang_ok and set_ok


def test_shellcheck() -> bool:
    if not shutil.which("shellcheck"):
        print("OK (skip): shellcheck not installed")
        return True
    if not RUNNER.is_file():
        print("FAIL: shellcheck skipped — runner missing")
        return False
    r = subprocess.run(["shellcheck", str(RUNNER)], capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"{'OK' if ok else 'FAIL'}: shellcheck ({r.stdout.strip() or 'clean'})")
    return ok


def test_shfmt_format_clean() -> bool:
    if not shutil.which("shfmt"):
        print("OK (skip): shfmt not installed (PASS-WITH-NOTE)")
        return True
    if not RUNNER.is_file():
        print("FAIL: shfmt skipped — runner missing")
        return False
    r = subprocess.run(["shfmt", "-i", "2", "-d", str(RUNNER)], capture_output=True, text=True)
    ok = r.returncode == 0 and not r.stdout.strip()
    print(f"{'OK' if ok else 'FAIL'}: shfmt -i 2 -d clean")
    return ok


def test_arg_validation_and_envvar_preflight() -> bool:
    if not RUNNER.is_file():
        print("FAIL: arg/env preflight skipped — runner missing")
        return False
    body = RUNNER.read_text()
    ct = code_text(body)
    checks = {
        "PROXMOX_HOST preflight":         "PROXMOX_HOST" in ct,
        "PROXMOX_USER preflight":         "PROXMOX_USER" in ct,
        "PROXMOX_TOKEN_ID preflight":     "PROXMOX_TOKEN_ID" in ct,
        "PROXMOX_TOKEN_SECRET preflight": "PROXMOX_TOKEN_SECRET" in ct,
        "ubuntu26 case branch":           bool(re.search(r"\bubuntu26\b", ct)),
        "fedora case branch":             bool(re.search(r"\bfedora\b", ct)),
        "windows11 case branch":          bool(re.search(r"\bwindows11\b", ct)),
        "usage / error on unknown OS":    bool(re.search(r"(usage|Usage|UNKNOWN|unknown)", ct)),
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def test_windows11_specific_steps() -> bool:
    if not RUNNER.is_file():
        print("FAIL: windows11 steps skipped — runner missing")
        return False
    body = RUNNER.read_text()
    ct = code_text(body)
    checks = {
        "command -v genisoimage preflight":   bool(re.search(r"command\s+-v\s+genisoimage", ct)),
        "genisoimage invocation":              bool(re.search(r"\bgenisoimage\b[^|&;]*-volid\s+[\"']?Unattend", ct, re.DOTALL)),
        "autounattend.iso output path":        "autounattend-win11.iso" in ct,
        "packer/autounattend/windows11 input": "packer/autounattend/windows11" in ct,
    }
    for what, ok in checks.items():
        print(f"{'OK' if ok else 'FAIL'}: {what}")
    return all(checks.values())


def test_packer_init_then_build_force() -> bool:
    if not RUNNER.is_file():
        print("FAIL: packer init/build ordering skipped — runner missing")
        return False
    body = RUNNER.read_text()
    lines = code_lines(body)
    ct = "\n".join(lines)
    init_idx = next((i for i, ln in enumerate(lines) if re.search(r"\bpacker\s+init\b", ln)), -1)
    build_idx = next((i for i, ln in enumerate(lines) if re.search(r"\bpacker\s+build\b", ln)), -1)
    ordered = init_idx != -1 and build_idx != -1 and init_idx < build_idx
    build_uses_force = bool(re.search(r"packer\s+build[^|&;\n]*-force", ct))
    print(f"{'OK' if ordered else 'FAIL'}: packer init (line {init_idx}) precedes packer build (line {build_idx})")
    print(f"{'OK' if build_uses_force else 'FAIL'}: packer build uses -force")
    return ordered and build_uses_force


def test_packer_build_uses_directory_form() -> bool:
    """Regression: packer build must use directory form '-only=<source> .' so
    _variables.pkr.hcl siblings are loaded (per mem-1777854396-6d9e). Single-file
    form 'packer build foo.pkr.hcl' does NOT load directory siblings, leaving
    var.* references undeclared at HCL parse → 8x 'Unsupported attribute' errors.
    """
    if not RUNNER.is_file():
        print("FAIL: packer build directory-form check skipped — runner missing")
        return False
    body = RUNNER.read_text()
    lines = code_lines(body)
    # Match the actual command line, not log/echo strings that mention 'packer build'.
    build_lines = [ln for ln in lines if re.search(r"^\s*packer\s+build\b", ln)]
    if not build_lines:
        print("FAIL: no 'packer build' command line found")
        return False
    build_line = build_lines[0]
    uses_only = bool(re.search(r"-only=[\"']?proxmox-iso\.", build_line))
    # Directory form: trailing '.' as positional arg, NOT a single-file 'X.pkr.hcl'.
    uses_dir = bool(re.search(r"\s\.\s*$", build_line))
    no_single_file = not re.search(r"\b[\w$\"'{}]+\.pkr\.hcl\b", build_line)
    print(f"{'OK' if uses_only else 'FAIL'}: packer build uses -only=proxmox-iso.<name>")
    print(f"{'OK' if uses_dir else 'FAIL'}: packer build targets directory '.' (not a single .pkr.hcl file)")
    print(f"{'OK' if no_single_file else 'FAIL'}: packer build line has no '<name>.pkr.hcl' positional arg")
    return uses_only and uses_dir and no_single_file


def main() -> int:
    results = [
        test_exists_and_executable(),
        test_shebang_and_set(),
        test_shellcheck(),
        test_shfmt_format_clean(),
        test_arg_validation_and_envvar_preflight(),
        test_windows11_specific_steps(),
        test_packer_init_then_build_force(),
        test_packer_build_uses_directory_form(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
