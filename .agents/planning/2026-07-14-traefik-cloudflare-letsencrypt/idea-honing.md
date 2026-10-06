# Idea Honing — Requirements Clarification

_Q&A log for: Update Traefik for a Cloudflare-managed domain with Let's Encrypt
SSL. One question at a time; answers appended as the user responds._

## Q1 — What is driving this task, and what does "set up correctly" mean?

Is something currently broken (cert errors, failed/expiring renewals, sites
unreachable, browser TLS warnings), or is this a preventative "verify it's
correct and harden it" pass over an already-working setup? What would "done"
look like to you?

**Answer:** This is a **preventative hardening pass**, not a break/fix. Cloudflare
is currently in **proxied (orange cloud)** mode, but the user is open to switching
to **DNS-only (grey cloud)** if that is the recommendation. The setup is
**unverified** — it is a brand-new, work-in-progress deployment, so nothing has
been confirmed to actually issue certs / serve traffic yet. "Done" therefore
means: a design that is provably correct and hardened, with a way to verify the
end-to-end flow, rather than a fix to a known failure.

## Q2 — Target TLS architecture (proxied + Full-Strict vs DNS-only)?

With Cloudflare **proxied**, the visitor sees Cloudflare's edge cert; the Let's
Encrypt wildcard on the origin (Traefik) becomes the *origin* cert that
Cloudflare validates on the back-connection. That only works if Cloudflare's
SSL/TLS mode is **Full (Strict)**; "Flexible"/"Full" would misbehave (redirect
loop / no origin validation). DNS-01 (`le-dns-cf`, already configured) is the
right challenge type either way because HTTP-01 breaks behind the proxy.

Which target do you want?

**Answer:** Not sure yet — user wants to **research the trade-offs** (proxied vs
DNS-only for a homelab) before deciding. → Branch to research (Step 4), then
return here to finalize Q2.

**Final answer (post-research):** **Hybrid** — grey (DNS-only) for Plex (ToS) and
the internal services (reached via Tailscale/LAN) now; reserve proxied+Full-Strict
only for a future genuinely-public web service, documented as an upgrade path.
Net effect: the current design is DNS-only, keeping `le-dns-cf` wildcard +
`lan-allowlist` + Tailscale correct. See
[research/proxied-vs-dns-only.md](../research/proxied-vs-dns-only.md).

## Q3 — DNS record model & how names resolve

For DNS-only to be both reachable and safe, we need to pin down the record layout:
- Is there a **wildcard** `*.yoonnation.com` record, or per-host records?
- What do they point at — the **home public IP**, the **LAN IP (192.168.1.111)**,
  or a **Tailscale IP**?
- How do you reach internal dashboards day-to-day — over **Tailscale**, on the
  **LAN**, or from anywhere? Is there any split-horizon / internal DNS?
- Are DNS records managed **by hand in the Cloudflare dashboard**, or should they
  be **managed as code** (e.g. a Cloudflare Ansible/Terraform provider) as part of
  this work?

**Answer (partial):**
- DNS management: **out of scope — kept manual** in the Cloudflare dashboard; the
  design documents the required records. ✓
- Internal resolution: **user reconsidering** — "maybe these should be set for the
  proxied Cloudflare routes." This reopens the Q2 Hybrid decision for the internal
  dashboards. → Clarifying follow-up Q3a below.

## Q3a — What does "proxied Cloudflare routes" mean for the internal dashboards?

"Expose the internal dashboards through Cloudflare" realistically means one of:
1. **Cloudflare Tunnel (`cloudflared`)** — outbound-only tunnel from the host to
   Cloudflare. No port-forward, home IP never exposed, records are proxied by
   definition, and you can layer **Cloudflare Access (SSO/Zero-Trust)** in front
   instead of `lan-allowlist`. Visitor sees Cloudflare's edge cert; Traefik behind
   the tunnel can still present the LE wildcard. Bigger scope, different model.
2. **Proxied public A-records → home IP** — orange-cloud records pointing at the
   home public IP via the existing port-forward. Requires SSL/TLS=Full(Strict),
   split-horizon DNS for LAN, `forwardedHeaders.trustedIPs`, and `ipStrategy.depth`
   on the allow-lists. Complex, and still exposes the home IP through the forward.
3. **Grey/DNS-only** (the Hybrid we had) — no Cloudflare in the data path;
   `lan-allowlist` + Tailscale as-is.

**Answer:** **Adopt Cloudflare Tunnel + Access now** (option 1). Internal dashboards
will be exposed via `cloudflared` with Cloudflare Access (SSO) in front, replacing
`lan-allowlist` on tunneled routes. Scope expands accordingly. See
[research/tunnel-vs-tailscale.md](../research/tunnel-vs-tailscale.md).

> **Scope note:** the task is now "Traefik + Cloudflare (Tunnel + Access) + Let's
> Encrypt," not just a TLS-mode tweak. Traefik stays the reverse proxy *behind* the
> tunnel; the LE wildcard remains on the origin (Plex, Tailscale/direct access,
> defense-in-depth).

## Q4 — Service exposure map (esp. Plex under the Tunnel)

Cloudflare's ToS bars streaming media through its proxy/tunnel, so **Plex cannot go
through the Tunnel**. We need a per-service exposure decision:
- **Internal dashboards** (grafana, prometheus, uptime, homepage, whoami) → Tunnel
  + Access. �was implied by the Q3a choice.
- **Plex** → must NOT use the Tunnel. Options: keep it **direct via the existing
  port-forward + LE cert** (public `plex.yoonnation.com`, grey DNS), or make it
  **Tailscale-only** (no WAN exposure at all).
- Confirm no other service needs public/browser exposure.

**Answer:**
- **Plex → Direct via port-forward + LE (public).** Keep `plex.yoonnation.com`
  public: grey A-record → home IP, existing 80/443 port-forward, Traefik serves the
  LE wildcard, `security-headers` but no `lan-allowlist`; Plex's own auth guards it.
- **Other services → none now ("maybe later").** The design must leave a clean,
  repeatable pattern to add more tunneled + Access-gated services later.

## Q5 — Tunnel wiring: management model + how cloudflared reaches Traefik

Two sub-decisions for the `cloudflared` component:
- **Management model:** (a) **locally-managed** — `config.yml` + credentials file
  rendered by Ansible (ingress rules live in the repo, "as code"); or (b)
  **remotely-managed** — a dashboard-created tunnel using a **token** (stored in
  vault like `CF_DNS_API_TOKEN`), ingress edited in the Zero Trust dashboard.
- **cloudflared → Traefik hop:** cloudflared runs in the compose stack and reaches
  Traefik by service name. Recommended: cloudflared forwards each hostname to
  `https://traefik` (websecure), so Traefik still routes by Host and serves the LE
  wildcard end-to-end; `originServerName` set to the hostname (or `noTLSVerify` as a
  fallback). Keeps the LE wildcard meaningful behind the tunnel.

**Answer:** **Remotely-managed** — tunnel created in the Cloudflare dashboard;
`cloudflared` runs with a **token stored in vault** (alongside
`CF_DNS_API_TOKEN`); ingress + Access apps configured in the Zero Trust dashboard.
The cloudflared→Traefik hop design detail (forward to `https://traefik`, keep host
routing + LE wildcard) is delegated to the design doc.

## Q6 — Cloudflare Access identity & policy

Who is allowed through the Access gate, and via which login? For a single-admin
homelab the natural fit is **Google login restricted to your account**
(emmanuelx08@gmail.com) with **email OTP** as a fallback IdP, MFA on. Policy: allow
that email, block everyone else; apply to every tunneled dashboard hostname.

**Answer:** **Google SSO + email OTP fallback**, MFA on; **single-user allow policy
for emmanuelx08@gmail.com**, everyone else blocked, applied to every tunneled
dashboard.

## Q7 — Fate of the in-flight Traefik dashboard change (api.insecure :8080)

The uncommitted working-tree diff adds `api.insecure: true` and publishes `:8080`
(LAN/Tailscale-only). Under the new Tunnel + Access model, the cleaner pattern is to
**drop `api.insecure` and the `:8080` publish** and instead route the dashboard via
Traefik's `api@internal` service as a proper router `traefik.yoonnation.com`,
tunneled + Access-gated like the other dashboards. That removes an unauthenticated
port and unifies the access model. Alternative: keep the insecure LAN-only port as
the diff intends.

**Answer:** **Tunnel + Access, drop the insecure port.** Remove `api.insecure` and
the `:8080` publish; route the dashboard via `api@internal` as
`traefik.yoonnation.com`, tunneled + Access-gated like the other dashboards.
(Supersedes the uncommitted working-tree diff.)

## Q8 — Direct Tailscale/LAN access to dashboards, or Tunnel-only?

`cloudflared` reaches Traefik from the Docker network, so its source IP is not in
`lan-allowlist` — meaning the tunnel path and the current `lan-allowlist` path are
in tension. Two models:
- **Dual-path (recommended):** keep direct Tailscale/LAN access to dashboards (fast,
  works even if Cloudflare is down) **and** Tunnel + Access for browser/remote. The
  dashboard routers allow LAN + Tailscale + the cloudflared source; Access gates
  only the tunnel path. Trade-off: on-LAN access bypasses SSO (LAN treated as
  trusted).
- **Tunnel-only:** dashboards reachable *only* via Cloudflare Access. Strongest (SSO
  everywhere), but requires enforcing the Access JWT at Traefik so the shared `:443`
  can't be used to bypass Access on-LAN, and you always round-trip through
  Cloudflare.

**Answer:** **Dual-path.** Keep direct Tailscale/LAN access to dashboards AND add
Tunnel + Access for browser/remote. Dashboard routers allow LAN + Tailscale +
cloudflared source; Access gates the tunnel path; on-LAN access is trusted and
bypasses SSO.

## Q9 — Verification & rollout (it's brand-new/unverified)

Since nothing has been proven yet and "done = prove it works," and Let's Encrypt has
strict prod rate limits: do you want a **staging-first** rollout — validate the full
chain against the **LE staging** CA (untrusted cert, but proves DNS-01 + tunnel +
Access + Plex end-to-end), then flip to **prod** LE and confirm a browser-trusted
cert — before calling it done? Acceptance should extend the existing
`docs/runbooks/acceptance-validation.md`.

**Answer:** **Staging-first, then prod** (validate whole chain on LE staging, flip to
prod, confirm browser-trusted cert). Acceptance = **extend
`acceptance-validation.md`** with concrete pass/fail checks (valid auto-renewing LE
cert per host, tunnel healthy, Access blocks unauth + allows the admin, Plex public,
dashboards dual-path).

## Q10 — Secrets and the unused HTTP-01 resolver

- **Tunnel token secret:** follow the existing vault pattern
  (`vault_cloudflare_dns_api_token` → `CF_DNS_API_TOKEN`). Add
  `vault_cloudflare_tunnel_token` → `TUNNEL_TOKEN` for `cloudflared`, rendered into
  the sibling `.env` (0600). Separate from the DNS token (different scope).
- **`le-http` resolver:** DNS-01 (`le-dns-cf`) stays the active resolver. Keep
  `le-http` defined-but-unused as a documented fallback, or remove it for tidiness?

**Answer:** Tunnel token → **add `vault_cloudflare_tunnel_token` → `TUNNEL_TOKEN`**
in the `.env` (0600), separate from the DNS token. **Remove `le-http`** — DNS-01
(`le-dns-cf`) becomes the sole resolver. (Plex's public cert is covered by the
DNS-01 wildcard, so HTTP-01 is unnecessary.)

---

## Consolidated requirements (end of clarification)

1. **Architecture (Hybrid, DNS-first):** no Cloudflare *proxy* on data paths;
   Cloudflare used as (a) DNS + DNS-01 ACME provider and (b) **Tunnel + Access** for
   the internal dashboards.
2. **Certs:** single Let's Encrypt **wildcard** `yoonnation.com` + `*.yoonnation.com`
   via **DNS-01** (`le-dns-cf`), auto-renewing, stored in `acme.json`. `le-http`
   removed. **Staging-first**, then prod.
3. **Internal dashboards** (grafana, prometheus, uptime-kuma, homepage, whoami, and
   the **Traefik dashboard** as `traefik.yoonnation.com` via `api@internal`):
   exposed via **cloudflared Tunnel + Cloudflare Access** (Google SSO + email-OTP
   fallback, MFA, single-user allow `emmanuelx08@gmail.com`). **Dual-path**: also
   directly reachable over Tailscale/LAN.
4. **Plex:** public, **direct** via existing 80/443 port-forward + LE wildcard,
   grey DNS A-record → home IP, `security-headers` only (Plex's own auth). **Not**
   tunneled/proxied (Cloudflare media ToS).
5. **Middleware:** `lan-allowlist` retained for the direct Tailscale/LAN path;
   dashboard routers additionally admit the cloudflared source so the tunnel path
   works; Access is the gate on the tunnel path. `security-headers` everywhere.
6. **Tunnel:** **remotely-managed** (dashboard-created), `cloudflared` in the compose
   stack running with **`TUNNEL_TOKEN`** from vault; forwards to `https://traefik`
   so Traefik keeps host-routing + serves the LE wildcard end-to-end.
7. **DNS management:** out of scope / manual in the Cloudflare dashboard; design
   documents the required records (grey `plex` A-record; tunnel CNAMEs auto-created
   by the tunnel; internal hostnames via Tunnel/Tailscale).
8. **Dashboard hardening:** drop the uncommitted `api.insecure` + `:8080` publish;
   dashboard served through Traefik behind Access.
9. **Secrets:** `vault_cloudflare_dns_api_token` (scoped Zone:DNS:Edit +
   Zone:Zone:Read) and `vault_cloudflare_tunnel_token`, both rendered to `.env`
   (0600), never committed.
10. **Verification:** staging→prod rollout; extend
    `docs/runbooks/acceptance-validation.md` with concrete pass/fail checks.


