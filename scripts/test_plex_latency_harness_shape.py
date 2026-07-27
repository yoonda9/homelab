"""Shape test for Step 1a — the Plex latency measurement harness.

Per `.agents/planning/2026-07-27-plex-optimization/implementation/plan.md`
Step 1 — pins `scripts/measure_plex_latency.py`, the re-runnable harness whose
whole reason to exist is that Step 4 must diff its numbers against Step 1's
baseline. A number typed into a doc once is not comparable; the same script run
twice is. So the properties guarded here are the ones that would silently make
two runs *incomparable* or unsafe, not the script's prose:

  1. the Plex token comes from the ENVIRONMENT and from nowhere else (the repo
     has a no-plaintext-secrets house rule; a token literal or a `--token`
     default would put a household credential in git),
  2. BOTH legs of the controlled A/B are probed — through Traefik on :443 AND
     direct to the backend on :32400 — because "Traefik is the suspect" is only
     testable as a difference between the two,
  3. the authenticated library endpoints appear ONLY when a token is supplied,
  4. every run record carries `label` + `vantage` + a UTC timestamp, since an
     unlabelled run, or a LAN run mistaken for an off-LAN one, poisons the
     baseline the plan defines as external-network,
  5. the summary statistics are actually computed from the samples,
  6. a FAILED sample contributes a measurement to NEITHER series — an endpoint
     that never returned a byte must not report a `total` median (which would be
     the timeout duration wearing a latency's clothes), and `ttfb` and `total`
     must always summarise the SAME set of samples,
  7. `--label` and `--vantage` are mandatory, so a convenient LAN run cannot
     self-file as the plan's external-network baseline,
  8. the harness is import-safe and offline-safe — `scripts/run_gate.py` runs
     this file with NO network, so the test must never perform a real request,
  9. neither the JSONL record nor the stdout report echoes the token.

Behaviour is exercised, not grepped: the record-building and statistics paths
run end to end against an INJECTED fake prober with scripted timings, under a
socket guard that raises on any real connect. Sentinel inputs are values that
appear nowhere else in the repo (mem-1784140865-9b40) so a check cannot pass by
coincidence with a default, and each check is registered in `TESTS` — a
`test_*` function missing from that tuple is green-by-omission
(mem-1784137124-c346).

Two levels of fake, deliberately: `FakeProbe` replaces the harness's timer and
can only ever report success, so on its own it leaves `time_request`'s
except-branch completely unexercised (mem-1785119466-0e93). `FakeTransport` sits
one level lower — it replaces `http.client.HTTP(S)Connection`, so the harness's
REAL `time_request` runs against it — and it has a failure mode, which is what
makes properties 6 testable at all.

Follows the repo's dual-mode shape-test convention (see
`test_plex_ramdisk_bind_mount_shape.py`): module-level `test_<name>() -> bool`
printing `OK` / `FAIL: ...` (no `assert`), plus `main() -> int` summing them.
Stdlib only.
"""

import contextlib
import datetime
import http.client
import importlib.util
import io
import json
import os
import pathlib
import socket
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
HARNESS = REPO_ROOT / "scripts" / "measure_plex_latency.py"

# Sentinels chosen to appear NOWHERE else in the repo, so no check can pass by
# coinciding with a default, a real address, or another test's fixture.
PROBE_HOST = "plex.probe-vantage-7431.invalid"
PROBE_DIRECT = "10.253.7.43:59137"
PROBE_TOKEN = "probe-token-a7f31c9e-never-a-real-plex-token"
PROBE_LABEL = "probe-label-51ac"
PROBE_VANTAGE = "probe-vantage-9d2f"
PROBE_NOW = datetime.datetime(2001, 2, 3, 4, 5, 6, tzinfo=datetime.timezone.utc)

# Scripted timings: five distinct values whose min/median/max are all different,
# so a statistic computed off the wrong end (or off the raw list order) shows.
FAKE_TTFB = [37.0, 11.0, 91.0, 53.0, 23.0]  # -> min 11.0, median 37.0, max 91.0
FAKE_TOTAL = [74.0, 22.0, 182.0, 106.0, 46.0]  # -> min 22.0, median 74.0, max 182.0
FAKE_TTFB_STATS = (11.0, 37.0, 91.0)
FAKE_TOTAL_STATS = (22.0, 74.0, 182.0)


class NetworkAttempted(RuntimeError):
    """Raised by the socket guard when code under test tries to reach the wire."""


NETWORK_ATTEMPTS: list = []


@contextlib.contextmanager
def _no_network():
    """Block every path to the wire — connect, create_connection, and DNS.

    The gate runs offline, so a harness that reached the network here would fail
    the whole gate on a machine with no route. Guarding DNS too matters: name
    resolution is a network call even when the connect never happens.
    """
    saved = (
        socket.socket.connect,
        socket.socket.connect_ex,
        socket.create_connection,
        socket.getaddrinfo,
    )

    def _blocker(name):
        def _raise(*args, **kwargs):
            NETWORK_ATTEMPTS.append(name)
            raise NetworkAttempted(name)

        return _raise

    socket.socket.connect = _blocker("socket.connect")
    socket.socket.connect_ex = _blocker("socket.connect_ex")
    socket.create_connection = _blocker("socket.create_connection")
    socket.getaddrinfo = _blocker("socket.getaddrinfo")
    try:
        yield
    finally:
        (
            socket.socket.connect,
            socket.socket.connect_ex,
            socket.create_connection,
            socket.getaddrinfo,
        ) = saved


def _load_harness():
    """Import `measure_plex_latency` by path, under the network guard."""
    spec = importlib.util.spec_from_file_location("measure_plex_latency", HARNESS)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {HARNESS}")
    module = importlib.util.module_from_spec(spec)
    with _no_network():
        spec.loader.exec_module(module)
    return module


IMPORT_ERROR = None
MOD = None
try:
    MOD = _load_harness()
except Exception as exc:  # noqa: BLE001 - reported as a FAIL, never raised
    IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
IMPORT_NETWORK_ATTEMPTS = list(NETWORK_ATTEMPTS)


class FakeProbe:
    """Stand-in for the harness's real timer: scripted results, no I/O.

    Records every call so a check can assert *which* URLs were probed, how many
    times, and which of them were handed the token.

    Every result it returns is a SUCCESS, which is the right fixture for the
    statistics and record-shape checks and the wrong one for anything about
    failure — it bypasses `time_request` entirely. The error path is covered by
    `FakeTransport` instead; do not add a failure mode here, or the two fakes
    will disagree about what a failed sample looks like.
    """

    def __init__(self, ttfbs=FAKE_TTFB, totals=FAKE_TOTAL):
        self.ttfbs = ttfbs
        self.totals = totals
        self.calls: list = []

    def __call__(self, url, timeout=None, token=None):
        index = sum(1 for call in self.calls if call[0] == url)
        self.calls.append((url, timeout, token))
        return {
            "status": 200,
            "ttfb_ms": self.ttfbs[index % len(self.ttfbs)],
            "total_ms": self.totals[index % len(self.totals)],
            "bytes": 11,
            "error": None,
        }


class _FakeResponse:
    """The bare surface `time_request` uses: a status line and a readable body."""

    status = 200

    def read(self):
        return b"probe-body"


class FakeTransport:
    """Stand-in for `http.client.HTTP(S)Connection` — the harness's real I/O boundary.

    `FakeProbe` above replaces the *timer*, so every check that uses it drives
    only the success path and `time_request`'s except-branch stays unexercised —
    the outcome-provenance blind spot of mem-1785119466-0e93. This fake sits one
    level lower: it is installed over `http.client`, so the harness's OWN
    `time_request` runs for real against it, and it HAS a failure mode. Hosts
    listed in `failing_hosts` raise the `TimeoutError` the socket layer would
    raise on an unreachable endpoint — the exact live case, since the plan's
    external vantage cannot reach the RFC1918 direct leg.

    No socket is created either way, so this stays valid under `_no_network()`.


    `flaky_hosts` maps a host to the 0-based attempt indices that fail, which is
    the PARTIAL outage — the only shape in which "how many samples were
    requested" and "how many were measured" disagree. Without such a row, a
    count taken off the wrong list is invisible: with every attempt succeeding
    or every attempt failing, the two numbers coincide (mem-1784139112-e13c).
    """

    def __init__(self, failing_hosts=(), flaky_hosts=None):
        self.failing_hosts = set(failing_hosts)
        self.flaky_hosts = {host: set(idx) for host, idx in (flaky_hosts or {}).items()}
        self.attempts: dict = {}
        self.opened: list = []

    @contextlib.contextmanager
    def installed(self):
        saved = (http.client.HTTPConnection, http.client.HTTPSConnection)
        transport = self

        class _Conn:
            def __init__(self, host, port=None, timeout=None, **kwargs):
                attempt = transport.attempts.get(host, 0)
                transport.attempts[host] = attempt + 1
                transport.opened.append((host, port, timeout))
                self.fails = (
                    host in transport.failing_hosts
                    or attempt in transport.flaky_hosts.get(host, ())
                )

            def request(self, method, path, headers=None, **kwargs):
                if self.fails:
                    raise TimeoutError("the read operation timed out")

            def getresponse(self):
                return _FakeResponse()

            def close(self):
                return None

        http.client.HTTPConnection = _Conn
        http.client.HTTPSConnection = _Conn
        try:
            yield self
        finally:
            (http.client.HTTPConnection, http.client.HTTPSConnection) = saved


def _transport_run(failing_hosts=(), flaky_hosts=None, repeats=len(FAKE_TTFB), **kwargs):
    """Drive the harness's REAL prober (`probe=None`) over `FakeTransport`.

    Returns `(record, transport, error)`. Deliberately does not inject a probe:
    the point is to execute `time_request` itself, including its except-branch.
    """
    transport = FakeTransport(failing_hosts, flaky_hosts)
    try:
        with _no_network(), transport.installed():
            record = MOD.run_measurement(
                label=PROBE_LABEL,
                vantage=PROBE_VANTAGE,
                host=PROBE_HOST,
                direct=PROBE_DIRECT,
                repeats=repeats,
                now=PROBE_NOW,
                **kwargs,
            )
    except NetworkAttempted as exc:
        return None, transport, f"NetworkAttempted: {exc}"
    return record, transport, None


def _parse_argv(argv):
    """Run the harness's REAL parser on `argv`; never let it exit this process.

    Returns `(namespace_or_None, exit_code_or_None)`. argparse writes usage to
    stderr on failure, which would spam the gate log, so both streams are
    captured.
    """
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stderr(buffer), contextlib.redirect_stdout(buffer):
            return MOD._parser().parse_args(argv), None
    except SystemExit as exc:
        return None, exc.code


def _fake_run(token=None, repeats=len(FAKE_TTFB), probe=None):
    """Drive the harness's real pipeline with the fake prober, offline.

    Returns `(record, probe, error)`. A harness that ignores the injected prober
    and reaches for the wire trips the socket guard; that is reported as an
    `error` string so the caller prints a FAIL, rather than escaping as a
    traceback that aborts the remaining checks.
    """
    probe = probe if probe is not None else FakeProbe()
    try:
        with _no_network():
            record = MOD.run_measurement(
                label=PROBE_LABEL,
                vantage=PROBE_VANTAGE,
                host=PROBE_HOST,
                direct=PROBE_DIRECT,
                repeats=repeats,
                token=token,
                probe=probe,
                now=PROBE_NOW,
            )
    except NetworkAttempted as exc:
        return None, probe, f"NetworkAttempted: {exc}"
    return record, probe, None


def _guard(name: str) -> bool:
    """Report an unusable harness once, as a FAIL, instead of raising."""
    if MOD is None:
        print(f"FAIL: {name}: harness did not import ({IMPORT_ERROR})")
        return False
    return True


def test_harness_imports_and_exposes_its_api() -> bool:
    """Premise guard: the module loads and every symbol the checks use exists.

    Without this, a renamed function would surface below as a confusing
    AttributeError instead of 'the harness stopped exposing its API'.
    """
    if not _guard("harness api"):
        return False
    required = (
        "resolve_token",
        "build_targets",
        "summarize",
        "measure_target",
        "build_record",
        "run_measurement",
        "render_report",
        "time_request",
        "TOKEN_ENV",
        "DEFAULT_DIRECT",
    )
    missing = [name for name in required if not hasattr(MOD, name)]
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: harness imports and exposes its API (missing={missing})")
    return ok


def test_token_read_from_environment_only() -> bool:
    """AC: the token comes from an env var — no literal, no CLI default.

    Behavioural, not a grep: an empty environment MUST yield no token. A
    hardcoded fallback, a repo-file read, or an argparse `--token` default would
    all make this return a value where None is required.
    """
    if not _guard("token from env"):
        return False
    absent = MOD.resolve_token({})
    blank = MOD.resolve_token({MOD.TOKEN_ENV: "   "})
    present = MOD.resolve_token({MOD.TOKEN_ENV: PROBE_TOKEN})
    # No CLI surface for the token at all: a flag invites shell-history leakage
    # and a default would defeat the env-only rule. Asked of the real parser's
    # option strings rather than grepped out of the source — a whole-file grep
    # would bind to the docstring that *describes* this rule.
    token_flags = sorted(
        opt
        for action in MOD._parser()._actions
        for opt in action.option_strings
        if "token" in opt.lower()
    )
    ok = absent is None and blank is None and present == PROBE_TOKEN and not token_flags
    print(
        f"{'OK' if ok else 'FAIL'}: token resolves from ${MOD.TOKEN_ENV} only "
        f"(absent={absent!r}, blank={blank!r}, present_matches={present == PROBE_TOKEN}, "
        f"token_flags={token_flags})"
    )
    return ok


def test_probes_traefik_and_direct_backend() -> bool:
    """AC: both legs of the A/B are probed — via Traefik AND direct to :32400.

    'Traefik is the suspect' is only testable as a difference between the two,
    so dropping either leg makes every recorded run uninterpretable. Asserted
    against sentinel targets (the URLs must be built from the arguments, not
    from a hardcoded household address) plus the shipped default, which must
    still name the backend port 32400.
    """
    if not _guard("traefik + direct probes"):
        return False
    targets = MOD.build_targets(PROBE_HOST, PROBE_DIRECT)
    by_via = {}
    for target in targets:
        by_via.setdefault(target["via"], []).append(target)
    traefik_urls = [t["url"] for t in by_via.get("traefik", [])]
    direct_urls = [t["url"] for t in by_via.get("direct", [])]
    traefik_ok = traefik_urls == [f"https://{PROBE_HOST}/identity"]
    direct_ok = direct_urls == [f"http://{PROBE_DIRECT}/identity"]
    # The default backend is the Traefik service's own upstream: port 32400.
    default_port_ok = MOD.DEFAULT_DIRECT.endswith(":32400")
    ok = traefik_ok and direct_ok and default_port_ok
    print(
        f"{'OK' if ok else 'FAIL'}: probes Traefik and the direct backend "
        f"(traefik={traefik_urls}, direct={direct_urls}, default_direct={MOD.DEFAULT_DIRECT!r})"
    )
    return ok


def test_authenticated_targets_require_a_token() -> bool:
    """AC: library endpoints are added ONLY when a token is supplied.

    Unauthenticated `/library/sections` returns 401 and would silently record a
    fast, meaningless error path as if it were a library-load measurement.
    """
    if not _guard("auth targets gated"):
        return False
    anon = MOD.build_targets(PROBE_HOST, PROBE_DIRECT, authenticated=False)
    authed = MOD.build_targets(PROBE_HOST, PROBE_DIRECT, authenticated=True)
    anon_auth = [t["url"] for t in anon if t["auth"]]
    authed_auth = sorted(t["url"] for t in authed if t["auth"])
    # Added for BOTH legs, so the A/B holds for the authenticated probe too.
    vias = {t["via"] for t in authed if t["auth"]}
    ok = not anon_auth and len(authed_auth) > len(anon_auth) and vias == {"traefik", "direct"}
    print(
        f"{'OK' if ok else 'FAIL'}: authenticated targets appear only with a token "
        f"(anon={anon_auth}, authed={authed_auth}, authed_vias={sorted(vias)})"
    )
    return ok


def test_record_carries_label_vantage_and_utc_timestamp() -> bool:
    """AC: every record is self-describing — label + vantage + UTC timestamp.

    Step 4 diffs baseline against post-change out of this JSONL; a record that
    loses its label, or its LAN/external vantage, cannot be paired with the run
    it is supposed to be compared to. The timestamp is injected, so a value
    invented instead of derived (or a naive local-time stamp) reddens.
    """
    if not _guard("record label/vantage/timestamp"):
        return False
    record, _, error = _fake_run()
    if record is None:
        print(f"FAIL: run record carries label + vantage + UTC timestamp ({error})")
        return False
    stamp = record.get("timestamp")
    try:
        parsed = datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    except ValueError:
        parsed = None
    utc_ok = parsed is not None and parsed.utcoffset() == datetime.timedelta(0)
    same_instant = parsed is not None and parsed == PROBE_NOW
    ok = (
        record.get("label") == PROBE_LABEL
        and record.get("vantage") == PROBE_VANTAGE
        and utc_ok
        and same_instant
    )
    print(
        f"{'OK' if ok else 'FAIL'}: run record carries label + vantage + UTC timestamp "
        f"(label={record.get('label')!r}, vantage={record.get('vantage')!r}, "
        f"timestamp={stamp!r}, utc={utc_ok}, matches_injected_clock={same_instant})"
    )
    return ok


def test_summary_statistics_are_computed_from_samples() -> bool:
    """AC: min/median/max come from the samples, per endpoint, for TTFB and total.

    Driven by scripted timings whose three statistics are all different, so
    reporting the mean, the first sample, or the total in place of the TTFB is
    distinguishable. Also pins that every endpoint really got `repeats` probes —
    a run that silently sampled once is not comparable to one that sampled five
    times.
    """
    if not _guard("summary statistics"):
        return False
    record, probe, error = _fake_run()
    if record is None:
        print(f"FAIL: min/median/max computed from the samples ({error})")
        return False
    targets = record.get("targets", [])
    got_ttfb = {
        (t["ttfb"]["min_ms"], t["ttfb"]["median_ms"], t["ttfb"]["max_ms"]) for t in targets
    }
    got_total = {
        (t["total"]["min_ms"], t["total"]["median_ms"], t["total"]["max_ms"]) for t in targets
    }
    counts = {t["ttfb"]["count"] for t in targets}
    ok = (
        bool(targets)
        and got_ttfb == {FAKE_TTFB_STATS}
        and got_total == {FAKE_TOTAL_STATS}
        and counts == {len(FAKE_TTFB)}
        and len(probe.calls) == len(targets) * len(FAKE_TTFB)
    )
    print(
        f"{'OK' if ok else 'FAIL'}: min/median/max computed from the samples "
        f"(ttfb={sorted(got_ttfb)}, total={sorted(got_total)}, counts={sorted(counts)}, "
        f"probe_calls={len(probe.calls)}, targets={len(targets)})"
    )
    return ok


def test_failed_sample_is_a_measurement_of_nothing() -> bool:
    """AC: a request that never returned a byte yields NO latency in either field.

    Exercises the real `time_request` over a transport that raises the socket
    layer's own `TimeoutError`. The tempting shape — null the TTFB but keep the
    elapsed time as `total_ms` — records the *timeout duration* as a total load
    time: a number that moves when `--timeout` moves and reads downstream as a
    genuinely slow endpoint. So both fields must be None, and the elapsed time,
    if kept at all, must live in a field no summary ever touches.
    """
    if not _guard("failed sample records no latency"):
        return False
    transport = FakeTransport(failing_hosts={PROBE_HOST})
    with _no_network(), transport.installed():
        sample = MOD.time_request(f"https://{PROBE_HOST}/identity", timeout=0.25)
    reached_transport = bool(transport.opened)
    took_error_path = bool(sample.get("error")) and "TimeoutError" in str(sample.get("error"))
    ok = (
        reached_transport
        and took_error_path
        and sample.get("status") is None
        and sample.get("ttfb_ms") is None
        and sample.get("total_ms") is None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: a failed sample carries no latency in either field "
        f"(ttfb_ms={sample.get('ttfb_ms')!r}, total_ms={sample.get('total_ms')!r}, "
        f"status={sample.get('status')!r}, error={sample.get('error')!r}, "
        f"transport_used={reached_transport})"
    )
    return ok


def test_ttfb_and_total_summarise_the_same_samples() -> bool:
    """AC: per target, `ttfb` and `total` always cover an identical sample set.

    Models the live external-vantage case exactly: the Traefik leg answers and
    the direct RFC1918 leg is unreachable. The dead leg must summarise to
    `count 0` on BOTH series with every statistic None — not `ttfb count 0`
    beside `total count N`, and not a suspiciously fast pair either — and the
    report must decline to print a Traefik-overhead figure it cannot compute.
    The counts must also agree on the HEALTHY leg, so the check cannot be
    satisfied by a harness that simply reports zero everywhere.
    """
    if not _guard("both series over the same samples"):
        return False
    direct_host = PROBE_DIRECT.split(":")[0]
    record, transport, error = _transport_run(failing_hosts={direct_host})
    if record is None:
        print(f"FAIL: ttfb and total summarise the same samples ({error})")
        return False
    targets = {t["via"]: t for t in record["targets"]}
    live, dead = targets.get("traefik"), targets.get("direct")
    if not live or not dead:
        print(f"FAIL: ttfb and total summarise the same samples (missing leg: {sorted(targets)})")
        return False
    # Read through `.get` throughout: a harness that stops emitting one of these
    # fields must make this check print FAIL, not raise a KeyError that aborts
    # every check after it.
    def _series(target, series, stat):
        return (target.get(series) or {}).get(stat)

    # The invariant, asserted for EVERY target rather than only the dead one.
    agree = all(
        _series(t, "ttfb", "count") == _series(t, "total", "count") == t.get("succeeded")
        and (t.get("succeeded"), t.get("failed")) != (None, None)
        and (t.get("succeeded") or 0) + (t.get("failed") or 0) == t.get("requested")
        for t in record["targets"]
    )
    dead_is_empty = (
        _series(dead, "ttfb", "count") == 0
        and _series(dead, "total", "count") == 0
        and all(
            _series(dead, series, stat) is None
            for series in ("ttfb", "total")
            for stat in ("min_ms", "median_ms", "max_ms")
        )
        and bool(dead.get("errors"))
    )
    live_is_measured = (
        live.get("succeeded") == len(FAKE_TTFB)
        and not live.get("errors")
        and _series(live, "total", "median_ms") is not None
    )
    report = MOD.render_report(record)
    overhead_claimed = "overhead" in report and "n/a" not in report.split("overhead")[-1]
    ok = (
        bool(transport.opened)
        and agree
        and dead_is_empty
        and live_is_measured
        and not overhead_claimed
    )
    print(
        f"{'OK' if ok else 'FAIL'}: ttfb and total summarise the same samples "
        f"(counts_agree={agree}, dead_leg ttfb={_series(dead, 'ttfb', 'count')}"
        f"/total={_series(dead, 'total', 'count')} "
        f"median_total={_series(dead, 'total', 'median_ms')!r}, "
        f"live_leg={live.get('succeeded')}/{live.get('requested')}, "
        f"overhead_claimed_without_both_legs={overhead_claimed})"
    )
    return ok


def test_partial_failure_does_not_inflate_the_sample_count() -> bool:
    """AC: the reported count is what was MEASURED, not what was requested.

    The discriminator row for every count in the record. When a leg is wholly up
    or wholly down, "samples requested" and "samples summarised" are the same
    number and any confusion between them is invisible; only a PARTIAL outage
    separates them. Two of five attempts fail here, so a count sourced from the
    requested list instead of the surviving samples reports 5 where 3 is true —
    a median over three samples advertised as a five-sample measurement.
    """
    if not _guard("partial failure sample count"):
        return False
    failed_attempts = {1, 3}
    expected_ok = len(FAKE_TTFB) - len(failed_attempts)
    record, transport, error = _transport_run(flaky_hosts={PROBE_HOST: failed_attempts})
    if record is None:
        print(f"FAIL: a partial failure does not inflate the sample count ({error})")
        return False
    flaky = next((t for t in record["targets"] if t["via"] == "traefik"), None)
    if flaky is None:
        print("FAIL: a partial failure does not inflate the sample count (no traefik target)")
        return False
    counts = ((flaky.get("ttfb") or {}).get("count"), (flaky.get("total") or {}).get("count"))
    ok = (
        bool(transport.opened)
        and flaky.get("requested") == len(FAKE_TTFB)
        and flaky.get("succeeded") == expected_ok
        and flaky.get("failed") == len(failed_attempts)
        and counts == (expected_ok, expected_ok)
        and bool(flaky.get("errors"))
        and (flaky.get("ttfb") or {}).get("median_ms") is not None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: a partial failure does not inflate the sample count "
        f"(requested={flaky.get('requested')}, succeeded={flaky.get('succeeded')}, "
        f"failed={flaky.get('failed')}, series_counts={counts}, expected={expected_ok})"
    )
    return ok


def test_label_and_vantage_are_mandatory() -> bool:
    """AC: the run cannot be started without a label and a vantage.

    This is the step's own stated structural defence — the plan's baseline is
    definitionally off-LAN, and the failure mode it exists to prevent is a
    convenient LAN run being filed as the baseline because it was easy to take.
    A `default=` on either flag reinstates exactly that, so the parser is driven
    for real: every incomplete argv must exit non-zero, and an unknown vantage
    must be refused rather than recorded verbatim.
    """
    if not _guard("label and vantage mandatory"):
        return False
    complete, complete_rc = _parse_argv(["--label", PROBE_LABEL, "--vantage", "external"])
    refused = {
        "no args": _parse_argv([])[1],
        "label only": _parse_argv(["--label", PROBE_LABEL])[1],
        "vantage only": _parse_argv(["--vantage", "external"])[1],
        "unknown vantage": _parse_argv(["--label", PROBE_LABEL, "--vantage", PROBE_VANTAGE])[1],
    }
    all_refused = all(rc not in (None, 0) for rc in refused.values())
    complete_ok = (
        complete_rc is None
        and complete is not None
        and complete.label == PROBE_LABEL
        and complete.vantage == "external"
    )
    ok = all_refused and complete_ok
    print(
        f"{'OK' if ok else 'FAIL'}: --label and --vantage are mandatory and validated "
        f"(refused={refused}, complete_parses={complete_ok})"
    )
    return ok


def test_direct_leg_is_skippable_and_the_record_says_so() -> bool:
    """AC: the A/B can be dropped on purpose, and the record admits it.

    From an external vantage the direct leg is RFC1918 and unreachable by
    construction, so a CORRECT baseline capture otherwise spends
    repeats x timeout hanging and then exits non-zero. `--skip-direct` is the
    affordance for that; the danger is a run that quietly lost half the A/B, so
    `direct_probed` must record which shape the run had. Default stays BOTH legs.
    """
    if not _guard("direct leg skippable"):
        return False
    # A harness with no such affordance raises TypeError on the keyword; that is
    # a FAIL to report, not a traceback that aborts the checks after this one.
    try:
        skipped = MOD.build_targets(PROBE_HOST, PROBE_DIRECT, probe_direct=False)
        default = MOD.build_targets(PROBE_HOST, PROBE_DIRECT)
        record, _, error = _transport_run(probe_direct=False)
        both, _, both_error = _transport_run()
    except TypeError as exc:
        print(f"FAIL: the direct leg is skippable and recorded (TypeError: {exc})")
        return False
    skipped_vias = sorted({t["via"] for t in skipped})
    default_vias = sorted({t["via"] for t in default})
    flags = [
        opt
        for action in MOD._parser()._actions
        for opt in action.option_strings
        if "skip-direct" in opt
    ]
    ok = (
        error is None
        and both_error is None
        and record is not None
        and both is not None
        and skipped_vias == ["traefik"]
        and default_vias == ["direct", "traefik"]
        and record.get("direct_probed") is False
        and both.get("direct_probed") is True
        and bool(flags)
    )
    print(
        f"{'OK' if ok else 'FAIL'}: the direct leg is skippable and recorded "
        f"(skipped_vias={skipped_vias}, default_vias={default_vias}, "
        f"direct_probed={None if record is None else record.get('direct_probed')!r}/"
        f"{None if both is None else both.get('direct_probed')!r}, flags={flags})"
    )
    return ok


def test_harness_is_offline_safe() -> bool:
    """AC: importing and driving the harness performs NO real request.

    `scripts/run_gate.py` runs this file with no network. Import already ran
    under the socket guard above; here the full measurement pipeline runs under
    it too, with the prober injected. Any real connect — or any DNS lookup —
    raises `NetworkAttempted` and this check goes red rather than the gate
    failing mysteriously on an offline machine.
    """
    if not _guard("offline safe"):
        return False
    before = len(NETWORK_ATTEMPTS)
    record, probe, error = _fake_run()
    during = NETWORK_ATTEMPTS[before:]
    injected_only = bool(probe.calls)
    ok = (
        not IMPORT_NETWORK_ATTEMPTS
        and error is None
        and not during
        and injected_only
        and bool(record)
    )
    print(
        f"{'OK' if ok else 'FAIL'}: harness is import- and offline-safe "
        f"(import_attempts={IMPORT_NETWORK_ATTEMPTS}, run_attempts={during}, "
        f"error={error}, injected_probe_used={injected_only})"
    )
    return ok


def test_token_never_reaches_the_record_or_report() -> bool:
    """AC: the credential is used, never persisted or printed.

    The JSONL under `logs/` is committed and the report is pasted into runbooks,
    so a token echoed into either is a leak with a long half-life. Proven with a
    token that IS in play: the authenticated targets must have received it (else
    the check would pass vacuously on a harness that simply ignores the token)
    while neither serialised artifact contains it.
    """
    if not _guard("token not persisted"):
        return False
    # The token is BOTH passed in and exported, because those are two distinct
    # leak sources: a record field threaded from the argument, and a reporting
    # path that re-reads $PLEX_TOKEN out of the environment for itself. Setting
    # only the argument would leave the second invisible to this check.
    previous = os.environ.get(MOD.TOKEN_ENV)
    os.environ[MOD.TOKEN_ENV] = PROBE_TOKEN
    try:
        record, probe, error = _fake_run(token=PROBE_TOKEN)
        report = "" if record is None else MOD.render_report(record)
    finally:
        if previous is None:
            os.environ.pop(MOD.TOKEN_ENV, None)
        else:
            os.environ[MOD.TOKEN_ENV] = previous
    if record is None:
        print(f"FAIL: token is used but never recorded or printed ({error})")
        return False
    serialised = json.dumps(record)
    token_was_used = any(call[2] == PROBE_TOKEN for call in probe.calls)
    ok = token_was_used and PROBE_TOKEN not in serialised and PROBE_TOKEN not in report
    print(
        f"{'OK' if ok else 'FAIL'}: token is used but never recorded or printed "
        f"(sent_to_probe={token_was_used}, in_record={PROBE_TOKEN in serialised}, "
        f"in_report={PROBE_TOKEN in report})"
    )
    return ok


TESTS = (
    test_harness_imports_and_exposes_its_api,
    test_token_read_from_environment_only,
    test_probes_traefik_and_direct_backend,
    test_authenticated_targets_require_a_token,
    test_record_carries_label_vantage_and_utc_timestamp,
    test_summary_statistics_are_computed_from_samples,
    test_failed_sample_is_a_measurement_of_nothing,
    test_ttfb_and_total_summarise_the_same_samples,
    test_partial_failure_does_not_inflate_the_sample_count,
    test_label_and_vantage_are_mandatory,
    test_direct_leg_is_skippable_and_the_record_says_so,
    test_harness_is_offline_safe,
    test_token_never_reaches_the_record_or_report,
)


def main() -> int:
    results = [fn() for fn in TESTS]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
