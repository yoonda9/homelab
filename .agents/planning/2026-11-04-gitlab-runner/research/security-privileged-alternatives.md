# Alternatives to `privileged = true` for the GitLab Runner VM

Researched 2026-11-04. Builds on `dind-tls-docker-executor.md`.

**Evidence tags:**
- **[source]**: read in source code at the commit noted.
- **[docs]**: official documentation.
- **[issue]**: upstream issue tracker.
- **[inferred]**: reasoning only, not run on the target VM.

**Sources pinned:**
- gitlab-runner `main` @ `3e6aa9a` (2026-11-03, VERSION 19.6.0; released package 19.5.x). Paths are relative to the repo root (<https://gitlab.com/gitlab-org/gitlab-runner>).
- moby `master` @ `b56dc7e` (2026-11-04), `daemon/` (<https://github.com/moby/moby>).
- docker-library `docker` `master`, `29/dind/dockerd-entrypoint.sh` (<https://github.com/docker-library/docker>). The logic relevant here is the same in the 27 variant [inferred].
- Kata Containers `main` docs (<https://github.com/kata-containers/kata-containers/tree/main/docs>).
- sysbox through the GitHub API: releases, issues, commits (<https://github.com/nestybox/sysbox>).

**The constraint:**
- An untagged job, unmodified, uses `services: [docker:27-dind]` with `DOCKER_TLS_CERTDIR=/certs` and `DOCKER_HOST=tcp://docker:2376`. It runs `docker build/run` from `docker:27`.
- Every job on this runner can therefore *request* that service. With untagged jobs the runner cannot route work to a different runner config.
- Allow-lists do not make a runner skip a job. They are checked when containers are created, after the job is assigned, so a disallowed job fails instead [source: `executors/docker/docker.go`, `isInAllowedPrivilegedImages` is called from `createService` / `createHostConfig`].

---

## 1. `privileged = false` + `services_privileged = true` + `allowed_privileged_services`

### How it works

**Key names** [source: `common/config.go:302-348`]:
- `privileged` (bool)
- `services_privileged` (*bool; unset inherits `privileged`)
- `allowed_privileged_images` ([]string)
- `allowed_privileged_services` ([]string)

**Service containers** [source: `executors/docker/docker.go:677-684`, `:517`]:
- The effective privilege is `(services_privileged ?? privileged) && nameMatches(allowed_privileged_services)`.
- An empty list means "all allowed" (`isInAllowedPrivilegedImages`, `docker.go:453`).

**Build and helper containers** [source: `docker.go:1272`]:
- The effective privilege is `privileged && nameMatches(allowed_privileged_images)`.
- **With `privileged = false`, `allowed_privileged_images` has no effect.**

**What docs say** [docs: <https://docs.gitlab.com/runner/configuration/advanced-configuration/>, "Capabilities in privileged mode"]:
- "A service container runs in privileged mode when the image matches `allowed_privileged_services`", and either `services_privileged` is true, or it is unset and `privileged` is true.
- `cap_add` / `cap_drop` / `services_cap_*` do not change a privileged container's capabilities.
- `services_cap_add` / `services_cap_drop` were introduced in Runner 19.4. The other keys carry no version note.

**Matching** [source]:
- The match uses `doublestar.Match(pattern, definition.Name)`, against the service name **as written in `.gitlab-ci.yml`**, with no normalisation.
- `services_test.go` shows the bare name `alpine` matches the pattern `alpine`, while `*:*` does not.
- `*` does not cross `/`.
- So `docker:*-dind` matches `docker:27-dind`.
- The docs' rootless example `docker.io/library/docker:*-dind-rootless` [docs: <https://docs.gitlab.com/runner/executors/docker/>] would **not** match a job that writes `docker:27-dind`.

### config.toml

```toml
[runners.docker]
  privileged = false
  services_privileged = true
  allowed_privileged_services = ["docker:*-dind"]   # name as the job writes it
  disable_entrypoint_overwrite = true               # services/images keep their own ENTRYPOINT
  volumes = ["/certs/client", "/cache"]
[runners.feature_flags]
  FF_NETWORK_PER_BUILD = true                       # per-job bridge; dind not on the shared default bridge
```

### Results

- **Unmodified dind+TLS job: works.** The service is privileged as before. The job container never needed privilege, because it only talks to the daemon over TCP+TLS [inferred from source plus the prior findings].
- **Playwright/Chromium: works.** It never needed privilege. Playwright launches Chromium without its sandbox by default (`chromiumSandbox` defaults to false) [docs].
- **Performance:** unchanged.
- **Residual risk: high against a deliberate job author** [inferred; standard container-escape reasoning, not tested on a VM]:
  - Any untagged job can request the allowed `docker:*-dind` service.
  - Through that daemon's API, which it holds the client certs for, the job can start nested privileged containers. A privileged container inside a privileged container still reaches the VM's devices and kernel interfaces, so the job can still get root on the VM.
  - Service-side knobs also escape the list [source]. A job's service `command:` decides what runs inside the privileged service, and so does its `entrypoint:` unless `disable_entrypoint_overwrite = true`. The service `docker: user:` option is not checked against `allowed_users`, which only applies to build containers.
- **What it does buy:** jobs that don't use dind (node, python, Playwright, the postgres and redis services) run unprivileged. Opportunistic malware in an `npm install` or `pip install` step is then contained by ordinary container isolation.
- **Verdict:** turn it on as defence in depth. It is not a fix.

## 2. sysbox-runc runtime

- **How:** an OCI runtime that gives each container its own user namespace, plus virtualised `/proc` and `/sys`, so system software (dockerd, systemd) runs inside without `--privileged` [docs: <https://github.com/nestybox/sysbox>].
- **Config:**
  - `[runners.docker] runtime = "sysbox-runc"`, `privileged = false`. sysbox does not support `--privileged` [docs].
  - The runner passes `Runtime` to service containers too, so the old gitlab-runner issue #27168 is fixed on `main` [source].
  - Host: install the sysbox package and register the runtime in `daemon.json`.
- **Does the unmodified dind+TLS job work?** Probably [inferred].
  - The `docker:dind` entrypoint does not test for privilege.
  - The mounts dockerd needs are permitted inside a sysbox container.
  - **This must be proven by the existing smoke test**, run with `--runtime sysbox-runc` and without `--privileged`.
- **Chromium:** works. Playwright runs it unsandboxed by default [docs].
- **Maintenance in 2026:**
  - v0.7.1 shipped 2026-07-31, and commits continue into October 2026.
  - The README says Docker sponsors it but does not officially support it.
  - There was a roughly 13-month gap before v0.7.0, and runc CVE fixes have landed months after upstream [inferred from release dates].
  - **Treat it as best-effort.**
- **Ubuntu 26.04 is outside its support matrix**, which stops at 24.04 (kernel 6.8+). Known issues that would affect this VM:
  - #1005 and #947: the `fusermount3` AppArmor profile shipped since Ubuntu 25.04 blocks sysbox-fs. Workaround: a local AppArmor override.
  - #1011: Docker 29.5+ fails container creation over time namespaces. Reported workaround: `"features": {"time-namespaces": false}` in `daemon.json`.
  - #1041: the host's network interface names leak into containers. This is information disclosure only.
- **Performance:** close to ordinary runc.
- **Residual risk:** reaching host root needs a kernel user-namespace bug or a sysbox bug. That is a far higher bar than privileged mode.
- **Verdict:** the only option that both keeps the job unchanged and closes the privileged path to root on the VM. It needs a throwaway-VM trial, ideally on Ubuntu 24.04 to stay inside the support matrix.

## 3. Rootless dind (`docker:dind-rootless`)

- The job asks for `docker:27-dind` by name, and the runner has no image-substitution mechanism. A local retag of `docker:27-dind` to the rootless image is a fragile hack, and `if-not-present` plus prune makes it unreliable.
- It still needs privileged mode (or equivalent seccomp/AppArmor relaxation) to set up its user namespace [docs].
- The unchecked service `user:` option means a job could run it as root anyway [source].
- **Verdict:** not workable under the no-CI-change constraint.

## 4. Kata Containers / gVisor

- **Kata:**
  - It needs nested virtualisation: Proxmox CPU type `host` and nesting enabled on `pve`.
  - Docker integration goes only through the deprecated shim-v2 runtime path and is tested with QEMU only.
  - It does not support `--link`, the runner's default way of connecting services.
  - With Docker, `--privileged` passes all host devices through, and that can't be turned off.
  - DinD storage has known problems on virtio-fs [docs: <https://katacontainers.io/docs/>].
- **gVisor:**
  - Docker-in-gVisor needs `dockerd --iptables=false` and tmpfs or vfs storage, which the job's stock dind service does not pass [docs: <https://gvisor.dev/docs/tutorials/docker-in-gvisor/>].
  - It adds substantial overhead on syscall-heavy builds [inferred].
- **Verdict:** neither runs the unmodified job.

## 5. userns-remap on the host daemon

- moby rejects `--privileged` on a remapped daemon unless the container uses `--userns=host`, which opts out of the remap [source and docs: <https://docs.docker.com/engine/security/userns-remap/>].
- The runner's `userns_mode` applies to build and service containers alike. The choice is therefore "dind breaks" or "nothing is remapped".
- With option 1 (privileged dind only), remap could cover the unprivileged containers, but the dind service would still need `host`. It adds complexity for a small gain.
- **Verdict:** incompatible with the privileged dind path. No.

## 6. Seccomp, AppArmor and no-new-privileges with privileged

- An explicitly set seccomp or AppArmor profile still applies to a privileged container, and so does the daemon-level `no-new-privileges` [source].
- None of them meaningfully contains a privileged container, which has every capability and every device.
- A profile tight enough to matter would break dockerd inside dind.
- **Verdict:** not recommended.

## Comparison

| Option | Unmodified dind+TLS job | Playwright | Perf | Maturity 2026 | Residual: job → VM root |
|---|---|---|---|---|---|
| All privileged (current design) | yes | yes | baseline | stable | trivial, for every job |
| Privileged dind service only (§1) | yes | yes | baseline | stable (runner keys) | yes, deliberately via dind; opportunistic non-dind jobs contained |
| sysbox-runc (§2) | probably (must smoke-test) | yes | ~baseline | best-effort; 26.04 unsupported | needs a kernel or sysbox bug |
| Rootless dind (§3) | no (name mismatch) | n/a | n/a | n/a | n/a |
| Kata (§4) | no (links, devices, nested virt) | ? | high | Docker path deprecated | — |
| gVisor (§4) | no (dind flags) | slow | high | stable | — |
| userns-remap (§5) | breaks dind | yes | baseline | stable | — |
| seccomp/AppArmor (§6) | breaks or no effect | yes | baseline | stable | unchanged |

## Recommendation

1. **Ship now:**
   - `privileged = false`, `services_privileged = true`, `allowed_privileged_services = ["docker:*-dind"]`;
   - `disable_entrypoint_overwrite = true`;
   - `FF_NETWORK_PER_BUILD = true`.
2. **Keep treating the VM as host-root for anyone who can push to an attached project.** That means a dedicated VM, locked project runners, LAN egress firewalled outside the VM, and re-image plus runner recreation on suspected compromise.
3. **Trial sysbox-runc on a throwaway VM**, preferably Ubuntu 24.04. If the existing smoke test passes, switch the runner's runtime and drop `services_privileged`.

Source checkouts used for this analysis live in the session scratchpad (`scratchpad/src/`), not in the repo.
