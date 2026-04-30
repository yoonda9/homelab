variable "name" {
  description = "Name of the new VM as it appears in the Proxmox UI."
  type        = string
}

variable "vmid" {
  description = "VM id assigned to the new VM (must be unique on the cluster)."
  type        = number
}

variable "clone_from" {
  description = "VM id of the cloud-init template to clone from (e.g. 9001 for ubuntu-26.04-cloud)."
  type        = number
}

variable "memory" {
  description = "Dedicated memory for the new VM, in megabytes."
  type        = number
}

variable "cores" {
  description = "Number of CPU cores assigned to the new VM."
  type        = number
}

variable "bridge" {
  description = "Linux bridge the VM's primary NIC attaches to (e.g. vmbr0)."
  type        = string
}

variable "template_node" {
  description = "Proxmox node where the source template lives (the new VM is created on the same node)."
  type        = string
}

variable "tags" {
  description = "Optional tags applied to the new VM in Proxmox."
  type        = list(string)
  default     = []
}

variable "disk_gb" {
  description = "Boot disk size in GB (integer, e.g. 32 or 64). Required input — drives the disk { size } attribute on the cloned VM."
  type        = number
}

variable "static_ip" {
  description = "Static IPv4 address in CIDR (e.g. 192.168.1.50/24). When null, the VM uses DHCP. Must be paired with var.gateway."
  type        = string
  default     = null
}

variable "gateway" {
  description = "IPv4 default gateway address. When null, the VM uses DHCP. Must be paired with var.static_ip."
  type        = string
  default     = null
}

variable "default_user" {
  description = "Daily-driver username created on every dev VM via cloud-init (replaces the image's default ubuntu/cloud-user)."
  type        = string
}

variable "default_password" {
  description = "Password for default_user. Sensitive — populated from var.default_password at the root level."
  type        = string
  sensitive   = true
}

variable "ssh_authorized_keys" {
  description = "List of SSH public keys authorized on default_user via cloud-init."
  type        = list(string)
}
