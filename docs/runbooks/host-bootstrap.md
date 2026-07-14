# Runbook: Proxmox host bootstrap (bare `pve` → "Tofu can talk to Proxmox")

This runbook covers the **manual** host prerequisites that OpenTofu cannot
provision for itself: the root@pam login ticket it authenticates with, the SSH
access bpg needs for idmap/bind-mount operations, a host-GID sanity check, and
the router port-forward placeholder. Work through it once on a fresh Proxmox VE
host (`pve`) before running `just plan`.

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

## 4. Delegate the Plex CT punch GIDs in `/etc/subgid`

The unprivileged Plex CT's idmap (Step 7) punches the host GIDs **993**
(`render`) and **44** (`video`) **1:1** into the container so it can open
`/dev/dri` and read `/media` while staying unprivileged. The provider applies
that map with `newgidmap`, which will only write a sub-GID range that is
**delegated to `root`** in `/etc/subgid`. Proxmox's default allocation is
`root:100000:65536` — that covers the idmap's `+100000` *offset* tiles, but
**not** the two size-1 *punch* tiles at GID 44 and 993, which fall outside it.
Without the delegations the container **fails to start** with:

```
lxc_map_ids: newgidmap failed: "newgidmap: gid range [44-45) -> [44-45) not allowed"
TASK ERROR: startup for container '110' failed
```

`getent group render video` (section 3) is clean, `just plan`/`apply` is clean —
this surfaces only at first **CT start**, so set it up here, before any apply.

Append one delegation **per punch GID** to `/etc/subgid` on `pve` (each punch
needs its own line — a blanket range will not do):

```bash
# on pve, as root — idempotent (grep-guard avoids duplicate lines)
grep -qxF 'root:44:1'  /etc/subgid || echo 'root:44:1'  >> /etc/subgid   # video
grep -qxF 'root:993:1' /etc/subgid || echo 'root:993:1' >> /etc/subgid   # render
```

> **`/etc/subuid` needs nothing.** The Plex CT's **uid** map is a single offset
> tile (`0 → 100000`, size 65536) that lies entirely inside `root`'s default
> `root:100000:65536` subuid allocation — there are no uid punches, so no extra
> uid delegation is required. Only the **gid** side needs the two lines above.

If you change the host GIDs (so `tofu/locals.tf`'s `host_gids` change), update
these `/etc/subgid` lines to match the new punch GIDs.

## 5. Router port-forward (placeholder)

Public ingress (Traefik on the Docker-host LXC) requires the home router to
forward inbound web traffic to the LXC. This is a **manual router change**, filled
in once the Docker-host CT exists (Step 3+):

| Protocol | External port | Internal target  | Notes                                  |
| -------- | ------------- | ---------------- | -------------------------------------- |
| TCP      | 80            | `192.168.1.111`  | HTTP→HTTPS redirect only               |
| TCP      | 443           | `192.168.1.111`  | HTTPS (Traefik); `plex.yoonnation.com` |

> Certificates are issued over **DNS-01** (Cloudflare), so **no inbound `:80` is
> needed for ACME** — port 80 is forwarded only for the HTTP→HTTPS redirect. Port
> `443` is required so `plex.yoonnation.com` (grey/DNS-only home-IP `A` record)
> reaches Traefik directly; the internal dashboards do **not** rely on this
> forward from WAN — they go through the Cloudflare tunnel (§7).

---

## 6. Verify connectivity

With `mise.local.toml` populated and the steps above done:

```bash
just plan
```

OpenTofu authenticates to `pve` (token + SSH), resolves the
`proxmox_version` data source (the connectivity probe in
`tofu/auth_check.tf`), and reports **no resource changes**. A clean plan that
shows the PVE version output means "Tofu can talk to Proxmox" — bootstrap is
complete.

---

## 7. Manual Cloudflare + Tailscale setup (traefik-cloudflare-letsencrypt)

Public access for the dashboards is an **outbound Cloudflare tunnel + Cloudflare
Access**, and the tailnet direct path is a **Tailscale split-DNS** override.
Neither is provisioned by this repo — both are **manual, operator-run** steps
configured in the Cloudflare Zero Trust and Tailscale admin consoles. The repo
only ships the `cloudflared` connector and consumes two vault-stored tokens.

Do these **once**, in order. Full step-by-step procedures live in the dedicated
runbooks; this section is the bootstrap checklist and the pointer to them.

### 7.1 Scoped Cloudflare **DNS** token (for DNS-01 wildcard issuance)

Traefik issues the `*.yoonnation.com` wildcard over **DNS-01**. Create a scoped
API token with **`Zone:DNS:Edit` + `Zone:Zone:Read`** on the `yoonnation.com`
zone and store it in the vault as **`vault_cloudflare_dns_api_token`** (rendered
into the compose `.env` as `CF_DNS_API_TOKEN`). Never commit the raw token.

### 7.2 Cloudflare **tunnel** token

Create a **remotely-managed** tunnel in **Zero Trust → Networks → Tunnels** and
store its connector token in the vault as **`vault_cloudflare_tunnel_token`**
(rendered into `.env` as `TUNNEL_TOKEN`). The `cloudflared` service runs it
outbound — **no inbound ports**.

### 7.3 Access apps **before** ingress, then per-host ingress

**Ordering is load-bearing** — create the Access app first, publish the ingress
second, or the dashboard is briefly reachable unauthenticated:

- **FIRST** — one **self-hosted Access application per dashboard hostname**
  (Google SSO + One-time-PIN fallback, MFA on, a single Allow policy for
  `emmanuelx08@gmail.com`). **Not** a `*.yoonnation.com` wildcard app (it would
  wrongly catch Plex).
- **THEN** — one tunnel **public-hostname ingress** per dashboard →
  `https://traefik:443` with `originRequest.originServerName` = the hostname.
  (`noTLSVerify: true` **only** while on LE staging; removed at the Step-7 prod
  flip.)

Full procedure: **`cloudflare-access.md`**.

### 7.4 Grey (DNS-only) `plex` A-record

Leave **`plex.yoonnation.com`** as a **grey (DNS-only) `A` record** to the home
IP. Plex is **not** routed through the tunnel/Access (Cloudflare ToS bars media
through the proxy) — it stays public via the `:443` port-forward (§5) with its own
auth.

### 7.5 Tailscale split-DNS entry (the direct dual-path)

In the **Tailscale admin console → DNS**, add a **split-DNS** override scoped to
`yoonnation.com` that resolves the dashboard hosts →
**`192.168.1.111`** for tailnet devices (over IPv4 **and** IPv6), so on-tailnet
clients reach the origin directly, bypassing Cloudflare. **Do not** override
`plex.yoonnation.com` (keep its grey home-IP `A` record).

Full procedure: **`tailscale-split-dns.md`**.

### 7.6 Production flip and final acceptance

Once the tunnel + Access + split-DNS are verified on LE **staging**, flip to LE
**production** (stop Traefik → truncate `acme.json` → start, and **remove
`noTLSVerify`** from every ingress), then run **`acceptance-validation.md`**
top-to-bottom for sign-off.
