# GitLab Runner: registration, config.toml, tokens, concurrency, metrics, install

Researched 2026-11-04. Versions seen today:
- **gitlab-runner 19.5.2-1** is the newest package in the official apt repo for both `ubuntu/noble` and `ubuntu/resolute` (26.04). The repo index is dated 2026-10-29.
- gitlab-runner `main` is at `VERSION` 19.6.0, commit `3e6aa9a3`, 2026-11-03.
- Source citations below are from that `main` checkout: `https://gitlab.com/gitlab-org/gitlab-runner/-/blob/main/<path>`.
- gitlab.com (SaaS) runs the current GitLab release, so runner 19.x matches it.

## 1. Runner authentication tokens (`glrt-`): the flow

The current model, per <https://docs.gitlab.com/ci/runners/new_creation_workflow/>:
1. Create the runner on the GitLab side, in the UI or with the API.
2. GitLab returns a runner authentication token with the prefix `glrt-`.
3. On the host, `gitlab-runner register --token glrt-...`, or write `config.toml` yourself (see section 3).

Server-side attributes are set **only in GitLab**, in the UI or API: tags, run-untagged, locked, maximum timeout, protected (access level), paused and the maintenance note. With `--token` the CLI **rejects** these flags. `register.go` raises a fatal error: "Runner configuration other than name and executor configuration is reserved (specifically --locked, ...". With the legacy `--registration-token glrt-...` spelling they are ignored with a warning. Sources: <https://docs.gitlab.com/runner/register/>, `commands/register.go` (`ensureServerConfigArgsEmpty`).

### Creating a project runner

- **UI:** Project > Settings > CI/CD > Runners > *New project runner*. Set tags or tick **Run untagged jobs**, then *Create runner*. The page shows the `glrt-` token once. (<https://docs.gitlab.com/ci/runners/runners_scope/>; the UI flow is also described at <https://docs.gitlab.com/ci/runners/new_creation_workflow/>.)
- **API:** `POST /user/runners`, documented at <https://docs.gitlab.com/api/users/> under "Create a runner linked to a user".
  - `runner_type` is required: `instance_type`, `group_type` or `project_type`.
  - `project_id` is required when the type is `project_type`.
  - Optional: `description`, `paused`, `locked`, `run_untagged`, `tag_list` (comma-separated), `access_level` (`not_protected` or `ref_protected`), `maximum_timeout` (seconds), `maintenance_note`.
  - Auth: "An access token with the `create_runner` scope", from a user who is admin or holds a sufficient role on the namespace or project. The fetched page said Owner. In my experience project runners can be created by Maintainers in the UI; **verify which role is needed on gitlab.com before relying on it.**
  - Response: `id` (the runner ID, e.g. `9171`), `token` (`glrt-...`) and `token_expires_at` (`null` when the token does not expire). "copy or save the `token` in the response, the value cannot be retrieved again."
  - Example:
    ```sh
    curl --request POST --header "PRIVATE-TOKEN: $PAT" \
      --data runner_type=project_type --data project_id=$PID \
      --data run_untagged=true --data "description=pve-runner-1" \
      --data maximum_timeout=7200 \
      https://gitlab.com/api/v4/user/runners
    ```

### What `gitlab-runner register --token glrt-...` actually does

Read from source, `commands/register.go`:
- It **does not create a runner.** For a `glrt-` token it skips the registration-token prompt and calls `s.network.VerifyRunner(ctx, s.RunnerConfig, s.SystemID)`, which is `POST /api/v4/runners/verify` with `token` and `system_id`.
- It fails if the result is nil or `result.ID == 0`.
- From the response it sets:
  ```go
  s.ID = result.ID
  s.TokenObtainedAt = s.timeNowFn().UTC().Truncate(time.Second)
  s.TokenExpiresAt = result.TokenExpiresAt
  ```
  The token stays the one you supplied. The legacy path is different: there `s.Token = result.Token`.
- It then **appends** a `[[runners]]` block to `config.toml`. It does not de-duplicate: "the registered runner is added to the configuration file without removing existing entries" (<https://docs.gitlab.com/runner/commands/>). **Running `register` twice gives two identical `[[runners]]` blocks in the local file.** Both poll with the same token and system_id, so GitLab still shows **one** runner manager, but locally you get doubled concurrency and log noise. This is the main reason not to call `register` from Ansible on every run.
- If register is interrupted it cleans up with `UnregisterRunnerManager(...)`, which is `DELETE /runners/managers`. It never deletes the runner itself.

What `/runners/verify` does on the server, from `lib/api/ci/runner.rb` and `lib/api/ci/helpers/runner.rb` in gitlab-org/gitlab:
- It calls `authenticate_runner!` with `ensure_runner_manager: true`, the default.
- `current_runner_manager` reads `params.fetch(:system_id, LEGACY_SYSTEM_XID)` and calls `current_runner.ensure_manager(system_xid)`.
- So **any** authenticated call carrying a system_id **creates or finds the runner-manager record for that `system_id`**. That covers verify and every job request.
- Re-registering or re-verifying from the same host, with the same system_id, is idempotent server-side.
- A **new system_id** (a new host or a re-image) appears as an **additional runner manager** under the same runner. The UI shows managers "under the same runner in the GitLab UI, but with an identifying system ID" (<https://docs.gitlab.com/ci/runners/new_creation_workflow/>).
- Managers can be listed with `GET /runners/:id/managers` (<https://docs.gitlab.com/api/runners/>).
- Stale managers are cleaned up after **7 days** without contact. That figure comes from GitLab MRs and issues, not the main docs: <https://gitlab.com/gitlab-org/gitlab/-/merge_requests/108837>, <https://gitlab.com/gitlab-org/gitlab/-/issues/423306>. Issue 423306 suggests the cleanup may be tier-gated on some installs.

## 2. `.runner_system_id` and re-imaging

Source: `commands/internal/configfile/system_id_state.go`, and <https://docs.gitlab.com/runner/commands/>.
- On startup the runner reads `.runner_system_id` **from the directory containing `config.toml`**, so `/etc/gitlab-runner/.runner_system_id` when running as root.
- A valid value matches `^[sr]_[0-9a-zA-Z]{12}$`. If the file is missing or malformed, the runner generates an ID and writes the file with mode 0600.
- Generation is **deterministic from `/etc/machine-id`**: `"s_" + hex(HMAC-SHA256(key=machine-id, "gitlab-runner"))[0:12]`. A random `r_...` ID is used only if the machine ID is unavailable.
- If the file cannot be written, the runner logs a warning. Older versions (15.7/15.8) refused to start.

Implications:
- Re-imaging the VM gives a new machine-id. This repo's Packer template seals the image with `truncate -s 0 /etc/machine-id` (`packer/ubuntu26.pkr.hcl:83`), so every clone or re-image gets a fresh one. The runner then gets a new `s_` system_id and a **new runner-manager entry**. The old one goes stale and offline, and is GC'd after about 7 days. **The token stays valid.** No new runner is created and no GitLab action is needed.
- For a stable identity across a re-image, Ansible could template `.runner_system_id` with a fixed `s_xxxxxxxxxxxx` value. This is optional and cosmetic.
- **Cloning a VM without resetting machine-id would make two hosts share one system_id.** The Packer seal prevents this, but keep it in mind for the second node.
- The system_id also feeds the Docker cache-volume name (`ProjectRealUniqueName` = sha256 of token, system_id, project and concurrency id). A new system_id or a rotated token therefore orphans the old `runner-*-cache-*` volumes. The scheduled prune reclaims them; see docker-upkeep.md.

## 3. Rendering config.toml from a template, with no `register`

**Yes, this works.** `gitlab-runner run` "reads all defined runners from `config.toml`" (<https://docs.gitlab.com/runner/commands/>). The Helm chart has an equivalent mode, `configOverride`, that writes a config verbatim and skips registration (<https://gitlab.com/gitlab-org/charts/gitlab-runner/-/merge_requests/544>). The runner-manager record is created on the first authenticated poll (section 1).

`RunnerCredentials` in `common/config.go`:

```go
URL             string    `toml:"url" ... required:"true"`
ID              int64     `toml:"id"`
Token           string    `toml:"token" ... required:"true"`
TokenObtainedAt time.Time `toml:"token_obtained_at"`
TokenExpiresAt  time.Time `toml:"token_expires_at"`
```

`RunnerSettings.Executor` is `toml:"executor" required:"true"`.

- **Required:** `url`, `token`, `executor` and the executor section (`[runners.docker] image = ...`). A `name` is effectively always wanted; it is local-only.
- **`id`** is optional. It is the GitLab runner ID returned by `POST /user/runners` or `/runners/verify`. In the docker executor it is used only for the `runner_id` label (`executors/docker/labeler.go`) and by the experimental `FF_SUSPENDABLE_ENVIRONMENTS`, which errors when `ID <= 0`. Recommendation: put it in vars next to the token, because it is known from the creation response or the UI URL.
- **`token_obtained_at` and `token_expires_at`** can be omitted, which leaves them as the zero time. With a zero `token_expires_at`, automatic rotation is skipped entirely (see section 5). For gitlab.com project runners the token has no expiry by default (`token_expires_at: null`), so omitting them is correct.
- **Caveat: the runner writes to config.toml.** Token rotation saves the file (`mr.configfile.Save()` in `commands/multi.go`), and so do `verify --delete` and `register`. With a non-expiring token none of these run during normal operation, and Ansible remains the only writer. If expiry is ever enabled, Ansible's template would fight the runner over `token`. Either disable rotation with `FF_DISABLE_AUTOMATIC_TOKEN_ROTATION`, or stop templating the token line.
- Hot reload is covered in section 9.

### `gitlab-runner verify`

Source: `commands/verify.go`.
- For each `[[runners]]` block, or one selected with `--name`, `--url` or `--token`, it calls `VerifyRunner(...)` with the system_id, i.e. `POST /runners/verify`.
- It exits with a fatal error, non-zero, when any runner fails ("Failed to verify runners"). It **does not modify config.toml** unless `--delete` is given.
- It doesn't check the service: "it doesn't verify if the runners are being used by the GitLab Runner service" (<https://docs.gitlab.com/runner/commands/>).
- It is safe as an Ansible check task (`changed_when: false`). Note that a successful verify also creates or touches the runner-manager record.
- `verify --delete` drops runners deleted in GitLab from config.toml by rewriting the file. "This operation cannot be undone." **Don't use it with a templated config**: Ansible would re-add the entry anyway.
- `unregister`, for UI- or API-created runners, "deletes the runner manager, but not the runner". Fully deleting the runner requires the UI or `DELETE /runners` with the token (<https://docs.gitlab.com/runner/commands/>, <https://docs.gitlab.com/api/runners/>).

## 4. Deprecated registration tokens: status

- Deprecated since 15.6. In **GitLab 17.0+ the legacy registration workflow can be disabled**, and attempts then return `410 Gone` (<https://docs.gitlab.com/ci/runners/new_creation_workflow/>).
- **Removal is "scheduled for removal in GitLab 20.0"** (<https://docs.gitlab.com/runner/register/>). Docs mirrors place 20.0 in **May 2027** (<https://docs.gitlab.com/ci/runners/new_creation_workflow/>; deprecations page <https://docs.gitlab.com/update/deprecations/>).
- As of today (GitLab 19.x) registration tokens are not yet removed, but the plan must not use them.

## 5. Token rotation and expiry for `glrt-` tokens

- `token_expires_at` is `null` unless an admin sets an instance, group or project "Runners expiration" interval (Admin > Settings > CI/CD; <https://docs.gitlab.com/ci/runners/configure_runners/>).
  - The admin setting has a minimum of 7200 s (<https://gitea.com/yoginth/gitlab/src/branch/master/config/application_setting_columns/runner_token_expiration_interval.yml>; mirror of `config/application_setting_columns`).
  - Group and project owners cannot set this on gitlab.com SaaS as far as I found, so tokens are **non-expiring by default**.
- **Automatic self-rotation** happens in the runner, in `commands/multi.go` (`nextRunnerToReset`, `resetOneRunnerToken`):
  - It applies only when `TokenExpiresAt` is non-zero.
  - At `TokenObtainedAt + 0.75 x (TokenExpiresAt - TokenObtainedAt)` (`common/consts.go`: `TokenResetIntervalFactor = 0.75`) the runner calls `POST /runners/reset_authentication_token`.
  - It then rewrites `token`, `token_expires_at` and `token_obtained_at` in config.toml.
  - `FF_DISABLE_AUTOMATIC_TOKEN_ROTATION` turns this off and only logs a warning.
  - Known issue: when one token is used on several hosts, "only the first runner manager receives the new token" (<https://docs.gitlab.com/ci/runners/new_creation_workflow/>).
- **Manual rotation:**
  - `POST /runners/:id/reset_authentication_token` (admin or owner, PAT), or
  - `POST /runners/reset_authentication_token` with `token=<current glrt>` (<https://docs.gitlab.com/api/runners/>).
  - The response contains the new `token` and `token_expires_at`. The old token stops working immediately.
  - Runbook: reset, put the new token in vault, run the playbook. The template changes, the runner hot-reloads and keeps the same runner ID.
  - Alternative: the UI "Reset token", or delete and re-create the runner, which changes the ID (<https://docs.gitlab.com/ci/runners/configure_runners/>).

## 6. Untagged jobs

**Confirmed: this is a GitLab-side runner attribute, not a config.toml key.**
- No `run_untagged` key exists in `[[runners]]` for auth-token runners.
- `--run-untagged` is listed among the deprecated register flags that are ignored or rejected with auth tokens (<https://docs.gitlab.com/runner/register/>).
- To set it:
  - in the UI, Edit runner > **Run untagged jobs** (<https://docs.gitlab.com/ci/runners/configure_runners/>);
  - `run_untagged=true` on `POST /user/runners`;
  - or `PUT /runners/:id run_untagged=true` (<https://docs.gitlab.com/api/runners/>).
- Also set **Maximum job timeout** there. The minimum is 600 s, and if it is unset the project timeout applies. lumologic's jobs need 90 min, so use at least 5400 s, or leave it unset.

## 7. Concurrency: `concurrent`, `limit`, `request_concurrency`, `check_interval`

Source: <https://docs.gitlab.com/runner/configuration/advanced-configuration/>.
- **`concurrent`** (global): "Limits how many jobs can run concurrently, across all registered runners... this value sets a maximum for all of those values combined". "`0` is forbidden": the process exits with a critical error.
- **`limit`** (per `[[runners]]`): "how many jobs can be handled concurrently by this registered runner. `0` (default) means do not limit." The effective cap is min(limit, global remaining).
- **`request_concurrency`** (per runner): the number of concurrent long-poll job requests to GitLab. The default is `1`. The docs flag `request_concurrency=1` as a "request bottleneck... during long polling", especially with a low `limit`. For one VM with concurrent=4, `request_concurrency = 2..4` is reasonable. `FF_USE_ADAPTIVE_REQUEST_CONCURRENCY` only matters above 1. Support KB: <https://support.gitlab.com/hc/en-us/articles/21324350882076-GitLab-Runner-Concurrency-Tuning-Understanding-request-concurrency>.
- **`check_interval`** (global): seconds between job checks, default `3`; values of 0 or less mean the default.
  - With N `[[runners]]` blocks the runner sleeps `check_interval / N` between them.
  - After it receives a job it immediately re-polls until there are no jobs or it reaches `concurrent` or `limit`, unless `strict_check_interval = true`.
- Other global keys: `shutdown_timeout` (default 30 s, used only for the *forceful* abort path; see docker-upkeep.md), `log_level`, and `connection_max_age` (default 15m).

## 8. Metrics

Source: <https://docs.gitlab.com/runner/monitoring/>.
- Set the global `listen_address = ":9252"`, or `"<ip>:9252"`. "If the listen address does not contain a port, it defaults to `9252`."
- It is served at `/metrics`, with **no auth**. Bind to the LAN IP and firewall it to the Prometheus host.
- **`listen_address` changes need a service restart**, not a hot reload. It is the documented exception (<https://docs.gitlab.com/runner/configuration/advanced-configuration/>). The Ansible handler must restart the service when this value changes.
- Metric names, read from source on `main`:

  | Metric | Meaning |
  |---|---|
  | `gitlab_runner_jobs` (gauge) | "The current number of running builds", labels incl. runner, system_id, state, stage, executor_stage (`commands/builds_helper.go`) |
  | `gitlab_runner_jobs_total` | "Total number of handled jobs" |
  | `gitlab_runner_job_duration_seconds` | Job duration histogram |
  | `gitlab_runner_job_queue_duration_seconds` | Job queue duration histogram |
  | `gitlab_runner_concurrent` | Value of the `concurrent` setting |
  | `gitlab_runner_limit` | Value of the `limit` setting |
  | `gitlab_runner_request_concurrency`, `_exceeded_total`, `_hard_limit` | Request-concurrency gauges |
  | `gitlab_runner_errors_total` | "The number of caught errors", a counter labelled by log `level` (`helpers/prometheus/log_hook.go`) |
  | `gitlab_runner_api_request_statuses_total` | API requests by endpoint and status. Good for an "unauthorized/403" alert, which catches an invalid token |
  | `gitlab_runner_api_request_attempts_total`, `gitlab_runner_api_request_duration_seconds` | Request attempts and latency |
  | `gitlab_runner_worker_healthy` | "1 while the runner worker is healthy, 0 from exceeding unhealthy_requests_limit..." |
  | `gitlab_runner_worker_health_check_failures_total` | Worker health-check failures |
  | `gitlab_runner_version_info` | Constant `1` with version labels |

  Plus the standard `process_*` and `go_*` metrics.
- Alert candidates:
  - `up == 0`;
  - `gitlab_runner_worker_healthy == 0`;
  - an increase in `gitlab_runner_api_request_statuses_total{status=~"401|403"}`;
  - `rate(gitlab_runner_errors_total{level="error"}[15m]) > 0`.
  - Pair these with node_exporter disk alerts, as on docker-host.

## 9. Install from the official apt repo

Source: <https://docs.gitlab.com/runner/install/linux-repository/>.
- **Script:** `https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh`. I downloaded and read it on 2026-11-04. It does the following:
  - Fetches the key `https://packages.gitlab.com/gpgkey/gpg.key`, runs `gpg --dearmor` and writes `/etc/apt/keyrings/runner_gitlab-runner-archive-keyring.gpg` (0644).
  - Writes `/etc/apt/sources.list.d/runner_gitlab-runner.list`, fetched from `.../config_file.list`. For noble or resolute it contains:
    ```
    deb [signed-by=/etc/apt/keyrings/runner_gitlab-runner-archive-keyring.gpg] https://packages.gitlab.com/runner/gitlab-runner/ubuntu resolute main
    ```
  - Removes the old `/etc/apt/trusted.gpg.d/runner_gitlab-runner.gpg`.
- **For Ansible, do this manually without the script:** `get_url` the key, then `deb822_repository` or `apt_repository` with `signed_by`. The repo works for **Ubuntu 26.04 "resolute"**: `dists/resolute/InRelease` returns 200 and contains 19.5.2-1.
- **Repo signing key:** `InRelease` is signed by `F640 3F65 44A3 8863 DAA0 B6E0 3F01 618A 5131 2F3F`, "GitLab B.V. (package repository signing key)", rsa4096, **expires 2028-02-06**. I verified this with `gpg --verify` on 2026-11-04.
  - The docs page also lists a *package* signing key `931D A69C FA3A FEBB C97D AA8C 6C57 C29C 6BA7 5A4E` with expiry 2026-04-28. That is a different key, used for package-file signatures, not apt metadata, and its listed expiry is already past.
  - "Users must manually install new keys when they are updated." Having Ansible re-fetch the key with `get_url` handles a key refresh.
- **Packages:** `gitlab-runner` and **`gitlab-runner-helper-images`**. Since 17.7.1 the helper-images package must be installed explicitly when pinning: `apt install gitlab-runner=19.5.2-1 gitlab-runner-helper-images=19.5.2-1`. Pin both to the same version, or install both as `latest`.
- **Config path:** run as root, `/etc/gitlab-runner/config.toml`. As non-root, `~/.gitlab-runner/config.toml` (<https://docs.gitlab.com/runner/commands/>).
  - The post-install script creates the `gitlab-runner` system user and `/etc/gitlab-runner`, then stops, uninstalls, reinstalls and starts the service (`packaging/root/usr/share/gitlab-runner/post-install`).
  - The service runs as root with `--user gitlab-runner`, which applies only to the shell executor.
  - Post-install warns if the user is in the `docker` group. Don't add it.
- **Automatic reload:** "The runner checks `config.toml` for changes every 3 seconds and reloads if needed". It also reloads on `SIGHUP`. Most global and `[[runners]]` options need no restart. Exceptions: `listen_address` needs a restart, and `[session_server]` changes may need `gitlab-runner restart` (<https://docs.gitlab.com/runner/configuration/advanced-configuration/>).
  - Ansible pattern: template the file at mode 0600 root:root and let the runner hot-reload. Notify a restart handler only when `listen_address` or `session_server` changes, or simply always restart. A restart kills running jobs unless the SIGQUIT drop-in is installed; see docker-upkeep.md.
- **Package install/upgrade side effect:** the deb `postinst` runs `/usr/share/gitlab-runner/clear-docker-cache prune` unless `NO_DOCKER_PRUNE` is set (`packaging/scripts/postinst.deb`). This removes runner-labelled (`com.gitlab.gitlab-runner.managed=true`) stopped containers, unused labelled images and unused networks, but not volumes. It is harmless, but it is a side effect of every upgrade.
