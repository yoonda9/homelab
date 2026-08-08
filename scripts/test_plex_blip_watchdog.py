#!/usr/bin/env python3
"""Unit and integration tests for plex_blip_watchdog.py log monitoring script.

Verifies zero-overhead inotify log tailing, trigger matching for DB lock stalls,
slow queries (>500ms), and network/relay collapses, 30s debounce rate-limiting,
and structured JSONL diagnostic snapshots (fuser, lsof, pidstat).
"""

import ast
import inspect
import json
import os
import pathlib
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
WATCHDOG_DIR = REPO_ROOT / "ansible" / "roles" / "plex" / "files"
WATCHDOG_SCRIPT = WATCHDOG_DIR / "plex_blip_watchdog.py"

if str(WATCHDOG_DIR) not in sys.path:
    sys.path.insert(0, str(WATCHDOG_DIR))

import plex_blip_watchdog as watchdog


class TestPlexBlipWatchdog(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="plex_watchdog_test_")
        self.log_path = os.path.join(self.test_dir, "mock_plex.log")
        self.out_dir = os.path.join(self.test_dir, "diagnostics")
        os.makedirs(self.out_dir, exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Aug 04, 2026 06:57:00.000 [100] INFO - Server starting up\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_trigger_matching(self):
        # 1. DB Transaction Stall
        line = "Aug 04, 2026 06:58:11.899 [101] WARN - Took too long (0.120000 seconds) to start a transaction on StatisticsBandwidth.cpp:110"
        res = watchdog.check_trigger(line, threshold_ms=500.0)
        self.assertIsNotNone(res, "Should trigger on TX_STALL")
        self.assertEqual(res["event_type"], "TX_STALL")
        self.assertEqual(res["delay_ms"], 120.0)

        # 2. Slow Query Warn
        line = "Aug 04, 2026 06:58:49.160 [102] WARN - [Req#57d3a] SLOW QUERY: It took 4360.000000 ms to retrieve 0 items."
        res = watchdog.check_trigger(line, threshold_ms=500.0)
        self.assertIsNotNone(res, "Should trigger on SLOW_QUERY warning")
        self.assertEqual(res["event_type"], "SLOW_QUERY")
        self.assertEqual(res["delay_ms"], 4360.0)

        # 3. Completed query > 500ms
        line = "Aug 04, 2026 06:58:52.965 [103] DEBUG - Completed: [192.168.1.111:55824] 200 GET /library/sections/3/all #57d3a Page 0--1 35905ms 707 bytes"
        res = watchdog.check_trigger(line, threshold_ms=500.0)
        self.assertIsNotNone(res, "Should trigger on Completed > threshold")
        self.assertEqual(res["event_type"], "SLOW_QUERY")
        self.assertEqual(res["delay_ms"], 35905.0)

        # 4. Completed query <= 500ms (should NOT trigger)
        line = "Aug 04, 2026 06:58:53.000 [104] DEBUG - Completed: [192.168.1.111:55824] 200 GET /library/sections/3/all #57d3b Page 0--1 120ms 707 bytes"
        res = watchdog.check_trigger(line, threshold_ms=500.0)
        self.assertIsNone(res, "Should NOT trigger on Completed <= threshold")

        # 5. Connectivity / Relay drop
        line1 = "Aug 04, 2026 07:00:10.756 [105] ERROR - [EventSourceClient/...] Relay: Failed to retrieve relay host key from plex.tv"
        res1 = watchdog.check_trigger(line1, threshold_ms=500.0)
        self.assertIsNotNone(res1, "Should trigger on Relay key failure")
        self.assertEqual(res1["event_type"], "CONNECTIVITY_DROP")

        line2 = "Aug 04, 2026 07:00:15.000 [106] ERROR - We appear to have lost Internet connectivity"
        res2 = watchdog.check_trigger(line2, threshold_ms=500.0)
        self.assertIsNotNone(res2, "Should trigger on lost Internet connectivity")
        self.assertEqual(res2["event_type"], "CONNECTIVITY_DROP")

        line3 = "Aug 04, 2026 07:00:20.000 [107] DEBUG - Shutting down idle session 8a729f13-b95d-4aab-9700-5eab86bf88f2 (idle time is 180 seconds)"
        res3 = watchdog.check_trigger(line3, threshold_ms=500.0)
        self.assertIsNotNone(res3, "Should trigger on session shut down")
        self.assertEqual(res3["event_type"], "STREAM_DROP")
        self.assertEqual(res3["delay_ms"], 180000.0)

    def test_debounce_cooldown(self):
        engine = watchdog.WatchdogEngine(log_path=self.log_path, output_dir=self.out_dir, debounce_sec=30.0)
        # Force initial state
        now = 1000.0
        self.assertTrue(engine.should_trigger(now), "First event should trigger")
        engine.record_trigger(now)

        # Event within 30s window should be debounced
        self.assertFalse(engine.should_trigger(now + 15.0), "Event at +15s should be debounced")
        self.assertFalse(engine.should_trigger(now + 29.9), "Event at +29.9s should be debounced")

        # Event at or after 30s should trigger
        self.assertTrue(engine.should_trigger(now + 30.0), "Event at +30.0s should trigger after cooldown")
        self.assertTrue(engine.should_trigger(now + 45.0), "Event at +45s should trigger after cooldown")

    def test_diagnostic_snapshot_format(self):
        # Create a temporary sqlite db to test lock checking
        db_path = os.path.join(self.test_dir, "com.plexapp.plugins.library.db")
        con = sqlite3.connect(db_path)
        con.execute("CREATE TABLE IF NOT EXISTS test (id INT);")
        con.commit()
        con.close()

        trigger = {
            "event_type": "TX_STALL",
            "delay_ms": 120.0,
            "line": "Aug 04, 2026 06:58:11.899 [101] WARN - Took too long (0.120000 seconds) to start a transaction on StatisticsBandwidth.cpp:110"
        }

        engine = watchdog.WatchdogEngine(
            log_path=self.log_path,
            output_dir=self.out_dir,
            db_pattern=db_path,
            dry_run=True
        )
        engine.capture_snapshot(trigger)

        # Check JSONL output
        out_files = list(pathlib.Path(self.out_dir).glob("*.jsonl"))
        self.assertEqual(len(out_files), 1, "Should generate exactly one JSONL file")
        
        with open(out_files[0], "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1, "JSONL file should have 1 line for 1 snapshot")
        
        record = json.loads(lines[0])
        self.assertIn("timestamp", record)
        self.assertEqual(record["trigger_event"], "TX_STALL")
        self.assertEqual(record["delay_ms"], 120.0)
        self.assertEqual(record["trigger_line"], trigger["line"])
        self.assertIn("lock_holders", record)
        self.assertIn("process_traces", record)
        self.assertIn("sysstat_metrics", record)
        self.assertTrue(record.get("dry_run", False))

    def test_dry_run_subprocess(self):
        # Execute standalone verification via command line as specified in plan.md Step 2
        cmd = [
            sys.executable,
            str(WATCHDOG_SCRIPT),
            "--log-path", self.log_path,
            "--output-dir", self.out_dir,
            "--dry-run",
            "--max-triggers", "1",
        ]
        
        # Start watchdog process in background
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait briefly to let watchdog start monitoring
        time.sleep(0.5)

        # Append a trigger line to the log file
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write("Aug 04, 2026 06:58:11.899 [101] WARN - Took too long (0.120000 seconds) to start a transaction on StatisticsBandwidth.cpp:110\n")
            f.flush()

        stdout, stderr = proc.communicate(timeout=5)
        self.assertEqual(proc.returncode, 0, f"Process failed with code {proc.returncode}: {stderr}\n{stdout}")

        out_files = list(pathlib.Path(self.out_dir).glob("*.jsonl"))
        self.assertEqual(len(out_files), 1, f"Should generate JSONL record in {self.out_dir}")
        with open(out_files[0], "r", encoding="utf-8") as f:
            record = json.loads(f.readline().strip())
        self.assertEqual(record["trigger_event"], "TX_STALL")
        self.assertEqual(record["delay_ms"], 120.0)

    def test_adversarial_malformed_logs_and_rotation(self):
        # Adversarial evaluation: garbage UTF-8, truncated lines, empty lines, and log rotation
        cmd = [
            sys.executable,
            str(WATCHDOG_SCRIPT),
            "--log-path", self.log_path,
            "--output-dir", self.out_dir,
            "--dry-run",
            "--debounce-sec", "0.1",
            "--max-triggers", "1",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(0.4)

        # 1. Write garbage bytes and non-trigger spam
        with open(self.log_path, "wb") as f:
            f.write(b"\xff\xfe\x00\x01 random garbage line without timestamp\r\n\n\n")
            f.flush()
        time.sleep(0.2)

        # 2. Simulate log rotation (rename old file, create new clean log file with trigger)
        rotated_path = self.log_path + ".1"
        if os.path.exists(self.log_path):
            os.rename(self.log_path, rotated_path)
        
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Aug 04, 2026 07:00:10.756 [105] ERROR - Relay: Failed to retrieve relay host key from plex.tv\n")
            f.flush()

        stdout, stderr = proc.communicate(timeout=5)
        self.assertEqual(proc.returncode, 0, f"Adversarial rotation run failed: {stderr}")
        
        out_files = list(pathlib.Path(self.out_dir).glob("*.jsonl"))
        self.assertGreaterEqual(len(out_files), 1)
        with open(out_files[0], "r", encoding="utf-8") as f:
            record = json.loads(f.readline().strip())
        self.assertEqual(record["trigger_event"], "CONNECTIVITY_DROP")

    def test_standalone_mock_log_smoke_command(self):
        # Explicit verification against /tmp/test_plex.log and /tmp/watchdog_out as in plan.md
        tmp_log = "/tmp/test_plex.log"
        tmp_out = "/tmp/watchdog_out"
        shutil.rmtree(tmp_out, ignore_errors=True)
        try:
            with open(tmp_log, "w", encoding="utf-8") as f:
                f.write("Aug 04, 2026 06:50:00.000 [10] INFO - Initial line\n")
            
            cmd = [
                sys.executable,
                str(WATCHDOG_SCRIPT),
                "--log-path", tmp_log,
                "--output-dir", tmp_out,
                "--dry-run",
                "--max-triggers", "1"
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            time.sleep(0.5)
            
            with open(tmp_log, "a", encoding="utf-8") as f:
                f.write("Aug 04, 2026 06:58:49.160 [102] WARN - [Req#57d3a] SLOW QUERY: It took 4360.000000 ms to retrieve 0 items.\n")
                f.flush()
                
            stdout, stderr = proc.communicate(timeout=5)
            self.assertEqual(proc.returncode, 0, f"Smoke command failed: {stderr}")
            out_files = list(pathlib.Path(tmp_out).glob("*.jsonl"))
            self.assertEqual(len(out_files), 1, f"Expected 1 JSONL file in {tmp_out}")
        finally:
            if os.path.exists(tmp_log):
                os.remove(tmp_log)
            shutil.rmtree(tmp_out, ignore_errors=True)

    def test_inotify_watch_recovery_after_rotation(self):
        if not watchdog.HAS_INOTIFY:
            self.skipTest("inotify not supported on this platform")
        tailer = watchdog.InotifyTailer(self.log_path)
        try:
            self.assertIsNotNone(tailer.inotify_fd)
            self.assertIsNotNone(tailer.watch_fd)
            # Drain initial contents
            while tailer.read_line(timeout=0.1) is not None:
                pass
            
            # Simulate log rotation (rename old log, write new line to recreated log file)
            rotated_path = self.log_path + ".1"
            if os.path.exists(self.log_path):
                os.rename(self.log_path, rotated_path)
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write("Aug 04, 2026 07:00:10.000 [100] INFO - Line after rotation 1\n")
                f.flush()

            # Tailer reads the first line from the new file after detecting inode change
            line = tailer.read_line(timeout=0.5)
            self.assertEqual(line, "Aug 04, 2026 07:00:10.000 [100] INFO - Line after rotation 1\n")

            # Drain any lingering inotify events (such as IN_MOVE_SELF from the rename) before testing new writes
            if tailer.inotify_fd is not None:
                try:
                    while True:
                        os.read(tailer.inotify_fd, 4096)
                except (OSError, BlockingIOError):
                    pass

            # Write a second line to the new file while tailer is waiting at EOF
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write("Aug 04, 2026 07:00:15.000 [100] INFO - Line after rotation 2\n")
                f.flush()

            # Assert that inotify actually detected the write to the new inode without sleep fallback
            import select
            r, _, _ = select.select([tailer.inotify_fd], [], [], 0.5)
            self.assertTrue(len(r) > 0, "Inotify failed to generate event on new log file after rotation; watch descriptor was wedged on old inode.")
        finally:
            tailer.close()

    def test_plex_media_server_fd_probing(self):
        # Create a mock /proc tree in test_dir to verify dynamic Plex process FD counting
        mock_proc = os.path.join(self.test_dir, "mock_proc")
        os.makedirs(mock_proc, exist_ok=True)
        
        # 1. Non-Plex process (watchdog script itself)
        pid_watchdog = os.path.join(mock_proc, "1101")
        os.makedirs(os.path.join(pid_watchdog, "fd"), exist_ok=True)
        with open(os.path.join(pid_watchdog, "comm"), "w", encoding="utf-8") as f:
            f.write("python3\n")
        with open(os.path.join(pid_watchdog, "cmdline"), "w", encoding="utf-8") as f:
            f.write("python3\x00plex_blip_watchdog.py\x00--log-path\x00test.log\x00")
        for i in range(4):
            with open(os.path.join(pid_watchdog, "fd", str(i)), "w") as f:
                f.write("")

        # 2. Mock Plex Media Server process
        pid_plex = os.path.join(mock_proc, "1102")
        os.makedirs(os.path.join(pid_plex, "fd"), exist_ok=True)
        with open(os.path.join(pid_plex, "comm"), "w", encoding="utf-8") as f:
            f.write("Plex Media Serv\n")
        with open(os.path.join(pid_plex, "cmdline"), "w", encoding="utf-8") as f:
            f.write("/usr/lib/plexmediaserver/Plex Media Server\x00-k\x00")
        for i in range(15):
            with open(os.path.join(pid_plex, "fd", str(i)), "w") as f:
                f.write("")

        # Verify get_plex_fd_count counts the 15 FDs from Plex and ignores the 4 FDs from watchdog
        fd_count = watchdog.get_plex_fd_count(proc_dir=mock_proc, dry_run=False)
        self.assertEqual(fd_count, 15, f"Expected 15 FDs for simulated Plex process, got {fd_count}")

        # Verify fallback when no Plex process exists in dry-run mode vs live mode
        shutil.rmtree(pid_plex)
        self.assertEqual(watchdog.get_plex_fd_count(proc_dir=mock_proc, dry_run=False), -1)
        self.assertGreaterEqual(watchdog.get_plex_fd_count(proc_dir=mock_proc, dry_run=True), 0)


class TestRunCmdStructuredResult(unittest.TestCase):
    """Step 1a — `_run_cmd`'s structured probe result (design §5.1).

    The contract is `{status, elapsed_ms, output, error}` with `status` in exactly
    four spellings. Each spelling is reached by a named input, all four below:
      ok      -> a command that exits normally (`sys.executable -c print(...)`)
      timeout -> a command that sleeps past the timeout (`time.sleep(5)` at 0.2s)
      missing -> a binary that is not on PATH (the no-`psmisc` `fuser` case)
      error   -> a path that exists but is not executable (PermissionError)
    """

    CONTRACT_KEYS = {"status", "elapsed_ms", "output", "error"}

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="plex_watchdog_runcmd_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_run_cmd_timeout_records_elapsed_ms(self):
        # The regression that matters most: the pre-change code had no clock at
        # all, so asserting only status=="timeout" would pass for the wrong
        # reason. Assert the NUMBER. `lsof` crossing the threshold on the DB
        # files is itself a contention signal and must survive the timeout.
        timeout = 0.2
        res = watchdog._run_cmd(
            [sys.executable, "-c", "import time; time.sleep(5)"], timeout=timeout
        )
        self.assertIsInstance(res, dict, "probe result must be the structured dict")
        self.assertEqual(set(res), self.CONTRACT_KEYS)
        self.assertEqual(res["status"], "timeout")
        self.assertIsInstance(res["elapsed_ms"], float)
        self.assertGreaterEqual(
            res["elapsed_ms"], timeout * 1000.0 * 0.9,
            "elapsed_ms must be the measured duration, not 0/None, on the timeout path",
        )
        self.assertLess(
            res["elapsed_ms"], timeout * 1000.0 + 1500.0,
            "elapsed_ms must be ~the timeout, not the 5s the command wanted to sleep",
        )

    def test_run_cmd_default_timeout_is_two_seconds(self):
        # 0.5s was tuned for the healthy case; lsof exceeded it in 12/12 in-blip
        # snapshots. Per-probe override stays available via the same kwarg.
        default = inspect.signature(watchdog._run_cmd).parameters["timeout"].default
        self.assertEqual(default, 2.0)

    def test_run_cmd_missing_binary_is_missing_not_error(self):
        # The no-`psmisc` `fuser` case. Today "missing" and "error" are the same
        # string, so this test must separate them.
        res = watchdog._run_cmd(["plex-blip-no-such-binary-xyz"], timeout=0.5)
        self.assertIsInstance(res, dict)
        self.assertEqual(set(res), self.CONTRACT_KEYS)
        self.assertEqual(res["status"], "missing")
        self.assertNotEqual(res["status"], "error", "a deployment defect is not a runtime hiccup")
        self.assertIsNone(res["output"])
        self.assertIsNotNone(res["error"])
        self.assertIsInstance(res["elapsed_ms"], float)
        self.assertGreaterEqual(res["elapsed_ms"], 0.0)

    def test_run_cmd_ok_preserves_output(self):
        payload = "plex  1234 F....m  \tuser  (interior   whitespace kept)"
        res = watchdog._run_cmd(
            [sys.executable, "-c", f"print({payload!r})"], timeout=5.0
        )
        self.assertIsInstance(res, dict)
        self.assertEqual(set(res), self.CONTRACT_KEYS)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["output"], payload, "output preserved byte-for-byte after strip")
        self.assertIsNone(res["error"])
        self.assertIsInstance(res["elapsed_ms"], float)
        self.assertGreater(res["elapsed_ms"], 0.0)

    def test_run_cmd_error_is_reachable_and_distinct_from_missing(self):
        # Fourth spelling: the file EXISTS (so it is not "missing") but cannot be
        # executed -> PermissionError -> generic except.
        not_executable = os.path.join(self.test_dir, "probe.sh")
        with open(not_executable, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\necho hi\n")
        os.chmod(not_executable, 0o644)

        res = watchdog._run_cmd([not_executable], timeout=0.5)
        self.assertIsInstance(res, dict)
        self.assertEqual(set(res), self.CONTRACT_KEYS)
        self.assertEqual(res["status"], "error")
        self.assertNotEqual(res["status"], "missing")
        self.assertIsNone(res["output"])
        self.assertIsNotNone(res["error"])

    def test_run_cmd_status_vocabulary_is_exactly_four_spellings(self):
        seen = {
            watchdog._run_cmd([sys.executable, "-c", "pass"], timeout=5.0)["status"],
            watchdog._run_cmd(
                [sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2
            )["status"],
            watchdog._run_cmd(["plex-blip-no-such-binary-xyz"], timeout=0.5)["status"],
        }
        not_executable = os.path.join(self.test_dir, "probe2.sh")
        with open(not_executable, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n")
        os.chmod(not_executable, 0o644)
        seen.add(watchdog._run_cmd([not_executable], timeout=0.5)["status"])

        self.assertEqual(seen, {"ok", "timeout", "missing", "error"})


class TestSnapshotStructuredShape(unittest.TestCase):
    """Step 1b — the snapshot record carries `_run_cmd`'s structured result (design §5.1).

    Step 1a changed `_run_cmd` to return a dict. `capture_snapshot`'s three
    dry-run fallbacks still tested that return AS A STRING, and `"probe error"
    in <dict>` tests KEYS, so it is permanently False. THE FAILURE IS SILENT:
    not a crash, just `--dry-run` quietly ceasing to simulate while every test
    stays green. `test_dry_run_fallbacks_fire_when_the_probe_binary_is_missing`
    is the row that refuses to stay green through that, and it is written to be
    unfakeable by a substring test: the probes are made genuinely absent by
    setting `PATH` to a stub dir ALONE (prepending does not work -- `execvp`
    skips a candidate it cannot run and keeps searching the rest of PATH).
    """

    # Widened twice: Step 2d took it 8 -> 10, Step 3a takes it 10 -> 11. Spelled
    # in digits deliberately -- a number-WORD here is what let a method name go
    # on claiming a count the set had outgrown, and this comment is the only
    # place the history is worth keeping. The eight below the fold are the keys
    # the 34 captures already on disk carry;
    # `hold_site` and `live_connections` are Step 2's Integration line
    # (plan.md:95); `sqlite` is Step 3's WAL block (design C1.4, plan.md:165).
    # The set is still an EQUALITY, not a subset: an addition is a deliberate
    # edit here and a removal still breaks every capture already written.
    KEYS_ALREADY_ON_DISK = {
        "timestamp",
        "trigger_event",
        "delay_ms",
        "trigger_line",
        "lock_holders",
        "process_traces",
        "sysstat_metrics",
        "dry_run",
    }
    TOP_LEVEL_KEYS = KEYS_ALREADY_ON_DISK | {"hold_site", "live_connections", "sqlite"}
    PROBE_KEYS = {"status", "elapsed_ms", "output", "error"}

    TRIGGER = {
        "event_type": "TX_STALL",
        "delay_ms": 120.0,
        "line": "Aug 04, 2026 06:58:11.899 [101] WARN - Took too long (0.120000 seconds) to start a transaction on StatisticsBandwidth.cpp:110",
    }

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="plex_watchdog_snapshot_")
        self.log_path = os.path.join(self.test_dir, "mock_plex.log")
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Aug 04, 2026 06:57:00.000 [100] INFO - Server starting up\n")
        self.out_dir = os.path.join(self.test_dir, "diagnostics")
        self.db_path = os.path.join(self.test_dir, "com.plexapp.plugins.library.db")
        with open(self.db_path, "wb") as f:
            f.write(b"SQLite format 3\x00")
        self.stub_dir = os.path.join(self.test_dir, "stub_path")
        os.makedirs(self.stub_dir, exist_ok=True)
        self._real_path = os.environ.get("PATH", "")

    def tearDown(self):
        os.environ["PATH"] = self._real_path
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _install_silent_stub(self, name: str):
        """A probe that RUNS and says nothing -- real `fuser`/`lsof` exit 1 with
        empty output when nothing holds the file. status is "ok"; output is ""."""
        path = os.path.join(self.stub_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\nexit 1\n")
        os.chmod(path, 0o755)

    # Distinct text per probe, so the row also catches a cross-wiring: a fallback
    # that substituted lsof's line into fuser's site would keep "no [dry-run]"
    # true while still fabricating.
    SPEAKING_STUBS = {
        "fuser": "/tmp/library.db: 1234m 5678",
        "lsof": "COMMAND  PID USER  FD  TYPE  NAME\nPlex  1234 plex  42u  REG  library.db",
        "pidstat": "REAL PIDSTAT 1234 plex 0.4 0.0",
        "ps": "REAL PS 1234 plex Plex Media Server",
    }

    def _install_speaking_stub(self, name: str):
        """A probe that RUNS and SPEAKS -- status "ok" with non-empty output, which
        is the healthy post-`psmisc` case (Step 1c) the operator demos under
        `--dry-run`. Shell BUILTINS only: `PATH` is the stub dir alone, so `cat`
        and friends are not resolvable from inside the stub itself."""
        path = os.path.join(self.stub_dir, name)
        lines = " ".join(f"'{ln}'" for ln in self.SPEAKING_STUBS[name].split("\n"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"#!/bin/sh\nprintf '%s\\n' {lines}\nexit 0\n")
        os.chmod(path, 0o755)

    def _capture(self, dry_run=True):
        engine = watchdog.WatchdogEngine(
            log_path=self.log_path,
            output_dir=self.out_dir,
            db_pattern=self.db_path,
            dry_run=dry_run,
        )
        out_path = engine.capture_snapshot(self.TRIGGER)
        with open(out_path, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        self.assertEqual(len(lines), 1, "one trigger must write exactly one JSONL line")
        return json.loads(lines[0])

    # (a) round-trip + the structured shape, at the three sites design §5.1 names
    def test_snapshot_round_trips_with_the_structured_probe_shape(self):
        record = self._capture()

        reparsed = json.loads(json.dumps(record))
        self.assertEqual(reparsed, record, "the record must survive a json round-trip")

        for holder, probe in (
            ("lock_holders", "fuser"),
            ("lock_holders", "lsof"),
            ("process_traces", "pidstat"),
            ("process_traces", "ps_aux_t"),
        ):
            with self.subTest(site=f"{holder}.{probe}"):
                value = reparsed[holder][probe]
                self.assertIsInstance(
                    value, dict,
                    f"{holder}.{probe} must be the structured probe result, not a bare string",
                )
                self.assertEqual(set(value), self.PROBE_KEYS)
                self.assertIn(value["status"], {"ok", "timeout", "missing", "error"})
                self.assertIsInstance(
                    value["elapsed_ms"], float,
                    "elapsed_ms is the measurement the old contract discarded",
                )

    def test_probes_sit_where_the_design_puts_them(self):
        # pidstat is a process trace, not a sysstat metric -- design §5.1 puts it
        # under `process_traces` and leaves `sysstat_metrics` holding `fd_count`
        # alone. Asserting both key SETS, so the move is a move and not a copy.
        record = self._capture()
        self.assertEqual(set(record["lock_holders"]), {"fuser", "lsof"})
        self.assertEqual(set(record["process_traces"]), {"pidstat", "ps_aux_t"})
        self.assertEqual(set(record["sysstat_metrics"]), {"fd_count"})
        self.assertIsInstance(record["sysstat_metrics"]["fd_count"], int)

    # (b) THE ANTI-VACUITY ROW: the casualty this task exists for
    def test_dry_run_fallbacks_fire_when_the_probe_binary_is_missing(self):
        # The production no-psmisc case, and the one a dict conversion breaks
        # silently. PATH is the stub dir ALONE, so fuser/lsof/pidstat are
        # genuinely absent and every probe comes back status="missing".
        os.environ["PATH"] = self.stub_dir
        record = self._capture(dry_run=True)

        self.assertTrue(record["dry_run"])
        for holder, probe, marker in (
            ("lock_holders", "fuser", "[dry-run] fuser simulated check OK"),
            ("lock_holders", "lsof", "[dry-run] lsof simulated check OK"),
            ("process_traces", "pidstat", "[dry-run] pidstat diagnostic snapshot OK"),
        ):
            with self.subTest(site=f"{holder}.{probe}"):
                value = record[holder][probe]
                self.assertIsInstance(value, dict)
                self.assertEqual(
                    value["status"], "missing",
                    "the real status must survive the fallback, not be overwritten by it",
                )
                # The same sentence names three fields, not one: `status`,
                # `elapsed_ms` and `error` are all "left untouched". Pinning
                # only the status reads like pinning all three -- zeroing
                # elapsed_ms or dropping error inside the fallback kept the
                # whole suite green while the JSONL record on disk lost the
                # measurement. Step 4 exports
                # plex_watchdog_probe_duration_seconds out of elapsed_ms, and
                # `error` is the only place the reason survives once `output`
                # has been replaced by simulated text.
                self.assertGreater(
                    value["elapsed_ms"], 0.0,
                    f"the fallback overwrote {probe}'s measured elapsed_ms",
                )
                self.assertIsNotNone(
                    value["error"],
                    f"the fallback dropped {probe}'s error, so the record cannot "
                    "say why the probe produced nothing",
                )
                self.assertIsNotNone(
                    value["output"],
                    f"--dry-run stopped simulating: {holder}.{probe} has no fallback text",
                )
                self.assertIn(
                    marker, value["output"],
                    f"the dry-run fallback for {probe} never fired",
                )

    def test_dry_run_fallback_fires_for_a_probe_that_ran_and_said_nothing(self):
        # The arm the string test also covered (`fuser_out == ""`): the probe is
        # PRESENT and exits 1 with empty output, which is what real fuser/lsof do
        # when nothing holds the file. status is "ok", so a status-only rewrite
        # drops this case -- it must not.
        for name in ("fuser", "lsof", "pidstat", "ps"):
            self._install_silent_stub(name)
        os.environ["PATH"] = self.stub_dir
        record = self._capture(dry_run=True)

        for holder, probe, marker in (
            ("lock_holders", "fuser", "[dry-run] fuser simulated check OK"),
            ("lock_holders", "lsof", "[dry-run] lsof simulated check OK"),
            ("process_traces", "pidstat", "[dry-run] pidstat diagnostic snapshot OK"),
        ):
            with self.subTest(site=f"{holder}.{probe}"):
                value = record[holder][probe]
                self.assertEqual(value["status"], "ok", "the stub ran, so the probe is ok")
                self.assertIn(
                    marker, value["output"] or "",
                    f"an empty-output probe must still get {probe}'s dry-run fallback",
                )

    def test_a_probe_that_ran_and_spoke_keeps_its_own_output_under_dry_run(self):
        # The predicate's DISCRIMINATING half, and the arm the other three rows
        # leave open: they pin that the fallback FIRES (missing; ok-but-empty) and
        # that it never fires in a LIVE capture. None of them pins that it does
        # NOT fire when the probe ran and SPOKE -- so substituting unconditionally
        # (`if True:`) keeps the whole suite green while `--dry-run` overwrites
        # real fuser/lsof output with a simulated line that still carries
        # status="ok", a real elapsed_ms and error=None. That is a fabrication
        # wearing every mark of a probe that actually ran, which is this row's own
        # failure class inverted; the helper's docstring promises it cannot happen.
        # Step 1c installs psmisc and makes real fuser output the demo path.
        for name in self.SPEAKING_STUBS:
            self._install_speaking_stub(name)
        os.environ["PATH"] = self.stub_dir
        record = self._capture(dry_run=True)

        self.assertTrue(record["dry_run"], "this arm must be exercised under --dry-run")
        for holder, probe in (
            ("lock_holders", "fuser"),
            ("lock_holders", "lsof"),
            ("process_traces", "pidstat"),
        ):
            with self.subTest(site=f"{holder}.{probe}"):
                value = record[holder][probe]
                self.assertEqual(value["status"], "ok", "the stub ran and exited 0")
                output = value["output"] or ""
                self.assertIn(
                    self.SPEAKING_STUBS[probe].split("\n")[0], output,
                    f"{holder}.{probe} lost the output of a probe that actually ran",
                )
                self.assertNotIn(
                    "[dry-run]", json.dumps(value),
                    f"{holder}.{probe} overwrote a real probe's output with simulated text",
                )

    def test_no_fallback_text_leaks_into_a_live_capture(self):
        # The fallback is dry-run ONLY. Without this, a rewrite that fires the
        # fallback unconditionally would pass every row above.
        os.environ["PATH"] = self.stub_dir
        record = self._capture(dry_run=False)

        self.assertFalse(record["dry_run"])
        for holder, probe in (
            ("lock_holders", "fuser"),
            ("lock_holders", "lsof"),
            ("process_traces", "pidstat"),
        ):
            with self.subTest(site=f"{holder}.{probe}"):
                self.assertNotIn(
                    "[dry-run]", json.dumps(record[holder][probe]),
                    f"{holder}.{probe} fabricated probe output in a live capture",
                )

    # (c) additive-only at the top level: 448 KB of captures already on disk
    def test_top_level_keys_are_exactly_the_eleven_after_step_3(self):
        record = self._capture()
        self.assertEqual(
            set(record), self.TOP_LEVEL_KEYS,
            "Step 2d added hold_site/live_connections and Step 3a HAS NOW added "
            "sqlite -- the widening this message used to anticipate has landed, so "
            "a further ADDITION is a deliberate edit at TOP_LEVEL_KEYS and a "
            "REMOVAL breaks the captures already written",
        )

    def test_the_eight_keys_already_on_disk_are_all_still_written(self):
        # The removal half of the sentence above, stated as its own row so that
        # widening the set can never be mistaken for satisfying it. Measured at
        # this turn over /tmp/plex-logs/plex_blip_diagnostics_*.jsonl: 34 records,
        # 448,202 bytes, THREE distinct trigger_event values (STREAM_DROP 13,
        # SLOW_QUERY 15, TX_STALL 6) and ONE key set across all 34.
        record = self._capture()
        self.assertTrue(
            self.KEYS_ALREADY_ON_DISK.issubset(set(record)),
            "dropping a key the 34 captures on disk carry breaks every consumer of them; "
            f"missing: {sorted(self.KEYS_ALREADY_ON_DISK - set(record))}",
        )


class TestSqliteWalStateCapture(unittest.TestCase):
    """Step 3a — `_wal_state` and the snapshot's `sqlite` block (design C1.4).

    Design C1.4 buys the leading indicator for the price of three `os.stat`
    calls: no connection, no lock, no writer. That CHEAPNESS is the whole
    licence for putting it on the capture path, so it is asserted against the
    shipped function's AST here rather than promised in a docstring.

    THE ABSENT-VS-NULL CHOICE, MEASURED RATHER THAN INHERITED. plan.md:165-166
    says a missing WAL means "the `sqlite` block is omitted and the snapshot is
    still written", which is ambiguous between dropping the top-level key and
    dropping the inner figures. Censused at this turn over
    /tmp/plex-logs/plex_blip_diagnostics_*.jsonl: 34 records, 448,202 bytes,
    THREE trigger_event values (STREAM_DROP 13, SLOW_QUERY 15, TX_STALL 6) and
    exactly ONE top-level key set. Homogeneity is the only invariant that corpus
    actually has, so the top-level key is ALWAYS PRESENT -- and the same reader
    argument applies one level down, since `rec["sqlite"]["wal_bytes"]` taken as
    a column would KeyError on exactly the records the fault makes interesting.
    So both levels are always present and a file that is not there reads `None`.

    `None` is load-bearing and NOT a spelling of zero: a checkpointed WAL is
    genuinely 0 bytes and healthy, while an absent one means WAL mode is off or
    was never entered. `test_an_absent_wal_is_not_a_zero_byte_wal` is the row
    that refuses to let those two collapse into each other.
    """

    WAL_KEYS = {"db_bytes", "wal_bytes", "shm_bytes", "wal_ratio"}

    # Mutually distinct on purpose, and distinct from each other's ratio too:
    # equal fixtures let a transposed column pass by coincidence, which is the
    # single most-charged defect in this objective.
    DB_PAYLOAD = b"SQLite format 3\x00" + b"\xa5" * 4080     # 4096
    WAL_PAYLOAD = b"\xde\xad\xbe\xef" * 256                  # 1024
    SHM_PAYLOAD = b"\x5c" * 512                              # 512

    TRIGGER_LINE = (
        "Aug 04, 2026 06:58:11.899 [101] WARN - Took too long (0.120000 seconds) "
        "to start a transaction on StatisticsBandwidth.cpp:110"
    )

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="plex_watchdog_wal_")
        self.log_path = os.path.join(self.test_dir, "mock_plex.log")
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Aug 04, 2026 06:57:00.000 [100] INFO - Server starting up\n")
        self.out_dir = os.path.join(self.test_dir, "diagnostics")
        self.db_path = os.path.join(self.test_dir, "com.plexapp.plugins.library.db")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _write(self, path: str, payload: bytes) -> int:
        """Write a fixture and read its size back OFF THE ARTIFACT.

        `os.path.getsize` is a deliberately DIFFERENT spelling from the module's
        `os.stat(...).st_size`, and it is cross-checked against the payload
        length, so the expected figure is never a number this file hardcodes.
        """
        with open(path, "wb") as f:
            f.write(payload)
        size = os.path.getsize(path)
        self.assertEqual(size, len(payload), "fixture did not land at its own length")
        return size

    def _capture(self, db_pattern: str, dry_run: bool = True) -> dict:
        engine = watchdog.WatchdogEngine(
            log_path=self.log_path,
            output_dir=self.out_dir,
            db_pattern=db_pattern,
            dry_run=dry_run,
        )
        out_path = engine.capture_snapshot(
            {"event_type": "TX_STALL", "delay_ms": 120.0, "line": self.TRIGGER_LINE}
        )
        with open(out_path, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        self.assertEqual(len(lines), 1, "one trigger must write exactly one JSONL line")
        return json.loads(lines[0])

    # -- the function itself ------------------------------------------------

    def test_wal_state_reports_every_column_and_the_derived_ratio(self):
        db = self._write(self.db_path, self.DB_PAYLOAD)
        wal = self._write(self.db_path + "-wal", self.WAL_PAYLOAD)
        shm = self._write(self.db_path + "-shm", self.SHM_PAYLOAD)
        self.assertEqual(
            len({db, wal, shm}), 3,
            "the three fixtures must be MUTUALLY DISTINCT or a swapped column "
            f"is invisible: db={db} wal={wal} shm={shm}",
        )

        state = watchdog._wal_state(self.db_path)
        self.assertEqual(set(state), self.WAL_KEYS)
        self.assertEqual(state["db_bytes"], db)
        self.assertEqual(state["wal_bytes"], wal)
        self.assertEqual(state["shm_bytes"], shm)
        self.assertEqual(state["wal_ratio"], wal / db)

        # Anti-vacuity: the ratio must be a RATIO, not a fourth copy of a count.
        self.assertNotIn(
            state["wal_ratio"], {db, wal, shm},
            "wal_ratio coincides with a raw byte count, so the row cannot tell a "
            "real quotient from a mislabelled column",
        )

    def test_an_absent_wal_is_not_a_zero_byte_wal(self):
        # The reason the missing case is `None` and not 0. A checkpointed WAL is
        # genuinely zero bytes and HEALTHY; an absent one means WAL mode is off.
        # Collapsing them would make the Step 3b size audit unreadable.
        self._write(self.db_path, self.DB_PAYLOAD)
        absent = watchdog._wal_state(self.db_path)
        self.assertIsNone(absent["wal_bytes"], "an absent -wal must not report a size")
        self.assertIsNone(absent["wal_ratio"], "no WAL means no ratio, not a zero one")

        zero = self._write(self.db_path + "-wal", b"")
        checkpointed = watchdog._wal_state(self.db_path)
        self.assertEqual(checkpointed["wal_bytes"], zero)
        self.assertEqual(checkpointed["wal_ratio"], 0.0)

        self.assertNotEqual(
            absent["wal_bytes"], checkpointed["wal_bytes"],
            "an absent WAL and a checkpointed one must be distinguishable",
        )

    def test_a_zero_byte_database_beside_a_live_wal_does_not_divide(self):
        # The DENOMINATOR guard, armed. Found by mutation, not by inspection:
        # deleting `and db_bytes` from the ratio left every other row in this
        # class green (logs/builder-3a-mutants.log, C9), and the fault it hides
        # is not cosmetic -- it is a ZeroDivisionError raised from inside
        # capture_snapshot, which loses the entire snapshot. That is exactly the
        # trade plan.md:165-166 forbids.
        #
        # Reachable two ways: SQLite leaves a zero-byte database during creation,
        # and a database removed without its sidecars leaves the -wal with
        # nothing to divide by.
        zero_db = self._write(self.db_path, b"")
        wal = self._write(self.db_path + "-wal", self.WAL_PAYLOAD)

        state = watchdog._wal_state(self.db_path)
        self.assertEqual(state["db_bytes"], zero_db)
        self.assertEqual(state["wal_bytes"], wal)
        self.assertIsNone(
            state["wal_ratio"],
            "a zero-byte database has no ratio to report, and dividing by it "
            "raises from the capture path",
        )

        # The other direction: a WAL whose database is gone entirely.
        os.remove(self.db_path)
        orphaned = watchdog._wal_state(self.db_path)
        self.assertIsNone(orphaned["db_bytes"])
        self.assertEqual(orphaned["wal_bytes"], wal)
        self.assertIsNone(orphaned["wal_ratio"])

        # And the whole thing survives the real capture path.
        self._write(self.db_path, b"")
        record = self._capture(self.db_path + "*")
        self.assertEqual(json.loads(json.dumps(record)), record)
        self.assertIsNone(record["sqlite"]["wal_ratio"])

    def test_wal_state_opens_no_connection_and_spawns_no_process(self):
        # design C1.4's entire claim is that this is cheap enough to run on every
        # capture. Pinned to the shipped AST so a later "just one quick PRAGMA"
        # reds here instead of quietly taking a lock on the blip path.
        tree = ast.parse(inspect.getsource(watchdog._wal_state))
        called = {
            ast.unparse(node.func)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
        }
        forbidden = sorted(
            c for c in called
            if any(
                token in c.lower()
                for token in ("sqlite3", "subprocess", "_run_cmd", "connect", "popen", "system")
            )
        )
        self.assertEqual(
            forbidden, [],
            f"_wal_state must take no lock and spawn no process, but calls: {forbidden}",
        )
        self.assertIn(
            "os.stat", called,
            "design C1.4 names os.stat as the mechanism; asserting the absence of "
            "the expensive spellings proves nothing if the cheap one is gone too",
        )

    # -- the block inside the record ----------------------------------------

    def test_the_snapshot_sqlite_block_carries_the_measured_byte_counts(self):
        # Driven through the SHIPPED glob shape (`...db*`), which matches the db,
        # the -wal and the -shm. glob order is filesystem order, so this is also
        # the row that catches picking `matched_dbs[0]` and calling it the db.
        db = self._write(self.db_path, self.DB_PAYLOAD)
        wal = self._write(self.db_path + "-wal", self.WAL_PAYLOAD)
        shm = self._write(self.db_path + "-shm", self.SHM_PAYLOAD)

        record = self._capture(self.db_path + "*")
        block = record["sqlite"]
        self.assertEqual(set(block), self.WAL_KEYS)
        self.assertEqual(block["db_bytes"], db)
        self.assertEqual(block["wal_bytes"], wal)
        self.assertEqual(block["shm_bytes"], shm)
        self.assertEqual(block["wal_ratio"], wal / db)

    def test_the_base_database_is_chosen_by_name_not_by_glob_position(self):
        # glob order is FILESYSTEM order, so a row that merely creates the three
        # files and hopes scores positional selection by coin flip. The match set
        # is handed over in a controlled order instead, with the database LAST
        # and a `-journal` sidecar in front of it -- `...library.db*` sweeps that
        # up too, so excluding only -wal/-shm is not the same as picking the db.
        db = self._write(self.db_path, self.DB_PAYLOAD)
        wal = self._write(self.db_path + "-wal", self.WAL_PAYLOAD)
        self._write(self.db_path + "-shm", self.SHM_PAYLOAD)
        self._write(self.db_path + "-journal", b"\x17" * 77)

        ordered = [
            self.db_path + "-wal",
            self.db_path + "-shm",
            self.db_path + "-journal",
            self.db_path,
        ]

        class _OrderedGlob:
            @staticmethod
            def glob(_pattern):
                return list(ordered)

        real_glob = watchdog.glob
        watchdog.glob = _OrderedGlob
        try:
            record = self._capture(self.db_path + "*")
        finally:
            watchdog.glob = real_glob

        self.assertEqual(
            record["sqlite"]["db_bytes"], db,
            "the base database must be selected by name; this match set puts three "
            "sidecars ahead of it, so a positional pick reports one of those",
        )
        self.assertEqual(record["sqlite"]["wal_bytes"], wal)

    def test_a_missing_wal_still_writes_a_snapshot_that_round_trips(self):
        # plan.md:165-166 -- "a nice-to-have must never abort a capture".
        self._write(self.db_path, self.DB_PAYLOAD)
        self.assertFalse(os.path.exists(self.db_path + "-wal"))

        record = self._capture(self.db_path + "*")
        self.assertEqual(json.loads(json.dumps(record)), record)
        self.assertIn(
            "sqlite", record,
            "the top-level key is homogeneous across the 34 captures' successors; "
            "'omitted' is the inner figures reading null, not the block vanishing",
        )
        self.assertEqual(set(record["sqlite"]), self.WAL_KEYS)
        self.assertEqual(record["sqlite"]["db_bytes"], os.path.getsize(self.db_path))
        self.assertIsNone(record["sqlite"]["wal_bytes"])
        self.assertIsNone(record["sqlite"]["shm_bytes"])
        self.assertIsNone(record["sqlite"]["wal_ratio"])

    def test_a_pattern_matching_nothing_still_writes_the_snapshot(self):
        # The `targets = [self.db_pattern]` fallback at the resolved-glob site
        # hands an UNEXPANDED pattern downstream. Statting a literal "*" must
        # read as absent, never as a crash that loses the capture.
        missing = os.path.join(self.test_dir, "no-such-database.db*")
        record = self._capture(missing)
        self.assertEqual(json.loads(json.dumps(record)), record)
        self.assertEqual(set(record["sqlite"]), self.WAL_KEYS)
        self.assertEqual(
            {v for v in record["sqlite"].values()}, {None},
            "no database matched, so every figure must be null rather than zero",
        )

    def test_a_directory_where_the_wal_should_be_does_not_lose_the_capture(self):
        # Degenerate shapes the real host can produce. A directory stats fine and
        # a dangling symlink does not; neither may abort the snapshot.
        self._write(self.db_path, self.DB_PAYLOAD)
        os.makedirs(self.db_path + "-wal", exist_ok=True)
        os.symlink(os.path.join(self.test_dir, "gone"), self.db_path + "-shm")

        record = self._capture(self.db_path + "*")
        self.assertEqual(json.loads(json.dumps(record)), record)
        self.assertEqual(set(record["sqlite"]), self.WAL_KEYS)
        self.assertEqual(record["sqlite"]["db_bytes"], os.path.getsize(self.db_path))
        self.assertIsNone(
            record["sqlite"]["shm_bytes"], "a dangling symlink must read as absent"
        )


class TestModuleLatencyBoundIsTrue(unittest.TestCase):
    """Raising a timeout retires a latency budget, and the module header is where
    that budget is written down.

    The header's `<500ms` claim was already false before Step 1a (measured 2011.75 ms
    at 5c9a830, 4x over), so this row did not create the falsehood. What it created is
    the CONTRADICTION: `_run_cmd`'s own docstring now names 0.5s as the retired number
    while the header still advertises it as the bound. One file, one figure, two
    answers. These tests pin the header to the code instead of to a literal, so the
    next person to touch the default cannot leave the two disagreeing again.

    Round 2 added the two halves the first pass missed. Sweeping the retired NUMBER
    without sweeping the budget WORD only moves the contradiction: the header's new
    "bounded, not instant" is what converts every surviving "instantaneous" in the
    file from quietly stale into a live self-contradiction, so the word is censused
    here too. And pinning the two INPUTS to a bound does not pin the BOUND -- with
    only the timeout and the count asserted, deleting ", so 8.0s worst case" from
    the header outright was GREEN 16/16 (logs/critic-5507-r2-header-bound-hole.py),
    and that product is the one number an operator actually reads.

    Round 3 asserted that product, which is one layer better and still not the
    bound: `probes * default` equals what the code delivers only if no call site
    overrides the timeout and every call is spelled `_run_cmd([` on one line. With
    the product asserted, giving lsof the per-probe override `_run_cmd`'s own
    docstring advertises was GREEN with the header claiming 8.0s against a true
    11.0s, and a fifth probe spelled either through a variable or across lines was
    GREEN against a true 10.0s (logs/critic-5507-r3-bound-derivation.py). The bound
    is now summed per call site off the AST, so the guard computes it the way the
    code does; logs/builder-5507-r4-guard-closes.py scores those three RED here and
    GREEN again once the header is corrected to match.

    That sum is not merely a better formula -- it is the number the code burns.
    With every probe blocked, the real capture_snapshot measures 8015.11 ms here;
    give lsof the 5.0s override and it measures 11017.88 ms against a derivation
    that moved to exactly 11.0s, while `probes * default` stays at 8.0s
    (logs/builder-5507-r4-bound-is-measured.py).
    """

    def _module_source(self):
        return pathlib.Path(inspect.getsourcefile(watchdog)).read_text(encoding="utf-8")

    def _effective_probe_bound(self):
        """Derive the worst case the way the CODE computes it: walk every call to
        `_run_cmd` and sum that call's OWN effective timeout.

        `probes * default` is the product of two inputs, not the bound. It equals
        the delivered bound only under two things the code does not enforce: that
        no call site overrides the timeout, and that every call is spelled
        `_run_cmd([` on one line. `_run_cmd`'s own docstring advertises the
        override, and a formatter may rewrap any of these calls at any time.
        Reading the AST is override-aware and spelling-independent, so what comes
        back is the bound itself and there is nothing left over to pin.

        A timeout that is not a literal makes the bound UNDERIVABLE, and an
        underivable bound may not be certified: those sites come back named, so
        the caller fails loudly instead of silently crediting the default.

        Returns (call_sites, worst_case_seconds, underivable_sites).
        """
        default = inspect.signature(watchdog._run_cmd).parameters["timeout"].default
        sites, worst_case, underivable = 0, 0.0, []
        for node in ast.walk(ast.parse(self._module_source())):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node.func, "id", None) != "_run_cmd":
                continue
            sites += 1
            # Both spellings of an override: the advertised kwarg, and the
            # second positional the signature also accepts.
            override = next(
                (kw.value for kw in node.keywords if kw.arg == "timeout"),
                node.args[1] if len(node.args) > 1 else None,
            )
            if override is None:
                worst_case += default
            elif isinstance(override, ast.Constant):
                worst_case += override.value
            else:
                underivable.append(f":{node.lineno} {ast.unparse(override)}")
        return sites, worst_case, underivable

    def test_header_does_not_advertise_the_retired_500ms_bound(self):
        # Flip the guard's polarity, never delete it: the header must not claim a
        # bound the code cannot honour. 500ms is now unreachable -- ONE probe may
        # take 2.0s -- so the string must be gone from the module docstring.
        header = inspect.getdoc(watchdog) or ""
        self.assertNotIn(
            "<500ms", header,
            "module docstring still advertises the retired 0.5s probe budget; "
            "capture_snapshot's measured worst case is 8014.65 ms (16x)",
        )

    def test_header_states_the_bound_the_code_actually_delivers(self):
        # Derived, not hardcoded. A fifth probe or a new default must force the
        # header to move in the same commit rather than silently going stale.
        probes, _bound, _underivable = self._effective_probe_bound()
        default = inspect.signature(watchdog._run_cmd).parameters["timeout"].default
        self.assertEqual(probes, 4, "capture_snapshot's serial probe count")

        header = inspect.getdoc(watchdog) or ""
        self.assertIn(
            f"{default}s", header,
            "module docstring must name the per-probe timeout it actually uses",
        )
        self.assertIn(
            "four probes serial", header,
            "module docstring must disclose that the probes run serially, since "
            f"that is what makes the delivered bound {probes} x {default}s",
        )

    def test_header_names_the_bound_each_call_site_actually_adds_up_to(self):
        # The bound an operator quotes, derived the way the code computes it --
        # summed per call site, never `probes * default` and never 8000. A fifth
        # probe, a changed default, a formatter rewrapping one of these calls, or
        # lsof taking the per-probe override its own docstring advertises must all
        # move this sentence in the same commit.
        probes, worst_case, underivable = self._effective_probe_bound()
        self.assertEqual(
            underivable, [],
            "a probe's timeout is not a literal, so the module's worst case cannot "
            "be derived and the header's claim cannot be certified: "
            + " | ".join(underivable),
        )

        header = inspect.getdoc(watchdog) or ""
        self.assertIn(
            f"{worst_case}s worst case", header,
            f"module docstring must name the bound it delivers -- {probes} serial "
            f"probes summing to {worst_case}s at their own effective timeouts",
        )

    def test_no_surviving_docstring_calls_the_bounded_snapshot_instantaneous(self):
        # Census the budget WORD across the whole file, not just the retired
        # number. The header owns the only licensed occurrence -- the one that
        # denies it -- because a sentence saying "not instant" is precisely what
        # arms every copy of the word that outlives it 358 lines below.
        source = self._module_source()
        tree = ast.parse(source)
        self.assertIsInstance(
            tree.body[0], ast.Expr, "module docstring must be the first statement"
        )
        header_lines = range(tree.body[0].lineno, tree.body[0].end_lineno + 1)

        offenders = [
            f":{lineno} {line.strip()}"
            for lineno, line in enumerate(source.splitlines(), start=1)
            if "instant" in line.lower() and lineno not in header_lines
        ]
        self.assertEqual(
            offenders, [],
            "the module header states the snapshot is bounded and NOT instant, so "
            "no other line may still call it instantaneous: " + " | ".join(offenders),
        )


class TestTxHeldAndLiveConnections(unittest.TestCase):
    """The holder-side signal and the saturation counter, Step 2a.

    Every fixture below is a VERBATIM line from
    /tmp/plex-logs/2026-08-07/"Plex Media Server.log", copied in as an inline
    literal. It is not read at test time on purpose: /tmp is outside the repo,
    absent on CT 110 and in any fresh checkout, and this repo already carries
    two tests that go vacuously green from exactly that mistake
    (test_analyze_plex_blips.py:150 and :219 read a path that does not exist,
    print SKIP, and assert nothing inside a passing gate).

    Corpus counts, measured at this turn over that file: 42 lines match
    "Held transaction", 32 match "Took too long", 2 match
    "StatisticsManager.cpp:288", and 0 of the 42 Held lines carry a "(N live)"
    count -- which is why the TX_HELD dict has no live_connections key.
    """

    # :3284 -- the genuine first holder of the 06:37 blip.
    HELD_STATISTICS_MANAGER = (
        "Aug 07, 2026 06:37:33.273 [132687902931768] WARN - Held transaction for "
        "too long (/home/runner/_work/plex-media-server/plex-media-server/"
        "Statistics/StatisticsManager.cpp:288): 0.540000 seconds"
    )
    # :3294 -- same message, but a [Req#...] prefix sits between "WARN - " and it.
    HELD_METADATA_ITEM_SETTING = (
        "Aug 07, 2026 06:37:36.346 [132687881837368] WARN - [Req#8ec76] Held "
        "transaction for too long (/home/runner/_work/plex-media-server/"
        "plex-media-server/Library/MetadataItemSetting.cpp:459): 0.310000 seconds"
    )
    # :3352 and :3358 -- the waiter side, which must stay TX_STALL untouched.
    STALL_STATISTICS_BANDWIDTH = (
        "Aug 07, 2026 06:38:22.285 [132687915588408] WARN - Took too long "
        "(0.110000 seconds) to start a transaction on /home/runner/_work/"
        "plex-media-server/plex-media-server/Statistics/StatisticsBandwidth.cpp:110"
    )
    STALL_STATISTICS_MEDIA = (
        "Aug 07, 2026 06:38:27.179 [132687883946808] WARN - [Req#8ecac] Took too "
        "long (0.160000 seconds) to start a transaction on /home/runner/_work/"
        "plex-media-server/plex-media-server/Statistics/StatisticsMedia.cpp:99"
    )
    # :3553 and :3552 -- saturation at 06:40:46, one Request:, one Completed:.
    REQUEST_13_LIVE = (
        "Aug 07, 2026 06:40:46.096 [132687877618488] DEBUG - Request: "
        "[192.168.1.111:41052 (Subnet)] GET /status/sessions (13 live) #8ecec "
        "Signed-in Token (masyllis)"
    )
    COMPLETED_CLOSE_13_LIVE = (
        "Aug 07, 2026 06:40:46.067 [132688108632888] DEBUG - Completed after "
        "connection close: [192.168.1.208:43910] 200 GET /video/:/transcode/"
        "universal/session/f0ccf4d2-7bf1-47fd-bf19-6d85f7ed4e27/base/03075.ts "
        "(13 live) #8ece3 TLS 39727ms 2621440 bytes (pipelined: 1460)"
    )
    # :3236-ish -- a Completed: line that DOES trigger, and carries a count.
    COMPLETED_SLOW_4_LIVE = (
        "Aug 07, 2026 06:37:39.377 [132688110742328] DEBUG - Completed: "
        "[192.168.1.208:43890] 200 GET /:/timeline?key=%2Flibrary%2Fmetadata%2F378"
        "&ratingKey=378&playQueueItemID=15310&duration=5568563&time=3039038"
        "&playbackTime=2001342&hasMDE=1&context=home%3AcontinueWatching&row=0"
        "&col=0&state=playing (4 live) #8ec76 TLS GZIP 4977ms 820 bytes "
        "(pipelined: 144)"
    )

    def test_the_genuine_holder_line_is_tx_held_with_the_measured_delay(self):
        res = watchdog.check_trigger(self.HELD_STATISTICS_MANAGER, threshold_ms=500.0)
        self.assertIsNotNone(res, "the 06:37:33.273 holder line must trigger")
        self.assertEqual(res["event_type"], "TX_HELD")
        # 0.540000 s x 1000, the same seconds->ms conversion TX_STALL uses at :53.
        self.assertEqual(res["delay_ms"], 540.0)
        self.assertEqual(res["line"], self.HELD_STATISTICS_MANAGER)

    def test_hold_site_is_basenamed_not_the_ci_build_path(self):
        # THE ONE THAT LOOKS RIGHT AND IS WRONG. The parenthesised group in the
        # raw line is a 90-character CI build path from the Plex build runner.
        # Capturing it verbatim yields a plausible-looking hold_site that fails
        # the acceptance criterion, so this is asserted from both directions:
        # the exact value, and the absence of the path that a verbatim capture
        # would have left behind.
        res = watchdog.check_trigger(self.HELD_STATISTICS_MANAGER, threshold_ms=500.0)
        self.assertEqual(res["hold_site"], "StatisticsManager.cpp:288")
        self.assertNotIn("/", res["hold_site"], "hold_site must carry no path separator")
        self.assertNotIn("/home/runner", res["hold_site"])
        self.assertNotIn("plex-media-server", res["hold_site"])

    def test_a_req_prefixed_holder_line_still_yields_its_site(self):
        # check_trigger receives the WHOLE line, and this world puts [Req#8ec76]
        # between "WARN - " and the message -- anything anchored on the "WARN - "
        # boundary misses all of it.
        res = watchdog.check_trigger(self.HELD_METADATA_ITEM_SETTING, threshold_ms=500.0)
        self.assertIsNotNone(res, "the [Req#...] prefixed holder line must trigger")
        self.assertEqual(res["event_type"], "TX_HELD")
        self.assertEqual(res["delay_ms"], 310.0)
        self.assertEqual(res["hold_site"], "MetadataItemSetting.cpp:459")

    def test_tx_held_carries_exactly_the_keys_step_2b_must_mirror(self):
        # This row DEFINES the vocabulary that Step 2b mirrors into the analyzer
        # and Step 2c reports on. Pinning the key SET is what stops two hats
        # inventing two spellings with nothing going red. live_connections is
        # absent by measurement, not by omission: 0 of the corpus's 42 Held
        # lines carry a "(N live)" count.
        res = watchdog.check_trigger(self.HELD_STATISTICS_MANAGER, threshold_ms=500.0)
        self.assertEqual(
            set(res), {"event_type", "delay_ms", "hold_site", "line"},
            f"TX_HELD vocabulary drifted: {sorted(res)}",
        )

    def test_a_real_waiter_line_is_still_tx_stall_unchanged(self):
        # REGRESSION. Both are real corpus lines, one bare and one [Req#...]
        # prefixed, and neither may acquire a hold_site -- TX_STALL names where
        # the waiter gave up, which is not the holder's site.
        for label, line, delay in (
            ("bare", self.STALL_STATISTICS_BANDWIDTH, 110.0),
            ("[Req#8ecac]", self.STALL_STATISTICS_MEDIA, 160.0),
        ):
            with self.subTest(line=label):
                res = watchdog.check_trigger(line, threshold_ms=500.0)
                self.assertIsNotNone(res, f"{label} waiter line must still trigger")
                self.assertEqual(res["event_type"], "TX_STALL")
                self.assertEqual(res["delay_ms"], delay)
                self.assertNotIn("hold_site", res)

    def test_the_two_transaction_matchers_are_lexically_disjoint(self):
        # The regression above is winnable WITHOUT reordering branches, and this
        # is the reason: the holder text contains "too long" but never "Took too
        # long", and the waiter text never contains "Held transaction". If a
        # future edit needs the branches in a particular order to pass, the
        # matcher is wrong -- so the disjointness is asserted directly rather
        # than being left as an argument in a comment.
        for held in (self.HELD_STATISTICS_MANAGER, self.HELD_METADATA_ITEM_SETTING):
            self.assertIn("Held transaction for too long", held)
            self.assertNotIn("Took too long", held)
            self.assertNotIn("to start a transaction", held)
        for stall in (self.STALL_STATISTICS_BANDWIDTH, self.STALL_STATISTICS_MEDIA):
            self.assertIn("Took too long", stall)
            self.assertNotIn("Held transaction", stall)

    def test_live_connections_reads_the_count_off_a_real_request_line(self):
        self.assertEqual(watchdog.extract_live_connections(self.REQUEST_13_LIVE), 13)

    def test_live_connections_reads_the_count_off_a_real_completed_line(self):
        self.assertEqual(
            watchdog.extract_live_connections(self.COMPLETED_CLOSE_13_LIVE), 13
        )

    def test_live_connections_is_an_int_not_the_matched_text(self):
        # "13" would satisfy an equality against 13 in no Python at all, but it
        # would satisfy a truthiness or a str() comparison downstream in 2b/2c.
        for line in (self.REQUEST_13_LIVE, self.COMPLETED_CLOSE_13_LIVE):
            with self.subTest(line=line[:60]):
                self.assertIsInstance(watchdog.extract_live_connections(line), int)

    def test_live_connections_is_none_when_the_line_carries_no_count(self):
        for line in (self.HELD_STATISTICS_MANAGER, self.STALL_STATISTICS_BANDWIDTH):
            with self.subTest(line=line[:60]):
                self.assertIsNone(watchdog.extract_live_connections(line))

    def test_live_connections_rides_on_a_trigger_that_actually_fires(self):
        # The two 06:40:46 lines above carry a count but trigger nothing --
        # "Completed after connection close:" is not "Completed:", and a
        # Request: line has no rule at all. This one is a real Completed: line
        # over the 500 ms threshold that ALSO carries a count, which is the only
        # world where the number reaches a consumer.
        res = watchdog.check_trigger(self.COMPLETED_SLOW_4_LIVE, threshold_ms=500.0)
        self.assertIsNotNone(res, "a 4977 ms Completed: line must trigger")
        self.assertEqual(res["event_type"], "SLOW_QUERY")
        self.assertEqual(res["delay_ms"], 4977.0)
        self.assertEqual(res["live_connections"], 4)

    def test_the_two_saturation_lines_do_not_themselves_trigger(self):
        # Guards the claim the test above rests on. If either of these ever
        # starts triggering, the "(N live)" extractor is no longer the only way
        # to see the count on them and this class is testing the wrong seam.
        for line in (self.REQUEST_13_LIVE, self.COMPLETED_CLOSE_13_LIVE):
            with self.subTest(line=line[:60]):
                self.assertIsNone(watchdog.check_trigger(line, threshold_ms=500.0))


class TestSnapshotCarriesHoldSiteAndLiveConnections(unittest.TestCase):
    """Step 2d — plan.md:95: "Writes `hold_site` and `live_connections` into the
    Step 1 snapshot structure."

    Step 2a put both on the TRIGGER dict; this row puts them in the ARTIFACT.
    Until it landed, the one capture Step 2a changes -- a holder line, which
    previously classified as nothing at all -- reached disk with its defining
    field missing, recoverable only by re-parsing `trigger_line`, where the site
    is still the 90-character CI build path.

    THE ABSENT CASE IS `None`, NOT A MISSING KEY, and that is the opposite of the
    trigger dict's choice (DEC-227, absent-not-None). Two different consumers:

      - The trigger dict is read by ONE caller in the same process, immediately,
        and `"hold_site" in trigger` is a question about the LINE.
      - The record is read by a human or a script over a growing pile of JSONL.
        Measured over the 448,202 bytes / 34 records already on disk: THREE
        distinct trigger_event values, ONE key set. Key homogeneity, not key
        presence, is the invariant that corpus actually has -- so absent-not-None
        would make the key set a function of trigger_event and break a consumer
        that reads a column across records. `rec["hold_site"] is None` says "this
        capture's trigger named no site" without a KeyError.

    Every fixture is REUSED from TestTxHeldAndLiveConnections rather than retyped:
    those literals are byte-identical members of the corpus, and a second copy is
    a second chance to mistype one into a synthesised fixture.

    The two rows that matter run the REAL CLI through live inotify, not
    `capture_snapshot` directly, because the eight-key fact this row overturns
    was measured on the production path.
    """

    FIXTURES = TestTxHeldAndLiveConnections
    # 0.540000 s -> ms, and the basename of the CI path, both pinned by Step 2a.
    HOLD_SITE = "StatisticsManager.cpp:288"

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="plex_watchdog_2d_")
        self.log_path = os.path.join(self.test_dir, "mock_plex.log")
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Aug 07, 2026 06:30:00.000 [100] INFO - Server starting up\n")
        self.out_dir = os.path.join(self.test_dir, "diagnostics")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _capture_via_real_cli(self, trigger_line: str) -> dict:
        """Drive the shipped CLI: live inotify, --dry-run, --max-triggers 1."""
        cmd = [
            sys.executable,
            str(WATCHDOG_SCRIPT),
            "--log-path", self.log_path,
            "--output-dir", self.out_dir,
            "--dry-run",
            "--max-triggers", "1",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(0.5)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(trigger_line + "\n")
            f.flush()
        stdout, stderr = proc.communicate(timeout=15)
        self.assertEqual(proc.returncode, 0, f"real CLI run failed: {stderr}\n{stdout}")

        out_files = list(pathlib.Path(self.out_dir).glob("*.jsonl"))
        self.assertEqual(len(out_files), 1, f"expected one JSONL file in {self.out_dir}")
        with open(out_files[0], "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        self.assertEqual(len(lines), 1, "one trigger must write exactly one JSONL line")
        return json.loads(lines[0])

    def test_a_real_holder_line_writes_hold_site_through_the_real_cli(self):
        record = self._capture_via_real_cli(self.FIXTURES.HELD_STATISTICS_MANAGER)

        self.assertEqual(record["trigger_event"], "TX_HELD")
        self.assertEqual(record["delay_ms"], 540.0)
        self.assertEqual(
            record["hold_site"], self.HOLD_SITE,
            "the capture Step 2a changes must name its code site in a FIELD, not "
            "only inside trigger_line's 90-character CI path",
        )
        # The site must be the basename form, not the raw path the line carries.
        self.assertIn(self.HOLD_SITE, record["trigger_line"].replace(
            "/home/runner/_work/plex-media-server/plex-media-server/Statistics/", ""
        ))
        self.assertNotIn("/", record["hold_site"])

    def test_a_real_slow_completed_line_with_a_count_writes_live_connections(self):
        record = self._capture_via_real_cli(self.FIXTURES.COMPLETED_SLOW_4_LIVE)

        self.assertEqual(record["trigger_event"], "SLOW_QUERY")
        self.assertEqual(record["delay_ms"], 4977.0)
        self.assertEqual(record["live_connections"], 4)
        self.assertIsInstance(
            record["live_connections"], int,
            "the count must survive JSON as a number, not the matched text",
        )

    def test_the_absent_case_is_a_null_value_and_the_key_set_never_varies(self):
        # A waiter line: no hold site (the holder is the other side of the same
        # stall) and no "(N live)" count -- 0 of the corpus's 42 Held lines and
        # neither waiter fixture carries one.
        record = self._capture_via_real_cli(self.FIXTURES.STALL_STATISTICS_BANDWIDTH)

        self.assertEqual(record["trigger_event"], "TX_STALL")
        for key in ("hold_site", "live_connections"):
            with self.subTest(key=key):
                self.assertIn(
                    key, record,
                    f"{key} must be PRESENT and null on a trigger that does not carry "
                    "it -- the 34 records on disk share one key set across three "
                    "trigger_event values, and that homogeneity is the invariant",
                )
                self.assertIsNone(record[key])

    def test_every_trigger_kind_writes_the_same_eleven_top_level_keys(self):
        # The homogeneity claim as a measurement rather than a sentence: one
        # record per branch this row can reach, key sets compared as sets.
        expected = TestSnapshotStructuredShape.TOP_LEVEL_KEYS
        seen = {}
        for name, line in (
            ("TX_HELD", self.FIXTURES.HELD_STATISTICS_MANAGER),
            ("SLOW_QUERY", self.FIXTURES.COMPLETED_SLOW_4_LIVE),
            ("TX_STALL", self.FIXTURES.STALL_STATISTICS_BANDWIDTH),
        ):
            with self.subTest(trigger_event=name):
                shutil.rmtree(self.out_dir, ignore_errors=True)
                record = self._capture_via_real_cli(line)
                self.assertEqual(record["trigger_event"], name)
                self.assertEqual(set(record), expected)
                seen[name] = set(record)
        self.assertEqual(
            len(set(frozenset(k) for k in seen.values())), 1,
            f"the key set must not be a function of trigger_event: {seen}",
        )

    def test_hold_site_is_read_from_the_trigger_and_not_re_derived(self):
        # A synthesised trigger carrying a site the LINE does not mention. If the
        # record re-parses trigger_line instead of reading the dict Step 2a
        # populates, the two spellings drift apart silently -- which is exactly
        # how 2b/2c could end up reporting a different site than the snapshot.
        engine = watchdog.WatchdogEngine(
            log_path=self.log_path,
            output_dir=self.out_dir,
            db_pattern=os.path.join(self.test_dir, "nonexistent.db"),
            dry_run=True,
        )
        out_path = engine.capture_snapshot({
            "event_type": "TX_HELD",
            "delay_ms": 1020.0,
            "line": "Aug 07, 2026 06:39:06.340 [1] WARN - Held transaction for too long (X): 1.020000 seconds",
            "hold_site": "MetadataItemSetting.cpp:459",
            "live_connections": 7,
        })
        with open(out_path, "r", encoding="utf-8") as f:
            record = json.loads(f.readline())
        self.assertEqual(record["hold_site"], "MetadataItemSetting.cpp:459")
        self.assertEqual(record["live_connections"], 7)


# ---------------------------------------------------------------------------
# Step 4a -- the Prometheus textfile emitter (design §5.2, plan.md Step 4).
#
# THE INSTRUMENT, AND WHY IT IS HAND-WRITTEN. plan.md's first Tests bullet names
# `prometheus_client.parser.text_string_to_metric_families`. That package is
# importable under NEITHER `.venv/bin/python` NOR `mise exec -- python`, and
# `pyproject.toml` is `dependencies = []` while `run_gate.py:54` runs every
# `scripts/test_*.py` as a standalone stdlib script under `sys.executable`
# (plan.md Step 4, premise 1). So the obligation stands and the instrument
# changes: a strict stdlib reader, written below.
#
# A parser written beside the writer it scores is worth NOTHING unless it can
# refuse. An acceptor that accepts exactly what the writer emits is a second
# spelling of the thing under test, which is the charge DEC-243 laid on
# re-spelling an Ansible `that:` expression in Python. So the parser is scored
# in both directions BEFORE it scores anything: it must accept a valid document
# this repo never writes, and it must refuse four named malformations, each one
# derived from a document that parses green by a SINGLE edit.
# ---------------------------------------------------------------------------

_METRIC_NAME_RE = re.compile(r"[a-zA-Z_:][a-zA-Z0-9_:]*")
_LABEL_NAME_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
_METRIC_TYPES = ("counter", "gauge", "histogram", "summary", "untyped")


class ExpositionError(ValueError):
    """Text that a Prometheus text-format parser would refuse."""


def _parse_label_value(line, i, lineno):
    """Read one quoted label value, honouring exactly the three escapes the
    exposition format defines (`\\\\`, `\\"`, `\\n`). An unescaped `"` ENDS the
    value here, which is what leaves the trailing garbage the caller rejects."""
    i += 1  # the opening quote
    out = []
    while i < len(line):
        c = line[i]
        if c == "\\":
            if i + 1 >= len(line):
                raise ExpositionError(f":{lineno} label value ends in a dangling escape")
            e = line[i + 1]
            if e == "n":
                out.append("\n")
            elif e in ('"', "\\"):
                out.append(e)
            else:
                raise ExpositionError(f":{lineno} unknown escape \\{e} in a label value")
            i += 2
            continue
        if c == '"':
            return "".join(out), i + 1
        out.append(c)
        i += 1
    raise ExpositionError(f":{lineno} unterminated label value")


def _parse_labels(line, i, lineno):
    """Read a `{k="v",...}` list. Rejects an unquoted value, a missing `=`, a
    duplicate key, and a list that does not close where it should."""
    labels = {}
    if i < len(line) and line[i] == "}":
        return labels, i + 1
    while True:
        m = _LABEL_NAME_RE.match(line, i)
        if not m:
            raise ExpositionError(f":{lineno} expected a label name at offset {i}")
        key = m.group(0)
        i = m.end()
        if i >= len(line) or line[i] != "=":
            raise ExpositionError(f":{lineno} label {key!r} carries no '='")
        i += 1
        if i >= len(line) or line[i] != '"':
            raise ExpositionError(f":{lineno} label {key!r} has an unquoted value")
        value, i = _parse_label_value(line, i, lineno)
        if key in labels:
            raise ExpositionError(f":{lineno} duplicate label {key!r}")
        labels[key] = value
        if i < len(line) and line[i] == ",":
            i += 1
            if i < len(line) and line[i] == "}":
                return labels, i + 1
            continue
        if i < len(line) and line[i] == "}":
            return labels, i + 1
        raise ExpositionError(
            f":{lineno} label list is not closed -- unescaped quote or stray text "
            f"at offset {i}: {line[i:]!r}"
        )


def _parse_sample(line, lineno):
    m = _METRIC_NAME_RE.match(line)
    if not m:
        raise ExpositionError(f":{lineno} line does not open with a metric name")
    name = m.group(0)
    i = m.end()
    labels = {}
    if i < len(line) and line[i] == "{":
        labels, i = _parse_labels(line, i + 1, lineno)
    rest = line[i:]
    if rest and not rest[0].isspace():
        raise ExpositionError(f":{lineno} metric name is not followed by whitespace")
    fields = rest.split()
    if not fields:
        raise ExpositionError(f":{lineno} sample carries no value")
    if len(fields) > 2:
        raise ExpositionError(f":{lineno} trailing text after the sample value")
    token = fields[0]
    # `float("1_0")` is 10.0 in Python and is not a sample value anywhere else.
    if "_" in token:
        raise ExpositionError(f":{lineno} {token!r} is not a sample value")
    try:
        value = float(token)
    except ValueError:
        raise ExpositionError(f":{lineno} {token!r} is not a float") from None
    if len(fields) == 2:
        try:
            int(fields[1])
        except ValueError:
            raise ExpositionError(f":{lineno} {fields[1]!r} is not a millisecond timestamp") from None
    return name, labels, value


def parse_exposition(text):
    """Strict, stdlib-only reader for the Prometheus text exposition format.

    Returns `{name: {"help": str|None, "type": str, "samples": [(labels, value)]}}`.
    Raises `ExpositionError` for a sample with no preceding `# TYPE`, a repeated
    `# HELP` or `# TYPE` for one name, an unknown metric type, a malformed label
    list, and a value that is not a float.
    """
    families = {}
    helps = {}
    for lineno, raw in enumerate(text.split("\n"), start=1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            parts = line.split(None, 3)
            if len(parts) >= 2 and parts[1] == "HELP":
                if len(parts) < 3:
                    raise ExpositionError(f":{lineno} '# HELP' names no metric")
                name = parts[2]
                if name in helps:
                    raise ExpositionError(f":{lineno} duplicate '# HELP' for {name!r}")
                helps[name] = parts[3] if len(parts) > 3 else ""
            elif len(parts) >= 2 and parts[1] == "TYPE":
                if len(parts) < 4:
                    raise ExpositionError(f":{lineno} '# TYPE' is incomplete")
                name, mtype = parts[2], parts[3]
                if mtype not in _METRIC_TYPES:
                    raise ExpositionError(f":{lineno} unknown metric type {mtype!r}")
                if name in families:
                    raise ExpositionError(f":{lineno} duplicate '# TYPE' for {name!r}")
                families[name] = {"help": None, "type": mtype, "samples": []}
            continue
        name, labels, value = _parse_sample(line, lineno)
        if name not in families:
            raise ExpositionError(f":{lineno} sample {name!r} has no preceding '# TYPE'")
        families[name]["samples"].append((labels, value))
    for name, help_text in helps.items():
        if name not in families:
            raise ExpositionError(f"'# HELP' for {name!r} names no typed family")
        families[name]["help"] = help_text
    return families


def _samples_by_label(families, name, label):
    """`{label value: sample value}` for one family, so a test names a series by
    its LABEL rather than by its position in the file."""
    return {labels[label]: value for labels, value in families[name]["samples"]}


class TestPrometheusExpositionParserRefuses(unittest.TestCase):
    """The instrument, scored in both directions before it scores the writer.

    Each refusal below is DIFFERENTIAL: the same document is parsed green first
    and then broken by one edit, so a parser that refused everything -- the way
    an over-strict instrument silently turns every later row into a pass for the
    wrong reason -- fails the control half of its own test.
    """

    # A real node-exporter document. Nothing in this repo emits these names, an
    # explicit millisecond timestamp, or a trailing comma inside a label list,
    # so accepting it cannot be a property of the writer.
    VALID_FOREIGN = (
        "# HELP node_load1 1m load average.\n"
        "# TYPE node_load1 gauge\n"
        "node_load1 0.42 1754870400000\n"
        "\n"
        "# HELP node_scrape_collector_success Whether the collector succeeded.\n"
        "# TYPE node_scrape_collector_success gauge\n"
        'node_scrape_collector_success{collector="textfile",} 1\n'
        'node_scrape_collector_success{collector="cpu"} 0\n'
        "# a bare comment line\n"
    )

    def test_the_parser_accepts_a_valid_document_this_repo_never_writes(self):
        families = parse_exposition(self.VALID_FOREIGN)
        self.assertEqual(set(families), {"node_load1", "node_scrape_collector_success"})
        self.assertEqual(families["node_load1"]["type"], "gauge")
        self.assertEqual(families["node_load1"]["help"], "1m load average.")
        self.assertEqual(families["node_load1"]["samples"], [({}, 0.42)])
        self.assertEqual(
            _samples_by_label(families, "node_scrape_collector_success", "collector"),
            {"textfile": 1.0, "cpu": 0.0},
        )

    def test_a_sample_with_no_preceding_type_is_refused(self):
        good = "# TYPE plex_probe gauge\nplex_probe 1\n"
        self.assertEqual(len(parse_exposition(good)), 1)

        bad = good.replace("# TYPE plex_probe gauge\n", "")
        with self.assertRaises(ExpositionError) as ctx:
            parse_exposition(bad)
        self.assertIn("# TYPE", str(ctx.exception))

    def test_a_duplicated_help_for_one_name_is_refused(self):
        good = "# HELP plex_probe One sentence.\n# TYPE plex_probe gauge\nplex_probe 1\n"
        self.assertEqual(parse_exposition(good)["plex_probe"]["help"], "One sentence.")

        bad = good.replace(
            "# TYPE plex_probe gauge\n",
            "# HELP plex_probe A second sentence.\n# TYPE plex_probe gauge\n",
        )
        with self.assertRaises(ExpositionError) as ctx:
            parse_exposition(bad)
        self.assertIn("duplicate", str(ctx.exception))

    def test_an_unescaped_quote_in_a_label_value_is_refused(self):
        good = '# TYPE plex_probe gauge\nplex_probe{hold_site="Cache.cpp:12"} 1\n'
        self.assertEqual(
            _samples_by_label(parse_exposition(good), "plex_probe", "hold_site"),
            {"Cache.cpp:12": 1.0},
        )

        # ONE character: the quote that the writer is obliged to escape. The
        # value terminates early and the label list no longer closes.
        bad = good.replace('Cache.cpp:12"}', 'Cache"cpp:12"}')
        with self.assertRaises(ExpositionError):
            parse_exposition(bad)

        # And the ESCAPED form of the same character must still parse, or the
        # refusal above is a ban on quotes rather than a conformance check.
        escaped = good.replace('Cache.cpp:12"}', 'Cache\\"cpp:12"}')
        self.assertEqual(
            _samples_by_label(parse_exposition(escaped), "plex_probe", "hold_site"),
            {'Cache"cpp:12': 1.0},
        )

    def test_a_non_float_sample_value_is_refused(self):
        good = "# TYPE plex_probe gauge\nplex_probe 1\n"
        self.assertEqual(parse_exposition(good)["plex_probe"]["samples"], [({}, 1.0)])

        for token in ("ok", "1.2.3", "", "1_0"):
            with self.subTest(value=token):
                bad = f"# TYPE plex_probe gauge\nplex_probe {token}\n"
                with self.assertRaises(ExpositionError):
                    parse_exposition(bad)

    def test_the_four_refusals_are_four_and_not_one_blanket_no(self):
        # Anti-vacuity for the instrument itself: every control document above
        # parses, so the refusals are properties of the malformation.
        for doc in (
            self.VALID_FOREIGN,
            "# TYPE plex_probe gauge\nplex_probe 1\n",
            "# HELP plex_probe One sentence.\n# TYPE plex_probe gauge\nplex_probe 1\n",
            '# TYPE plex_probe gauge\nplex_probe{hold_site="Cache.cpp:12"} 1\n',
            "",
        ):
            with self.subTest(doc=doc[:40]):
                parse_exposition(doc)


class TestTextfileMetricsRendering(unittest.TestCase):
    """`render_textfile_metrics` -- design §5.2's exposition, byte for byte.

    The renderer is a PURE function of the metric state so the golden can be
    compared without a filesystem, a clock or a probe in the way. Its state dict
    is the one the engine keeps in memory across snapshots; nothing here reads
    `plex_blip_diagnostics_*.jsonl` back (plan.md Step 4, premise 5).

    THE HELP STRINGS ARE THE DESIGN'S OWN for the four families design §5.2
    spells out, so a reader can hold the two side by side; the other four are
    authored here because §5.2 renders them under a shared block.
    """

    # design §5.2's own figures, so the golden IS the design's example.
    STATE = {
        "sqlite": {
            "db_bytes": 42834944,
            "wal_bytes": 43735168,
            "shm_bytes": 360448,
            # The fourth key the record's `sqlite` block carries. It is a RATIO,
            # not a byte count, and it must not reach the collector file at all.
            "wal_ratio": 43735168 / 42834944,
        },
        "events": {"TX_HELD": 42, "TX_STALL": 32, "SLOW_QUERY": 49, "STREAM_DROP": 8},
        "hold_seconds_max": {"MetadataItemSetting.cpp:459": 2.51},
        "probe_seconds": {"lsof": 2.0, "fuser": 0.031},
        "probe_ok": {"fuser": True, "lsof": False},
        "live_connections": 13,
    }

    GOLDEN = (
        "# HELP plex_sqlite_wal_bytes Size of the SQLite WAL file.\n"
        "# TYPE plex_sqlite_wal_bytes gauge\n"
        "plex_sqlite_wal_bytes 43735168\n"
        "\n"
        "# HELP plex_sqlite_db_bytes Size of the Plex library SQLite database.\n"
        "# TYPE plex_sqlite_db_bytes gauge\n"
        "plex_sqlite_db_bytes 42834944\n"
        "\n"
        "# HELP plex_sqlite_shm_bytes Size of the SQLite shared-memory index.\n"
        "# TYPE plex_sqlite_shm_bytes gauge\n"
        "plex_sqlite_shm_bytes 360448\n"
        "\n"
        "# HELP plex_watchdog_events_total Watchdog trigger events by type since start.\n"
        "# TYPE plex_watchdog_events_total counter\n"
        'plex_watchdog_events_total{event_type="SLOW_QUERY"} 49\n'
        'plex_watchdog_events_total{event_type="STREAM_DROP"} 8\n'
        'plex_watchdog_events_total{event_type="TX_HELD"} 42\n'
        'plex_watchdog_events_total{event_type="TX_STALL"} 32\n'
        "\n"
        "# HELP plex_watchdog_hold_seconds_max Longest transaction hold observed, by site.\n"
        "# TYPE plex_watchdog_hold_seconds_max gauge\n"
        'plex_watchdog_hold_seconds_max{hold_site="MetadataItemSetting.cpp:459"} 2.51\n'
        "\n"
        "# HELP plex_watchdog_probe_duration_seconds Duration of the last diagnostic probe.\n"
        "# TYPE plex_watchdog_probe_duration_seconds gauge\n"
        'plex_watchdog_probe_duration_seconds{probe="fuser"} 0.031\n'
        'plex_watchdog_probe_duration_seconds{probe="lsof"} 2.0\n'
        "\n"
        "# HELP plex_watchdog_probe_status 1 when the last diagnostic probe returned ok, 0 otherwise.\n"
        "# TYPE plex_watchdog_probe_status gauge\n"
        'plex_watchdog_probe_status{probe="fuser"} 1\n'
        'plex_watchdog_probe_status{probe="lsof"} 0\n'
        "\n"
        "# HELP plex_live_connections Concurrent Plex connections seen on the last trigger line.\n"
        "# TYPE plex_live_connections gauge\n"
        "plex_live_connections 13\n"
    )

    def _state(self, **overrides):
        state = json.loads(json.dumps(self.STATE))
        state.update(overrides)
        return state

    def test_the_rendered_exposition_matches_the_golden_byte_for_byte(self):
        self.assertEqual(watchdog.render_textfile_metrics(self._state()), self.GOLDEN)

    def test_the_golden_is_what_the_strict_parser_reads_back(self):
        # The golden pins the BYTES; this pins their MEANING, through the
        # instrument that was scored against four malformations above.
        families = parse_exposition(watchdog.render_textfile_metrics(self._state()))

        self.assertEqual(families["plex_sqlite_wal_bytes"]["type"], "gauge")
        self.assertEqual(families["plex_watchdog_events_total"]["type"], "counter")
        self.assertEqual(families["plex_sqlite_wal_bytes"]["samples"], [({}, 43735168.0)])
        self.assertEqual(
            _samples_by_label(families, "plex_watchdog_events_total", "event_type"),
            {"TX_HELD": 42.0, "TX_STALL": 32.0, "SLOW_QUERY": 49.0, "STREAM_DROP": 8.0},
        )
        self.assertEqual(
            _samples_by_label(families, "plex_watchdog_probe_status", "probe"),
            {"fuser": 1.0, "lsof": 0.0},
        )
        self.assertEqual(
            _samples_by_label(families, "plex_watchdog_probe_duration_seconds", "probe"),
            {"fuser": 0.031, "lsof": 2.0},
        )

    def test_every_family_carries_its_own_help_and_type(self):
        # design §5.2 renders three gauges under ONE header block, which is legal
        # exposition and leaves two of the three untyped for anything reading the
        # file. The writer emits a header pair per family instead, and this is
        # the row that says so.
        families = parse_exposition(watchdog.render_textfile_metrics(self._state()))
        self.assertEqual(len(families), 8, f"eight families, got {sorted(families)}")
        for name, family in families.items():
            with self.subTest(metric=name):
                self.assertIn(family["type"], ("gauge", "counter"))
                self.assertTrue(family["help"], f"{name} carries no # HELP text")
                self.assertTrue(family["help"].endswith("."), "HELP is a sentence")

    def test_the_ratio_column_is_not_published_as_a_byte_count(self):
        text = watchdog.render_textfile_metrics(self._state())
        self.assertNotIn("wal_ratio", text)
        self.assertNotIn(repr(self.STATE["sqlite"]["wal_ratio"]), text)

    def test_a_null_wal_omits_the_sample_rather_than_publishing_a_zero(self):
        # plan.md Step 4, premise 6a. A zero is indistinguishable from a freshly
        # checkpointed WAL once it is a point on a Grafana graph, and
        # task-1786152655-55f9 measured an orphaned 41.71 MiB WAL recording as
        # all-null -- so the null case is exactly the case that must not lie.
        state = self._state()
        state["sqlite"] = {"db_bytes": None, "wal_bytes": None, "shm_bytes": None, "wal_ratio": None}
        text = watchdog.render_textfile_metrics(state)

        families = parse_exposition(text)
        for name in ("plex_sqlite_wal_bytes", "plex_sqlite_db_bytes", "plex_sqlite_shm_bytes"):
            with self.subTest(metric=name):
                self.assertNotIn(
                    name, families,
                    "a null measurement must omit the family outright -- a `# TYPE` "
                    "with no sample still tells a reader the series exists",
                )
        self.assertNotIn("plex_sqlite", text)
        # The rest of the document is unaffected: omission is per family.
        self.assertIn("plex_watchdog_events_total", families)

    def test_a_zero_byte_wal_is_published_because_zero_is_a_measurement(self):
        # The other half of the same distinction, and the one that keeps the row
        # above from being satisfiable by "never publish the WAL at all".
        state = self._state()
        state["sqlite"] = {"db_bytes": 42834944, "wal_bytes": 0, "shm_bytes": None, "wal_ratio": 0.0}
        families = parse_exposition(watchdog.render_textfile_metrics(state))

        self.assertEqual(families["plex_sqlite_wal_bytes"]["samples"], [({}, 0.0)])
        self.assertIn("plex_sqlite_db_bytes", families)
        self.assertNotIn("plex_sqlite_shm_bytes", families)

    def test_a_label_value_carrying_a_quote_or_a_backslash_is_escaped(self):
        # `hold_site` is a compiler-supplied string. It has never carried either
        # character, which is exactly why an unescaped writer would ship green
        # for months and then emit one unparseable file on the day it does.
        state = self._state()
        state["hold_seconds_max"] = {'Odd"Site\\cpp:1': 1.5, "Line\nBreak.cpp:2": 0.5}
        text = watchdog.render_textfile_metrics(state)

        self.assertIn(r'hold_site="Odd\"Site\\cpp:1"', text)
        self.assertIn(r'hold_site="Line\nBreak.cpp:2"', text)
        self.assertEqual(
            len(text.split("\n")), len(self.GOLDEN.split("\n")) + 1,
            "an unescaped newline would add a line to the document",
        )
        self.assertEqual(
            _samples_by_label(parse_exposition(text), "plex_watchdog_hold_seconds_max", "hold_site"),
            {'Odd"Site\\cpp:1': 1.5, "Line\nBreak.cpp:2": 0.5},
        )

    def test_an_empty_state_renders_an_empty_document_not_a_file_of_headers(self):
        empty = watchdog.render_textfile_metrics(watchdog._new_metrics_state())
        self.assertEqual(empty, "")
        self.assertEqual(parse_exposition(empty), {})

    def test_series_are_ordered_by_label_so_two_renders_are_byte_identical(self):
        # node-exporter re-serves this file verbatim; a set-ordered document
        # would churn the bytes on every write for no change in meaning.
        shuffled = self._state()
        shuffled["events"] = dict(reversed(list(shuffled["events"].items())))
        shuffled["probe_seconds"] = {"lsof": 2.0, "fuser": 0.031}
        self.assertEqual(watchdog.render_textfile_metrics(shuffled), self.GOLDEN)


class TestTextfileMetricsFromTheRecord(unittest.TestCase):
    """The engine half: the metric state is derived from the IN-MEMORY record.

    plan.md Step 4, premise 5 -- the emitter must not read the day's JSONL back.
    A counter that resets when the unit restarts is not a defect (Prometheus
    handles counter resets); a reader of `plex_blip_diagnostics_*.jsonl` is
    `task-1786137337-99cf`'s subject and that file mixes 8-key, 10-key and
    11-key records on the deploy day.
    """

    TRIGGERS = {
        "TX_HELD": {
            "event_type": "TX_HELD",
            "delay_ms": 540.0,
            "line": "Aug 07, 2026 06:37:33.273 [1] WARN - Held transaction for too long (X): 0.540000 seconds",
            "hold_site": "StatisticsManager.cpp:288",
            "live_connections": 4,
        },
        "TX_STALL": {
            "event_type": "TX_STALL",
            "delay_ms": 120.0,
            "line": "Aug 07, 2026 06:38:11.899 [101] WARN - Took too long (0.120000 seconds) to start a transaction",
        },
        "SLOW_QUERY": {
            "event_type": "SLOW_QUERY",
            "delay_ms": 4977.0,
            "line": "Aug 07, 2026 06:39:00.000 [1] DEBUG - Completed: [x] 200 GET /library (7 live) 4977ms",
            "live_connections": 7,
        },
    }

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="plex_watchdog_4a_")
        self.log_path = os.path.join(self.test_dir, "mock_plex.log")
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Aug 07, 2026 06:30:00.000 [100] INFO - Server starting up\n")
        self.out_dir = os.path.join(self.test_dir, "diagnostics")
        self.textfile_dir = os.path.join(self.test_dir, "textfile_collector")
        os.makedirs(self.textfile_dir, exist_ok=True)
        self.db_path = os.path.join(self.test_dir, "com.plexapp.plugins.library.db")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _engine(self, **overrides):
        kwargs = dict(
            log_path=self.log_path,
            output_dir=self.out_dir,
            db_pattern=self.db_path + "*",
            dry_run=False,
            textfile_dir=self.textfile_dir,
        )
        kwargs.update(overrides)
        return watchdog.WatchdogEngine(**kwargs)

    def _prom_path(self):
        return os.path.join(self.textfile_dir, watchdog.TEXTFILE_NAME)

    def _published(self):
        with open(self._prom_path(), "r", encoding="utf-8") as f:
            return parse_exposition(f.read())

    def _write_db(self, db=None, wal=None, shm=None):
        for suffix, size in ((".db", db), (".db-wal", wal), (".db-shm", shm)):
            if size is None:
                continue
            path = self.db_path if suffix == ".db" else self.db_path + suffix[3:]
            with open(path, "wb") as f:
                f.truncate(size)

    # -- counters -----------------------------------------------------------

    def test_counters_are_monotonic_across_three_successive_snapshots(self):
        engine = self._engine()
        seen = []
        for name in ("TX_HELD", "TX_STALL", "TX_HELD"):
            engine.capture_snapshot(self.TRIGGERS[name])
            seen.append(_samples_by_label(self._published(), "plex_watchdog_events_total", "event_type"))

        self.assertEqual(seen[0], {"TX_HELD": 1.0})
        self.assertEqual(seen[1], {"TX_HELD": 1.0, "TX_STALL": 1.0})
        self.assertEqual(seen[2], {"TX_HELD": 2.0, "TX_STALL": 1.0})
        for earlier, later in zip(seen, seen[1:]):
            for event_type, count in earlier.items():
                with self.subTest(event_type=event_type):
                    self.assertGreaterEqual(
                        later[event_type], count, "a counter may not go backwards"
                    )
        self.assertEqual(sum(seen[-1].values()), 3.0, "one snapshot, one increment")

    def test_the_counter_lives_in_memory_and_survives_the_jsonl_being_deleted(self):
        # premise 5, measured rather than promised: the artifact is removed
        # between snapshots and the count still carries. An emitter that
        # re-derived its counters from the day's file would restart at 1 here.
        engine = self._engine()
        engine.capture_snapshot(self.TRIGGERS["TX_HELD"])
        for stale in pathlib.Path(self.out_dir).glob("*.jsonl"):
            stale.unlink()
        engine.capture_snapshot(self.TRIGGERS["TX_HELD"])

        self.assertEqual(
            _samples_by_label(self._published(), "plex_watchdog_events_total", "event_type"),
            {"TX_HELD": 2.0},
        )

    def test_a_second_engine_starts_its_counters_at_zero_and_that_is_the_contract(self):
        # The other side of premise 5: a unit restart resets the counter, which
        # Prometheus handles, and NOT reading the mixed-schema artifact back is
        # the trade that buys it. Pinned so a later row cannot quietly add the
        # read without `task-1786137337-99cf` coming with it.
        first = self._engine()
        first.capture_snapshot(self.TRIGGERS["TX_HELD"])
        first.capture_snapshot(self.TRIGGERS["TX_HELD"])
        self.assertEqual(
            _samples_by_label(self._published(), "plex_watchdog_events_total", "event_type"),
            {"TX_HELD": 2.0},
        )

        second = self._engine()
        second.capture_snapshot(self.TRIGGERS["TX_HELD"])
        self.assertEqual(
            _samples_by_label(self._published(), "plex_watchdog_events_total", "event_type"),
            {"TX_HELD": 1.0},
        )

    def test_the_emitter_names_no_diagnostics_artifact_anywhere_in_its_source(self):
        # An AST/source census beside the behavioural row above, because the
        # behavioural one passes for an emitter that reads the file and happens
        # to add to it rather than replacing.
        for func in (
            watchdog.WatchdogEngine._observe_record,
            watchdog.WatchdogEngine.write_textfile_metrics,
            watchdog.WatchdogEngine.refresh_textfile_gauges,
            watchdog.render_textfile_metrics,
        ):
            with self.subTest(func=func.__name__):
                source = inspect.getsource(func)
                self.assertNotIn("plex_blip_diagnostics", source)
                self.assertNotIn("output_dir", source)
                self.assertNotIn("json.load", source)

    def test_hold_seconds_max_keeps_the_longest_hold_per_site(self):
        engine = self._engine()
        long_hold = {**self.TRIGGERS["TX_HELD"], "delay_ms": 2510.0}
        short_hold = {**self.TRIGGERS["TX_HELD"], "delay_ms": 540.0}
        other_site = {**self.TRIGGERS["TX_HELD"], "delay_ms": 1020.0,
                      "hold_site": "MetadataItemSetting.cpp:459"}

        for trigger in (long_hold, short_hold, other_site):
            engine.capture_snapshot(trigger)

        self.assertEqual(
            _samples_by_label(self._published(), "plex_watchdog_hold_seconds_max", "hold_site"),
            {"StatisticsManager.cpp:288": 2.51, "MetadataItemSetting.cpp:459": 1.02},
            "the MAX per site, in SECONDS -- a later shorter hold must not lower it",
        )

    def test_a_waiter_trigger_publishes_no_hold_site_series(self):
        engine = self._engine()
        engine.capture_snapshot(self.TRIGGERS["TX_STALL"])
        self.assertNotIn(
            "plex_watchdog_hold_seconds_max", self._published(),
            "TX_STALL is the waiter side and names no code site; a null hold_site "
            "must not become a series labelled with the empty string",
        )

    def test_live_connections_publishes_the_count_the_last_trigger_carried(self):
        engine = self._engine()
        engine.capture_snapshot(self.TRIGGERS["TX_HELD"])
        self.assertEqual(self._published()["plex_live_connections"]["samples"], [({}, 4.0)])

        engine.capture_snapshot(self.TRIGGERS["SLOW_QUERY"])
        self.assertEqual(self._published()["plex_live_connections"]["samples"], [({}, 7.0)])

        # A trigger that carries no count must not zero the gauge: the saturation
        # counter rides on Request:/Completed: lines only, so "absent" here means
        # "this line did not say", not "there are no connections".
        engine.capture_snapshot(self.TRIGGERS["TX_STALL"])
        self.assertEqual(self._published()["plex_live_connections"]["samples"], [({}, 7.0)])

    # -- probes -------------------------------------------------------------

    def test_probe_status_is_one_for_ok_alone_across_all_four_run_cmd_statuses(self):
        # The four statuses are produced by the SHIPPED `_run_cmd` rather than
        # typed into a fixture, so the row cannot drift from the vocabulary
        # `test_run_cmd_status_vocabulary_is_exactly_four_spellings` pins.
        not_executable = os.path.join(self.test_dir, "probe.sh")
        with open(not_executable, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n")
        os.chmod(not_executable, 0o644)

        results = {
            "ok": watchdog._run_cmd([sys.executable, "-c", "print('held')"], timeout=5.0),
            "timeout": watchdog._run_cmd(
                [sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2
            ),
            "missing": watchdog._run_cmd(["plex-blip-no-such-binary-xyz"], timeout=0.5),
            "error": watchdog._run_cmd([not_executable], timeout=0.5),
        }
        self.assertEqual(
            {name: res["status"] for name, res in results.items()},
            {"ok": "ok", "timeout": "timeout", "missing": "missing", "error": "error"},
            "the four spellings must be REACHED, or this row scores nothing",
        )

        engine = self._engine()
        engine._observe_record({
            "trigger_event": "TX_STALL",
            "lock_holders": {"fuser": results["ok"], "lsof": results["missing"]},
            "process_traces": {"pidstat": results["timeout"], "ps_aux_t": results["error"]},
            "sqlite": {"db_bytes": None, "wal_bytes": None, "shm_bytes": None, "wal_ratio": None},
        })
        engine.write_textfile_metrics()

        self.assertEqual(
            _samples_by_label(self._published(), "plex_watchdog_probe_status", "probe"),
            {"fuser": 1.0, "lsof": 0.0, "pidstat": 0.0, "ps_aux_t": 0.0},
            "1 for `ok` ALONE -- missing, timeout and error are each a 0, and the "
            "metric that would have surfaced the absent psmisc on day one is the "
            "one that must not report a missing binary as healthy",
        )

    def test_the_probe_duration_is_the_measured_elapsed_ms_in_seconds(self):
        engine = self._engine()
        timed_out = watchdog._run_cmd(
            [sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2
        )
        engine._observe_record({
            "trigger_event": "TX_STALL",
            "lock_holders": {"lsof": timed_out},
            "process_traces": {},
            "sqlite": {"db_bytes": None, "wal_bytes": None, "shm_bytes": None, "wal_ratio": None},
        })
        engine.write_textfile_metrics()

        published = _samples_by_label(
            self._published(), "plex_watchdog_probe_duration_seconds", "probe"
        )
        self.assertEqual(
            published["lsof"], timed_out["elapsed_ms"] / 1000.0,
            "the gauge is the probe's own measurement, converted -- never the "
            "timeout it was given and never the milliseconds unconverted",
        )
        self.assertGreaterEqual(published["lsof"], 0.18)
        self.assertLess(published["lsof"], 2.0)

    # -- the two silences ---------------------------------------------------

    def test_a_dry_run_writes_nothing_into_the_collector_directory(self):
        # plan.md Step 4, premise 6b. `_dry_run_fallback` keeps the measurement
        # but `task-1786128505-658f` measured `elapsed_ms` pinned only by
        # PRESENCE, so a fabricated 999.0 would land on a Grafana graph as a real
        # probe duration. The collector directory is the boundary.
        engine = self._engine(dry_run=True)
        engine.capture_snapshot(self.TRIGGERS["TX_HELD"])

        self.assertEqual(
            sorted(os.listdir(self.textfile_dir)), [],
            "--dry-run must leave the collector directory EMPTY -- not a stale "
            "file, not a .tmp, not an empty .prom",
        )
        # ...and the snapshot itself still lands, so the silence is not a crash.
        self.assertEqual(len(list(pathlib.Path(self.out_dir).glob("*.jsonl"))), 1)

    def test_an_unset_textfile_dir_writes_nothing_and_is_the_default(self):
        # The flag defaults to unset and unset means silence; the wiring is 4b's.
        default = inspect.signature(watchdog.WatchdogEngine.__init__).parameters["textfile_dir"].default
        self.assertIsNone(default, "--textfile-dir must default to unset")

        engine = self._engine(textfile_dir=None)
        engine.capture_snapshot(self.TRIGGERS["TX_HELD"])
        self.assertEqual(sorted(os.listdir(self.textfile_dir)), [])
        self.assertEqual(len(list(pathlib.Path(self.out_dir).glob("*.jsonl"))), 1)

    def test_a_null_wal_reaches_the_collector_file_as_an_omitted_sample(self):
        # The omission proven end-to-end through `capture_snapshot`, not only
        # through the renderer: the db is present, the -wal is not.
        self._write_db(db=4096)
        engine = self._engine()
        engine.capture_snapshot(self.TRIGGERS["TX_STALL"])

        families = self._published()
        self.assertEqual(families["plex_sqlite_db_bytes"]["samples"], [({}, 4096.0)])
        self.assertNotIn("plex_sqlite_wal_bytes", families)
        self.assertNotIn("plex_sqlite_shm_bytes", families)

        # And with the -wal in place the same call publishes its true size.
        self._write_db(wal=43735168)
        engine.capture_snapshot(self.TRIGGERS["TX_STALL"])
        self.assertEqual(
            self._published()["plex_sqlite_wal_bytes"]["samples"], [({}, 43735168.0)]
        )

    # -- the record is not widened ------------------------------------------

    def test_the_record_key_set_is_untouched_by_the_metrics_row(self):
        # Acceptance 2 as a live equality here as well as at :695 and :1454:
        # metrics are a SECOND OUTPUT, not a wider record.
        self._write_db(db=4096, wal=1024)
        engine = self._engine()
        out_path = engine.capture_snapshot(self.TRIGGERS["TX_HELD"])
        with open(out_path, "r", encoding="utf-8") as f:
            record = json.loads(f.readline())

        self.assertEqual(set(record), TestSnapshotStructuredShape.TOP_LEVEL_KEYS)
        self.assertEqual(set(record["sqlite"]), TestSqliteWalStateCapture.WAL_KEYS)
        self.assertEqual(
            record["sqlite"]["wal_bytes"],
            self._published()["plex_sqlite_wal_bytes"]["samples"][0][1],
            "the published gauge must be the record's own number, so the two "
            "outputs cannot disagree about the same measurement",
        )


class TestTextfileWriteIsAtomic(unittest.TestCase):
    """Write-and-rename, proven by forcing the failure rather than asserting it.

    node-exporter reads this file on its own schedule, so a reader can land
    between the `write()` and the rename. `os.replace` is atomic ONLY within a
    filesystem, which is why the temporary file being a sibling of the target is
    a correctness property and not a matter of style.
    """

    PREVIOUS = "# HELP plex_sqlite_wal_bytes Size of the SQLite WAL file.\n"

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="plex_watchdog_atomic_")
        self.log_path = os.path.join(self.test_dir, "mock_plex.log")
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Aug 07, 2026 06:30:00.000 [100] INFO - Server starting up\n")
        self.out_dir = os.path.join(self.test_dir, "diagnostics")
        self.textfile_dir = os.path.join(self.test_dir, "textfile_collector")
        os.makedirs(self.textfile_dir, exist_ok=True)
        self.engine = watchdog.WatchdogEngine(
            log_path=self.log_path,
            output_dir=self.out_dir,
            db_pattern=os.path.join(self.test_dir, "absent.db*"),
            dry_run=False,
            textfile_dir=self.textfile_dir,
        )
        self.engine._metrics["events"]["TX_HELD"] = 1
        self.target = os.path.join(self.textfile_dir, watchdog.TEXTFILE_NAME)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    class _OsShim:
        """Proxies the real `os` and intercepts `replace` alone -- the same
        module-attribute rebinding `test_the_base_database_is_chosen_by_name...`
        uses for `glob`, so the failure is injected at the seam the code
        actually goes through rather than by monkeypatching the stdlib."""

        def __init__(self, real, on_replace):
            self._real = real
            self._on_replace = on_replace

        def __getattr__(self, name):
            return getattr(self._real, name)

        def replace(self, src, dst):
            return self._on_replace(src, dst)

    def _with_replace(self, on_replace):
        real_os = watchdog.os
        watchdog.os = self._OsShim(real_os, on_replace)
        try:
            return self.engine.write_textfile_metrics()
        finally:
            watchdog.os = real_os

    def test_the_temporary_file_is_a_sibling_of_the_target(self):
        seen = {}

        def _record(src, dst):
            seen["src"], seen["dst"] = src, dst
            return os.replace(src, dst)

        self._with_replace(_record)
        self.assertEqual(seen["dst"], self.target)
        self.assertEqual(
            os.path.dirname(seen["src"]), os.path.dirname(seen["dst"]),
            "a rename ACROSS filesystems is not atomic, so the temporary file "
            f"must be a sibling of the target: {seen}",
        )
        self.assertNotEqual(seen["src"], seen["dst"])
        self.assertTrue(os.path.exists(self.target))

    def test_a_failure_between_the_write_and_the_rename_leaves_the_previous_bytes(self):
        with open(self.target, "w", encoding="utf-8") as f:
            f.write(self.PREVIOUS)
        before = os.stat(self.target)

        self.engine._metrics["events"]["TX_HELD"] = 99
        self._with_replace(lambda src, dst: (_ for _ in ()).throw(OSError("ENOSPC")))

        with open(self.target, "r", encoding="utf-8") as f:
            after_text = f.read()
        self.assertEqual(
            after_text, self.PREVIOUS,
            "a scrape landing on the failed write must read the PREVIOUS document, "
            "never a truncated one",
        )
        self.assertEqual(os.stat(self.target).st_ino, before.st_ino)
        self.assertEqual(
            sorted(os.listdir(self.textfile_dir)), [watchdog.TEXTFILE_NAME],
            "the temporary file must not be left behind for the collector to trip on",
        )

    def test_a_failure_on_the_first_write_leaves_no_target_at_all(self):
        self._with_replace(lambda src, dst: (_ for _ in ()).throw(OSError("EROFS")))
        self.assertFalse(
            os.path.exists(self.target),
            "an absent file is a scrape with no samples; a half-written one is a "
            "parse error for every series in it",
        )
        self.assertEqual(sorted(os.listdir(self.textfile_dir)), [])

    def test_a_failing_metrics_write_never_costs_the_snapshot(self):
        # The same trade `_wal_state` makes: a nice-to-have may not abort the
        # capture. The collector directory is removed out from under the engine.
        shutil.rmtree(self.textfile_dir)
        os.makedirs(self.textfile_dir)
        os.chmod(self.textfile_dir, 0o500)
        try:
            out_path = self.engine.capture_snapshot(
                {"event_type": "TX_STALL", "delay_ms": 120.0, "line": "x"}
            )
        finally:
            os.chmod(self.textfile_dir, 0o700)

        with open(out_path, "r", encoding="utf-8") as f:
            record = json.loads(f.readline())
        self.assertEqual(set(record), TestSnapshotStructuredShape.TOP_LEVEL_KEYS)

    def test_the_target_is_replaced_by_rename_and_never_rewritten_in_place(self):
        first = self.engine.write_textfile_metrics()
        first_ino = os.stat(first).st_ino
        self.engine._metrics["events"]["TX_STALL"] = 7
        second = self.engine.write_textfile_metrics()

        self.assertEqual(first, second)
        self.assertNotEqual(
            os.stat(second).st_ino, first_ino,
            "an in-place rewrite keeps the inode and is exactly the window this "
            "row exists to close",
        )
        self.assertEqual(
            _samples_by_label(
                parse_exposition(pathlib.Path(second).read_text(encoding="utf-8")),
                "plex_watchdog_events_total",
                "event_type",
            ),
            {"TX_HELD": 1.0, "TX_STALL": 7.0},
        )


class TestIdleGaugeRefreshAndTheRealCli(unittest.TestCase):
    """plan.md Step 4, premise 4 -- the gauges must move BETWEEN blips.

    `capture_snapshot` is reached only from `run()`'s trigger branch, so a
    `.prom` written there alone leaves node-exporter re-serving one stale sample
    until the next stall and the operator MANUFACTURING a blip to see the graph
    the step's own Demo promises. `run()` already gets `None` out of
    `read_line(timeout=0.5)` on every idle poll, so the refresh goes in a branch
    that already exists.

    It is STAT-ONLY. No `_run_cmd` call site is added, which is what keeps
    `task-1786124338-5963` unarmed and the module header's 8.0s bound true.
    """

    WAL_BYTES = 43735168      # the live CT 110 pathology, and Step 3's fixture
    DB_BYTES = 41943040       # 40 MiB

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="plex_watchdog_idle_")
        self.log_path = os.path.join(self.test_dir, "mock_plex.log")
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Aug 07, 2026 06:30:00.000 [100] INFO - Server starting up\n")
        self.out_dir = os.path.join(self.test_dir, "diagnostics")
        self.textfile_dir = os.path.join(self.test_dir, "textfile_collector")
        os.makedirs(self.textfile_dir, exist_ok=True)
        self.db_path = os.path.join(self.test_dir, "com.plexapp.plugins.library.db")
        self.target = os.path.join(self.textfile_dir, watchdog.TEXTFILE_NAME)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _sparse(self, path, size):
        with open(path, "wb") as f:
            f.truncate(size)
        self.assertEqual(os.path.getsize(path), size, "fixture did not land at its own size")

    def _engine(self, **overrides):
        kwargs = dict(
            log_path=self.log_path,
            output_dir=self.out_dir,
            db_pattern=self.db_path + "*",
            dry_run=False,
            textfile_dir=self.textfile_dir,
            textfile_refresh_sec=0.0,
        )
        kwargs.update(overrides)
        return watchdog.WatchdogEngine(**kwargs)

    def _published(self):
        return parse_exposition(pathlib.Path(self.target).read_text(encoding="utf-8"))

    def test_the_refresh_re_stats_the_database_with_no_trigger_at_all(self):
        self._sparse(self.db_path, self.DB_BYTES)
        self._sparse(self.db_path + "-wal", 1024)
        engine = self._engine()

        engine.refresh_textfile_gauges()
        self.assertEqual(self._published()["plex_sqlite_wal_bytes"]["samples"], [({}, 1024.0)])

        # The WAL grows while Plex is perfectly quiet -- no log line, no trigger.
        self._sparse(self.db_path + "-wal", self.WAL_BYTES)
        engine.refresh_textfile_gauges()
        self.assertEqual(
            self._published()["plex_sqlite_wal_bytes"]["samples"],
            [({}, float(self.WAL_BYTES))],
            "the gauge must follow the file between blips, or the Demo needs a "
            "manufactured stall to show anything",
        )

    def test_the_refresh_honours_its_interval(self):
        self._sparse(self.db_path, self.DB_BYTES)
        self._sparse(self.db_path + "-wal", 1024)
        engine = self._engine(textfile_refresh_sec=3600.0)

        self.assertIsNotNone(engine.refresh_textfile_gauges(), "the first poll publishes")
        self._sparse(self.db_path + "-wal", self.WAL_BYTES)
        self.assertIsNone(
            engine.refresh_textfile_gauges(),
            "a second refresh inside the window must not rewrite the file",
        )
        self.assertEqual(self._published()["plex_sqlite_wal_bytes"]["samples"], [({}, 1024.0)])

    def test_the_refresh_preserves_the_counters_it_did_not_measure(self):
        self._sparse(self.db_path, self.DB_BYTES)
        engine = self._engine()
        engine.capture_snapshot({
            "event_type": "TX_HELD", "delay_ms": 540.0, "line": "x",
            "hold_site": "StatisticsManager.cpp:288",
        })
        engine.refresh_textfile_gauges()

        families = self._published()
        self.assertEqual(
            _samples_by_label(families, "plex_watchdog_events_total", "event_type"),
            {"TX_HELD": 1.0},
            "a gauge refresh rewrites the whole document, so it must carry the "
            "counters forward rather than publishing a reset",
        )
        self.assertEqual(families["plex_sqlite_db_bytes"]["samples"], [({}, float(self.DB_BYTES))])

    def test_the_refresh_is_silent_under_dry_run_and_without_a_collector_dir(self):
        self._sparse(self.db_path, self.DB_BYTES)
        for label, engine in (
            ("dry-run", self._engine(dry_run=True)),
            ("unset", self._engine(textfile_dir=None)),
        ):
            with self.subTest(engine=label):
                self.assertIsNone(engine.refresh_textfile_gauges())
        self.assertEqual(sorted(os.listdir(self.textfile_dir)), [])

    def test_the_refresh_spawns_no_process_and_adds_no_probe_call_site(self):
        # `task-1786124338-5963` stays unarmed and the header's derived bound
        # stays true only while this path runs no probe. Pinned to the shipped
        # AST, the way design C1.4's cheapness is pinned for `_wal_state`.
        source = textwrap.dedent(inspect.getsource(watchdog.WatchdogEngine.refresh_textfile_gauges))
        tree = ast.parse(source)
        called = {ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)}
        forbidden = sorted(
            c for c in called
            if any(t in c.lower() for t in ("_run_cmd", "subprocess", "popen", "sqlite3", "connect"))
        )
        self.assertEqual(forbidden, [], f"the idle refresh must stay stat-only: {forbidden}")

    def test_the_idle_branch_of_run_is_what_publishes_before_any_trigger(self):
        # The refresh proven THROUGH `run()`, not by calling it directly: the
        # trigger arrives only after the file already exists, so the publication
        # cannot be attributed to `capture_snapshot`.
        self._sparse(self.db_path, self.DB_BYTES)
        self._sparse(self.db_path + "-wal", self.WAL_BYTES)
        engine = self._engine()

        thread = threading.Thread(target=engine.run, kwargs={"max_triggers": 1}, daemon=True)
        thread.start()
        deadline = time.time() + 10.0
        while time.time() < deadline and not os.path.exists(self.target):
            time.sleep(0.1)
        published_before_any_trigger = os.path.exists(self.target)
        idle_document = pathlib.Path(self.target).read_text(encoding="utf-8") if published_before_any_trigger else ""

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write("Aug 07, 2026 06:37:33.273 [1] WARN - Held transaction for too "
                    "long (Statistics/StatisticsManager.cpp:288): 0.540000 seconds\n")
            f.flush()
        thread.join(timeout=30.0)
        self.assertFalse(thread.is_alive(), "run() did not stop after --max-triggers 1")

        self.assertTrue(
            published_before_any_trigger,
            "run()'s idle branch must publish the gauges before the first trigger",
        )
        idle = parse_exposition(idle_document)
        self.assertEqual(idle["plex_sqlite_wal_bytes"]["samples"], [({}, float(self.WAL_BYTES))])
        self.assertNotIn(
            "plex_watchdog_events_total", idle,
            "no trigger has fired yet, so there is no counter to publish",
        )

        after = self._published()
        self.assertEqual(
            _samples_by_label(after, "plex_watchdog_events_total", "event_type"),
            {"TX_HELD": 1.0},
        )
        self.assertEqual(after["plex_sqlite_wal_bytes"]["samples"], [({}, float(self.WAL_BYTES))])

    def test_the_real_cli_publishes_the_true_wal_size_with_dry_run_not_set(self):
        # ACCEPTANCE 9, the Demo, as a test rather than only as a transcript.
        # `--dry-run` is NOT passed, the fixture is Step 3's own 40 MiB database
        # beside a 43,735,168-byte -wal, and the number is read back OUT of the
        # emitted file. Same fault the Step 3 cross-artifact join drove, so the
        # two records compare.
        self._sparse(self.db_path, self.DB_BYTES)
        self._sparse(self.db_path + "-wal", self.WAL_BYTES)

        cmd = [
            sys.executable, str(WATCHDOG_SCRIPT),
            "--log-path", self.log_path,
            "--output-dir", self.out_dir,
            "--db-pattern", self.db_path + "*",
            "--textfile-dir", self.textfile_dir,
            "--max-triggers", "1",
        ]
        self.assertNotIn("--dry-run", cmd, "the Demo runs the live path")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            time.sleep(1.0)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write("Aug 07, 2026 06:37:33.273 [1] WARN - Held transaction for too "
                        "long (Statistics/StatisticsManager.cpp:288): 0.540000 seconds\n")
                f.flush()
            stdout, stderr = proc.communicate(timeout=60)
        finally:
            if proc.poll() is None:
                proc.kill()
        self.assertEqual(proc.returncode, 0, f"real CLI run failed: {stderr}\n{stdout}")

        document = pathlib.Path(self.target).read_text(encoding="utf-8")
        self.assertIn(
            f"plex_sqlite_wal_bytes {self.WAL_BYTES}\n", document,
            "the Demo's whole claim: the pathology, at its true size, in the file "
            "node-exporter serves",
        )
        families = parse_exposition(document)
        self.assertEqual(families["plex_sqlite_wal_bytes"]["samples"], [({}, float(self.WAL_BYTES))])
        self.assertEqual(families["plex_sqlite_db_bytes"]["samples"], [({}, float(self.DB_BYTES))])
        self.assertEqual(
            _samples_by_label(families, "plex_watchdog_events_total", "event_type"),
            {"TX_HELD": 1.0},
        )
        self.assertEqual(
            _samples_by_label(families, "plex_watchdog_hold_seconds_max", "hold_site"),
            {"StatisticsManager.cpp:288": 0.54},
        )
        # The live path ran real probes, so every one of them must have a status.
        self.assertEqual(
            set(_samples_by_label(families, "plex_watchdog_probe_status", "probe")),
            {"fuser", "lsof", "pidstat", "ps_aux_t"},
        )


if __name__ == "__main__":
    unittest.main()
