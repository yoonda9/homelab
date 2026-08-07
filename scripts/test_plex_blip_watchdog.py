#!/usr/bin/env python3
"""Unit and integration tests for plex_blip_watchdog.py log monitoring script.

Verifies zero-overhead inotify log tailing, trigger matching for DB lock stalls,
slow queries (>500ms), and network/relay collapses, 30s debounce rate-limiting,
and structured JSONL diagnostic snapshots (fuser, lsof, pidstat).
"""

import inspect
import json
import os
import pathlib
import shutil
import sqlite3
import subprocess
import sys
import tempfile
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


if __name__ == "__main__":
    unittest.main()
