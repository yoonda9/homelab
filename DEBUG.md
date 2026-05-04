# DEBUG Error

Running  `./scripts/build_template.sh fedora` fails with the following output.

It seems like the cloud-init isn't actually getting picked up properly and so the user and SSH are not being set up as expected.

```shell
==> proxmox-clone.fedora: Timeout waiting for SSH.
==> proxmox-clone.fedora: Timeout waiting for SSH.
==> proxmox-clone.fedora: Step "StepConnect" failed, aborting...
==> proxmox-clone.fedora: aborted: skipping cleanup of step "stepTypeBootCommand"
==> proxmox-clone.fedora: aborted: skipping cleanup of step "StepHTTPServer"
==> proxmox-clone.fedora: aborted: skipping cleanup of step "stepStartVM"
==> proxmox-clone.fedora: aborted: skipping cleanup of step "stepUploadISO"
==> proxmox-clone.fedora: aborted: skipping cleanup of step "StepDownload"
==> proxmox-clone.fedora: aborted: skipping cleanup of step "StepCreateCD"
==> proxmox-clone.fedora: aborted: skipping cleanup of step "StepMapSourceDisks"
==> proxmox-clone.fedora: aborted: skipping cleanup of step "StepSshKeyPair"
Build 'proxmox-clone.fedora' errored after 30 minutes 11 seconds: Timeout waiting for SSH.

==> Wait completed after 30 minutes 11 seconds

==> Some builds didn't complete successfully and had errors:
--> proxmox-clone.fedora: Timeout waiting for SSH.

==> Builds finished but no artifacts were created.
```
