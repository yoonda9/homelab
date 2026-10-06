# Summary — Traefik + Cloudflare (DNS-01 + Tunnel/Access) + Let's Encrypt

## Artifacts created

```
.agents/planning/2026-07-14-traefik-cloudflare-letsencrypt/
├── rough-idea.md                     # original idea + grounding on the existing setup
├── idea-honing.md                    # 10-question requirements Q&A + consolidated requirements
├── research/
│   ├── proxied-vs-dns-only.md         # why not proxied; SSL modes; token scoping (cited)
│   └── tunnel-vs-tailscale.md         # Tunnel+Access vs Tailscale; dual-path (cited)
├── design/
│   └── detailed-design.md             # full standalone design (R1–R12, diagrams, error handling, tests)
├── implementation/
│   └── plan.md                        # 8 incremental, staging-first, demoable steps + checklist
└── summary.md                         # this document
```

## Design overview

A **DNS-first hybrid**: Cloudflare is used as DNS + DNS-01 ACME provider and as a
**Tunnel + Access** front door — never as an in-path reverse proxy for origin data.

- **Certs:** one Let's Encrypt **wildcard** (`yoonnation.com` + `*.yoonnation.com`) via
  **DNS-01** (`le-dns-cf`), auto-renewing. `le-http` removed. **Staging→prod** via an
  `acme_ca_server` toggle.
- **Dashboards** (Grafana, Prometheus, Uptime-Kuma, Homepage, whoami, + the Traefik
  dashboard as `traefik.yoonnation.com`): exposed via **cloudflared Tunnel + Cloudflare
  Access** (Google SSO + email-OTP, MFA, single-user allow) **and** directly over
  **Tailscale** (split-DNS → `192.168.1.111`) — dual-path.
- **Plex:** public and **direct** via the 80/443 port-forward with the LE cert and its
  own auth; never tunneled/proxied (Cloudflare media ToS).
- **Hardening:** the uncommitted insecure dashboard port (`:8080`) is dropped; secrets
  (`CF_DNS_API_TOKEN`, `TUNNEL_TOKEN`) stay in vault → `.env` (0600).

## Implementation approach

8 steps, sequenced so core TLS works first and each step is independently demoable:
cert issuance on staging → middleware/subnet prep → dashboard hardening → tunnel →
Access → split-DNS dual-path → prod-LE flip → acceptance/docs. Staging-first protects
against LE rate-limit lockout.

## Suggested next steps

1. Review `design/detailed-design.md` and `implementation/plan.md`.
2. Gather the manual Cloudflare prerequisites: scoped DNS token
   (`Zone:DNS:Edit` + `Zone:Zone:Read`), a remotely-managed tunnel token, and confirm
   the Google account for Access. Put both tokens in `group_vars/vault.yml`.
3. Execute Step 1 against **LE staging** first; only flip to prod (Step 7) once the
   whole chain is green.

## Design/plan review (applied)

A thorough review was run against the actual repo templates/handlers; findings were
folded into `design/detailed-design.md` and `implementation/plan.md`:

- **acme.json lifecycle (was silent-fail):** the staging→prod flip now explicitly
  stops Traefik, truncates/recreates `acme.json`, and starts — a `caServer` change +
  restart alone would keep serving the untrusted staging cert.
- **No network-subnet pinning:** `internal-allowlist` now admits `172.16.0.0/12`
  (+ Tailscale IPv6 `fd7a:115c:a1e0::/48`) instead of pinning the compose subnet, which
  would have forced a network recreation the role can't perform.
- **Wildcard issuance anchored:** the wildcard `tls.domains` moves to the stable
  `traefik-dashboard` file-provider router (off the docker `whoami` router), closing the
  per-host prod-cert race.
- **Access-before-ingress:** Access apps/policy are created before publishing tunnel
  hostnames, so auth-less dashboards are never briefly open; per-host Access apps chosen
  over a fragile wildcard app.
- **Monitoring re-pointed** to internal URLs (Access 302s would otherwise fake status),
  and a WAN `:443` direct-hit **403** check was added to acceptance.

## Areas still worth a human decision (not blocking)

- **On-LAN SSO bypass:** dual-path trusts the LAN/tailnet by design; add Cloudflare
  Access-JWT verification at Traefik later if you want SSO everywhere.
- **Scoped DNS token:** verify the scoped token actually issues certs on first run.
  (`cloudflared:2026.7.1` is verified present on Docker Hub and pinned.)
