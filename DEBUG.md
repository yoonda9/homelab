# DEBUG Error

Running  `./scripts/build_template.sh fedora` fails with the following output.

```shell
==> step 1: env-var pre-flight
==> step 2: fedora — ensure tpl-cloud-fedora43 source template (idempotent)
==> step 1: idempotent guard — qm status 9001 on root@pve.home.arpa
==>        template VM 9001 (tpl-cloud-fedora43) already exists; skipping bootstrap
==> step 4: packer init
==> step 5: packer build -only=proxmox-clone.fedora (force=true overwrite)
[1;32mproxmox-clone.fedora: output will be in this color.[0m

[1;31mBuild 'proxmox-clone.fedora' errored after 7 milliseconds 829 microseconds: Could not retrieve VM: vm 'tpl-cloud-fedora43' not found[0m

==> Wait completed after 8 milliseconds 6 microseconds

==> Some builds didn't complete successfully and had errors:
--> proxmox-clone.fedora: Could not retrieve VM: vm 'tpl-cloud-fedora43' not found

==> Builds finished but no artifacts were created.
```
