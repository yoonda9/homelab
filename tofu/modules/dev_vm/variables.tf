variable "name" {
  type        = string
  description = "VM display name. Linux clones receive this as the hostname via PVE auto-cidata; Win11 clones receive a sysprep-random hostname (hostname asymmetry per C-12)."
}

variable "os" {
  type        = string
  description = "Short OS name; resolves to a stable template VM-ID via tofu/locals.tf:template_ids."
  validation {
    condition     = contains(["ubuntu26", "fedora", "win11"], var.os)
    error_message = "os must be one of ubuntu26, fedora, win11."
  }
}

variable "template_id" {
  type        = number
  description = "PVE VM-ID of the template to clone from. Caller passes local.template_ids[var.os]."
}

variable "node" {
  type    = string
  default = "pve"
}

variable "cores" {
  type    = number
  default = 2
}

variable "memory_mb" {
  type    = number
  default = 4096
}

variable "disk_gb" {
  type    = number
  default = 32
}

variable "datastore_id" {
  type    = string
  default = "local-lvm"
}

variable "bridge" {
  type    = string
  default = "vmbr0"
}
