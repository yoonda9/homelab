resource "proxmox_virtual_environment_vm" "dev_vm" {
  name      = var.name
  node_name = var.node

  clone {
    vm_id = var.template_id
    full  = true
  }

  cpu {
    cores = var.cores
  }

  memory {
    dedicated = var.memory_mb
  }

  disk {
    interface    = "scsi0"
    datastore_id = var.datastore_id
    size         = var.disk_gb
    discard      = "on"
    ssd          = true
  }

  network_device {
    bridge = var.bridge
  }

  agent {
    enabled = true
  }

  # Sole purpose: trigger PVE per-clone cidata regeneration so each
  # clone boots with a fresh local-hostname (= var.name on Linux) and
  # instance-id. No user_account / user_data_file_id — credentials
  # are baked into the template at install time per C-6, and per-clone
  # OS-level identity reset is the template's seal step (C-8). Per Q6/A6
  # this module is intentionally bare.
  initialization {
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  stop_on_destroy = true
}
