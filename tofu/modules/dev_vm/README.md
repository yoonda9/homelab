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

## Notes

- Linux clones receive `hostname = var.name` via PVE auto-cidata.
- Win11 clones receive a sysprep-random hostname per C-12; `var.name`
  is the PVE display name only.
- Credentials (`user`/`password`) are baked into the template at build
  time per C-6 — this module does not pass cloud-init userdata.
