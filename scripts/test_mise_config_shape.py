"""Shape test for the mise dev-environment foundation (Step 1: direnv -> mise).

Per design SS5.5/Appendix A and DEC-001 — verifies the committed `mise.toml`
pins the tooling (incl. the `just` task runner) and, after the Step-4 cutover,
carries NO `[tasks.*]` (the justfile is now the sole task interface). It also
carries the non-secret Proxmox env + python venv config, keeps the secret half
only in the gitignored `mise.local.toml` (template committed as
`mise.local.toml.example`), and proves the legacy direnv `.envrc` approach is
fully gone.

Follows the repo's dual-mode shape-test convention (see
`test_dev_vm_module_shape.py`, `test_repo_artifacts.py`): module-level
`test_<name>() -> bool` functions that print `OK` / `FAIL: ...` (no `assert`),
plus `main() -> int` that sums the booleans and `sys.exit`s non-zero on any
failure. Stdlib only. The real gate is the standalone exit code.

Per `mem-1777480918-6c5f`, `git check-ignore` is always invoked with
`--no-index` so ignore rules are evaluated independent of tracking state.
"""

import pathlib
import re
import subprocess
import sys
import tomllib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MISE_TOML = REPO_ROOT / "mise.toml"
MISE_LOCAL_EXAMPLE = REPO_ROOT / "mise.local.toml.example"
GITIGNORE = REPO_ROOT / ".gitignore"
# Step 12 — the capstone aggregate `just test` gate and its sign-off runbook.
ACCEPTANCE_RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "acceptance-validation.md"

# Tool keys mise.toml [tools] must pin (DEC-001 / design Appendix A). `just` is
# the task runner the Step-4 cutover migrated onto (asserted separately below).
REQUIRED_TOOLS = ("opentofu", "packer", "python", "pipx:ansible")
# Secret-bearing keys that must NEVER appear in the committed mise.toml —
# the Tofu/Cloudflare half plus the four Packer vars (DEC-001).
# NB: the Tofu provider authenticates with the root@pam username/password TICKET,
# not an API token — PROXMOX_VE_API_TOKEN is deliberately absent from the provider
# env (bpg token precedence would otherwise shadow the ticket and 403 the Plex CT
# device passthrough). The Packer build keeps its own separate PROXMOX_TOKEN_*.
SECRET_KEYS = (
    "PROXMOX_VE_SSH_USERNAME",
    "PROXMOX_VE_PASSWORD",
    "CLOUDFLARE_DNS_API_TOKEN",
    "PROXMOX_HOST",
    "PROXMOX_USER",
    "PROXMOX_TOKEN_ID",
    "PROXMOX_TOKEN_SECRET",
)
PLACEHOLDER = "CHANGEME"


def _load_mise_toml() -> dict | None:
    """Parse mise.toml with stdlib tomllib; return None if absent/invalid."""
    if not MISE_TOML.is_file():
        return None
    try:
        with MISE_TOML.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError:
        return None


def git_ls_files(*paths: str) -> list[str]:
    """Return `git ls-files <paths...>` output as a list of lines."""
    result = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def git_check_ignore(path: str) -> int:
    """Exit code of `git check-ignore --no-index -q <path>` (0 = ignored)."""
    return subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", path],
        cwd=REPO_ROOT,
    ).returncode


def test_mise_toml_parses() -> bool:
    data = _load_mise_toml()
    ok = data is not None
    print(f"{'OK' if ok else 'FAIL'}: mise.toml exists and parses as TOML")
    return ok


def test_tools_pinned() -> bool:
    data = _load_mise_toml() or {}
    tools = data.get("tools", {})
    bad = [
        t for t in REQUIRED_TOOLS
        if not isinstance(tools.get(t), str) or not tools.get(t, "").strip()
    ]
    ok = not bad
    print(
        f"{'OK' if ok else 'FAIL'}: [tools] pins {list(REQUIRED_TOOLS)} "
        f"with non-empty versions (bad={bad})"
    )
    return ok


def test_just_pinned() -> bool:
    """Step-4 cutover: mise [tools] still pins the `just` task runner."""
    data = _load_mise_toml() or {}
    tools = data.get("tools", {})
    val = tools.get("just")
    ok = isinstance(val, str) and bool(val.strip())
    print(
        f"{'OK' if ok else 'FAIL'}: [tools] pins the `just` task runner "
        f"(value={val!r})"
    )
    return ok


def test_no_tasks_block() -> bool:
    """Step-4 cutover: the justfile is the sole task interface — mise has
    no `[tasks.*]` blocks left (re-adding one reddens this; non-tautology)."""
    data = _load_mise_toml() or {}
    tasks = data.get("tasks", {}) or {}
    ok = not tasks
    print(
        f"{'OK' if ok else 'FAIL'}: mise.toml has no [tasks.*] blocks "
        f"(migrated to the justfile) (found={sorted(tasks)})"
    )
    return ok


def test_nonsecret_env_present() -> bool:
    data = _load_mise_toml() or {}
    env = data.get("env", {})
    has_endpoint = bool(str(env.get("PROXMOX_VE_ENDPOINT", "")).strip())
    has_insecure = "PROXMOX_VE_INSECURE" in env
    venv = (((env.get("_") or {}).get("python") or {}).get("venv")) or {}
    venv_ok = venv.get("path") == ".venv" and venv.get("create") is True
    ok = has_endpoint and has_insecure and venv_ok
    print(
        f"{'OK' if ok else 'FAIL'}: [env] has PROXMOX_VE_ENDPOINT + "
        f"PROXMOX_VE_INSECURE and _.python.venv(path=.venv, create=true) "
        f"(endpoint={has_endpoint}, insecure={has_insecure}, venv={venv_ok})"
    )
    return ok


def test_local_example_tracked() -> bool:
    exists = MISE_LOCAL_EXAMPLE.is_file()
    tracked = "mise.local.toml.example" in git_ls_files("mise.local.toml.example")
    ok = exists and tracked
    print(
        f"{'OK' if ok else 'FAIL'}: mise.local.toml.example exists and is "
        f"tracked (exists={exists}, tracked={tracked})"
    )
    return ok


def test_local_secrets_gitignored() -> bool:
    ignored = git_check_ignore("mise.local.toml")
    example = git_check_ignore("mise.local.toml.example")
    ok = ignored == 0 and example == 1
    print(
        f"{'OK' if ok else 'FAIL'}: mise.local.toml ignored (exit {ignored}, "
        f"want 0) and mise.local.toml.example NOT ignored (exit {example}, "
        f"want 1)"
    )
    return ok


def test_no_envrc_remains() -> bool:
    on_disk = [
        n for n in (".envrc", ".envrc.local")
        if (REPO_ROOT / n).exists()
    ]
    tracked = git_ls_files(".envrc", ".envrc.local")
    gi = GITIGNORE.read_text() if GITIGNORE.is_file() else ""
    gi_lines = {line.strip() for line in gi.splitlines()}
    block_remains = bool({".envrc", ".envrc.local"} & gi_lines)
    ok = not on_disk and not tracked and not block_remains
    print(
        f"{'OK' if ok else 'FAIL'}: no .envrc remains "
        f"(on_disk={on_disk}, tracked={tracked}, gitignore_block={block_remains})"
    )
    return ok


def test_no_plaintext_secrets_committed() -> bool:
    # Committed mise.toml must contain none of the secret key names.
    mise_text = MISE_TOML.read_text() if MISE_TOML.is_file() else ""
    leaked = [k for k in SECRET_KEYS if k in mise_text]
    # In the .example, every secret key must carry a placeholder value.
    example_ok = True
    bad_placeholders: list[str] = []
    if MISE_LOCAL_EXAMPLE.is_file():
        try:
            with MISE_LOCAL_EXAMPLE.open("rb") as fh:
                ex_env = tomllib.load(fh).get("env", {})
        except tomllib.TOMLDecodeError:
            ex_env = {}
            example_ok = False
        for k in SECRET_KEYS:
            if k not in ex_env or ex_env.get(k) != PLACEHOLDER:
                bad_placeholders.append(k)
        example_ok = example_ok and not bad_placeholders
    else:
        example_ok = False
    ok = not leaked and example_ok
    print(
        f"{'OK' if ok else 'FAIL'}: no plaintext secrets committed "
        f"(mise.toml leaks={leaked}, .example non-placeholder={bad_placeholders})"
    )
    return ok


def test_acceptance_runbook_documents_reproducibility() -> bool:
    """Step 12: the rebuild-from-code cycle + WAN-block acceptance is documented."""
    body = ACCEPTANCE_RUNBOOK.read_text() if ACCEPTANCE_RUNBOOK.is_file() else ""
    checks = {
        "exists/non-empty": len(body.strip()) > 0,
        # The clean rebuild-from-code cycle: destroy -> apply -> gen-inventory -> play.
        "tofu destroy": re.search(r"tofu\s+destroy", body) is not None,
        "just apply": re.search(r"just\s+apply", body) is not None,
        "just gen-inventory": re.search(
            r"just\s+gen-inventory", body
        )
        is not None,
        "just play": re.search(r"just\s+play", body) is not None,
        # Adversarial WAN-block acceptance: grafana blocked from WAN while
        # plex returns 200 — the headline Plex-only-public invariant.
        "wan-block grafana": (
            re.search(r"grafana\.yoonnation\.com", body) is not None
            and re.search(r"\bWAN\b", body) is not None
        ),
        "plex 200 from wan": (
            re.search(r"plex\.yoonnation\.com", body) is not None
            and re.search(r"\b200\b", body) is not None
        ),
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: docs/runbooks/acceptance-validation.md "
        f"documents the rebuild cycle + adversarial WAN-block (missing={missing})"
    )
    return ok


TESTS = (
    test_mise_toml_parses,
    test_tools_pinned,
    test_just_pinned,
    test_no_tasks_block,
    test_nonsecret_env_present,
    test_local_example_tracked,
    test_local_secrets_gitignored,
    test_no_envrc_remains,
    test_no_plaintext_secrets_committed,
    test_acceptance_runbook_documents_reproducibility,
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
