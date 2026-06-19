locals {
  # template_ids — authoritative VM-ID map for the three Packer-built
  # templates. Each key is the short-name passed to the dev_vm module's
  # `os` variable and to scripts/build_template.sh. The values are the
  # stable PVE VM-IDs reserved for this pipeline (clause #1 boundary
  # via the 9100–9102 range and the pkr- name prefix).
  template_ids = {
    ubuntu26 = 9100
    fedora   = 9101
    win11    = 9102
  }

  # service_ids — stable PVE VM-IDs for the service LXCs provisioned via the
  # lxc_service module. Plex (110) lands in Step 7; docker-host (111) in Step 3.
  service_ids = {
    plex        = 110
    docker_host = 111
  }

  # net — homelab L3 facts shared by every service CT: the gateway/bridge plus
  # the per-service static CIDRs (.110 plex, .111 docker-host).
  net = {
    gateway          = "192.168.1.1"
    bridge           = "vmbr0"
    plex_cidr        = "192.168.1.110/24"
    docker_host_cidr = "192.168.1.111/24"
  }

  # host_gids — render/video group GIDs as they exist on `pve` (verified via
  # `getent group render video` on 2026-06-19, design §5.1). Step 7 consumes
  # these to punch GPU device GIDs 1:1 through the unprivileged Plex CT's idmap.
  host_gids = {
    render = 993
    video  = 44
  }
}

locals {
  # --- Unprivileged idmap tiling for the Plex CT (design §5.1/§5.3) ----------
  # Default unprivileged map is container 0..65535 -> host 100000..165535. To
  # let the CT open the GPU render nodes and read the DAS, each host GID in
  # local.host_gids (993 render, 44 video) is punched through 1:1. That means
  # splitting the gid map into contiguous tiles: offset tiles keep the +100000
  # shift, size-1 punch tiles map gid g -> host gid g. The tiling is GENERATED
  # by folding over the sorted GIDs, so the literals live only in host_gids —
  # add a GID there and the tiling regenerates (no hand-enumerated tiles).
  idmap_uid_offset = 100000
  idmap_id_space   = 65536

  # Host GIDs to punch, sorted ascending. Zero-pad before sort() (lexicographic)
  # so the ordering is numeric, then back to numbers.
  idmap_punch_gids = [
    for s in sort([for g in values(local.host_gids) : format("%06d", g)]) : tonumber(s)
  ]

  # For each punch GID emit the offset tile leading up to it (from the previous
  # punch's end, or 0) plus the 1:1 punch tile.
  idmap_gid_pairs = flatten([
    for i, g in local.idmap_punch_gids : [
      {
        container_id = i == 0 ? 0 : local.idmap_punch_gids[i - 1] + 1
        host_id      = local.idmap_uid_offset + (i == 0 ? 0 : local.idmap_punch_gids[i - 1] + 1)
        size         = g - (i == 0 ? 0 : local.idmap_punch_gids[i - 1] + 1)
      },
      {
        container_id = g
        host_id      = g
        size         = 1
      },
    ]
  ])

  # Trailing offset tile from the last punch's end to the top of the id space.
  idmap_gid_tail = [{
    container_id = local.idmap_punch_gids[length(local.idmap_punch_gids) - 1] + 1
    host_id      = local.idmap_uid_offset + local.idmap_punch_gids[length(local.idmap_punch_gids) - 1] + 1
    size         = local.idmap_id_space - (local.idmap_punch_gids[length(local.idmap_punch_gids) - 1] + 1)
  }]

  # Gap-free gid tiling: offset+punch pairs then the trailing offset, dropping
  # any zero-size offset tile (adjacent GIDs). Adjacency still holds when a
  # zero-size tile is dropped, so the map stays contiguous over 0..65536.
  plex_gid_maps = [
    for t in concat(local.idmap_gid_pairs, local.idmap_gid_tail) : t if t.size > 0
  ]

  # The uid map needs no punches: one full-offset tile covering the id space.
  plex_uid_maps = [{
    container_id = 0
    host_id      = local.idmap_uid_offset
    size         = local.idmap_id_space
  }]
}
