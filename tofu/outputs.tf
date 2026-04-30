# Ansible-consumable inventory structure aggregated over every instance
# of `module "linux_vm"` and `module "windows_vm"`. Step 1b dropped the
# legacy per-module host blocks in favour of a for-expression that
# walks `module.<name>[*]` (the for_each-induced map). Step 2 adds a
# sibling `windows_dev_vms` group following the same shape.
#
# Shape consumed by `scripts/tofu_to_inventory.py`:
#   <group> -> hosts -> <hostname> -> { ansible_host, vmid, node_name }
#                vars  -> { ansible_user = "user" }
#
# Both modules' `ipv4_address` outputs wrap the bpg/proxmox
# ipv4_addresses lookup in try() so plan stays valid before the
# qemu-guest-agent reports a lease.
#
# The `proxmox_vms.children.windows` mapping (with
# `ansible_shell_type: powershell`) lands in Step 3
# (scripts/tofu_to_inventory.py); this Tofu-side output emits the
# sibling `windows_dev_vms` group only.

output "ansible_inventory" {
  description = "Ansible-inventory-shaped output consumed by scripts/tofu_to_inventory.py."

  value = {
    proxmox_vms = {
      hosts = {
        for k, v in module.linux_vm : k => {
          ansible_host = try(v.ipv4_address, null)
          vmid         = v.vmid
          node_name    = v.node_name
        }
      }
      vars = {
        ansible_user = var.default_user
      }
    }
    windows_dev_vms = {
      hosts = {
        for k, v in module.windows_vm : k => {
          ansible_host = try(v.ipv4_address, null)
          vmid         = v.vmid
          node_name    = v.node_name
        }
      }
      vars = {
        ansible_user = var.default_user
      }
    }
  }
}
