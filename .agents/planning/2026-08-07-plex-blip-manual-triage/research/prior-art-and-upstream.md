# Research: Prior Art & Upstream References

**Purpose:** record what the two preceding projects already settled, so this one
does not re-derive it; and collect the upstream references the design depends on.

---

## Part 1 — In-repo prior art

### `.agents/planning/2026-07-29-plex-monitoring/`

**Original question:** "sporadic connection issues with Plex, LAN and remote — what
metrics and logs do I need and how should I track them?"

**What it landed** (all in `ansible/roles/docker_host/`):
- `pve-exporter` (3.9.0) as a **multi-target** job — `metrics_path: /pve` with the
  `__param_target` relabel. The template carries an unusually blunt comment
  explaining that pointing the job straight at `pve-exporter:9221` reads `UP` in
  Status → Targets while producing **zero** `pve_*` series. That is a trap worth not
  re-entering.
- `plex-exporter` (axsuul 2.1.0) as a **single-target** job on the default
  `/metrics` path — deliberately the opposite shape, and the template says so.
- Grafana dashboards for the homelab, PVE, and Plex Health.

**Operator-gate history worth knowing:** this project parked repeatedly on operator
gates (`[[plex-monitoring-four-operator-gates-one-just-play]]`,
`[[plex-monitoring-step1b-gate-resumed]]`), and there was a **two-week Prometheus
outage** during its life. At 15-day retention, that outage means most pre-outage
history is already unrecoverable — relevant to the retention argument in
[instrumentation-gaps.md](instrumentation-gaps.md) §4.

**Carried forward:** the existing metric surface and dashboard, inventoried in
[current-telemetry-inventory.md](current-telemetry-inventory.md).

---

### `.agents/planning/2026-08-04-debug-plex-blip/`

**Original question:** a blip at ~07:00 EDT on 2026-08-04 — heartbeat gap from
06:59:15, mild CPU rise to ~30%, Traefik and Plex logs apparently silent. Stated
objective: *"the task at hand is to first figure out how to track this down as this
has happened multiple times but is sporadic."*

**Status:** `implementation/progress.md` reports **all 5 steps complete**. Shipped:

| Artifact | Path |
|---|---|
| Offline log analyzer | `scripts/analyze_plex_blips.py` (+ `test_analyze_plex_blips.py`) |
| Watchdog | `ansible/roles/plex/files/plex_blip_watchdog.py` (+ `test_plex_blip_watchdog.py`) |
| systemd integration | `ansible/roles/plex/templates/plex_blip_watchdog.service.j2` |
| Scrape-collision remediation | `prometheus.yml.j2` 60s/50s; `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS=1800` |
| WAL audit + maintenance runbook | `docs/runbooks/plex-sqlite-maintenance.md` |

**The root-cause finding, in one paragraph:** SQLite lock contention began around
06:56:50 from client timeline updates and bandwidth-statistics flushes. Prometheus
then scraped `plex-exporter` at 06:57:16, triggering the *synchronous* per-section
`GET /library/sections/<key>/all` sweep; congested SQLite made section 3 alone take
29.8s, blowing the then-30s `scrape_timeout`. The aborted scrape meant the sweep was
retried on the next 60s tick — 35.9s at 06:58:17, 34.4s at 06:59:19. Three minutes
of ~35s synchronous queries exhausted Plex worker threads, blocked client heartbeat
updates past the 180s idle threshold, and at 07:00:10 Plex shut down the idle
session and `SIGKILL`ed transcoder job 76242. **Causal inversion confirmed:** the
scheduled hourly library scan did *not* fire at 07:00:05 that day — it fired at
07:05:10, delayed by the storm it was initially suspected of causing.

**Three things this project must carry forward:**

1. **The amplifier was fixed; the trigger was not.** The remediation lengthened the
   sweep interval and the timeout, breaking the retry storm. It did not remove the
   underlying contention between timeline updates, bandwidth flushes, and reads. A
   recurrence post-remediation is therefore *new information*, not a regression —
   and the runbook should say so, because the instinct will be to assume the fix
   failed.
2. **"Traefik logs show nothing" was never a finding.** The rough-idea recorded it
   as a null result. It was an artifact of `accessLog` never having been configured
   ([current-telemetry-inventory.md](current-telemetry-inventory.md) §3). Any future
   triage that concludes "the logs are clean" must first establish that the logs
   exist.
3. **The verification notes were left open.** `implementation/progress.md` lists
   unfinished follow-ups — a read-only WAL audit check, an optional off-peak
   maintenance timer at 03:30, and in-container `sqlite3` pragma verification. These
   are adjacent to, but not part of, this project's scope; worth flagging in the
   summary rather than absorbing.

---

### Other repo context that bears on triage

| Source | Why it matters |
|---|---|
| `docs/runbooks/plex-sqlite-maintenance.md` | The WAL/maintenance procedure; class-A remediation reference. |
| `docs/runbooks/plex-ramdisk.md`, `scripts/test_plex_ramdisk_bind_mount_shape.py` | Transcode dir is tmpfs — **a restart wipes transcoder evidence**. Decay hazard. |
| `docs/runbooks/plex-latency-baseline.md`, `docs/plex-remote-latency-audit.md`, `scripts/measure_plex_latency.py` | Established latency baselines and the measurement harness. Remote `/identity` TTFB 157/293/486 ms; DNS+TCP+TLS is 77–85% of every remote sample. |
| `docs/runbooks/{das-zfs-migration,usb-media-mounts}.md` | The media storage topology behind blind class D. |
| `scripts/verify_plex_ihd_cvt.py` | After-the-fact QSV/iHD verification; the only class-F tool. |
| `traefik.yml.j2` histogram-bucket comment (lines 65–104) | Documents that `traefik_*_request_duration_seconds` measures **server-side handler duration only** — no TCP connect, no TLS, no client transit. Do not read it as client-experienced latency. |

**Two measurement cautions established by prior work, both of which constrain this
design:**

- `[[plex-lan-vantage-from-dev-box-is-not-a-lan-client]]` — a probe from `.60` or
  `.111` to `.110` traverses 0.046 ms of virtual bridge. It is a valid *reachability*
  measurement and an invalid *LAN client latency* measurement.
- `[[plex-optimization-step2-premise-false]]` — measured 2026-07-28, Traefik is <2%
  of a remote request. Proxy overhead is not where remote latency lives. Relevant
  here as a prior on class E: for *latency*, suspect the path, not the proxy.
  (Reachability is a separate question, and one the proxy can absolutely break.)

---

## Part 2 — Upstream references

### Plex

- **[Plex API: Server Identity][plexopedia]** — `GET /identity` returns
  `machineIdentifier` and version; **unauthenticated**, no `X-Plex-Token` required.
- **[plexinc/pms-docker — `root/healthcheck.sh`][pms-hc]** — Plex's own container
  healthcheck, i.e. upstream's answer to "how do you cheaply ask if Plex is alive".
  Direct precedent for the blackbox probe target.
- **[Troubleshooting Remote Access][plex-remote]**, **[Why can't the Plex app find
  or connect to my server?][plex-connect]** — official failure-mode taxonomy for
  class E/G.
- **[Plex forum — Players randomly unable to connect to server][plex-forum]** — the
  community thread closest to this symptom profile.

### Prometheus ecosystem

- **[axsuul/plex-media-server-exporter][axsuul]** — metric definitions. `plex_up`
  1/0 = reachable/unreachable; `plex_sessions_count` labelled by username, user_id,
  and state; `plex_media_count` by title and type; separate audio/video transcode
  counters; `plex_info` carries the server version.
  `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS` (default **300**, set to **1800**
  here) throttles the expensive library collection. The README does not document
  whether collection is synchronous within the scrape — **the repo's own template
  comment asserts it is, verified empirically against the shipped 2.1.0 image**, and
  the 2026-08-04 timeline corroborates it. Treat the in-repo comment as the
  authority over the upstream README here.
- **[prometheus/blackbox_exporter][bb]** — the `/probe?module=&target=` multi-target
  pattern and its relabel triplet; probe timeout is derived from Prometheus'
  `scrape_timeout` (slightly reduced), further capped by the exporter's own config,
  defaulting to 120s if neither is set.
  **[HTTP probe configuration reference][bb-http]** for module options
  (`valid_status_codes`, `method`, `fail_if_body_not_matches_regexp`, `tls_config`).
- **[Prometheus storage][prom-storage]** — `--storage.tsdb.retention.time`, default
  15d when unset.

### Traefik

- **[Logs and AccessLogs reference][traefik-al]** — `accessLog` options: `filePath`,
  `format` (`common` / `genericCLF` / `json`), `bufferingSize`, `addInternals`,
  `filters` (`statusCodes`, `retryAttempts`, `minDuration`), `fields`
  (`defaultMode`, `names`, `headers`, `queryParameters`). Field names of interest:
  `Duration`, **`OriginDuration`**, **`Overhead`**, `RetryAttempts`,
  `DownstreamStatus`, `OriginStatus`, `ServiceName`, `ClientAddr`, `RequestPath`,
  `RequestMethod`, `StartUTC`.

### Session history

- **[mm503/tautulli-exporter][taut-exp]** — Tautulli API → Prometheus.
- **[bdgarmon/GrafanaPlexMonitor][gpm]** — NOC-style Grafana dashboards over
  Tautulli-sourced Prometheus series, aimed specifically at diagnosing playback
  failures and buffering events.
- **[Tautulli Exporter Guide][taut-wiki]**, **[tautulli.com][taut]** — session
  history lives in `config/tautulli.db`.

---

[plexopedia]: https://www.plexopedia.com/plex-media-server/api/server/identity/
[pms-hc]: https://github.com/plexinc/pms-docker/blob/master/root/healthcheck.sh
[plex-remote]: https://support.plex.tv/articles/200931138-troubleshooting-remote-access/
[plex-connect]: https://support.plex.tv/articles/204604227-why-can-t-the-plex-app-find-or-connect-to-my-plex-media-server/
[plex-forum]: https://forums.plex.tv/t/players-randomly-unable-to-connect-to-server/931919
[axsuul]: https://github.com/axsuul/plex-media-server-exporter
[bb]: https://github.com/prometheus/blackbox_exporter
[bb-http]: https://deepwiki.com/prometheus/blackbox_exporter/2.3-http-probe-configuration
[prom-storage]: https://prometheus.io/docs/prometheus/latest/storage/
[traefik-al]: https://doc.traefik.io/traefik/reference/install-configuration/observability/logs-and-accesslogs/
[taut-exp]: https://github.com/mm503/tautulli-exporter
[gpm]: https://github.com/bdgarmon/GrafanaPlexMonitor
[taut-wiki]: https://github.com/Tautulli/Tautulli/wiki/Exporter-Guide
[taut]: https://tautulli.com/
