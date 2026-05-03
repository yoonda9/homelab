packer {
  required_plugins {
    proxmox = {
      version = "~> 1.2"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

variable "proxmox_host" {
  type = string
}

variable "proxmox_user" {
  type = string
}

variable "proxmox_token_id" {
  type = string
}

variable "proxmox_token_secret" {
  type      = string
  sensitive = true
}

variable "proxmox_node" {
  type    = string
  default = "pve"
}

variable "storage_pool" {
  type    = string
  default = "local-lvm"
}

variable "iso_storage_pool" {
  type    = string
  default = "local"
}

variable "network_bridge" {
  type    = string
  default = "vmbr0"
}

source "proxmox-iso" "ubuntu26" {
  proxmox_url              = "https://${var.proxmox_host}:8006/api2/json"
  username                 = "${var.proxmox_user}!${var.proxmox_token_id}"
  token                    = var.proxmox_token_secret
  insecure_skip_tls_verify = true

  node                 = var.proxmox_node
  vm_id                = 9100
  template_name        = "pkr-ubuntu26"
  template_description = "Built by Packer; see scripts/build_template.sh ubuntu26"
  force                = true

  bios     = "ovmf"
  machine  = "q35"
  cpu_type = "host"
  cores    = 2
  memory   = 2048

  efi_config {
    efi_storage_pool  = "local-lvm"
    efi_type          = "4m"
    pre_enrolled_keys = true
  }

  network_adapters {
    bridge = var.network_bridge
    model  = "virtio"
  }

  scsi_controller = "virtio-scsi-pci"
  disks {
    type         = "scsi"
    storage_pool = var.storage_pool
    disk_size    = "32G"
    format       = "raw"
  }

  boot_iso {
    type              = "scsi"
    iso_url           = "https://cloud-images.ubuntu.com/releases/26.04/release/ubuntu-26.04-server-cloudimg-amd64.img"
    iso_checksum      = "file:https://cloud-images.ubuntu.com/releases/26.04/release/SHA256SUMS"
    iso_storage_pool  = var.iso_storage_pool
    unmount           = true
    keep_cdrom_device = false
  }

  http_directory = "http/ubuntu26"
  boot_command = [
    "<esc><wait>",
    "linux /casper/vmlinuz autoinstall ds=nocloud-net;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ ---<enter>",
    "initrd /casper/initrd<enter>",
    "boot<enter>",
  ]
  boot_wait = "10s"

  communicator = "ssh"
  ssh_username = "user"
  ssh_password = "password"
  ssh_timeout  = "30m"
}

build {
  sources = ["source.proxmox-iso.ubuntu26"]

  # Floor verification (C-3): user, sshd, python already in cloud image.
  provisioner "shell" {
    inline = [
      "set -eu",
      "id user || (echo 'FAIL: user missing'; exit 1)",
      "command -v python3 || (echo 'FAIL: python3 missing'; exit 1)",
      "systemctl is-enabled ssh || sudo systemctl enable ssh",
    ]
  }

  # Last-provisioner seal (C-8): cloud-init clean + machine-id truncate
  # + ssh host keys removal so per-clone identity regens at first boot.
  provisioner "shell" {
    inline = [
      "set -eu",
      "sudo cloud-init clean --logs --seed",
      "sudo truncate -s 0 /etc/machine-id",
      "[ -f /var/lib/dbus/machine-id ] && sudo truncate -s 0 /var/lib/dbus/machine-id || true",
      "sudo rm -f /etc/ssh/ssh_host_*",
      "sudo sync",
    ]
  }
}
