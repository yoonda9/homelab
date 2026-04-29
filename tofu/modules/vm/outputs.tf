output "vmid" {
  description = "VM id of the cloned guest, mirrored from the input."
  value       = proxmox_virtual_environment_vm.this.vm_id
}

output "name" {
  description = "Name assigned to the cloned guest in Proxmox."
  value       = proxmox_virtual_environment_vm.this.name
}

output "node_name" {
  description = "Proxmox node hosting the cloned guest."
  value       = proxmox_virtual_environment_vm.this.node_name
}

# bpg/proxmox v0.104.0 exposes ipv4_addresses as a list-of-lists,
# one inner list per network interface. Index [0] is loopback, [1] is
# the first non-loopback NIC. Wrapped in try() so tofu validate / plan
# stay green before apply (qemu-guest-agent only populates this after
# the VM is up).
output "ipv4_address" {
  description = "First non-loopback IPv4 address as reported by the qemu-guest-agent (null until apply)."
  value       = try(proxmox_virtual_environment_vm.this.ipv4_addresses[1][0], null)
}
