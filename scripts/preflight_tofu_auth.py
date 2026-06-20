#!/usr/bin/env python3
"""Preflight auth guard for `just apply` / `just provision`.

Fails fast — BEFORE OpenTofu ever calls the Proxmox API — when the live
environment carries a `PROXMOX_VE_API_TOKEN`. Such a token would otherwise
cause the Plex CT create to 403 with
``configuring device passthrough is only allowed for root@pam``.

Why: bpg's auth modes are mutually exclusive and the API token takes
PRECEDENCE (``proxmox/api/credentials.go`` early-returns; ``client.go``
``NewClient`` checks ``TokenCredentials`` first). If ``PROXMOX_VE_API_TOKEN``
is set, bpg authenticates EVERY call with the token and never builds the
``root@pam`` username/password ticket — and Proxmox refuses to configure LXC
``dev[n]`` device passthrough through any API token, even a root@pam-owned one.
So the only auth that clears the gate is the username/password ticket
(``PROXMOX_VE_USERNAME=root@pam`` + ``PROXMOX_VE_PASSWORD``), which demands the
token be absent.

The root cause of the original failure was the token lingering in the user's
gitignored ``mise.local.toml``; this guard makes that reintroduction a loud,
instant preflight error instead of a deep 403 mid-apply.

Stdlib only. ``check_env(env)`` returns an error string (or ``None`` when the
env is clean) so it is unit-testable; ``main()`` reads ``os.environ`` and exits
non-zero with guidance when the token is present.
"""

import os
import sys

TOKEN_VAR = "PROXMOX_VE_API_TOKEN"


def check_env(env: dict) -> str | None:
    """Return an error message if the tofu auth env is unsafe, else None.

    Unsafe == ``PROXMOX_VE_API_TOKEN`` set to a non-empty value: it shadows the
    ``root@pam`` ticket and 403s the device-passthrough create.
    """
    if env.get(TOKEN_VAR, "").strip():
        return (
            f"{TOKEN_VAR} is set in the OpenTofu environment.\n"
            f"  bpg gives the API token PRECEDENCE over the root@pam "
            f"username/password ticket, so it authenticates every call with the "
            f"token and never builds the ticket. Proxmox then 403s the Plex CT "
            f"device-passthrough create ('only allowed for root@pam').\n"
            f"  Fix: comment out / remove {TOKEN_VAR} from mise.local.toml and "
            f"keep only PROXMOX_VE_USERNAME=root@pam + PROXMOX_VE_PASSWORD."
        )
    return None


def main() -> int:
    err = check_env(dict(os.environ))
    if err:
        print(f"preflight-tofu-auth: FAIL\n  {err}", file=sys.stderr)
        return 1
    print("preflight-tofu-auth: OK (no PROXMOX_VE_API_TOKEN; root@pam ticket auth)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
