terraform {
  required_version = ">= 1.6.0"
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
      # Floor at 0.108.0 for the create-time idmap fix the Plex CT relies on
      # in Step 7 (design DD L335/L384/L394). Backward compatible with the
      # dev_vm module (validated standalone at its own pin).
      version = ">= 0.108.0"
    }
  }
}
