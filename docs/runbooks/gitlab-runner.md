# Runbook: self-hosted GitLab Runner (VM 120)

Operator runbook for the GitLab Runner VM `gitlab-runner-pve` (VM 120,
`192.168.1.120`). Sections are filled in as the plan's steps land; a section
whose body says "not yet written" belongs to a later step.

## Table of contents

- [Create the VM](#create-the-vm)
- [Register a runner](#register-a-runner)
- [Add a project](#add-a-project)
- [Rotate a token](#rotate-a-token)
- [Upgrade](#upgrade)
- [Clean disk](#clean-disk)
- [Troubleshooting](#troubleshooting)

## Create the VM

The VM is declared in `tofu/locals.tf` (`gitlab_runners` map) and created by the
`gitlab_runner` module call in `tofu/main.tf`. `tofu apply` is operator-run.

### Pre-checks

1. Storage: on the Proxmox host, `pvesm status` must show at least 150 GB free
   on `local-lvm`.
2. Address: `192.168.1.120` must be free and outside the router's DHCP pool.
   `ping -c2 192.168.1.120` must fail and `arp -n | grep 192.168.1.120` must be
   empty.
3. Keys: `local.operator_ssh_keys` is non-empty (the plan fails otherwise).

### Plan and apply

```sh
just plan     # expect exactly one VM to add, plus one terraform_data keys guard
just apply    # operator-run; interactive confirmation
```

Then `just gen-inventory` should list `gitlab-runner-pve`, and
`ssh user@192.168.1.120` should log in with the operator key.

### Recovery via the guest agent

If SSH does not come up, use the QEMU guest agent from the Proxmox host:

```sh
qm guest exec 120 -- /bin/sh -c 'ip -4 addr; systemctl status ssh'
```

Fix the address or keys in place, or destroy and recreate the VM
(`tofu destroy -target=module.gitlab_runner`, then `just apply`).

## Register a runner

Not yet written.

## Add a project

Not yet written.

## Rotate a token

Not yet written.

## Upgrade

Not yet written.

## Clean disk

Not yet written.

## Troubleshooting

Not yet written.
