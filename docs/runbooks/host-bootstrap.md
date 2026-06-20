# Runbook: Proxmox host bootstrap (bare `pve` → "Tofu can talk to Proxmox")

This runbook covers the **manual** host prerequisites that OpenTofu cannot
provision for itself: the root@pam login ticket it authenticates with, the SSH
access bpg needs for idmap/bind-mount operations, a host-GID sanity check, and
the router port-forward placeholder. Work through it once on a fresh Proxmox VE
host (`pve`) before running `mise run plan`.

All credentials are consumed from the environment exported by **mise**
(non-secret config in committed `mise.toml`; secrets in gitignored
`mise.local.toml` — see `mise.local.toml.example` and DEC-001). Nothing in this
runbook is hardcoded into the OpenTofu HCL.

---

## 1. Provide the `root@pam` login ticket (username + password)

OpenTofu authenticates with the `root@pam` **login ticket** (username +
password), **not** an API token. The Plex CT configures LXC device passthrough
(`dev[n]` keys), which Proxmox refuses through *any* API token — even a
`root@pam`-owned one (`HTTP 403 … device passthrough is only allowed for
root@pam`). A real `root@pam` login ticket is the only credential that clears
that gate.

> **Do not set `PROXMOX_VE_API_TOKEN` for the Tofu provider.** bpg's auth modes
> are mutually exclusive and the API token takes **precedence**: if the token env
> var is set, bpg authenticates every API call with it and never builds the
> ticket, so the passthrough create 403s even when the username/password are also
> present. (The separate Packer build keeps its own `PROXMOX_TOKEN_*` token —
> that is unrelated to this provider, see DEC-001.)

No Proxmox-side setup is needed beyond knowing the `root@pam` account password.
Put the ticket credentials in your gitignored `mise.local.toml`:

```toml
[env]
PROXMOX_VE_USERNAME = "root@pam"
PROXMOX_VE_PASSWORD = "<the root@pam account password>"
```

> The matching non-secret `PROXMOX_VE_ENDPOINT` (e.g.
> `https://pve.home.arpa:8006/`) and `PROXMOX_VE_INSECURE=true` already live in
> the committed `mise.toml`.

## 2. Enable provider SSH access

The bpg provider performs some operations over SSH (idmap on container create,
`root@pam`-level bind mounts). The provider's `ssh {}` block uses `agent = true`
and reads the **username** natively from the `PROXMOX_VE_SSH_USERNAME`
environment variable.

1. Choose the SSH user bpg will connect as (typically `root`) and record it in
   `mise.local.toml`:

   ```toml
   [env]
   PROXMOX_VE_SSH_USERNAME = "root"
   ```

2. Ensure your SSH key is loaded into an agent on the workstation running
   OpenTofu, and that the public key is authorized on `pve`:

   ```bash
   ssh-add -l                              # key present in the agent?
   ssh-copy-id root@pve.home.arpa          # authorize it on the host (once)
   ssh root@pve.home.arpa true             # smoke test — must succeed non-interactively
   ```

   bpg authenticates via the agent, so no private key material is ever placed in
   the repo or in HCL.

## 3. Verify host GIDs (`render` / `video`)

The iGPU device nodes (`/dev/dri/renderD128`, `/dev/dri/card1`) are owned by the
host `render` and `video` groups. Later steps pass these GIDs straight through to
the Plex container via idmap, so they **must** match the values committed in
`tofu/locals.tf`, which defines `host_gids = { render = 993, video = 44 }`. The
idmap *tiling* that consumes that map to punch the GIDs 1:1 into the unprivileged
Plex CT is the Step 7 artifact.

Run on `pve` and confirm the GIDs before any apply:

```bash
getent group render video
```

Expected output (the trailing number is the GID):

```
render:x:993:
video:x:44:
```

> Generic guides often cite `104` for `render` — that is **wrong** for this
> host. If your output differs from **render=993 / video=44**, stop and reconcile
> the values (and re-check the design) before continuing — the Step 7 idmap map
> must carry your host's real GIDs; a mismatch will make `vainfo` fail inside the
> Plex CT.

## 4. Router port-forward (placeholder)

Public ingress (Traefik on the Docker-host LXC) requires the home router to
forward inbound web traffic to the LXC. This is a **manual router change**, filled
in once the Docker-host CT exists (Step 3+):

| Protocol | External port | Internal target  | Notes                                  |
| -------- | ------------- | ---------------- | -------------------------------------- |
| TCP      | 80            | `192.168.1.111`  | ACME HTTP-01 challenge + HTTP→HTTPS     |
| TCP      | 443           | `192.168.1.111`  | HTTPS (Traefik); `plex.yoonnation.com` |

> Leave this as a placeholder for now. It is required before ACME can issue a
> certificate (design §6: verify port-forward 80→`.111` + DNS A record; switch
> to DNS-01 when Cloudflare is ready).

---

## 5. Verify connectivity

With `mise.local.toml` populated and the steps above done:

```bash
mise run plan
```

OpenTofu authenticates to `pve` (token + SSH), resolves the
`proxmox_version` data source (the connectivity probe in
`tofu/auth_check.tf`), and reports **no resource changes**. A clean plan that
shows the PVE version output means "Tofu can talk to Proxmox" — bootstrap is
complete.
