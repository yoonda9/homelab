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

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOFU = REPO_ROOT / "tofu"
VERSIONS = TOFU / "versions.tf"
PROVIDERS = TOFU / "providers.tf"
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "host-bootstrap.md"

# Secret-bearing env-var names whose *values* must never be literal in HCL.
SECRET_KEYS = (
    "PROXMOX_VE_API_TOKEN",
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
