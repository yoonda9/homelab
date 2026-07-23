# tofu/modules/lxc_service

Generic, reusable module wrapping `proxmox_virtual_environment_container`. It
provisions an unprivileged LXC (the `unprivileged` default `true` is the
fallback switch per R2) with optional GPU/device passthrough, host bind mounts,
and an idmap — all driven by list variables that default to empty.

It is the single module behind every service CT: the plain docker-host CT
(Step 3) and the GPU/media Plex CT (Step 7).

## Example — docker-host CT 111 (plain, no passthrough/bind/idmap)

    module "docker_host" {
      source           = "./modules/lxc_service"
      name             = "docker-host"
      vm_id            = local.service_ids.docker_host
      ip_cidr          = local.net.docker_host_cidr
      gateway          = local.net.gateway
      bridge           = local.net.bridge
      dns_servers      = local.net.dns_servers
      dns_domain       = local.net.dns_domain
      template_file_id = proxmox_download_file.debian13_lxc.id
      nesting          = true
    }

## Notes

- `device_passthroughs`, `bind_mounts`, `gid_maps`, and `uid_maps` all default
  to `[]`. With empty lists the matching `device_passthrough{}`,
  `mount_point{}`, and `idmap{}` blocks render **nothing** — docker-host uses
  none. Step 7 populates them for the Plex CT (renderD128 gid 993 + card1 gid
  44 passthrough, `/tank/Media`→`/media` bind, gap-free idmap tiling).
- `dns_servers` (list, default `[]`) and `dns_domain` (string, default `""`)
  populate `initialization.dns` and must be set for every real CT. Left empty,
  PVE writes no `nameserver:`/`searchdomain:` key and copies the **PVE host's**
  `/etc/resolv.conf` into the container instead — and that file is owned by
  Tailscale (`nameserver 100.100.100.100`, MagicDNS), which is unroutable from a
  non-tailnet CT. Every lookup then hangs and `apt update` fails, while SSH keeps
  working because the Ansible inventory uses raw IPs. This broke CT 110 on
  2026-07-23. Uses the provider's `servers` list, not the deprecated singular
  `server`. See `docs/runbooks/tailscale-split-dns.md`.
- Bind mounts require the provider to authenticate as `root@pam`; the idmap
  requires provider SSH (`ssh { agent = true }` in the root `providers.tf`).
- `gid_maps`/`uid_maps` are merged into the provider's flat `idmap` blocks with
  the required `type` (`g`/`u`) added automatically.
