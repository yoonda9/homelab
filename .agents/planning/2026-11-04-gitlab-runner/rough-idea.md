# Self-hosted GitLab Runner on the Proxmox homelab

## Goal

Run GitLab.com CI jobs on homelab hardware instead of GitLab's metered instance runners. Build it as a general homelab service, managed like the rest of this repo: a runner VM that any of my GitLab projects can use. The first project to use it is lumologic/lumologic. Its pipelines used up this month's compute minutes, so every job now fails with ci_quota_exceeded.

## Context you can't get from this repo

- GitLab is the SaaS instance at https://gitlab.com, not self-hosted. A runner only polls gitlab.com over outbound HTTPS, so it needs no inbound ports.
- There are two Proxmox VE nodes. They are separate, not a cluster, and this repo currently targets only node pve. Start with one runner VM on pve. Make the node a variable, so that a second runner on the other node later is one more entry. Ask me for the second node's details when you need them.
- lumologic's pipeline is the minimum the runner must support. Treat these as general capabilities, not lumologic-specific settings:
  - Docker executor: every job names its own image (python:3.14-slim, node:24, docker:27, mcr.microsoft.com/playwright:v1.59.1-noble). Jobs also use service containers (postgres:16, redis:8.6).
  - Privileged mode: one job runs Docker-in-Docker, the docker:27-dind service with TLS (DOCKER_HOST tcp://docker:2376, client certs in /certs/client).
  - Untagged jobs: no job sets tags, so the runner must accept untagged jobs.
  - Load: 7 jobs per pipeline in 3 stages, at most 3 running at once. The two long jobs take about 50 minutes each on GitLab's small runner (2 vCPU, 8 GB), with 90-minute timeouts. Each clone pulls about 360 MB of Git LFS files.

## Requirements

- Use a VM, not an LXC. Privileged Docker-in-Docker is unreliable in an unprivileged container, and it would give CI jobs root over whatever else that container runs. Build the VM from the existing Packer Ubuntu template through the existing tofu VM module, and configure it with an ansible role, following the patterns already in this repo.
- Starting size, all variables: 8 vCPU, 16 GB RAM, 150 GB disk, concurrent = 4.
- Install Docker Engine and gitlab-runner from their official apt repositories.
- Render the runner config from a template; it must never be hand-edited. It needs:
  - the docker executor, in privileged mode;
  - volumes /certs/client and /cache;
  - pull_policy if-not-present;
  - a small default image;
  - configurable concurrency, overall and per runner.
- Registration:
  - Use GitLab's current authentication-token flow: glrt- tokens created in the GitLab UI or API. Do not use the deprecated registration tokens.
  - I create each token. It goes in ansible vault with the other secrets.
  - Re-running the playbook must never register a duplicate runner.
  - Support a list of runners and projects, so adding another project is only a vars change.
- Upkeep:
  - Prune Docker on a schedule, so images and build caches cannot fill the disk.
  - Upgrade gitlab-runner and Docker through the normal playbook run.
  - If it fits the existing monitoring, scrape the runner's metrics endpoint and add a disk-usage alert like docker-host's.
- Isolation: no bind mounts or shared credentials from other homelab services. Put nothing on the VM that a CI job should not be able to read; a privileged job is effectively root there.

## Out of scope

- The fleeting-plugin-proxmox repo, and autoscaling in general: one static VM per node.
- Any change to a GitLab project's CI config or settings. I turn off instance runners and retry pipelines myself.

## How to work

- Read this repo's conventions first: the README, justfile, tofu modules, ansible roles, and the .agents/planning history. Plan before building.
- Verify each step with the repo's own checks (just test, just fmt, tofu plan) before moving on.
- Stop and ask before:
  - anything that changes the live Proxmox node: tofu apply, just provision, or a playbook run against it;
  - anything that needs a GitLab token.

## Done when

- The VM exists, two playbook runs in a row succeed with the second changing nothing, and gitlab-runner verify passes.
- A smoke test on the VM proves privileged Docker-in-Docker with TLS works the way the CI job uses it: a docker:27-dind daemon and a docker:27 client running docker info over tcp port 2376 with the shared certs.
- The runner shows as online in the lumologic/lumologic project's runner list.
- A runbook in docs/runbooks covers: creating and registering a runner, adding a project, rotating a token, upgrading, cleaning disk, and troubleshooting an offline or stuck runner.
- Your final message lists exactly what I still need to do in GitLab:
  - create the token;
  - turn off instance runners for the project;
  - retry the failed lumologic pipeline and confirm its jobs ran on this runner.
