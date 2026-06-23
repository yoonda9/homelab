variable "name" {
  type        = string
  description = "CT hostname / display name (e.g. \"docker-host\")."
}

variable "vm_id" {
  type        = number
  description = "PVE VM-ID for the container. Caller passes local.service_ids.<svc>."
}

variable "ip_cidr" {
  type        = string
  description = "Static IPv4 in CIDR form for eth0, e.g. \"192.168.1.111/24\"."
}

variable "gateway" {
  type        = string
  description = "IPv4 default gateway, e.g. \"192.168.1.1\"."
}

variable "node" {
  type    = string
  default = "pve"
}

variable "datastore_id" {
  type        = string
  default     = "local-lvm"
  description = "Datastore for the container root disk."
}

variable "bridge" {
  type    = string
  default = "vmbr0"
}

variable "template_file_id" {
  type        = string
  description = "vztmpl file id to provision from, e.g. \"local:vztmpl/debian-13-standard_13.x_amd64.tar.zst\" (caller passes the download_file resource id)."
}

variable "cores" {
  type    = number
  default = 2
}

variable "memory_mb" {
  type    = number
  default = 2048
}

variable "disk_gb" {
  type    = number
  default = 16
}

# The fallback switch (design §4.1 / R2): unprivileged by default. Step 7's
# Plex CT flips this to false only if the unprivileged idmap path fails.
variable "unprivileged" {
  type    = bool
  default = true
}

variable "nesting" {
  type        = bool
  default     = false
  description = "features.nesting — required for the docker-host CT to run Docker."
}

variable "keyctl" {
  type        = bool
  default     = false
  description = "features.keyctl — required ALONGSIDE nesting for Docker in an unprivileged CT: dockerd/containerd need the kernel keyring, and without it the docker provider registers no routers (Traefik 404). See tofu/main.tf docker_host."
}

variable "start_on_boot" {
  type    = bool
  default = true
}

# --- Optional capability lists. All default to [] so the conditional blocks
# below render NOTHING for a plain CT (docker-host). Step 7 supplies these for
# the Plex CT (GPU passthrough + media bind mount + idmap tiling). ---

variable "device_passthroughs" {
  type = list(object({
    path = string
    gid  = number
    mode = optional(string)
  }))
  default     = []
  description = "Host device nodes to pass through (e.g. /dev/dri/renderD128). Empty = none."
}

variable "bind_mounts" {
  type = list(object({
    host_path = string
    ct_path   = string
    read_only = optional(bool, false)
  }))
  default     = []
  description = "Host directories bind-mounted into the CT. Needs root@pam. Empty = none."
}

variable "gid_maps" {
  type = list(object({
    container_id = number
    host_id      = number
    size         = number
  }))
  default     = []
  description = "GID idmap entries (type \"g\"). Empty = default unprivileged mapping only."
}

variable "uid_maps" {
  type = list(object({
    container_id = number
    host_id      = number
    size         = number
  }))
  default     = []
  description = "UID idmap entries (type \"u\"). Empty = default unprivileged mapping only."
}

variable "ssh_public_keys" {
  type        = list(string)
  default     = []
  description = "Authorized SSH public keys injected via initialization.user_account.keys."
}
