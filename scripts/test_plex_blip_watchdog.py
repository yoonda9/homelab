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

    TOP_LEVEL_KEYS = {
        "timestamp",
        "trigger_event",
        "delay_ms",
        "trigger_line",
        "lock_holders",
        "process_traces",
        "sysstat_metrics",
        "dry_run",
    }
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
    def test_top_level_keys_are_exactly_the_eight_already_on_disk(self):
        record = self._capture()
        self.assertEqual(
            set(record), self.TOP_LEVEL_KEYS,
            "Steps 2-3 add sqlite/hold_site/live_connections -- an ADDITION here is "
            "expected and a REMOVAL breaks the captures already written",
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


if __name__ == "__main__":
    unittest.main()
