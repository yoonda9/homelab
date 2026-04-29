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
