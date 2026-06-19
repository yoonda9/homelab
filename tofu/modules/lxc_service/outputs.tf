output "vm_id" {
  value = proxmox_virtual_environment_container.this.vm_id
}

output "name" {
  value = var.name
}

# Best-effort post-provision IPv4 for eth0. The container `ipv4` attribute is a
# map(interface -> address); may be empty before the CT network is up. Mirrors
# the dev_vm module's try()-guarded address output.
output "ipv4_address" {
  value = try(proxmox_virtual_environment_container.this.ipv4["eth0"], null)
}
