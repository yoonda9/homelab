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

variable "ssh_public_keys" {
  type        = list(string)
  default     = []
  description = "Operator public keys. When non-empty, main.tf renders initialization.user_account with them; empty keeps the bare-template behaviour."
}

variable "ssh_username" {
  type        = string
  default     = "user"
  description = "The template's baked-in user that receives ssh_public_keys."
}

variable "ipv4_cidr" {
  type        = string
  default     = ""
  description = "Static IPv4 address with prefix (e.g. 192.168.1.120/24). Empty means DHCP."
}

variable "ipv4_gateway" {
  type        = string
  default     = ""
  description = "IPv4 gateway. Required when ipv4_cidr is set."
  validation {
    # Cross-variable reference in a validation block needs OpenTofu >= 1.9.
    condition     = var.ipv4_cidr == "" || var.ipv4_gateway != ""
    error_message = "ipv4_gateway must be set whenever ipv4_cidr is set."
  }
}

variable "dns_servers" {
  type        = list(string)
  default     = []
  description = "DNS servers; rendered in initialization.dns only when set."
}

variable "dns_domain" {
  type        = string
  default     = ""
  description = "DNS search domain; rendered in initialization.dns only when set."
}

variable "vm_id" {
  type        = number
  default     = null
  description = "Stable PVE VM-ID. Null lets PVE pick."
}

variable "firewall" {
  type        = bool
  default     = false
  description = "Sets network_device.firewall. Inert until the VM's own firewall options are enabled."
}

variable "cpu_type" {
  type        = string
  default     = "host"
  description = "CPU type, pinned explicitly because the bpg schema default is qemu64 while the template uses host."
}
