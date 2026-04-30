# Ansible-consumable inventory structure aggregated over every instance
# of `module "linux_vm"`. Step 1b drops the legacy ad-hoc per-module
# host blocks in favour of a for-expression that walks `module.linux_vm[*]`
# (the for_each-induced map). Adding a host is a single entry in
# `local.linux_vms`; this output picks it up automatically.
#
# Shape consumed by `scripts/tofu_to_inventory.py`:
#   <group> -> hosts -> <hostname> -> { ansible_host, vmid, node_name }
#                vars  -> { ansible_user = "user" }
#
# `ansible_host` is wrapped in try() inside the linux_vm module's
# `ipv4_address` output, so this stays valid before apply (the
# qemu-guest-agent only reports addresses once the VM is up).

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
  }
}
