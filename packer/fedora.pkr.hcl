source "proxmox-iso" "fedora" {
  proxmox_url              = "https://${var.proxmox_host}:8006/api2/json"
  username                 = "${var.proxmox_user}!${var.proxmox_token_id}"
  token                    = var.proxmox_token_secret
  insecure_skip_tls_verify = true

  node                 = var.proxmox_node
  vm_id                = 9101
  template_name        = "pkr-fedora-workstation"
  template_description = "Built by Packer; see scripts/build_template.sh fedora"

  bios     = "ovmf"
  machine  = "q35"
  cpu_type = "host"
  cores    = 2
  memory   = 4096

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
    type              = "sata"
    iso_url           = "https://download.fedoraproject.org/pub/fedora/linux/releases/43/Workstation/x86_64/iso/Fedora-Workstation-Live-43-1.6.x86_64.iso"
    iso_checksum      = "file:https://download.fedoraproject.org/pub/fedora/linux/releases/43/Workstation/x86_64/iso/Fedora-Workstation-43-1.6-x86_64-CHECKSUM"
    iso_storage_pool  = var.iso_storage_pool
    unmount           = true
    keep_cdrom_device = false
  }

  http_directory = "http/fedora"
  boot_command = [
    "<wait5><tab><end> inst.ks=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ks.cfg<enter>",
  ]
  boot_wait = "10s"

  communicator = "ssh"
  ssh_username = "user"
  ssh_password = "password"
  ssh_timeout  = "30m"
}

build {
  sources = ["source.proxmox-iso.fedora"]

  # Defensive cloud-init install BEFORE seal (C-8 Fedora addendum):
  # kickstart adds it via %packages, but a re-install covers operator
  # overrides and is required by test_pkr_seal_step.assert_fedora_dnf_install.
  provisioner "shell" {
    inline = [
      "set -eu",
      "sudo dnf install -y cloud-init cloud-utils-growpart",
      "id user || (echo 'FAIL: user missing'; exit 1)",
      "command -v python3 || (echo 'FAIL: python3 missing'; exit 1)",
      "systemctl is-enabled sshd || sudo systemctl enable sshd",
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
