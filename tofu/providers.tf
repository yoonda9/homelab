# All provider config flows from env vars exported by mise
# (non-secret in mise.toml [env]; secrets in gitignored mise.local.toml):
#   PROXMOX_VE_ENDPOINT      (e.g., https://pve.home.arpa:8006/)
#   PROXMOX_VE_API_TOKEN     (e.g., root@pam!ansible-token=<secret-uuid>)
#   PROXMOX_VE_INSECURE=true (for self-signed cert on homelab)
#   PROXMOX_VE_SSH_USERNAME  (e.g., root — read natively by the ssh{} block)
#   PROXMOX_VE_USERNAME=root@pam + PROXMOX_VE_PASSWORD  (root@pam login ticket)
# bpg reads all of these env vars natively — no attrs in HCL, so no secret
# literal is committed. The username/password ticket is REQUIRED by the Plex CT:
# Proxmox refuses to configure LXC device passthrough (dev[n] keys) through any
# API token, even a root@pam-owned one, and demands a real root@pam login
# ticket. The provider uses the ticket for that privileged op and the API token
# for everything else.
provider "proxmox" {
  # SSH-backed operations are required for the idmap (later steps) and
  # root@pam for bind mounts. bpg reads the SSH username natively from the
  # PROXMOX_VE_SSH_USERNAME env var; the agent handles authentication so no
  # key material or secret literal appears in committed HCL.
  ssh {
    agent = true
  }
}
