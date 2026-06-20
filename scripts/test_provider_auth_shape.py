"""Shape test for Step 2 — provider auth + host bootstrap runbook.

Per design SS5.2/SS5.3 and the canonical plan Step 2 — verifies the root
OpenTofu config can authenticate against the Proxmox host `pve`:

  * `tofu/versions.tf` floors `bpg/proxmox` at `>= 0.108.0` (the create-time
    idmap fix needed by the Plex CT in Step 7),
  * `tofu/providers.tf` carries an `ssh {}` block (`agent = true`, username
    from the `PROXMOX_VE_SSH_USERNAME` env var) so bpg has the SSH-backed
    operations idmap/bind-mounts need,
  * a harmless auth-exercising `data` source exists so `tofu plan` forces a
    real authenticated round-trip with no resource changes,
  * `docs/runbooks/host-bootstrap.md` documents the manual host prereqs
    (API token, provider SSH, `getent group render video` GID check, the
    router port-forward placeholder),
  * no secret literals leak into any committed HCL (DEC-001).

Follows the repo's dual-mode shape-test convention (see
`test_dev_vm_module_shape.py`, `test_mise_config_shape.py`): module-level
`test_<name>() -> bool` functions that print `OK` / `FAIL: ...` (no `assert`),
plus `main() -> int` that sums the booleans and `sys.exit`s non-zero on any
failure. Stdlib only. The real gate is the standalone exit code.
"""

import pathlib
import re
import sys
import tomllib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOFU = REPO_ROOT / "tofu"
VERSIONS = TOFU / "versions.tf"
PROVIDERS = TOFU / "providers.tf"
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "host-bootstrap.md"
MISE_LOCAL_EXAMPLE = REPO_ROOT / "mise.local.toml.example"
JUSTFILE = REPO_ROOT / "justfile"
PREFLIGHT = REPO_ROOT / "scripts" / "preflight_tofu_auth.py"

# Secret-bearing env-var names whose *values* must never be literal in HCL.
SECRET_KEYS = (
    "PROXMOX_VE_API_TOKEN",
    "PROXMOX_VE_PASSWORD",
    "PROXMOX_TOKEN_SECRET",
    "CLOUDFLARE_DNS_API_TOKEN",
)


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def test_versions_floors_bpg_0108() -> bool:
    body = _read(VERSIONS)
    # bpg/proxmox source present and its version constraint floors at >= 0.108.0.
    has_source = re.search(r'source\s*=\s*"bpg/proxmox"', body) is not None
    has_floor = re.search(r'version\s*=\s*"[^"]*>=\s*0\.108\.0', body) is not None
    ok = has_source and has_floor
    print(
        f"{'OK' if ok else 'FAIL'}: tofu/versions.tf floors bpg/proxmox at "
        f">= 0.108.0 (source={has_source}, floor={has_floor})"
    )
    return ok


def test_providers_has_ssh_block() -> bool:
    body = _read(PROVIDERS)
    # An ssh block that actually carries `agent = true` (not an empty `ssh{}`
    # mentioned in a comment).
    block = re.search(r'ssh\s*\{[^{}]*?agent\s*=\s*true[^{}]*?\}', body, re.DOTALL)
    has_agent_block = block is not None
    # Username is sourced from the PROXMOX_VE_SSH_USERNAME env var (bpg reads it
    # natively); the provider config must reference that scheme.
    mentions_user = "PROXMOX_VE_SSH_USERNAME" in body
    ok = has_agent_block and mentions_user
    print(
        f"{'OK' if ok else 'FAIL'}: tofu/providers.tf has ssh{{}} block with "
        f"agent=true (block={has_agent_block}, "
        f"PROXMOX_VE_SSH_USERNAME={mentions_user})"
    )
    return ok


def test_auth_exercising_data_source() -> bool:
    # A harmless data source (anywhere in the root config) forces `tofu plan`
    # to authenticate without proposing resource changes.
    hcl = "\n".join(
        _read(p) for p in TOFU.glob("*.tf")
    )
    ok = re.search(r'data\s+"proxmox_(version|virtual_environment_\w+)"', hcl) is not None
    print(
        f"{'OK' if ok else 'FAIL'}: root config has an auth-exercising "
        f"proxmox_* data source"
    )
    return ok


def test_runbook_documents_prereqs() -> bool:
    body = _read(RUNBOOK)
    if not body:
        print(f"FAIL: docs/runbooks/host-bootstrap.md exists and is non-empty")
        return False
    checks = {
        "api token": re.search(r'ansible-token|API token', body, re.IGNORECASE)
        is not None,
        "provider SSH": re.search(r'\bssh\b', body, re.IGNORECASE) is not None
        and "PROXMOX_VE_SSH_USERNAME" in body,
        "GID verification": "getent group render video" in body
        and "993" in body
        and "44" in body,
        "port-forward": re.search(r'port[- ]forward', body, re.IGNORECASE)
        is not None
        and "80" in body
        and "443" in body,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: host-bootstrap.md covers token/SSH/GID/"
        f"port-forward (missing={missing})"
    )
    return ok


def test_root_pam_ticket_for_device_passthrough() -> bool:
    """Regression: the Plex CT 403 'configuring device passthrough is only
    allowed for root@pam'.

    Proxmox forbids configuring LXC device passthrough (dev[n] keys) through any
    API token, even a root@pam-owned one, and demands a real root@pam login
    ticket. bpg's auth modes are mutually exclusive and the API token takes
    PRECEDENCE: if `PROXMOX_VE_API_TOKEN` is set, bpg authenticates EVERY API call
    with the token and never builds the username/password ticket, so the
    passthrough create still 403s even when the ticket vars are also present
    (the prior "keep token + add user/pass" fix was insufficient).

    The fix is therefore to authenticate solely with the ticket: the `[env]` of
    the .example template must define `PROXMOX_VE_USERNAME = "root@pam"` plus a
    `PROXMOX_VE_PASSWORD` placeholder, and must NOT define `PROXMOX_VE_API_TOKEN`
    at all. providers.tf must explain the requirement so the token is not
    reintroduced.
    """
    example = _read(MISE_LOCAL_EXAMPLE)
    # Parse the [env] table so a comment that merely *names* PROXMOX_VE_API_TOKEN
    # (explaining why it is omitted) does not register as an assignment.
    try:
        env = tomllib.loads(example).get("env", {})
    except tomllib.TOMLDecodeError:
        env = {}
    # Username pinned to root@pam (the ticket only clears the gate as root@pam).
    user_root_pam = env.get("PROXMOX_VE_USERNAME") == "root@pam"
    # Password key documented with the CHANGEME placeholder (secret half).
    pass_placeholder = env.get("PROXMOX_VE_PASSWORD") == "CHANGEME"
    # The API token MUST be absent from the provider env — its mere presence would
    # take precedence over the ticket and reintroduce the 403.
    token_absent = "PROXMOX_VE_API_TOKEN" not in env
    # providers.tf records why the ticket is needed (env-native, no HCL literal).
    providers = _read(PROVIDERS)
    providers_doc = (
        "PROXMOX_VE_PASSWORD" in providers
        and re.search(r'device passthrough', providers, re.IGNORECASE) is not None
    )
    ok = user_root_pam and pass_placeholder and token_absent and providers_doc
    print(
        f"{'OK' if ok else 'FAIL'}: root@pam ticket is the sole API auth for "
        f"device passthrough (user=root@pam {user_root_pam}, password placeholder "
        f"{pass_placeholder}, api_token absent {token_absent}, "
        f"providers.tf documents it {providers_doc})"
    )
    return ok


def test_preflight_guards_api_token() -> bool:
    """Regression: the real (gitignored) env carrying PROXMOX_VE_API_TOKEN.

    The original 403 root cause was the token lingering in the user's gitignored
    `mise.local.toml` — invisible to the .example template guard
    (`test_root_pam_ticket_for_device_passthrough`, which can only see the
    committed template). `scripts/preflight_tofu_auth.py` closes that gap: it
    inspects the LIVE env and aborts `just apply` before bpg ever authenticates,
    so a stray token surfaces as an instant preflight error instead of a deep
    device-passthrough 403. This test exercises the guard's logic directly (the
    exact failing condition) and confirms the `apply` recipe runs it first.
    """
    if not PREFLIGHT.is_file():
        print("FAIL: scripts/preflight_tofu_auth.py exists")
        return False

    # Exercise the guard's decision function on both env shapes (the import path
    # works because the script's own directory is on sys.path[0] when run as
    # `python scripts/test_provider_auth_shape.py`).
    try:
        import preflight_tofu_auth as guard
    except ImportError as exc:
        print(f"FAIL: cannot import preflight_tofu_auth ({exc})")
        return False

    # The failing condition (token set) must be flagged…
    flags_token = bool(guard.check_env({"PROXMOX_VE_API_TOKEN": "root@pam!x=uuid"}))
    # …an empty token must be treated as absent (not a false positive)…
    empty_ok = guard.check_env({"PROXMOX_VE_API_TOKEN": ""}) is None
    # …and the ticket-only env (the fix) must pass clean.
    ticket_ok = (
        guard.check_env(
            {"PROXMOX_VE_USERNAME": "root@pam", "PROXMOX_VE_PASSWORD": "pw"}
        )
        is None
    )

    # The apply recipe must actually invoke the guard before `tofu apply`, else
    # it never runs. Match the preflight line preceding the apply line.
    just = JUSTFILE.read_text() if JUSTFILE.is_file() else ""
    wired = (
        re.search(
            r"preflight_tofu_auth\.py[^\n]*\n\s*tofu\s+apply",
            just,
            re.MULTILINE,
        )
        is not None
    )

    ok = flags_token and empty_ok and ticket_ok and wired
    print(
        f"{'OK' if ok else 'FAIL'}: preflight guards PROXMOX_VE_API_TOKEN in the "
        f"live env (flags_token={flags_token}, empty_ok={empty_ok}, "
        f"ticket_ok={ticket_ok}, wired_into_apply={wired})"
    )
    return ok


def test_no_secret_literals_in_hcl() -> bool:
    leaks = []
    for tf in TOFU.glob("*.tf"):
        body = tf.read_text()
        for key in SECRET_KEYS:
            # An assignment of a secret env-var name to a literal string value.
            if re.search(rf'{key}\s*=\s*"', body):
                leaks.append(f"{tf.name}:{key}")
    ok = not leaks
    print(f"{'OK' if ok else 'FAIL'}: no secret literals in committed HCL (leaks={leaks})")
    return ok


TESTS = (
    test_versions_floors_bpg_0108,
    test_providers_has_ssh_block,
    test_auth_exercising_data_source,
    test_runbook_documents_prereqs,
    test_root_pam_ticket_for_device_passthrough,
    test_preflight_guards_api_token,
    test_no_secret_literals_in_hcl,
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
