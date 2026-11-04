# tofu/modules/dev_vm

Clones one of the three Packer-built dev VM templates. Caller resolves
the template VM-ID from the parent `tofu/locals.tf:template_ids` map
and passes it via `template_id`.

## Example

    module "dev" {
      source      = "../modules/dev_vm"
      name        = "smoke-1"
      os          = "ubuntu26"
      template_id = local.template_ids["ubuntu26"]
    }

## Optional inputs

Every input below is optional. With none set the module is DHCP with no
credentials, i.e. the bare-template behaviour.

| Variable | Default | Effect |
|---|---|---|
| `ssh_public_keys` | `[]` | Non-empty renders `initialization.user_account` with these keys |
| `ssh_username` | `"user"` | Template user that receives the keys |
| `ipv4_cidr` | `""` | Static address with prefix; empty means DHCP |
| `ipv4_gateway` | `""` | Required whenever `ipv4_cidr` is set (validated; needs OpenTofu >= 1.9) |
| `dns_servers` | `[]` | Renders `initialization.dns` when set |
| `dns_domain` | `""` | Search domain; also renders `initialization.dns` |
| `vm_id` | `null` | Stable PVE VM-ID; null lets PVE pick |
| `firewall` | `false` | `network_device.firewall`; inert until the VM's own firewall is enabled |
| `cpu_type` | `"host"` | Pinned because the bpg schema default is `qemu64` |

Outputs: `vm_id`, `name`, `ipv4_address` (guest-agent, best effort) and
`ipv4_configured` (the static address without its prefix; null under DHCP).

Requires OpenTofu >= 1.9 and bpg/proxmox >= 0.108.0.

## Static example

    module "runner" {
      source          = "../modules/dev_vm"
      name            = "gitlab-runner-pve"
      os              = "ubuntu26"
      template_id     = local.template_ids["ubuntu26"]
      vm_id           = 120
      ssh_public_keys = [var.operator_key]
      ipv4_cidr       = "192.168.1.120/24"
      ipv4_gateway    = "192.168.1.1"
      dns_servers     = ["192.168.1.1"]
      firewall        = true
    }

## Notes

- Linux clones receive `hostname = var.name` via PVE auto-cidata.
- Win11 clones receive a sysprep-random hostname per C-12; `var.name`
  is the PVE display name only.
- Credentials (`user`/`password`) are baked into the template at build
  time per C-6. Passing `ssh_public_keys` only adds an operator key to
  that user; it does not replace the baked password.
