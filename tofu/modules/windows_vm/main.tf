# Per-VM autounattend.xml rendered from the module-local template. Lands
# under build/<name>-autounattend.xml so the genisoimage step has a
# deterministic input path (build/ is gitignored — see .gitignore).
resource "local_file" "autounattend" {
  filename = "${path.module}/build/${var.name}-autounattend.xml"
  content = templatefile(
    "${path.module}/templates/autounattend.xml.tftpl",
    {
      name                = var.name
      default_user        = var.default_user
      default_password    = var.default_password
      ssh_authorized_keys = var.ssh_authorized_keys
    }
  )
}

# Bake the rendered XML into a per-VM ISO. Windows Setup discovers
# autounattend.xml on any attached removable media at the root, so a
# Joliet+Rock-Ridge-friendly ISO with volume label AUTOUNATTEND is the
# canonical shape. The triggers map keys on the rendered XML's md5 so
# the ISO rebuilds whenever the rendered XML changes (e.g. if the
# operator rotates default_password).
resource "null_resource" "build_iso" {
  triggers = {
    autounattend_md5 = local_file.autounattend.content_md5
  }

  provisioner "local-exec" {
    command = join(" ", [
      "genisoimage",
      "-o", "${path.module}/build/${var.name}-autounattend.iso",
      "-V", "AUTOUNATTEND",
      "-J", "-r",
      local_file.autounattend.filename,
    ])
  }
}

# Upload the per-VM autounattend ISO to Proxmox so the cdrom block can
# attach it via `local:iso/<name>-autounattend.iso`. The install ISO and
# virtio-win.iso are presumed already staged in `local:iso/` by the
# operator (see Step 2 progress.md notes).
resource "proxmox_virtual_environment_file" "autounattend_iso" {
  content_type = "iso"
  datastore_id = "local"
  node_name    = var.template_node

  source_file {
    path = "${path.module}/build/${var.name}-autounattend.iso"
  }

  depends_on = [null_resource.build_iso]
}

resource "proxmox_virtual_environment_vm" "this" {
  name      = var.name
  node_name = var.template_node
  vm_id     = var.vmid
  tags      = var.tags

  # OVMF/UEFI firmware is non-negotiable: Win 11 Setup refuses Legacy
  # BIOS, and Win 10 boots fine on UEFI.
  bios            = "ovmf"
  machine         = "q35"
  stop_on_destroy = true

  # qemu-guest-agent ships in virtio-win.iso (installed by the
  # autounattend FirstLogonCommands). Once running, Tofu can read back
  # the VM's IP via .ipv4_addresses.
  agent {
    enabled = true
  }

  cpu {
    cores = var.cores
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = var.memory
  }

  efi_disk {
    datastore_id = "local-lvm"
    type         = "4m"
  }

  tpm_state {
    datastore_id = "local-lvm"
    version      = "v2.0"
  }

  # bpg/proxmox v0.104.0 enforces MaxItems=1 on the cdrom block. The
  # single cdrom block carries the Windows install ISO; the autounattend
  # ISO + virtio-win.iso land via kvm_arguments below (see DEC-007).
  cdrom {
    interface = "ide0"
    file_id   = "local:iso/${var.iso_file}"
  }

  # Two extra optical drives passed straight to qemu so Windows Setup
  # discovers autounattend.xml (on the autounattend ISO) and the virtio
  # drivers + qemu-guest-agent MSI (on virtio-win.iso). PVE preserves
  # these args verbatim in the qm.conf `args:` line. Filesystem path
  # `/var/lib/vz/template/iso/` is PVE's default location for the
  # `local` datastore's iso content; operators with custom storage
  # layouts can override the iso_storage_path module input.
  kvm_arguments = join(" ", [
    "-drive file=${var.iso_storage_path}/${var.name}-autounattend.iso,if=ide,index=2,media=cdrom",
    "-drive file=${var.iso_storage_path}/virtio-win.iso,if=ide,index=3,media=cdrom",
  ])

  disk {
    interface    = "scsi0"
    datastore_id = "local-lvm"
    size         = var.disk_gb
    discard      = "on"
    ssd          = true
  }

  network_device {
    bridge = var.bridge
    model  = "virtio"
  }

  operating_system {
    type = "win11"
  }

  # PVE only reads kvm_arguments at VM start, so the autounattend ISO
  # must be uploaded before the VM boots. The implicit edge through
  # `proxmox_virtual_environment_file.autounattend_iso.id` is gone
  # (kvm_arguments references the path string directly), so wire the
  # dependency explicitly.
  depends_on = [proxmox_virtual_environment_file.autounattend_iso]
}
