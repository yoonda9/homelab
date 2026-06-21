# Debian 13 (trixie) standard LXC template, downloaded from code so the CT
# fleet is reproducible without a manual `pveam` step. content_type "vztmpl"
# lands it in the `local` datastore's template store; its `.id`
# ("local:vztmpl/<file_name>") feeds the lxc_service module.
#
# Manual alternative (equivalent, if you prefer pulling from the PVE mirror):
#   pveam update && pveam available --section system | grep debian-13-standard
#   pveam download local debian-13-standard_13.1-2_amd64.tar.zst
# then pass "local:vztmpl/debian-13-standard_13.1-2_amd64.tar.zst" directly.
resource "proxmox_download_file" "debian13_lxc" {
  node_name    = "pve"
  datastore_id = "local"
  content_type = "vztmpl"
  file_name    = "debian-13-standard_13.1-2_amd64.tar.zst"
  url          = "http://download.proxmox.com/images/system/debian-13-standard_13.1-2_amd64.tar.zst"
}

# docker-host CT 111 — the simple end-to-end consumer of lxc_service: an
# unprivileged container with nesting enabled (to run Docker) and no GPU
# passthrough / bind mounts / idmap (those empty defaults render nothing). The
# GPU/media Plex CT 110 is added in Step 7 against this same module.
module "docker_host" {
  source = "./modules/lxc_service"

  name             = "docker-host"
  vm_id            = local.service_ids.docker_host
  ip_cidr          = local.net.docker_host_cidr
  gateway          = local.net.gateway
  bridge           = local.net.bridge
  template_file_id = proxmox_download_file.debian13_lxc.id
  nesting          = true
}

# Plex CT 110 — the GPU/media consumer of lxc_service. Unprivileged, with the
# Intel iGPU /dev/dri nodes passed through (renderD128 gid render, card1 gid
# video — GIDs sourced from local.host_gids so they live in one place), the
# /tank/media DAS bind-mounted read-only at /media, and the gap-free idmap
# tiling (local.plex_gid_maps/plex_uid_maps) that punches host GIDs 993/44 1:1
# so the unprivileged CT can open the render nodes and read the media.
#
# Fallback (design §6): if the unprivileged idmap fights GPU/DAS access at
# apply time, flip unprivileged = false and re-apply — see the idmap fallback
# note in docs/runbooks/das-zfs-migration.md.
module "plex" {
  source = "./modules/lxc_service"

  name             = "plex"
  vm_id            = local.service_ids.plex
  ip_cidr          = local.net.plex_cidr
  gateway          = local.net.gateway
  bridge           = local.net.bridge
  template_file_id = proxmox_download_file.debian13_lxc.id
  unprivileged     = true
  # The Debian 13 template ships systemd 257, which hangs on first boot in an
  # unprivileged CT without nesting (Proxmox warns "Systemd 257 detected. You
  # may need to enable nesting") — the create's vzreboot step then times out and
  # the CT is left tainted. Mirror docker_host's nesting=true so the boot
  # completes. (docker_host, also unprivileged+systemd 257, is the control.)
  nesting   = true
  cores     = 6
  memory_mb = 4096

  device_passthroughs = [
    {
      path = "/dev/dri/renderD128"
      gid  = local.host_gids.render
      mode = "0660"
    },
    {
      path = "/dev/dri/card1"
      gid  = local.host_gids.video
      mode = "0660"
    },
  ]

  bind_mounts = [
    {
      host_path = "/tank/media"
      ct_path   = "/media"
      read_only = true
    },
  ]

  gid_maps = local.plex_gid_maps
  uid_maps = local.plex_uid_maps
}
