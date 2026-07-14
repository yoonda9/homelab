# Runbook: Acceptance validation (rebuild-from-code + sign-off)

This runbook proves the headline requirement — **the whole service layer is
rebuildable from code** — and walks the on-host acceptance checklist that signs
off a deployment. It is the capstone: the original rebuild-from-code gate plus
the **traefik-cloudflare-letsencrypt** terminal acceptance (tunnel + Cloudflare
Access, the direct dual-path, the WAN `:443`→`403` gate, and the production LE
flip). Everything here needs **live** `pve` + DAS + WAN, so it is **manual,
documented acceptance**: the offline gate (`just test`) is the automated half;
this is the on-host half. A full pass prints `LOOP_COMPLETE` (§4).

Run it after a clean teardown to confirm the stack comes up purely from the repo
with no manual fiddling **beyond the already-documented host prerequisites**:

- API token, provider SSH, host GIDs, router port-forward → `host-bootstrap.md`
- DAS/ZFS pool import + `/tank/media` → `das-zfs-migration.md`
- Plex claim / Custom server access URLs → `plex-claim.md`

Do **not** duplicate those steps here — complete them once, then follow this
cycle.

---

## 0. Offline gate first (no infra needed)

Before touching `pve`, the full offline backpressure gate must be green:

```bash
just test
```

This runs every `scripts/test_*.py` shape-test plus `tofu fmt -check`/`validate`
plus `ansible-lint --offline` + `ansible-playbook --syntax-check` and exits
non-zero on any failure. A clean `just test` is the precondition for a live
rebuild.

---

## 1. Rebuild from code (clean `just destroy` → `just provision`)

The reproducibility cycle. With the host prerequisites in place and
`mise.local.toml` populated (secrets — see `host-bootstrap.md` and DEC-001):

```bash
# 1. Clean teardown — `just destroy` runs `tofu destroy` on the managed
#    containers (110 plex, 111 docker-host). The DAS/ZFS pool and /tank/media
#    are NOT tofu-managed and survive this.
just destroy

# 2. Re-provision the whole stack from code in one shot.
just provision
```

`just provision` chains the three leaf recipes it composes — run them
individually if you want to inspect each stage:

- `just apply` — re-provision the LXCs from code.
- `just gen-inventory` — render the Ansible inventory from live `tofu output`
  (static .110/.111 fallback when an IP is still null).
- `just play` — re-configure everything inside the containers from code.

> `tofu destroy` removes only the OpenTofu-managed CTs. Media on the ZFS DAS is
> imported out-of-band (`das-zfs-migration.md`) and is bind-mounted read-only
> into the Plex CT, so a destroy/apply cycle never touches the library.

A second `just play` (or `ansible-playbook --check`) should report **no
changes** — idempotency confirms the configuration is fully code-defined.

---

## 2. Acceptance checklist (design §1 "done")

Walk every line. All must hold before sign-off.

### 2.1 Containers created from code

```bash
ssh root@pve "pct list"        # expect 110 (plex) and 111 (docker-host) running
```

### 2.2 Plex GPU / QSV hardware transcode

```bash
# Inside the Plex CT — the iGPU driver MUST be iHD (not i965), and the device
# nodes must be present at the host-mapped GIDs.
ssh root@pve "pct exec 110 -- vainfo --display drm --device /dev/dri/renderD128"
ssh root@pve "pct exec 110 -- ls -l /dev/dri"
```

- `vainfo` reports driver **`iHD`** (the `plex` role asserts this; a wrong
  driver fails the play).
- Play a transcoding title and confirm the Plex Dashboard shows
  **`Transcode (hw)`** (not `(sw)`). Requires Plex Pass — see `plex-claim.md`.

### 2.3 Plex is reachable and trusted from the public internet

From a host **off the LAN** (cellular / external network — true WAN):

```bash
curl -I https://plex.yoonnation.com
```

- Returns **`200`** (or a normal Plex redirect to `/web`), served over a valid,
  browser-trusted Let's Encrypt certificate (no TLS warning).
- This is the **only** service that answers from WAN.

### 2.4 Internal dashboards: LAN-only, valid certs, WAN-blocked

The four extras dashboards each carry a real LE cert (wildcard
`*.yoonnation.com` post DNS-01 switchover) **and** the `internal-allowlist`
middleware, so they load on the LAN/Tailscale but are refused from WAN.

On the **LAN** (or over Tailscale) — each must load with a valid cert:

```bash
for h in grafana prometheus homepage uptime-kuma; do
  curl -I "https://$h.yoonnation.com"      # expect 200 (or auth 401 where set), valid cert
done
```

### 2.5 Adversarial WAN-block (the headline invariant)

From the **same off-LAN host** used in §2.3, prove the Plex-only-public
boundary holds — `grafana` (representative of every internal dashboard) must be
**blocked from WAN** while `plex` still answers:

```bash
# From WAN — MUST be refused (connection refused / 403 / timeout), NEVER 200:
curl -I --max-time 10 https://grafana.yoonnation.com   # expect failure, NOT 200
# …while, from the same WAN vantage point, Plex still answers:
curl -I https://plex.yoonnation.com                    # expect 200
```

Sign-off requires **both**: `grafana.yoonnation.com` unreachable from WAN **and**
`plex.yoonnation.com` returning `200` from WAN, simultaneously. If an internal
dashboard answers `200` from WAN, the deployment FAILS acceptance — re-check the
Traefik router rules and the `internal-allowlist@file` middleware before sign-off.

### 2.6 Cloudflare Access — allow/deny by identity (the tunnel path)

Off-tailnet, the dashboards are reachable **only** through the Cloudflare tunnel,
gated by a **per-host Access application** (Google SSO + MFA). Prove the identity
gate from a browser on any **off-tailnet** network (see `cloudflare-access.md`):

1. Visit `https://grafana.yoonnation.com` → redirected to the **Cloudflare
   Access** login (SSO + MFA prompt), **not** the dashboard.
2. **Allow:** sign in as `emmanuelx08@gmail.com` → the dashboard **loads through
   the tunnel**.
3. **Deny:** sign in as a **different** Google identity → **denied** (implicit
   deny). Access allows exactly one identity and denies every other.

Access sits in front of the origin, so an unauthenticated probe never reaches a
dashboard — this is also why monitors probe internal URLs (§2.9).

### 2.7 Direct dual-path over IPv4 **and** IPv6 (on-tailnet)

On a **tailnet** device (Tailscale up), the same hostnames resolve **directly**
to the origin via the split-DNS override (see `tailscale-split-dns.md`),
bypassing Cloudflare — the second, direct leg of the dual-path:

```bash
# On-tailnet — resolves to the origin, NOT the tunnel CNAME:
dig +short grafana.yoonnation.com          # expect 192.168.1.111
# Loads directly (no Access prompt), over both IPv4 and IPv6:
curl -4 -I https://grafana.yoonnation.com  # IPv4 direct -> 200, valid prod cert
curl -6 -I https://grafana.yoonnation.com  # IPv6 direct -> 200, valid prod cert
```

Both the **IPv4** and the **Tailscale IPv6** address of `192.168.1.111` must be
admitted — `internal-allowlist` carries the v4 CGNAT range `100.64.0.0/10` **and**
the Tailscale IPv6 range `fd7a:115c:a1e0::/48`, so a tailnet client reaching the
box over **v4 or v6** is let through the direct path identically. No Cloudflare
Access prompt appears on the direct path.

### 2.8 WAN direct-hit `:443` with a dashboard `Host` → **403** (load-bearing)

The Plex port-forward opens `:443` on the home IP for **every** `Host`, so a WAN
attacker can point a dashboard hostname straight at the home IP and skip the
tunnel/Access entirely. The `internal-allowlist` middleware is the load-bearing
gate that stops this. From a **WAN** host (cellular / off-LAN), hit the home IP
on **`:443`** directly while **spoofing a dashboard `Host` header**:

```bash
# From WAN — direct to the home IP on :443, Host spoofed to a dashboard.
# --resolve pins the SNI+Host to the raw home IP, skipping DNS/tunnel entirely.
curl -I --max-time 10 --resolve grafana.yoonnation.com:443:<home-IP> \
  https://grafana.yoonnation.com                 # expect 403 (internal-allowlist)
```

This **MUST** return **`403`** (the request originates outside every
`internal-allowlist` range). A `200` here means the allow-list gate is not
covering the port-forward path → the deployment **FAILS** acceptance. Repeat for
`traefik.yoonnation.com` (the dashboard host) — also **403**.

### 2.9 Production certs, monitors, and no staging leftovers

The Step-7 prod flip must be fully landed and monitors must report real status:

- **Browser-trusted prod certs:** every host (dashboards direct + via tunnel,
  `traefik.yoonnation.com`, `plex.yoonnation.com`) serves a **browser-trusted**
  Let's Encrypt **production** wildcard — no TLS warning.

  ```bash
  openssl s_client -connect 192.168.1.111:443 -servername grafana.yoonnation.com \
    </dev/null 2>/dev/null | openssl x509 -noout -issuer   # expect LE prod issuer
  ```

  `acme.json` holds the prod `*.yoonnation.com` wildcard with **no leftover
  staging cert** (staging is gone — the store was reset at the Step-7 flip).
- **No `noTLSVerify` remains on any ingress:** the staging-only
  `noTLSVerify: true` was removed from **every** tunnel public-hostname ingress at
  the prod flip. Confirm in **Zero Trust → Networks → Tunnels → Public
  Hostnames**: no ingress carries `noTLSVerify` — the origin now presents a
  publicly-trusted cert.
- **Dashboard hardened — no `:8080`:** the unauthenticated Traefik dashboard port
  is gone; the dashboard is served only as the routed `traefik.yoonnation.com`.

  ```bash
  curl -I --max-time 5 http://192.168.1.111:8080   # expect connection refused (no :8080)
  ```

- **Monitors report real status:** Homepage `siteMonitor` probes and the
  Uptime-Kuma monitors target **internal** service URLs (docker service
  name/port, e.g. `http://grafana:3000`), **not** the public hostnames — so they
  never receive a Cloudflare Access `302` and report a false "down". Confirm every
  monitored service shows **up/green**.

---

## 3. Sign-off

Acceptance passes when, after a clean §1 rebuild-from-code:

- [ ] `just test` (offline gate) is green.
- [ ] CTs 110/111 created purely from `just apply`.
- [ ] `vainfo` → `iHD`; Plex Dashboard → `Transcode (hw)`.
- [ ] `https://plex.yoonnation.com` → `200` + valid LE cert **from WAN**.
- [ ] grafana / prometheus / homepage / uptime-kuma reachable on **LAN** with
      valid certs.
- [ ] `grafana.yoonnation.com` **blocked from WAN** while `plex.yoonnation.com`
      stays `200` (§2.5).
- [ ] Cloudflare **Access allows** `emmanuelx08@gmail.com` and **denies** every
      other identity on the tunnel path (§2.6).
- [ ] On-tailnet **direct dual-path** resolves to `192.168.1.111` and loads over
      both **IPv4 and IPv6** with no Access prompt (§2.7).
- [ ] **WAN direct `:443`** with a dashboard `Host` header returns **`403`**
      (`internal-allowlist` gate holds over the Plex port-forward) (§2.8).
- [ ] Every host serves a **browser-trusted LE prod** cert; **no leftover staging
      cert**; **no `noTLSVerify`** remains on any ingress; no `:8080` (§2.9).
- [ ] Monitors (Homepage `siteMonitor` + Uptime-Kuma) probe **internal** URLs and
      report real up/down status (§2.9).
- [ ] A repeat `just play` reports no changes (idempotent).

---

## 4. Objective terminal condition — `LOOP_COMPLETE`

This runbook is the objective's terminal gate. When the full §3 sign-off
checklist passes end-to-end against the live production stack — every box ticked,
all nine E2E acceptance checks (§2.1–§2.9) green — the traefik-cloudflare-letsencrypt
objective is **complete**. Record the sign-off and print:

```
LOOP_COMPLETE
```

`LOOP_COMPLETE` is the signal that the whole plan (staging-first through the prod
flip, tunnel + Access, dual-path, monitoring) has been accepted. Do **not** print
it until every acceptance item above has passed on the live stack.
