# Docker Engine install, disk upkeep, logging, and upgrade safety on the runner VM

Researched 2026-11-04.
- **Docker Engine `5:29.9.3-1~ubuntu.26.04~resolute`** is current in `download.docker.com/linux/ubuntu` for Ubuntu 26.04. I checked the `dists/resolute` Packages index today.
- gitlab-runner 19.5.2 is the current package. Runner source cited from `main` (19.6.0, `3e6aa9a3`).

## 1. Docker Engine from the official apt repo (Ubuntu)

Source: <https://docs.docker.com/engine/install/ubuntu/>.
- Supported releases: Ubuntu 26.10 "Stonking", **26.04 LTS "Resolute"** (this repo's Packer template is `packer/ubuntu26.pkr.hcl`), 24.04 and 22.04.
- First remove conflicting packages: `docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc`.
- Keyring: `curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc`, an ASCII-armored key, no dearmor needed.
  - Key fingerprint: `9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88`, "Docker Release (CE deb)". I checked it today.
- Sources use **deb822** at `/etc/apt/sources.list.d/docker.sources`, with `Signed-By: /etc/apt/keyrings/docker.asc`, `Types: deb`, `URIs: https://download.docker.com/linux/ubuntu`, `Suites: <codename>` and `Components: stable`.
- Packages: `docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`.
- Upgrade: the docs say to re-run the apt install step with the new version. Don't re-run the convenience script, which "can cause issues".
- **This repo already vendors `geerlingguy.docker`** (`ansible/galaxy_roles/geerlingguy.docker`, pinned in `ansible/requirements.yml`). `docker_host` uses it as a meta dependency.
  - It writes the key via `signed_by: "{{ docker_apt_gpg_key }}"` and removes the old `trusted.gpg.d/docker.asc`.
  - It exposes `docker_packages`, `docker_packages_state` and `docker_daemon_options` (a dict rendered to `/etc/docker/daemon.json`).
  - Reusing it is the repo-consistent choice. Set `docker_packages_state: latest` if "upgrade through the normal playbook run" should mean upgrading every run.

## 2. Disk growth on a CI host: what accumulates

1. **Job, service and helper images** pulled with `if-not-present`: python, node, playwright (about 2 GB), postgres, redis, docker:dind. These are **not** runner-labelled, because they come from upstream registries.
2. **Runner cache volumes**, `runner-<hash>-cache-<md5>`: one per (token, system_id, project, concurrency slot) per volume path. That covers `/cache`, `/certs/client` and, with `GIT_STRATEGY: fetch`, the builds dir with its Git LFS objects. They are labelled `com.gitlab.gitlab-runner.managed=true`, `type=cache`, `reusable=true` (`executors/docker/internal/volumes/manager.go`). Naming is per <https://docs.gitlab.com/runner/executors/docker/>:
   - before 18.4.0: `runner-<short-token>-project-<id>-concurrent-<n>-cache-<md5>`;
   - 18.4.0 and later: `runner-<runner-id-hash>-cache-<md5-of-path><protection>`.
   - **Token rotation, a re-image (new system_id) or the 18.4 naming change orphans the old volumes.**
3. **Stopped runner containers** (build, helper, service, "predefined", "cache" containers). They are runner-labelled and are normally removed at job end; crashed or killed jobs leave them behind.
4. **Inside DinD**: the nested daemon's `/var/lib/docker` is an anonymous volume of the `docker:dind` service container, because the dind image declares `VOLUME /var/lib/docker`. The runner removes service containers *with* their volumes at job end. Leftovers from killed jobs are anonymous volumes.
5. **BuildKit build cache** on the host daemon, if any job uses the host daemon. These jobs use DinD, so it is mostly inside the nested daemon and is discarded.
6. Container json logs (section 4).

## 3. Pruning

### GitLab's own `clear-docker-cache`

Installed by the gitlab-runner package at `/usr/share/gitlab-runner/clear-docker-cache`. I read the source on `main`.
- Default filters: `CONTAINER_FILTER_FLAGS`, `IMAGE_FILTER_FLAGS` and `VOLUME_FILTER_FLAGS` all default to `label=com.gitlab.gitlab-runner.managed=true`. They are overridable and comma-separated.
- `prune-volumes`, the default, on Docker 23 or newer runs:
  ```
  docker container prune -f --filter=label=com.gitlab.gitlab-runner.managed=true
  docker image prune -af   --filter=label=com.gitlab.gitlab-runner.managed=true
  docker volume prune -af  --filter=label=com.gitlab.gitlab-runner.managed=true   # -a needed for NAMED volumes on >=23
  docker network prune -f
  ```
- `prune` does the same without the volume step. `space` runs `docker system df`.
- GitLab docs: "The default option is `prune-volumes`, which removes all unused containers (dangling and unreferenced) and volumes". The script "does not remove Docker images because they are not tagged by the GitLab Runner". The docs recommend running it regularly, "for example weekly with `cron`" (<https://docs.gitlab.com/runner/executors/docker/>, "Clear the Docker cache").
- **Gotcha: it does not prune job images** such as `python:3.14-slim` and `node:24`, which are the bulk. For those, the docs point to `docker system prune`.
- The deb `postinst` already runs `clear-docker-cache prune` on every gitlab-runner install or upgrade unless `NO_DOCKER_PRUNE=1` is set (`packaging/scripts/postinst.deb`; <https://docs.gitlab.com/runner/install/linux-repository/>).
- The old `gitlab-runner-docker-cleanup` / docker-gc tool is **archived** (<https://gitlab.com/gitlab-org/gitlab-runner-docker-cleanup>). Use cron or a systemd timer around the prune commands instead.

### Docker prune semantics

Source: <https://docs.docker.com/engine/manage-resources/pruning/>.
- `docker system prune` removes stopped containers, unused networks, dangling images and build cache.
  - `-a` also removes unused tagged images.
  - `--volumes` removes only unused **anonymous** volumes.
  - "Named volumes that aren't attached to a container are left alone unless you pass `--all` / `-a`" on `docker volume prune`.
- The `until` filter, for example `--filter "until=24h"`, works on container, image, network, system and builder prune. **Volume prune supports only `label` filters, not `until`.**
- "In use" protects running jobs:
  - Prune never removes an image used by an existing container (running or stopped), or a volume attached to any container.
  - A prune that runs *between* a job's image pull and its container create can delete the just-pulled image. The job then re-pulls with `if-not-present`, or fails with `never`.
  - `until=` on image prune avoids that race.

### Recommended scheduled prune

A systemd timer, for example daily at 04:00, or hourly with a disk-usage gate:

```sh
#!/usr/bin/env bash
# /usr/local/sbin/ci-docker-prune  (rendered by ansible; no secrets)
set -euo pipefail
KEEP="${KEEP:-72h}"                       # images/containers younger than this survive
# 1. stopped containers older than KEEP (runner leftovers from killed jobs too)
docker container prune -f --filter "until=${KEEP}"
# 2. unused images (job + service + helper) older than KEEP; keeps the warm set used in the last KEEP
docker image prune -af --filter "until=${KEEP}"
# 3. build cache older than KEEP
docker builder prune -af --filter "until=${KEEP}"
# 4. runner-managed volumes not attached to any container (caches, certs, builds dirs, orphans after rotation)
docker volume prune -af --filter "label=com.gitlab.gitlab-runner.managed=true"
# 5. anonymous leftovers (e.g. dind /var/lib/docker from killed jobs)
docker volume prune -f
docker network prune -f --filter "until=${KEEP}"
```

Notes:
- Image `until` uses the image's **creation** time, not the last-used time. A `python:3.14-slim` built 10 days ago is pruned on every run once unused and then re-pulled.
  - That's acceptable. Alternatively use a disk-pressure gate: only `image prune -a` when `/var/lib/docker` usage is above X%.
  - Or keep the `until` value small and accept re-pulls. Pulls are free for public images. Docker Hub anonymous pull rate limits could matter at high volume; consider a Docker Hub login or a registry mirror if `toomanyrequests` appears.
- Step 4 removes reusable caches: the builds dir with its Git LFS objects, and `/cache`. It costs one re-clone of about 360 MB of LFS per slot after each prune. That is acceptable daily or weekly. To keep the warm clone, run step 4 weekly instead of daily.
- Volumes attached to a **running** job are never removed, so a prune during a job is safe.
- Alternatively, just schedule `clear-docker-cache` (the docs' recommendation) plus `docker image prune -af --filter until=...` for the unlabelled images.
- For the disk alert, follow the repo's docker-host pattern, which uses node_exporter filesystem free percentage on `/`. On this VM, `/var/lib/docker` lives on `/`.

## 4. `daemon.json`: log rotation and CI-host settings

- The default `json-file` driver **does not rotate**: `max-size` "Defaults to -1 (unlimited)". `max-file` defaults to 1 and is "Only effective when `max-size` is also set" (<https://docs.docker.com/engine/logging/drivers/json-file/>).
- The `local` driver rotates by default: 20m × 5 files, compressed, "100MB of log messages per container" (<https://docs.docker.com/engine/logging/drivers/local/>).
- Log config applies only to **newly created** containers. "Existing containers don't use the new logging configuration automatically", and a daemon restart is needed. CI containers are short-lived, so this resolves itself.
- Job output reaches GitLab through the runner, which attaches to the container streams, not by reading the json log files. That is my reading of the docker executor's attach-based design. It means a small log cap does not truncate the CI job log; the runner's `output_limit` (default 4096 KB) governs that. **Verify** with one pipeline.
- Suggested `/etc/docker/daemon.json`, through `geerlingguy.docker` `docker_daemon_options`:
  ```json
  {
    "log-driver": "json-file",
    "log-opts": { "max-size": "10m", "max-file": "3" },
    "live-restore": false
  }
  ```
  - Mirror whatever log options docker-host's recent "bounded container logs" commit (`3f69dcb`) chose, for consistency.
  - `live-restore` keeps containers running across a dockerd restart. It does not help DinD, which uses the TCP and network stack, and it can confuse the runner. Leave it off.
  - `default-address-pools` is optional. Each job's network uses a bridge subnet, and with `FF_NETWORK_PER_BUILD` and concurrency 4 the default pools are plenty. Set it only if 172.17–31/16 collides with LAN or VPN ranges.
- Changing `daemon.json` restarts dockerd, through the role handler. **That kills running jobs**, so treat it like a runner restart (section 5).

## 5. Upgrades while jobs run

### gitlab-runner package upgrade

What happens, from the source deb maintainer scripts:
- The old package's `prerm` runs `/usr/share/gitlab-runner/pre-remove`, which does `gitlab-runner stop` and `gitlab-runner uninstall` with errors ignored.
- The new `postinst` runs `post-install`: it stops, uninstalls and reinstalls the service unit, then starts it. Then it runs `clear-docker-cache prune` unless `NO_DOCKER_PRUNE` is set.
- `apt install gitlab-runner=<new>`, or an Ansible `apt state=latest`, therefore **stops the running service**.
- GitLab: "the installation script kills, and restarts the runner process that was probably handling new jobs at the time" (<https://docs.gitlab.com/runner/configuration/init/>).

Signal semantics (<https://docs.gitlab.com/runner/commands/>, `commands/multi.go`):
- **SIGQUIT**: "Stop accepting new builds. Exit as soon as the running builds finish (graceful shutdown)". The runner waits **indefinitely** for builds. `handleGracefulShutdown` loops until `runFinished` or until another signal arrives.
- **SIGTERM / SIGINT**: "Abort all running builds and exit as soon as possible". The forceful path aborts the builds, then waits at most **`shutdown_timeout`** (global, default **30 s**, `common/consts.go` `DefaultShutdownTimeout`) for cleanup, then exits.
  - **`shutdown_timeout` does not bound the graceful SIGQUIT wait.** It applies only to the forceful path.
  - Jobs killed this way show as failed in GitLab. Some stay "running" until GitLab's stuck-job timeout; issue <https://gitlab.com/gitlab-org/gitlab-runner/-/issues/36786> covers a variant where a short TimeoutStopSec left jobs pending.
- **SIGHUP**: reload config.
- The systemd unit generated by `gitlab-runner install` uses systemd's default SIGTERM. So a plain `systemctl stop` or restart, or a package upgrade, **kills running jobs** unless you override it.

GitLab's documented fix, a systemd drop-in (<https://docs.gitlab.com/runner/configuration/init/>):
```ini
# /etc/systemd/system/gitlab-runner.service.d/kill.conf
[Service]
KillMode=mixed
TimeoutStopSec=7200
KillSignal=SIGQUIT
```
- "Systemd sends `SIGQUIT` to the GitLab Runner process and waits up to two hours for it to stop". After that, systemd sends SIGKILL to the cgroup.
- For this runner the jobs have 90-minute timeouts. Use **`TimeoutStopSec` of at least the max job timeout plus margin**, for example 6000 s (100 min), or keep 7200.
- **Drop-in survival:** `post-install` uninstalls and reinstalls the *unit file*. A drop-in under `gitlab-runner.service.d/` is a separate file, so it survives. Ansible should still assert it on every run and `daemon-reload`.

Consequences for the Ansible upgrade path:
- With the drop-in, `apt` blocks inside `prerm` until running jobs finish, up to `TimeoutStopSec`. **The playbook can hang for up to 100 minutes** while jobs drain, and new jobs are not accepted meanwhile.
  - Set an Ansible `async`/`timeout` larger than that, or pre-drain explicitly: `systemctl stop gitlab-runner` (SIGQUIT, waits), then upgrade, then start.
  - Or gate the upgrade on `gitlab_runner_jobs == 0` / no running build containers (`docker ps --filter label=com.gitlab.gitlab-runner.managed=true`) and skip or retry otherwise.
- `apt state=latest` upgrades only when a new version exists, so idempotent second runs don't restart anything. Pin `gitlab-runner` and `gitlab-runner-helper-images` to the same version, or use `latest` for both.
- Re-rendering `config.toml` does **not** need a restart; it hot-reloads (section 9 of the registration doc). Except `listen_address`.

### Docker Engine upgrade

- Upgrading `docker-ce` or `containerd.io` restarts `docker.service` and containerd. Without `live-restore` that **kills every running job container**, including DinD daemons.
- So run Docker upgrades only when the runner is drained: `systemctl stop gitlab-runner` (graceful, with the drop-in), then upgrade docker, then `systemctl start gitlab-runner`.
  - In Ansible, use a block that checks whether `docker-ce` / `containerd.io` / `gitlab-runner` have pending upgrades (`apt list --upgradable`, or `check_mode` of the apt task), and only then stops the runner, upgrades and starts it.
  - That keeps the second playbook run a no-op.
- Optionally hold the packages (`dpkg_selections: hold`) so unattended-upgrades never restarts dockerd mid-job. Upgrades then happen only via the playbook.
  - Check whether the Packer template enables unattended-upgrades. Docker's repo is not in the default `Allowed-Origins`, so docker-ce is not auto-upgraded by default, but `containerd`-adjacent Ubuntu packages could be.
