# Research: Instrumentation Gaps & Candidate Additions

**Purpose:** the additions that would close the undecidable classes from
[blip-taxonomy-and-discriminators.md](blip-taxonomy-and-discriminators.md), each
priced by cost, risk, and blast radius.

---

## The governing constraint: in this homelab, monitoring has already caused an outage

This is not a hypothetical. The 2026-08-04 investigation established that
`plex-exporter`'s synchronous library sweep — a *monitoring* component — was the
amplifier that turned transient SQLite contention into a 3-minute stream-killing
stall. The observer changed the observed.

Every candidate below is therefore priced on **load imposed on Plex and on CT 110**,
not just on implementation effort. The design principle that follows:

> **Prefer probes that touch Plex's cheapest surface, or that don't touch Plex at
> all.** Read the kernel, read the proxy, read the log — before you read the API.

This is why `/identity` matters so much (§2): it is unauthenticated and does no
database work, which makes it the one Plex endpoint safe to poll at high frequency.

---

> **Revised 2026-08-07 after the live-blip case study.** Two changes below are
> driven by measured evidence from `/tmp/plex-logs/2026-08-07/`:
> a new item **0** (the watchdog/analyzer regex gap) now outranks everything else,
> and **§2's `/identity` recommendation is corrected** — a `probe_success` check on
> `/identity` would have stayed green through a five-minute outage. See
> [live-blip-2026-08-07-case-study.md](live-blip-2026-08-07-case-study.md).

## Priority ranking

| # | Addition | Closes class | Cost | Risk to Plex | Verdict |
|---|---|---|---|---|---|
| **0** | **`Held transaction for too long` trigger in watchdog + analyzer** | **A2 (the live fault)** | **Trivial** | **None** | **Do first — highest value** |
| 1 | Prometheus alert rules + notification | *detection itself* | Low | **None** | **Do first** |
| 2 | blackbox-exporter synthetic probes | E, H1, H2, B | Low | **Very low** | **Do first** |
| 3 | Traefik `accessLog` | E | Very low | None | **Do first** |
| 4 | Prometheus retention → 90d | cross-event | Trivial | None | **Do first** |
| 5 | `up{}` + `plex_info` Grafana panels | H1, B | Trivial | None | **Do first** |
| 6 | node-exporter inside CT 110 | C, B, D | Low | Low | Do |
| 7 | Watchdog JSONL → textfile collector | A, all | Medium | None | Do |
| 8 | PVE-host storage telemetry (ZFS/USB/disk) | D | Medium | None | Do |
| 9 | Tautulli + session history | G, H3 | Medium | **Medium** | Consider |
| 10 | Loki + Promtail | all (convenience) | High | Low | Defer |
| 11 | GPU/QSV telemetry | F | High | Low | Defer |

---

## 0. Match the causal log line — a one-line change, verified against a real outage

`plex_blip_watchdog.py::check_trigger` and `analyze_plex_blips.py::parse_log_line`
both key on `"Took too long" ... "to start a transaction"` — the **waiter's** view.
Plex also emits `Held transaction for too long (<site>): N seconds` — the
**holder's** view, which appears *first* and **names the offending code site in its
own text**.

Measured on the 2026-08-07 blip:

- first `Held transaction` line: **06:37:33.273**
- first line the watchdog can match: **06:38:22.285**
- **the watchdog fires 49 seconds late**, after the cascade is already underway

Executing `check_trigger` against the line returns `None`. The most causally
specific signal Plex produces is currently discarded by both tools.

**Change:** add a `TX_HELD` event type keyed on `Held transaction for too long`,
capturing the parenthesised site and the duration. Both files already have test
suites (`scripts/test_plex_blip_watchdog.py`, `scripts/test_analyze_plex_blips.py`)
to extend.

**Cost:** a regex and tests. **Risk:** none — pure log parsing.
**Why it outranks the rest:** it fixes the tool that already exists, already runs,
and is already deployed, so that it fires on the *cause* rather than 49 seconds
into the *effect*. Nothing else here has that ratio.

Whilst in the same code path, extract the `(N live)` connection count that every
`Request:`/`Completed:` line already carries — it produced a clean 5→13→3
saturation curve across this event and costs nothing to collect.

---

## 1. Alerting — the largest gap, and the cheapest to close

`prometheus.yml.j2` has **no `rule_files:` and no `alerting:` block**; there is no
Alertmanager in `compose.yml.j2`. Nothing in this homelab ever tells anyone that a
blip happened. Detection today is "a human noticed playback paused" — which is why
every investigation so far has started hours late, in the T+1h-or-worse column of
the decay table.

This is the gap that most directly frustrates the manual-triage goal: **a runbook
that can only be started late is a runbook that can only ever reach Class A or H1.**

Minimum viable rules (recording the *distinction* from the inventory §2.1):

```yaml
groups:
  - name: plex-blip
    rules:
      - alert: PlexUnreachable
        expr: plex_up == 0
        for: 1m
        labels: {severity: critical}
        annotations:
          summary: "Plex reported unreachable by the exporter"
      - alert: PlexExporterScrapeFailing
        expr: up{job="plex-exporter"} == 0
        for: 2m
        labels: {severity: warning}
        annotations:
          summary: "plex-exporter scrape failing — NOT necessarily a Plex outage"
      - alert: PlexProbeFailing            # requires blackbox (§2)
        expr: probe_success{job="blackbox-plex"} == 0
        for: 30s
        labels: {severity: critical}
      - alert: PlexStreamsCollapsed
        expr: >
          (sum(plex_sessions_count{state="playing"}) == 0)
          and (sum(plex_sessions_count{state="playing"} offset 5m) > 0)
        for: 1m
        labels: {severity: warning}
      - alert: PlexSlowQueryStorm          # requires §7 textfile collector
        expr: increase(plex_watchdog_events_total{event_type="TX_STALL"}[5m]) > 3
```

**Notification path is the actual decision.** Alertmanager → where? Options: an
existing uptime-kuma push endpoint, ntfy, a webhook, email. `[[ralph-robot-telegram-unwired]]`
records that the Telegram path in this repo is not wired up, so that is not a
shortcut. This needs an explicit choice from the operator — it is the one item here
that cannot be decided from the code.

**Cost:** one `rules/` template, one Alertmanager service, one receiver.
**Risk:** none to Plex — Prometheus already holds the data; this only evaluates it.

---

## 2. blackbox-exporter — the single highest-value new signal

**What it closes:** an *independent*, cheap, high-frequency reachability
measurement, decoupled from `plex-exporter`'s expensive sweep. It settles H1 (was
the exporter at fault?), H2 (was kuma right?), gives class E its per-path evidence,
and catches short blips that the 60s `plex_up` sampling misses entirely.

> **CORRECTED 2026-08-07.** The reasoning below is right about *cost* and wrong
> about *sensitivity*. On the 2026-08-07 blip, `/identity` returned HTTP 200 on
> every probe with a worst case of 1,761 ms, while `/status/sessions` reached
> 101,394 ms — so a `probe_success` alert on `/identity` alone would have stayed
> **green through the entire five-minute outage**. The property that makes it cheap
> (it never touches the database) is the same property that makes it insensitive to
> the failure mode we actually have.
>
> **Revised design:** (a) probe `/identity` at 15 s but alert on
> **`probe_duration_seconds`**, not just `probe_success` — the 2 ms → 1,761 ms shift
> is an ~900× signal; (b) add a second probe against **`/status/sessions`** at 60 s
> with a generous timeout — this is the one that actually goes red; (c) treat the
> **ratio** as a discriminator: `/identity` fast + `/status/sessions` slow ⇒ DB/lock;
> both slow ⇒ thread-pool or host saturation; both unreachable ⇒ process or network.
> Full measurements in [live-blip-2026-08-07-case-study.md](live-blip-2026-08-07-case-study.md) §6.

**Why it's safe:** `/identity` is **unauthenticated** and returns only the server
version and `machineIdentifier` — no database access, no library work
([Plexopedia][plexopedia]; it's the endpoint Plex's own container healthcheck uses,
[pms-docker/healthcheck.sh][pms-hc]). Polling it at 15s costs Plex essentially
nothing, which is exactly the opposite of the `library/sections/all` sweep.

**Probe several vantages, because class E has several paths:**

| Target | Path exercised |
|---|---|
| `http://192.168.1.110:32400/identity` | direct to Plex, bypassing everything |
| `https://plex.{{ domain }}/identity` | full Traefik + TLS path |
| `http://192.168.1.111/identity` (Host header) | Traefik plain-HTTP twin |

The differential is the diagnosis: direct up + proxied down ⇒ Traefik/TLS. Both
down ⇒ Plex or CT 110. This is a discriminator that **currently does not exist at
all**, and it produces a verdict in one glance at one panel.

**Metrics gained:** `probe_success`, `probe_duration_seconds`,
`probe_http_status_code`, `probe_http_duration_seconds` broken out by phase
(resolve / connect / tls / processing / transfer), `probe_ssl_earliest_cert_expiry`.
The phase breakdown is itself a class-E discriminator: a stall in `connect` is a
network fault, a stall in `processing` is a server fault.

**Config shape** — the multi-target relabel pattern, same as the existing
`pve-exporter` job ([blackbox_exporter README][bb]):

```yaml
  - job_name: blackbox-plex
    scrape_interval: 15s
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - http://192.168.1.110:32400/identity
          - https://plex.{{ domain }}/identity
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

Blackbox derives its own probe timeout from Prometheus' `scrape_timeout`, so a 15s
interval with the default 10s timeout is coherent without extra tuning.

**Caveat carried from prior work:** `[[plex-lan-vantage-from-dev-box-is-not-a-lan-client]]`
— a probe from the Docker host is *not* a real LAN client measurement; `.111 → .110`
is a virtual-bridge hop. These probes are excellent for **reachability** and
**path differentiation**; they are not a substitute for real client-side latency
data, and the design should not claim otherwise.

---

## 3. Traefik `accessLog` — the trivially-closed gap

Currently absent entirely (`traefik.yml.j2:106` is `log: level: INFO` and nothing
more). Adding it turns "Traefik logs show nothing" into actual per-request forensics
([Traefik reference][traefik-al]):

```yaml
accessLog:
  filePath: /var/log/traefik/access.log
  format: json
  bufferingSize: 100
  fields:
    defaultMode: keep
    headers:
      defaultMode: drop
      names:
        User-Agent: keep
        X-Forwarded-For: keep
```

The fields that matter for a blip: `Duration` (total, ns), **`OriginDuration`**
(time Plex itself took) and **`Overhead`** (Traefik's own) — that pair separates
"Plex was slow" from "the proxy was slow", which the aggregated histogram cannot do
— plus `DownstreamStatus`, `OriginStatus`, `RetryAttempts`, `ClientAddr`,
`RequestPath`, `ServiceName`.

**Consider `filters.minDuration`** (e.g. `1s`) to log only slow requests. Plex is
chatty — full access logging is a meaningful volume on the Docker host — and for
blip triage the slow tail is the entire object of interest. A `minDuration` filter
gets ~100% of the diagnostic value at ~1% of the volume.

**Cost:** ~10 lines in the template plus a volume mount and rotation.
**Risk:** disk growth on `.111`; zero risk to Plex.
**Hard limitation to state plainly:** this only ever sees proxied traffic. Streams
that connect directly to `:32400` — likely most LAN playback — remain invisible.
That is what §2's direct probe is for.

---

## 4. Prometheus retention → 90d

One flag: `--storage.tsdb.retention.time=90d` (currently unset ⇒ 15d default).
Directly enables the cross-event periodicity analysis that a *sporadic* fault
requires. Cost is disk on `.111`; at this scrape volume, small.

---

## 5. Grafana panels for the discriminators we already have

Zero new collection; pure presentation. Add to `grafana-plex-health-dashboard.json`:

- `up{job="plex-exporter"}` **beside** `plex_up`, explicitly labelled so the
  ambiguity in inventory §2.1 is visible rather than latent.
- `up{job=~"traefik|pve-exporter|node-exporter"}` — a scrape-health row.
- `changes(plex_info[1h])` or a `plex_info` version/uptime stat — the closest
  available proxy for "did Plex restart" (class B).
- Re-window the Traefik rate panels from `[5m]` to `[1m]` — a 34s stall inside a 5m
  window is diluted ~10×. Keep a `[5m]` variant for trend if desired.
- A "Blip triage" dashboard row, or a separate dashboard, laying the discriminators
  out in tree order so the runbook can say "open this, read top to bottom."

This is the cheapest real improvement to *manual* triage specifically, and it needs
no new services at all.

---

## 6. node-exporter inside CT 110

Closes the class-C hole: load average, `D`-state process count, per-CPU time,
memory pressure/PSI, disk I/O latency, fd and thread counts — **as a time series
with a baseline**, rather than the watchdog's single instant at trigger time.

The classic starvation signature (load average climbing while CPU% stays flat) is
currently unobservable, and 2026-08-04's "mild ~30% CPU spike" is exactly the kind
of reading that a load-average series would disambiguate.

**Cost:** an Ansible task in `ansible/roles/plex/`, a systemd unit, one scrape job.
**Risk:** low — node-exporter is a small static binary reading `/proc`. Set
`Nice`/`CPUSchedulingPolicy=idle` as the watchdog unit already does. Note some
collectors are noisy or meaningless inside an unprivileged LXC; disable those
rather than fighting them.
**Bonus:** it brings a **textfile collector**, which is the delivery mechanism for §7.

---

## 7. Watchdog JSONL → Prometheus

Today the watchdog's findings are stranded on CT 110's disk (inventory §5) and can
only be joined to metrics by a human comparing timestamps. Once §6 puts a
node-exporter in CT 110, the watchdog can additionally write a `.prom` textfile:

```
plex_watchdog_events_total{event_type="TX_STALL"} 17
plex_watchdog_events_total{event_type="SLOW_QUERY"} 243
plex_watchdog_events_total{event_type="STREAM_DROP"} 4
plex_watchdog_events_total{event_type="CONNECTIVITY_DROP"} 2
plex_watchdog_last_event_timestamp_seconds{event_type="TX_STALL"} 1.7e9
plex_watchdog_max_delay_ms{event_type="SLOW_QUERY"} 35905
```

That turns the watchdog into an alertable, graphable, correlatable signal — the
JSONL stays as the detailed forensic record, the counters become the index into it.
This is what makes "was there a stall at T?" a Grafana question instead of an SSH
question, and it collapses several manual triage steps to a glance.

**Also add here:** a logrotate policy for `/var/log/plex_blip_watchdog/` with long
retention (see decay note in [triage-window-and-data-survival.md](triage-window-and-data-survival.md)).

**Cost:** a writer function in `plex_blip_watchdog.py` plus tests; the script
already has a test suite (`scripts/test_plex_blip_watchdog.py`).
**Risk:** none — atomic write-and-rename to a textfile directory.

---

## 8. PVE-host storage telemetry

Class D is completely blind. `pve-exporter` gives guest disk *usage*, not I/O
latency or errors; `node-exporter` on `.111` does not see the media mounts at all.

Options, cheapest first:
1. **node-exporter on the PVE host** — brings `node_disk_io_time_seconds_total`,
   `node_disk_read_time_seconds_total`, and the `textfile` collector. Covers USB/SCSI
   I/O latency and gives somewhere to land ZFS state.
2. **A ZFS textfile script** — `zpool status`/`zpool events` scraped into
   `zfs_pool_state`, `zfs_pool_errors_total` via the textfile collector.
3. **Persistent kernel logs** — enable persistent journald (`Storage=persistent`)
   on the PVE host so `journalctl -k` survives reboots. Cheapest possible fix for
   the `dmesg`-ring-buffer decay hazard, and it also closes part of class B (OOM).

Note the constraint from prior work (`.agents/planning/2026-08-04-debug-plex-blip/research/proxmox-isolation-and-native-telemetry.md`):
**avoid bare-metal hypervisor modification.** Item 3 is a config toggle and clearly
in bounds; item 1 installs a package on the PVE host and needs an explicit operator
decision. That tension should be surfaced in the design, not silently resolved.

---

## 9. Tautulli — session history, with a real caveat

**Closes:** class G (client-side) and H3 (was it just a normal idle timeout?). Gives
per-session start/stop, termination reason, buffering events, and client identity —
i.e. the entire viewer's-side-of-the-connection blind spot. A Prometheus exporter
exists ([mm503/tautulli-exporter][taut-exp]) and community Grafana dashboards are
built on exactly this pattern ([GrafanaPlexMonitor][gpm]).

**The caveat that keeps it out of the "do first" tier:** Tautulli works by polling
the Plex API continuously and mirroring activity into its own SQLite database. That
is *the same category of load* that caused the 2026-08-04 incident. It is a much
lighter query than the full `library/sections/all` sweep, and Tautulli is very
widely deployed without incident — but on a server with demonstrated SQLite
contention, adding a second continuous API poller deserves explicit thought rather
than a default yes.

**If adopted:** stage it *after* the alerting and probes are in place, so that if it
does perturb anything, the perturbation is immediately visible. Its own DB must live
off the Plex container's storage.

---

## 10. Loki + Promtail — defer

**Closes:** nothing new. It makes everything already collected *reachable* — logs
from CT 110, the Docker host, and the PVE host queryable in Grafana beside the
metrics, on the same time axis, without SSH.

The convenience is genuine and it would collapse most of the manual runbook's Tier-1
steps into dashboard queries. But it is the largest single piece of new
infrastructure here, and it does not decide any class that isn't already decidable.
**Correct ordering: make the signals exist and alert on them first; make them
convenient second.** If the runbook proves painful in practice after items 1–8,
that is the evidence that justifies Loki.

---

## 11. GPU / QSV telemetry — defer

Class F stays blind. `intel_gpu_top`-derived metrics inside an unprivileged LXC with
ID-mapped `/dev/dri` is genuinely awkward, and the payoff is one failure class that
has not yet been observed. `scripts/verify_plex_ihd_cvt.py` already provides an
after-the-fact "is transcoding working" check, which is enough for now. Revisit if a
blip is ever traced to a dead transcode with a healthy API.

---

## What "do first" adds up to

Items 1–5 are: one alerting stack, one small exporter, ten lines of Traefik config,
one Prometheus flag, and some dashboard JSON. Together they:

- make blips **detected** rather than noticed (1)
- make blips **timestamped to 15s** rather than 60s (2)
- **separate Plex-down from exporter-down from proxy-down** (2, 5)
- give **per-request edge forensics** for proxied traffic (3)
- extend the **pattern-finding horizon 6×** (4)

None of them touch Plex's database, and none add meaningful load to CT 110. That
combination — high diagnostic yield, near-zero observer effect — is what earns them
the front of the queue, given that observer effect is the exact thing that burned
this homelab before.

---

## References

- [prometheus/blackbox_exporter][bb] — multi-target relabel pattern, probe metrics,
  timeout derivation from `scrape_timeout`.
- [Traefik — Logs and Access Logs reference][traefik-al] — `accessLog` options,
  `filters.minDuration`, field names incl. `OriginDuration` / `Overhead`.
- [Plexopedia — Plex API: Server Identity][plexopedia] and
  [plexinc/pms-docker healthcheck.sh][pms-hc] — `/identity` is unauthenticated and
  is Plex's own healthcheck surface.
- [axsuul/plex-media-server-exporter][axsuul] — `plex_up` semantics and the
  `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS` throttle.
- [mm503/tautulli-exporter][taut-exp], [bdgarmon/GrafanaPlexMonitor][gpm] — session
  history as Prometheus series.
- [Prometheus storage documentation](https://prometheus.io/docs/prometheus/latest/storage/) — retention flags.
- Repo prior art: `.agents/planning/2026-08-04-debug-plex-blip/research/{containerized-diagnostic-sidecars,proxmox-isolation-and-native-telemetry,low-overhead-diagnostics}.md`

[bb]: https://github.com/prometheus/blackbox_exporter
[traefik-al]: https://doc.traefik.io/traefik/reference/install-configuration/observability/logs-and-accesslogs/
[plexopedia]: https://www.plexopedia.com/plex-media-server/api/server/identity/
[pms-hc]: https://github.com/plexinc/pms-docker/blob/master/root/healthcheck.sh
[axsuul]: https://github.com/axsuul/plex-media-server-exporter
[taut-exp]: https://github.com/mm503/tautulli-exporter
[gpm]: https://github.com/bdgarmon/GrafanaPlexMonitor
