"""Unit and integration tests for analyze_plex_blips.py log analysis tool.

Verifies operational taxonomy classification rules, regex parsing, timestamp
range filtering, output presentation formats (summary, jsonl, csv), directory
vs file scanning, and live evidence verification against /tmp/plex-logs.
"""

import csv
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_plex_blips as analyzer


class TestAnalyzePlexBlips(unittest.TestCase):
    def test_parse_tx_stall(self):
        line = "Aug 04, 2026 06:58:11.899 [132687892384568] WARN - Took too long (0.120000 seconds) to start a transaction on /home/runner/_work/plex-media-server/plex-media-server/Statistics/StatisticsBandwidth.cpp:110"
        ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev)
        self.assertEqual(ev.event_type, "TX_STALL")
        self.assertEqual(ev.duration_ms, 120.0)
        self.assertEqual(ev.thread_id, "132687892384568")
        self.assertEqual(ev.time_only, "06:58:11.899")

    def test_parse_slow_query_warn(self):
        line = "Aug 04, 2026 06:58:49.160 [132687933201208] WARN - [Req#57d3a] SLOW QUERY: It took 4360.000000 ms to retrieve 0 items."
        ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev)
        self.assertEqual(ev.event_type, "SLOW_QUERY")
        self.assertEqual(ev.duration_ms, 4360.0)

    def test_parse_slow_query_completed(self):
        line = "Aug 04, 2026 06:58:52.965 [132688110742328] DEBUG - Completed: [192.168.1.111:55824] 200 GET /library/sections/3/all (3 live) #57d3a Page 0--1 35905ms 707 bytes"
        ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev)
        self.assertEqual(ev.event_type, "SLOW_QUERY")
        self.assertEqual(ev.duration_ms, 35905.0)
        self.assertIn("/library/sections/3/all", ev.details)

    def test_parse_exporter_scrape_under_threshold(self):
        line = "Aug 04, 2026 06:58:17.248 [132687933201208] DEBUG - Request: [192.168.1.111:55824 (Subnet)] GET /library/sections/3/all (3 live) #57d3a Page 0--1 Signed-in Token (masyllis)"
        ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev)
        self.assertEqual(ev.event_type, "EXPORTER_SCRAPE")

    def test_parse_stream_drop(self):
        line = "Aug 04, 2026 07:00:10.642 [132688073702200] DEBUG - Shutting down idle session 8a729f13-b95d-4aab-9700-5eab86bf88f2 (idle time is 180 seconds)"
        ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev)
        self.assertEqual(ev.event_type, "STREAM_DROP")
        self.assertIn("8a729f13-b95d-4aab-9700-5eab86bf88f2", ev.details)
        self.assertEqual(ev.duration_ms, 180000.0)

    def test_parse_scheduled_task(self):
        line = "Aug 01, 2026 04:00:05.254 [132687937817400] INFO - It's been 3600 seconds, so we're starting scheduled library update for section 1 (Korean Shows)"
        ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev)
        self.assertEqual(ev.event_type, "SCHEDULED_TASK")
        self.assertIn("scheduled library update", ev.details)

    def test_timestamp_filtering(self):
        events = [
            analyzer.LogEvent("2026-08-04 06:56:59.000", "06:56:59.000", "TX_STALL", "1", 100.0, "msg1", "raw1", "f1"),
            analyzer.LogEvent("2026-08-04 06:57:45.784", "06:57:45.784", "SLOW_QUERY", "2", 29767.0, "msg2", "raw2", "f1"),
            analyzer.LogEvent("2026-08-04 07:00:10.642", "07:00:10.642", "STREAM_DROP", "3", 180000.0, "msg3", "raw3", "f1"),
            analyzer.LogEvent("2026-08-04 07:01:05.000", "07:01:05.000", "TX_STALL", "4", 100.0, "msg4", "raw4", "f1"),
        ]
        filtered = analyzer.filter_events(events, start="06:57:00", end="07:01:00")
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].event_type, "SLOW_QUERY")
        self.assertEqual(filtered[1].event_type, "STREAM_DROP")

    def test_output_formats(self):
        events = [
            analyzer.LogEvent("2026-08-04 06:58:11.899", "06:58:11.899", "TX_STALL", "123", 120.0, "Took too long (0.120000 seconds) to start a transaction", "raw", "f1"),
        ]
        out_summary = analyzer.format_output(events, "summary", start="06:57:00", end="07:01:00")
        self.assertIn("Plex Blip Analysis Summary", out_summary)
        self.assertIn("| TX_STALL | 1 |", out_summary)

        out_jsonl = analyzer.format_output(events, "jsonl")
        data = json.loads(out_jsonl.strip())
        self.assertEqual(data["event_type"], "TX_STALL")
        self.assertEqual(data["duration_ms"], 120.0)

        out_csv = analyzer.format_output(events, "csv")
        reader = csv.reader(io.StringIO(out_csv))
        rows = list(reader)
        self.assertEqual(rows[0], ["timestamp", "time_only", "event_type", "duration_ms", "thread_id", "source_file", "details", "raw_line"])
        self.assertEqual(rows[1][2], "TX_STALL")
        self.assertEqual(rows[1][3], "120.0")

    def test_directory_scanning_and_sorting(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = pathlib.Path(tmpdir) / "Plex Media Server.2.log"
            p2 = pathlib.Path(tmpdir) / "Plex Media Server.1.log"
            p1.write_text("Aug 04, 2026 07:00:10.642 [1] DEBUG - Shutting down idle session 8a729f13-b95d-4aab-9700-5eab86bf88f2 (idle time is 180 seconds)\n")
            p2.write_text("Aug 04, 2026 06:58:11.899 [2] WARN - Took too long (0.120000 seconds) to start a transaction on file.cpp:10\n")

            events = analyzer.analyze_path(tmpdir, threshold_ms=500)
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0].time_only, "06:58:11.899")
            self.assertEqual(events[0].event_type, "TX_STALL")
            self.assertEqual(events[1].time_only, "07:00:10.642")
            self.assertEqual(events[1].event_type, "STREAM_DROP")

    def test_multi_threaded_parsing(self):
        import concurrent.futures
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(5):
                p = pathlib.Path(tmpdir) / f"Plex Media Server.{i}.log"
                p.write_text(f"Aug 04, 2026 06:58:1{i}.899 [{i}] WARN - Took too long (0.120000 seconds) to start a transaction on file.cpp:10\n")

            with patch("concurrent.futures.ThreadPoolExecutor", wraps=concurrent.futures.ThreadPoolExecutor) as mock_executor:
                events = analyzer.analyze_path(tmpdir, threshold_ms=500)
                self.assertEqual(len(events), 5)
                self.assertGreaterEqual(mock_executor.call_count, 1, "Expected ThreadPoolExecutor for multi-threaded parsing")

    def test_correlation_engine(self):
        events = [
            analyzer.LogEvent("2026-08-04 06:58:11.899", "06:58:11.899", "TX_STALL", "1", 120.0, "stall msg", "raw1", "f1"),
            analyzer.LogEvent("2026-08-04 06:58:52.965", "06:58:52.965", "SLOW_QUERY", "2", 35905.0, "slow query msg", "raw2", "f1"),
            analyzer.LogEvent("2026-08-04 07:00:10.642", "07:00:10.642", "STREAM_DROP", "3", 180000.0, "drop msg", "raw3", "f1"),
        ]
        clusters_120 = analyzer.correlate_events(events, window_sec=120.0)
        self.assertEqual(len(clusters_120), 1)
        self.assertEqual(len(clusters_120[0]), 3)

        clusters_60 = analyzer.correlate_events(events, window_sec=60.0)
        self.assertEqual(len(clusters_60), 2)
        self.assertEqual(len(clusters_60[0]), 2)
        self.assertEqual(len(clusters_60[1]), 1)

        out = analyzer.format_output(events, "summary", window_sec=120.0)
        self.assertIn("Correlated Event Clusters (Window: 120.0s)", out)
        self.assertIn("Cluster 1", out)

    def test_live_evidence_verification(self):
        log_path = pathlib.Path("/tmp/plex-logs/Plex Media Server.log")
        if not log_path.is_file():
            print(f"SKIP: Live log not present at {log_path}")
            return
        events = analyzer.analyze_path(str(log_path), start="06:57:00", end="07:01:00", threshold_ms=500)
        summary = analyzer.format_output(events, "summary", start="06:57:00", end="07:01:00", window_sec=120.0)

        # Verify stream disconnect at 07:00:10 (session 8a729f13-b95d-4aab-9700-5eab86bf88f2)
        stream_drops = [e for e in events if e.event_type == "STREAM_DROP" and "8a729f13-b95d-4aab-9700-5eab86bf88f2" in e.details]
        self.assertTrue(len(stream_drops) >= 1, "Expected STREAM_DROP for session 8a729f13-b95d-4aab-9700-5eab86bf88f2")

        # Verify SLOW_QUERY event completing at 06:58:52 with 35905ms on GET /library/sections/3/all
        slow_queries = [e for e in events if e.event_type == "SLOW_QUERY" and e.duration_ms == 35905.0 and "/library/sections/3/all" in e.details]
        self.assertTrue(len(slow_queries) >= 1, "Expected SLOW_QUERY completing at 06:58:52 with 35905ms")

        # Verify presence of SQLite TX_STALL warnings overlapping with these events
        tx_stalls = [e for e in events if e.event_type == "TX_STALL"]
        self.assertTrue(len(tx_stalls) >= 1, "Expected overlapping TX_STALL warnings")

        # Verify correlation clusters section links these events
        self.assertIn("Correlated Event Clusters", summary, "Expected Correlated Event Clusters in summary")
        clusters = analyzer.correlate_events(events, window_sec=120.0)
        multi_event_clusters = [c for c in clusters if len(c) >= 2]
        self.assertTrue(len(multi_event_clusters) >= 1, "Expected at least one correlation cluster linking events within 120s")

        print("OK: Live log evidence verification passed")

    def test_markdown_output_executive_metrics(self):
        events = [
            analyzer.LogEvent("2026-08-04 06:58:11.899", "06:58:11.899", "TX_STALL", "101", 120.0, "Took too long (0.120000 seconds)", "raw1", "f1"),
            analyzer.LogEvent("2026-08-04 06:58:15.000", "06:58:15.000", "TX_STALL", "102", 80.0, "Took too long (0.080000 seconds)", "raw2", "f1"),
            analyzer.LogEvent("2026-08-04 06:58:20.000", "06:58:20.000", "EXPORTER_SCRAPE", "103", 5.0, "GET /library/sections/3/all", "raw3", "f1"),
            analyzer.LogEvent("2026-08-04 06:58:52.965", "06:58:52.965", "SLOW_QUERY", "104", 35905.0, "Completed GET /library/sections/3/all 35905ms", "raw4", "f1"),
            analyzer.LogEvent("2026-08-04 07:00:10.642", "07:00:10.642", "STREAM_DROP", "105", 180000.0, "Shutting down idle session 8a729f13-b95d-4aab-9700-5eab86bf88f2 (idle time is 180 seconds)", "raw5", "f1"),
        ]
        out = analyzer.format_output(events, "markdown", window_sec=120.0)

        self.assertIn("| Metric | Value |", out)
        self.assertIn("| :--- | :--- |", out)
        self.assertIn("200.0 ms", out)
        self.assertIn("35905.0 ms", out)
        self.assertIn("8a729f13-b95d-4aab-9700-5eab86bf88f2", out)
        self.assertIn("EXPORTER_SCRAPE", out)
        self.assertIn("| Timestamp | Event Type | Duration (ms) | Thread ID | Details |", out)

    def test_anomaly_centered_correlation(self):
        routine_events = [
            analyzer.LogEvent("2026-08-04 06:00:00.000", "06:00:00.000", "EXPORTER_SCRAPE", "1", 2.0, "GET /all", "raw1", "f1"),
            analyzer.LogEvent("2026-08-04 06:00:30.000", "06:00:30.000", "EXPORTER_SCRAPE", "2", 3.0, "GET /all", "raw2", "f1"),
            analyzer.LogEvent("2026-08-04 06:01:00.000", "06:01:00.000", "SCHEDULED_TASK", "3", None, "library update", "raw3", "f1"),
        ]
        clusters_routine = analyzer.correlate_events(routine_events, window_sec=120.0)
        self.assertEqual(len(clusters_routine), 0, f"Expected 0 correlation clusters for routine-only events, got {len(clusters_routine)}")

        mixed_events = [
            analyzer.LogEvent("2026-08-04 06:58:00.000", "06:58:00.000", "EXPORTER_SCRAPE", "10", 5.0, "scrape before stall", "r1", "f1"),
            analyzer.LogEvent("2026-08-04 06:58:30.000", "06:58:30.000", "TX_STALL", "11", 120.0, "stall anomaly", "r2", "f1"),
            analyzer.LogEvent("2026-08-04 08:00:00.000", "08:00:00.000", "EXPORTER_SCRAPE", "12", 4.0, "isolated scrape", "r3", "f1"),
            analyzer.LogEvent("2026-08-04 08:00:30.000", "08:00:30.000", "EXPORTER_SCRAPE", "13", 3.0, "isolated scrape 2", "r4", "f1"),
        ]
        clusters_mixed = analyzer.correlate_events(mixed_events, window_sec=120.0)
        self.assertEqual(len(clusters_mixed), 1, "Expected exactly 1 correlation cluster centered around TX_STALL")
        self.assertEqual(len(clusters_mixed[0]), 2, "Expected cluster to contain only the anomaly and nearby scrape")
        event_types = [e.event_type for e in clusters_mixed[0]]
        self.assertIn("TX_STALL", event_types)
        self.assertIn("EXPORTER_SCRAPE", event_types)

    def test_broken_pipe_handling(self):
        import subprocess
        log_path = pathlib.Path("/tmp/plex-logs/Plex Media Server.log")
        if not log_path.is_file():
            print(f"SKIP: Live log not present at {log_path}")
            return
        cmd = f"set -o pipefail; python3 \"{SCRIPTS_DIR / 'analyze_plex_blips.py'}\" \"{log_path}\" | head -n 1"
        res = subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Expected 0 exit code on broken pipe, got {res.returncode} with stderr: {res.stderr}")
        self.assertEqual(res.stderr, "", f"Expected empty stderr on broken pipe, got: {res.stderr}")

    def test_gzip_rotated_logs(self):
        import gzip
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = pathlib.Path(tmpdir) / "Plex Media Server.log"
            p2 = pathlib.Path(tmpdir) / "Plex Media Server.1.log.gz"
            p1.write_text("Aug 04, 2026 07:00:10.642 [1] DEBUG - Shutting down idle session 8a729f13-b95d-4aab-9700-5eab86bf88f2 (idle time is 180 seconds)\n")
            with gzip.open(p2, "wt", encoding="utf-8") as f:
                f.write("Aug 04, 2026 06:58:11.899 [2] WARN - Took too long (0.120000 seconds) to start a transaction on file.cpp:10\n")

            events = analyzer.analyze_path(tmpdir, threshold_ms=500)
            self.assertEqual(len(events), 2, f"Expected 2 events from .log and .log.gz files, got {len(events)}")
            self.assertEqual(events[0].time_only, "06:58:11.899")
            self.assertEqual(events[0].event_type, "TX_STALL")
            self.assertEqual(events[1].time_only, "07:00:10.642")
            self.assertEqual(events[1].event_type, "STREAM_DROP")

            single_events = analyzer.analyze_path(str(p2), threshold_ms=500)
            self.assertEqual(len(single_events), 1)
            self.assertEqual(single_events[0].event_type, "TX_STALL")


def main() -> int:
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyzePlexBlips)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: analyze_plex_blips unit tests passed")
        return 0
    print("FAIL: analyze_plex_blips unit tests failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
