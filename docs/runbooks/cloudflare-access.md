# Runbook: Cloudflare Access, then publish the tunnel ingress (Step 5)

This runbook is the **manual, operator-run** half of Step 5 of the
traefik-cloudflare-letsencrypt work. The repo already ships the outbound
`cloudflared` connector (Step 4) with **zero inbound ports and no
public-hostname ingress** — nothing is reachable from the internet yet. This
step puts **Cloudflare Access (Google SSO + MFA)** in front of every dashboard
hostname **before** any tunnel ingress is published, so a dashboard is never
exposed unauthenticated even for a moment.

Everything here is configured in the **Cloudflare Zero Trust dashboard**, not in
this repo — a remotely-managed tunnel keeps the origin config on Cloudflare's
side (only the `TUNNEL_TOKEN` lives in the vault). There is **no template
change** for this step.

> **Still on Let's Encrypt _staging_.** The production cert flip is Step 7. The
> `noTLSVerify: true` ingress setting below is a **staging-only** allowance and
> is removed at the Step-7 prod flip.

---

## The one load-bearing rule: Access **before** ingress

**The ordering is load-bearing.** Publishing a tunnel public-hostname **before**
its Access application + policy exists makes that dashboard **momentarily
reachable unauthenticated** — a real exposure window. Always:

- **FIRST** — create the Access application + policy for a hostname.
- **THEN** — publish that hostname's tunnel ingress.

Confirm every Access app + policy exists **before** you publish the first
ingress. Never publish an ingress for a hostname that is not already gated.

The dashboard hostnames gated here (all `*.yoonnation.com`):

| Hostname | Service |
|---|---|
| `traefik.yoonnation.com` | Traefik dashboard (`api@internal`) |
| `grafana.yoonnation.com` | Grafana |
| `prometheus.yoonnation.com` | Prometheus |
| `uptime.yoonnation.com` | Uptime-Kuma |
| `homepage.yoonnation.com` | Homepage |
| `whoami.yoonnation.com` | whoami smoke route |

**Plex is excluded.** `plex.yoonnation.com` stays public via the existing
`:443` **port-forward** with its own auth and is served the LE cert directly by
Traefik — it is **not** routed through the Cloudflare tunnel/Access/proxy
(Cloudflare's ToS bars media through the proxy). Leave its DNS record a **grey**
(DNS-only) `A` record to the home IP.

---

## Step A (FIRST) — identity + one Access app per hostname

### A.1 Identity providers (once)

In **Zero Trust → Settings → Authentication**:

1. Add **Google** as a login method (identity provider).
2. Add **One-time PIN** (OTP) as a fallback login method.
3. Turn **MFA** on so every login is multi-factor.

### A.2 One **self-hosted** Access application **per dashboard hostname**

In **Zero Trust → Access → Applications**, create a **self-hosted** application
for **each** hostname in the table above — **one application per hostname**.

> **Do NOT create a single `*.yoonnation.com` wildcard Access application.** A
> wildcard app is fragile with respect to Plex — `plex.yoonnation.com` must stay
> ungated and public, and a wildcard would try to gate it too. Use **per-host,
> self-hosted** applications so Plex is never caught by an Access policy.

For each application:

- **Application domain** = the exact dashboard hostname (e.g.
  `grafana.yoonnation.com`), on the `yoonnation.com` zone.
- **Identity providers** = Google + One-time PIN, **MFA required**.
- **Policy** — a single **Allow** policy:
  - Action: **Allow**
  - Include: **Emails** → `emmanuelx08@gmail.com` (this one account only).
  - Everyone else falls through to the **implicit deny** — no other identity
    gets in.

Repeat for all six dashboard hostnames. Do **not** touch `plex.yoonnation.com`.

---

## Step B (THEN) — publish the per-host tunnel ingress

Only after every Access app + policy from Step A exists, add the tunnel
public-hostname ingress. In **Zero Trust → Networks → Tunnels →** *(your
remotely-managed tunnel)* **→ Public Hostnames**, add **one entry per dashboard
hostname**:

- **Subdomain / Domain** = the dashboard hostname (e.g. `grafana` on
  `yoonnation.com`).
- **Service** = **`https://traefik:443`** — `cloudflared` reaches Traefik over
  the internal compose network; its source is in `172.16.0.0/12`, already
  admitted by the `internal-allowlist` middleware.
- **Additional application settings → TLS:**
  - **`originRequest.originServerName`** = the **same hostname** (e.g.
    `grafana.yoonnation.com`). This sets the SNI so Traefik presents the LE
    wildcard cert for the right host — without it `cloudflared → Traefik` throws
    a TLS mismatch.
  - **`noTLSVerify: true`** — **staging only.** While on the LE **staging**
    directory the origin cert is not browser-trusted, so `cloudflared` must skip
    verification. **Remove `noTLSVerify` at the Step-7 production flip** once the
    origin serves a browser-trusted prod cert.

Each dashboard's public DNS record becomes an **orange (proxied) CNAME** to
`<tunnel-id>.cfargotunnel.com` (Cloudflare creates it when you save the public
hostname).

---

## Verification (human-confirmed)

From any browser, off the LAN:

1. Visit a gated dashboard (e.g. `https://grafana.yoonnation.com`) →
   redirected to the **Cloudflare login** page (SSO + MFA prompt).
2. Sign in as `emmanuelx08@gmail.com` → the dashboard **loads through the
   tunnel**.
3. Sign in as a **different** Google identity → **denied** (implicit deny).
4. Confirm **no dashboard was ever reachable unauthenticated** — because every
   ingress was published only after its Access policy existed (Step A before
   Step B).
5. `plex.yoonnation.com` is **unaffected** — still public, no SSO prompt.

---

## Next

- **Step 6** — Tailscale split-DNS so tailnet devices reach the same dashboards
  directly at `192.168.1.111:443` (the direct dual-path), bypassing the tunnel.
- **Step 7** — flip to production Let's Encrypt (stop Traefik → truncate
  `acme.json` → start) and **remove `noTLSVerify`** from every tunnel ingress.
