variable "pve_api_endpoint" {
  description = "Proxmox VE API endpoint, e.g. https://pve.example.com:8006/. Do not include /api2/json."
  type        = string
}

variable "pve_api_token" {
  description = "Proxmox VE API token in the form 'user@realm!tokenid=secret'. Reuses the same token Ansible consumes."
  type        = string
  sensitive   = true
}

variable "pve_node_name" {
  description = "Name of the Proxmox node that hosts the VMs (matches the node name shown in the PVE UI)."
  type        = string
}

variable "pve_insecure" {
  description = "Skip TLS verification when talking to the Proxmox API. Default false; set true only for self-signed dev clusters."
  type        = bool
  default     = false
}

variable "default_user" {
  description = "Daily-driver username created on every dev VM via cloud-init (Linux + Windows once Step 2 lands). Replaces image defaults like ubuntu/cloud-user with one uniform 'user'."
  type        = string
  default     = "user"
}

variable "default_password" {
  description = "Password for default_user (and the Windows Administrator account in Step 2). Dev-only; these VMs are not exposed externally. Sensitive to keep it out of plan output and state diffs."
  type        = string
  sensitive   = true
}

variable "ssh_authorized_keys" {
  description = "List of SSH public keys to authorize on default_user via cloud-init. Empty list disables key-based auth (password still works)."
  type        = list(string)
}
