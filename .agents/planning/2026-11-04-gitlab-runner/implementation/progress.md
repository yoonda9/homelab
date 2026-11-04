# Progress — gitlab-runner

## Completed Steps

- Step 1a: dev_vm provider pin >= 0.108.0 — commit b9e183d (versions.tf floor + one new guard arm); shape test 7/7 incl. tofu validate; review.passed; no consumer module, so no live state moves.
- Step 1b: dev_vm §4.1 variables + guard polarity flip — commit fd1187a (9 vars w/ exact defaults; user_data_file_id/static_ip still forbidden; gateway validation + required_version >= 1.9 same commit); shape test 8/8, cpu_type mutant killed, tofu fmt clean; review.passed.
- Step 1c: dev_vm main.tf render — commit 553ea77 (vm_id, cpu.type, NIC firewall, conditional static ip/gateway, dynamic user_account+dns); shape test 11/11, tofu fmt clean, scope main.tf+test only, defaults keep bare DHCP behaviour; review.passed.
- Step 1d: dev_vm outputs ipv4_configured — commit d8e6e93 (null under DHCP, split strip of prefix); tofu fmt/validate clean; shape test 12/12; mutant red; review.passed. Unrelated plex-latency failure pre-existing.
- Step 1e: dev_vm README + scratch-plan demo — commit 3575939 (README table matches variables.tf defaults/outputs, static example); shape test 12 passed, tofu validate OK, no root module calls dev_vm; review.passed. **Step 1 complete.**
- Step 2a: root gitlab_runners map + module gitlab_runner call (VM 120) — commit c3dc71e; fmt/validate OK, shape test 5/5; review.passed. Module blocks reject lifecycle preconditions, so the keys guard is a no-op terraform_data gitlab_runner_operator_keys + depends_on: plan shows VM + one terraform_data (Demo/runbook wording must say so).
- Step 2b: root output gitlab_runners {ipv4=ipv4_configured, vm_id} per VM — commit 2310769; fmt+validate OK, shape test 6/6, diff scoped to 2 files; review.passed.
- Step 2d: play-runner justfile recipe — commit 74ed016 (mirrors play, ansible/ workdir, --limit gitlab_runner); dry-run renders correctly, test_justfile_shape 16/16, scope justfile + shape test; review.passed; only known pre-existing reds.
- Step 2c: gen_inventory renders gitlab_runner group (group from tofu output, static .120 fallback incl. null-ip) — commit 6417956; test_gen_inventory_shape 4/4, legacy groups byte-identical, committed hosts.yml block matches generator; scope 3 files; review.passed.
- Step 2e: runbook skeleton — commit ae5d486 (7 headings + TOC, create-the-VM section: pvesm 150GB local-lvm, .120 free/DHCP, just plan/apply, qm guest exec); referenced tofu/justfile names exist; shape guard 3/3; review.passed. **Step 2 build complete; only operator GATE f7e5 remains.**
- Step 3a: premise check (read-only, 2026-11-04) PASSED — download.docker.com/linux/ubuntu/dists/resolute/Release 200, stable/binary-amd64 lists 23 docker-ce versions; packages.gitlab.com/runner/gitlab-runner/ubuntu/dists/resolute/Release 200 (Codename resolute, amd64, component main). Both also list noble. No re-plan needed.
- Step 3b: role skeleton + harden.yml — commit 951f096 (sshd drop-in validated, cloud-init drop-in removal, password_lock, needrestart excl. for 3 units guarded by stat); shape test 7/7; review.passed. Filed hole: test_needrestart_exclusion 'guarded' has A-or-B-and-C precedence, deleting `when: stat.exists` still passes.
- Step 3c: docker meta dependency + role-owned daemon.json — commit 2619069 (meta vars present/{}/started/[]; daemon.json.j2 10m x3; template notifies 'Drain and restart docker', handler lands in 3d); role-shape test 11/11; ansible-lint deferred to 3e gate (vault env); review.passed.
- Step 3d: Drain and restart docker handler — commit 12fe5c3 (probe -> stop gitlab-runner -> restart docker -> start, stop/start gated on unit rc==0, listened to via docker.yml notify); role-shape 12/12 + order arm; scope handlers + one arm; review.passed. ansible-lint vault-pass error is environmental (deferred to 3e gate).
- Step 3e: site.yml gitlab_runner play after common + Ubuntu resolute in common platforms — commit ad6dd43; shape 14/14 (host group, become, role, order arms) re-run by critic; syntax-check/ansible-lint deferred to operator gate 4344 (vault env); review.passed. **Step 3 build complete; only operator GATE 4344 and filed guard row d41e remain.**

## Remaining

- Operator GATEs f7e5 (tofu apply VM 120) and 4344 (play-runner twice), not run from the loop; guard row d41e (needrestart `when:` arm); Steps 4-13
