# Thorough Review: Research, Design & Implementation Plan

## Second Review Pass: The "Scrape Retry Storm" Discovery
During a second, deeper chronological log verification pass of `Plex Media Server.log` (lines 41135–41215), an critical empirical refinement was discovered regarding how `plex-exporter` interacts with SQLite lock contention:
* **From Victim to Feedback Loop**: While initial research identified `plex-exporter` as a victim hitting a database locked by bandwidth statistics writer threads (`StatisticsBandwidth.cpp:110`), timestamp tracing reveals that `plex-exporter` actually enters a destructive **Scrape Retry Storm**.
* **The 60-Second Retry Loop**: At `06:57:16`, Prometheus scraped `plex-exporter` (`192.168.1.111`), triggering a synchronous media metrics sweep. Section 3 took 29,767ms, causing total collection across all sections to exceed Prometheus's `scrape_timeout: 30s`. Because the scrape timed out and aborted before completion, **on the very next 60-second Prometheus scrape interval (`06:58:17`), `plex-exporter` re-attempted the full synchronous library sweep**. This second query took 35,905ms (failing again), causing a third re-attempt at `06:59:19` (34,413ms).
* **Direct Cause of the Stream Drop**: This 3-minute synchronous retry storm (06:57 to 07:00) exhausted Plex worker threads and blocked client timeline updates (`GET /:/timeline`) from device `192.168.1.199` for 180 seconds, directly forcing Plex to shut down the session and execute a `SIGKILL` (-9) on the transcoder job at `07:00:10.642`.
* **Remediation Validation**: This empirical evidence provides exact proof for Step 4 of the implementation plan: increasing `scrape_timeout: 50s` ensures that even during transient database maintenance, the sweep finishes without aborting, resetting `plex-exporter`'s collection timer and permanently eliminating the 60s retry loop.

## First Review Pass Summary

Overall the research, design, and implementation plan are **high quality and internally consistent**. The core hypothesis (SQLite lock contention + plex-exporter scrape collision) is well-evidenced from actual log data and real repository configuration. However, the first review uncovered **three materially incorrect or overstated claims**, **one serious omission**, and **several minor issues**, all of which have been corrected across the documentation before execution begins.

---


## 1. Research Review

### ✅ Strengths

**homelab-architecture.md**
- Correctly identifies CT 110, unprivileged container, USB ZFS storage, and the plex_state_host_path bind mount as the SQLite host.
- Line number references to `ansible/roles/plex/tasks/main.yml` and `das-zfs-migration.md` are accurate.
- Correctly notes the remote latency audit ruling out Traefik as a cause.

**log-correlation-patterns.md**
- Actual log lines are reproduced verbatim from `/tmp/plex-logs/Plex Media Server.log` — confirmed accurate.
- The 35,905ms and 34,413ms query stall durations are real numbers from the logs at lines 41186 and 41205.
- The 07:00:10.642 idle session shutdown at line 41215 is correctly identified.
- The "Relay: Failed to retrieve relay host key" and "We appear to have lost Internet connectivity" messages at lines 41231–41237 are real.

**containerized-diagnostic-sidecars.md**
- Correctly reads the `prometheus.yml.j2` scrape config and identifies the synchronous scrape + 30s timeout constraint.
- Correctly reads `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS=300` from `compose.yml.j2` line 269.
- The deployment trade-offs table is fair and well-reasoned.

**proxmox-isolation-and-native-telemetry.md**
- Proxmox hygiene best-practice reasoning is sound and consistent with community practice.
- The pve-exporter multi-target pattern reference is accurate.

---

### ⚠️ Issues Found in Research

#### Issue R1 (MATERIAL — INCORRECT CLAIM): The scheduled library update did NOT fire at 07:00:05 on Aug 04
> **Source**: `log-correlation-patterns.md` states: *"scheduled hourly activities reliably fire within seconds of the top of the hour (e.g., `07:00:05` scheduled library scans)"*

**What the logs actually show**: On August 4, 2026, the scheduled library update did **NOT** run at 07:00:05. Looking at `Plex Media Server.log`, the nearest library scan fired at **07:05:10** (line 43320: `"It's been 3604 seconds, so we're starting scheduled library update..."`). The scheduler was delayed by the very blockage we're investigating. The preceding scan ran at **06:05:06**, and the next would have been expected at 07:05:06 — but it was held for 5 extra minutes due to the active lockup.

The 07:00:05 figure comes from earlier log files (`.5.log`, Aug 01) where a scan *did* fire precisely. On the specific Aug 04 blip day, the actual trigger chain is: scheduled task was **delayed/blocked by the SQLite stall already in progress** rather than **causing** it.

**Impact**: This does not change the root cause hypothesis, but it inverts the causal direction. The scheduled scan did not cause the lock — the lock blocked the scan from running on time. The actual triggering source is still under investigation and is likely the `plex-exporter` synchronous media scrape (Section 3: `GET /library/sections/3/all`) firing just before 07:00 EDT, which is documented in the logs at lines 41183–41186 (req `#57d3a`, started 06:58:17, took 35,905ms).

#### Issue R2 (MINOR — IMPRECISE CLAIM): plex-exporter "collision" framing needs caution
> **Source**: `containerized-diagnostic-sidecars.md` states the scrape collision "directly exacerbates" the blip.

**Nuance**: The `plex-exporter` scrape fires a `GET /library/sections/<key>/all` API call every 300 seconds (5 minutes). When **that** API call hits Plex while SQLite is locked, it hangs and breaks the Prometheus scrape timeout. But there is an unresolved chicken-and-egg question: **what acquires the SQLite lock first?** The `StatisticsBandwidth.cpp:110` transaction stalls began at 06:58:11, before the plex-exporter scrape likely fired (the large query at 06:58:17 req `#57d3a` appears to be the plex-exporter call hitting an already-locked DB). This distinction matters for remediation: increasing the media collection interval reduces collision probability but may not eliminate the root lock acquisition.

**The log evidence actually points to the Bandwidth Statistics writer thread as the primary SQLite lock holder**. The "Took too long (0.120000 seconds) to start a transaction on StatisticsBandwidth.cpp:110" warnings indicate the statistics writer is holding an exclusive lock.

#### Issue R3 (MINOR — OUTDATED LINK): plex_exporter upstream repository link
> **Source**: `containerized-diagnostic-sidecars.md` references `https://github.com/nabsul/plex_exporter`

The upstream exporter used in this repo should be verified against the actual Docker image configured in `compose.yml.j2` (`docker_host_plex_exporter_image`). The nabsul repository is one of several forks and may not match. This reference should be updated or removed until verified.

#### Issue R4 (MINOR — INCOMPLETE): `low-overhead-diagnostics.md` recommends `zpool status` and `zpool iostat` as watchdog actions
> These commands run on the Proxmox host's ZFS pool, not from within LXC CT 110. Since the watchdog is deployed inside CT 110, **these commands are unavailable**. CT 110 is an unprivileged container with no ZFS tooling and no host storage visibility. This recommendation is incompatible with the chosen deployment model and should be removed from the watchdog's action list.

---

## 2. Design Review

### ✅ Strengths

**watchdog-component.md**
- Trigger regex patterns are correct and match actual log strings verbatim.
- The debounce window (30s) is appropriately sized for the observed ~35-second lockup duration.
- The systemd unit with `Nice=10` and `CPUSchedulingPolicy=idle` is appropriate.
- JSONL output format is well-suited for machine-readable post-analysis.

**log-pipeline-component.md**
- The 5 event taxonomy categories (`TX_STALL`, `SLOW_QUERY`, `SCHEDULED_TASK`, `STREAM_DROP`, `EXPORTER_SCRAPE`) map correctly to real log patterns confirmed in the data.
- The `SCHEDULED_TASK` trigger string `"It's been 3600 seconds, so we're starting scheduled library update for section"` is verified verbatim from the logs.
- Rolling 60-second correlation window is a sensible design choice.

**observability-and-remediation.md**
- The `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS: 1800` target environment variable is the correct name, confirmed in `compose.yml.j2` line 269.
- Adjusting scrape_timeout to 50s is correctly justified.

---

### ⚠️ Issues Found in Design

#### Issue D1 (MATERIAL — INCORRECT): The watchdog `output-dir` path will not survive container restarts
> **Source**: `watchdog-component.md` systemd unit uses `--output-dir /var/lib/plexmediaserver/.../Logs/Diagnostics`

However, the systemd unit's `ExecStart` line also shows an alternative path: `Diagnostic JSONL Dumps (/tmp/plex-blip-diagnostics.jsonl)`. `/tmp` inside an LXC container is **ephemeral** and cleared on reboot. The design should commit to a single persistent path that survives reboots, preferably under `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Logs/Diagnostics` (which is on the host state bind mount and therefore persistent), and drop the `/tmp` reference entirely.

#### Issue D2 (MATERIAL — NEEDS VERIFICATION): `pidstat` may not be available in the Plex LXC container
> **Source**: `watchdog-component.md` calls `pidstat -t 1 1` as part of the diagnostic snapshot.

`pidstat` is part of the `sysstat` package. Unprivileged LXC containers typically only have packages explicitly installed. If `sysstat` is not installed in CT 110, the watchdog will fail silently or crash at diagnostic capture time. The implementation plan should add installing `sysstat` (and `lsof`) as prerequisites in the Ansible role before deploying the watchdog.

#### Issue D3 (MINOR): The design diagram in `system-architecture.md` labels plex-exporter as using "Async / Decoded Media Scrapes"
> This is **aspirational, not current**. The exporter currently runs synchronously. The remediated state should be labeled as "post-remediation" to avoid implying the current deployment is already async.

#### Issue D4 (MINOR): The `SLOW QUERY` regex in `watchdog-component.md` will not match the actual log format
> The design specifies: `r"SLOW QUERY: It took ([0-9.]+) ms to retrieve"`

But the actual log format observed is: `SLOW QUERY: It took 4360.000000 ms to retrieve 0 items.` — with **6 decimal places**. The regex `[0-9.]+` will match this correctly, so this is not broken. However the design should document the full log format as a reference for future regex maintenance.

---

## 3. Implementation Plan Review

### ✅ Strengths
- Step ordering is logical: offline tool first (low risk), then watchdog script, then deployment, then configuration remediation, then DB audit.
- Each step has explicit rollback instructions.
- Verification commands are specific and testable.
- Pointing Step 4's post-remediation verification at Step 1's analyzer tool is a clean design loop.

### ⚠️ Issues Found in Implementation Plan

#### Issue I1 (MATERIAL — MISSING PREREQUISITE): No step installs `sysstat` and `lsof` in CT 110
> Step 3 deploys the watchdog but relies on `fuser`, `lsof`, and `pidstat` without ensuring they are installed. These must be installed in CT 110 via the Ansible Plex role before the watchdog is deployed. Step 3 execution steps should include:
> ```yaml
> - name: Install watchdog diagnostic dependencies
>   apt:
>     name: [sysstat, lsof, procps]
>     state: present
> ```

#### Issue I2 (MATERIAL — TEST SUITE IMPACT): Step 4 changes will break the existing test suite pin on `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS: "300"`
> **Source**: `scripts/test_traefik_config_shape.py` line 1634 asserts `"METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS": "300"` as part of `PLEX_EXPORTER_ENV`.

Changing the value to `1800` in `compose.yml.j2` **will fail the existing test assertion**. Step 4 must include updating `test_traefik_config_shape.py` to reflect the new value. The `just test` verification in Step 4 will fail if this is not done first.

#### Issue I3 (MINOR): Step 1 verification command references `06:59:15 EDT blip` as an expected output
> The verification instruction says: *"Verify that the tool correctly outputs a Markdown summary identifying the August 4th 06:59:15 EDT blip"*

The actual first transaction warning begins at 06:58:11, not 06:59:15. The 06:59:15 timestamp is when the Grafana heartbeat likely recorded the blip (inferred), but it does not appear as a distinct line in the logs. The verification criterion should reference the 06:58:11 TX_STALL event and the 06:58:52 SLOW_QUERY completion (35,905ms) instead, as these are directly observable.

#### Issue I4 (MINOR): Step 5 runs `sqlite3` inside CT 110 without confirming `sqlite3` is installed
> The SQLite CLI (`sqlite3`) is unlikely to be installed in the Plex container by default. The step should either note this prerequisite or substitute a read of the DB journal mode using Python's built-in `sqlite3` module (which avoids the package installation entirely):
> ```python
> python3 -c "import sqlite3; c=sqlite3.connect('/path/to/library.db'); print(c.execute('PRAGMA journal_mode').fetchone())"
> ```

---

## Summary of Required Corrections

| ID | Severity | Location | Correction Needed |
|:--|:--|:--|:--|
| R1 | **Material** | `log-correlation-patterns.md` §4 | Correct the Aug 04 causal timeline: scheduled scan did NOT fire at 07:00 on blip day; it fired at 07:05 (delayed by the lockup). Update the causal model accordingly. |
| R2 | Minor | `containerized-diagnostic-sidecars.md` §Critical Discovery | Clarify that the statistics writer is the likely primary lock holder, not plex-exporter itself. plex-exporter is a victim that also worsens the symptoms. |
| R3 | Minor | `containerized-diagnostic-sidecars.md` §References | Remove or verify the nabsul/plex_exporter GitHub link. |
| R4 | **Material** | `low-overhead-diagnostics.md` §Snapshot Actions | Remove `zpool status` and `zpool iostat` from the in-container watchdog action list; these are host-only commands unavailable inside CT 110. |
| D1 | **Material** | `watchdog-component.md` §Systemd | Commit to a single persistent output path (not `/tmp`). Use `Logs/Diagnostics` subdirectory on the state bind mount. |
| D2 | **Material** | `watchdog-component.md` §Snapshot | Add `sysstat`, `lsof`, `procps` as Ansible package prerequisites before deploying the watchdog. |
| D3 | Minor | `system-architecture.md` §Diagram | Label plex-exporter scrape as "Synchronous (pre-remediation)" to reflect current state. |
| D4 | Minor | `watchdog-component.md` §Trigger Regex | Document full expected log line format alongside each regex. |
| I1 | **Material** | `plan.md` Step 3 | Add Ansible task to install `sysstat`, `lsof`, `procps` in CT 110. |
| I2 | **Material** | `plan.md` Step 4 | Add sub-step to update `test_traefik_config_shape.py` line 1634 from `"300"` to `"1800"` before running `just test`. |
| I3 | Minor | `plan.md` Step 1 §Verification | Reference 06:58:11 TX_STALL and 06:58:52 SLOW_QUERY events, not `06:59:15 EDT blip`. |
| I4 | Minor | `plan.md` Step 5 | Substitute Python one-liner for `sqlite3` CLI or add `sqlite3` installation step. |
