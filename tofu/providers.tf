# All provider config flows from env vars exported by mise
# (non-secret in mise.toml [env]; secrets in gitignored mise.local.toml):
#   PROXMOX_VE_ENDPOINT      (e.g., https://pve.home.arpa:8006/)
#   PROXMOX_VE_API_TOKEN     (e.g., root@pam!ansible-token=<secret-uuid>)
#   PROXMOX_VE_INSECURE=true (for self-signed cert on homelab)
#   PROXMOX_VE_SSH_USERNAME  (e.g., root — read natively by the ssh{} block)
provider "proxmox" {
  # SSH-backed operations are required for the idmap (later steps) and
  # root@pam for bind mounts. bpg reads the SSH username natively from the
  # PROXMOX_VE_SSH_USERNAME env var; the agent handles authentication so no
  # key material or secret literal appears in committed HCL.
  ssh {
    agent = true
  }
}
