# All provider config flows from env vars exported by mise
# (non-secret in mise.toml [env]; secrets in gitignored mise.local.toml):
#   PROXMOX_VE_ENDPOINT      (e.g., https://pve.home.arpa:8006/)
#   PROXMOX_VE_USERNAME=root@pam + PROXMOX_VE_PASSWORD  (root@pam login ticket)
#   PROXMOX_VE_INSECURE=true (for self-signed cert on homelab)
#   PROXMOX_VE_SSH_USERNAME  (e.g., root — read natively by the ssh{} block)
# bpg reads all of these env vars natively — no attrs in HCL, so no secret
# literal is committed. API auth is the root@pam username/password TICKET, and
# deliberately NOT an API token: the Plex CT configures LXC device passthrough
# (dev[n] keys), which Proxmox refuses through any API token even a root@pam-owned
# one — it demands a real root@pam login ticket. bpg's auth modes are mutually
# exclusive and the API token takes PRECEDENCE (proxmox/api/credentials.go
# early-returns; client.go NewClient checks TokenCredentials first), so setting
# PROXMOX_VE_API_TOKEN would make bpg use the token for ALL calls and never build
# the ticket — the passthrough create would 403. PROXMOX_VE_API_TOKEN is therefore
# intentionally unset for this provider. (Packer uses a separate token scheme.)
provider "proxmox" {
  # SSH-backed operations are required for the idmap (later steps) and
  # root@pam for bind mounts. bpg reads the SSH username natively from the
  # PROXMOX_VE_SSH_USERNAME env var; the agent handles authentication so no
  # key material or secret literal appears in committed HCL.
  ssh {
    agent = true
  }
}
