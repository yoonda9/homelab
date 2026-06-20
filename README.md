# Home Lab Auto Deploy

Provisions a homelab Proxmox VE node and the [core services](#core-services)
that run on top of it.

## Packer templates (Proxmox VE)

Three VM templates are built from cloud images on the PVE node:

- `pkr-ubuntu26` (vmid 9100) — Ubuntu 26.04 server cloud image, built via
  `proxmox-clone` from a one-time `tpl-cloud-ubuntu26` source template.
- `pkr-fedora-workstation` (vmid 9101) — Fedora 44 Cloud Base, built via
  `proxmox-clone` from `tpl-cloud-fedora44` with workstation packages
  layered on at provision time.
- `pkr-windows11` (vmid 9102) — Windows 11 24H2, built via `proxmox-iso`
  with sysprep + autounattend (Windows has no cloud image).

The Linux templates take their first-boot config (user, ssh key,
qemu-guest-agent) from a NoCloud cloud-init seed pre-baked locally with
`genisoimage -volid cidata` and attached as an additional ISO. No
keystroke timing, no installer boot menus.

### Prerequisites

- [`mise`](https://mise.jdx.dev) for the toolchain and env. Run `mise install`
  to provision Packer/OpenTofu/Python/Ansible/[`just`](https://just.systems) (the
  task runner — `just <recipe>` drives plan/apply/play/gen-inventory/test), then
  copy the secrets template:
  `cp mise.local.toml.example mise.local.toml` and fill it in. mise exports the
  four PVE API credentials Packer needs — `PROXMOX_HOST`, `PROXMOX_USER`,
  `PROXMOX_TOKEN_ID`, `PROXMOX_TOKEN_SECRET` — from the gitignored
  `mise.local.toml`.
- `genisoimage` for building the cidata seed ISO.
- For the two Linux templates, run the one-time bootstrap that downloads
  the upstream cloud image and registers it as a PVE source template:

  ```bash
  bash scripts/bootstrap_cloud_template.sh ubuntu26   # → tpl-cloud-ubuntu26
  bash scripts/bootstrap_cloud_template.sh fedora     # → tpl-cloud-fedora44
  ```

  The bootstrap is idempotent — re-running it is a no-op once the source
  template exists. `pkr-windows11` doesn't need it.

### Quickstart

```bash
bash scripts/build_template.sh ubuntu26      # → pkr-ubuntu26
bash scripts/build_template.sh fedora        # → pkr-fedora-workstation
bash scripts/build_template.sh windows11     # → pkr-windows11
```

Each invocation runs `packer init`, bakes the per-OS seed ISO when
applicable, and then `packer build -force -only=<source>.<key> packer/`.

## Core Services

### Reverse Proxy

### Media

#### Plex

#### Calibre

### Metrics & Monitoring

#### Grafana

### Pi Hole

### Bitwarden
