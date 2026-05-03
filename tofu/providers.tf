# All provider config flows from env vars exported by .envrc:
#   PROXMOX_VE_ENDPOINT      (e.g., https://pve.home.arpa:8006/)
#   PROXMOX_VE_USERNAME      (e.g., root@pam!ansible-token)
#   PROXMOX_VE_API_TOKEN     (e.g., root@pam!ansible-token=<secret-uuid>)
#   PROXMOX_VE_INSECURE=true (for self-signed cert on homelab)
provider "proxmox" {
}
