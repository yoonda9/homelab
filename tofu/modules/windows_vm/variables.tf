variable "name" {
  description = "VM name as it appears in the Proxmox UI. Also used as the ComputerName inside Windows and as the per-VM autounattend ISO filename prefix."
  type        = string
}

variable "vmid" {
  description = "VM id assigned to the new Windows VM (must be unique on the cluster)."
  type        = number
}

variable "iso_file" {
  description = "Filename of the Windows install ISO already staged in Proxmox `local:iso/`. Referenced verbatim — operators stage `Win10_22H2_English_x64.iso` / `Win11_23H2_English_x64.iso` (or whichever build is current) into the local ISO datastore by hand."
  type        = string
}

variable "memory" {
  description = "Dedicated memory for the VM, in megabytes."
  type        = number
}

variable "cores" {
  description = "Number of CPU cores assigned to the VM."
  type        = number
}

variable "disk_gb" {
  description = "Boot disk size in GB (Number, e.g. 120). Drives the disk { size } attribute on the VM resource. bpg/proxmox v0.104.0 expects a Number here — string-with-G fails plan."
  type        = number
}

variable "bridge" {
  description = "Linux bridge the VM's primary NIC attaches to (e.g. vmbr0)."
  type        = string
}

variable "template_node" {
  description = "Proxmox node where the VM is created (matches the node name shown in the PVE UI)."
  type        = string
}

variable "default_user" {
  description = "Daily-driver Windows username created via autounattend.xml. Mirrors the Linux module's default_user so a single Ansible inventory `ansible_user` covers both platforms."
  type        = string
}

variable "default_password" {
  description = "Password for default_user (and the local Administrator account, used for the one-shot autologon during OOBE). Sensitive."
  type        = string
  sensitive   = true
}

variable "ssh_authorized_keys" {
  description = "List of SSH public keys authorized on the Windows OpenSSH server's Administrators group. Joined by newlines and written to C:\\ProgramData\\ssh\\administrators_authorized_keys by the autounattend FirstLogonCommands."
  type        = list(string)
}

variable "tags" {
  description = "Optional tags applied to the VM in Proxmox."
  type        = list(string)
  default     = []
}

variable "iso_storage_path" {
  description = "Filesystem path on the Proxmox host where ISOs in the `local:iso` storage live. Defaults to PVE's stock `/var/lib/vz/template/iso` location. Used by kvm_arguments to pass extra `-drive ...,media=cdrom` flags to qemu (per DEC-007 — bpg/proxmox v0.104.0 caps cdrom blocks at 1, so the extra ISOs land via raw qemu CLI args)."
  type        = string
  default     = "/var/lib/vz/template/iso"
}
