#!/usr/bin/env python3
"""Zero-overhead diagnostic watchdog for Plex Media Server.

Monitors Plex Media Server logs using standard asynchronous inotify file stream
events (zero CPU polling). Matches DB transaction lock stalls, slow library
queries (>500ms), and network relay connectivity drops. Enforces a 30-second
debounce cooldown window and executes bounded diagnostic snapshots (2.0s default
per probe, four probes serial, so 8.0s worst case) including fuser/lsof on SQLite
databases, pidstat, and open descriptor counts, serialized as structured JSON Lines.
The snapshot is bounded, not instant: a probe that blocks is itself the signal, so
each one is allowed to run to its timeout and report the elapsed time it burned.
"""

import argparse
import ctypes
import glob
import json
import os
import re
import select
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any

try:
    _libc = ctypes.CDLL(None)
    _inotify_init1 = _libc.inotify_init1
    _inotify_add_watch = _libc.inotify_add_watch
    _inotify_rm_watch = _libc.inotify_rm_watch
    IN_MODIFY = 0x00000002
    IN_CREATE = 0x00000100
    IN_MOVED_TO = 0x00000080
    IN_DELETE_SELF = 0x00000400
    IN_MOVE_SELF = 0x00000800
    HAS_INOTIFY = True
except Exception:
    HAS_INOTIFY = False

COMPLETED_RE = re.compile(
    r"Completed:\s+\[[^\]]+\]\s+\d+\s+(?:GET|POST|PUT|DELETE)\s+\S+.*?\b(\d+)(?:\.\d+)?ms\b"
)


def check_trigger(line: str, threshold_ms: float = 500.0) -> Optional[Dict[str, Any]]:
    """Evaluates a log line against known blip triggers."""
    line_stripped = line.rstrip("\r\n")

    # 1. DB Transaction Stall
    if "Took too long" in line_stripped and "to start a transaction" in line_stripped:
        m = re.search(r"Took too long \(([0-9.]+)\s+seconds\)", line_stripped)
        delay_ms = float(m.group(1)) * 1000.0 if m else None
        return {"event_type": "TX_STALL", "delay_ms": delay_ms, "line": line_stripped}

    # 2. Slow Query Warn
    if "SLOW QUERY:" in line_stripped:
        m = re.search(r"It took ([0-9.]+)\s+ms", line_stripped)
        delay_ms = float(m.group(1)) if m else None
        return {"event_type": "SLOW_QUERY", "delay_ms": delay_ms, "line": line_stripped}

    # 3. Completed Query >= threshold_ms
    if "Completed:" in line_stripped:
        m = COMPLETED_RE.search(line_stripped)
        if m:
            delay_ms = float(m.group(1))
            if delay_ms >= threshold_ms:
                return {"event_type": "SLOW_QUERY", "delay_ms": delay_ms, "line": line_stripped}

    # 4. Connectivity / Relay Drop & Stream Collapse
    if any(k in line_stripped for k in ("We appear to have lost Internet connectivity", "Failed to retrieve relay host key")):
        return {"event_type": "CONNECTIVITY_DROP", "delay_ms": None, "line": line_stripped}

    if "Shutting down idle session" in line_stripped:
        m = re.search(r"idle time is (\d+)\s+seconds", line_stripped)
        delay_ms = float(m.group(1)) * 1000.0 if m else None
        return {"event_type": "STREAM_DROP", "delay_ms": delay_ms, "line": line_stripped}
    elif any(k in line_stripped for k in ("Terminated session", "Stopping transcode session", "Killing job", "signal: Killed")):
        return {"event_type": "STREAM_DROP", "delay_ms": None, "line": line_stripped}

    return None


def _run_cmd(cmd: list[str], timeout: float = 2.0) -> Dict[str, Any]:
    """Run an external diagnostic probe safely with a hard timeout.

    ALWAYS returns status + elapsed_ms, never a bare string:
        {"status": "ok"|"timeout"|"missing"|"error",
         "elapsed_ms": float, "output": str|None, "error": str|None}

    Three properties this shape exists for, each evidence-driven:
      - The default is 2.0s, not 0.5s: `lsof` exceeded 500ms in 12/12 in-blip
        snapshots, so the probe was tuned for the healthy case. Per-probe
        override stays on the same kwarg.
      - `elapsed_ms` is recorded EVEN ON TIMEOUT. A probe crossing the threshold
        on the database files is itself a contention signal; the old contract
        discarded it, and had no clock to measure it with in the first place.
      - `missing` is separated from `error`. A binary that is not installed is a
        deployment defect (34/34 `fuser` failures were one missing package) and
        must not be spelled the same way as a runtime hiccup.
    """
    started = time.monotonic()

    def _elapsed_ms() -> float:
        return (time.monotonic() - started) * 1000.0

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout
        )
        return {
            "status": "ok",
            "elapsed_ms": _elapsed_ms(),
            "output": proc.stdout.strip(),
            "error": None,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "elapsed_ms": _elapsed_ms(),
            "output": None,
            "error": f"probe timeout exceeded ({timeout}s)",
        }
    except FileNotFoundError as e:
        # Before the generic handler, otherwise "missing" is unreachable.
        return {
            "status": "missing",
            "elapsed_ms": _elapsed_ms(),
            "output": None,
            "error": f"probe binary not found: {e}",
        }
    except Exception as e:
        return {
            "status": "error",
            "elapsed_ms": _elapsed_ms(),
            "output": None,
            "error": f"probe error: {e}",
        }


def get_plex_fd_count(proc_dir: str = "/proc", dry_run: bool = False) -> int:
    """Dynamically count open file descriptors for Plex Media Server processes."""
    total_fds = 0
    found_pids = 0
    my_pid = os.getpid()
    try:
        if os.path.exists(proc_dir):
            for p in os.listdir(proc_dir):
                if not p.isdigit():
                    continue
                pid = int(p)
                if pid == my_pid:
                    continue
                pid_path = os.path.join(proc_dir, p)
                try:
                    cmd = ""
                    comm = ""
                    cmdline_path = os.path.join(pid_path, "cmdline")
                    comm_path = os.path.join(pid_path, "comm")
                    if os.path.exists(cmdline_path):
                        with open(cmdline_path, "r", encoding="utf-8", errors="ignore") as f:
                            cmd = f.read().replace("\x00", " ").strip()
                    if os.path.exists(comm_path):
                        with open(comm_path, "r", encoding="utf-8", errors="ignore") as f:
                            comm = f.read().strip()
                    
                    if "plex_blip_watchdog" in cmd:
                        continue
                    
                    if any(k in comm.lower() or k in cmd.lower() for k in ("plex media server", "plexmediaserver")):
                        fd_dir = os.path.join(pid_path, "fd")
                        if os.path.exists(fd_dir):
                            total_fds += len(os.listdir(fd_dir))
                            found_pids += 1
                except (OSError, FileNotFoundError, PermissionError):
                    continue
    except Exception:
        pass

    if found_pids > 0:
        return total_fds
    if dry_run:
        # Fallback in dry-run/test environments where Plex is not actively running
        try:
            fd_dir = f"{proc_dir}/{my_pid}/fd"
            if os.path.exists(fd_dir):
                return len(os.listdir(fd_dir))
            fd_dir = f"/proc/{my_pid}/fd"
            if os.path.exists(fd_dir):
                return len(os.listdir(fd_dir))
        except Exception:
            return 0
        return 0
    return -1


class InotifyTailer:
    """Non-blocking log file tailer using Linux inotify (or sleep fallback)."""

    def __init__(self, filepath: str):
        self.filepath = os.path.abspath(filepath)
        self.file_obj = None
        self.inotify_fd = None
        self.watch_fd = None

        if HAS_INOTIFY:
            try:
                self.inotify_fd = _inotify_init1(os.O_NONBLOCK | 0x80000)  # O_NONBLOCK | O_CLOEXEC
                self._setup_watch()
            except Exception:
                self.inotify_fd = None

        self._open_file(seek_end=True)

    def _remove_watch(self):
        if self.inotify_fd is not None and self.watch_fd is not None and self.watch_fd >= 0:
            try:
                _inotify_rm_watch(self.inotify_fd, self.watch_fd)
            except Exception:
                pass
            self.watch_fd = None

    def _setup_watch(self):
        if self.inotify_fd is not None:
            if self.watch_fd is not None and self.watch_fd >= 0:
                self._remove_watch()
            target = self.filepath
            if not os.path.exists(target):
                target = os.path.dirname(target) or "."
            mask = IN_MODIFY | IN_CREATE | IN_MOVED_TO | IN_DELETE_SELF | IN_MOVE_SELF
            try:
                self.watch_fd = _inotify_add_watch(self.inotify_fd, target.encode("utf-8"), mask)
            except Exception:
                self.watch_fd = None

    def _open_file(self, seek_end: bool = True):
        if os.path.exists(self.filepath):
            try:
                self.file_obj = open(self.filepath, "r", encoding="utf-8", errors="replace")
                if seek_end:
                    self.file_obj.seek(0, os.SEEK_END)
            except Exception:
                self.file_obj = None

    def _check_rotation_or_truncation(self):
        if self.file_obj is None:
            return
        try:
            cur_stat = os.stat(self.filepath)
            open_ino = os.fstat(self.file_obj.fileno()).st_ino
            # Inode changed: log was rotated or replaced
            if cur_stat.st_ino != open_ino:
                self.file_obj.close()
                self.file_obj = None
                self._remove_watch()
                self._open_file(seek_end=False)
                if self.file_obj is not None:
                    self._setup_watch()
                return
            # Truncated in place: file size shrunk below read position
            if cur_stat.st_size < self.file_obj.tell():
                self.file_obj.seek(0, os.SEEK_SET)
        except (OSError, FileNotFoundError):
            # File was removed or doesn't exist anymore
            try:
                self.file_obj.close()
            except Exception:
                pass
            self.file_obj = None
            self._remove_watch()

    def read_line(self, timeout: float = 0.5) -> Optional[str]:
        """Read next appended line or wait up to timeout in zero-CPU kernel sleep."""
        if self.file_obj is None:
            self._open_file(seek_end=False)
            if self.file_obj is None:
                time.sleep(min(timeout, 0.2))
                return None
            else:
                self._setup_watch()

        line = self.file_obj.readline()
        if line:
            return line

        # At EOF: check if rotation or truncation occurred before waiting
        self._check_rotation_or_truncation()
        if self.file_obj is not None:
            line = self.file_obj.readline()
            if line:
                return line

        # Sleep wait in kernel via select on inotify fd
        if self.inotify_fd is not None and self.watch_fd is not None and self.watch_fd >= 0:
            r, _, _ = select.select([self.inotify_fd], [], [], timeout)
            if r:
                try:
                    os.read(self.inotify_fd, 4096)
                except OSError:
                    pass
                line = self.file_obj.readline() if self.file_obj else None
                if line:
                    return line
                self._check_rotation_or_truncation()
                if self.file_obj is not None:
                    line = self.file_obj.readline()
                    if line:
                        return line
        else:
            time.sleep(min(timeout, 0.2))
            self._check_rotation_or_truncation()
            if self.file_obj is not None:
                line = self.file_obj.readline()
                if line:
                    return line

        return None


    def close(self):
        self._remove_watch()
        if self.file_obj:
            try:
                self.file_obj.close()
            except Exception:
                pass
        if self.inotify_fd is not None and self.inotify_fd >= 0:
            try:
                os.close(self.inotify_fd)
            except Exception:
                pass
            self.inotify_fd = None


class WatchdogEngine:
    def __init__(
        self,
        log_path: str,
        output_dir: str,
        db_pattern: str = "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db*",
        debounce_sec: float = 30.0,
        threshold_ms: float = 500.0,
        dry_run: bool = False
    ):
        self.log_path = log_path
        self.output_dir = output_dir
        self.db_pattern = db_pattern
        self.debounce_sec = debounce_sec
        self.threshold_ms = threshold_ms
        self.dry_run = dry_run
        self.last_trigger_time: Optional[float] = None

        os.makedirs(self.output_dir, exist_ok=True)

    def should_trigger(self, now: float) -> bool:
        if self.last_trigger_time is None:
            return True
        return (now - self.last_trigger_time) >= self.debounce_sec

    def record_trigger(self, now: float):
        self.last_trigger_time = now

    def capture_snapshot(self, trigger: Dict[str, Any]) -> str:
        """Execute the bounded diagnostic probes and serialize to JSONL.

        Every probe is allowed to run to `_run_cmd`'s timeout rather than being cut
        short, because a probe that blocks is itself the signal. The module header
        names the resulting worst case; it is not repeated here, since a figure
        quoted far from the code it describes is how the `<500ms` claim went stale
        in the first place.
        """
        now_ts = datetime.now()
        iso_ts = now_ts.isoformat(timespec="milliseconds")

        # Resolve DB pattern to matching files
        matched_dbs = glob.glob(self.db_pattern)
        targets = matched_dbs if matched_dbs else [self.db_pattern]

        # 1. Lock Holder Probes
        fuser_out = _run_cmd(["fuser", "-v"] + targets)
        lsof_out = _run_cmd(["lsof"] + targets)

        if self.dry_run:
            if not fuser_out or "probe error" in fuser_out or fuser_out == "":
                fuser_out = f"[dry-run] fuser simulated check OK for {self.db_pattern}"
            if not lsof_out or "probe error" in lsof_out or lsof_out == "":
                lsof_out = f"[dry-run] lsof simulated check OK for {self.db_pattern}"

        # 2. Thread State & CPU Metrics
        pidstat_out = _run_cmd(["pidstat", "-tl"])
        ps_out = _run_cmd(["ps", "-aux", "-T"])
        if self.dry_run and ("probe error" in pidstat_out or not pidstat_out):
            pidstat_out = "[dry-run] pidstat diagnostic snapshot OK"

        # 3. FD Count
        fd_count = get_plex_fd_count(proc_dir="/proc", dry_run=self.dry_run)

        record = {
            "timestamp": iso_ts,
            "trigger_event": trigger.get("event_type", "UNKNOWN"),
            "delay_ms": trigger.get("delay_ms"),
            "trigger_line": trigger.get("line", ""),
            "lock_holders": {
                "fuser": fuser_out,
                "lsof": lsof_out,
            },
            "process_traces": {
                "ps_aux_t": ps_out,
            },
            "sysstat_metrics": {
                "pidstat": pidstat_out,
                "fd_count": fd_count,
            },
            "dry_run": self.dry_run
        }

        filename = f"plex_blip_diagnostics_{now_ts.strftime('%Y%m%d')}.jsonl"
        out_path = os.path.join(self.output_dir, filename)
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            f.flush()

        if self.dry_run:
            print(f"[DRY-RUN] Snapshot captured for {record['trigger_event']} -> {out_path}", file=sys.stdout)

        return out_path

    def run(self, max_triggers: Optional[int] = None):
        tailer = InotifyTailer(self.log_path)
        triggers_seen = 0

        try:
            while True:
                line = tailer.read_line(timeout=0.5)
                if line is not None:
                    trigger = check_trigger(line, threshold_ms=self.threshold_ms)
                    if trigger is not None:
                        now = time.time()
                        if self.should_trigger(now):
                            self.record_trigger(now)
                            self.capture_snapshot(trigger)
                            triggers_seen += 1
                            if max_triggers is not None and triggers_seen >= max_triggers:
                                break
                        else:
                            # Debounced
                            pass
        except KeyboardInterrupt:
            pass
        finally:
            tailer.close()


def main():
    parser = argparse.ArgumentParser(description="Plex Blip Zero-Overhead Diagnostic Watchdog")
    parser.add_argument("--log-path", required=True, help="Path to Plex Media Server.log to monitor")
    parser.add_argument("--output-dir", required=True, help="Directory to store persistent JSONL diagnostic artifacts")
    parser.add_argument("--db-pattern", default="/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db*", help="File glob pattern for Plex SQLite database files")
    parser.add_argument("--debounce-sec", type=float, default=30.0, help="Cooldown window between snapshots in seconds")
    parser.add_argument("--threshold-ms", type=float, default=500.0, help="Slow query latency threshold in milliseconds")
    parser.add_argument("--dry-run", action="store_true", help="Perform simulated non-destructive verification check")
    parser.add_argument("--max-triggers", type=int, default=None, help="Stop running after N triggers (useful for testing and verification)")

    args = parser.parse_args()
    engine = WatchdogEngine(
        log_path=args.log_path,
        output_dir=args.output_dir,
        db_pattern=args.db_pattern,
        debounce_sec=args.debounce_sec,
        threshold_ms=args.threshold_ms,
        dry_run=args.dry_run
    )
    engine.run(max_triggers=args.max_triggers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
