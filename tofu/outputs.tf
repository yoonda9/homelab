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

# gitlab-runner VM facts for the Ansible inventory (gen_inventory.py renders the
# gitlab_runner group from this). ipv4 is the configured static address, so it
# does not depend on the guest agent.
output "gitlab_runners" {
  description = "gitlab-runner VMs by name: static IPv4 and PVE VM-ID."
  value       = { for k, m in module.gitlab_runner : k => { ipv4 = m.ipv4_configured, vm_id = m.vm_id } }
}
