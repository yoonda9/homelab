# Step 10a premise: bpg firewall resources vs the locked provider

Source: `tofu providers schema -json` in `tofu/` (offline), lock file pins bpg/proxmox 0.120.0 (constraint >= 0.108.0). Design review saw 0.110.0; the names held.

| Design §4.10 name | Locked schema | Notes |
|---|---|---|
| `proxmox_node_firewall` | present (`enabled`, `node_name` R; `nftables`, `ndp`, `nosmurfs`, ... O/C) | `proxmox_virtual_environment_node_firewall` also exists but is **deprecated**; use the non-deprecated name |
| `proxmox_virtual_environment_cluster_firewall` | present: `enabled`, `input_policy`, `output_policy`, `forward_policy`, `ebtables` all Optional (no Computed) | Optional, non-computed `input_policy`: deleting the line falls back to the provider default (DROP), so the guard pins the line |
| `proxmox_virtual_environment_firewall_ipset` | `name` R; `node_name`, `vm_id`, `container_id` O; repeated `cidr {name R, comment, nomatch}` block | IP goes in `cidr.name`; set `name = "ipfilter-net0"` |
| `proxmox_virtual_environment_firewall_options` | `node_name` R; `vm_id`/`container_id` O; `enabled`, `input_policy`, `output_policy`, `macfilter`, `ipfilter`, `radv`, `dhcp`, `ndp`, `log_level_*` all O | all design-listed attrs exist |
| `proxmox_virtual_environment_firewall_rules` | `node_name`, `vm_id` O; repeated `rule {type, action, proto, source, dest, dport, sport, macro, iface, log, enabled, comment; pos C}` | no per-rule ordering beyond list order; IPv6 drop = `dest = "::/0"` |

Differences from the design to carry into 10b/10c: none of the names changed; only the node firewall resource must use the non-deprecated spelling. `node_name` is required on options (and optional elsewhere), so pass it everywhere.
