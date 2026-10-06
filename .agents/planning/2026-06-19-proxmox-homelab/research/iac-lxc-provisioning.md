# Research: Provisioning the Plex LXC with bpg/proxmox (OpenTofu)

_Sources: bpg/proxmox provider docs + CHANGELOG (verified 2026-06-19). Repo already pins
`bpg/proxmox ~> 0.104` (latest release line is 0.110.x), OpenTofu ≥ 1.6._

## Resource: `proxmox_virtual_environment_container`

The existing repo uses `proxmox_virtual_environment_vm` (clone-based). LXCs use the sibling
**`proxmox_virtual_environment_container`**. Key blocks for our needs:

### `device_passthrough` — /dev/dri for QSV (maps to Proxmox `dev0:` ...)
Repeatable block. Arguments:
- `path` **(required)** — e.g. `/dev/dri/renderD128`
- `mode` (opt) — 4-digit octal string, e.g. `"0660"`
- `uid` / `gid` (opt) — ownership of the device node **as seen inside the container**
- `deny_write` (opt, default false)

Works for **unprivileged** containers (the primary use case). Introduced in **v0.70.0**, a
create-time bug fixed in **v0.70.1** → our `~>0.104` is safe. This maps to Proxmox's modern
`dev0:` passthrough, which auto-wires host↔container ID translation (cleaner than raw
`lxc.mount.entry` + `lxc.cgroup2.devices.allow`).

### `mount_point` — bind-mount the DAS media path
Repeatable block. Arguments:
- `volume` **(required)** — an **absolute host path (e.g. `/tank/media`) → bind mount**
  (other forms: storage ID = new volume; full volume ID = existing volume)
- `path` **(required)** — mount path inside the container
- `size` (only for volume-backed), `read_only`, `backup` (default false), `acl`, `quota`,
  `replicate`, `shared`, `mount_options` (list)
- ⚠️ A **bind mount of a host path requires `root@pam` auth** on the provider connection.

### `unprivileged` + `features`
- `unprivileged` (bool, **default `false`** → privileged by default; set **`true`**).
- `features { nesting, fuse, keyctl, mknod, mount=[...] }`. `nesting=true` recommended
  (needed for Docker-in-LXC etc.); changing any feature except `nesting` needs `root@pam`.

### `idmap` — map host render/video GID into an unprivileged container
Repeatable block: `type` (`uid`|`gid`), `container_id`, `host_id`, `size` (all required).
The provider writes these as `lxc.idmap` lines **via SSH** (the PVE API can't write `lxc.*`),
so the provider must also have **SSH access to the node** configured (in addition to the API
token). idmap-on-first-boot reliability improved in **v0.108.0** → if we lean on idmap at
create time, **pin `>= 0.108.0`** within `~>0.104`.

### `operating_system` + `initialization`
- `operating_system { template_file_id = "local:vztmpl/<file>", type = "debian"|"ubuntu" }`
  (can reference a `proxmox_virtual_environment_download_file` resource).
- `initialization { hostname, dns { domain, servers=[...] }, ip_config { ipv4 { address =
  "192.168.1.x/24", gateway = "192.168.1.1" } }, user_account { keys=[...] } }`.
- `network_interface { name = "veth0", bridge = "vmbr0" }`.

## GID strategy for THIS host (ground truth)

> The web research assumed host render GID ≈ 104. **We OBSERVED on `pve`:
> `render:x:993` and `video:x:44`.** So on this host the **host render GID is 993**, video 44.
> Confirm again before apply: `getent group render video` and `ls -n /dev/dri/renderD128`.

Two viable approaches (decide in design):
1. **Privileged LXC (simplest):** GIDs match host 1:1. Put `plex` in a group with GID 993
   (render) + 44 (video); `device_passthrough { path=.../renderD128, gid=993 }`. No idmap.
   Trade-off: weaker isolation.
2. **Unprivileged LXC (recommended for safety):** use `device_passthrough` with `gid` set to
   the **container-side** render GID, plus `idmap` gid entries that punch host 993 and 44
   straight through (rest of GID space offset by +100000). More config; needs provider SSH +
   `>=0.108.0`. Same approach handles the DAS bind-mount ownership (or chown the host dir to
   the mapped UID/GID).

> Note on the PVE-9 + AppArmor 4.1 quirk: `intel_gpu_top` *monitoring* fails inside an
> unprivileged LXC, but **transcoding still works** — run `intel_gpu_top` on the host instead.
> Do **not** "fix" it with `lxc.apparmor.profile: unconfined`.

## Minimal HCL skeleton (to be turned into a module `tofu/modules/lxc_service` or `plex_lxc`)

```hcl
resource "proxmox_virtual_environment_container" "plex" {
  node_name    = "pve"
  vm_id        = 110            # free range 110-119 (100-103/9000-9001/9100-9101 used)
  unprivileged = true

  features { nesting = true }

  operating_system {
    template_file_id = "local:vztmpl/debian-13-standard_*.tar.zst"
    type             = "debian"
  }

  cpu    { cores = 6 }
  memory { dedicated = 4096, swap = 512 }
  disk   { datastore_id = "local-lvm", size = 16 }

  initialization {
    hostname = "plex"
    ip_config { ipv4 { address = "192.168.1.110/24", gateway = "192.168.1.1" } }
    dns       { domain = "yoonnation.com", servers = ["192.168.1.1"] }
    user_account { keys = [trimspace(file("~/.ssh/id_ed25519.pub"))] }
  }

  network_interface { name = "veth0", bridge = "vmbr0" }

  device_passthrough { path = "/dev/dri/renderD128", gid = 993, mode = "0660" }
  device_passthrough { path = "/dev/dri/card1",      gid = 44,  mode = "0660" }

  mount_point { volume = "/tank/media", path = "/media", read_only = false }

  # idmap blocks here if unprivileged (punch GID 993 + 44 through to host) — see above
  started = true
}
```
_(`card1` not `card0` on this host — observed. Confirm device names at apply time.)_

## Provider auth requirements summary (must satisfy all)
- **API token** (`root@pam!ansible-token`) — already exists.
- **`root@pam`** auth — required for bind mounts + non-nesting feature flags.
- **SSH to the node** — required for `idmap`. Provider `ssh {}` block / `PROXMOX_VE_SSH_*`.

## Open design decisions fed by this research
- **Privileged vs unprivileged** Plex LXC (recommend unprivileged + idmap; fall back to
  privileged if idmap proves fiddly).
- **Pin provider `>= 0.108.0`** (still `~>0.104`-compatible) for reliable create-time idmap.
- Whether to build a **generic `lxc_service` module** (reused for Plex + the Docker-host LXC)
  vs a Plex-specific module. Leans generic, matching the repo's `dev_vm` precedent.

## URLs
- Container resource: https://registry.terraform.io/providers/bpg/proxmox/latest/docs/resources/virtual_environment_container
- Raw docs: https://github.com/bpg/terraform-provider-proxmox/blob/main/docs/resources/virtual_environment_container.md
- CHANGELOG: https://github.com/bpg/terraform-provider-proxmox/blob/main/CHANGELOG.md
