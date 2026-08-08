# Runbook: Plex SQLite Database Maintenance

This runbook documents the SQLite database maintenance procedures for Plex Media Server.

## 1. WAL Mode Audit

Plex Media Server utilizes SQLite for its library database, located at `{{ plex_state_dir }}/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db`. For high concurrency between reads (library queries) and writes (scans/metadata updates), the database **must** be operating in Write-Ahead Logging (WAL) mode.

**WAL mode is necessary but NOT sufficient to prevent transaction lock stalls (`TX_STALL`).** This runbook used to say WAL mode exists *to prevent* them. On **2026-08-07** we measured WAL mode enabled **and** `TX_STALL` occurring at the same time on CT 110: the write-ahead log stood at **43,735,168 bytes** against a 40.9 MiB database and had been byte-identical for 42.5 hours, because a long-lived reader pinned the oldest snapshot and nothing could reclaim the log. An unchecked WAL is itself a stall mechanism — every reader walks it, and it only grows.

The Ansible role audits **both halves** on every deployment, and either one fails the play:

| Half | Where | What it asserts |
| --- | --- | --- |
| Journal mode | `ansible/roles/plex/tasks/main.yml:369-378` — the `sqlite3` CLI, `-readonly` | `PRAGMA journal_mode` returns `wal` |
| WAL size | `ansible/roles/plex/tasks/main.yml:380-438` — `ansible.builtin.stat` plus an `assert` | the `-wal` file is under `plex_wal_max_bytes`, **8388608** bytes (`ansible/roles/plex/defaults/main.yml:54`) |

The size half is deliberately not derived from the `sqlite3` output. It stands on a `stat` alone, so it can be watched going red without a deploy and without the CLI — see `scripts/test_plex_wal_guard_shape.py`. When it fires, the failure message carries the ordered manual remedy inline (`ansible/roles/plex/tasks/main.yml:425-435`): stop `plexmediaserver`, reclaim the log, start it again, in that order. Do not run the reclaim step while Plex is up — it comes back `busy`, moves nothing, and the CLI still exits `0`.

To manually verify the journal mode (read-only), as the Plex service user:
```bash
sudo -u plex sqlite3 -readonly "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db" "PRAGMA journal_mode;"
```

**Run it as `plex`, not as root.** A read-only connection to a WAL database has to materialise the `-shm` sidecar in order to read it, and cannot run the close-time cleanup that removes it — only a writer can. Measured against libsqlite3 3.51.2 with no live holder: the read-only open leaves a 0-byte `-wal` and a 32768-byte `-shm` behind, mode 0644. Run as root, those land root-owned in a directory Plex's own uid owns, and on Plex's next write SQLite falls back rather than failing loudly: the server keeps serving and **the library goes silently read-only**. While Plex is up the sidecars already exist and nothing is created, so this only bites when the check is run against a stopped server — which is exactly when an operator reaches for it.

**Expected Output:**
```
wal
```
If this returns anything other than `wal` (e.g., `delete`), Plex's internal migrations have failed or an external process has rolled back the journal mode.

## 2. Off-peak VACUUM / REINDEX Timer — THERE IS NO SUCH TIMER

Because WAL mode appends writes rather than modifying the main database file in-place, the database and its indexes can become fragmented over time, degrading query performance (`SLOW_QUERY`).

**Nothing schedules maintenance on this database, and this runbook used to claim something did.** It said Plex Media Server *"has a scheduled task that performs `VACUUM` and `REINDEX` operations"*, *"configured to run at **03:30 AM**"*. Neither half survives measurement: `grep -rniE 'VACUUM|REINDEX|03:30' ansible/ --exclude-dir=galaxy_roles` returns **zero hits** and `ansible/roles/plex/templates/` holds exactly one file (the watchdog unit), so this repo ships no such timer — and it is not a stock Plex Media Server feature either. A 03:30 `VACUUM`/`REINDEX` timer was *proposed* in `.agents/planning/2026-08-04-debug-plex-blip/implementation/plan.md:116` and was never built.

**What that means for triage:** there is no maintenance window, so a `SLOW_QUERY` event is never collateral from a maintenance lock and must **not** be ignored on those grounds. The advice this section used to give — ignore them near the window unless they persist outside it — was advice to ignore the fault. Fragmentation accumulates unattended; the only automated pressure on this database today is the WAL size half of §1's audit.
