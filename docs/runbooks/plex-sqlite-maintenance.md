# Runbook: Plex SQLite Database Maintenance

This runbook documents the SQLite database maintenance procedures for Plex Media Server.

## 1. WAL Mode Audit

Plex Media Server utilizes SQLite for its library database, located at `{{ plex_state_dir }}/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db`. To prevent transaction lock stalls (`TX_STALL`) and ensure high concurrency for reads (library queries) while writes (scans/metadata updates) are occurring, the database **must** be operating in Write-Ahead Logging (WAL) mode.

The Ansible role automatically audits this requirement during deployment using the `sqlite3` CLI.

To manually verify the journal mode (read-only):
```bash
sqlite3 "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db" "PRAGMA journal_mode;"
```
**Expected Output:**
```
wal
```
If this returns anything other than `wal` (e.g., `delete`), Plex's internal migrations have failed or an external process has rolled back the journal mode.

## 2. Off-peak VACUUM / REINDEX Timer

Because WAL mode appends writes rather than modifying the main database file in-place, the database and its indexes can become fragmented over time, degrading query performance (`SLOW_QUERY`).

Plex Media Server has a scheduled task that performs `VACUUM` and `REINDEX` operations. This timer is configured to run at **03:30 AM** (off-peak hours) to ensure that the heavy I/O and exclusive database locks required by these operations do not interrupt media streaming or user interaction.

If you encounter `SLOW_QUERY` events near this time window, they are likely collateral from the maintenance lock and can be ignored unless they persist outside the maintenance window.
