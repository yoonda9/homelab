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
import re
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

    # --- Step 2b: the holder side, mirrored from the watchdog ----------------
    #
    # Every fixture below is a VERBATIM line from
    # /tmp/plex-logs/2026-08-07/"Plex Media Server.log", copied in as an inline
    # literal. It is NOT read at test time, on purpose: /tmp is outside the
    # repo and absent on CT 110 and in any fresh checkout, and this very file
    # already carries two tests that go vacuously green from exactly that
    # mistake -- test_live_evidence_verification (:149) and
    # test_broken_pipe_handling (:217) read /tmp/plex-logs/Plex Media Server.log,
    # which does not exist, print SKIP and assert nothing inside a passing gate.
    # Repairing those two is filed separately; not adding a third is this row's
    # job, so every row below runs everywhere.
    #
    # Corpus counts measured over that file at this turn: 42 lines match
    # "Held transaction", 32 match "Took too long", 0 of the 42 holder lines
    # carry a "(N live)" count, and only 2 lines in the whole file carry
    # "(13 live)".

    # :3284 -- the genuine first holder of the 06:37 blip.
    HELD_STATISTICS_MANAGER = (
        "Aug 07, 2026 06:37:33.273 [132687902931768] WARN - Held transaction for "
        "too long (/home/runner/_work/plex-media-server/plex-media-server/"
        "Statistics/StatisticsManager.cpp:288): 0.540000 seconds"
    )
    # :3294 -- same message, but a [Req#...] prefix sits inside the message.
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
    # :3553 and :3552 -- the only two lines in the file carrying "(13 live)".
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
    # :3300 -- a Completed: line that DOES classify here (4977 ms >= 500) and
    # carries a count, which is what keeps live_connections from being a dead
    # field on this module's events.
    COMPLETED_SLOW_4_LIVE = (
        "Aug 07, 2026 06:37:39.377 [132688110742328] DEBUG - Completed: "
        "[192.168.1.208:43890] 200 GET /:/timeline?key=%2Flibrary%2Fmetadata%2F378"
        "&ratingKey=378&playQueueItemID=15310&duration=5568563&time=3039038"
        "&playbackTime=2001342&hasMDE=1&context=home%3AcontinueWatching&row=0"
        "&col=0&state=playing (4 live) #8ec76 TLS GZIP 4977ms 820 bytes "
        "(pipelined: 144)"
    )

    def test_the_genuine_holder_line_is_tx_held_with_the_measured_delay(self):
        ev = analyzer.parse_log_line(self.HELD_STATISTICS_MANAGER, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev, "the 06:37:33.273 holder line must parse")
        self.assertEqual(ev.event_type, "TX_HELD")
        # 0.540000 s x 1000 -- the same seconds->ms conversion TX_STALL uses.
        self.assertEqual(ev.duration_ms, 540.0)
        self.assertEqual(ev.hold_site, "StatisticsManager.cpp:288")
        self.assertEqual(ev.thread_id, "132687902931768")
        self.assertEqual(ev.time_only, "06:37:33.273")
        self.assertEqual(ev.raw_line, self.HELD_STATISTICS_MANAGER)

    def test_hold_site_is_basenamed_not_the_ci_build_path(self):
        # THE ONE THAT LOOKS RIGHT AND IS WRONG. Plex compiles on a CI runner,
        # so the parenthesised group in the raw line is a 90-character path
        # under /home/runner/_work/... Capturing it verbatim yields a
        # plausible-looking hold_site that fails the criterion, so this asserts
        # from both directions: the exact value, and the absence of what a
        # verbatim capture would have left behind.
        ev = analyzer.parse_log_line(self.HELD_STATISTICS_MANAGER, "test.log", threshold_ms=500)
        self.assertEqual(ev.hold_site, "StatisticsManager.cpp:288")
        self.assertNotIn("/", ev.hold_site, "hold_site must carry no path separator")
        self.assertNotIn("/home/runner", ev.hold_site)
        self.assertNotIn("plex-media-server", ev.hold_site)

    def test_a_req_prefixed_holder_line_still_yields_its_site(self):
        # 40 of the corpus's 42 holder lines put a [Req#...] token between the
        # level boundary and the message, so anything anchored on that boundary
        # misses that whole world.
        ev = analyzer.parse_log_line(self.HELD_METADATA_ITEM_SETTING, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev, "the [Req#8ec76] prefixed holder line must parse")
        self.assertEqual(ev.event_type, "TX_HELD")
        self.assertEqual(ev.duration_ms, 310.0)
        self.assertEqual(ev.hold_site, "MetadataItemSetting.cpp:459")

    def test_the_analyzer_and_the_watchdog_name_the_same_hold_site(self):
        # THE REASON THIS ROW WAS ORDERED AFTER THE WATCHDOG'S. Two hats
        # inventing two spellings of the same site is the failure the ordering
        # exists to prevent, and nothing catches it inside one module. Asserted
        # across both rather than argued in a comment: the analyzer's report
        # and the watchdog's snapshot must name ONE site.
        watchdog_dir = REPO_ROOT / "ansible" / "roles" / "plex" / "files"
        if str(watchdog_dir) not in sys.path:
            sys.path.insert(0, str(watchdog_dir))
        import plex_blip_watchdog as watchdog

        for label, line in (
            ("bare", self.HELD_STATISTICS_MANAGER),
            ("[Req#8ec76]", self.HELD_METADATA_ITEM_SETTING),
        ):
            with self.subTest(line=label):
                ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
                trigger = watchdog.check_trigger(line, threshold_ms=500.0)
                self.assertEqual(ev.event_type, trigger["event_type"])
                self.assertEqual(ev.hold_site, trigger["hold_site"])
                self.assertEqual(ev.duration_ms, trigger["delay_ms"])

    def test_a_real_waiter_line_is_still_tx_stall_with_no_hold_site(self):
        # REGRESSION. Both are real corpus lines, one bare and one [Req#...]
        # prefixed, and neither may acquire a hold_site -- TX_STALL names where
        # the waiter gave up waiting, which is not the holder's site.
        for label, line, duration in (
            ("bare", self.STALL_STATISTICS_BANDWIDTH, 110.0),
            ("[Req#8ecac]", self.STALL_STATISTICS_MEDIA, 160.0),
        ):
            with self.subTest(line=label):
                ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
                self.assertIsNotNone(ev, f"{label} waiter line must still parse")
                self.assertEqual(ev.event_type, "TX_STALL")
                self.assertEqual(ev.duration_ms, duration)
                self.assertIsNone(ev.hold_site)

    def test_the_two_transaction_matchers_are_lexically_disjoint(self):
        # The regression above is winnable WITHOUT reordering branches, and
        # this is the reason: the holder text contains "too long" but never
        # "Took too long", and no waiter line contains "Held transaction". If a
        # future edit needs the branches in a particular order to pass, the
        # matcher is wrong -- so disjointness is asserted through the module's
        # own matcher rather than left as an argument in a comment.
        for held in (self.HELD_STATISTICS_MANAGER, self.HELD_METADATA_ITEM_SETTING):
            self.assertIsNotNone(analyzer.HELD_TRANSACTION_RE.search(held))
            self.assertNotIn("Took too long", held)
            self.assertNotIn("to start a transaction", held)
        for stall in (self.STALL_STATISTICS_BANDWIDTH, self.STALL_STATISTICS_MEDIA):
            self.assertIsNone(analyzer.HELD_TRANSACTION_RE.search(stall))
            self.assertIn("Took too long", stall)
            self.assertIn("to start a transaction", stall)

    def test_live_connections_reads_the_count_off_the_real_13_live_lines(self):
        # Asserted on the extractor, not through parse_log_line, because only
        # two lines in the whole corpus carry "(13 live)" and this module
        # classifies NEITHER: :3553 is GET /status/sessions rather than a
        # /library/sections/../all scrape, and :3552 says "Completed after
        # connection close:", which the `msg.startswith("Completed:")` gate
        # does not admit. Both were re-parsed at this turn and returned None,
        # unchanged by this row -- so the count is pinned where it exists.
        self.assertEqual(analyzer.extract_live_connections(self.REQUEST_13_LIVE), 13)
        self.assertEqual(analyzer.extract_live_connections(self.COMPLETED_CLOSE_13_LIVE), 13)
        self.assertIsNone(analyzer.parse_log_line(self.REQUEST_13_LIVE, "test.log", threshold_ms=500))
        self.assertIsNone(analyzer.parse_log_line(self.COMPLETED_CLOSE_13_LIVE, "test.log", threshold_ms=500))

    def test_live_connections_rides_a_classified_event(self):
        # ...and the field is not dead on this module's events: this real
        # Completed: line does classify (4977 ms >= the 500 ms threshold) and
        # carries "(4 live)".
        ev = analyzer.parse_log_line(self.COMPLETED_SLOW_4_LIVE, "test.log", threshold_ms=500)
        self.assertIsNotNone(ev)
        self.assertEqual(ev.event_type, "SLOW_QUERY")
        self.assertEqual(ev.duration_ms, 4977.0)
        self.assertEqual(ev.live_connections, 4)

    def test_lines_with_no_live_count_leave_live_connections_none(self):
        # ANTI-VACUITY for the row above: a field that were always populated,
        # or always populated with the same number, would pass it just as well.
        # 0 of the corpus's 42 holder lines carry a count, so the holder side
        # is the honest negative case.
        for label, line in (
            ("holder", self.HELD_STATISTICS_MANAGER),
            ("waiter", self.STALL_STATISTICS_BANDWIDTH),
        ):
            with self.subTest(line=label):
                ev = analyzer.parse_log_line(line, "test.log", threshold_ms=500)
                self.assertIsNone(ev.live_connections)

    def test_the_reporting_layer_is_untouched_by_the_new_fields(self):
        # SCOPE FENCE, ARMED. format_output enumerates its keys by hand in both
        # the jsonl branch and the csv header, so adding LogEvent fields
        # changes no output -- which is correct HERE. Surfacing them is Step
        # 2c's reporting layer, and this row is what goes red when 2c does it,
        # at which point it is widened to the new key set rather than deleted.
        ev = analyzer.parse_log_line(self.COMPLETED_SLOW_4_LIVE, "test.log", threshold_ms=500)
        self.assertEqual(ev.live_connections, 4)
        data = json.loads(analyzer.format_output([ev], "jsonl").strip())
        self.assertEqual(
            set(data),
            {"timestamp", "time_only", "event_type", "duration_ms", "thread_id",
             "source_file", "details", "raw_line"},
            "Step 2b must not widen the reporting layer; that is Step 2c",
        )
        header = next(csv.reader(io.StringIO(analyzer.format_output([ev], "csv"))))
        self.assertEqual(len(header), 8, f"csv header widened outside Step 2c: {header}")

    # --- Step 2c: the report separates the stone from the ripple -------------
    #
    # Three more VERBATIM corpus lines, same rule as 2b's block: inline
    # literals, never read from /tmp at test time. Line numbers are into
    # /tmp/plex-logs/2026-08-07/"Plex Media Server.log".
    #
    # EVERY NUMBER ASSERTED BELOW WAS MEASURED AT THIS TURN over that file
    # (logs/builder-2c-corpus-measurements.log), not carried from plan.md:
    #   holders  42 events / 35210.0 ms   vs   waiters 32 events / 9450.0 ms
    #            -- the stone is 3.7x the ripple, and the report printed only
    #            the ripple, under a label ("Total Lock Delay Duration") that
    #            names neither side.
    #   sites    MetadataItemSetting.cpp:459 x27, MetadataItemSetting.cpp:409
    #            x13, StatisticsManager.cpp:288 x2 -- so the Demo's site is the
    #            FIRST holder and NOT the loudest, which is why the fixtures
    #            below deliberately put those two in conflict.
    #   header   179 events against a taxonomy table summing 137 -- 42 events
    #            (every TX_HELD) uncounted, because the table iterates a
    #            hardcoded five-name list.
    #   curve    over --start 06:37:00 --end 06:43:00: 4 -> 12 -> 3. NOT the
    #            5 -> 13 -> 3 of plan.md: 77 counted events in the file have
    #            min 2 / max 12, and the only two "(13 live)" lines in the
    #            corpus are the pair 2b pinned as unclassifiable.

    # :3387 and :3392 -- two more MetadataItemSetting.cpp:459 holders, which
    # make :459 outrank :288 by both count and total held time.
    HELD_METADATA_ITEM_SETTING_2 = (
        "Aug 07, 2026 06:38:49.891 [132687881837368] WARN - [Req#8ecb7] Held "
        "transaction for too long (/home/runner/_work/plex-media-server/"
        "plex-media-server/Library/MetadataItemSetting.cpp:459): 0.830000 seconds"
    )
    HELD_METADATA_ITEM_SETTING_3 = (
        "Aug 07, 2026 06:38:51.680 [132687879727928] WARN - [Req#8ec9d] Held "
        "transaction for too long (/home/runner/_work/plex-media-server/"
        "plex-media-server/Library/MetadataItemSetting.cpp:459): 1.110000 seconds"
    )
    # :3547 and :3616 -- the real peak and the real trough of the 06:37-06:43
    # saturation curve. Both classify (1763 ms and 774 ms are over threshold),
    # so the curve is readable off the event stream rather than off the file.
    COMPLETED_SLOW_12_LIVE = (
        "Aug 07, 2026 06:40:43.501 [132688110742328] DEBUG - Completed: "
        "[192.168.1.111:41040] 200 GET /identity (12 live) #8ecdd 1763ms 338 bytes"
    )
    COMPLETED_SLOW_3_LIVE = (
        "Aug 07, 2026 06:42:50.886 [132688110742328] DEBUG - Completed: "
        "[192.168.1.111:55372] 200 GET /activities (3 live) #8ed23 774ms 203 bytes"
    )

    def _parse_all(self, *lines):
        """Parses fixture lines into events, failing loudly on any that do not."""
        events = []
        for line in lines:
            ev = analyzer.parse_log_line(line, "Plex Media Server.log", threshold_ms=500)
            self.assertIsNotNone(ev, f"fixture line failed to classify: {line[:80]}")
            events.append(ev)
        return events

    @staticmethod
    def _section(out, heading):
        """Returns one '## <heading>' section of the report, up to the next '## '."""
        body = []
        collecting = False
        for line in out.splitlines():
            if line.startswith("## "):
                if collecting:
                    break
                collecting = line[3:].strip() == heading
                continue
            if collecting:
                body.append(line)
        return "\n".join(body)

    def _the_blip_slice(self):
        """The four holders, two waiters and three counted events, in log order."""
        return self._parse_all(
            self.HELD_STATISTICS_MANAGER,        # 06:37:33.273  :288    540.0 ms
            self.COMPLETED_SLOW_4_LIVE,          # 06:37:39.377   4 live
            self.HELD_METADATA_ITEM_SETTING,     # 06:37:36.346  :459    310.0 ms
            self.STALL_STATISTICS_BANDWIDTH,     # 06:38:22.285          110.0 ms
            self.STALL_STATISTICS_MEDIA,         # 06:38:27.179          160.0 ms
            self.HELD_METADATA_ITEM_SETTING_2,   # 06:38:49.891  :459    830.0 ms
            self.HELD_METADATA_ITEM_SETTING_3,   # 06:38:51.680  :459   1110.0 ms
            self.COMPLETED_SLOW_12_LIVE,         # 06:40:43.501  12 live
            self.COMPLETED_SLOW_3_LIVE,          # 06:42:50.886   3 live
        )

    def test_the_taxonomy_table_lists_tx_held_alongside_the_other_classes(self):
        out = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        table = self._section(out, "Event Counts by Taxonomy")
        self.assertIn("| TX_HELD | 4 |", table, f"TX_HELD missing from the taxonomy table:\n{table}")
        # ...without displacing the five classes that were already there.
        self.assertIn("| TX_STALL | 2 |", table)
        self.assertIn("| SLOW_QUERY | 3 |", table)
        self.assertIn("| STREAM_DROP | 0 |", table)
        self.assertIn("| SCHEDULED_TASK | 0 |", table)
        self.assertIn("| EXPORTER_SCRAPE | 0 |", table)

    def test_the_taxonomy_table_sums_to_the_headers_own_total(self):
        # THE REPORT MUST RECONCILE WITH ITSELF. Over the real 08-07 file the
        # header said 179 and this table said 137; over the dated directory,
        # 5811 against 5748. Adding TX_HELD to the hardcoded list closes
        # today's gap and leaves the defect, so the last event here carries a
        # taxonomy that is in NO list anywhere in the module: if the table is
        # still a fixed enumeration, this row is the one that goes missing.
        events = self._the_blip_slice()
        events.append(analyzer.LogEvent(
            "2026-08-07 06:42:59.000", "06:42:59.000", "PLUGIN_STALL", "132687902931768",
            None, "a class no enumeration in this module knows about", "raw", "Plex Media Server.log",
        ))
        out = analyzer.format_output(events, "markdown", window_sec=120.0)

        m = re.search(r"\*\*Total Events Matched\*\*:\s*(\d+)", out)
        self.assertIsNotNone(m, "the header total is missing from the report")
        header_total = int(m.group(1))
        self.assertEqual(header_total, len(events))

        rows = re.findall(r"^\|\s*([A-Z_]+)\s*\|\s*(\d+)\s*\|$", self._section(out, "Event Counts by Taxonomy"), re.M)
        tabulated = sum(int(n) for _, n in rows)
        self.assertEqual(
            tabulated, header_total,
            f"taxonomy table sums to {tabulated} but the header claims {header_total}; rows={rows}",
        )
        self.assertIn(("PLUGIN_STALL", "1"), rows, f"an unenumerated class went unreported: {rows}")

    def test_holders_and_waiters_are_counted_and_totalled_separately(self):
        # The sentence the report has to make true. One number over both
        # classes is the defect: 4 holders holding 2790.0 ms is a different
        # fact from 2 waiters delayed 270.0 ms, and the old report printed
        # only the second under a label that named neither.
        out = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        section = self._section(out, "Lock Contention: Holders vs Waiters")
        self.assertTrue(section.strip(), "no holders-vs-waiters section in the report")

        self.assertRegex(section, r"Holders \(TX_HELD\)\s*\|\s*4\s*\|\s*2790\.0")
        self.assertRegex(section, r"Waiters \(TX_STALL\)\s*\|\s*2\s*\|\s*270\.0")
        # And the waiter-only Executive Metric now says which side it measures,
        # rather than reading as the whole of lock contention.
        metrics = self._section(out, "Executive Metrics")
        self.assertIn("270.0 ms", metrics)
        self.assertRegex(metrics, r"Lock Holders \(TX_HELD\)\s*\|\s*4 events / 2790\.0 ms")
        self.assertRegex(metrics, r"Lock Waiters \(TX_STALL\)\s*\|\s*2 events / 270\.0 ms")

    def test_the_report_names_the_first_holder_by_its_basenamed_site(self):
        # THE DISCRIMINATOR, and it is not a grep for the site. The string
        # "StatisticsManager.cpp:288" is ALREADY in this report at the parent
        # sha -- four times over the real corpus -- because the timeline prints
        # `details`, and `details` carries the raw 90-character CI path. What
        # is zero times at the parent is the site NOT preceded by a slash.
        out = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        section = self._section(out, "Lock Contention: Holders vs Waiters")

        self.assertRegex(section, r"(?<!/)\bStatisticsManager\.cpp:288\b")
        self.assertRegex(section, r"06:37:33\.273")
        self.assertNotIn("/home/runner/", section, "the holder section must name sites basenamed, not by CI path")
        # Anti-vacuity: the pathed form is still in the report (the timeline
        # prints it), so the assertion above is about the new section and not
        # about the corpus.
        self.assertIn("/home/runner/", out)

    def test_the_holder_breakdown_ranks_the_loudest_site_not_only_the_first(self):
        # Over the real file :288 is 2 of 42 lines and MetadataItemSetting.cpp:459
        # is 27. A breakdown that names only the Demo's site names the first
        # holder and hides the loudest one, so the fixtures put the two in
        # conflict: :288 is first in time, :459 is 3 events / 2250.0 ms.
        out = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        section = self._section(out, "Lock Contention: Holders vs Waiters")

        self.assertRegex(section, r"MetadataItemSetting\.cpp:459\s*\|\s*3\s*\|\s*2250\.0")
        self.assertRegex(section, r"StatisticsManager\.cpp:288\s*\|\s*1\s*\|\s*540\.0")
        # Read the ORDER off the attribution table's own rows. Comparing raw
        # offsets in the section would be confounded by the "First holder"
        # line, which names :288 above the table by design and would make this
        # assertion pass or fail for a reason that is not the ranking.
        ranked = [
            row.split("|")[1].strip()
            for row in section.splitlines()
            if re.match(r"^\|\s*\S+\.cpp:\d+\s*\|", row)
        ]
        self.assertEqual(
            ranked, ["MetadataItemSetting.cpp:459", "StatisticsManager.cpp:288"],
            "the holder breakdown must rank by held time, so the loudest site is not hidden below the first one",
        )

    def test_the_live_connection_curve_is_reported_first_peak_last(self):
        # 4 -> 12 -> 3, the measured curve over 06:37:00-06:43:00 and the
        # honest replacement for plan.md's 5 -> 13 -> 3. These three fixtures
        # ARE the corpus's own first, peak and last counted events in that
        # window.
        out = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        metrics = self._section(out, "Executive Metrics")
        self.assertRegex(metrics, r"Live Connections.*\|.*4 -> 12 -> 3")
        self.assertIn("06:40:43.501", metrics)

    def test_a_range_with_no_holders_still_renders_and_says_so(self):
        # ANTI-VACUITY for every row above: a report that hardcoded the holder
        # prose would pass them all. Waiters only -> the section must render,
        # state that there are no holders, and not invent a peak connection
        # count out of a set of events that carries none.
        events = self._parse_all(self.STALL_STATISTICS_BANDWIDTH, self.STALL_STATISTICS_MEDIA)
        out = analyzer.format_output(events, "markdown", window_sec=120.0)
        section = self._section(out, "Lock Contention: Holders vs Waiters")

        self.assertRegex(section, r"Holders \(TX_HELD\)\s*\|\s*0\s*\|\s*0\.0")
        self.assertRegex(section, r"Waiters \(TX_STALL\)\s*\|\s*2\s*\|\s*270\.0")
        self.assertNotIn(".cpp:", section)
        self.assertIn("| TX_HELD | 0 |", self._section(out, "Event Counts by Taxonomy"))
        self.assertRegex(self._section(out, "Executive Metrics"), r"Live Connections.*\|\s*n/a\s*\|")

    # --- Step 2c round 2: the columns the round-1 guards stopped short of ----
    #
    # The block above ships NINE new numeric report cells and pins FIVE. Every
    # assertion in it has the shape `assertRegex(section, r"Holders
    # \(TX_HELD\)\s*\|\s*4\s*\|\s*2790\.0")` -- row-shaped, and it ends at the
    # second cell. A mutation run over the delivered code (round 1's own
    # numbers, logs/critic-2c-mutants.log) put five mutants through it green:
    #   M06  max_hold_ms = 0.0                       the Holders row's Max cell
    #   M07  max_wait_ms = 0.0                       the Waiters row's Max cell
    #   M08  "Max Held (ms)" prints the TOTAL        on the real corpus that is
    #        MetadataItemSetting.cpp:459 at 24170.0 where 2510.0 is true -- a
    #        10x wrong number in a shipped report, suite green
    #   M09  "First Seen" prints the LAST seen       independent of the
    #        **First holder** line, which has its own min() and IS guarded
    #   M13  the no-holders sentence deleted         in a test whose own NAME
    #        is "..._still_renders_and_says_so"; only the renders half is
    #        asserted
    # The repair is ADDITIVE ONLY -- new methods below, no line above touched
    # -- because acceptance 3 forbids modifying a test line, so the weak
    # assertions stay exactly where they are and these stand beside them.
    #
    # The fix for the shape is to stop matching a prefix of a row and start
    # comparing the row's CELLS by identity: a prefix match cannot fail on a
    # column it never reaches.

    @staticmethod
    def _row_cells(section, label):
        """Returns one markdown table row's cells, split and stripped.

        `label` is matched against the row's FIRST cell by equality, so a row
        is addressed by its own name rather than by an offset into the table.
        Returns None when no row carries that label.
        """
        for line in section.splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0] == label:
                return cells
        return None

    def test_every_cell_of_the_holders_and_waiters_rows_is_pinned(self):
        # M06 and M07. The fixtures make max != total on BOTH sides on purpose
        # (1110.0 of 2790.0 held; 160.0 of 270.0 waited), so a Max column that
        # printed the total, or zero, is red here rather than green by
        # coincidence.
        out = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        section = self._section(out, "Lock Contention: Holders vs Waiters")

        holders = self._row_cells(section, "Holders (TX_HELD)")
        waiters = self._row_cells(section, "Waiters (TX_STALL)")
        self.assertEqual(holders, ["Holders (TX_HELD)", "4", "2790.0", "1110.0"], f"section:\n{section}")
        self.assertEqual(waiters, ["Waiters (TX_STALL)", "2", "270.0", "160.0"], f"section:\n{section}")
        self.assertNotEqual(holders[2], holders[3], "fixture no longer separates the held total from the held max")
        self.assertNotEqual(waiters[2], waiters[3], "fixture no longer separates the waited total from the waited max")

    def test_every_cell_of_the_holder_attribution_rows_is_pinned(self):
        # M08 and M09, and the fixture discriminates both at once:
        # MetadataItemSetting.cpp:459 is 3 events over 2250.0 ms whose worst
        # single hold is 1110.0 ms (so Max != Total) and whose first sighting
        # 06:37:36.346 is not its last 06:38:51.680 (so First != Last).
        out = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        section = self._section(out, "Lock Contention: Holders vs Waiters")

        loudest = self._row_cells(section, "MetadataItemSetting.cpp:459")
        first = self._row_cells(section, "StatisticsManager.cpp:288")
        self.assertEqual(
            loudest,
            ["MetadataItemSetting.cpp:459", "3", "2250.0", "1110.0", "2026-08-07 06:37:36.346"],
            f"section:\n{section}",
        )
        self.assertEqual(
            first,
            ["StatisticsManager.cpp:288", "1", "540.0", "540.0", "2026-08-07 06:37:33.273"],
            f"section:\n{section}",
        )
        self.assertNotEqual(loudest[2], loudest[3], "fixture no longer separates a site's total from its max")
        self.assertNotIn("06:38:51.680", section, "First Seen is showing the site's LAST sighting")

    def test_every_cell_of_the_live_connection_curve_is_pinned(self):
        # The curve cell carries a fourth number nothing reads: how many events
        # the curve was computed over. 3 of the 9 fixture events carry a count,
        # and a curve quoted without that denominator cannot be told from one
        # computed over two events.
        out = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        metrics = self._section(out, "Executive Metrics")

        self.assertEqual(
            self._row_cells(metrics, "Live Connections (first -> peak -> last)"),
            ["Live Connections (first -> peak -> last)", "4 -> 12 -> 3 (peak at 06:40:43.501, 3 counted events)"],
            f"metrics:\n{metrics}",
        )

    def test_the_no_holder_range_says_so_in_words_and_promises_no_breakdown(self):
        # M13, the missing half of test_a_range_with_no_holders_still_renders_
        # and_says_so: that test asserts the zero rows and never the sentence,
        # so deleting the sentence leaves the suite green and the reader with
        # a holder table of zeroes and no statement of why.
        events = self._parse_all(self.STALL_STATISTICS_BANDWIDTH, self.STALL_STATISTICS_MEDIA)
        out = analyzer.format_output(events, "markdown", window_sec=120.0)
        section = self._section(out, "Lock Contention: Holders vs Waiters")

        self.assertIn("No TX_HELD holder events in this range", section, f"section:\n{section}")
        self.assertNotIn("Holder Attribution by Code Site", out, "an empty breakdown section rendered anyway")
        # Anti-vacuity: hardcoding that sentence into every report would pass
        # the line above, so the same two claims must be FALSE when holders
        # exist.
        with_holders = analyzer.format_output(self._the_blip_slice(), "markdown", window_sec=120.0)
        self.assertNotIn("No TX_HELD holder events", with_holders)
        self.assertIn("Holder Attribution by Code Site", with_holders)

    def test_the_executive_footnote_points_at_rows_and_sections_that_exist(self):
        # THE ONE SENTENCE IN THE REPORT WHOSE JOB IS TO PREVENT THE CONFUSION
        # THIS ROW EXISTS TO END, and round 1 shipped it pointing at the wrong
        # row: "the holder side is the row beneath it". The row beneath
        # "Total Lock Delay Duration" is "Lock Waiters (TX_STALL)" -- the SAME
        # side, printing the SAME number. The holder row is two beneath. A
        # reader who follows the pointer lands back on the ripple.
        #
        # So the footnote addresses rows and sections by LABEL, never by
        # position, and this test holds it to the report it is printed in:
        # every name it quotes must be a row or a heading of THAT report. That
        # also settles the second half of the charge -- the footnote promised a
        # code-site breakdown that does not render when there are no holders.
        no_holders = self._parse_all(self.STALL_STATISTICS_BANDWIDTH, self.STALL_STATISTICS_MEDIA)
        for label, events in (("with holders", self._the_blip_slice()), ("no holders", no_holders)):
            with self.subTest(corpus=label):
                out = analyzer.format_output(events, "markdown", window_sec=120.0)
                footnote = next(
                    (l for l in out.splitlines() if l.startswith('*"Total Lock Delay Duration"')), ""
                )
                self.assertTrue(footnote, f"no Executive Metrics footnote in the {label} report")

                self.assertNotRegex(
                    footnote, r"\brow (beneath|below|above|under) it\b",
                    "the footnote points at a row by position; the row beneath the waiter total "
                    "is the waiter row, so a positional pointer sends the reader to the wrong side",
                )
                quoted = re.findall(r'"([^"]+)"', footnote)
                self.assertIn(
                    "Lock Holders (TX_HELD)", quoted,
                    f"the footnote must name the holder row by its own label; quoted={quoted}",
                )
                headings = [l.lstrip("#").strip() for l in out.splitlines() if l.startswith("#")]
                for name in quoted:
                    self.assertTrue(
                        f"| {name} |" in out or name in headings,
                        f"the footnote quotes {name!r}, which is no row and no heading of the "
                        f"{label} report it is printed in",
                    )

    # --- Step 2c round 3: the lines in the section that are NOT table rows ---
    #
    # Round 2 replaced every row-shaped prefix match with a cell-by-cell
    # equality, on the finding that A PREFIX MATCH CANNOT FAIL ON A COLUMN IT
    # NEVER REACHES. The sibling half, and the residue that finding left
    # behind: A SECTION-SCOPED MATCH CANNOT FAIL ON A LINE THAT ANOTHER LINE IN
    # THE SAME SECTION SATISFIES. Every guard round 2 strengthened addresses a
    # table ROW; the one line of this section that is not a row was left with
    # no guard of its own. The two assertions aimed at it --
    #     assertRegex(section, r"(?<!/)\bStatisticsManager\.cpp:288\b")
    #     assertRegex(section, r"06:37:33\.273")
    # -- are BOTH satisfied by the attribution table's own row,
    #     | StatisticsManager.cpp:288 | 1 | 540.0 | 540.0 | 2026-08-07 06:37:33.273 |
    # so they cannot tell the prose line from its neighbour:
    #   N01  the whole **First holder** line DELETED          survived, green
    #        -- and that line carries acceptance 5's own sentence, so the row's
    #        Demo claim could be deleted outright with nothing red
    #   N02  its duration prints the ALL-HOLDER total         survived, green
    #        -- 2790.0 here, and on the real corpus it ships "(35210.0 ms)"
    #        where 540.0 ms is true: 65x wrong under a green suite, which is
    #        round 1's M08 (10x wrong, green) one container up
    # The line's duration was a TENTH numeric value that no census in this row
    # ever counted, because the censuses counted table cells.
    #
    # The cheap discriminator is to MUTATE BY DELETION FIRST: a line whose
    # deletion is green has no guard of its own, however many regexes mention
    # its content. So this pins the section's non-table lines as a CLOSED SET
    # by equality -- the same closure move the taxonomy table got, and the
    # reason it is a set rather than the one charged line: the no-holders
    # sentence is guarded by an assertIn of its first clause only, so its
    # second clause ("the counts above are the waiter side only") could be
    # dropped green too. Additive as before: no line above is touched.

    @staticmethod
    def _non_table_lines(section):
        """Every line of a section that is not a markdown table row."""
        return [l for l in section.splitlines() if l.strip() and not l.strip().startswith("|")]

    def test_every_non_table_line_of_the_contention_section_is_pinned(self):
        # N01 and N02, and the whole class they belong to, at both corpora.
        events = self._the_blip_slice()
        section = self._section(
            analyzer.format_output(events, "markdown", window_sec=120.0),
            "Lock Contention: Holders vs Waiters",
        )
        self.assertEqual(
            self._non_table_lines(section),
            [
                "**First holder**: 2026-08-07 06:37:33.273 -- StatisticsManager.cpp:288 (540.0 ms)",
                "### Holder Attribution by Code Site",
            ],
            f"section:\n{section}",
        )

        no_holders = self._parse_all(self.STALL_STATISTICS_BANDWIDTH, self.STALL_STATISTICS_MEDIA)
        nh_section = self._section(
            analyzer.format_output(no_holders, "markdown", window_sec=120.0),
            "Lock Contention: Holders vs Waiters",
        )
        self.assertEqual(
            self._non_table_lines(nh_section),
            ["No TX_HELD holder events in this range; the counts above are the waiter side only."],
            f"section:\n{nh_section}",
        )

        # Anti-vacuity, so a later fixture edit cannot leave the equalities
        # above true by coincidence. The first holder's own 540.0 ms must be
        # neither number the Holders row prints (2790.0 total / 1110.0 max),
        # or N02 and a print-the-max variant would both pass; and the first
        # holder must not also be the last, or min() and max() agree.
        holders = self._row_cells(section, "Holders (TX_HELD)")
        self.assertNotIn(
            "540.0", holders[2:],
            f"fixture no longer separates the first holder's duration from the holder totals: {holders}",
        )
        held = sorted(e.timestamp for e in events if e.event_type == "TX_HELD")
        self.assertNotEqual(held[0], held[-1], "fixture no longer separates the first holder from the last")



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
