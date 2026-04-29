# Ansible-consumable inventory structure. The Step 4 generator will
# read `tofu output -json ansible_inventory` and write it to
# ansible/inventory/tofu_generated.yml. Shape:
#   <group> -> hosts -> <hostname> -> { ansible_host, vmid, node_name }
#                vars  -> { ansible_user = "ubuntu" }
# `ansible_host` is wrapped in try() inside the vm module's
# `ipv4_address` output, so this stays valid before apply (the
# qemu-guest-agent only reports addresses once the VM is up).

output "ansible_inventory" {
  description = "Ansible-inventory-shaped output consumed by ansible/configure-vms.yml in Step 4."

  value = {
    proxmox_vms = {
      hosts = {
        (module.ubuntu26_test.name) = {
          ansible_host = try(module.ubuntu26_test.ipv4_address, null)
          vmid         = module.ubuntu26_test.vmid
          node_name    = module.ubuntu26_test.node_name
        }
        (module.centos10_test.name) = {
          ansible_host = try(module.centos10_test.ipv4_address, null)
          vmid         = module.centos10_test.vmid
          node_name    = module.centos10_test.node_name
        }
      }
      vars = {
        ansible_user = "ubuntu"
      }
    }
  }
}
