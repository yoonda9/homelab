// Win11 24H2 Packer template. Plugin requirements + shared input
// variables live in packer/_variables.pkr.hcl (DEC-014); declaring
// them again here would fail `packer init` per the directory-as-
// config-root rule (mem-1777854396-6d9e).

source "proxmox-iso" "windows11" {
  proxmox_url              = "https://${var.proxmox_host}:8006/api2/json"
  username                 = "${var.proxmox_user}!${var.proxmox_token_id}"
  token                    = var.proxmox_token_secret
  insecure_skip_tls_verify = true

  node                 = var.proxmox_node
  vm_id                = 9102
  template_name        = "pkr-win11"
  template_description = "Built by Packer; see scripts/build_template.sh windows11"

  bios     = "ovmf"
  machine  = "q35"
  cpu_type = "host"
  cores    = 4
  memory   = 8192

  efi_config {
    efi_storage_pool  = "local-lvm"
    efi_type          = "4m"
    pre_enrolled_keys = true
  }

  tpm_config {
    tpm_storage_pool = "local-lvm"
    tpm_version      = "v2.0"
  }

  network_adapters {
    bridge = var.network_bridge
    model  = "virtio"
  }

  scsi_controller = "virtio-scsi-pci"
  disks {
    type         = "scsi"
    storage_pool = var.storage_pool
    disk_size    = "64G"
    format       = "raw"
  }

  # Slot 1: Win11 ISO (operator pre-stages on PVE local:iso per C-7).
  boot_iso {
    type              = "sata"
    iso_file          = "local:iso/Win11_24H2_EnglishInternational_x64.iso"
    iso_checksum      = "none"
    unmount           = true
    keep_cdrom_device = false
  }

  # Slot 2: virtio-win drivers (operator pre-stages on PVE local:iso per C-7).
  additional_iso_files {
    type              = "sata"
    iso_file          = "local:iso/virtio-win-0.1.262.iso"
    iso_checksum      = "none"
    unmount           = true
    keep_cdrom_device = false
  }

  # Slot 3: pre-baked autounattend cidata ISO. Built by
  # scripts/build_template.sh into packer_cache/, uploaded to PVE by
  # Packer via iso_download_pve. Volume label "Unattend" is load-
  # bearing per C-10 — Win11 Setup auto-discovers autounattend.xml
  # at the root of any CD with that label.
  additional_iso_files {
    type              = "sata"
    iso_url           = "file://${path.cwd}/packer_cache/autounattend-win11.iso"
    iso_checksum      = "none"
    iso_storage_pool  = "local"
    iso_download_pve  = true
    unmount           = true
    keep_cdrom_device = false
  }

  boot_wait = "10s"
  # No boot_command — Win11 Setup auto-loads autounattend.xml from the
  # cidata CD with volume label "Unattend".

  communicator   = "winrm"
  winrm_username = "user"
  winrm_password = "password"
  winrm_use_ssl  = false
  winrm_insecure = true
  winrm_timeout  = "4h"
  winrm_port     = 5985
}

build {
  sources = ["source.proxmox-iso.windows11"]

  # Step 1: install OpenSSH.Server capability so the SEALED template
  # ships with sshd (FR-2 floor for clones). Capability install can fail
  # if the ISO lacks the FoD payload AND the build subnet has no WU
  # access — provisioner exits non-zero and aborts the build BEFORE the
  # seal step runs (per C-9 + design §6.1).
  provisioner "powershell" {
    inline = [
      "Set-StrictMode -Version Latest",
      "$ErrorActionPreference = 'Stop'",
      "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0",
      "Set-Service -Name sshd -StartupType Automatic",
      "Start-Service sshd",
      "New-NetFirewallRule -Name 'OpenSSH-22' -DisplayName 'OpenSSH Server (TCP 22)' -Protocol TCP -LocalPort 22 -Action Allow -Direction Inbound -Profile Public,Private,Domain",
    ]
  }

  # Step 2: install python.org silent installer with PrependPath=1.
  provisioner "powershell" {
    inline = [
      "Set-StrictMode -Version Latest",
      "$ErrorActionPreference = 'Stop'",
      "$url = 'https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe'",
      "$dst = 'C:\\Windows\\Temp\\python-installer.exe'",
      "Invoke-WebRequest -Uri $url -OutFile $dst -UseBasicParsing",
      "Start-Process -FilePath $dst -ArgumentList '/quiet','InstallAllUsers=1','PrependPath=1' -Wait",
      "& 'C:\\Program Files\\Python313\\python.exe' --version",
    ]
  }

  # Step 3: pre-sysprep verifier (C-9). Loud-fails the build if sshd
  # is not Running, so a partial OpenSSH install never produces a
  # sealed template that silently violates FR-2.
  provisioner "powershell" {
    inline = [
      "Set-StrictMode -Version Latest",
      "$ErrorActionPreference = 'Stop'",
      "$running = (Get-Service sshd).Status -eq 'Running'",
      "if (-not $running) { throw 'sshd not Running pre-sysprep — aborting build per C-9' }",
      "Write-Host 'OK: sshd Running pre-sysprep'",
    ]
  }

  # Step 4: sysprep generalize seal (C-8). Persists autounattend.xml at
  # C:\Windows\Panther\unattend.xml so generalize re-applies the
  # specialize+oobe passes on first clone boot.
  provisioner "powershell" {
    inline = [
      "Set-StrictMode -Version Latest",
      "$ErrorActionPreference = 'Stop'",
      "& C:\\Windows\\System32\\Sysprep\\sysprep.exe /generalize /oobe /shutdown /unattend:C:\\Windows\\Panther\\unattend.xml",
    ]
  }
}
