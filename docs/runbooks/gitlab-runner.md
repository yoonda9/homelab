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
- [Security model](#security-model)
- [GitLab-side hygiene](#gitlab-side-hygiene)
- [Known limits](#known-limits)

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

## Security model

Developer or above on any attached project = root on the runner VM and all its
tokens. A job runs arbitrary code on the VM's Docker daemon, so anyone who can
push a pipeline can read every runner secret on the host. Attach only trusted
projects, and treat membership of an attached project as access to the VM.

## GitLab-side hygiene

Set these in the GitLab UI for each attached project; none are enforced by the
VM.

- The runner is locked to its project (Settings > CI/CD > Runners), so it cannot
  be enabled on other projects.
- Fork pipelines in the parent project are off, so a fork cannot run jobs on the
  runner.
- The project's maximum job timeout is set to 5400-5700 s, so a stuck job cannot
  hold the VM indefinitely.
- The job-token allowlist stays at its default; do not widen it to other
  projects.

## Known limits

- No Alertmanager: alerts are evaluated by Prometheus but nothing pages anyone.
- The split manager (a separate runner-manager host from the job executor) is a
  follow-up, not built.
- Sysbox (rootless-style container isolation for job containers) is a follow-up,
  not built.
