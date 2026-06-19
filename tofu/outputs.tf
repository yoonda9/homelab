# Docker-host CT facts, surfaced for the Step 4 Ansible inventory (which
# renders hosts from `tofu output`). ipv4_address is best-effort and may be
# null until the CT network is up.
output "docker_host_vm_id" {
  description = "PVE VM-ID of the docker-host LXC."
  value       = module.docker_host.vm_id
}

output "docker_host_name" {
  description = "Hostname of the docker-host LXC."
  value       = module.docker_host.name
}

output "docker_host_ipv4" {
  description = "Best-effort IPv4 of the docker-host LXC (null until network up)."
  value       = module.docker_host.ipv4_address
}

# Plex CT facts, surfaced for the Ansible inventory (Step 8 plex role targets
# this host). ipv4 is best-effort and may be null until the CT network is up.
output "plex_vm_id" {
  description = "PVE VM-ID of the plex LXC."
  value       = module.plex.vm_id
}

output "plex_name" {
  description = "Hostname of the plex LXC."
  value       = module.plex.name
}

output "plex_ipv4" {
  description = "Best-effort IPv4 of the plex LXC (null until network up)."
  value       = module.plex.ipv4_address
}
