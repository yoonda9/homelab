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
  # Running Docker in an UNPRIVILEGED LXC needs BOTH nesting=1 AND keyctl=1.
  # Without keyctl, dockerd/containerd cannot manage the kernel keyring, so the
  # Docker daemon/API is impaired and Traefik's docker provider registers ZERO
  # *@docker routers — every dashboard host then 404s while plex@file (file
  # provider) still serves. tfstate had keyctl:false. (DEBUG.md Traefik 404.)
  keyctl = true
  # Inject the operator SSH key so root@docker-host has an authorized_keys entry;
  # otherwise Ansible's root SSH login is denied (DEBUG.md). See tofu/variables.tf.
  ssh_public_keys = local.operator_ssh_keys
}

# Plex CT 110 — the GPU/media consumer of lxc_service. Unprivileged, with the
# Intel iGPU /dev/dri nodes passed through (renderD128 gid render, card1 gid
# video — GIDs sourced from local.host_gids so they live in one place), the
# /tank/Media DAS bind-mounted read-only at /media, the Plex state dir
# bind-mounted read-write from /tank/Server/AppData/plex so it survives CT
# rebuilds, the /mnt/xtra-one and /mnt/xtra-two USB drives bound through
# read-only at their host paths (usb-media-mounts.md), and the gap-free idmap
# tiling (local.plex_gid_maps/plex_uid_maps)
# that punches host GIDs 993/44 1:1 so the unprivileged CT can open the render
# nodes and read the media.
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
      host_path = "/tank/Media"
      ct_path   = "/media"
      read_only = true
    },
    # Plex state — Preferences.xml (claim token + machine identity), library DB,
    # metadata — lives on host storage so a CT destroy/recreate comes back
    # claimed with libraries intact; without this, every rebuild means re-running
    # the claim wizard and re-scanning. Host path is a plain subdirectory of the
    # DASPool/Server/AppData dataset (DASPool mounts at /tank). Ownership must be
    # the in-CT plex uid/gid +100000 (the uid map is a single offset tile) — see
    # docs/runbooks/plex-claim.md §5 for the chown procedure and cutover order.
    {
      host_path = "/tank/Server/AppData/plex"
      ct_path   = "/var/lib/plexmediaserver"
      read_only = false
    },
    # USB media drives — host fstab automounts (see
    # docs/runbooks/usb-media-mounts.md), bound through at the same path so
    # CT-side Plex library paths match the host. Deliberately bound at the
    # mount root: if a drive is absent at boot (fstab nofail), the CT starts
    # with an empty directory here rather than failing loudly — re-scan only
    # after confirming the drive is mounted (runbook §4 tradeoff).
    {
      host_path = "/mnt/xtra-one"
      ct_path   = "/mnt/xtra-one"
      read_only = true
    },
    {
      host_path = "/mnt/xtra-two"
      ct_path   = "/mnt/xtra-two"
      read_only = true
    },
  ]

  gid_maps = local.plex_gid_maps
  uid_maps = local.plex_uid_maps

  # Same operator SSH key as docker_host so root@plex is reachable by Ansible
  # (without it user_account.keys=[] and root SSH is denied — DEBUG.md).
  ssh_public_keys = local.operator_ssh_keys
}
