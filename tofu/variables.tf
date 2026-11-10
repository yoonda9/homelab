# Operator SSH access to the service CTs (DEBUG fix, 2026-06-22).
#
# The lxc_service module injects these keys into
# initialization.user_account.keys (modules/lxc_service/variables.tf
# ssh_public_keys). Without at least one key — and with no root password set —
# the provisioned CTs have NO root credential, so user_account.keys=[] in
# tfstate and Ansible's `root@<ct>` SSH login is rejected with
# "Permission denied (publickey,password)" (the `just play` failure in DEBUG.md;
# docker-host .111 reachable-but-denied is the clean positive case).
#
# Supply your key one of two mise-friendly ways in the gitignored
# mise.local.toml (both default to empty so a bare checkout still plans clean):
#   TF_VAR_operator_ssh_public_key_file = "/home/you/.ssh/id_ed25519.pub"
#   TF_VAR_operator_ssh_public_keys     = '["ssh-ed25519 AAAA... you@host"]'
variable "operator_ssh_public_keys" {
  type        = list(string)
  default     = []
  description = "Authorized SSH public keys (literal strings) injected into every service CT's root user_account. Usually set as a JSON list via TF_VAR_operator_ssh_public_keys."
}

variable "operator_ssh_public_key_file" {
  type        = string
  default     = ""
  description = "Path to a single SSH public key file (e.g. ~/.ssh/id_ed25519.pub) whose contents are injected into every service CT's root user_account. Set via TF_VAR_operator_ssh_public_key_file. Empty = use operator_ssh_public_keys only."
}

# Proxmox firewall for the gitlab-runner VMs (design §4.10, plan Step 10).
# Every firewall resource is gated on this by count/for_each.
#   0 = no firewall resources (rollback)   1 = each VM's own ipset, options, rules
# Default 1 since gate 2506 (2026-11-10). pve's datacenter and node firewalls were
# already on (policy_in DROP), so the per-VM objects are live once they exist. The
# old stage 2 (datacenter input ACCEPT, node firewall off) would only have loosened
# pve's own firewall, so it is retired and 2 fails validation.
variable "gitlab_runner_firewall_stage" {
  type        = number
  default     = 1
  description = "Firewall stage for the gitlab-runner VMs: 0 none (rollback), 1 each VM's own firewall (live, since pve's datacenter firewall is on). Stage 2 is retired."

  validation {
    condition     = contains([0, 1], var.gitlab_runner_firewall_stage)
    error_message = "gitlab_runner_firewall_stage must be 0 or 1. Stage 2 is retired: pve's datacenter and node firewalls are already on, and stage 2 would set the datacenter input policy to ACCEPT and turn the node firewall off (runbook: Firewall)."
  }
}
