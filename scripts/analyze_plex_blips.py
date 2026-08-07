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
    # Appended, with defaults, and appended rather than interleaved: LogEvent
    # carries no other default and is built POSITIONALLY at 28 sites (8 in this
    # module, 20 in its test file). Inserting either field above raw_line stops
    # the module importing outright ("non-default argument follows default
    # argument"), and appending without a default breaks all 28 constructions.
    # This is the placement that leaves every existing call site untouched.
    hold_site: Optional[str] = None
    live_connections: Optional[int] = None

    def __post_init__(self) -> None:
        """Derives live_connections from the event's own raw line.

        This is the analyzer's counterpart to the watchdog's `_event` helper,
        which computes the count ONCE at the top of check_trigger and stamps it
        onto whichever trigger fires. The count is a property of the LINE and
        not of any one taxonomy, so deriving it at the single point where every
        event is constructed is what keeps it from disagreeing with raw_line --
        and what lets the eight existing positional constructions stay as they
        are instead of each having to pass it.

        An explicitly supplied value wins, so a caller that already knows the
        count is never overruled. Unlike the watchdog's dict, where the key is
        absent when it does not apply, a dataclass field is always present, so
        "this line carries no count" is spelled None.
        """
        if self.live_connections is None:
            self.live_connections = extract_live_connections(self.raw_line)


PREFIX_RE = re.compile(
    r"^([A-Z][a-z]{2})\s+(\d{2}),\s+(\d{4})\s+(\d{2}:\d{2}:\d{2}(?:\.\d{3})?)\s+\[(\d+)\]\s+([A-Z]+)\s+-\s+(.*)$"
)
COMPLETED_RE = re.compile(
    r"Completed:\s+\[[^\]]+\]\s+\d+\s+(GET|POST|PUT|DELETE)\s+(\S+).*?\b(\d+)(?:\.\d+)?ms\b"
)
REQUEST_RE = re.compile(
    r"Request:\s+\[[^\]]+\]\s+(GET|POST|PUT|DELETE)\s+(\S+)"
)

# The holder side of a lock contention: the only signal Plex emits that names
# the offending code site in its own text. Unanchored on purpose -- a [Req#...]
# token sits in front of the message on 40 of the corpus's 42 holder lines, so
# anything anchored on the start of the message misses that whole world. The
# site group cannot contain ")" (it is a POSIX path plus ":<line>"), so [^)]+
# is exact rather than merely convenient.
#
# This and the two helpers below are deliberate verbatim mirrors of the
# watchdog's (ansible/roles/plex/files/plex_blip_watchdog.py): the two tools
# ship as separate units -- one deploys to CT 110 through Ansible, this one
# runs offline from the repo -- so neither can import the other. What keeps
# them from drifting into two spellings of one site is not this comment but
# test_the_analyzer_and_the_watchdog_name_the_same_hold_site, which parses the
# same line through both and asserts the results are equal.
HELD_TRANSACTION_RE = re.compile(
    r"Held transaction for too long \(([^)]+)\):\s*([0-9.]+)\s+seconds"
)

# The saturation counter that Request:/Completed: lines already carry.
LIVE_CONNECTIONS_RE = re.compile(r"\((\d+)\s+live\)")


def extract_live_connections(line: str) -> Optional[int]:
    """Reads the "(N live)" concurrent-connection count off a log line.

    Returns None when the line carries no count, which is the common case: the
    counter rides on Request:/Completed: lines only, and never on the WARN
    lines that carry the transaction signals.
    """
    m = LIVE_CONNECTIONS_RE.search(line)
    return int(m.group(1)) if m else None


def _basename_site(site: str) -> str:
    """Reduces a build-time source path to the "<file>:<line>" form.

    Plex compiles on a CI runner, so the site it prints is a 90-character
    absolute path under /home/runner/_work/... The useful identity is the last
    path component, and that is what every downstream report names. Idempotent
    on an already-bare site.
    """
    return site.rsplit("/", 1)[-1]


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

    # 1b. TX_HELD: the holder side of that same contention -- the only signal
    # Plex emits that names the code site holding the lock. TX_STALL says a
    # transaction gave up waiting; this says who it was waiting on.
    #
    # Lexically disjoint from TX_STALL rather than merely ordered after it:
    # "Held transaction for too long" contains "too long" but never "Took too
    # long", and no waiter line contains "Held transaction". If this branch
    # ever needs a particular position to be correct, the matcher is wrong --
    # asserted directly by the disjointness test, not left as an argument here.
    m_held = HELD_TRANSACTION_RE.search(msg)
    if m_held:
        return LogEvent(
            iso_ts,
            time_only,
            "TX_HELD",
            thread_id,
            float(m_held.group(2)) * 1000.0,
            msg,
            line,
            source_file,
            hold_site=_basename_site(m_held.group(1)),
        )

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

        # The two sides of one contention, kept apart on purpose. TX_STALL is
        # the WAITER side -- requests that gave up waiting -- and it is the only
        # side "Total Lock Delay Duration" has ever measured. TX_HELD is the
        # HOLDER side, the code site that was holding the lock they waited on.
        # Over the 2026-08-07 log the two are 32 events / 9450.0 ms against 42
        # events / 35210.0 ms: summing them would report a single number that
        # is true of neither, and printing only the first reads as a
        # contradiction (a small delay total next to large stalls) until you
        # see it is the ripple and not the stone.
        holder_events = [e for e in events if e.event_type == "TX_HELD"]
        waiter_events = [e for e in events if e.event_type == "TX_STALL"]
        total_hold_ms = sum(e.duration_ms for e in holder_events if e.duration_ms is not None)
        max_hold_ms = max([e.duration_ms for e in holder_events if e.duration_ms is not None], default=0.0)
        max_wait_ms = max([e.duration_ms for e in waiter_events if e.duration_ms is not None], default=0.0)

        # The saturation curve, read off the events that actually carry a
        # count. First and last are positional because analyze_path hands this
        # function a chronologically sorted list; the peak is computed, not
        # positional. None is spelled "n/a" rather than 0, because a range
        # whose events carry no count is not a range with no connections.
        counted_events = [e for e in events if e.live_connections is not None]
        if counted_events:
            peak_event = max(counted_events, key=lambda e: e.live_connections)
            live_curve_str = (
                f"{counted_events[0].live_connections} -> {peak_event.live_connections} -> "
                f"{counted_events[-1].live_connections} "
                f"(peak at {peak_event.time_only}, {len(counted_events)} counted events)"
            )
        else:
            live_curve_str = "n/a"

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
        lines.append(f"| Lock Waiters (TX_STALL) | {len(waiter_events)} events / {total_lock_delay_ms:.1f} ms |")
        lines.append(f"| Lock Holders (TX_HELD) | {len(holder_events)} events / {total_hold_ms:.1f} ms |")
        lines.append(f"| Maximum Query Latency | {max_query_latency_ms:.1f} ms |")
        lines.append(f"| Impacted Streaming Clients | {impacted_str} |")
        lines.append(f"| Correlated Triggers | {triggers_str} |")
        lines.append(f"| Live Connections (first -> peak -> last) | {live_curve_str} |\n")
        # Every row and section this footnote sends a reader to is named by its
        # LABEL, never by its position. The row beneath "Total Lock Delay
        # Duration" is "Lock Waiters (TX_STALL)" -- the same side, printing the
        # same number -- so "the row beneath it" pointed at the ripple, which is
        # the confusion this section exists to end. The breakdown is promised
        # only in the reports that render one: with no holders there is no
        # attribution table to send anyone to.
        footnote = (
            "*\"Total Lock Delay Duration\" is the WAITER side only (TX_STALL), kept at its "
            "original meaning and restated under a label that names the side by the "
            "\"Lock Waiters (TX_STALL)\" row. The holder side is the \"Lock Holders (TX_HELD)\" "
            "row. The two are compared under \"Lock Contention: Holders vs Waiters\""
        )
        if holder_events:
            footnote += ", which attributes the holders by code site under \"Holder Attribution by Code Site\""
        lines.append(footnote + ".*\n")

        counts: dict[str, int] = {}
        for e in events:
            counts[e.event_type] = counts.get(e.event_type, 0) + 1

        lines.append("## Event Counts by Taxonomy\n")
        lines.append("| Taxonomy | Count |")
        lines.append("| :--- | :--- |")
        # The five names below are printed in a fixed order, including at zero,
        # so the table's shape does not change with the corpus. Anything else
        # `counts` holds is printed after them: the header counts len(events)
        # while this table used to count five names, so every TX_HELD event was
        # invisible here -- 5811 in the header against 5748 tabulated over the
        # dated directory, 179 against 137 over the single 08-07 file. Adding
        # TX_HELD to the list would close today's gap and leave the defect, so
        # the table is now closed against the counts dict instead: whatever
        # taxonomy a future step introduces, the table still sums to the header.
        known_taxonomies = ["TX_STALL", "TX_HELD", "SLOW_QUERY", "STREAM_DROP", "SCHEDULED_TASK", "EXPORTER_SCRAPE"]
        for taxonomy in known_taxonomies:
            lines.append(f"| {taxonomy} | {counts.get(taxonomy, 0)} |")
        for taxonomy in sorted(k for k in counts if k not in known_taxonomies):
            lines.append(f"| {taxonomy} | {counts[taxonomy]} |")
        lines.append("")

        lines.append("## Lock Contention: Holders vs Waiters\n")
        lines.append("| Side | Events | Total Duration (ms) | Max (ms) |")
        lines.append("| :--- | :--- | :--- | :--- |")
        lines.append(f"| Holders (TX_HELD) | {len(holder_events)} | {total_hold_ms:.1f} | {max_hold_ms:.1f} |")
        lines.append(f"| Waiters (TX_STALL) | {len(waiter_events)} | {total_lock_delay_ms:.1f} | {max_wait_ms:.1f} |\n")

        if holder_events:
            first_holder = min(holder_events, key=lambda e: e.timestamp)
            first_dur = "-" if first_holder.duration_ms is None else f"{first_holder.duration_ms:.1f} ms"
            lines.append(
                f"**First holder**: {first_holder.timestamp} -- "
                f"{first_holder.hold_site or '(unattributed)'} ({first_dur})\n"
            )

            # Ranked by total time held, not by first appearance: over the
            # 08-07 log the first holder is StatisticsManager.cpp:288 at 2 of
            # 42 lines, while MetadataItemSetting.cpp:459 accounts for 27. A
            # breakdown ordered by time would name the first holder and hide
            # the loudest one.
            site_stats: dict[str, dict] = {}
            for e in holder_events:
                site = e.hold_site or "(unattributed)"
                st = site_stats.setdefault(site, {"count": 0, "total": 0.0, "max": 0.0, "first": e.timestamp})
                st["count"] += 1
                if e.duration_ms is not None:
                    st["total"] += e.duration_ms
                    st["max"] = max(st["max"], e.duration_ms)
                if e.timestamp < st["first"]:
                    st["first"] = e.timestamp

            lines.append("### Holder Attribution by Code Site\n")
            lines.append("| Hold Site | Events | Total Held (ms) | Max Held (ms) | First Seen |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for site, st in sorted(site_stats.items(), key=lambda kv: (-kv[1]["total"], -kv[1]["count"], kv[0])):
                lines.append(f"| {site} | {st['count']} | {st['total']:.1f} | {st['max']:.1f} | {st['first']} |")
            lines.append("")
        else:
            lines.append(
                "No TX_HELD holder events in this range; the counts above are the waiter side only.\n"
            )

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
