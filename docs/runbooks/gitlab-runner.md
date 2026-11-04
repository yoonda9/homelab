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
- [Compromise playbook](#compromise-playbook)
- [Routine re-image](#routine-re-image)
- [Firewall](#firewall)
- [Hairpin](#hairpin)
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

The runner is created on the GitLab side and the repo only holds its token and
a declaration. The VM never runs `gitlab-runner register`. The token never goes
into chat, a ticket or any transcript: never paste it anywhere but the vault
editor.

1. Create a project runner in the GitLab UI: the project's Settings > CI/CD >
   Runners > New project runner. Set the attributes. None of them can be set from `config.toml`.
   - Run untagged jobs: on.
   - Locked to the current project: on.
   - Protected: off (on is optional for a project with outside contributors).
   - Maximum job timeout: **set** it to 5400-5700 s and never leave it unset.
     The invariant is: drain timeout > max job timeout + after_script + upload.
   - Description: the runner name, for example `lumologic-pve`.
2. Create the runner. GitLab shows the `glrt-` token once. Note the runner id
   from the page or from the URL.
3. On your workstation run `ansible-vault edit ansible/group_vars/all/vault.yml`
   and add the key under `vault_gitlab_runner_tokens`:

   ```yaml
   vault_gitlab_runner_tokens:
     lumologic-pve: glrt-...
   ```

   The vault stays in `group_vars/all`; do not move it.
4. In `ansible/group_vars/gitlab_runner/vars.yml` append one entry to
   `gitlab_runner_runners`, with the runner name, the host, the project, the
   runner id from step 2 and an optional `limit`:

   ```yaml
   gitlab_runner_runners:
     - name: lumologic-pve
       host: gitlab-runner-pve
       project: lumologic/lumologic
       id: 1234567
   ```

   Commit this and the vault edit in the same commit. An entry without its vault
   key fails the role's pre-render assert and renders nothing.
5. Run `just play-runner`, then a second time: the second run must report
   `changed=0`.
6. On the VM `gitlab-runner verify` must exit 0, and the runner must show online
   under the project's Settings > CI/CD > Runners.

## Add a project

There are two paths. Pick by whether the project should get its own runner or
share an existing one.

- **A new project runner.** Follow [Register a runner](#register-a-runner) for
  the new project: create the runner in the GitLab UI with the same attributes,
  add one vault key under `vault_gitlab_runner_tokens`, append one entry to `gitlab_runner_runners` in
  `ansible/group_vars/gitlab_runner/vars.yml`, and run `just play-runner`.
- **Enable an existing project runner for another project.** In the GitLab UI,
  open the other project's Settings > CI/CD > Runners and enable the existing
  runner there. There is no repo change and no play. The runner stays locked to
  its first project, so unlock it for the move first and re-lock it after.
  Attached projects share one trust boundary (see
  [Security model](#security-model)), so enable only trusted projects.

## Rotate a token

Rotate when a token leaked or the compromise playbook calls for it, and when
`gitlab-runner verify` fails with a 401 (the play fails at its verify task). A
401 means rotate: the token is dead or revoked, and the runner will not rotate
it by itself because the token has no expiry.

1. Reset the token by the runner's id. In the GitLab UI use Reset token on the
   runner, or call `POST /runners/:id/reset_authentication_token` with a personal
   access token. Never use the token-based reset endpoint: it needs the old
   token, which is the one you cannot trust. The old token stops working at
   once, so jobs on the runner fail until step 3 finishes.
2. Put the new token into the vault with
   `ansible-vault edit ansible/group_vars/all/vault.yml`, replacing the value
   under `vault_gitlab_runner_tokens`. Do not paste it into chat.
3. Run `just play-runner`. The template changes and the runner hot-reloads
   within seconds. The runner id is unchanged, so `gitlab_runner_runners` needs
   no edit. Then `gitlab-runner verify` must exit 0.

A rotated token orphans the old `runner-*-cache-*` Docker volumes, because the
token is part of their name. The scheduled `ci-docker-prune` reclaims them; run
it by hand to reclaim them sooner.

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

## Compromise playbook

Use this when a job, an attached project member, or the VM itself is suspected
of being compromised. Do the steps in order.

1. Pause the runner in GitLab (Settings > CI/CD > Runners > Pause), so no new
   job lands on the VM while you work.
2. Re-image the VM with `just runner-reimage NAME`. This recipe is planned (it
   arrives with the Proxmox firewall step) and does not exist yet; until it
   does, use `tofu apply -replace` on the VM by hand, and confirm the VM is
   not left without its firewall before unpausing.
3. Delete and recreate the runner in GitLab, or use the ID-based token reset,
   so the old authentication token is dead. A re-imaged VM must not reuse the
   token the compromised one held.
4. Rotate any CI variables the runner could have seen: every variable of every
   attached project, plus any deploy key or registry credential a job used.

## Routine re-image

Re-image the VM monthly and on upgrades, using the same procedure as steps 2-3
of the compromise playbook, with the runner drained first instead of paused
for cause. The SSH host key changes on every re-image, so remove the old entry
from `~/.ssh/known_hosts` (`ssh-keygen -R 192.168.1.120`) before the next
login.

## Firewall

The Proxmox VM firewall drops VM 120's egress to RFC1918, the tailnet range
(`100.64.0.0/10`), multicast and IPv6 at the hypervisor, and blocks spoofing.
Root in the guest cannot undo it. It is off until three switches are all on:
the datacenter `enable`, the NIC's `firewall=1` (set at VM creation), and the
VM's own options `enable`. Every resource sits behind the root variable
`gitlab_runner_firewall_stage`: `0` (default) creates none, `1` creates the
per-VM objects (ipset, options, rules), `2` also flips the datacenter switch.
An ordinary `just apply` at stage 0 never touches any of it. Both applies are
operator-run. Do not run them from the loop.

### Enable sequence

1. Pre-flight, read-only on `pve`:
   - `pve-firewall status`;
   - read `/etc/pve/firewall/cluster.fw` and `nodes/pve/host.fw`, and import any
     existing rules first;
   - record `sysctl net.bridge.bridge-nf-call-iptables` and `conntrack -C`.
     The datacenter firewall turns on bridge netfilter and conntrack for all
     `vmbr0` traffic, CT 110's Plex streams included, which
     `input_policy = ACCEPT` does not cover;
   - take a Plex latency baseline with `scripts/measure_plex_latency.py`;
   - `grep -l '^enable: 1' /etc/pve/firewall/*.fw` must list nothing. Record
     `grep -l firewall=1 /etc/pve/{qemu-server,lxc}/*.conf` for the re-check
     in step 5.
2. Keep a root SSH session to `pve` open, and the console at hand, for the
   whole sequence.
3. Apply A: set `gitlab_runner_firewall_stage = 1` and apply. The plan must
   show only VM 120 firewall objects and **0 to change/destroy** on the VM.
   Stop otherwise.
4. Apply B: set `gitlab_runner_firewall_stage = 2` and apply. The node firewall
   goes off first, then the datacenter on with `input_policy = "ACCEPT"`.
5. Verify immediately (the verification list):
   - the PVE UI still answers from the LAN and the tailnet;
   - CT 110 and CT 111 still serve, and a Plex latency run matches the baseline;
   - from VM 120, `gitlab.com` is reachable while `.111:443`, `.50:8006` and
     `.110:32400` time out;
   - `curl` of `:9252/metrics` from CT 111 works;
   - SSH from the LAN works, and `:9100` from a non-`.111` host is refused;
   - the guests recorded in step 1 are still unfiltered.
6. Root-proof negative control: drain the runner first
   (`systemctl stop gitlab-runner`), because the flush wipes Docker's NAT and
   the restore restarts dockerd. In VM 120 run `nft flush ruleset` and repeat
   the `.111` probe: it must still fail. Restore with
   `systemctl restart ci-egress docker gitlab-runner`.

### Rollback

From the open root session on `pve`, or the console: `pve-firewall stop`.
Persistently, set `enable: 0` in `/etc/pve/firewall/cluster.fw` and set
`gitlab_runner_firewall_stage` back to `1` or `0` before the next apply.

### Re-image

`qm destroy` likely deletes `/etc/pve/firewall/120.fw`, so a re-image must
replace the firewall objects with the VM. Use `just runner-reimage <name>`,
which passes `-replace` for the VM and that runner's ipset, options and rules
in one apply. Before you unpause the runner, re-run `pve-firewall status` and
the `.111` probe from VM 120 (it must fail); unpause only when both pass.

## Hairpin

Open question, not yet measured: whether a job on VM 120 can reach Traefik's
internal-only routers, or the router's own admin ports, by connecting to the
router's public (WAN) IP. Traefik's `internal-allowlist` admits
`192.168.1.0/24`, so a hairpin that presents the VM's source address `.120`
would be let in. Measurement is an operator-gated live step (plan Step 11);
this section holds the result, either the evidence or an explicit acceptance,
once that step runs.

Measure from VM 120:

```sh
curl -sk --resolve whoami.<domain>:443:<WAN IP> https://whoami.<domain>/
```

The whoami response echoes `RemoteAddr` / `X-Real-Ip`, which is the source IP
the router presents (`.120`, or `.1` if it SNATs). Repeat for one internal-only
router such as grafana, and probe the router's admin ports (80, 443, 22) on the
WAN IP. The PVE RFC1918 drop does not cover a hairpin to the public address.

Outcome: blocked means record the evidence here. Open with source `.120` means
narrow `internal-allowlist` to exclude the runner IPs. Open with source `.1`, or
router admin reachable, means add a PVE egress DROP to the WAN IP, which is
dynamic and needs a runbook check when the IP changes. Otherwise record the
operator's explicit acceptance of the risk.

## Known limits

- No Alertmanager: alerts are evaluated by Prometheus but nothing pages anyone.
- The split manager (a separate runner-manager host from the job executor) is a
  follow-up, not built.
- Sysbox (rootless-style container isolation for job containers) is a follow-up,
  not built.
