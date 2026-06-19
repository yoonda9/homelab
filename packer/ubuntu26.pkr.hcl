// Ubuntu 26.04 Packer template (DEC-019). Cloud-image flow:
// `proxmox-clone` clones the bootstrapped `tpl-cloud-ubuntu26`
// Cloud-Init source template on the PVE node and seeds first-boot
// config via a NoCloud cidata CD attached as `additional_iso_files`
// (on-the-fly `cd_files` generation, no genisoimage pre-bake).
// The bootstrap template is owned by Step 2c (`scripts/build_template.sh`
// + `scripts/bootstrap_cloud_template.sh`).
//
// `bios`, `machine`, and `efi_config` are intentionally OMITTED from
// this source — they inherit from `tpl-cloud-ubuntu26`, which the
// bootstrap step creates with `--bios ovmf --machine q35
// --efidisk0 local-lvm:0,efitype=4m,pre-enrolled-keys=1`. Setting them
// here would either be redundant or risk conflicting with the cloned
// hardware spec (Step 1 Critic note 2).

source "proxmox-clone" "ubuntu26" {
  proxmox_url              = "https://${var.proxmox_host}:8006/api2/json"
  username                 = "${var.proxmox_user}!${var.proxmox_token_id}"
  token                    = var.proxmox_token_secret
  insecure_skip_tls_verify = true

  node                 = var.proxmox_node
  vm_id                = 9100
  template_name        = "pkr-ubuntu26"
  template_description = "Built by Packer; see scripts/build_template.sh ubuntu26"

  clone_vm   = "tpl-cloud-ubuntu26"
  full_clone = true

  cpu_type = "host"
  cores    = 2
  memory   = 2048
  os       = "l26"

  network_adapters {
    bridge = var.network_bridge
    model  = "virtio"
  }

  scsi_controller = "virtio-scsi-pci"

  # NoCloud seed for FIRST-BOOT config (user, ssh, qemu-guest-agent).
  # cloud-init finds the CD labelled "cidata" and applies its user-data.
  additional_iso_files {
    type             = "ide"
    iso_storage_pool = var.iso_storage_pool
    cd_files = [
      "${path.root}/seed/ubuntu26/user-data",
      "${path.root}/seed/ubuntu26/meta-data",
    ]
    cd_label          = "cidata"
    unmount           = true
    keep_cdrom_device = false
  }

  qemu_agent = true

  communicator = "ssh"
  ssh_username = "user"
  ssh_password = "password"
  ssh_timeout  = "30m"
}

build {
  sources = ["source.proxmox-clone.ubuntu26"]

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
