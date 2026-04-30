output "vmid" {
  description = "VM id of the Windows guest, mirrored from the input."
  value       = proxmox_virtual_environment_vm.this.vm_id
}

output "name" {
  description = "Name assigned to the Windows guest in Proxmox."
  value       = proxmox_virtual_environment_vm.this.name
}

output "node_name" {
  description = "Proxmox node hosting the Windows guest."
  value       = proxmox_virtual_environment_vm.this.node_name
}

# bpg/proxmox v0.104.0 exposes ipv4_addresses as a list-of-lists, one
# inner list per network interface. Index [0] is loopback, [1] is the
# first non-loopback NIC. Wrapped in try() so plan stays valid before
# qemu-guest-agent reports a lease (Windows boots, runs FirstLogon
# commands to install virtio-win drivers + qemu-ga.msi, *then* the
# guest agent populates this attribute).
output "ipv4_address" {
  description = "First non-loopback IPv4 address as reported by qemu-guest-agent (null until apply)."
  value       = try(proxmox_virtual_environment_vm.this.ipv4_addresses[1][0], null)
}
