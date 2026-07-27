#!/usr/bin/env python3
"""Re-runnable Plex latency harness (Step 1a of the Plex optimization plan).

`.agents/planning/2026-07-27-plex-optimization/implementation/plan.md` Step 1
asks for a **baseline** of TTFB + total load time for the Plex API/UI that Step 4
can be compared against. A number typed into a document once is not comparable;
the same script run twice is. This is that script.

What it measures, and why in this shape:

* **A controlled A/B.** Every run probes the same endpoint twice — once through
  Traefik on :443 (`https://<host>/identity`) and once straight at the backend
  (`http://<ip>:32400/identity`). The design names Traefik as the remaining
  suspect for the slow initial library load, and "Traefik is slow" is only a
  testable claim as the *difference* between those two legs. One leg alone
  measures the internet.
* **Labelled and vantage-stamped.** `--label` separates `baseline` from
  `post-change`; `--vantage` records whether the run came from the LAN or from
  an external network. Both are mandatory because the plan's baseline is
  definitionally an off-LAN measurement, and a LAN run silently filed as the
  baseline would make Step 4's comparison meaningless.
* **Append-only JSONL.** Each run appends one record to `logs/plex-latency.jsonl`
  so runs accumulate and stay machine-diffable.

Safety properties, by construction:

* read-only `GET`s against endpoints the operator already exposes; it never
  mutates Plex state,
* one attempt per sample — **no retries**, so a sick server is never hammered,
* an explicit connect/read timeout on every request,
* the Plex token is read from the ``PLEX_TOKEN`` environment variable and from
  nowhere else. There is deliberately no `--token` flag (it would land in shell
  history) and no repo-file fallback (the repo has a no-plaintext-secrets rule).
  The token is sent as a header, and is never written to the JSONL or printed.

Stdlib only, matching repo convention (`scripts/run_gate.py` and the shape
tests). `scripts/test_plex_latency_harness_shape.py` pins the properties above;
it drives the pipeline below with an injected prober, which is why
`run_measurement` takes a `probe` argument.

A failed request is a measurement of NOTHING: it contributes to neither the TTFB
series nor the total series, so the two always summarise the same samples. How
long the failure took to surface is kept separately as `failed_after_ms` — it is
a diagnostic, not a latency, because on a timeout it is just `--timeout`.

Usage::

    export PLEX_TOKEN=...            # optional; adds the library endpoints
    python scripts/measure_plex_latency.py --label baseline --vantage external

Exit codes: ``0`` measured everything it set out to; ``1`` at least one target
returned no successful sample (the record is still written first, so nothing is
lost); ``2`` bad arguments. From an external vantage the direct leg is RFC1918
and cannot answer, so pass ``--skip-direct`` there — otherwise a correct capture
spends ``repeats x timeout`` hanging and then exits 1.

See `docs/runbooks/plex-latency-baseline.md` for the off-LAN procedure.
"""

import argparse
import datetime
import http.client
import json
import os
import pathlib
import statistics
import sys
import time
import urllib.parse

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Bumped when the record layout changes, so Step 4 can refuse to diff across
#: incompatible shapes rather than silently comparing different things.
#: v2 — failed samples no longer contribute a `total_ms`; targets gained
#: `succeeded`/`failed`; records gained `direct_probed`.
SCHEMA_VERSION = 2

#: The token comes from here and from nowhere else. See the module docstring.
TOKEN_ENV = "PLEX_TOKEN"
TOKEN_HEADER = "X-Plex-Token"

#: Defaults mirror the repo's own configuration: `domain` in
#: ansible/group_vars/all/vars.yml and `docker_host_plex_url` in
#: ansible/roles/docker_host/defaults/main.yml. Both are overridable so the
#: harness is usable against any Plex, not just this household's.
DEFAULT_HOST = "plex.yoonnation.com"
DEFAULT_DIRECT = "192.168.1.110:32400"

DEFAULT_REPEATS = 5
DEFAULT_TIMEOUT = 10.0
DEFAULT_LOG = REPO_ROOT / "logs" / "plex-latency.jsonl"

VANTAGES = ("lan", "external")

VIA_TRAEFIK = "traefik"
VIA_DIRECT = "direct"

#: `/identity` is unauthenticated and cheap — the clean TTFB comparison.
UNAUTH_PATH = "/identity"
#: The endpoints that actually model the slow *initial library load*. They 401
#: without a token, so they are only probed when one is supplied.
AUTH_PATHS = ("/library/sections",)

USER_AGENT = "homelab-plex-latency/1 (+scripts/measure_plex_latency.py)"


def resolve_token(env=None):
    """The Plex token from the environment, or None.

    Whitespace-only is treated as absent so an exported-but-empty variable does
    not produce authenticated probes that all 401.
    """
    env = os.environ if env is None else env
    token = (env.get(TOKEN_ENV) or "").strip()
    return token or None


def build_targets(host=DEFAULT_HOST, direct=DEFAULT_DIRECT, authenticated=False, probe_direct=True):
    """The ordered probe list: the Traefik leg and the direct leg, paired.

    Order is fixed so two runs' records line up positionally as well as by name.
    Authenticated paths are added for BOTH legs, so the A/B holds for the
    library probe too, and only when a token is in play.

    `probe_direct=False` drops the direct leg entirely. That is the honest shape
    for an external run, where the backend address is RFC1918 and unreachable by
    construction — see `--skip-direct`. It costs the A/B, so the record stamps
    `direct_probed` and never leaves that implicit.
    """
    paths = [(UNAUTH_PATH, False)]
    if authenticated:
        paths += [(path, True) for path in AUTH_PATHS]

    legs = [(VIA_TRAEFIK, f"https://{host}")]
    if probe_direct:
        legs.insert(1, (VIA_DIRECT, f"http://{direct}"))

    return [
        {
            "name": f"{via}{path}",
            "via": via,
            "path": path,
            "url": f"{origin}{path}",
            "auth": auth,
        }
        for path, auth in paths
        for via, origin in legs
    ]


def time_request(url, timeout=DEFAULT_TIMEOUT, token=None):
    """One read-only GET, timed. Returns a sample dict; never raises.

    TTFB is the wall time from before the connection is opened to the moment the
    response *status line* is available (`getresponse()` returns once headers are
    parsed); total additionally includes draining the body. Both include DNS,
    TCP and — on the Traefik leg — the TLS handshake, which is the point: that
    handshake is part of what a remote client pays.

    Exactly one attempt. A failure is recorded as an error sample rather than
    retried, so an unhealthy server is never hammered by a measurement.

    A FAILED sample has `ttfb_ms` **and** `total_ms` set to None. The tempting
    alternative — null the TTFB but keep the elapsed time as the total — would
    file the *timeout duration* as a total load time: a number that changes when
    `--timeout` changes and that reads downstream as a genuinely slow endpoint.
    The elapsed time is still useful as a diagnostic, so it is kept under
    `failed_after_ms`, a field no summary ever touches.
    """
    parts = urllib.parse.urlsplit(url)
    connector = (
        http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
    )
    path = parts.path or "/"
    if parts.query:
        path = f"{path}?{parts.query}"
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if token:
        headers[TOKEN_HEADER] = token

    conn = connector(parts.hostname, parts.port, timeout=timeout)
    start = time.perf_counter()
    try:
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        ttfb = (time.perf_counter() - start) * 1000.0
        body = response.read()
        total = (time.perf_counter() - start) * 1000.0
        return {
            "status": response.status,
            "ttfb_ms": round(ttfb, 3),
            "total_ms": round(total, 3),
            "bytes": len(body),
            "failed_after_ms": None,
            "error": None,
        }
    except (OSError, http.client.HTTPException) as exc:
        return {
            "status": None,
            "ttfb_ms": None,
            "total_ms": None,
            "bytes": 0,
            # NOT a latency: how long the failure took to surface, which on a
            # timeout is just `--timeout`. Segregated from both series so it can
            # never be summarised into one.
            "failed_after_ms": round((time.perf_counter() - start) * 1000.0, 3),
            "error": f"{type(exc).__name__}: {exc}",
        }
    finally:
        conn.close()


def summarize(values):
    """min / median / max over the non-None samples of one series."""
    clean = sorted(v for v in values if v is not None)
    if not clean:
        return {"count": 0, "min_ms": None, "median_ms": None, "max_ms": None}
    return {
        "count": len(clean),
        "min_ms": round(clean[0], 3),
        "median_ms": round(statistics.median(clean), 3),
        "max_ms": round(clean[-1], 3),
    }


def measure_target(target, repeats=DEFAULT_REPEATS, timeout=DEFAULT_TIMEOUT, token=None, probe=None):
    """Probe one endpoint `repeats` times and summarise it.

    `probe` is injectable so the shape test can exercise this path with scripted
    timings and no network; it defaults to the real timer.
    """
    probe = time_request if probe is None else probe
    samples = [
        probe(target["url"], timeout=timeout, token=token if target["auth"] else None)
        for _ in range(repeats)
    ]
    statuses = sorted({s["status"] for s in samples if s["status"] is not None})
    errors = sorted({s["error"] for s in samples if s["error"]})
    succeeded = sum(1 for s in samples if s["error"] is None)
    return {
        "name": target["name"],
        "via": target["via"],
        "path": target["path"],
        "url": target["url"],
        "authenticated": target["auth"],
        "requested": repeats,
        # `succeeded` + `failed` == `requested`, and both series below summarise
        # exactly the `succeeded` samples. Recorded explicitly so Step 4 can tell
        # "fast" from "we only got two samples out of five" without re-deriving
        # it, and so a partially-populated target cannot pass for a whole one.
        "succeeded": succeeded,
        "failed": len(samples) - succeeded,
        "statuses": statuses,
        "errors": errors,
        "ttfb": summarize([s["ttfb_ms"] for s in samples]),
        "total": summarize([s["total_ms"] for s in samples]),
    }


def build_record(
    label,
    vantage,
    host,
    direct,
    repeats,
    timeout,
    authenticated,
    targets,
    now=None,
    direct_probed=True,
):
    """One self-describing JSONL record: everything needed to pair two runs.

    `now` is injectable so the record's clock is testable. It carries no token —
    see the module docstring.
    """
    stamp = now or datetime.datetime.now(datetime.timezone.utc)
    stamp = stamp.astimezone(datetime.timezone.utc)
    return {
        "schema": SCHEMA_VERSION,
        "timestamp": stamp.isoformat().replace("+00:00", "Z"),
        "label": label,
        "vantage": vantage,
        "host": host,
        "direct": direct,
        # Whether the A/B was actually run. A record with only the Traefik leg is
        # a legitimate external capture, but it is NOT the same measurement as a
        # two-leg run and Step 4 must be able to tell them apart.
        "direct_probed": direct_probed,
        "repeats": repeats,
        "timeout_s": timeout,
        "authenticated": authenticated,
        "targets": targets,
    }


def run_measurement(
    label,
    vantage,
    host=DEFAULT_HOST,
    direct=DEFAULT_DIRECT,
    repeats=DEFAULT_REPEATS,
    timeout=DEFAULT_TIMEOUT,
    token=None,
    probe=None,
    now=None,
    probe_direct=True,
):
    """Measure every target and return the finished record. Performs no writes."""
    targets = build_targets(host, direct, authenticated=bool(token), probe_direct=probe_direct)
    results = [
        measure_target(target, repeats=repeats, timeout=timeout, token=token, probe=probe)
        for target in targets
    ]
    return build_record(
        label=label,
        vantage=vantage,
        host=host,
        direct=direct,
        repeats=repeats,
        timeout=timeout,
        authenticated=bool(token),
        targets=results,
        now=now,
        direct_probed=probe_direct,
    )


def append_record(record, path=DEFAULT_LOG):
    """Append one record to the JSONL log, creating `logs/` if needed."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return path


def _cell(value):
    return "n/a" if value is None else f"{value:.1f}"


def render_report(record):
    """Human-readable summary of one record. Carries no token."""
    lines = [
        f"Plex latency — label={record['label']} vantage={record['vantage']} "
        f"at {record['timestamp']}",
        f"  host={record['host']}  direct={record['direct']}"
        f"{'' if record.get('direct_probed', True) else ' (SKIPPED)'}  "
        f"repeats={record['repeats']}  timeout={record['timeout_s']}s  "
        f"authenticated={record['authenticated']}",
        "",
        f"  {'endpoint':<28} {'n':>5} {'TTFB min/med/max (ms)':>26}  "
        f"{'total min/med/max (ms)':>26}  status",
    ]
    for target in record["targets"]:
        ttfb = target["ttfb"]
        total = target["total"]
        ttfb_cell = f"{_cell(ttfb['min_ms'])}/{_cell(ttfb['median_ms'])}/{_cell(ttfb['max_ms'])}"
        total_cell = f"{_cell(total['min_ms'])}/{_cell(total['median_ms'])}/{_cell(total['max_ms'])}"
        status = ",".join(str(s) for s in target["statuses"]) or "-"
        # How many samples the statistics rest on. Without it, a median over one
        # surviving sample of five is typographically identical to a clean run.
        n_cell = f"{target.get('succeeded', ttfb['count'])}/{target['requested']}"
        lines.append(
            f"  {target['name']:<28} {n_cell:>5} {ttfb_cell:>26}  {total_cell:>26}  {status}"
        )
        for error in target["errors"]:
            lines.append(f"      ! {error}")

    # The headline number: what Traefik costs on the same unauthenticated probe.
    # It needs BOTH legs to have answered; when it cannot be computed, say so
    # rather than omitting the line, so a reader is never left to assume the
    # A/B was measured and simply came out flat.
    by_via = {t["via"]: t for t in record["targets"] if t["path"] == UNAUTH_PATH}
    traefik, direct = by_via.get(VIA_TRAEFIK), by_via.get(VIA_DIRECT)
    a = traefik["ttfb"]["median_ms"] if traefik else None
    b = direct["ttfb"]["median_ms"] if direct else None
    if a is not None and b is not None:
        lines += ["", f"  Traefik overhead on {UNAUTH_PATH} (median TTFB): {a - b:+.1f} ms"]
    else:
        why = "the direct leg was skipped" if not record.get("direct_probed", True) else (
            "one leg returned no successful samples"
        )
        lines += ["", f"  Traefik overhead on {UNAUTH_PATH} (median TTFB): n/a — {why}"]
    return "\n".join(lines)


def _parser():
    parser = argparse.ArgumentParser(
        description="Measure Plex TTFB/total latency through Traefik and direct to the backend.",
        epilog=f"The Plex token is read from ${TOKEN_ENV}; there is no flag for it.",
    )
    parser.add_argument(
        "--label",
        required=True,
        help="run label, e.g. 'baseline' or 'post-change' (required: an unlabelled run cannot be paired)",
    )
    parser.add_argument(
        "--vantage",
        required=True,
        choices=VANTAGES,
        help="network vantage point; the plan's baseline is only valid as 'external'",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Traefik hostname (default: {DEFAULT_HOST})")
    parser.add_argument(
        "--direct", default=DEFAULT_DIRECT, help=f"backend host:port (default: {DEFAULT_DIRECT})"
    )
    parser.add_argument(
        "--skip-direct",
        action="store_true",
        help=(
            "do not probe the backend directly. Use this from an EXTERNAL vantage, where the "
            "backend address is RFC1918 and unreachable by construction; without it the run "
            "hangs for repeats x timeout and exits 1 on a perfectly good capture. It gives up "
            "the Traefik-vs-direct A/B, so the record is stamped direct_probed=false."
        ),
    )
    parser.add_argument(
        "--repeats", type=int, default=DEFAULT_REPEATS, help=f"samples per endpoint (default: {DEFAULT_REPEATS})"
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"per-request timeout in seconds (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument("--out", default=str(DEFAULT_LOG), help=f"JSONL log path (default: {DEFAULT_LOG})")
    parser.add_argument("--no-log", action="store_true", help="print the report but do not append to the JSONL log")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    if args.repeats < 1:
        print("FAIL: --repeats must be >= 1", file=sys.stderr)
        return 2

    token = resolve_token()
    if token is None:
        print(
            f"note: ${TOKEN_ENV} is not set — probing the unauthenticated {UNAUTH_PATH} only.",
            file=sys.stderr,
        )
    if args.vantage == "lan":
        print(
            "note: vantage=lan. The plan's baseline must be captured from an EXTERNAL network;"
            " a LAN run is a smoke test, not the baseline.",
            file=sys.stderr,
        )
    if args.skip_direct:
        print(
            "note: --skip-direct. Traefik leg only; there is no Traefik-vs-direct comparison in"
            " this run, and the record says so (direct_probed=false).",
            file=sys.stderr,
        )

    record = run_measurement(
        label=args.label,
        vantage=args.vantage,
        host=args.host,
        direct=args.direct,
        repeats=args.repeats,
        timeout=args.timeout,
        token=token,
        probe_direct=not args.skip_direct,
    )
    print(render_report(record))

    if not args.no_log:
        path = append_record(record, args.out)
        print(f"\nappended 1 record to {path}")

    unreachable = [t["name"] for t in record["targets"] if t["ttfb"]["count"] == 0]
    if unreachable:
        # stdout is block-buffered when piped into a log, stderr is not, so
        # without this the warning surfaces ABOVE the report it refers to.
        sys.stdout.flush()
        print(f"\nWARNING: no successful samples for: {unreachable}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
