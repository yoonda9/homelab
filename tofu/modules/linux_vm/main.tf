locals {
  # Both static_ip and gateway must be set together. The precondition
  # below fails plan when exactly one is null, so this branch is only
  # reached for the both-set or both-null cases.
  use_static_ip = var.static_ip != null && var.gateway != null

  # Cloud-init user-data dropped via a snippets file. Two purposes:
  # 1. Drop a sudoers.d entry granting passwordless sudo to the %sudo
  #    group, so Ansible's `become: true` works without prompting for
  #    var.default_password (which is sensitive and not interactively
  #    available during `ansible-playbook` runs).
  # 2. Ensure default_user lands in the sudo group. The cloud-init
  #    `user_account` block already creates the user and seeds the SSH
  #    keys; this `users:` stanza appends sudo membership without
  #    discarding the rest of the cloud image's defaults.
  user_data_yaml = <<-EOT
    #cloud-config
    users:
      - default
      - name: ${var.default_user}
        groups: [sudo]
        shell: /bin/bash
    write_files:
      - path: /etc/sudoers.d/90-${var.default_user}-nopasswd
        owner: root:root
        permissions: '0440'
        content: |
          %sudo ALL=(ALL) NOPASSWD:ALL
  EOT
}

resource "proxmox_virtual_environment_file" "user_data" {
  content_type = "snippets"
  datastore_id = "local"
  node_name    = var.template_node

  source_raw {
    data      = local.user_data_yaml
    file_name = "${var.name}-user-data.yaml"
  }
}

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

  disk {
    interface    = "scsi0"
    datastore_id = "local-lvm"
    size         = var.disk_gb
    discard      = "on"
    ssd          = true
  }

  initialization {
    user_account {
      username = var.default_user
      password = var.default_password
      keys     = var.ssh_authorized_keys
    }

    user_data_file_id = proxmox_virtual_environment_file.user_data.id

    ip_config {
      ipv4 {
        address = local.use_static_ip ? var.static_ip : "dhcp"
        gateway = local.use_static_ip ? var.gateway : null
      }
      ipv6 {
        address = "auto"
      }
    }
  }

  network_device {
    bridge = var.bridge
  }

  lifecycle {
    precondition {
      condition = (var.static_ip == null) == (var.gateway == null)
      error_message = join(" ", [
        "var.static_ip and var.gateway must be set together (both or neither).",
        "Got static_ip=${var.static_ip == null ? "null" : "<set>"},",
        "gateway=${var.gateway == null ? "null" : "<set>"}.",
      ])
    }
  }
}
