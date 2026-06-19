# Runbook: Acceptance validation (rebuild-from-code + sign-off)

This runbook proves the headline requirement — **the whole service layer is
rebuildable from code** — and walks the on-host acceptance checklist that signs
off a deployment. It is the capstone (Step 12). Everything here needs **live**
`pve` + DAS + WAN, so it is **manual, documented acceptance**: the offline gate
(`mise run test`) is the automated half; this is the on-host half.

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
mise run test
```

This runs every `scripts/test_*.py` shape-test plus `tofu fmt -check`/`validate`
plus `ansible-lint --offline` + `ansible-playbook --syntax-check` and exits
non-zero on any failure. A clean `mise run test` is the precondition for a live
rebuild.

---

## 1. Rebuild from code (clean destroy → apply → play)

The reproducibility cycle. With the host prerequisites in place and
`mise.local.toml` populated (secrets — see `host-bootstrap.md` and DEC-001):

```bash
# 1. Clean teardown — destroy the managed containers (110 plex, 111 docker-host).
#    The DAS/ZFS pool and /tank/media are NOT tofu-managed and survive this.
mise exec -- tofu -chdir=tofu destroy        # equivalently: cd tofu && tofu destroy

# 2. Re-provision the LXCs from code.
mise run apply

# 3. Render the Ansible inventory from live `tofu output` (static .110/.111
#    fallback when an IP is still null).
mise run gen-inventory

# 4. Re-configure everything inside the containers from code.
mise run play
```

> `tofu destroy` removes only the OpenTofu-managed CTs. Media on the ZFS DAS is
> imported out-of-band (`das-zfs-migration.md`) and is bind-mounted read-only
> into the Plex CT, so a destroy/apply cycle never touches the library.

A second `mise run play` (or `ansible-playbook --check`) should report **no
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
`*.yoonnation.com` post DNS-01 switchover) **and** the `lan-allowlist`
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
Traefik router rules and the `lan-allowlist@file` middleware before sign-off.

---

## 3. Sign-off

Acceptance passes when, after a clean §1 rebuild-from-code:

- [ ] `mise run test` (offline gate) is green.
- [ ] CTs 110/111 created purely from `mise run apply`.
- [ ] `vainfo` → `iHD`; Plex Dashboard → `Transcode (hw)`.
- [ ] `https://plex.yoonnation.com` → `200` + valid LE cert **from WAN**.
- [ ] grafana / prometheus / homepage / uptime-kuma reachable on **LAN** with
      valid certs.
- [ ] `grafana.yoonnation.com` **blocked from WAN** while `plex.yoonnation.com`
      stays `200` (§2.5).
- [ ] A repeat `mise run play` reports no changes (idempotent).
