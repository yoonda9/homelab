# Idea Honing — Self-hosted GitLab Runner

Requirements clarification, one question at a time. Source: [rough-idea.md](rough-idea.md).

## Q1. How does the runner VM get its operator SSH key and lose the template's `user`/`password` login?

The `pkr-ubuntu26` template ships `user`/`password` with NOPASSWD sudo and password SSH. `tofu/modules/dev_vm` passes no keys, and `test_no_consumer_cidata_variables` guards that. Options:
- (a) Extend `dev_vm` with an optional `ssh_public_keys` + static `ipv4_cidr`/`gateway` (empty default keeps current behaviour); polarity-flip the guard to "optional, default empty". Ansible reaches the VM by key from the first run, and `common` disables password auth.
- (b) Leave `dev_vm` bare; the first Ansible run logs in with `user`/`password` (`--ask-pass`/sshpass), installs the key, then hardens.
- (c) A separate `vm_service` module for long-lived service VMs, leaving `dev_vm` for dev boxes.

**Answer:** (a) Extend `dev_vm` with optional `ssh_public_keys` and a static IPv4/gateway, both empty by default so existing dev-VM behaviour is unchanged. The `test_no_consumer_cidata_variables` guard is polarity-flipped to "optional, empty by default" in the same commit. Ansible reaches the VM by key from the first run; `common` disables password SSH.

## Q2. What vmid and static IP does the first runner VM (on `pve`) get?

The existing convention is vmid = last IP octet (110 plex, 111 docker-host, `tofu/locals.tf` `service_ids` / `net`). The design adds a `runners` map keyed by name with `{ node, vm_id, ip_cidr, ... }` so a second node is one more entry.

**Answer:** vmid **120**, IP **192.168.1.120/24** on `pve` (operator to confirm the address is free and outside the router's DHCP pool). A second-node runner later takes 121 / .121.

## Q3. Which Docker version does the DinD smoke test pin, given `docker:27` is unmaintained upstream (Docker Hub supports 29.x only; the VM's engine will be docker-ce 29.x)?

The Done-when criterion names `docker:27-dind` + `docker:27` because that is what lumologic's job uses.

**Answer:** It doesn't matter for the runner itself: each job picks its own image, and the runner only supplies privileged mode and the `/certs/client` volume. The smoke test uses the current stable line (docker 29.x dind + client), with the tag as a single variable. Pinning to the CI job's exact 27 tag was considered and dropped as not worth carrying.

## Q4. Is monitoring (node-exporter + gitlab-runner `:9252` scrape on docker-host's Prometheus, plus the runner job in the disk alerts) part of this project, or a follow-up?

It touches CT 111 (`docker_host` render + Prometheus restart) and two large guard files, but the runner works without it.

**Answer:** Include it, as the **final** plan step, behind its own operator gate because it touches CT 111. The runner is complete and usable before that step.

## Q5. When a playbook run finds a gitlab-runner / docker-ce / containerd.io upgrade pending while jobs are running, what should it do?

With the SIGQUIT drain drop-in, stopping the service waits for running jobs (up to the 90-min job timeout). Without it, the upgrade kills them.

**Answer:** Drain, then upgrade. A systemd drop-in (`KillSignal=SIGQUIT`, `KillMode=mixed`, long `TimeoutStopSec`) makes stop graceful. The play detects a pending upgrade of any of the three packages, stops the runner (waiting for running jobs), upgrades, and starts it. A run can block up to ~90 min; no job is lost.

## Q6. What prune schedule and retention?

**Answer:** Daily systemd timer. Prune images and build cache unused for 7 days (`--filter until=168h`), plus the runner's labelled cache/build volumes (`docker volume prune -a --filter label=com.gitlab.gitlab-runner.managed=true`; volume prune has no age filter, and in-use volumes are skipped). Retention is a variable. The next job after a volume prune re-fetches ~360 MB of LFS.

**Revised in design review (2026-11-04):** `image prune --filter until=` counts from the upstream build date, not last use, so it would wipe most images nightly. Images are now evicted by **Docuum**: LRU by last use above a disk threshold (default 60%), installed from a pinned release binary with its sha256 checked. The daily timer keeps containers, build cache, networks, labelled volumes and dangling images.

## Q7. Should CI jobs be firewalled off from the rest of the LAN?

A privileged job is root on the VM and can reach anything on 192.168.1.0/24 (PVE API .50, CT 110/111, the router). The runner itself needs only outbound HTTPS to gitlab.com and registries.

**Answer:** Yes. In-VM nftables drop egress from the VM and its containers to 192.168.1.0/24, except the gateway (DNS/routing). Inbound SSH from the LAN and the Prometheus scrape from .111 only stay open. Recorded limitation: a privileged job is root and could flush the rules, so this guards against accidents, not a determined attacker. The Proxmox-firewall alternative (tamper-proof from inside the VM) was considered and noted as a possible later hardening.

## Q8. After the security research, which controls go into the design?

Ranked options are in `research/security-evaluation.md`. The main risk is root-on-VM, which leads to token theft and a LAN pivot, not a VM escape.

**Answer:** Adopt the following:
- **(1)** Privileged only for `docker:*-dind` services (`privileged = false`, `services_privileged = true`, `allowed_privileged_services`), plus `disable_entrypoint_overwrite`, `FF_NETWORK_PER_BUILD` and `FF_ENABLE_JOB_CLEANUP`. **Revised in the fresh review:** `disable_entrypoint_overwrite` is dropped, because runner source applies it to job containers too, which silently breaks `image: {entrypoint: [...]}` overrides (R1).
- **(2)** Close the IPv6 egress gap, and measure the WAN-IP hairpin to Traefik's internal allowlist, closing it if it is open.
- **(3)** GitLab-side hygiene:
  - lock each runner to its project;
  - turn off fork pipelines running in the parent;
  - set the max job timeout to 5400–5700 s (below the 6000 s drain timeout; never unset);
  - keep the job-token allowlist at its default;
  - add the runbook rule "Developer+ on an attached project = root on the runner".
- **(4)** A Proxmox VM firewall from tofu: egress block plus anti-spoofing that can't be undone from inside the VM. It gets its own gated step with a lockout-safe enable sequence.

Not adopted, recorded as follow-ups:
- **(5)** split runner manager (tokens off the job VM);
- **(6)** sysbox-runc trial.

Routine re-imaging and the compromise playbook go into the runbook, since they are documentation only.
