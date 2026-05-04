// Shared plugin requirements and input variables for all
// packer/*.pkr.hcl templates. Packer merges every *.pkr.hcl file in
// this directory into one configuration root, so plugin requirements
// and variable declarations live here exactly once. Variable values
// come from PKR_VAR_<name> env vars (set by .envrc) and from
// packer/common.pkrvars.hcl.

packer {
  required_plugins {
    proxmox = {
      version = "~> 1.2"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

variable "proxmox_host" {
  type = string
}

variable "proxmox_user" {
  type = string
}

variable "proxmox_token_id" {
  type = string
}

variable "proxmox_token_secret" {
  type      = string
  sensitive = true
}

variable "proxmox_node" {
  type    = string
  default = "pve"
}

variable "storage_pool" {
  type    = string
  default = "local-lvm"
}

variable "iso_storage_pool" {
  type    = string
  default = "local"
}

variable "network_bridge" {
  type    = string
  default = "vmbr0"
}
