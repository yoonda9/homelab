terraform {
  required_version = ">= 1.6.0"
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
      # Floor at 0.108.0: the container device_passthrough / mount_point /
      # idmap blocks this module emits need >= 0.108.0, which also carries the
      # create-time idmap fix the unprivileged Plex CT relies on in Step 7
      # (design §A / §6). Matches the root tofu/versions.tf floor.
      version = ">= 0.108.0"
    }
  }
}
