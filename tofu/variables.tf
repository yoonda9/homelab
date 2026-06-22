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
