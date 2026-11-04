resource "proxmox_virtual_environment_vm" "dev_vm" {
  name      = var.name
  node_name = var.node
  vm_id     = var.vm_id

  clone {
    vm_id = var.template_id
    full  = true
  }

  cpu {
    cores = var.cores
    type  = var.cpu_type
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
    bridge   = var.bridge
    firewall = var.firewall
  }

  agent {
    enabled = true
  }

  # Always present so PVE regenerates per-clone cidata (fresh
  # local-hostname = var.name, fresh instance-id). The consumer inputs
  # are all optional: with none set this is DHCP and no credentials,
  # exactly the bare-template behaviour (C-6/C-8).
  initialization {
    ip_config {
      ipv4 {
        address = var.ipv4_cidr == "" ? "dhcp" : var.ipv4_cidr
        gateway = var.ipv4_cidr == "" ? null : var.ipv4_gateway
      }
    }

    dynamic "user_account" {
      for_each = length(var.ssh_public_keys) > 0 ? [1] : []
      content {
        username = var.ssh_username
        keys     = var.ssh_public_keys
      }
    }

    dynamic "dns" {
      for_each = length(var.dns_servers) > 0 || var.dns_domain != "" ? [1] : []
      content {
        servers = var.dns_servers
        domain  = var.dns_domain == "" ? null : var.dns_domain
      }
    }
  }

  stop_on_destroy = true
}
