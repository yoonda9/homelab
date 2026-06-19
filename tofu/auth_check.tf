# Harmless auth-exercising reference (canonical plan Step 2).
#
# The `proxmox_version` data source reads the PVE API version on every
# `tofu plan`/`apply`. It forces a real authenticated round-trip against `pve`
# — surfacing token/SSH misconfiguration early — while proposing zero resource
# changes. Exposed as an output so the value is actually resolved (and visible
# in `tofu output` as a connectivity probe).
data "proxmox_version" "pve" {}

output "proxmox_version" {
  description = "PVE API version — authentication probe, not a managed resource."
  value       = data.proxmox_version.pve.version
}
