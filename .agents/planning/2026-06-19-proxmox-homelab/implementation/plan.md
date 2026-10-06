# Implementation Plan — Reproducible Proxmox Homelab (Plex + Traefik)

_Project: `2026-06-19-proxmox-homelab` · Companion to `design/detailed-design.md`._

This plan converts the design into a series of **test-driven, incremental, demoable** steps.
Each step builds on the previous, ends by wiring things together, and leaves no orphaned code.
Tests are written **before/alongside** the code in each step (no testing-only steps). Core
end-to-end functionality (provision → configure → reachable service) appears as early as the
dependency chain allows; the riskiest piece (GPU + idmap on the Plex CT) is isolated after the
simpler Docker-host path is proven end-to-end.

> **Context assumed available during implementation:** `idea-honing.md`, `design/detailed-design.md`,
> and all `research/*.md`. The host (`pve` @ 192.168.1.50) is reachable read-only via SSH.
> The DAS media migration is a **manual, user-performed** runbook (Step 6) — not automated.

---

## Progress Checklist

- [ ] **Step 1** — Dev-environment foundation: migrate direnv → mise (tool pins, env, tasks)
- [ ] **Step 2** — Host bootstrap runbook + OpenTofu provider auth (token + SSH for idmap)
- [ ] **Step 3** — Generic `lxc_service` OpenTofu module + provision the Docker-host LXC (minimal)
- [ ] **Step 4** — Ansible scaffolding + `common` role applied to the Docker-host LXC
- [ ] **Step 5** — `docker_host` role: Docker + Traefik (HTTP-01) + smoke route
- [ ] **Step 6** — DAS/ZFS migration runbook + host `/tank` media path wiring
- [ ] **Step 7** — Provision the Plex LXC: GPU passthrough + DAS bind-mount + idmap (unprivileged)
- [ ] **Step 8** — `plex` role: iHD/QSV drivers + Plex install + `vainfo` acceptance gate
- [ ] **Step 9** — Traefik public route for Plex + HTTP-01 cert + Plex custom access URL
- [ ] **Step 10** — Extras stack: Homepage, Uptime Kuma, Grafana, Prometheus (internal-only)
- [ ] **Step 11** — Cloudflare DNS-01 wildcard switchover (internal-service TLS + resolver flip)
- [ ] **Step 12** — Reproducibility validation (destroy → re-apply → re-play) + acceptance sign-off

---

## Step 1: Dev-environment foundation (direnv → mise)

**Objective:** Establish a reproducible developer/operator environment with `mise` so every later
step uses pinned tool versions and consistent env loading; remove direnv.

**Implementation guidance:**
- Add `mise.toml`: `[tools]` pinning `opentofu`, `packer`, `python`, and `"pipx:ansible"`;
  `[env]` for non-secret `PROXMOX_VE_ENDPOINT`, `PROXMOX_VE_INSECURE`, plus
  `_.python.venv = {path=".venv", create=true}`; `[tasks]` for `plan`, `apply`, `play`, `fmt`,
  `test`.
- Add `mise.local.toml.example` (template) documenting the gitignored secret env vars
  (`PROXMOX_VE_API_TOKEN`, `PROXMOX_VE_SSH_USERNAME`, `CLOUDFLARE_DNS_API_TOKEN`).
- Update `.gitignore` to ignore `mise.local.toml`; remove the old `.envrc` and its direnv ignore.

**Test requirements:**
- `scripts/test_mise_config_shape.py`: asserts `mise.toml` parses, has the pinned tools + the five
  tasks; `mise.local.toml` is gitignored; `mise.local.toml.example` exists; **no `.envrc`** remains;
  no plaintext secret keys appear in committed files.

**Integration:** Replaces the existing direnv-based env flow used by `tofu/providers.tf`; the
provider now reads its env from mise.

**Demo:** `mise install` installs pinned opentofu/packer/ansible/python; `cd` into the repo
auto-loads `PROXMOX_VE_*`; `mise run fmt` works; the new pytest passes; `.envrc` is gone.

---

## Step 2: Host bootstrap runbook + provider auth (token + SSH)

**Objective:** Make OpenTofu able to authenticate and operate against `pve`, including the **SSH
access required for idmap** and **root@pam for bind mounts**, with the manual host prereqs documented.

**Implementation guidance:**
- Write `docs/runbooks/host-bootstrap.md`: creating/locating the `root@pam!ansible-token` API
  token, enabling provider SSH (user + key/agent), confirming `getent group render video`
  (expect 993/44), and the router port-forward placeholder.
- Update `tofu/versions.tf`: bump `bpg/proxmox` to **`>= 0.108.0`** (keep `~> 0.104` line).
- Update `tofu/providers.tf`: add an `ssh {}` block (`agent = true`, username from
  `PROXMOX_VE_SSH_USERNAME`).
- Add a harmless `data` source or a node `locals` reference so a `plan` exercises authentication.

**Test requirements:**
- `scripts/test_provider_auth_shape.py`: `versions.tf` pins bpg ≥ 0.108.0; `providers.tf` contains
  an `ssh` block; runbook file exists and mentions token + SSH + GID verification.
- Live check (documented): `mise run plan` authenticates without error (no resources yet).

**Integration:** Builds on Step 1's env loading; provider config is now complete for the
container features used in later steps.

**Demo:** `tofu validate` passes; `tofu plan` connects to `pve` and authenticates successfully;
the bootstrap runbook walks a reader from bare host to "Tofu can talk to Proxmox."

---

## Step 3: `lxc_service` module + provision the Docker-host LXC (minimal)

**Objective:** Create the reusable LXC module and prove **end-to-end provisioning** by standing up
the Docker-host container (no GPU/bind complexity yet).

**Implementation guidance:**
- Create `tofu/modules/lxc_service/` (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`,
  `README.md`) wrapping `proxmox_virtual_environment_container` with the variables in design §4.1
  (incl. `unprivileged` default true, `nesting`, dynamic `device_passthrough`/`mount_point`/`idmap`
  from list vars, `ssh_public_keys`).
- Add `tofu/locals.tf` entries: `service_ids`, `net`, `host_gids` (design §5.1).
- Add `tofu/main.tf` instantiating the module for **docker-host** (vmid 111, `nesting=true`,
  192.168.1.111/24, no passthrough/bind). Add `tofu/outputs.tf` exposing CT id/ip/name.
- Ensure a Debian 13 LXC template is available on `local` (`vztmpl`) — document the
  `pveam`/download step or use a `proxmox_virtual_environment_download_file` resource.

**Test requirements:**
- `scripts/test_lxc_service_module_shape.py`: module files present; resource is
  `proxmox_virtual_environment_container`; `unprivileged` defaults true; module renders
  passthrough/mount/idmap blocks only when vars are set; pins bpg ≥ 0.108.
- `tofu validate` + `tofu fmt -check` in CI.

**Integration:** First consumer of the module + provider from Steps 1–2; outputs will feed the
Ansible inventory in Step 4.

**Demo:** `mise run apply` creates CT 111; `pct list` on `pve` shows `docker-host` running; you can
SSH into it with the provisioned key.

---

## Step 4: Ansible scaffolding + `common` role

**Objective:** Stand up the configuration layer and apply a baseline `common` role to the
Docker-host CT, driven by an inventory derived from Tofu outputs.

**Implementation guidance:**
- Create `ansible/` (`ansible.cfg`, `inventory/hosts.yml`, `group_vars/all.yml`,
  `group_vars/vault.yml` [Ansible Vault], `site.yml`, `roles/common/`).
- `common` role: base packages, timezone, unattended-upgrades, service user, SSH hardening —
  idempotent.
- Document/automate generating `inventory/hosts.yml` from `tofu output` (e.g. a `mise` task).

**Test requirements:**
- `scripts/test_ansible_layout_shape.py`: roles/`site.yml`/inventory/vault exist and are wired;
  `ansible-lint` clean; `ansible-playbook --syntax-check site.yml` passes.
- Idempotency: second `--check` run reports no changes.

**Integration:** Consumes Step 3 outputs (CT IP) as inventory; establishes the role pattern reused
by `plex` and `docker_host`.

**Demo:** `mise run play` runs `common` against `docker-host`; re-running is a no-op (idempotent);
syntax/lint/shape tests pass.

---

## Step 5: `docker_host` role — Docker + Traefik (HTTP-01) + smoke route

**Objective:** Bring up Docker + Compose and a working **Traefik** with a smoke service, proving
the reverse-proxy path before adding real apps.

**Implementation guidance:**
- `docker_host` role: install Docker CE + compose plugin; deploy `compose.yml.j2` with **Traefik**
  (entrypoints `web`→redirect→`websecure`; two certresolvers defined `le-http`/`le-dns-cf`,
  default `le-http`) and a **`whoami`** smoke container with internal-only router + `lan-allowlist`.
- Define middlewares: `redirect-to-https`, `security-headers`, `lan-allowlist`.

**Test requirements:**
- Extend `test_traefik_config_shape.py`: both certresolvers present; `lan-allowlist` applied to the
  smoke router; compose template renders valid YAML (lint).
- Live: `docker compose config` valid; Traefik container healthy; `whoami` reachable on LAN.

**Integration:** Builds on the `common`-prepared Docker-host CT; the Traefik instance here is the
same one Plex and the extras attach to in Steps 9–10.

**Demo:** On LAN, hitting the smoke route returns the `whoami` response via Traefik (HTTP→HTTPS
redirect working); the route is blocked from WAN.

---

## Step 6: DAS/ZFS migration runbook + host `/tank` media path

**Objective:** Produce the **manual, discovery-based** migration runbook and ensure the host
`/tank/media` path exists so the Plex CT bind-mount (Step 7) has a target.

**Implementation guidance:**
- Write `docs/runbooks/das-zfs-migration.md` per research: power-down/export on old host → physical
  move → `zpool import` discovery → `zpool import -f -d /dev/disk/by-id <pool>` → set
  `mountpoint=/tank` / cachefile → `autotrim=off` → scrub → verify media intact (the migration
  acceptance gate).
- Document the interim for testing **before** the real migration: create an empty `/tank/media` on
  the host so bind-mount mechanics can be validated without real media.

**Test requirements:**
- `scripts/test_runbook_shape.py`: runbook exists and contains the import-by-id, `-f`, `mountpoint`,
  and "verify media intact" steps.
- No automated infra test (migration is manual by design); validation is the runbook's own checks.

**Integration:** Provides the `/tank/media` host path consumed by Step 7's `bind_mounts`.

**Demo:** Walk the runbook end-to-end on paper; on the host, `/tank/media` exists (empty placeholder
or real pool if migration already performed); `zpool status` ONLINE when the DAS is attached.

---

## Step 7: Provision the Plex LXC — GPU passthrough + DAS bind + idmap

**Objective:** Instantiate the **Plex CT (110)** from the same module with the hard parts:
`/dev/dri` device passthrough, the `/tank/media` bind-mount, and unprivileged **idmap** for GID
993/44.

**Implementation guidance:**
- Add a `module "plex"` block (design §5.2): `unprivileged=true`, `device_passthroughs` for
  `renderD128` (gid 993) + `card1` (gid 44), `bind_mounts` `/tank/media`→`/media`.
- Implement the idmap generation in the module (design §5.3 tiling) from `host_gids`.
- Add Plex CT to `outputs.tf`/inventory.

**Test requirements:**
- Extend `test_lxc_service_module_shape.py`: given passthrough+idmap vars, the module emits the
  expected `device_passthrough`, `mount_point`, and gap-free `idmap` blocks.
- Live acceptance: after apply, inside CT 110 `ls -l /dev/dri/renderD128` shows the device with the
  mapped group; `/media` lists the DAS contents (or the placeholder dir).

**Integration:** Reuses the Step 3 module + Step 2 provider SSH (for idmap) + Step 6 `/tank/media`.

**Demo:** `mise run apply` creates CT 110; `pct list` shows `plex`; inside the container the GPU
render node and the `/media` mount are both present with correct ownership. _(If idmap proves
fiddly, flip `unprivileged=false` — the documented fallback — and re-apply.)_

---

## Step 8: `plex` role — iHD/QSV drivers + Plex install + verify

**Objective:** Configure the Plex CT so Plex runs and **QSV hardware transcoding works**, with an
automated `vainfo` acceptance gate.

**Implementation guidance:**
- `plex` role: enable Debian `non-free`; install `intel-media-va-driver-non-free vainfo
  intel-gpu-tools`; add the Plex APT repo + key; install `plexmediaserver`; ensure the `plex` user
  is in the in-CT render/video groups.
- Post-deploy task: run `vainfo --display drm --device /dev/dri/renderD128` and **assert driver
  `iHD`** (fail the play otherwise).
- Document the claim flow (web wizard at `:32400/web`, token TTL ~4 min) and setting Plex
  "Custom server access URLs" → `https://plex.yoonnation.com:443`.

**Test requirements:**
- Extend `test_ansible_layout_shape.py`: `plex` role installs the iHD package and contains the
  `vainfo`/`iHD` assertion task.
- Live acceptance: `vainfo` reports `iHD` with `VAEntrypointEncSlice`; Plex Dashboard shows
  **"Transcode (hw)"** on a forced-transcode playback.

**Integration:** Runs against the Step 7 Plex CT via the Step 4 Ansible pipeline.

**Demo:** Plex web UI reachable at `http://192.168.1.110:32400/web`; a library added from `/media`;
forcing a transcode shows hardware transcoding in the Plex Dashboard.

---

## Step 9: Traefik public route for Plex + HTTP-01 cert

**Objective:** Deliver the **core public end-to-end**: `plex.yoonnation.com` served over HTTPS with
a valid Let's Encrypt cert via the router port-forward.

**Implementation guidance:**
- Add a Traefik **file-provider** router (Plex isn't in Docker) routing
  `plex.yoonnation.com` (websecure, resolver `le-http`) → `http://192.168.1.110:32400`.
- Confirm router port-forward 80/443 → 192.168.1.111 and the `plex` public DNS A record (runbook).
- Set Plex "Custom server access URLs" to the public hostname.

**Test requirements:**
- Extend `test_traefik_config_shape.py`: a `plex` router exists on the public path using
  `le-http`; `public_services == [plex]`.
- Live acceptance: `curl -I https://plex.yoonnation.com` → 200 with a valid LE cert from WAN;
  internal routers remain WAN-blocked.

**Integration:** Connects the Step 5 Traefik to the Step 8 Plex; first externally-reachable service.

**Demo:** From outside the LAN, `https://plex.yoonnation.com` loads Plex with a valid certificate
and plays media (HW transcoding when needed).

---

## Step 10: Extras stack — Homepage, Uptime Kuma, Grafana, Prometheus (internal-only)

**Objective:** Add the supporting services to the compose stack, all **LAN/Tailscale-only**, with
working monitoring.

**Implementation guidance:**
- Extend `compose.yml.j2`: Homepage, Uptime Kuma, Grafana, Prometheus, each with Traefik labels for
  an **internal** router + `lan-allowlist`. Prometheus scrapes node/cAdvisor + Traefik metrics;
  Grafana provisioned with the Prometheus datasource + a starter dashboard; Homepage links the
  services; Uptime Kuma monitors Plex + the others.
- Drive which services are public/internal from `group_vars` (`public_services=[plex]`,
  `internal_services=[homepage,uptime-kuma,grafana,prometheus]`).

**Test requirements:**
- Extend `test_traefik_config_shape.py`: all four extras are internal routers carrying
  `lan-allowlist`; none appear in `public_services`; Prometheus never public.
- Live acceptance: each dashboard reachable on LAN/Tailscale, blocked from WAN; Grafana shows live
  Prometheus data.

**Integration:** Same Traefik/compose stack from Steps 5/9; uses the config-driven exposure split.

**Demo:** On LAN/Tailscale, Homepage shows all services; Grafana renders host metrics from
Prometheus; Uptime Kuma shows everything green; none of them are reachable from the internet.

---

## Step 11: Cloudflare DNS-01 wildcard switchover

**Objective:** Enable valid TLS for the **internal** services (which can't use HTTP-01) by switching
to the Cloudflare **DNS-01 wildcard `*.yoonnation.com`**, proving the resolver is a one-variable flip.

**Implementation guidance:**
- Prereq (user-paced): complete the Namecheap→Cloudflare DNS migration; create a scoped
  `CLOUDFLARE_DNS_API_TOKEN` (Zone:DNS:Edit) in `mise.local.toml`.
- Configure Traefik `le-dns-cf` certresolver (Cloudflare provider) for `*.yoonnation.com`; flip
  `acme_resolver` (and per-router resolvers) to `le-dns-cf`.

**Test requirements:**
- Extend `test_traefik_config_shape.py`: `le-dns-cf` resolver defined with the Cloudflare DNS
  challenge + wildcard domains; resolver selection is variable-driven.
- Live acceptance: internal hostnames present a valid wildcard LE cert (no browser warning) on
  LAN/Tailscale; Plex still valid.

**Integration:** Replaces the interim self-signed certs for internal services from Step 10; reuses
the dual-resolver design from Step 5.

**Demo:** `grafana.yoonnation.com` (LAN/Tailscale) loads with a valid `*.yoonnation.com` cert;
flipping the resolver variable back and forth re-issues certs without other changes.

---

## Step 12: Reproducibility validation + acceptance sign-off

**Objective:** Prove the headline requirement — the whole service layer is **rebuildable from
code** — and confirm all automation-scope "done" criteria.

**Implementation guidance:**
- Run the full cycle: `tofu destroy` (CTs) → `tofu apply` → generate inventory → `ansible-playbook
  site.yml` → bring up compose — with **no manual fiddling** beyond the documented host prereqs
  (token/SSH/port-forward/DAS already in place).
- Capture any manual touchpoints discovered and fold them into roles or the runbook (close orphan gaps).
- Add a top-level `mise run test` aggregating all pytest shape-tests + `tofu validate` + `ansible-lint`.

**Test requirements:**
- Full shape-test suite + validate/lint green in CI.
- On-host acceptance checklist (the design §1 "done" gates): CTs created; `vainfo` iHD; Plex HW
  transcode; `https://plex.yoonnation.com` valid from WAN; internal services LAN-only with valid
  certs; rebuild reproduced.

**Integration:** Exercises every prior step together; the final wiring/validation of the system.

**Demo:** A clean teardown + rebuild yields a fully working stack (Plex transcoding + reachable
externally; dashboards internal) purely from the repo, with the acceptance checklist all green.

---

## Notes on sequencing & TDD
- Each step ships its own tests with the code (no separate "add tests" steps).
- Risk isolation: the simple Docker-host path (Steps 3–5) proves module+Ansible+Traefik before the
  GPU/idmap complexity (Steps 7–8).
- Earliest user-visible value: a working reverse proxy by Step 5; public Plex by Step 9.
- Manual, non-automated work (DAS migration, DNS migration, port-forward) is documented in
  runbooks and explicitly outside the automation "done" criteria.
