#!/usr/bin/env python3
"""Offline log analysis tool for debugging Plex heartbeat blips.

Parses Plex Media Server logs using multiple threads to correlate SQLite
lock contention, slow queries, scheduled library maintenance, exporter scrapes,
and streaming disconnects into structured chronological reports and rolling
correlation clusters.
"""

import argparse
import bisect
import concurrent.futures
import csv
import gzip
import io
import json
import os
import pathlib
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class LogEvent:
    timestamp: str
    time_only: str
    event_type: str
    thread_id: str
    duration_ms: Optional[float]
    details: str
    raw_line: str
    source_file: str


PREFIX_RE = re.compile(
    r"^([A-Z][a-z]{2})\s+(\d{2}),\s+(\d{4})\s+(\d{2}:\d{2}:\d{2}(?:\.\d{3})?)\s+\[(\d+)\]\s+([A-Z]+)\s+-\s+(.*)$"
)
COMPLETED_RE = re.compile(
    r"Completed:\s+\[[^\]]+\]\s+\d+\s+(GET|POST|PUT|DELETE)\s+(\S+).*?\b(\d+)(?:\.\d+)?ms\b"
)
REQUEST_RE = re.compile(
    r"Request:\s+\[[^\]]+\]\s+(GET|POST|PUT|DELETE)\s+(\S+)"
)

MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}


def parse_log_line(line: str, source_file: str, threshold_ms: float = 500.0) -> Optional[LogEvent]:
    line = line.rstrip("\r\n")
    m = PREFIX_RE.match(line)
    if not m:
        return None

    month, day, year, time_str, thread_id, level, msg = m.groups()
    month_num = MONTH_MAP.get(month, "01")
    iso_ts = f"{year}-{month_num}-{day.zfill(2)} {time_str}"
    time_only = time_str

    # 1. TX_STALL: SQLite transaction start delays
    if "Took too long" in msg and "to start a transaction" in msg:
        m_dur = re.search(r"Took too long \(([0-9.]+)\s+seconds\)", msg)
        duration = float(m_dur.group(1)) * 1000.0 if m_dur else None
        return LogEvent(iso_ts, time_only, "TX_STALL", thread_id, duration, msg, line, source_file)

    # 2. STREAM_DROP: Timeout of streaming resources or job termination
    if "Shutting down idle session" in msg:
        m_dur = re.search(r"idle time is (\d+)\s+seconds", msg)
        duration = float(m_dur.group(1)) * 1000.0 if m_dur else None
        return LogEvent(iso_ts, time_only, "STREAM_DROP", thread_id, duration, msg, line, source_file)
    elif any(k in msg for k in ("Killing job", "signal: Killed", "Terminated session", "Stopping transcode session")):
        return LogEvent(iso_ts, time_only, "STREAM_DROP", thread_id, None, msg, line, source_file)

    # 3. SCHEDULED_TASK: Top-of-hour library maintenance
    if "scheduled library update" in msg or "starting scheduled library update" in msg:
        return LogEvent(iso_ts, time_only, "SCHEDULED_TASK", thread_id, None, msg, line, source_file)

    # 4. SLOW_QUERY: Explicit slow query warnings
    if "SLOW QUERY:" in msg:
        m_dur = re.search(r"It took ([0-9.]+)\s+ms", msg)
        duration = float(m_dur.group(1)) if m_dur else None
        return LogEvent(iso_ts, time_only, "SLOW_QUERY", thread_id, duration, msg, line, source_file)

    # 5. Completed queries -> SLOW_QUERY if duration >= threshold_ms, else check EXPORTER_SCRAPE
    if msg.startswith("Completed:"):
        m_comp = COMPLETED_RE.search(msg)
        if m_comp:
            method, endpoint, dur_str = m_comp.groups()
            duration = float(dur_str)
            if duration >= threshold_ms:
                return LogEvent(iso_ts, time_only, "SLOW_QUERY", thread_id, duration, msg, line, source_file)
            elif "/library/sections/" in endpoint and endpoint.endswith("/all"):
                return LogEvent(iso_ts, time_only, "EXPORTER_SCRAPE", thread_id, duration, msg, line, source_file)

    # 6. Request queries -> EXPORTER_SCRAPE
    if msg.startswith("Request:"):
        m_req = REQUEST_RE.search(msg)
        if m_req:
            method, endpoint = m_req.groups()
            if "/library/sections/" in endpoint and "/all" in endpoint:
                return LogEvent(iso_ts, time_only, "EXPORTER_SCRAPE", thread_id, None, msg, line, source_file)

    return None


def filter_events(events: List[LogEvent], start: Optional[str] = None, end: Optional[str] = None) -> List[LogEvent]:
    filtered = []
    for e in events:
        if start:
            target = e.time_only if ("-" not in start and " " not in start) else e.timestamp
            if target < start:
                continue
        if end:
            target = e.time_only if ("-" not in end and " " not in end) else e.timestamp
            comp_end = end if ("." in end or len(end) > 8) else f"{end}.999999"
            if target > comp_end:
                continue
        filtered.append(e)
    return filtered


def _parse_file(fpath: pathlib.Path, threshold_ms: float = 500.0) -> List[LogEvent]:
    events: List[LogEvent] = []
    try:
        if fpath.name.endswith(".gz") or fpath.suffix == ".gz":
            file_ctx = gzip.open(fpath, "rt", encoding="utf-8", errors="replace")
        else:
            file_ctx = fpath.open("r", encoding="utf-8", errors="replace")
        with file_ctx as f:
            for line in f:
                ev = parse_log_line(line, fpath.name, threshold_ms=threshold_ms)
                if ev:
                    events.append(ev)
    except (OSError, EOFError):
        pass
    return events


def analyze_path(path_str: str, start: Optional[str] = None, end: Optional[str] = None, threshold_ms: float = 500.0) -> List[LogEvent]:
    p = pathlib.Path(path_str)
    if not p.exists():
        raise FileNotFoundError(f"Log path not found: {path_str}")

    if p.is_dir():
        files_to_read = sorted(list(p.glob("*.log")) + list(p.glob("*.log.gz")))
    else:
        files_to_read = [p]

    events: List[LogEvent] = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(_parse_file, fpath, threshold_ms) for fpath in files_to_read]
        for fut in concurrent.futures.as_completed(futures):
            events.extend(fut.result())

    events.sort(key=lambda x: (x.timestamp, x.raw_line))
    return filter_events(events, start=start, end=end)


def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace(" ", "T"))
    except Exception:
        return datetime.min


def correlate_events(events: List[LogEvent], window_sec: float = 120.0) -> List[List[LogEvent]]:
    if not events:
        return []

    anomalies = [e for e in events if e.event_type in ("TX_STALL", "SLOW_QUERY", "STREAM_DROP")]
    if not anomalies:
        return []

    anom_times = [_parse_ts(a.timestamp).timestamp() for a in anomalies]
    relevant_events = []
    for ev in events:
        t_ev = _parse_ts(ev.timestamp).timestamp()
        idx = bisect.bisect_left(anom_times, t_ev)
        matched = False
        if idx < len(anom_times) and abs(anom_times[idx] - t_ev) <= window_sec:
            matched = True
        elif idx > 0 and abs(t_ev - anom_times[idx - 1]) <= window_sec:
            matched = True
        if matched:
            relevant_events.append(ev)

    if not relevant_events:
        return []

    clusters: List[List[LogEvent]] = []
    for ev in relevant_events:
        if not clusters:
            clusters.append([ev])
            continue

        current_cluster = clusters[-1]
        last_ev = current_cluster[-1]
        t_last = _parse_ts(last_ev.timestamp)
        t_curr = _parse_ts(ev.timestamp)

        diff_sec = (t_curr - t_last).total_seconds()
        if 0 <= diff_sec <= window_sec:
            current_cluster.append(ev)
        else:
            clusters.append([ev])

    final_clusters = [c for c in clusters if any(e.event_type in ("TX_STALL", "SLOW_QUERY", "STREAM_DROP") for e in c)]
    return final_clusters


def format_output(events: List[LogEvent], format_type: str, start: Optional[str] = None, end: Optional[str] = None, window_sec: float = 120.0) -> str:
    if format_type == "jsonl":
        lines = []
        for e in events:
            d = {
                "timestamp": e.timestamp,
                "time_only": e.time_only,
                "event_type": e.event_type,
                "duration_ms": e.duration_ms,
                "thread_id": e.thread_id,
                "source_file": e.source_file,
                "details": e.details,
                "raw_line": e.raw_line,
            }
            lines.append(json.dumps(d))
        return "\n".join(lines) + ("\n" if lines else "")

    elif format_type == "csv":
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["timestamp", "time_only", "event_type", "duration_ms", "thread_id", "source_file", "details", "raw_line"])
        for e in events:
            writer.writerow([
                e.timestamp,
                e.time_only,
                e.event_type,
                "" if e.duration_ms is None else str(e.duration_ms),
                e.thread_id,
                e.source_file,
                e.details,
                e.raw_line,
            ])
        return out.getvalue()

    elif format_type == "both":
        summary_out = format_output(events, "markdown", start=start, end=end, window_sec=window_sec)
        jsonl_out = format_output(events, "jsonl", start=start, end=end, window_sec=window_sec)
        return f"{summary_out}\n--- JSONL Events ---\n{jsonl_out}"

    else:
        # summary or markdown format
        lines = []
        lines.append("# Plex Blip Analysis Summary\n")
        range_str = f"**Time Range**: {start or 'start'} to {end or 'end'}"
        if not start and not end and events:
            range_str = f"**Time Range**: {events[0].timestamp} to {events[-1].timestamp}"
        lines.append(range_str)
        lines.append(f"**Total Events Matched**: {len(events)}\n")

        total_lock_delay_ms = sum(e.duration_ms for e in events if e.event_type == "TX_STALL" and e.duration_ms is not None)
        max_query_latency_ms = max([e.duration_ms for e in events if e.event_type == "SLOW_QUERY" and e.duration_ms is not None], default=0.0)

        impacted_sessions = set()
        stream_drops_count = 0
        for e in events:
            if e.event_type == "STREAM_DROP":
                stream_drops_count += 1
                m = re.search(r"session\s+([^\s\(\),]+)", e.details, re.IGNORECASE)
                if m:
                    impacted_sessions.add(m.group(1))

        if impacted_sessions:
            impacted_str = f"{len(impacted_sessions)} ({', '.join(sorted(list(impacted_sessions)))})"
        elif stream_drops_count > 0:
            impacted_str = f"{stream_drops_count} (unnamed)"
        else:
            impacted_str = "0 (None)"

        clusters = correlate_events(events, window_sec=window_sec)
        triggers = set()
        for c in clusters:
            for ce in c:
                if ce.event_type in ("EXPORTER_SCRAPE", "SCHEDULED_TASK"):
                    triggers.add(ce.event_type)
        triggers_str = ", ".join(sorted(list(triggers))) if triggers else "None"

        lines.append("## Executive Metrics\n")
        lines.append("| Metric | Value |")
        lines.append("| :--- | :--- |")
        lines.append(f"| Total Lock Delay Duration | {total_lock_delay_ms:.1f} ms ({total_lock_delay_ms / 1000.0:.2f} s) |")
        lines.append(f"| Maximum Query Latency | {max_query_latency_ms:.1f} ms |")
        lines.append(f"| Impacted Streaming Clients | {impacted_str} |")
        lines.append(f"| Correlated Triggers | {triggers_str} |\n")

        counts: dict[str, int] = {}
        for e in events:
            counts[e.event_type] = counts.get(e.event_type, 0) + 1

        lines.append("## Event Counts by Taxonomy\n")
        lines.append("| Taxonomy | Count |")
        lines.append("| :--- | :--- |")
        for taxonomy in ["TX_STALL", "SLOW_QUERY", "STREAM_DROP", "SCHEDULED_TASK", "EXPORTER_SCRAPE"]:
            lines.append(f"| {taxonomy} | {counts.get(taxonomy, 0)} |")
        lines.append("")

        lines.append(f"## Correlated Event Clusters (Window: {window_sec:.1f}s)\n")
        multi_clusters = [c for c in clusters if len(c) >= 2]
        if multi_clusters:
            for idx, cluster in enumerate(multi_clusters, start=1):
                t_first = _parse_ts(cluster[0].timestamp)
                t_last = _parse_ts(cluster[-1].timestamp)
                span = (t_last - t_first).total_seconds()
                lines.append(f"### Cluster {idx} (Span: {span:.1f}s, Events: {len(cluster)})\n")
                lines.append("| Timestamp | Event Type | Duration (ms) | Thread ID | Details |")
                lines.append("| :--- | :--- | :--- | :--- | :--- |")
                for ce in cluster:
                    dur_str = f"{ce.duration_ms:.1f}" if ce.duration_ms is not None else "-"
                    details_esc = ce.details.replace("|", "&#124;")
                    lines.append(f"| {ce.timestamp} | {ce.event_type} | {dur_str} | {ce.thread_id} | {details_esc} |")
                lines.append("")
        else:
            lines.append("No multi-event correlation clusters found.\n")

        lines.append("## Chronological Timeline of Events\n")
        lines.append("| Timestamp | Event Type | Duration (ms) | Thread ID | Details |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for e in events:
            dur_str = f"{e.duration_ms:.1f}" if e.duration_ms is not None else "-"
            details_esc = e.details.replace("|", "&#124;")
            lines.append(f"| {e.timestamp} | {e.event_type} | {dur_str} | {e.thread_id} | {details_esc} |")
        lines.append("")

        return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Plex heartbeat blip offline log analysis tool.")
    parser.add_argument("path", nargs="?", default=None, help="Path to log file or directory")
    parser.add_argument("--log-dir", dest="log_dir", help="Path to log file or directory (alias for positional path)")
    parser.add_argument("--format", "--output-format", dest="format", choices=["summary", "markdown", "jsonl", "csv", "both"], default="summary", help="Output format (default: summary)")
    parser.add_argument("--start", "--start-time", dest="start", help="Start timestamp filter (e.g. 06:57:00)")
    parser.add_argument("--end", "--end-time", dest="end", help="End timestamp filter (e.g. 07:01:00)")
    parser.add_argument("--threshold-ms", type=float, default=500.0, help="Latency threshold in ms for slow queries (default: 500)")
    parser.add_argument("--correlation-window", "--window-sec", dest="window_sec", type=float, default=120.0, help="Rolling correlation window in seconds (default: 120.0)")

    args = parser.parse_args()
    target_path = args.log_dir or args.path or "/tmp/plex-logs"
    try:
        events = analyze_path(target_path, start=args.start, end=args.end, threshold_ms=args.threshold_ms)
        output = format_output(events, args.format, start=args.start, end=args.end, window_sec=args.window_sec)
        sys.stdout.write(output)
        sys.stdout.flush()
        return 0
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 0
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Error executing log analysis: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
