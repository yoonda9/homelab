# Two-map for_each shape from § "Architecture / tofu/main.tf" of the
# dev-vms-design spec. Adding or removing a dev VM is a single map
# entry in `local.linux_vms` or `local.windows_vms`; new Linux distros
# are a single entry in `local.cloud_templates`. Windows install ISOs
# are referenced by filename — operators stage them in `local:iso/` by
# hand (no cloud-init equivalent for Windows; autounattend.xml is the
# moral equivalent and is rendered/built per-VM by module.windows_vm).

locals {
  # Cloud-init template vmids managed by `pve_base`. Keys are the
  # human-readable distro slugs referenced by `local.linux_vms` entries.
  cloud_templates = {
    ubuntu-24-04       = 9000
    ubuntu-26-04       = 9001
    fedora-workstation = 9003
  }

  # Canonical Linux dev fleet. Required per-entry keys: vmid, template,
  # memory, cores, disk_gb. Optional: static_ip, gateway (must be set
  # together — half-configured fails plan via the module precondition).
  linux_vms = {
    ubuntu26-dev           = { vmid = 310, template = "ubuntu-26-04", memory = 4096, cores = 2, disk_gb = 120 }
    fedora-workstation-dev = { vmid = 312, template = "fedora-workstation", memory = 4096, cores = 2, disk_gb = 120 }
  }

  # Canonical Windows dev fleet. Required per-entry keys: vmid, iso
  # (filename in `local:iso/`), memory, cores, disk_gb. Win 11 gets
  # 8 GB RAM / 4 cores by default (Windows Hello + Hyper-V containers
  # tax memory more than Win 10 does); Win 10 stays at 4 GB / 2 cores
  # to keep the dev fleet's resource footprint tight.
  windows_vms = {
    win10-dev = { vmid = 320, iso = "Win10_22H2_English_x64.iso", memory = 4096, cores = 2, disk_gb = 120 }
    win11-dev = { vmid = 321, iso = "Win11_23H2_English_x64.iso", memory = 8192, cores = 4, disk_gb = 120 }
  }
}

module "linux_vm" {
  for_each = local.linux_vms

  source              = "./modules/linux_vm"
  name                = each.key
  vmid                = each.value.vmid
  clone_from          = local.cloud_templates[each.value.template]
  memory              = each.value.memory
  cores               = each.value.cores
  disk_gb             = each.value.disk_gb
  static_ip           = try(each.value.static_ip, null)
  gateway             = try(each.value.gateway, null)
  bridge              = "vmbr0"
  template_node       = var.pve_node_name
  default_user        = var.default_user
  default_password    = var.default_password
  ssh_authorized_keys = var.ssh_authorized_keys
  tags                = ["linux", "dev", "tofu"]
}

module "windows_vm" {
  for_each = local.windows_vms

  source              = "./modules/windows_vm"
  name                = each.key
  vmid                = each.value.vmid
  iso_file            = each.value.iso
  memory              = each.value.memory
  cores               = each.value.cores
  disk_gb             = each.value.disk_gb
  bridge              = "vmbr0"
  template_node       = var.pve_node_name
  default_user        = var.default_user
  default_password    = var.default_password
  ssh_authorized_keys = var.ssh_authorized_keys
  tags                = ["windows", "dev", "tofu"]
}
