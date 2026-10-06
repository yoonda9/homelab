# Implementation Plan: Debugging & Remediating Sporadic Plex Heartbeat Blips

## Executive Overview
This structured implementation plan translates the detailed modular design into five sequential, incremental engineering steps. Each step is independently deployable, strictly non-destructive to real-time hardware transcoding (Intel QSV), and adheres to Proxmox VE hypervisor isolation best practices by restricting all execution to unprivileged containers (`CT 110` and `Docker Host`) or local developer tooling.

---

## Step 1: Develop Offline Reproducible Log Analysis Tool (`analyze_plex_blips.py`)
* **Objective**: Create an offline log parsing and correlation script in the repository (`scripts/analyze_plex_blips.py`) to quantify slow queries (`SLOW QUERY`), SQLite transaction delays (`Took too long ... to start a transaction`), and stream disconnects across historical and live log bundles.
* **Pre-conditions**:
  * Historical log bundles must be accessible (e.g., preserved in `/tmp/plex-logs/` or target log mounts).
  * Python 3 standard library environment available on the developer workstation or test runner.
* **Execution Steps**:
  1. Create `scripts/analyze_plex_blips.py` with multi-threading timestamp parser and rolling 60-second correlation window engine.
  2. Implement command-line arguments: `--log-dir`, `--start-time`, `--end-time`, `--threshold-ms`, and `--output-format` (`markdown`, `jsonl`, `both`).
  3. Add automated classification taxonomy for `TX_STALL`, `SLOW_QUERY`, `SCHEDULED_TASK`, `STREAM_DROP`, and `EXPORTER_SCRAPE`.
* **Verification Instructions**:
  * Run a non-destructive smoke verification against the existing historical log bundle:
    ```bash
    python3 scripts/analyze_plex_blips.py --log-dir /tmp/plex-logs --output-format markdown --threshold-ms 500
    ```
  * Verify that the tool correctly outputs a Markdown summary identifying:
    1. The `TX_STALL` event at `06:58:11` (transaction start delay on `StatisticsBandwidth.cpp:110`)
    2. The `SLOW_QUERY` event completing at `06:58:52` with a `35905ms` total duration on `GET /library/sections/3/all`
    3. The `STREAM_DROP` at `07:00:10` (idle session killed after 180s)
  * Confirm the tool correctly links these events within a 120-second backward correlation window.
* **Rollback Instructions**:
  * Delete `scripts/analyze_plex_blips.py` if validation fails; zero operational state is touched.

---

## Step 2: Implement Zero-Overhead Watchdog Script (`plex_blip_watchdog.py`)
* **Objective**: Create the event-driven Python monitoring utility designed for container-local deployment inside LXC `CT 110`.
* **Pre-conditions**:
  * Step 1 analysis engine syntax and regex triggers verified.
* **Execution Steps**:
  1. Create `ansible/roles/plex/files/plex_blip_watchdog.py` utilizing standard non-blocking asynchronous log tailing (`inotify`/event-driven stream reads without active CPU polling loops).
  2. Implement target trigger matching for database lock stalls, slow library queries > 500ms, and network relay connectivity drops, enforced by a 30-second debounce cooldown window.
  3. Implement instantaneous (< 500ms) diagnostic command snapshotting: executing `fuser -v` and `lsof` against `/var/lib/plexmediaserver/.../com.plexapp.plugins.library.db*`, running `pidstat -tl`, and serializing the output as structured JSON Lines into `--output-dir`.
* **Verification Instructions**:
  * Execute a standalone unit verification using a temporary mock log file and simulated SQLite file lock on a local scratch database:
    ```bash
    python3 ansible/roles/plex/files/plex_blip_watchdog.py --log-path /tmp/test_plex.log --output-dir /tmp/watchdog_out --dry-run
    ```
  * Verify that the script rests in zero-CPU kernel sleep when idle, and immediately outputs a valid JSONL diagnostic record upon appending a mock warning string to `/tmp/test_plex.log`.
* **Rollback Instructions**:
  * Revert or remove `ansible/roles/plex/files/plex_blip_watchdog.py`; no live systems are modified during standalone testing.

---

## Step 3: Ansible Role & Systemd Watchdog Service Integration in LXC CT 110
* **Objective**: Deploy the verified watchdog script inside unprivileged LXC container `CT 110` and establish a resilient, low-priority systemd daemon without touching the bare-metal Proxmox host (`pve`).
* **Pre-conditions**:
  * Step 2 watchdog script completed and verified.
  * SSH access or local Ansible execution capability against the container target.
* **Execution Steps**:
  1. Add a package installation task to `ansible/roles/plex/tasks/main.yml` to install watchdog diagnostic tool dependencies **before** deploying the watchdog script:
     ```yaml
     - name: Install plex-blip-watchdog diagnostic dependencies
       apt:
         name: [sysstat, lsof, procps]
         state: present
     ```
  2. Create the systemd service unit template at `ansible/roles/plex/templates/plex-blip-watchdog.service.j2` configured with `Nice=10`, `CPUSchedulingPolicy=idle`, and automatic restart semantics.
  3. Update `ansible/roles/plex/tasks/main.yml` to copy `plex_blip_watchdog.py` to `/usr/local/bin/`, deploy the systemd service template to `/etc/systemd/system/`, and enable/start `plex-blip-watchdog.service` within `CT 110`.
* **Verification Instructions**:
  * Run repository configuration test suite and dry-run Ansible playbook syntax verification:
    ```bash
    just test
    ansible-playbook --syntax-check playbooks/plex.yml
    ```
  * Post-deployment (if applied live), verify unprivileged service status and zero impact on container CPU utilizing standard read-only commands:
    ```bash
    systemctl status plex-blip-watchdog.service
    ps -eo pid,ni,comm | grep plex_blip_wat
    ```
* **Rollback Instructions**:
  * Disable and remove `plex-blip-watchdog.service` within `CT 110`, revert edits to `ansible/roles/plex/tasks/main.yml`, and re-apply the Ansible role to restore pristine container configuration.

---

## Step 4: Remediate Exporter Scrape Collision & Balance Prometheus Timeout
* **Objective**: Permanently eliminate the primary root cause of the 34-second database query hangs by decoupling synchronous `plex-exporter` media collection from Plex's scheduled 07:00 EDT hourly library maintenance.
* **Pre-conditions**:
  * Step 3 monitoring service is ready or operational.
  * Access to modify Docker host Ansible configuration templates.
* **Execution Steps**:
  1. In `ansible/roles/docker_host/templates/compose.yml.j2` under the `plex-exporter` environment definition, explicitly set `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS: 1800` (increasing the interval from 5 minutes to 30 minutes to reduce lock contention frequency).
  2. Update the corresponding test suite assertion in `scripts/test_traefik_config_shape.py` to match the new value — **this must be done before running `just test` or the assertion will fail**:
     ```python
     # Line ~1634 in test_traefik_config_shape.py — update from:
     "METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS": "300",
     # to:
     "METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS": "1800",
     ```
  3. In `ansible/roles/docker_host/templates/prometheus.yml.j2` under the `plex-exporter` scrape job, update `scrape_interval: 60s` and `scrape_timeout: 50s` (preventing transient DB waits from throwing false DOWN statuses in Grafana).

* **Verification Instructions**:
  * Verify Ansible configuration shape and run unit test suite:
    ```bash
    just test
    ```
  * After applying to the Docker host, verify via Prometheus targets UI or API (`GET http://localhost:9090/api/v1/targets`) that `plex-exporter` consistently reads `UP`.
  * Execute Step 1's offline analyzer against newly generated production logs over a subsequent 07:00 EDT boundary to verify that `TX_STALL` and `SLOW_QUERY` durations remain below the critical 30-second timeout threshold.
* **Rollback Instructions**:
  * Revert `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS` back to `300` in `compose.yml.j2`, and restore `scrape_timeout: 30s` in `prometheus.yml.j2`, then re-apply via Ansible.

---

## Step 5: SQLite Database WAL Mode Concurrency Audit & Maintenance Playbook
* **Objective**: Confirm that Plex's SQLite library database (`com.plexapp.plugins.library.db`) is utilizing Write-Ahead Logging (`WAL`) mode for optimal read/write concurrency, and establish an automated off-peak maintenance check.
* **Pre-conditions**:
  * Container access to LXC `CT 110` database directory.
* **Execution Steps**:
  1. Add a safe, read-only audit check in `ansible/roles/plex/tasks/main.yml` (or create an operational diagnostic runbook in `docs/runbooks/`) that executes an inline SQLite pragma inspection: `sqlite3 "/var/lib/plexmediaserver/.../com.plexapp.plugins.library.db" "PRAGMA journal_mode;"` (verifying output is `wal`).
  2. If journal mode is not WAL or database fragmentation is high, document a safe, scheduled off-peak maintenance systemd timer (e.g., executing at 03:30 AM) to perform database defragmentation (`VACUUM; REINDEX;`) without colliding with 07:00 EDT morning streams.
* **Verification Instructions**:
  * Run read-only SQLite journal mode check inside the container using Python's built-in `sqlite3` module (no package installation required):
    ```bash
    python3 -c "
    import sqlite3
    db = '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'
    con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    mode = con.execute('PRAGMA journal_mode').fetchone()[0]
    print(f'journal_mode: {mode}')
    assert mode == 'wal', f'Expected WAL, got {mode}'
    "
    ```
  * Ensure the query completes cleanly returning `journal_mode: wal` without locking active streaming connections.
* **Rollback Instructions**:
  * Revert newly added tasks or timers in `ansible/roles/plex/tasks/main.yml`; database read-only inspection alters zero on-disk bits.
