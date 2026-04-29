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
