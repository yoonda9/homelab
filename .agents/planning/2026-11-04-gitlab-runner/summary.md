# Summary: Self-hosted GitLab Runner VM (2026-11-04)

This is a PDD planning session that turned `rough-idea.md` into a reviewed design and a 13-step, test-driven implementation plan. Nothing has been implemented, and nothing has touched a live host.

## Artifacts

- `rough-idea.md`: the original brief.
- `idea-honing.md`: decisions Q1–Q8. Q6 (prune) and Q8 (entrypoint, timeout) were revised during review.
- `research/`:
  - `repo-conventions.md`
  - `existing-monitoring.md`
  - `gitlab-runner-registration.md`
  - `dind-tls-docker-executor.md`
  - `docker-upkeep.md`
  - `security-threat-model.md`
  - `security-privileged-alternatives.md`
  - `security-containment.md`
  - `security-evaluation.md`, the ranked synthesis of the security notes.
- `design/detailed-design.md`: requirements R1–R28 and done-when criteria D1–D6, the architecture, components, data models, error handling, testing strategy and alternatives.
- `implementation/plan.md`: a 13-step plan with a checklist and operator gates (⛔).
- `summary.md`: this file.

## Design in brief

- **VM:** an Ubuntu 26.04 VM, `gitlab-runner-pve` (vmid 120, 192.168.1.120, 8 vCPU / 16 GB / 150 GB).
  - It is cloned from `pkr-ubuntu26` through an extended `dev_vm`, using a `for_each` map of runners so a second node can be added.
  - It is configured by a new `gitlab_runner` Ansible role and played with `just play-runner` (`--limit gitlab_runner`).
- **Runner:**
  - `config.toml` is templated, never `register`ed, and `glrt-` tokens live in the vault.
  - The executor is Docker. Only `docker:*-dind` services run privileged.
  - `FF_NETWORK_PER_BUILD` and `FF_ENABLE_JOB_CLEANUP` are on.
  - Volumes are only `/certs/client` and `/cache`.
- **Upkeep:**
  - Package upgrades and `daemon.json` changes drain running jobs first, via SIGQUIT.
  - A daily prune timer cleans up Docker. Docuum evicts images least recently used first once disk use passes a threshold.
  - needrestart is excluded from restarting docker, containerd and gitlab-runner.
- **Isolation, in layers:**
  - Password SSH is retired. That required the cloud-init drop-in fix.
  - In-VM nftables act as the accident guard.
  - A staged Proxmox VM firewall is the enforcement layer, enabled through a lockout-safe sequence with checks on Plex impact.
  - A WAN-IP hairpin measurement checks whether jobs can reach internal services through the public IP.
  - GitLab-side settings: a locked runner, fork pipelines in the parent project off, and a max job timeout of 5400–5700 s.
- **Monitoring:** the last step. Two static scrape jobs and the `host-disk` alerts on CT 111.
- **Runbook:** `docs/runbooks/gitlab-runner.md`. It covers creating and registering the runner, adding a project, rotating a token, upgrading, cleaning disk, troubleshooting an offline or stuck runner, the security model, the compromise playbook and routine re-imaging.

## Plan in brief

| Step | What it does |
|---|---|
| 1 | Extend `dev_vm` (offline) |
| 2 | Create the VM (⛔ `tofu apply`) |
| 3 | Hardening and Docker (⛔ first plays; proves Docker on 26.04 before any later role code) |
| 4 | Install gitlab-runner with a config that has zero runners |
| 5 | Drain-gated upgrades |
| 6 | DinD-TLS smoke test (29 and 27) |
| 7 | In-VM egress fence |
| 8 | Prune timer and Docuum |
| 9 | Register lumologic (⛔ you handle the token via `ansible-vault edit`; D1, D3) |
| 10 | Proxmox firewall, in stages 1 and 2 |
| 11 | Hairpin measurement |
| 12 | Runbook completion |
| 13 | Monitoring and the final handoff (D5) |

The loop files each gate as a task and parks; it never runs a gated action.

## Areas that may need refinement

- **Live premises with stated fallbacks:**
  - Docker and GitLab publish repos for 26.04 (Step 3).
  - Docuum works with Docker 29 (Step 8). If not, the disk-gated script replaces it.
  - The exact bpg firewall resource names (Step 10).
  - The hairpin result, which decides Step 11's branch.
- **Operator pre-checks:**
  - 150 GB free on `local-lvm`;
  - `.120` is free and outside the DHCP pool;
  - whether gitlab.com needs Maintainer or Owner to create a project runner.
- **Second Proxmox node:** it needs its own template, a provider `for_each` instance, and its own firewall singletons.
- **Other Ubuntu and Fedora VMs** built from these templates probably have the same `50-cloud-init.conf` password-SSH hole. That is outside this project.

## Follow-ups (deferred)

- **Split runner manager:** an unprivileged LXC holds the tokens. This closes token theft.
- **sysbox-runc trial** on a throwaway VM, possibly Ubuntu 24.04.
- **Proxmox host hardening** beyond the VM firewall.

## Next steps

1. Review `implementation/plan.md` once more if you want to.
2. Start the Ralph loop yourself (see below). It parks at the first ⛔ gate, Step 2's `tofu apply`, after Step 1 and Step 2's offline work.
3. Clear gates as they come: approve the action, run it or let the loop run it, then resume.
