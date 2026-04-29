resource "proxmox_virtual_environment_vm" "this" {
  name      = var.name
  node_name = var.template_node
  vm_id     = var.vmid
  tags      = var.tags

  # qemu-guest-agent ships in the cloud-init templates managed by
  # ansible/roles/pve_base, so enabling the agent is safe and lets
  # Tofu read back the VM's DHCP-assigned IPs.
  agent {
    enabled = true
  }

  stop_on_destroy = true

  clone {
    vm_id = var.clone_from
  }

  cpu {
    cores = var.cores
  }

  memory {
    dedicated = var.memory
  }

  initialization {
    ip_config {
      ipv4 {
        address = "dhcp"
      }
      ipv6 {
        address = "auto"
      }
    }
  }

  network_device {
    bridge = var.bridge
  }
}
