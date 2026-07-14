# Runbook: Tailscale split-DNS for the direct dual-path (Step 6)

This runbook is the **manual, operator-run** half of Step 6 of the
traefik-cloudflare-letsencrypt work. Step 5 published the dashboards through the
**Cloudflare tunnel + Access** (the remote path). This step adds the **second,
direct path**: a Tailscale **split-DNS** override so the *same* dashboard
hostnames resolve straight to the origin (`192.168.1.111`) for **tailnet
devices**, bypassing Cloudflare entirely.

Everything here is configured in the **Tailscale admin console**, not in this
repo — split-horizon DNS is a per-tailnet setting (manual DNS, per R12). There is
**no template change** for this step; the origin already admits the tailnet
because the `internal-allowlist` middleware
(`ansible/roles/docker_host/templates/dynamic.yml.j2`) allows
`192.168.1.0/24` + Tailscale v4 `100.64.0.0/10` + Tailscale IPv6
`fd7a:115c:a1e0::/48`.

> **Still on Let's Encrypt _staging_.** The production cert flip is Step 7. Until
> then the origin serves the LE **staging** wildcard; a tailnet browser will show
> a staging-CA warning on the direct path (expected) until Step 7.

---

## The dual-path, in one picture

The dashboard hostnames (`*.yoonnation.com`) now resolve **two different ways**
depending on where the client sits:

| Client | Resolves to | Path to the origin |
|---|---|---|
| **On-tailnet** (Tailscale up) | `192.168.1.111` (this override) | **Direct** to Traefik `:443`, admitted by `internal-allowlist` — no Cloudflare |
| **Off-tailnet** (any other network) | the orange tunnel CNAME (`<id>.cfargotunnel.com`) | Through the **Cloudflare tunnel + Access** (SSO + MFA), as published in Step 5 |

Both paths terminate at the **same Traefik**, which presents the **same LE
wildcard cert** (`*.yoonnation.com`) on either route — the direct path via SNI to
Traefik's global cert store, the tunnel path via the ingress
`originRequest.originServerName`. Same URL, same cert, two paths: on Tailscale it
hits the origin directly and fast; off Tailscale it goes through Access.

The dashboard hostnames covered by the override (all on `yoonnation.com`):
`traefik`, `grafana`, `prometheus`, `uptime`, `homepage`, `whoami`.

---

## ⏸ OPERATOR PAUSE — add the split-DNS override, then confirm

**This is a manual Tailscale-console step. Nothing in this repo performs it.**

In the **Tailscale admin console → DNS**:

1. Under **Nameservers**, add a **restricted nameserver** (a **split-DNS** /
   MagicDNS search-domain override) scoped to **`yoonnation.com`**.
2. Point that restricted nameserver at a resolver that answers
   `*.yoonnation.com` → **`192.168.1.111`** for tailnet devices. Either:
   - run a small internal resolver on the LAN that returns `192.168.1.111` for
     the dashboard hosts, and list it as the `yoonnation.com` restricted
     nameserver; **or**
   - if you only need the specific dashboard hosts, add per-host **MagicDNS**
     overrides mapping each of `traefik`/`grafana`/`prometheus`/`uptime`/
     `homepage`/`whoami`.`yoonnation.com` → `192.168.1.111`.
3. Leave **`plex.yoonnation.com` out of the override** (see the Plex note below).

The origin at `192.168.1.111` answers on **both IPv4 and any Tailscale IPv6**
address — the `internal-allowlist` middleware already admits the Tailscale IPv6
range `fd7a:115c:a1e0::/48` alongside the v4 CGNAT range, so a tailnet client
reaching the box over **v4 or v6** is let through the direct path identically.

**Pause here for human confirmation before relying on the direct path.**

---

## Plex stays on its own path (do NOT override it)

**`plex.yoonnation.com` must NOT be captured by this split-DNS override.** Plex
is **not** routed through Cloudflare (media ToS) and is **not** part of the
dashboard dual-path — it stays public via the existing `:443` **port-forward**
and keeps its **grey** (DNS-only) home-IP **`A` record** for non-tailnet clients.

If the override is scoped to the specific dashboard hosts, Plex is untouched by
construction. If you instead point a restricted nameserver at the whole
`yoonnation.com` zone, make sure that resolver **returns the grey home-IP `A`
record for `plex`** (not `192.168.1.111`) so **off-tailnet Plex resolution is
unaffected** and on-tailnet Plex still reaches it directly. Either way the rule
is the same: the split-DNS override **must not break** Plex resolution.

---

## Verification (human-confirmed)

**On a tailnet device (Tailscale up):**

1. `dig grafana.yoonnation.com` → returns **`192.168.1.111`** (the override), on
   both **IPv4** and any **IPv6** address.
2. `https://grafana.yoonnation.com` **loads directly** — straight to Traefik via
   `internal-allowlist`, **no** Cloudflare Access prompt (staging-CA warning
   until Step 7).
3. `plex.yoonnation.com` still resolves/loads (its own path, unaffected).

**Off-tailnet (Tailscale down / any other network):**

4. `dig grafana.yoonnation.com` → returns the **tunnel CNAME**; the name goes
   **through the tunnel + Access** (SSO + MFA), exactly as in Step 5.
5. Both paths present the **same** LE **wildcard** cert.
6. `plex.yoonnation.com` still resolves to the **grey home-IP `A` record** and
   works — **off-tailnet Plex resolution is unaffected**.

---

## Next

- **Step 7** — flip to production Let's Encrypt (stop Traefik → truncate
  `acme.json` → start) and **remove `noTLSVerify`** from every tunnel ingress;
  the direct-path staging-CA warning disappears once the origin serves a
  browser-trusted prod wildcard.
