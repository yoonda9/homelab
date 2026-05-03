# Non-secret build-side defaults. Secret vars (proxmox_token_*) are
# injected via PKR_VAR_* env vars from .envrc; this file is the only
# *.pkrvars.hcl file intentionally checked in.

proxmox_node     = "pve"
storage_pool     = "local-lvm"
iso_storage_pool = "local"
network_bridge   = "vmbr0"
