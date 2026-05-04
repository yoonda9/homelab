# DEBUG 

Running `./scripts/build_template.sh ubuntu26` and `./scripts/build_template.sh fedora` throws the same errors below.

```shell
==> step 1: env-var pre-flight
==> step 4: packer init
==> step 5: packer build fedora.pkr.hcl (force=true overwrite)
Error: Unsupported attribute

  on fedora.pkr.hcl line 3:
  (source code not available)

This object does not have an attribute named "proxmox_user".

Error: Unsupported attribute

  on fedora.pkr.hcl line 3:
  (source code not available)

This object does not have an attribute named "proxmox_token_id".

Error: Unsupported attribute

  on fedora.pkr.hcl line 4:
  (source code not available)

This object does not have an attribute named "proxmox_token_secret".

Error: Unsupported attribute

  on fedora.pkr.hcl line 32:
  (source code not available)

This object does not have an attribute named "storage_pool".

Error: Unsupported attribute

  on fedora.pkr.hcl line 25:
  (source code not available)

This object does not have an attribute named "network_bridge".

Error: Unsupported attribute

  on fedora.pkr.hcl line 7:
  (source code not available)

This object does not have an attribute named "proxmox_node".

Error: Unsupported attribute

  on fedora.pkr.hcl line 41:
  (source code not available)

This object does not have an attribute named "iso_storage_pool".

Error: Unsupported attribute

  on fedora.pkr.hcl line 2:
  (source code not available)

This object does not have an attribute named "proxmox_host".

```
