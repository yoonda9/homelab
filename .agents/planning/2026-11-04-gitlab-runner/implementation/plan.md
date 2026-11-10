# Implementation Plan: Self-hosted GitLab Runner VM

This plan is derived from [../design/detailed-design.md](../design/detailed-design.md). Requirement IDs (`R*`), done-when IDs (`D*`) and § references point into that document. The design, `../idea-honing.md` and `../research/` are available during implementation and are not restated here.

There are thirteen steps. Each one is test-driven: offline guards are written with or before the code, and a guard counts only once it has gone red against a mutated artifact (design §7, "Mutation discipline"). Every step ends with `just test`, `just fmt` and `tofu plan` green (R21).

## Operator gates (R22)

- ⛔ marks an action that changes a live host or needs a GitLab token. The loop doesn't run it. Ralph's `human.interact` is not wired up in this repo, so the loop **files the gate as a task and parks** once every item in the ready set is gated. It doesn't stop to wait while deploy-independent work remains.
- **No deploy leakage.** Code may land ahead of its gate only when no *earlier* gated command would deploy it.
  - **Tofu:** every Proxmox firewall resource sits behind `gitlab_runner_firewall_stage`, which defaults to `0` (design §4.10). Firewall HCL can merge early, and an ordinary `just apply` still shows no firewall diff. Only the operator changes the stage.
  - **Ansible:** changes to `docker_host` (Steps 11 and 13) don't land until the step's own gate is approved, because any play against CT 111 would ship them. Runner role code reaches only the runner VM, via `--limit gitlab_runner`.
- **Proof first.** No role code for Step 4 or later lands until Step 3's live play has passed. Docker on 26.04 is the largest unknown, and stacking four slices on top of it risks reworking all of them.

## Checklist

- [x] **Step 1:** `dev_vm` gains optional keys, static IPv4/DNS, vmid, firewall and cpu_type; the provider pin moves to `>= 0.108.0` — done (1a–1e)
- [x] **Step 2:** Root tofu `gitlab_runners` map, inventory group with static fallback, `play-runner`, runbook skeleton; ⛔ `tofu apply` creates VM 120 — done (2a–2e + operator gate f7e5)
- [x] **Step 3:** Role slice 1: hardening (R20, R28) and Docker CE with a role-owned `daemon.json` and a drain-safe restart; ⛔ first two plays — done (3a–3e, d41e + operator gate 4344)
- [x] **Step 4:** gitlab-runner from its apt repo and a templated `config.toml` with zero runners (R10–R13) — done (4a–4c + operator gate 00a9)
- [x] **Step 5:** Drain drop-in and drain-gated upgrades (R16) — done (5a, 5b + operator gate d3c6; the live drain ran with builds=0, so a drain that waits on a real job is first seen in Step 9)
- [x] **Step 6:** DinD-TLS smoke test and `just runner-smoke` (D2) — done (6a–6b + operator gate e2d0)
- [x] **Step 7:** In-VM nftables `ci_egress` and IPv6 off (R19) — done (+ operator gate 00c3)
- [x] **Step 8:** Upkeep: the daily prune timer plus Docuum image LRU (R15) — done (+ operator gate e7ba; Docuum passed its live check, no fallback)
- [x] **Step 9:** ⛔ Register the lumologic runner; runner online and jobs running (D1, D3) — done (9a, 9b, missing-token arm with 4c + operator token step bf62502; `verify` valid, online, retried pipeline ran here, privileged split seen on `django-tests`)
- [ ] **Step 10:** ⛔ Proxmox VM firewall, staged, through the lockout-safe sequence; `runner-reimage` (R24, D6) — build done (10a–10e); open: gate 2506, unblocked since f7e5 closed (created under an earlier loop: list it with `ralph tools task ready --all`)
- [ ] **Step 11:** ⛔ WAN-IP hairpin measurement and its fix or explicit acceptance (R25, D6)
- [ ] **Step 12:** Runbook completion: security model, compromise playbook, re-image, GitLab hygiene (R26, R27, D4) — 12a–12d, 12f, 12g done; open: operator gate f476 (12e UI walkthrough), and the Steps 2–11 cross-check after Step 11
- [ ] **Step 13:** ⛔ Monitoring on CT 111 (R17); final handoff message (D5)

---

## Step 1: Extend `tofu/modules/dev_vm` (R8)

**Objective.** The module can produce a VM with a known vmid, static address, DNS, operator key, explicit CPU type and NIC firewall flag. Every new input is optional and empty by default, so today's behaviour is unchanged.

**Guidance.**
- Add the §4.1 variables.
- Render `initialization.user_account` and `initialization.dns` with dynamic blocks, only when set. Validate that `ipv4_gateway` is set whenever `ipv4_cidr` is.
- Add the `ipv4_configured` output.
- Change `versions.tf` to `>= 0.108.0`.
- Update the module README.
- Confirm with a grep that no root module calls `dev_vm` today, so the `cpu_type = "host"` default changes no state.

**Tests (first).**
- In `scripts/test_dev_vm_module_shape.py`, polarity-flip `test_no_consumer_cidata_variables` in the same commit; don't delete it. The new form asserts that the consumer variables exist, are optional, and default to empty or DHCP.
- Arms for:
  - the provider pin;
  - the conditional `user_account` and `dns` blocks;
  - the gateway validation;
  - `firewall` defaulting to `false` and `cpu_type` to `"host"`.
- `tofu validate`.
- Mutants, each of which must go red:
  - restore `~> 0.104.0`;
  - make `user_account` unconditional;
  - default `firewall` to `true`.

**Integration.** Standalone. Steps 2 and 10 consume it.

**Demo.** `just test` is green. In a scratch root, `tofu plan -refresh=false` shows `user_account` and the static `ip_config` only when the new inputs are passed.

## Step 2: Root tofu, inventory, `play-runner`, runbook skeleton; ⛔ create VM 120

**Objective.** `tofu plan` shows exactly one new VM. The inventory has a `gitlab_runner` group. The runner can be played without touching CT 110 or CT 111.

**Guidance.**
- `locals.tf`: add the `gitlab_runners` map.
- `main.tf`: `module "gitlab_runner"` with `for_each`.
  - It reuses the **existing** `local.operator_ssh_keys` and adds a precondition that the list is non-empty.
  - It passes `firewall = true`, which stays inert until Step 10 (§4.10). Setting it at creation means Step 10 needs no VM change or restart.
- `outputs.tf`: `gitlab_runners`.
- `scripts/gen_inventory.py`: add the `gitlab_runner` group (`ansible_user: user`, `ansible_become: true`) with a static fallback IP, the same pattern CT 110 and CT 111 use.
- `justfile`: add `play-runner` (`--limit gitlab_runner`).
- `docs/runbooks/gitlab-runner.md`: create the section headings. Fill in **create the VM**: the pre-checks (`pvesm status` shows 150 GB free on `local-lvm`; `.120` is free and outside DHCP), `just plan`/`just apply`, and recovery via `qm guest exec`.

**Tests.**
- `test_gitlab_runner_tofu_shape.py` (new):
  - the map drives `for_each`;
  - `node` is a per-entry field;
  - vmid 120 and IP `.120`;
  - the keys precondition is present;
  - no firewall resource exists outside the stage gate.
- `test_gen_inventory_shape.py` (**new**; today only a regex in `test_ansible_layout_shape.py` covers the inventory):
  - the group renders from a fixture output;
  - the static fallback works with no output;
  - existing groups stay byte-identical.
- `test_justfile_shape.py`: a `play-runner` arm for `--limit gitlab_runner`. Mutant: drop the limit; it must go red.
- `test_gitlab_runner_runbook_shape.py` (new): pins only the sections that exist so far.

**Integration.** The root module consumes Step 1's `dev_vm` changes. The inventory feeds `play-runner`.

**Demo.**
- `tofu plan` (read-only) shows **one VM to add and nothing else**.
- ⛔ **Gate: `tofu apply`**, after the pre-checks.
- `just gen-inventory` lists `gitlab-runner-pve`, and `ssh user@192.168.1.120` logs in with the operator key.

## Step 3: Role slice 1: hardening and Docker (R10, R14, R18, R20, R28)

**Objective.** A converged, idempotent VM:
- password SSH off and the `user` password locked;
- needrestart excluded from docker, containerd and gitlab-runner;
- Docker CE from the official repo, with bounded logs;
- `daemon.json` changes that can never kill a job.

**Guidance.**
- **Premise check first, read-only.** Confirm that download.docker.com and packages.gitlab.com publish the 26.04 codename suite. The design review found both; re-confirm. If either is missing, stop and re-plan.
- Create the §4.3 layout with only this slice's tasks.
- `harden.yml`:
  - the `00-homelab-hardening.conf` sshd drop-in;
  - remove `50-cloud-init.conf`;
  - lock the `user` password;
  - the needrestart `conf.d` exclusion, only if needrestart is installed.
- Meta dependency on geerlingguy.docker with:
  - `docker_packages_state: present`;
  - `docker_daemon_options: {}`;
  - `docker_restart_handler_state: started`;
  - `docker_users: []`.
- The role templates `daemon.json` (log caps) itself.
- The `Drain and restart docker` handler stops gitlab-runner gracefully if the unit exists, restarts docker, then starts gitlab-runner if it exists.
- Add the `site.yml` play after `common`, and add Ubuntu to `common`'s meta platforms.

**Tests.** First arms of `test_gitlab_runner_role_shape.py`:
- the sshd drop-in and the `50-cloud-init.conf` removal;
- the needrestart exclusion names all three units;
- the geerlingguy vars as above;
- `daemon.json` notifies the drain handler (mutant: notify a bare docker restart);
- log caps 10m × 3;
- `docker_users` empty;
- no cross-role `src`.

Plus `ansible-lint --profile production` and `--syntax-check` through the gate.

**Integration.** The first play against the Step 2 VM. `common` runs on it too.

**Demo.**
- ⛔ **Gate: `just play-runner` twice.** The second recap shows `changed=0`.
- `sshd -T | grep -i passwordauthentication` prints `no`, and a `user`/`password` SSH login is refused.
- `docker info` shows `json-file` with the log opts.

## Step 4: gitlab-runner and templated `config.toml`, zero runners (R10–R13)

**Objective.** gitlab-runner is installed and running, polling nothing because there are zero `[[runners]]`. The whole config is rendered from the template.

**Guidance.**
- `install.yml`:
  - GitLab apt key and deb822 source;
  - the `gitlab-runner` and `gitlab-runner-helper-images` packages, installed with `NO_DOCKER_PRUNE=1`.
- `config.yml`:
  - the pre-render token assert;
  - `template` of the full §4.4 file, with the privilege split and feature flags and no `disable_entrypoint_overwrite`, using `validate:` with `tomllib`;
  - `verify`, only when runners exist;
  - a `listen_address` change notifies the drain-restart.

**Tests.** `test_gitlab_runner_config_shape.py` renders through **Ansible itself**: `mise exec -- ansible localhost -c local -m ansible.builtin.template` into a temp dir, then `tomllib`. The gate's Python has no `jinja2`, and the template uses Ansible filters. Arms:
- an empty list gives zero runners;
- with two hosts, only the current host's runner is rendered;
- `volumes` exactly `["/certs/client","/cache"]`, with no `:`;
- `pull_policy`, the default image, `concurrent`, `limit`, `request_concurrency`, `shm_size` and `listen_address`;
- `privileged = false`, `services_privileged = true`, the dind pattern and both feature flags;
- `disable_entrypoint_overwrite` and `token_expires_at` absent;
- no `register` anywhere in the role.

Mutants: `privileged = true`, a host bind, and an added `token_expires_at`.

**Integration.** Extends the role from Step 3. `config.yml` runs after `install.yml`.

**Demo.**
- ⛔ **Gate: `just play-runner` twice**; the second run shows `changed=0`.
- `gitlab-runner status` shows it running, and `config.toml` is root 0600 with no `[[runners]]`.

## Step 5: Drain drop-in and drain-gated upgrades (R16)

**Objective.** Package upgrades never kill a job. An idle run with nothing pending changes nothing.

**Guidance.**
- `files/gitlab-runner-drain.conf`: `KillSignal=SIGQUIT`, `KillMode=mixed`, `TimeoutStopSec` from the var, plus the daemon-reload handler.
- `upgrade.yml`:
  - the §4.5 `apt-get -s` probe (`changed_when: false`);
  - the drain → upgrade (`NO_DOCKER_PRUNE=1`) → start block with `async`, gated on `^Inst `.
- Runbook: the **upgrade** section, including the invariant that the drain timeout must exceed the max job timeout plus `after_script` plus upload.

**Tests.** Role-shape arms:
- the drop-in values, with the timeout above 5400 and read from the var;
- the probe is `changed_when: false`;
- the block's `when` reads `^Inst `;
- no check-mode `apt` task;
- `async` is at least the drain timeout.

Mutant: gate the block on `pending is changed`; it must go red.

**Integration.** `upgrade.yml` runs between `install.yml` and `config.yml`. The Step 3 drain handler reuses the same drop-in.

**Demo.**
- ⛔ **Gate: `just play-runner` twice**, with `changed=0`.
- ⛔ **Gate, live drain:**
  - downgrade both runner packages one version on the VM;
  - start a long-running labelled container;
  - run `just play-runner`;
  - the log shows stop → wait → upgrade → start, and the runner is back at the latest version.

## Step 6: DinD-TLS smoke test (D2)

**Objective.** One command proves that a privileged dind with TLS works on this VM, including its negative controls.

**Guidance.**
- `templates/dind-tls-smoke.sh.j2`: the `research/dind-tls-docker-executor.md` §3 script. The tag argument defaults to `gitlab_runner_smoke_tag`.
- `smoke.yml` installs it at `/usr/local/sbin/`. The play doesn't run it.
- `justfile`: add `runner-smoke [TAG]`.

**Tests.**
- Role-shape arms:
  - mode 0755;
  - a cleanup `trap`;
  - both negative controls (no-cert fails, 2375 unreachable);
  - the default tag comes from the var.
- `bash -n` on the rendered script, plus `shellcheck` if the gate has it.
- A `test_justfile_shape.py` arm for `runner-smoke`.

Mutant: delete the no-cert control; it must go red.

**Integration.** Uses Step 3's Docker. Step 8 checks Docuum against these images.

**Demo.**
- ⛔ **Gate: `just play-runner`, then `just runner-smoke` and `just runner-smoke 27`.** The second run is the brief's literal `docker:27`; Q3 chose 29 as the default.
- Each run prints `<version> tls-ok`, the nested busybox runs, and both negative controls fail as expected.
- `docker ps -a` shows nothing left over.

## Step 7: In-VM egress firewall (R19)

**Objective.**
- Containers and the VM can't reach `192.168.1.0/24`, except DNS on `.1`.
- The metrics ports answer `.111` and loopback only.
- IPv6 is off.
- Docker's own rules survive reloads.

**Guidance.**
- `firewall.yml`:
  - `ci-egress.nft.j2` (§4.6), with `oif lo` and `iif lo` accepted first;
  - `ci-egress.service`: `Type=oneshot`, `RemainAfterExit=yes`, `Before=docker.service`;
  - the IPv6-off sysctl;
  - the reload handler.
- Never touch `/etc/nftables.conf`.

**Tests.** Role-shape arms:
- no `flush ruleset` anywhere;
- the LAN drop in both `output` and `forward`;
- only port 53 to the gateway is accepted;
- the IPv6 drop;
- both `lo` accepts;
- the input chain admits only `gitlab_runner_metrics_allowed_from`;
- `RemainAfterExit=yes`.

Mutants: remove the `forward` drop, and add `flush ruleset`.

**Integration.** `firewall.yml` runs before `install.yml`, so the fence is up before the runner polls. Step 6's smoke test must still pass afterwards.

**Demo.**
- ⛔ **Gate: `just play-runner` twice**, with `changed=0`.
- `docker run --rm alpine wget -T3 http://192.168.1.111` fails, while `wget -T5 https://gitlab.com` succeeds.
- `curl -s 127.0.0.1:9252/metrics` on the VM is not dropped. A connection refused is fine; nothing listens there until a runner exists.
- `nft list tables` shows both Docker's tables and `inet ci_egress`.
- After `systemctl restart ci-egress`, `just runner-smoke` still passes.

## Step 8: Upkeep: prune timer and Docuum (R15)

**Objective.** Disk usage stays bounded without evicting images that are in active use.

**Guidance.**
- `prune.yml`:
  - the `ci-docker-prune` script, service and timer from §4.7, with no `image prune -a`;
  - the Docuum musl binary via `get_url` with the pinned version and a `sha256:` checksum;
  - `docuum.service`.
- **Checksum provenance.** Use the release's published checksum if there is one. Otherwise compute it once from the downloaded asset and record how in a comment beside the var.
- **Fallback if Docuum fails the live check:** replace it with the disk-gated variant, which runs `image prune -af` from the prune script only when `/` usage passes `gitlab_runner_docuum_threshold`. Record the swap in the design's alternatives section.
- Runbook: the **clean disk** section (`docker system df`, a manual prune, Docuum's journal, `qm resize`).

**Tests.** Role-shape arms:
- a label-filtered `volume prune -a` is present;
- `image prune -a` is absent;
- `until=` reads its value from the var;
- the timer is daily with `Persistent=true`;
- `get_url` has both a checksum and a pinned version;
- the unit passes `--threshold` and `--min-age` from the vars.

Mutants: delete the checksum, and add `image prune -a --filter until=`.

**Integration.** Uses Step 3's Docker, and Step 6's images for the live check.

**Demo.**
- ⛔ **Gate: `just play-runner` twice**, with `changed=0`.
- `systemctl list-timers ci-docker-prune.timer` shows the next run.
- `systemctl start ci-docker-prune` succeeds.
- After `just runner-smoke`, `journalctl -u docuum` records the smoke images. This is the live Docker 29 check; if it fails, take the fallback above.

## Step 9: ⛔ Register the lumologic runner (R12, R26; D1, D3)

**Objective.** `lumologic/lumologic` has an online project runner on this VM, configured only from the template, and its retried pipeline runs here.

**Guidance.**
- ⛔ **Gate: GitLab token.** The operator does the token handling; **the token never enters the loop's transcript**.
  - They create the project runner with the §5.3 attributes: untagged on, locked, max timeout **set** to 5400–5700 s.
  - They run `ansible-vault edit` to add `vault_gitlab_runner_tokens.lumologic-pve` themselves.
  - They supply the runner id.
- The loop prepares the `lumologic-pve` entry in `group_vars/gitlab_runner/vars.yml`. The operator commits it together with the vault edit, per the §5.1 sequencing.
- Runbook sections:
  - create/register a runner;
  - add a project, both paths;
  - rotate a token, using the ID-based reset and never the token-based one; a 401 from `verify` means rotate;
  - offline/stuck troubleshooting.

**Tests.**
- Config-shape arm, with a fixture vault: an entry whose key is missing fails the pre-render assert.
- The real vault's contents are proven only by the live `verify`. The gate decrypts the real vault when a password is present (`run_gate.py` `setdefault`), so no test may print vault values.
- `test_secrets_scoped_to_all_group` stays green.
- Runbook-shape arms for the new sections.

**Integration.** Fills Step 4's template. Real jobs now get the protections from Steps 4, 5 and 7.

**Demo.**
- ⛔ **Gate: `just play-runner` twice**, with `changed=0` (D1).
- `gitlab-runner verify` exits 0 (D1).
- The runner shows online under lumologic → Settings → CI/CD → Runners (D3).
- ⛔ The operator turns off instance runners and retries the failed pipeline. Its jobs list this runner.
- During a dind job in that pipeline, `docker inspect` shows the job container with `Privileged=false` and the dind service with `true`.

## Step 10: ⛔ Proxmox VM firewall (R24; D6)

**Objective.**
- VM 120's egress to RFC1918, the tailnet range, multicast and IPv6 is dropped at the hypervisor, and so is spoofing.
- Root in the guest can't undo it.
- `pve`, CT 110 and CT 111 are unaffected.
- A re-image can't leave the VM without its firewall.

**Guidance.**
- Add the §4.10 resources, all behind `gitlab_runner_firewall_stage`, which defaults to `0`.
- The singletons set `input_policy = "ACCEPT"` and turn the node firewall off.
- Confirm the exact bpg resource names against the pinned provider before writing HCL. The design review saw `proxmox_node_firewall`, `proxmox_virtual_environment_cluster_firewall` and the firewall `options`, `ipset` and `rules` resources in 0.110.0.
- `justfile`: add `runner-reimage NAME`, which does `-replace` for the VM and that runner's firewall objects together.
- Runbook:
  - the enable sequence;
  - rollback (`pve-firewall stop`);
  - the verification list;
  - the re-image procedure, which re-checks the firewall before unpausing.

**Tests.** `test_gitlab_runner_firewall_shape.py`:
- `input_policy = "ACCEPT"`, pinned by cell identity. Mutant: delete the line, which falls back to bpg's DROP; it must go red.
- The node firewall is disabled.
- `radv`, `ipfilter` and `macfilter` are set.
- The ipset holds the runner's IP.
- The drops cover RFC1918, `100.64.0.0/10` and IPv6.
- Stage `0` gives no firewall resources, `1` no datacenter switch, `2` everything.
- `dev_vm`'s `firewall` still defaults to false.

Add a `test_justfile_shape.py` arm: `runner-reimage` replaces both the VM and the firewall objects.

**Integration.** Builds on the tofu from Steps 1–2 (the NIC flag is already set). Step 7's in-VM table stays as the accident guard.

**Demo.** Each item is a ⛔ gate:
1. The read-only pre-flight (§4.10 step 1): the bridge-netfilter sysctl, the conntrack count and a Plex latency baseline.
2. Apply A: stage `1`. The plan shows only VM 120 firewall objects and **0 to change/destroy** on the VM.
3. Apply B: stage `2`, with a root SSH session to `pve` held open.
4. The whole §4.10 step 5 list, including a Plex latency run against the baseline and a curl of `:9252` from CT 111.
5. Drain the runner. Run `nft flush ruleset` in VM 120; the `.111` probe must still fail. Restore with `systemctl restart ci-egress docker gitlab-runner`.

## Step 11: ⛔ Hairpin measurement and closure (R25; D6)

**Objective.** Measure, rather than assume, whether a job can reach Traefik's internal-only routers or the router's own admin through the WAN IP. Then close the path or accept it explicitly.

**Guidance.**
- ⛔ **Gate: live measurement** from VM 120, following §4.10:
  - the `whoami` probe through the WAN IP, which shows the source IP the router presents, since Traefik has no access log;
  - one internal-only router, such as grafana;
  - the router's admin ports.
- Then branch:
  - **Blocked:** record the evidence in the runbook. No code.
  - **Open, source `.120`:** narrow `internal-allowlist` in `docker_host` so it excludes the runner IPs, and extend `test_traefik_config_shape.py` by cell identity. Add a `play-docker-host` recipe (`--limit docker_host`) and its justfile-shape arm. ⛔ **Gate:** `just play-docker-host`, never `just play`.
  - **Open, source `.1` or router admin reachable:** add a PVE egress DROP to the WAN IP. It is a variable, with a runbook check for when the IP changes, and it gets a firewall-shape arm. ⛔ **Gate:** `tofu apply`.
  - Or accept the risk explicitly in the runbook, in the operator's words.

**Tests.** On the code branches, as listed. The runbook-shape test pins a "Hairpin" section that holds either the evidence or the acceptance.

**Integration.** Completes D6 together with Step 10.

**Demo.** The probe output before and after the fix, or the recorded acceptance. Include the whoami response that shows the source IP.

## Step 12: Runbook completion (R26, R27; D4)

**Objective.** `docs/runbooks/gitlab-runner.md` covers all of D4 and the security model, and its guard pins every required section.

**Guidance.** Add these sections:
- **Security model:** "Developer or above on any attached project = root on the runner VM and all its tokens". Attach only trusted projects.
- **GitLab-side hygiene:**
  - the runner is locked to its project;
  - fork pipelines in the parent project are off;
  - the max timeout is set to 5400–5700 s;
  - the job-token allowlist stays at its default.
- **Compromise playbook:**
  - pause the runner;
  - re-image with `just runner-reimage`;
  - delete and recreate the runner, or use the ID-based reset;
  - rotate any CI variables the runner could have seen.
- **Routine re-image:** monthly and on upgrades. Note that the SSH host key changes.
- **Known limits:** no Alertmanager; the split manager and sysbox are follow-ups.

Cross-check that every section from Steps 2–11 is present.

**Tests.** `test_gitlab_runner_runbook_shape.py` pins:
- the six D4 sections;
- security model, compromise, re-image and hairpin.

Mutant: delete one heading; it must go red.

**Integration.** Documents Steps 2–11.

**Demo.**
- `just test` is green, and the runbook's table of contents lists every required section.
- ⛔ **With the operator in the GitLab UI:** walk through the token-rotation section without rotating, confirming that each UI path and command exists.

## Step 13: ⛔ Monitoring (R17) and handoff (D5)

**Objective.** CT 111's Prometheus scrapes the runner metrics and the VM's node-exporter, and the VM is covered by the `host-disk` alerts, including the absent case.

**Guidance.**
- **VM:** `prometheus-node-exporter` on `0.0.0.0:9100`. Steps 7 and 10 already admit only `.111`.
- **`docker_host`, per §4.9:**
  - `prometheus.yml.j2`: the `gitlab-runner` and `gitlab-runner-node` jobs, each with one static `hostvars['gitlab-runner-pve'].ansible_host` target line, following the plex precedent. No loop.
  - `host-disk-rules.yml.j2`: the new `absent()` arm and the annotations.
- **Optional:** `GitLabRunnerDown`, only if its guard cost stays small.
- This code lands only once this step's gate is approved (see "No deploy leakage").

**Tests.**
- `test_traefik_config_shape.py`:
  - pin the two new jobs by cell identity;
  - a census that every `gitlab_runner` inventory host has a target line. The Step 2 static fallback guarantees the group exists.
- `test_host_disk_alert_rules_promtool.py`: add a `gitlab-runner-node` fixture that must fire Low, Critical and Absent, with a positive control.
- Mutant: drop the new `absent()` arm; Absent must go red.

**Integration.** Uses Step 2's inventory group and the allowances from Steps 7 and 10. Add the `play-docker-host` recipe here if Step 11 didn't.

**Demo.**
- `promtool test rules` passes offline.
- ⛔ **Gate: `just play-runner`, then `just play-docker-host`**, which restarts Prometheus.
- In Prometheus, `up{job=~"gitlab-runner.*"} == 1`.
- `:9100` from a host other than `.111` is refused.

**Final handoff (D5).** The closing message splits the operator's GitLab actions into done and remaining:
- **Done during Step 9:**
  - created the token (locked, untagged on, max timeout 5400–5700 s);
  - turned off instance runners for `lumologic/lumologic`;
  - retried the failed pipeline and confirmed its jobs ran on `lumologic-pve`.
- **Remaining:**
  - turn off fork pipelines running in the parent project (R26; this goes beyond the brief's list);
  - anything from the above still outstanding.
