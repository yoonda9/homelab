output "vm_id" {
  value = proxmox_virtual_environment_vm.dev_vm.vm_id
}

output "name" {
  value = proxmox_virtual_environment_vm.dev_vm.name
}

# Best-effort post-cidata IPv4. May be empty before guest-agent wakes.
output "ipv4_address" {
  value = try(proxmox_virtual_environment_vm.dev_vm.ipv4_addresses[1][0], null)
}

# Deterministic static address (prefix stripped); null under DHCP. Unlike
# ipv4_address it does not depend on the guest agent.
output "ipv4_configured" {
  value = var.ipv4_cidr == "" ? null : split("/", var.ipv4_cidr)[0]
}
