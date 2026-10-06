# Idea Honing — Requirements Clarification

This document captures the Q&A used to refine the rough idea into a clear specification.

## Q1: What is the host hardware?

**Question:** What hardware will the Proxmox host run on? Specifically:
- CPU model / vendor (Intel vs AMD — affects iGPU transcoding via QSV/VAAPI)
- Onboard GPU you want to use for transcoding (Intel iGPU, AMD iGPU, or a discrete card)
- RAM and system disk
- The external DAS device (make/model, connection — USB, eSATA, SAS HBA — and disk layout)

**Answer:**
- **CPU:** Intel Core i5-13500 (13th gen, "Raptor Lake") — includes Intel UHD Graphics 770 iGPU with Quick Sync (excellent for HW transcoding, incl. HEVC/AV1 decode & 4K).
- **GPU for transcoding:** Intel iGPU (UHD Graphics 770).
- **RAM:** 64 GB.
- **DAS:** QNAP enclosure connected via **USB 3**, configured as **hardware RAID** (presents as a single block device to the host).

## Q2: What does "reproducible" mean to you — which automation tooling?

**Question:** "Reproducible" can mean very different levels of automation. Which approach do you
want this homelab repo to use? (Affects the entire structure of the project.)

**Answer:** **Full IaC** — Terraform/OpenTofu provisions Proxmox VMs/LXCs; Ansible
configures everything (GPU passthrough, DAS mount, Plex, Traefik). Git is the source of
truth. Most reproducible option.

_Considered: Ansible-only, Docker Compose + scripts, documented manual runbook._

## Q3: Plex as LXC container or dedicated VM?

**Question:** You flagged this in the rough idea. Given the hardware (Intel iGPU + USB-3
hardware-RAID DAS), should Plex run in an unprivileged/privileged LXC or a dedicated VM?

**Answer:** **LXC** (recommended path). Rationale: Intel QSV transcoding via `/dev/dri`
bind-mount and DAS access via host bind-mount are both far simpler in an LXC than VM
passthrough. _Open design detail: privileged vs unprivileged LXC (idmap for render group
+ DAS) — to resolve in design/research._

_Considered: dedicated VM with PCIe iGPU + USB passthrough (rejected: fragile, host loses iGPU)._

## Q4: Traefik — network exposure, domain, and TLS

**Question:** How should Traefik be reached, and what domain/TLS model do you want?
(local-only vs internet-exposed, domain name, DNS provider, certificate strategy)

**Answer:** **Internet-exposed + Let's Encrypt.** Services reachable from the internet via a
domain, with trusted Let's Encrypt certificates. _Follow-up details (domain, DNS provider,
exposure method) captured in Q4b._

_Considered: local-only + LE DNS-01, local-only + self-signed/internal CA._

## Q4b: Domain, DNS provider, and how traffic enters the network

**Question:** (a) Do you already own a domain, and through which registrar/DNS provider?
(b) How should external traffic reach Traefik — router port-forward (80/443) or a
Cloudflare Tunnel? (c) Does the host have a static LAN IP / how is DHCP handled?

**Answer:**
- **(a) Domain/DNS:** `yoonnation.com`, currently on **Namecheap**, with plans to migrate
  DNS to **Cloudflare**. Plex will be served at **`plex.yoonnation.com`**.
- **(b) Entry method:** **Router port-forward** (80/443) to the Proxmox host.
- **(c) Networking:** **Static LAN IPs** for both host and Plex LXC. Host is already at
  **192.168.1.50**. LXC IP TBD.

_Implications to address in design/research:_
- _ACME challenge: HTTP-01 works today via the port-forward on :80 with any DNS provider.
  DNS-01 (wildcard certs) is painful on Namecheap (API IP-allowlist + balance/domain
  minimums) but easy on Cloudflare — favors completing the Cloudflare DNS migration, then
  using Cloudflare DNS-01. Design should support switching the ACME resolver._
- _Plex behind Traefik: route `plex.yoonnation.com` → Plex LXC `:32400`, and set Plex
  "Custom server access URLs" accordingly._

## Q5: Current state of the Proxmox host — what's the scope boundary?

**Question:** Is Proxmox VE already installed/configured on 192.168.1.50 (so this project
automates VMs/LXCs/services on top of it), or should the project also cover the bare-metal
Proxmox install & host base config? And what Proxmox version are you on / planning?

**Answer:** Proxmox VE **9.2.3** is **already installed and running** (Debian 13 "Trixie"
base). **Scope: this repo automates only the services on top of the base Proxmox layer.**
Any specialized host-level configuration beyond a base install (e.g. GPU prep, USB DAS
host mount, Terraform API token creation) must be **well documented** in the repo (runbook),
not assumed. User plans to update Proxmox regularly.

_Implication: host-level prerequisites become a documented bootstrap runbook; Terraform/
Ansible target the existing host's API/SSH. Design must keep host changes minimal & explicit._

## Q6: Media storage — existing data, filesystem, and library layout

**Question:** On the QNAP USB RAID volume: (a) Is there existing media already on it that must
be preserved? (b) What filesystem is on the RAID volume (ext4, exFAT, NTFS, etc.)? (c) Rough
capacity and how you want the library organized (Movies/TV split, etc.)?

**Answer:** **This is a MIGRATION, not a greenfield build.** Plex is **already running on a
different server** with all media already populated on the DAS, which is configured as a
**ZFS pool**. The goal is to **migrate the data** (and Plex) to the new Proxmox host.

_This reframes the project: existing data must be preserved; ZFS pool import vs copy must be
decided; Plex application state (DB/watch history/metadata) migration is in scope. See Q6b.
Note: reconcile earlier "hardware RAID" description with "ZFS pool" (see Q6b)._

## Q6b: Migration specifics

**Question:** (1) Is the new i5-13500 box (192.168.1.50) replacing the old Plex server, and
will you physically move the DAS to it — or keep both running and copy over the network?
(2) ZFS detail: is the QNAP exposing raw disks that ZFS manages, or a single hardware-RAID
block device with a ZFS pool on top? (Reconciles the earlier "hardware RAID" note.)
(3) Plex application state: do you need to preserve the Plex database — watch history,
libraries, collections, metadata, account — by migrating the Plex config/data dir, or only
the media files? (4) What OS/platform is the old Plex server (bare metal, Docker, Synology,
another Proxmox)?

**Answer:**
1. **Replacement.** The new i5-13500 host replaces the old server; the **DAS will be
   physically moved** to the new host.
2. **Hardware RAID with a ZFS pool on top**, believed to be **RAID 0** (unconfirmed).
3. **Media files only** — no Plex DB/config migration needed; **metadata will be rebuilt**.
4. Old Plex ran as a **Docker container**. Nothing special needed for Plex migration — just
   ensure the **raw media data is intact** after the move.

**Key constraints derived:**
- The **data migration is a one-time, MANUAL but well-documented** task (runbook), **not
  automated**. By contrast, the **services must be reproducible/rebuildable at any time**
  (that's where Terraform + Ansible apply).
- Migration mechanism: move DAS → Proxmox host sees the single hardware-RAID block device →
  `zpool import` the existing ZFS pool → ZFS datasets mount on host → bind-mount media into
  Plex LXC. No file copy needed if pool imports cleanly.
- ⚠️ **RAID 0 = zero fault tolerance** (any disk failure loses everything; ZFS-on-RAID0 can
  detect but not repair). Must be addressed in the backup/risk discussion (Q9).

## Q7: Service scope — now vs. near-term roadmap

**Question:** "Initially involving Plex" implies more services later. What's in scope for
the first iteration, and what should the architecture be ready to grow into?

**Answer:** **Plex + Traefik + a few extras** (e.g. dashboard, monitoring), with the
repo structured around a **reusable per-service pattern** so more services can be added
later. Specific extras captured in Q7b.

_Considered: Plex+Traefik only; full *arr media-automation stack._

## Q7b: Which extras, and how to run them?

**Question:** Which specific extra services for iteration 1, and how should they run —
each in its own LXC, or a single "Docker host" LXC running them via Docker Compose?

**Answer:**
- **Extras (iteration 1):** **Homepage** (dashboard), **Uptime Kuma** (uptime monitoring),
  **Grafana + Prometheus** (metrics).
- **Run model:** **Decide during design** — weigh single Docker-host LXC (Traefik + extras
  via Compose, Plex in its own LXC) vs. one-LXC-per-service. _Open design decision; also
  decide where Traefik itself runs._

_Considered: one LXC per service; single Docker-host LXC._

## Q8: Secrets management for the IaC

**Question:** Full IaC needs secrets (Proxmox API token, Let's Encrypt/Cloudflare creds,
Plex claim token, Grafana admin pw, etc.). Since git is the source of truth, how do you want
secrets handled so nothing sensitive lands in the repo in plaintext?

**Answer:** **Decide during research.** Evaluate SOPS+age vs Ansible Vault vs gitignored
.env/tfvars (vs external managers like Bitwarden/Infisical) and recommend before committing.

_Considered: SOPS+age; Ansible Vault + gitignored tfvars; all gitignored .env._

## Q9: Backups & risk posture

**Question:** Two backup concerns: (a) **Service state** — IaC rebuilds structure, but stateful
data (Plex DB once rebuilt, Grafana dashboards, Uptime Kuma history) needs backup. Do you want
LXC/VM backups (Proxmox vzdump / Proxmox Backup Server) in scope? (b) **Media** — given RAID 0
has no fault tolerance, is there any existing/desired backup of the media, or is media treated
as expendable/re-acquirable?

**Answer:** **Backups are out of scope** — handled as a **separate task**. Many of these
things already have remote backups. Design should not block on backups, but **may note**
where state lives so a future backup task can target it. RAID 0 risk is **acknowledged and
accepted** for now.

## Q10: Definition of done for iteration 1

**Question:** What does "done" look like for this first iteration — the concrete success
criteria you'd use to call it complete?

**Answer:** "Done" = **only the items within the scope of automation** (the data migration is
explicitly excluded from the success criteria; it remains a documented one-time runbook
deliverable, but is not part of "done"). Concretely:

1. **Reproducible provisioning** — `terraform apply` creates the Plex LXC + the LXC(s) for
   Traefik/extras from scratch against the existing Proxmox host.
2. **Configured by Ansible** — GPU (`/dev/dri`) available in the Plex LXC, DAS path
   bind-mounted, and Plex + Traefik + Homepage + Uptime Kuma + Grafana/Prometheus all
   deployed via code.
3. **Plex working** — streams locally with **HW transcoding via QSV confirmed**.
4. **Traefik working** — `plex.yoonnation.com` (and dashboards) reachable externally over
   HTTPS with valid Let's Encrypt certs via the port-forward.
5. **Reproducibility proven** — tearing down and re-running the IaC rebuilds all services
   (stateful-data caveats aside) without manual fiddling; host-level prereqs captured in a
   runbook.

_Excluded from "done": the physical DAS move + ZFS pool import + media-intact verification
(documented runbook, performed once, manual)._

## Validation addendum (live SSH to host, 2026-06-19)

Confirmed/updated against the running host and existing repo
(full detail: `research/existing-environment.md`):
- **Tooling already in place:** repo uses **OpenTofu** + **`bpg/proxmox ~>0.104`** + **Packer**,
  with **pytest shape-tests** and **uv**. ⇒ Q2 "Terraform+Ansible" resolves to **OpenTofu
  (existing) + Ansible (NET-NEW)**; provider question settled (**bpg**, not telmate).
- **Proxmox API token already exists** (`root@pam!ansible-token`), auth via **`.envrc`/direnv**
  (gitignored). ⇒ feeds the Q8 secrets decision.
- **iGPU confirmed**: `renderD128`, host **render GID 993** / video GID 44 ⇒ key Q3 input for
  privileged-vs-unprivileged LXC + idmap.
- **No LXCs exist yet**; VMIDs 100–103 / 9000–9001 / 9100–9101 in use ⇒ new LXCs in **110–119**.
- **Tailscale already installed** + an **SDN `vnetdmz`** exists ⇒ options for the access/exposure design.
- **DAS not yet attached** (still on old server); no ZFS pool imported ⇒ Q6b pool specifics
  (RAID0 confirmation, datasets, capacity) **can't be validated until the physical move**;
  migration runbook must be discovery-based.
- **Node name `pve`**, bridge **`vmbr0`** (192.168.1.50/24, gw .1), storage **`local-lvm`**
  (rootdir/images) + **`local`** (vztmpl) — match existing module defaults.

## Q12: Plex LXC privilege level (resolved post-research)

**Question:** Privileged vs unprivileged for the Plex LXC, given confirmed host render GID 993?

**Answer:** **Unprivileged for now**, with a **documented fallback to privileged** if the idmap
setup proves too much friction. Confirmed (per research) there is **no meaningful runtime
performance overhead** to unprivileged — QSV transcoding and ZFS bind-mount I/O are unaffected;
the cost is one-time idmap config + provider SSH access, not speed. Design must therefore:
- encode the idmap (map host render GID **993** + video **44**, and DAS ownership) in the IaC,
- ensure the bpg provider has **SSH access** to `pve` (needed for idmap) and pin **bpg >= 0.108.0**,
- keep a privileged variant documented as an easy switch (e.g. a module variable).

## Q13: Plex Pass entitlement (resolved post-research)

**Question:** Do you have an active Plex Pass (hard requirement for HW transcoding)?

**Answer:** **Yes — active Plex Pass.** ⇒ "HW transcoding via QSV confirmed" remains a **hard
success criterion** for "done" (not a stretch goal).

## Q14: Secrets approach (resolved post-research)

**Question:** Which secrets mechanism to lock in?

**Answer:** **Gitignored `mise.local.toml` + Ansible Vault.**
- **Env / OpenTofu / Packer secrets** (Proxmox API token, Cloudflare token, Plex claim) live in
  a **gitignored `mise.local.toml`** (`[env]`), loaded automatically by mise on `cd`. Committed
  `mise.toml` holds tool pins + non-secret env (endpoint, INSECURE) + tasks; ship a
  `mise.local.toml.example` template.
- **In-playbook secrets** (service admin passwords, Grafana admin pw, app keys) via **Ansible
  Vault**.
- _Trade-off accepted: env secrets are not encrypted-in-git (no SOPS), they live only on the
  operator's machine. SOPS+age remains a documented future upgrade path._

_Considered: mise+SOPS+age (encrypted-in-git); defer-to-design._

## Q15: Public exposure scope (resolved post-research)

**Question:** Which services face the internet?

**Answer:** **Plex public + a couple of others** (specific subset captured in Q15b). Remaining
services restricted to **LAN + Tailscale**. Publicly-exposed non-Plex services MUST sit behind
**auth middleware** (Traefik forward-auth / basic-auth, TBD in design).

_Considered: Plex-only public; expose-everything-with-subdomains._

## Q15b: Which additional services should be public?

**Question:** Beyond `plex.yoonnation.com`, which of Homepage / Uptime Kuma / Grafana /
Prometheus should be internet-exposed (with auth), and which stay LAN/Tailscale-only?

**Answer (FINALIZED at design review):** **No additional public extras — Plex is the ONLY
internet-exposed service.** Homepage, Uptime Kuma, Grafana, and Prometheus are all
**LAN/Tailscale-only**. The per-router public/internal split is still config-driven, so a
service can be promoted to public later by editing `public_services`.

_Other design-review resolutions (2026-06-19):_
- **DAS host mountpoint = `/tank`** (confirmed; bind `/tank/media` → CT `/media`). Pool name
  still discovered during the migration runbook, but its mountpoint will be set to `/tank`.
- **No `vnetdmz` hardening yet** — docker-host LXC stays on `vmbr0` (enhancement deferred).
- **Proposed per-CT sizing accepted** (Plex 6c/4G, docker-host 4c/4G) — kept as module
  variables so it's trivial to change later.

## Q11: Dev environment management — migrating direnv → mise

**Question/Note (user-provided):** The project is **migrating away from `direnv` to `mise`**
for environment management during development.

**Answer / implications:**
- New work should use **`mise`** (mise-en-place) for dev env + tool/version management, **not
  `direnv`**. The current `.envrc`/direnv pattern that loads `PROXMOX_VE_*` is being phased out.
- ⇒ The OpenTofu provider env vars (`PROXMOX_VE_ENDPOINT/USERNAME/API_TOKEN/INSECURE`) and any
  Ansible-related env should be sourced via **`mise` config** (e.g. `mise.toml` `[env]`, possibly
  `[tools]` to pin opentofu/packer/ansible/uv versions, and `[tasks]` for workflows).
- ⇒ Directly informs the **Q8 secrets decision**: whatever secrets mechanism we pick (SOPS+age
  vs Ansible Vault vs file-based) must integrate with **mise** rather than direnv (e.g. mise's
  env-file support / `mise.local.toml` gitignored, or mise + SOPS).
- Migration of existing `.envrc` → `mise` is part of the work's context (may be a small
  preliminary task within the design).

