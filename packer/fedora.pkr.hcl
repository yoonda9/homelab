// Fedora Packer template (DEC-019 Q4). Cloud-image flow:
// `proxmox-clone` clones the bootstrapped `tpl-cloud-fedora44`
// Cloud-Init source template on the PVE node and seeds first-boot
// config via a NoCloud cidata CD attached as `additional_iso_files`
// (on-the-fly `cd_files` generation, no genisoimage pre-bake).
// Source template `tpl-cloud-fedora44` is bootstrapped by Step 3c
// (`scripts/bootstrap_cloud_template.sh fedora`) from the Fedora 44
// Cloud Base generic qcow2; the Workstation group install runs in a
// Packer shell provisioner below so the template literal stays
// `pkr-fedora-workstation` per DEC-019 Q4.
//
// `bios`, `machine`, and `efi_config` are intentionally OMITTED from
// this source — they inherit from `tpl-cloud-fedora44`, which the
// bootstrap step creates with `--bios ovmf --machine q35
// --efidisk0 local-lvm:0,efitype=4m,pre-enrolled-keys=1`. Setting them
// here would either be redundant or risk conflicting with the cloned
// hardware spec (Step 1 Critic note 2 carry-forward, mirrors ubuntu26).
//
// The installer surface (boot ISO, install disks, boot keystrokes,
// HTTP-served kickstart, boot wait) is dropped entirely: cloud images
// skip that phase and the disk is inherited from the cloned source
// template.

source "proxmox-clone" "fedora" {
  proxmox_url              = "https://${var.proxmox_host}:8006/api2/json"
  username                 = "${var.proxmox_user}!${var.proxmox_token_id}"
  token                    = var.proxmox_token_secret
  insecure_skip_tls_verify = true

  node                 = var.proxmox_node
  vm_id                = 9101
  template_name        = "pkr-fedora-workstation"
  template_description = "Built by Packer; see scripts/build_template.sh fedora"

  clone_vm   = "tpl-cloud-fedora44"
  full_clone = true

  cpu_type = "host"
  cores    = 2
  memory   = 4096
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
      "${path.root}/seed/fedora/user-data",
      "${path.root}/seed/fedora/meta-data",
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
  sources = ["source.proxmox-clone.fedora"]

  # Floor verification (C-3): user, sshd, python already in cloud image.
  # Fedora unit name is `sshd` (not `ssh` like Ubuntu).
  provisioner "shell" {
    inline = [
      "set -eu",
      "id user || (echo 'FAIL: user missing'; exit 1)",
      "command -v python3 || (echo 'FAIL: python3 missing'; exit 1)",
      "systemctl is-enabled sshd || sudo systemctl enable sshd",
    ]
  }

  # Workstation packages (DEC-010 / DEC-019 Q4): cloud image is Fedora
  # Cloud Base, so the Workstation desktop group is installed here to
  # satisfy the `pkr-fedora-workstation` template_name. The verbatim
  # `dnf install -y cloud-init cloud-utils-growpart` line is required by
  # `assert_fedora_dnf_install` in scripts/test_pkr_seal_step.py
  # (defensive re-install also covers operator overrides on the source
  # template).
  provisioner "shell" {
    inline = [
      "set -eu",
      "sudo dnf install -y cloud-init cloud-utils-growpart",
      "sudo dnf install -y @workstation-product-environment",
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
