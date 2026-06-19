locals {
  # Combine the GID/UID idmap lists into the provider's flat idmap block shape,
  # tagging each with its required `type` ("g" / "u"). Empty inputs yield an
  # empty list, so the dynamic "idmap" block below renders nothing for a plain
  # CT. Step 7 generates the gap-free tiling that fills gid_maps/uid_maps.
  idmap_entries = concat(
    [for m in var.gid_maps : {
      type         = "g"
      container_id = m.container_id
      host_id      = m.host_id
      size         = m.size
    }],
    [for m in var.uid_maps : {
      type         = "u"
      container_id = m.container_id
      host_id      = m.host_id
      size         = m.size
    }],
  )
}

resource "proxmox_virtual_environment_container" "this" {
  node_name     = var.node
  vm_id         = var.vm_id
  unprivileged  = var.unprivileged
  start_on_boot = var.start_on_boot

  features {
    nesting = var.nesting
  }

  cpu {
    cores = var.cores
  }

  memory {
    dedicated = var.memory_mb
  }

  disk {
    datastore_id = var.datastore_id
    size         = var.disk_gb
  }

  operating_system {
    template_file_id = var.template_file_id
    type             = "debian"
  }

  network_interface {
    name   = "eth0"
    bridge = var.bridge
  }

  initialization {
    hostname = var.name

    ip_config {
      ipv4 {
        address = var.ip_cidr
        gateway = var.gateway
      }
    }

    user_account {
      keys = var.ssh_public_keys
    }
  }

  # --- Optional capabilities. Each renders ONLY when its list var is non-empty
  # (docker-host sets none → these emit nothing). Populated in Step 7. ---

  dynamic "device_passthrough" {
    for_each = var.device_passthroughs
    content {
      path = device_passthrough.value.path
      gid  = device_passthrough.value.gid
      mode = device_passthrough.value.mode
    }
  }

  dynamic "mount_point" {
    for_each = var.bind_mounts
    content {
      volume    = mount_point.value.host_path
      path      = mount_point.value.ct_path
      read_only = mount_point.value.read_only
    }
  }

  dynamic "idmap" {
    for_each = local.idmap_entries
    content {
      type         = idmap.value.type
      container_id = idmap.value.container_id
      host_id      = idmap.value.host_id
      size         = idmap.value.size
    }
  }
}
