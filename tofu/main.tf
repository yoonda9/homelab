# Two-map for_each shape from § "Architecture / tofu/main.tf" of the
# dev-vms-design spec. Adding or removing a Linux dev VM is a single map
# entry in `local.linux_vms`; new distros are a single entry in
# `local.cloud_templates`. The Windows half (`local.windows_vms` +
# `module "windows_vm"`) lands in Step 2.

locals {
  # Cloud-init template vmids managed by `pve_base`. Keys are the
  # human-readable distro slugs referenced by `local.linux_vms` entries.
  cloud_templates = {
    ubuntu-24-04     = 9000
    ubuntu-26-04     = 9001
    centos-stream-10 = 9002
  }

  # Canonical dev fleet. Required per-entry keys: vmid, template,
  # memory, cores, disk_gb. Optional: static_ip, gateway (must be set
  # together — half-configured fails plan via the module precondition).
  linux_vms = {
    ubuntu26-dev = { vmid = 310, template = "ubuntu-26-04", memory = 4096, cores = 2, disk_gb = 120 }
    centos10-dev = { vmid = 311, template = "centos-stream-10", memory = 4096, cores = 2, disk_gb = 120 }
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
