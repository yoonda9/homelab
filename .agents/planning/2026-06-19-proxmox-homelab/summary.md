# Project Summary — Reproducible Proxmox Homelab (Plex + Traefik)

_Project: `2026-06-19-proxmox-homelab` · Planning completed: 2026-06-19_

## What this is
A Prompt-Driven Development planning pass that turned the rough idea — "a reproducible Proxmox
homelab with Plex (GPU transcoding + DAS storage) behind Traefik" — into a clarified spec,
validated research, a detailed design, and a step-by-step implementation plan.

## Artifacts created
```
.agents/planning/2026-06-19-proxmox-homelab/
├── rough-idea.md                     # the initial concept
├── idea-honing.md                    # full Q&A requirements clarification (Q1–Q15b) + validation addendum
├── research/
│   ├── existing-environment.md       # live host + repo facts (validated via SSH)
│   ├── iac-lxc-provisioning.md       # bpg/proxmox LXC: device_passthrough, mount_point, idmap, version pins
│   ├── gpu-transcoding-and-plex.md   # QSV in LXC, iHD drivers, verification, Plex setup
│   ├── zfs-das-migration.md          # ZFS-on-USB pool import + migration runbook outline
│   ├── secrets-and-mise.md           # mise dev-env + secrets options
│   └── traefik-and-exposure.md       # run model, ACME strategy, exposure, target architecture
├── design/
│   └── detailed-design.md            # standalone design (architecture, components, data models, errors, tests, appendices)
├── implementation/
│   └── plan.md                       # 12 test-driven, demoable steps + progress checklist
└── summary.md                        # this document
```
_Runbooks (`docs/runbooks/host-bootstrap.md`, `docs/runbooks/das-zfs-migration.md`) are authored as
implementation Steps 2 and 6._

## Design in brief
- **Two layers:** OpenTofu (provision) + Ansible (configure); git is the source of truth.
- **Plex:** unprivileged LXC (vmid 110) with `/dev/dri` QSV passthrough (host render GID **993**,
  video 44) and the DAS bind-mounted at `/media`. Privileged is a documented one-variable fallback.
- **Extras:** a single Docker-host LXC (vmid 111) runs Traefik + Homepage + Uptime Kuma + Grafana +
  Prometheus via Docker Compose.
- **Reuse:** one generic `lxc_service` OpenTofu module instantiated per service — mirrors the repo's
  existing `dev_vm` module + pytest shape-test conventions.
- **TLS/exposure:** **Plex is the only public service** (`plex.yoonnation.com`, HTTP-01 now);
  everything else is LAN/Tailscale-only. Two switchable certresolvers → flip to Cloudflare DNS-01
  **wildcard** after the DNS migration (also what gives internal services valid certs).
- **Secrets:** gitignored `mise.local.toml` (env/Tofu/Packer) + Ansible Vault (in-playbook).
- **Migration:** a manual, discovery-based runbook (move DAS → `zpool import` → verify) — explicitly
  outside the automation "done" criteria.

## Implementation approach
12 incremental steps, each demoable and shipping its own tests: dev-env (mise) → provider auth →
`lxc_service` module + Docker-host CT → Ansible `common` → Docker/Traefik smoke → migration runbook →
Plex CT (GPU+bind+idmap) → Plex/QSV role → public Plex route → internal extras stack → Cloudflare
DNS-01 switchover → full reproducibility validation. The simple Docker-host path is proven end-to-end
before the riskier GPU/idmap work.

## Suggested next steps
1. Review `design/detailed-design.md` and `implementation/plan.md`.
2. Ensure host prereqs are ready when implementing Step 2 (API token, provider SSH user, confirm
   `getent group render video` → 993/44).
3. Perform the manual DAS/ZFS migration per the Step 6 runbook when you're ready to move media (can
   be validated with an empty `/tank/media` placeholder beforehand).
4. Start implementation from Step 1 (see the Ralph loop handoff below).

## Areas that may need further refinement
- **DAS pool name** is unknown until the enclosure is attached — the migration runbook is
  discovery-based; `/tank` is the chosen host mountpoint.
- **mise SOPS+age** is a documented future upgrade if you later want secrets encrypted-in-git
  (current choice keeps env secrets gitignored only).
- **Internal-service TLS** carries a browser warning until the Cloudflare DNS-01 wildcard (Step 11)
  is enabled — fine on LAN in the interim.
- **`vnetdmz` isolation** for the web-facing LXC was deferred — a future hardening option.
- **RAID0** has no redundancy (accepted); a future backup task should target Plex/Grafana/Kuma state
  and the media pool.
