# Implementation Plan — Traefik + Cloudflare (DNS-01 + Tunnel/Access) + LE

Incremental, staging-first steps. Each yields a working, demoable increment and
builds on the previous. "Tests" here are concrete infra verifications (render/lint in
check mode, Traefik logs, `curl`/`openssl s_client`, Cloudflare dashboard state) since
this is Ansible-driven infra, not unit-tested code. Context docs
(`design/detailed-design.md`, `research/*`, `idea-honing.md`) are assumed available.

## Progress checklist

- [ ] **Step 1** — ACME staging toggle + remove `le-http`; verify DNS-01 wildcard issuance (staging)
- [ ] **Step 2** — `internal-allowlist` middleware (broad Docker range + Tailscale v4/v6); migrate dashboard routers; verify direct access unchanged
- [ ] **Step 3** — Harden Traefik dashboard: drop `api.insecure`/`:8080`, add `traefik.yoonnation.com` router + relocate wildcard `tls.domains` to it
- [ ] **Step 4** — Add `cloudflared` + `TUNNEL_TOKEN`; create tunnel (connector Healthy) — **no public hostnames yet**
- [ ] **Step 5** — Cloudflare Access apps + Google/OTP IdP + policy **first, then** publish ingress hostnames; verify allow/deny (never exposed unauth)
- [ ] **Step 6** — Tailscale split-DNS for dual-path (v4/v6); verify internal vs external resolution
- [ ] **Step 7** — Flip to production LE (**stop → truncate `acme.json` → start**, remove staging `noTLSVerify`); verify browser-trusted certs
- [ ] **Step 8** — Re-point monitors to internal URLs; extend acceptance/runbook docs; purge stale `le-http`/inventory refs; final acceptance run

---

## Step 1: ACME staging toggle and single DNS-01 resolver
**Objective:** Make LE issuance safe to iterate and prove the wildcard issues via
DNS-01 before anything else, using LE **staging** to avoid prod rate limits.

**Guidance:** In `group_vars/all.yml` add `acme_ca_server` (default = LE prod
directory URL; set to the LE **staging** URL for this phase). In
`templates/traefik.yml.j2` add `caServer: "{{ acme_ca_server }}"` under
`le-dns-cf.acme`, and **remove** the `le-http` resolver block (and, from the working
tree, `api.insecure`). Leave `acme_resolver: le-dns-cf`. Ensure the scoped
`vault_cloudflare_dns_api_token` (`Zone:DNS:Edit` + `Zone:Zone:Read`) is present. The
wildcard `tls.domains` block stays on the existing `whoami` router **for this step
only** (it is relocated to the stable `traefik-dashboard` router in Step 3, so
proactive issuance no longer depends on the docker `whoami` service).

**Tests:** `ansible-playbook --check --diff` renders cleanly; `docker compose config`
on the host validates; after apply, Traefik logs show a successful DNS-01 challenge
and `acme.json` contains a `yoonnation.com` + `*.yoonnation.com` cert from LE
**staging** (`openssl s_client -connect ...:443 -servername grafana.yoonnation.com`
shows the staging issuer). No `le-http` remains in the rendered config.

**Integration:** Foundation for every later step — all routers already reference
`{{ acme_resolver }}`, so they immediately use the freshly-issued wildcard.

**Demo:** From the host/LAN, hitting any existing dashboard host serves the wildcard
(staging, untrusted-but-valid chain); `acme.json` shows one wildcard cert; issuance is
repeatable without touching prod rate limits.

---

## Step 2: Introduce `internal-allowlist` (no subnet pinning)
**Objective:** Prepare the middleware model for the tunnel without regressing direct
access and **without** a disruptive network recreation.

**Guidance:** In `templates/dynamic.yml.j2` add an `internal-allowlist` middleware =
`192.168.1.0/24` + `100.64.0.0/10` + `fd7a:115c:a1e0::/48` (Tailscale IPv6) +
`172.16.0.0/12` (broad Docker private range, so any Docker-assigned subnet — hence the
future `cloudflared` — is admitted **without pinning** the network). Do **not** add a
`networks:` block or change IPAM: the default network already exists on the host and
changing its subnet would force a `down`/recreate the role's flow can't perform.
Switch the dashboard routers (grafana, prometheus, uptime-kuma, homepage, whoami) from
`lan-allowlist@file` to `internal-allowlist@file` (keep `security-headers@file`). Leave
Plex on `security-headers` only.

**Tests:** Render/lint clean; apply is a clean `up -d` (no network recreation error);
direct Tailscale/LAN access to each dashboard still loads with the wildcard over IPv4
**and** IPv6 (no regression); a request from outside the allow-listed ranges is
refused; Plex unaffected.

**Integration:** `internal-allowlist` already admits the Docker range the `cloudflared`
hop (Step 4) will use — no rework, no re-IP.

**Demo:** All dashboards reachable over Tailscale/LAN (v4+v6) exactly as before, now via
`internal-allowlist`, which already covers the tunnel's Docker source range.

---

## Step 3: Harden the Traefik dashboard
**Objective:** Remove the unauthenticated dashboard port and serve the dashboard as a
first-class routed service.

**Guidance:** In `templates/compose.yml.j2` remove the `:8080` publish; in
`defaults/main.yml` remove `docker_host_traefik_dashboard_port`. In
`templates/dynamic.yml.j2` add router `traefik-dashboard`:
`Host(\`traefik.{{ domain }}\`)`, `websecure`, `tls.certResolver={{ acme_resolver }}`,
service `api@internal`, middlewares `internal-allowlist@file` + `security-headers@file`.
**Relocate the wildcard `tls.domains`** (`main={{ domain }}`, `sans=*.{{ domain }}`,
gated on `acme_resolver == 'le-dns-cf'`) onto this router and **remove it from the
`whoami` router** — proactive wildcard issuance now rides a stable file-provider router,
independent of the docker `whoami` service, closing the per-host-cert race. Confirm
`api.dashboard: true` and `api.insecure` absent in `traefik.yml.j2`.

**Tests:** Render/lint clean; `:8080` no longer published (`docker compose ps` /
`ss`); `acme.json` still holds exactly one `*.yoonnation.com` wildcard (no new per-host
certs appeared); `traefik.yoonnation.com` loads the dashboard over Tailscale/LAN with
the wildcard; direct `http://<host>:8080` fails.

**Integration:** Reuses the Step-2 `internal-allowlist`; the dashboard becomes another
dual-path service ready for the tunnel, and now *anchors* wildcard issuance for every
host.

**Demo:** Traefik dashboard at `https://traefik.yoonnation.com` (LAN/Tailscale) with a
valid cert; no insecure port anywhere.

---

## Step 4: Add cloudflared and create the tunnel (no public hostnames yet)
**Objective:** Stand up the outbound tunnel connector **without exposing anything** —
so the auth-less dashboards are never briefly open to the internet.

**Guidance:** Create a remotely-managed tunnel in the Cloudflare Zero Trust dashboard;
store its token as `vault_cloudflare_tunnel_token`. Add
`TUNNEL_TOKEN={{ vault_cloudflare_tunnel_token | default('') }}` to `templates/env.j2`.
Set `docker_host_cloudflared_image: cloudflare/cloudflared:2026.7.1` (verified on
Docker Hub — current `latest`, multi-arch) in `defaults/main.yml` and add a
`cloudflared` service
(token, `tunnel --no-autoupdate run`, no ports, `depends_on: traefik`) to
`templates/compose.yml.j2`. **Do not add any public-hostname ingress yet.**

**Tests:** `cloudflared` container healthy; tunnel connector shows **Healthy** in the
dashboard; **no** public hostname resolves yet (nothing exposed). `.env` is mode 0600
and the token is not committed.

**Integration:** cloudflared's source is in the `172.16.0.0/12` range already admitted
by Step-2 `internal-allowlist`; Traefik keeps host-routing + serving the wildcard.

**Demo:** A healthy tunnel connector with zero inbound ports and nothing yet reachable
from the internet.

---

## Step 5: Cloudflare Access, then publish ingress
**Objective:** Gate identity **before** the dashboards are ever publicly reachable.

**Guidance:** **First**, in Zero Trust → Access, add a Google IdP (+ one-time-PIN
fallback), MFA on, and create a **self-hosted Access application per dashboard
hostname** (not a `*.yoonnation.com` wildcard — that would be fragile w.r.t. Plex),
policy = **allow `emmanuelx08@gmail.com`**, implicit deny. **Then** add the tunnel
public-hostname ingress for each dashboard → `https://traefik:443` with
`originRequest.originServerName` = the hostname and **`noTLSVerify: true` (staging
only)**. This ordering guarantees the first public exposure is already Access-gated.

**Tests:** Unauthenticated request to a dashboard host → Cloudflare login page;
sign-in as `emmanuelx08@gmail.com` → dashboard loads through the tunnel; a different
Google identity → denied. Confirm no dashboard was ever reachable unauthenticated
(ingress published only after the policy existed). Plex host unaffected (no Access app,
grey record).

**Integration:** Sits in front of the Step-4 tunnel; the direct Tailscale path
(Step 2/3) still bypasses Access by design (dual-path).

**Demo:** From any browser, visiting a dashboard prompts SSO+MFA and only your account
gets in — and it was gated from the very first public request.

---

## Step 6: Tailscale split-DNS for the direct dual-path
**Objective:** Ensure the same hostnames resolve to the origin for tailnet devices, so
direct access works and is Cloudflare-independent.

**Guidance:** In the Tailscale admin console add a split-DNS (restricted nameserver /
MagicDNS override) so `*.yoonnation.com` (or the specific dashboard hosts) resolve to
`192.168.1.111` for tailnet devices. Document it in the runbook (manual DNS, per R12).

**Tests:** On a tailnet device, `dig grafana.yoonnation.com` returns `192.168.1.111`
and the dashboard loads directly (valid wildcard, via `internal-allowlist`) over both
IPv4 and any Tailscale IPv6 address; off-tailnet, the same name resolves to the tunnel
CNAME and goes through Access. Both paths serve the same cert. Confirm the split-DNS
override does not break off-tailnet Plex resolution (Plex still resolves to the grey
home-IP A-record for non-tailnet clients).

**Integration:** Completes the dual-path promised in R5, layering cleanly over Steps
2–5.

**Demo:** Same URL, two paths: on Tailscale it hits the origin directly and fast; off
Tailscale it goes through Access — both show a valid cert.

---

## Step 7: Flip to production Let's Encrypt
**Objective:** Replace staging certs with browser-trusted prod certs.

**Guidance:** Set `acme_ca_server` to the LE **prod** directory URL. The critical part:
a `caServer` change **alone does not re-issue** — `acme.json` is keyed by resolver name
(`le-dns-cf`), so Traefik treats the staging cert as still valid and the role's
`Restart traefik` handler keeps the file. You **must reset the store**:
1. `docker compose stop traefik` (writing `acme.json` while running risks corruption),
2. truncate/remove and recreate `acme.json` empty at mode 0600 — either a manual host
   step or a **new gated Ansible task** (the existing `touch` task uses
   `modification_time: preserve` and will **not** empty it),
3. `docker compose start traefik` → wildcard re-issues from prod.

Then **remove `noTLSVerify: true`** from every tunnel ingress (origin now presents a
publicly-trusted cert).

**Tests:** Every hostname (dashboards direct + via tunnel, `traefik.yoonnation.com`,
`plex.yoonnation.com`) serves a **browser-trusted** LE cert (`openssl s_client` shows
the LE **prod** issuer, no warnings). `acme.json` contains the prod wildcard and **no
leftover staging cert**. Traefik logs show renewal scheduled (see the limited-check
caveat below). `noTLSVerify` is gone from every ingress.

**Integration:** Same config path as Step 1, plus the explicit store reset — proving the
staging→prod toggle works and is not silently defeated by a stale `acme.json`.

**Demo:** Green padlock on every service; certs are prod LE and set to auto-renew.
_(Renewal itself can't be demoed without time passing — this is a scheduled-renewal
log/date check, not a live-renewal proof.)_

---

## Step 8: Re-point monitoring, acceptance checklist, and runbook docs
**Objective:** Make "done" reproducible and documented, and stop monitoring from being
fooled by the new Access gate.

**Guidance:**
- **Re-point monitors/widgets:** update Uptime-Kuma monitors and Homepage widgets that
  currently probe the public dashboard URLs to hit **internal** service URLs (docker
  service name/port on the compose network, or `.111` + Host header) — otherwise they
  receive Cloudflare Access 302s and report false status. (`homepage-services.yaml.j2`,
  Uptime-Kuma monitor config.)
- **Acceptance:** extend `docs/runbooks/acceptance-validation.md` with the design's
  Testing-Strategy checks, **including** the security check that a WAN direct
  `https://<home-IP>:443` hit with a dashboard `Host` returns **403**, the v4+v6 direct
  dual-path check, and "**no `noTLSVerify` remains on any ingress**".
- **Runbook:** update `docs/runbooks/host-bootstrap.md` with the manual Cloudflare steps
  (tunnel token, per-host ingress, per-host Access apps, grey `plex` A-record, scoped
  DNS token) and the Tailscale split-DNS entry.
- **Purge stale references:** remove `le-http`/`api.insecure` mentions across docs, and
  refresh the documentation-only `public_services`/`internal_services` lists and
  comments in `group_vars/all.yml` to reflect the tunnel, `traefik.yoonnation.com`, and
  `whoami` (these lists are not templated off, but they should not mislead).

**Tests:** Run the full acceptance checklist top-to-bottom against the live stack;
every item passes. Docs contain no references to removed config.

**Integration:** Wires the whole thing together and captures the operational knowledge;
no orphaned config remains.

**Demo:** A clean pass of `acceptance-validation.md` end-to-end, and a runbook a future
operator can follow to reproduce the setup from scratch.
