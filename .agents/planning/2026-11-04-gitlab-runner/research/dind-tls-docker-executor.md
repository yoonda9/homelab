# Docker executor, Docker-in-Docker with TLS, and a standalone smoke test

Researched 2026-11-04.
- Runner source cited from gitlab-runner `main`, VERSION 19.6.0, commit `3e6aa9a3`. The released package is 19.5.2.
- docker-library entrypoints are cited from `docker-library/docker` `master`. Docker Hub's official `docker` image currently lists only the **29.x** series as supported (`29.9.3`, `29`, `latest`; <https://hub.docker.com/_/docker>).
- `docker:27` and `docker:27-dind` are still pullable but no longer listed or maintained. That is the job's choice, and it is fine on a 29.x host.

## 1. GitLab's documented DinD-with-TLS setup (docker executor)

Source: <https://docs.gitlab.com/ci/docker/docker_in_docker/>; overview at <https://docs.gitlab.com/ci/docker/using_docker_build/>.

The config.toml the docs show:
```toml
[[runners]]
  executor = "docker"
  [runners.docker]
    tls_verify = false          # runner->host-daemon TLS; unrelated to dind
    image = "docker:24.0.5-cli" # docs example; any small default
    privileged = true
    volumes = ["/certs/client", "/cache"]
```

The job side (`.gitlab-ci.yml`) for the docker executor:
```yaml
services:
  - docker:27-dind          # hostname/alias "docker"
variables:
  DOCKER_TLS_CERTDIR: "/certs"
  # optional/explicit (what lumologic sets):
  DOCKER_HOST: tcp://docker:2376
  DOCKER_TLS_VERIFY: 1
  DOCKER_CERT_PATH: "$DOCKER_TLS_CERTDIR/client"
```

- "The 'docker' hostname is the alias of the service container."
- `DOCKER_TLS_VERIFY` and `DOCKER_CERT_PATH` "are usually specified by the entrypoint, however the Kubernetes executor doesn't run entrypoints". With the docker executor they are optional but harmless.
- The docs suggest `HEALTHCHECK_TCP_PORT: "2376"` as a service variable to make the runner's service wait probe the TLS port.
- The runner waits `wait_for_services_timeout`, default 30 s, for services (<https://docs.gitlab.com/runner/configuration/advanced-configuration/>).
- Pin versions: "Always pin a specific version of the image". `vfs` vs `overlay2`: `overlay2` has been the default since 17.09.

### How the shared `/certs/client` volume works (verified in source)

The docs say Docker "creates `/certs/client` to share between the service and job container, thanks to volume mount from config.toml". The mechanics, from source:

1. `volumes = ["/certs/client"]` is a destination with no host path, so the runner's volume manager creates a **Docker named volume**, a "cache volume".
   - Its name is `runner-<sha256(token, system_id, project, concurrency-slot)[:32]>-cache-<md5(path)>`.
   - It carries labels `com.gitlab.gitlab-runner.managed=true`, `type=cache` and `reusable=true` (`executors/docker/internal/volumes/manager.go`, `createCacheVolume`; naming from `common/build.go` `ProjectRealUniqueName`).
   - Since runner **18.4.0** volume names are `runner-<runner-id-hash>-cache-<md5-of-path><protection>`. The upgrade ignores old caches (<https://docs.gitlab.com/runner/executors/docker/>).
2. **The same binds are given to service containers and to the build container.** `createServiceContainerConfig` sets `Binds: e.volumesManager.Binds()`, and so does the build container (`executors/docker/docker.go`). The `docker:dind` service and the job container therefore mount the *same* volume at `/certs/client`.
3. The dind entrypoint (`docker-library/docker` `dockerd-entrypoint.sh`, <https://raw.githubusercontent.com/docker-library/docker/master/29/dind/dockerd-entrypoint.sh>) behaves as follows when `DOCKER_TLS_CERTDIR=/certs`:
   - It generates `/certs/ca` and `/certs/server` inside the service container. These are **not** shared, because only `/certs/client` is a volume.
   - Because `ca/key.pem` exists, it re-issues the client cert (`CN=docker:dind client`, `extendedKeyUsage=clientAuth`) **on every startup** and copies the CA to `client/ca.pem`.
   - It starts `dockerd --host=tcp://0.0.0.0:2376 --tlsverify --tlscacert/--tlscert/--tlskey` from `server/`.
   - Stale client certs left in the reused volume from an earlier job are therefore overwritten each time. There is no stale-CA problem.
4. The `docker:27` client entrypoint (`docker-entrypoint.sh`, <https://raw.githubusercontent.com/docker-library/docker/master/29/cli/docker-entrypoint.sh>) works like this:
   - If `DOCKER_HOST` is a `tcp:` address, `DOCKER_TLS_VERIFY` and `DOCKER_CERT_PATH` are unset, and `$DOCKER_TLS_CERTDIR/client/{ca,cert,key}.pem` are non-empty, it exports `DOCKER_TLS_VERIFY=1` and `DOCKER_CERT_PATH=$DOCKER_TLS_CERTDIR/client`.
   - If `DOCKER_HOST` is unset and there is no local socket, it defaults to `tcp://docker:2376` when TLS applies.
   - It does **not** check that `docker` resolves.
   - GitLab overrides the entrypoint only if the job sets one, so it normally runs.
5. **Race:** the job can start before dind has written the client certs. The runner's service health-wait (TCP probe) covers this, and jobs commonly add `until docker info; do sleep 1; done`.
6. Concurrency: the slot index is part of the volume name, so two concurrent jobs of the same project get **different** `/certs/client` volumes. The docs warn that "concurrent jobs can conflict" because the directories persist. Their alternative is a Unix socket on a shared temporary volume.
7. Networking: by default the docker executor links services with legacy container links, which gives the alias `docker`. Setting `FF_NETWORK_PER_BUILD=true` gives a per-job user-defined bridge network instead, where services are reachable by alias. Either works for `tcp://docker:2376`. The smoke test below uses a user-defined network, the closer analogue to `FF_NETWORK_PER_BUILD`.

## 2. Docker executor `[runners.docker]` keys relevant to this plan

Sources: <https://docs.gitlab.com/runner/configuration/advanced-configuration/> (the `[runners.docker]` section) and <https://docs.gitlab.com/runner/executors/docker/>.

| Key | Semantics / default | Plan value |
|---|---|---|
| `image` | Default job image when a job sets none | Something small and pinned, e.g. `alpine:3.22` or `busybox`. Every lumologic job sets its own image |
| `privileged` | Runs build and service containers privileged. Required for DinD. Docs: "insecure" | `true` |
| `services_privileged` | If unset, inherits `privileged` | leave unset |
| `pull_policy` | `always` (default), `if-not-present`, `never`; a list is allowed | `["if-not-present"]` |
| `allowed_pull_policies` | Jobs may set `image: pull_policy:`. The effective policy is the intersection with `allowed_pull_policies`, and the job fails if the intersection is empty. If unset, it defaults to the values in `pull_policy` | Consider `["always", "if-not-present"]` so a job can force a refresh |
| `volumes` | `-v` syntax. A bare path becomes a persistent runner-managed named volume; a `host:container` pair is a bind | `["/certs/client", "/cache"]`. **No host binds**, per the isolation requirement |
| `shm_size` | Bytes; Docker's default is 64 MB | Playwright/Chromium jobs benefit from `shm_size = 2147483648` (2 GiB) or similar; lumologic uses `mcr.microsoft.com/playwright` |
| `disable_cache` | Disables the automatic local cache *volumes*. Volumes are then created non-reusable and removed after the job. Does not affect distributed cache | `false`, so the fetch strategy can reuse the clone |
| `services_limit` | Maximum services per job, default `-1` (unlimited) | leave, or e.g. `4` |
| `wait_for_services_timeout` | Default `30` s | 30–60 |
| `helper_image` / `helper_image_flavor` | Image used for git clone, LFS, artifacts and cache. Flavor default `alpine`. With the `gitlab-runner-helper-images` package installed, the helper is loaded from local tarballs instead of pulled | leave default |
| `allowed_images` / `allowed_services` | Wildcard allow-lists; absent means all (`["**"]`) | leave open; a general homelab runner |
| `cpus`, `memory`, `memory_swap` | Per-container limits (same page) | Optional. 8 vCPU / 16 GB with concurrent 4 means about 2 vCPU / 4 GB per job without limits; Docker shares fairly |

`pull_policy = "if-not-present"` semantics, from <https://docs.gitlab.com/runner/executors/docker/>:
- It is "Pull an image only when a local version does not exist". A moving tag such as `node:24` stays at whatever was first pulled until the image is pruned.
- The docs warn of security implications with private registries: a cached private image can be used by other projects on the same runner without credentials.
- With multiple policies, "The runner processes pull policies in the order listed until a pull attempt is successful".

Git LFS:
- The helper image "contains ... Git, Git LFS, and SSL certificates store" (<https://docs.gitlab.com/runner/configuration/advanced-configuration/>, helper image section).
- No runner config is needed for LFS.
- With `GIT_STRATEGY: fetch` (the default for new projects), the build directory is a **reusable cache volume**. `createBuildVolume` in `executors/docker/docker.go` calls `volumesManager.Create(jobsDir)` for `GitFetch`. `.git/lfs/objects` therefore persists per project and slot, so the 360 MB of LFS is downloaded once per slot, not once per job.
- With `GIT_STRATEGY: clone` it is a temporary volume. Pruning these volumes only costs a re-download.

## 3. Standalone DinD-TLS smoke test (plain docker on the VM)

This mirrors exactly what the CI job does: a privileged `docker:27-dind` daemon with `DOCKER_TLS_CERTDIR=/certs`, and a `docker:27` client sharing only `/certs/client`, talking to `tcp://docker:2376` with TLS verification. It is idempotent and self-cleaning. It is based on the Hub "TLS" example (<https://hub.docker.com/_/docker>).

```sh
#!/usr/bin/env bash
set -euo pipefail
TAG="${DIND_TAG:-27}"           # match the CI job's docker:27 / docker:27-dind
NET=dind-smoke VOL=dind-smoke-certs D=dind-smoke-daemon

cleanup() { docker rm -f "$D" >/dev/null 2>&1 || true
            docker network rm "$NET" >/dev/null 2>&1 || true
            docker volume rm "$VOL" >/dev/null 2>&1 || true; }
trap cleanup EXIT
cleanup

docker network create "$NET" >/dev/null
docker volume create "$VOL" >/dev/null

# Daemon: privileged, alias "docker", TLS certs generated under /certs, only client/ shared
docker run -d --privileged --name "$D" \
  --network "$NET" --network-alias docker \
  -e DOCKER_TLS_CERTDIR=/certs \
  -v "$VOL":/certs/client \
  "docker:${TAG}-dind" >/dev/null

client() {
  docker run --rm --network "$NET" \
    -e DOCKER_HOST=tcp://docker:2376 -e DOCKER_TLS_VERIFY=1 -e DOCKER_CERT_PATH=/certs/client \
    -v "$VOL":/certs/client:ro \
    "docker:${TAG}" "$@"
}

# Wait for certs + daemon (same race CI has)
for i in $(seq 1 60); do client docker info >/dev/null 2>&1 && break; sleep 1; done

# Positive: server version over TLS on 2376
client docker info --format '{{.ServerVersion}} tls-ok'
client docker version
# Prove nested containers run (the actual DinD use)
client docker run --rm busybox:1.37 true && echo "nested-run-ok"

# Negative control: no client certs => must FAIL (proves TLS verify is actually on)
if docker run --rm --network "$NET" -e DOCKER_HOST=tcp://docker:2376 -e DOCKER_TLS_VERIFY=1 \
     "docker:${TAG}" docker info >/dev/null 2>&1; then
  echo "FAIL: daemon accepted a client without certs"; exit 1
fi
# Negative control 2: plaintext port 2375 must not be listening
if docker run --rm --network "$NET" -e DOCKER_HOST=tcp://docker:2375 "docker:${TAG}" docker info >/dev/null 2>&1; then
  echo "FAIL: plaintext 2375 reachable"; exit 1
fi
echo "dind-tls smoke: PASS"
```

Notes:
- **Do not run `docker info` alone as a pass criterion.** The positive control must check the server version and `tls-ok` output. The negative controls show that verification and TLS are really in force, rather than the client silently falling back.
- Pulling `busybox` inside dind needs outbound internet from the nested daemon. Drop that line for an offline check.
- Since `/certs/ca` is not shared, the client gets only `ca.pem`, `cert.pem` and `key.pem` under `/certs/client`. That matches CI.
- No `exec` command exists in gitlab-runner `main` today (`commands/` has no exec.go), so a runner-level check needs a real pipeline. The standalone script is the on-VM proof.
- In Ansible: ship it as `/usr/local/sbin/dind-tls-smoke`, and run it with `changed_when: false` behind a tag or flag, since it pulls images.

## 4. Security implications of privileged mode

- GitLab: "Privileged mode has security risks". Container "security mechanisms are disabled and the host is exposed to privilege escalation" (<https://docs.gitlab.com/runner/executors/docker/>). `--docker-privileged` "effectively disables the container's security mechanisms and exposes your host to privilege escalation" and "can cause container breakout" (<https://docs.gitlab.com/ci/docker/docker_in_docker/>).
- What a privileged container can do:
  - It has all capabilities, all host devices (`/dev/*`, including block devices), and no seccomp, AppArmor or SELinux confinement. It can write `/sys` and `/proc/sys`.
  - It can mount the host's root disk (`mount /dev/sda1 /mnt`), load kernel modules, or `nsenter` into PID 1's namespaces.
  - **Any job, and any service image, is effectively root on the VM.** The `services_privileged` default inherits `privileged`.
- Consequences for this plan:
  - Everything on the VM is readable and writable by any job author with push access to any project using the runner. That includes `/etc/gitlab-runner/config.toml`, which holds **all runners' `glrt-` tokens**, other projects' cache volumes, and the Docker daemon.
  - A job can therefore steal the tokens and impersonate the runner, to pick up other projects' jobs and their CI variables and secrets.
  - Mitigations:
    - Keep it a dedicated VM. No homelab bind mounts, no shared credentials, no ansible vault material beyond the runner tokens, no SSH keys to other hosts.
    - Register it as **project runners** only for trusted projects, not group or instance runners.
    - Consider **Protected** (runs only on protected branches and tags) for projects with external contributors. Fork MR pipelines on gitlab.com run in the fork's project context, not on your project runners, unless they are run as parent-project pipelines.
    - Firewall the metrics port. Assume compromise means re-image plus token reset.
  - Network: a privileged job can reach anything the VM can reach on the LAN. Consider VLAN or firewall egress isolation from the rest of the homelab, allowing only outbound HTTPS to the internet and DNS.
- The less-privileged alternative, not chosen here: socket binding (`/var/run/docker.sock`). That is *also* host-root, and it shares the daemon between jobs. Rootless dind or kaniko/buildah avoid privileged mode, but the lumologic pipeline requires `docker:27-dind` with TLS.
