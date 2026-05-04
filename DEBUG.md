# DEBUG Error

Running  `./scripts/build_template.sh fedora` fails with the following output.

```shell
==> proxmox-clone.fedora: Error creating VM: clone failed: no such logical volume pve/vm-9001-disk-0
==> proxmox-clone.fedora: Deleted generated ISO from local:iso/packer457309238.iso
Build 'proxmox-clone.fedora' errored after 6 seconds 214 milliseconds: Error creating VM: clone failed: no such logical volume pve/vm-9001-disk-0

==> Wait completed after 6 seconds 214 milliseconds

==> Some builds didn't complete successfully and had errors:
--> proxmox-clone.fedora: Error creating VM: clone failed: no such logical volume pve/vm-9001-disk-0

==> Builds finished but no artifacts were created.
```
