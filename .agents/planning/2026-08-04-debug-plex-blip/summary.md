# Summary: Debugging & Tracking Sporadic Plex Heartbeat Blips (Project Summary)

## Project Overview
This document summarizes the comprehensive engineering design and research completed for tracking, debugging, and definitively remediating sporadic Plex Media Server heartbeat blips occurring around 07:00 EDT. Guided by rigorous log correlation and Proxmox hypervisor isolation best practices, the architecture establishes a zero-overhead diagnostic tracking suite and targeted monitoring remediations.

## Core Deliverables & Architecture Summary
1. **Automated Zero-Overhead Diagnostic Watchdog (`plex_blip_watchdog.py`)**:
   * Deployed strictly inside the unprivileged Plex LXC container (`CT 110`) via an Ansible-managed systemd service ([ansible/roles/plex/tasks/main.yml](file:///home/user/Work/homelab/ansible/roles/plex/tasks/main.yml)).
   * Uses non-blocking asynchronous file tailing (`inotify`) without CPU polling loops to monitor `Plex Media Server.log` for database transaction stalls (`Took too long to start a transaction`) and query delays (`SLOW QUERY`).
   * Upon trigger, executes an instant (< 500ms) diagnostic snapshot of SQLite file lock holders (`fuser`/`lsof` on `library.db`), process thread states (`pidstat -t`), and memory allocations, outputting structured JSONL audit dumps.
2. **Offline Reproducible Log Analysis Pipeline (`analyze_plex_blips.py`)**:
   * A flexible command-line analysis utility designed to parse raw and rotated log bundles (`/tmp/plex-logs/` or production log directories).
   * Quantifies slow query durations, correlates database lock timestamps with top-of-hour scheduled scans and streaming disconnects within rolling 60-second time windows, and outputs GitHub-flavored Markdown reports and JSONL timelines.
3. **Root-Cause Remediation & Enhanced Observability**:
   * **Crucial Research Finding**: Synchronous library scraping from `plex-exporter` every 5 minutes (`GET /library/sections/<key>/all`) collides directly with Plex's 07:00 EDT hourly library maintenance and bandwidth statistic flushes, locking SQLite for ~34.4 seconds and breaking Prometheus' 30-second scrape timeout!
   * **Remediation Plan**: Adjust `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS` to 1800s in Docker Compose, extend Prometheus `scrape_timeout` to 50s in [prometheus.yml.j2](file:///home/user/Work/homelab/ansible/roles/docker_host/templates/prometheus.yml.j2), and verify SQLite Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) concurrency optimization.

## Document Sitemap & References
### Research Phase
* **[homelab-architecture.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/research/homelab-architecture.md)**: Architectural mapping of Proxmox VE, LXC CT 110, unprivileged ID-mapped `/dev/dri` GPU passthrough, and ZFS USB media bind mounts.
* **[log-correlation-patterns.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/research/log-correlation-patterns.md)**: Empirical log correlation proving that SQLite lock contention around 07:00 EDT stalls read queries for over 30 seconds, causing heartbeat failures and stream drops.
* **[low-overhead-diagnostics.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/research/low-overhead-diagnostics.md)**: Comparative analysis of monitoring patterns, establishing passive event-driven file tailing as the optimal zero-overhead diagnostic trigger.
* **[proxmox-isolation-and-native-telemetry.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/research/proxmox-isolation-and-native-telemetry.md)**: Justification for avoiding bare-metal hypervisor modifications and utilizing containerized API scrapers (`pve-exporter`).
* **[containerized-diagnostic-sidecars.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/research/containerized-diagnostic-sidecars.md)**: Evaluation of in-container (CT 110) vs. Docker sidecar deployment, revealing the critical `plex-exporter` scrape collision.

### Detailed Design Phase
* **[system-architecture.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/design/system-architecture.md)**: High-level infrastructure design and Ansible systemd integration inside LXC CT 110.
* **[watchdog-component.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/design/watchdog-component.md)**: Technical specification, trigger regexes, snapshot command suite, and systemd service configuration for `plex_blip_watchdog.py`.
* **[log-pipeline-component.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/design/log-pipeline-component.md)**: CLI parameters, event taxonomy, time-window correlation engine, and markdown reporting specs for `analyze_plex_blips.py`.
* **[observability-and-remediation.md](file:///home/user/Work/homelab/.agents/planning/2026-08-04-debug-plex-blip/design/observability-and-remediation.md)**: Actionable configuration remediations for `prometheus.yml.j2`, `plex-exporter` intervals, and SQLite WAL database tuning.
