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
  6b. and a request that WAS answered, but not with a 2xx, is a failure too. A
     401 from `/library/sections` is Plex refusing before it touches the library
     and a Traefik 404/502 error page is Traefik answering for a backend it
     never reached: both are fast, both are flawless round trips at the
     transport layer, and both file as an excellent baseline if they are
     counted. The protocol has THREE outcomes (2xx, non-2xx, no answer) where
     the socket has two (mem-1785123219-03c9). The success band is pinned just
     outside AND just inside both of its edges, because a range predicate
     sampled at one interior point is guarded on one side only
     (mem-1785124653-a61d),
  6c. and every request the harness puts on the wire is a read-only `GET` with
     no body — the one irreversible thing this script could do to a live
     household server, and the property the fixture used to make unassertable by
     accepting `method` and discarding it (mem-1785124642-053b),
  7. `--label` and `--vantage` are mandatory, so a convenient LAN run cannot
     self-file as the plan's external-network baseline,
  8. the harness is import-safe and offline-safe — `scripts/run_gate.py` runs
     this file with NO network, so the test must never perform a real request,
  9. neither the JSONL record nor the stdout report echoes the token,
 10. the ENTRY POINT is wired: the argv the runbook publishes really reaches the
     measurement, the record really lands on disk, and the exit code really
     follows the documented 0/1/2/3 contract — including the case where the
     measurement succeeds and the WRITE is what fails,
 11. the human-readable report STATES WHAT THE RECORD STATES. It is half of this
     task's named output ("human-readable stdout AND an append-only structured
     record") and it is the half the operator transcribes, so its headline
     number and its per-endpoint rows are read and compared against the record
     they claim to describe (mem-1785121975-bdc3). Every cell is read UNDER THE
     HEADER THAT NAMES IT — "the value appears somewhere in the row" is the
     column-level version of a vacuous check — and the table is rendered under
     every outcome class the record can hold, because a column like `n` exists
     precisely for the outcome an all-success fixture cannot produce
     (mem-1785123232-2aff),
 12. the report lands on STDOUT and the diagnostics on STDERR, because the
     runbook 1b publishes tells the operator to redirect one of them.

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

Both of those fakes are injected BELOW `main()`, so on their own they prove the
library and say nothing about the wiring (mem-1785120628-7b8d): a CLI flag that
never reaches the keyword it names, or a write that never happens, stays green
through every one of them while `main()` prints its success message regardless.
So the checks for properties 10 and 2 drive `MOD.main(argv)` itself, over
`FakeTransport`, with `--out` at a temporary path, and assert against the record
that reached DISK and the code `main()` returned — never against what it printed.

Follows the repo's dual-mode shape-test convention (see
`test_plex_ramdisk_bind_mount_shape.py`): module-level `test_<name>() -> bool`
printing `OK` / `FAIL: ...` (no `assert`), plus `main() -> int` summing them.
Stdlib only.
"""

import contextlib
import datetime
import http.client
import io
import json
import os
import pathlib
import re
import socket
import sys
import tempfile
import types

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
# The SAME INSTANT in a non-UTC zone, with a half-hour offset so a stamp that
# merely looks plausible cannot coincide with the right one. The record promises
# UTC and normalises to it; `main()` never passes `now`, so that normalisation
# has no live symptom and is observable only through this seam.
PROBE_NOW_SHIFTED = PROBE_NOW.astimezone(datetime.timezone(datetime.timedelta(hours=9, minutes=30)))
# Distinct from the harness's own DEFAULT_TIMEOUT, so "the flag reached the
# request" is distinguishable from "the default did".
PROBE_TIMEOUT = 0.37

# Scripted timings: five distinct values whose min/median/max are all different,
# so a statistic computed off the wrong end (or off the raw list order) shows.
FAKE_TTFB = [37.0, 11.0, 91.0, 53.0, 23.0]  # -> min 11.0, median 37.0, max 91.0
FAKE_TOTAL = [74.0, 22.0, 182.0, 106.0, 46.0]  # -> min 22.0, median 74.0, max 182.0
FAKE_TTFB_STATS = (11.0, 37.0, 91.0)
FAKE_TOTAL_STATS = (22.0, 74.0, 182.0)

# A SECOND set of timings, for the direct leg only. The report's headline is a
# subtraction between the two legs' medians; with both legs on one script that
# difference is 0.0, which prints identically whichever way round the operands
# go. These make the difference non-zero and its sign observable.
FAKE_DIRECT_TTFB = [12.0, 4.0, 60.0, 20.0, 8.0]  # -> min 4.0, median 12.0, max 60.0
FAKE_DIRECT_TOTAL = [30.0, 10.0, 120.0, 50.0, 18.0]  # -> min 10.0, median 30.0, max 120.0

# A THIRD and FOURTH set, for the AUTHENTICATED library legs. The headline is
# specifically the overhead on the UNAUTHENTICATED path; with every path on one
# script the filter that selects it is invisible, because the number it would
# print without the filter is the same number. These make the library A/B
# (500 - 100 = +400.0) differ from the /identity A/B (37 - 12 = +25.0).
FAKE_LIB_TTFB = [500.0, 400.0, 900.0, 600.0, 300.0]  # -> median 500.0
FAKE_LIB_TOTAL = [1000.0, 800.0, 1800.0, 1200.0, 600.0]
FAKE_LIB_DIRECT_TTFB = [100.0, 80.0, 300.0, 200.0, 60.0]  # -> median 100.0
FAKE_LIB_DIRECT_TOTAL = [200.0, 160.0, 600.0, 400.0, 120.0]

# The HTTP status a rejected probe answers with: a real round trip, a real
# status line, and not a measurement of anything the endpoint is named for.
PROBE_REJECT_STATUS = 401
#
# 401 alone is not enough, and that is a structural point rather than a taste.
# The harness's success test is a RANGE — `200 <= status < 300` — and a range
# sampled at one interior point is guarded on one side only: with 401 as the sole
# non-2xx the fixture could construct, widening the band to `< 400`, or dropping
# its floor to `100 <=`, left every check in this file green, because every such
# widening still excludes 401 (mem-1785124653-a61d). The motivating example is
# exactly the sample most likely to be the only one.
#
# The untested side was the REACHABLE one. `--direct plex.yoonnation.com:80`
# answers **301** out of this repo's own Traefik, 3/3 samples; under the
# surviving mutation that redirect filed as a 2.4 ms measurement of `/identity`,
# printed a "Traefik overhead" computed from a real 200 minus a redirect, and
# exited 0. A captive portal on the mobile hotspot Step 1c is captured from
# answers 302, and that capture is taken once.
#: Just outside each edge (1xx below, 3xx above) plus the error pages Traefik
#: really serves. None of these is a measurement of the endpoint it names.
NON_MEASUREMENT_STATUSES = (100, 199, 300, 301, 404, 502)
#: Just INSIDE each edge. Without these a NARROWED band (`200 <= s < 250`, or
#: `210 <= s`) would be exactly as invisible as a widened one.
MEASUREMENT_STATUSES = (200, 201, 204, 299)

# The body every fake response returns. Its LENGTH is asserted: the payload size
# is the one control that separates "the total got slower" from "the payload got
# bigger", so a harness that computes it and drops it has thrown away Step 4's
# only defence against that confounder.
PROBE_BODY = b"probe-body-9c4f"

_COLUMN_GAP = re.compile(r"\s{2,}")


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
    """Compile the harness FROM ITS SOURCE TEXT and run it, under the network guard.

    Deliberately NOT `importlib.util.spec_from_file_location` + `exec_module`,
    which is the obvious way and which consults `__pycache__`. The cache key is
    `(source mtime truncated to whole SECONDS, source size)`, so a mutation
    matrix — the one instrument whose entire job is detecting false greens — can
    poison it: mutate the harness, run it, restore with `shutil.copy2` (which
    PRESERVES the original mtime), and if the edit was the same size the stale
    `.pyc` still validates against the restored source. Every later run then
    executes the MUTATION while the file on disk, and its sha256, are pristine.

    That is not hypothetical here. This very file caught it: `scripts/__pycache__`
    held a `render_report` compiled with the overhead subtraction REVERSED,
    left behind by the previous round's matrix, and the gate had been importing
    it ever since (`scripts/run_gate.py` runs each shape test as
    `[sys.executable, path]` with no `-B`). `python -B` does not help — it stops
    the cache being WRITTEN, not being READ.

    `compile()` over the text read from disk has no cache to consult, so the
    artifact under test is the artifact in git, always. Same family as
    mem-1785121487-cbe4, one level up: there a matrix row measured the wrong
    mutation; here every run measures the wrong file.
    """
    module = types.ModuleType("measure_plex_latency")
    module.__file__ = str(HARNESS)
    code = compile(HARNESS.read_text(encoding="utf-8"), str(HARNESS), "exec")
    with _no_network():
        exec(code, module.__dict__)  # noqa: S102 - the file under test, by design
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

    def __init__(self, ttfbs=FAKE_TTFB, totals=FAKE_TOTAL, per_origin=None):
        self.ttfbs = ttfbs
        self.totals = totals
        # url-substring -> (ttfbs, totals). Lets one run give the two legs
        # DIFFERENT timings, which is what makes the report's Traefik-vs-direct
        # subtraction have an observable sign.
        self.per_origin = dict(per_origin or {})
        self.calls: list = []

    def _script(self, url):
        for needle, script in self.per_origin.items():
            if needle in url:
                return script
        return self.ttfbs, self.totals

    def __call__(self, url, timeout=None, token=None):
        index = sum(1 for call in self.calls if call[0] == url)
        self.calls.append((url, timeout, token))
        ttfbs, totals = self._script(url)
        return {
            "status": 200,
            "ttfb_ms": ttfbs[index % len(ttfbs)],
            "total_ms": totals[index % len(totals)],
            "bytes": 11,
            "failed_after_ms": None,
            "error": None,
        }


class _FakeResponse:
    """The bare surface `time_request` uses: a status line and a readable body.

    The status is a CONSTRUCTOR ARGUMENT, not a class constant. Hardcoding it to
    200 is what made the whole file structurally incapable of constructing an
    answered-but-rejected probe: the fixture could produce two outcomes (a
    success and a dead socket) where the protocol has three, so a 401 recorded
    as a library-load measurement could not be seen by any check here
    (mem-1785123219-03c9).

    ANY status is constructible, not an enumerated few: the harness's success
    test is a range, and pinning a range needs samples on both sides of both
    edges — including a 1xx and a 299, which no hand-written reason table would
    have thought to list.
    """

    def __init__(self, status=200):
        self.status = status
        # `reason` is part of what the harness renders into its error string, so
        # it cannot be left blank for the statuses a real server would name.
        # Taken from the stdlib's own table, which is what a real server sends.
        self.reason = http.client.responses.get(status, "")

    def read(self):
        return PROBE_BODY


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

    `status_by_host` is the THIRD outcome class, and the one this fixture used
    to be incapable of expressing: the host answers, promptly and completely,
    with a status that means the endpoint did no work. Failing at the socket and
    refusing at the protocol are not the same event, and only one of them was
    modelled here.

    A note on what this fake ACCEPTS AND DISCARDS, because that set — not the
    assertions anyone has written — decides which properties this file is capable
    of guarding at all. `request()` used to take `method` and throw it away, so
    "the harness only ever GETs" could not be asserted here even in principle:
    mutating the harness to `POST` or `DELETE` left the shape test fully green
    and DELETE survived the entire `just test` gate, against the live household
    Plex this script is pointed at (mem-1785124642-053b). Method and body are now
    recorded and read. `_FakeResponse` was the same defect on the status axis one
    round earlier. Before adding a check here, read this stub's signature beside
    the tuple it records and set-diff the two.
    """

    def __init__(self, failing_hosts=(), flaky_hosts=None, status_by_host=None):
        self.failing_hosts = set(failing_hosts)
        self.flaky_hosts = {host: set(idx) for host, idx in (flaky_hosts or {}).items()}
        self.status_by_host = dict(status_by_host or {})
        self.attempts: dict = {}
        self.opened: list = []
        # One dict per attempted request: host, METHOD, path, BODY, headers. The
        # only place what actually went on the wire is observable — everything
        # else sees either the environment the token came from or the record it is
        # kept out of. A dict rather than a tuple so a later axis can be added
        # without every reader silently unpacking the wrong field.
        self.requests: list = []

    @contextlib.contextmanager
    def installed(self):
        saved = (http.client.HTTPConnection, http.client.HTTPSConnection)
        transport = self

        class _Conn:
            def __init__(self, host, port=None, timeout=None, **kwargs):
                attempt = transport.attempts.get(host, 0)
                transport.attempts[host] = attempt + 1
                transport.opened.append((host, port, timeout))
                self.host = host
                self.fails = (
                    host in transport.failing_hosts
                    or attempt in transport.flaky_hosts.get(host, ())
                )

            # Mirrors `http.client.HTTPConnection.request(method, url, body,
            # headers)` positionally, so a harness that starts sending a body
            # lands it where this stub can see it.
            def request(self, method, path, body=None, headers=None, **kwargs):
                # Recorded BEFORE the failure branch: what a doomed attempt sent
                # is as interesting as what a successful one did.
                transport.requests.append(
                    {
                        "host": self.host,
                        "method": method,
                        "path": path,
                        "body": body,
                        "headers": dict(headers or {}),
                    }
                )
                if self.fails:
                    raise TimeoutError("the read operation timed out")

            def getresponse(self):
                return _FakeResponse(transport.status_by_host.get(self.host, 200))

            def close(self):
                return None

        http.client.HTTPConnection = _Conn
        http.client.HTTPSConnection = _Conn
        try:
            yield self
        finally:
            (http.client.HTTPConnection, http.client.HTTPSConnection) = saved


def _transport_run(
    failing_hosts=(), flaky_hosts=None, status_by_host=None, repeats=len(FAKE_TTFB), **kwargs
):
    """Drive the harness's REAL prober (`probe=None`) over `FakeTransport`.

    Returns `(record, transport, error)`. Deliberately does not inject a probe:
    the point is to execute `time_request` itself, including its except-branch
    AND its non-2xx branch.
    """
    transport = FakeTransport(failing_hosts, flaky_hosts, status_by_host)
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


def _fake_run(token=None, repeats=len(FAKE_TTFB), probe=None, now=PROBE_NOW):
    """Drive the harness's real pipeline with the fake prober, offline.

    Returns `(record, probe, error)`. A harness that ignores the injected prober
    and reaches for the wire trips the socket guard; that is reported as an
    `error` string so the caller prints a FAIL, rather than escaping as a
    traceback that aborts the remaining checks.

    `now` is a parameter and not a constant because the record's UTC promise is
    only observable when the injected clock is NOT already UTC.
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
                now=now,
            )
    except NetworkAttempted as exc:
        return None, probe, f"NetworkAttempted: {exc}"
    return record, probe, None


@contextlib.contextmanager
def _env(name, value):
    """Bind one environment variable for the duration of a check, then restore it.

    `main()` resolves the token from the real environment, so a developer who
    happens to export `PLEX_TOKEN` would otherwise get a different set of probes
    than the gate does.
    """
    previous = os.environ.get(name)
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous


def _cli_argv(out, extra=(), repeats=2, timeout=PROBE_TIMEOUT):
    """The argv an operator would actually type, pointed at sentinel targets."""
    return [
        "--label", PROBE_LABEL,
        "--vantage", "external",
        "--host", PROBE_HOST,
        "--direct", PROBE_DIRECT,
        "--repeats", str(repeats),
        "--timeout", str(timeout),
        "--out", str(out),
        *extra,
    ]


class _Streams:
    """What `main()` wrote, per stream.

    Captured SEPARATELY and never re-merged by default. Merging them into one
    buffer — which is what this helper used to do — makes "the report is printed
    to stdout" unobservable: send `render_report`'s output to stderr instead and
    every check still finds the text it was looking for, while an operator
    following the runbook's `> baseline.txt` keeps an empty file
    (mem-1785123232-2aff).
    """

    def __init__(self, out, err):
        self.out = out
        self.err = err

    @property
    def both(self):
        return self.out + self.err

    def __repr__(self):
        return f"_Streams(out={len(self.out)} chars, err={len(self.err)} chars)"


def _cli_run(argv, failing_hosts=(), token=None, status_by_host=None):
    """Drive the harness's ENTRY POINT for real: argv -> record -> disk -> exit code.

    Returns `(rc, streams, transport, error)`. The fakes elsewhere in this file
    are injected below `main()`, so nothing else here executes the wiring
    between an argument and the measurement it is supposed to select, or the
    write that produces this task's named output. This runs the real thing:
    `main()` parses the argv, the harness's real `time_request` runs over
    `FakeTransport`, and the caller inspects the file on disk and the returned
    code. stdout/stderr are captured because the gate log should not carry a
    report for a run against `.invalid` hosts — and captured apart, because
    WHICH stream a line landed on is itself part of the published contract.
    """
    transport = FakeTransport(failing_hosts, status_by_host=status_by_host)
    out, err = io.StringIO(), io.StringIO()
    streams = lambda: _Streams(out.getvalue(), err.getvalue())  # noqa: E731 - read twice below
    try:
        with _env(MOD.TOKEN_ENV, token), _no_network(), transport.installed():
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = MOD.main(argv)
    except SystemExit as exc:  # argparse refuses malformed argv by exiting
        rc = exc.code
    except NetworkAttempted as exc:
        return None, streams(), transport, f"NetworkAttempted: {exc}"
    except OSError as exc:
        # An OSError escaping main() IS a defect, not a fixture problem: a write
        # that cannot happen has to be reported through the exit contract the
        # runbook publishes, not as a traceback on the operator's one-shot
        # capture. Returned as an error string so the check prints FAIL rather
        # than aborting every check after it.
        return None, streams(), transport, f"{type(exc).__name__} escaped main(): {exc}"
    return rc, streams(), transport, None


def _read_records(path):
    """Parse the JSONL the CLI claims to have written. Returns `(records, error)`.

    A missing file is `([], None)` — an absence the caller asserts on — while
    unparseable content is an error, because "the file exists" is not the
    property Step 4 depends on.
    """
    path = pathlib.Path(path)
    if not path.exists():
        return [], None
    try:
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ], None
    except ValueError as exc:
        return None, f"unparseable JSONL: {exc}"


def _report_table(report):
    """Parse the rendered table POSITIONALLY: `(headers, {endpoint: {header: cell}})`.

    The point of parsing rather than substring-searching is the column. A check
    that asks "is this number somewhere in this row?" cannot tell a TTFB from a
    total when the two cells are swapped in the row's f-string — the row still
    contains both numbers, so the check passes while the report prints 806 ms of
    total under a heading that says TTFB. Cells are therefore keyed by the
    HEADER ABOVE THEM: both the header line and the rows are laid out with the
    same field widths, so runs of two-or-more spaces separate the same columns
    in both.

    A row that does not split into exactly as many cells as the header is left
    OUT of the returned mapping, so the caller reports it as a missing row
    rather than silently checking nothing.
    """
    lines = report.splitlines()
    index = next((i for i, line in enumerate(lines) if "endpoint" in line), None)
    if index is None:
        return None, {}
    headers = _COLUMN_GAP.split(lines[index].strip())
    rows = {}
    for line in lines[index + 1:]:
        cells = _COLUMN_GAP.split(line.strip())
        if len(cells) == len(headers):
            rows[cells[0]] = dict(zip(headers, cells))
    return headers, rows


def _header_for(headers, needle):
    """The one header that IS `needle`, else the one containing it; None if ambiguous.

    Exact first, because the `n` column's whole label is one letter and that
    letter appears inside three of its neighbours.
    """
    headers = list(headers or ())
    exact = [h for h in headers if h == needle]
    if exact:
        return exact[0]
    matches = [h for h in headers if needle.lower() in h.lower()]
    return matches[0] if len(matches) == 1 else None


def _fmt_cell(value):
    """Render one statistic the way the report must: one decimal, or `n/a`."""
    return "n/a" if value is None else f"{value:.1f}"


def _expected_row(target):
    """What the record says this endpoint's row must contain, cell by cell.

    Keyed by a *substring of the header* rather than by position, so the header
    line and the row f-string have to agree with each other AND with the record.
    """
    def _triple(series):
        return "/".join(_fmt_cell(target[series][stat]) for stat in ("min_ms", "median_ms", "max_ms"))

    return {
        "endpoint": target["name"],
        # Not `requested/requested`: this column exists for exactly the case
        # where those two numbers differ, and a median over one surviving sample
        # of five is typographically identical to a clean run without it.
        "n": f"{target['succeeded']}/{target['requested']}",
        "TTFB": _triple("ttfb"),
        "total": _triple("total"),
        "status": ",".join(str(s) for s in target["statuses"]) or "-",
    }


def _row_mismatches(record, report):
    """Every (endpoint, column, expected, got) the report gets wrong. Empty is correct."""
    headers, rows = _report_table(report)
    problems = []
    for target in record["targets"]:
        row = rows.get(target["name"])
        if row is None:
            problems.append((target["name"], "<row>", "present", "missing"))
            continue
        for needle, expected in _expected_row(target).items():
            header = _header_for(headers, needle)
            if header is None:
                problems.append((target["name"], needle, "one header", f"headers={headers}"))
                continue
            if row[header] != expected:
                problems.append((target["name"], header, expected, row[header]))
    return problems


def _elapsed_diagnostics(target, expected):
    """`failed_after_ms` really is one MEASURED elapsed time per failed sample.

    Length alone is not enough and the difference is not academic: the list is
    built by comprehension over the failed samples, so a harness that stops
    recording the elapsed time still produces a list of the right length, full
    of `None`. That passed a length-only assertion while the diagnostic this
    field exists to be had ceased to exist (matrix row M4).
    """
    values = target.get("failed_after_ms")
    return (
        isinstance(values, list)
        and len(values) == expected
        and all(isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0 for v in values)
    )


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

    # ...and the URL the RECORD carries is the URL that was actually probed. It
    # was the one per-target field no check read, so `"url": ""` survived the
    # whole file: `build_targets`' copy above is read, `measure_target`'s copy —
    # the one that reaches disk, and the only thing that says WHICH address a
    # row's numbers came from when a host or a port changed between two runs —
    # was not. Compared against the prober's own call log rather than against a
    # literal, so the record and the wire have to agree with each other.
    record, probe, run_error = _fake_run()
    recorded_urls = sorted(t.get("url") for t in (record or {}).get("targets", []))
    probed_urls = sorted({call[0] for call in probe.calls})
    expected_urls = sorted([f"https://{PROBE_HOST}/identity", f"http://{PROBE_DIRECT}/identity"])
    record_urls_ok = (
        run_error is None
        and recorded_urls == probed_urls
        and recorded_urls == expected_urls
    )

    ok = traefik_ok and direct_ok and default_port_ok and record_urls_ok
    print(
        f"{'OK' if ok else 'FAIL'}: probes Traefik and the direct backend "
        f"(traefik={traefik_urls}, direct={direct_urls}, default_direct={MOD.DEFAULT_DIRECT!r}, "
        f"recorded_urls={recorded_urls}, probed_urls={probed_urls}, error={run_error})"
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
    """AC: every record is self-describing — schema + label + vantage + UTC timestamp.

    Step 4 diffs baseline against post-change out of this JSONL; a record that
    loses its label, or its LAN/external vantage, cannot be paired with the run
    it is supposed to be compared to. The timestamp is injected, so a value
    invented instead of derived (or a naive local-time stamp) reddens.

    `schema` is here for the same reason and was the one part of the record's
    self-description nothing read: `logs/plex-latency.jsonl` ALREADY holds
    records at three different versions, and the field exists so Step 4 can
    refuse to diff across incompatible shapes rather than silently comparing
    different things. Pinned two ways — the record's value must come FROM the
    module constant (delete the field and this reddens) and that constant must
    be at or past the version that made a non-2xx a non-measurement (revert it
    and older, differently-meant records start claiming the current shape).
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
    # UTC is a promise about NORMALISATION, not just about the default clock. The
    # record converts whatever it is handed; `main()` never passes `now`, so
    # dropping that conversion has no live symptom and the injectable clock is
    # the only seam where it shows. Same instant, expressed at +09:30: the stamp
    # must come out byte-identical to the UTC run's, Z and all — an unconverted
    # one renders `...T13:35:06+09:30`, which is the same moment and is not what
    # this field says it is.
    shifted, _, shifted_error = _fake_run(now=PROBE_NOW_SHIFTED)
    shifted_stamp = (shifted or {}).get("timestamp")
    normalised_ok = (
        shifted_error is None
        # The fixture's own discriminating power: a UTC "shifted" clock would
        # make this row pass for free.
        and PROBE_NOW_SHIFTED.utcoffset() != datetime.timedelta(0)
        and isinstance(shifted_stamp, str)
        and shifted_stamp.endswith("Z")
        and shifted_stamp == stamp
    )
    # A FLOOR, not a literal: a bump must not redden the gate, but a revert to a
    # version whose records mean something else must.
    schema_ok = (
        isinstance(MOD.SCHEMA_VERSION, int)
        and MOD.SCHEMA_VERSION >= 4
        and record.get("schema") == MOD.SCHEMA_VERSION
    )
    ok = (
        record.get("label") == PROBE_LABEL
        and record.get("vantage") == PROBE_VANTAGE
        and utc_ok
        and same_instant
        and normalised_ok
        and schema_ok
    )
    print(
        f"{'OK' if ok else 'FAIL'}: run record carries schema + label + vantage + UTC timestamp "
        f"(schema={record.get('schema')!r} constant={getattr(MOD, 'SCHEMA_VERSION', None)!r}, "
        f"label={record.get('label')!r}, vantage={record.get('vantage')!r}, "
        f"timestamp={stamp!r}, utc={utc_ok}, matches_injected_clock={same_instant}, "
        f"from_{PROBE_NOW_SHIFTED.utcoffset()}_clock={shifted_stamp!r} normalised={normalised_ok})"
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
    # The SHIPPED default has to support the statistic this check is about. The
    # task says "N repeats per endpoint (default >= 5)", the harness's entire
    # output is min/median/max, and over one sample all three are the same number
    # rendered three times — vacuous and typographically identical to a clean run.
    # Nothing else here reads the constant: every other check passes an explicit
    # `repeats`, so `DEFAULT_REPEATS = 1` survived the whole file. Asserted as a
    # FLOOR (a bump is fine) at BOTH the constant and the parser, because the wire
    # between them is its own failure: `default=1` on the flag makes the constant
    # decorative.
    parsed, parse_rc = _parse_argv(["--label", PROBE_LABEL, "--vantage", "external"])
    default_repeats_ok = (
        isinstance(MOD.DEFAULT_REPEATS, int)
        and MOD.DEFAULT_REPEATS >= 5
        and parse_rc is None
        and parsed is not None
        and parsed.repeats == MOD.DEFAULT_REPEATS
    )
    ok = (
        bool(targets)
        and got_ttfb == {FAKE_TTFB_STATS}
        and got_total == {FAKE_TOTAL_STATS}
        and counts == {len(FAKE_TTFB)}
        and len(probe.calls) == len(targets) * len(FAKE_TTFB)
        and default_repeats_ok
    )
    print(
        f"{'OK' if ok else 'FAIL'}: min/median/max computed from the samples "
        f"(ttfb={sorted(got_ttfb)}, total={sorted(got_total)}, counts={sorted(counts)}, "
        f"probe_calls={len(probe.calls)}, targets={len(targets)}, "
        f"default_repeats={getattr(MOD, 'DEFAULT_REPEATS', None)!r} "
        f"parser_default={None if parsed is None else parsed.repeats!r} (both must be >= 5))"
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
    """AC: per target, `ttfb`, `total` and `bytes` all cover an identical sample set.

    Models the live external-vantage case exactly: the Traefik leg answers and
    the direct RFC1918 leg is unreachable. The dead leg must summarise to
    `count 0` on EVERY series with every statistic None — not `ttfb count 0`
    beside `total count N`, and not a suspiciously fast pair either — and the
    report must decline to print a Traefik-overhead figure it cannot compute.
    The counts must also agree on the HEALTHY leg, so the check cannot be
    satisfied by a harness that simply reports zero everywhere.

    `bytes` is in that list because it is the control for the confounder Step 4
    will meet first — "the total got slower" versus "the payload got bigger" —
    and it was computed into every sample and then dropped before the record,
    the same shape `failed_after_ms` had a round earlier. Its median is compared
    against the real body length, so carrying a constant would not satisfy it.
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

    # The invariant, asserted for EVERY target rather than only the dead one, and
    # over EVERY series the record carries — a fourth series added later that
    # silently covers a different sample set is the same defect with a new name.
    agree = all(
        _series(t, "ttfb", "count")
        == _series(t, "total", "count")
        == _series(t, "bytes", "count")
        == t.get("succeeded")
        and (t.get("succeeded"), t.get("failed")) != (None, None)
        and (t.get("succeeded") or 0) + (t.get("failed") or 0) == t.get("requested")
        for t in record["targets"]
    )
    dead_is_empty = (
        _series(dead, "ttfb", "count") == 0
        and _series(dead, "total", "count") == 0
        and _series(dead, "bytes", "count") == 0
        and all(
            _series(dead, series, f"{stat}_{unit}") is None
            for series, unit in (("ttfb", "ms"), ("total", "ms"), ("bytes", "bytes"))
            for stat in ("min", "median", "max")
        )
        and bool(dead.get("errors"))
        # The elapsed time of each failure is kept, but only as a diagnostic:
        # one entry per attempt on a leg that never answered, and NONE on a leg
        # that did. A harness that filed these as latencies instead would show
        # up as a live leg with a non-empty list. Values, not just a length — a
        # list of the right length full of `None` is not a diagnostic.
        and _elapsed_diagnostics(dead, dead.get("requested"))
    )
    live_is_measured = (
        live.get("succeeded") == len(FAKE_TTFB)
        and not live.get("errors")
        and _series(live, "total", "median_ms") is not None
        and live.get("failed_after_ms") == []
        # The payload the leg actually returned, not a placeholder.
        and _series(live, "bytes", "median_bytes") == len(PROBE_BODY)
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
        f"{'OK' if ok else 'FAIL'}: ttfb, total and bytes summarise the same samples "
        f"(counts_agree={agree}, dead_leg ttfb={_series(dead, 'ttfb', 'count')}"
        f"/total={_series(dead, 'total', 'count')}/bytes={_series(dead, 'bytes', 'count')} "
        f"median_total={_series(dead, 'total', 'median_ms')!r}, "
        f"live_leg={live.get('succeeded')}/{live.get('requested')} "
        f"median_bytes={_series(live, 'bytes', 'median_bytes')!r} (body={len(PROBE_BODY)}), "
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
    counts = (
        (flaky.get("ttfb") or {}).get("count"),
        (flaky.get("total") or {}).get("count"),
        (flaky.get("bytes") or {}).get("count"),
    )
    # The failure diagnostic the module docstring promises is KEPT: one entry per
    # failed sample, carried into the record rather than computed and dropped.
    # Its length tracks the FAILURES, so it cannot be confused with either
    # latency series — and the partial row is what separates those numbers.
    diagnostics = flaky.get("failed_after_ms")
    diagnostics_ok = _elapsed_diagnostics(flaky, len(failed_attempts))
    ok = (
        bool(transport.opened)
        and flaky.get("requested") == len(FAKE_TTFB)
        and flaky.get("succeeded") == expected_ok
        and flaky.get("failed") == len(failed_attempts)
        and counts == (expected_ok, expected_ok, expected_ok)
        and bool(flaky.get("errors"))
        and (flaky.get("ttfb") or {}).get("median_ms") is not None
        and diagnostics_ok
    )
    print(
        f"{'OK' if ok else 'FAIL'}: a partial failure does not inflate the sample count "
        f"(requested={flaky.get('requested')}, succeeded={flaky.get('succeeded')}, "
        f"failed={flaky.get('failed')}, series_counts={counts}, expected={expected_ok}, "
        f"failed_after_ms={diagnostics!r})"
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

    Checked at BOTH levels, because they fail independently. That the library
    honours a `probe_direct` keyword and that the parser owns a `--skip-direct`
    flag are two facts with one untested wire between them: cut it, and the CLI
    still prints "note: --skip-direct", then probes the dead leg anyway, stamps
    `direct_probed=true` and exits 1 — the exact failure the flag exists to
    prevent, now announcing that it is not happening (mem-1785120628-7b8d). So
    the flag is also driven through `main()` against a direct host that CANNOT
    answer, and judged by the record on disk rather than by the message.
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
    # The wire, driven end to end. The direct host is made unreachable, which is
    # the live external case: with the flag honoured the run never touches it and
    # exits 0; with the flag a no-op the run probes it, fails, and exits 1.
    direct_host = PROBE_DIRECT.split(":")[0]
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "skip-direct.jsonl"
        cli_rc, _, cli_transport, cli_error = _cli_run(
            _cli_argv(out, ["--skip-direct"]), failing_hosts={direct_host}
        )
        written, parse_error = _read_records(out)
    on_disk = (written or [{}])[-1] if written else {}
    cli_vias = sorted({t.get("via") for t in on_disk.get("targets", [])})
    cli_ok = (
        cli_error is None
        and parse_error is None
        and cli_rc == 0
        and len(written or []) == 1
        and on_disk.get("direct_probed") is False
        and cli_vias == ["traefik"]
        # Nothing was even opened to the address the flag says to leave alone.
        and direct_host not in cli_transport.attempts
    )

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
        and cli_ok
    )
    print(
        f"{'OK' if ok else 'FAIL'}: the direct leg is skippable and recorded "
        f"(skipped_vias={skipped_vias}, default_vias={default_vias}, "
        f"direct_probed={None if record is None else record.get('direct_probed')!r}/"
        f"{None if both is None else both.get('direct_probed')!r}, flags={flags}, "
        f"cli_rc={cli_rc}, cli_record_direct_probed={on_disk.get('direct_probed')!r}, "
        f"cli_vias={cli_vias}, cli_opened={sorted(cli_transport.attempts)}, "
        f"cli_error={cli_error or parse_error})"
    )
    return ok


def test_cli_appends_the_record_and_honours_its_exit_contract() -> bool:
    """AC: the ENTRY POINT persists one record per run and returns 0 / 1 / 2.

    The JSONL is this task's named output and Step 4's only input, and `main()`
    is the only thing that writes it. Neuter the write and every library check
    here stays green while `main()` still prints "appended 1 record to <path>"
    unconditionally — a false success on a capture that is taken once, from a
    mobile hotspot, and cannot be retaken (mem-1785120628-7b8d). So the artifact
    is read back from disk instead of the message being believed.

    Four properties, all only observable from here:

    * a healthy run exits 0 and leaves exactly ONE parseable record carrying the
      argv it was given (a record whose targets came from a default instead of
      the flags would pair two different measurements in Step 4),
    * runs ACCUMULATE — a second run appends rather than truncating, which is
      the whole premise of an append-only log,
    * an unreachable target exits 1 *after* the record is written, so the
      diagnosis is never lost with the failure,
    * `--no-log` writes nothing, and `--repeats 0` is refused with 2 before any
      probing happens. Both codes are published in the module docstring and are
      about to be transcribed into the Step 1b runbook.
    """
    if not _guard("cli appends and exits"):
        return False
    direct_host = PROBE_DIRECT.split(":")[0]
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "nested" / "plex-latency.jsonl"
        healthy_rc, _, _, healthy_err = _cli_run(_cli_argv(out))
        after_first, first_err = _read_records(out)
        second_rc, _, _, second_err = _cli_run(_cli_argv(out))
        after_second, second_parse_err = _read_records(out)
        dead_rc, _, _, dead_err = _cli_run(_cli_argv(out), failing_hosts={direct_host})
        after_dead, dead_parse_err = _read_records(out)

        quiet = pathlib.Path(tmp) / "no-log.jsonl"
        quiet_rc, _, _, quiet_err = _cli_run(_cli_argv(quiet, ["--no-log"]))
        quiet_records, quiet_parse_err = _read_records(quiet)
        # Sampled INSIDE the temporary directory: asked after it is torn down,
        # `exists()` is False for every harness and pins nothing.
        quiet_exists = quiet.exists()

        refused = pathlib.Path(tmp) / "bad-repeats.jsonl"
        refused_rc, _, _, refused_err = _cli_run(_cli_argv(refused, repeats=0))
        refused_records, refused_parse_err = _read_records(refused)
        refused_exists = refused.exists()

    errors = [
        e
        for e in (
            healthy_err, first_err, second_err, second_parse_err, dead_err, dead_parse_err,
            quiet_err, quiet_parse_err, refused_err, refused_parse_err,
        )
        if e
    ]
    if errors or after_first is None or after_second is None or after_dead is None:
        print(f"FAIL: the CLI appends its record and honours the exit contract ({errors})")
        return False

    first = after_first[0] if after_first else {}
    written_ok = (
        healthy_rc == 0
        and len(after_first) == 1
        and first.get("label") == PROBE_LABEL
        and first.get("vantage") == "external"
        and first.get("host") == PROBE_HOST
        and first.get("direct") == PROBE_DIRECT
        and first.get("repeats") == 2
        and first.get("direct_probed") is True
        and sorted({t.get("via") for t in first.get("targets", [])}) == ["direct", "traefik"]
        and all(t.get("succeeded") == 2 for t in first.get("targets", []))
    )
    # Append, not overwrite: the first record must survive the second run.
    appends_ok = second_rc == 0 and len(after_second) == 2 and after_second[0] == first
    # The record is written BEFORE the non-zero return, so a failed capture still
    # leaves the evidence of what failed.
    dead_leg = next(
        (t for t in (after_dead[-1] if after_dead else {}).get("targets", []) if t.get("via") == "direct"),
        {},
    )
    dead_ok = (
        dead_rc == 1
        and len(after_dead) == 3
        and dead_leg.get("succeeded") == 0
        and dead_leg.get("failed") == 2
        and bool(dead_leg.get("errors"))
    )
    quiet_ok = quiet_rc == 0 and quiet_records == [] and not quiet_exists
    refused_ok = refused_rc == 2 and refused_records == [] and not refused_exists

    ok = written_ok and appends_ok and dead_ok and quiet_ok and refused_ok
    print(
        f"{'OK' if ok else 'FAIL'}: the CLI appends its record and honours the exit contract "
        f"(healthy rc={healthy_rc} records={len(after_first)} argv_echoed={written_ok}, "
        f"appends={appends_ok} lines={len(after_second)}, "
        f"unreachable rc={dead_rc} records={len(after_dead)} dead_leg="
        f"{dead_leg.get('succeeded')}/{dead_leg.get('requested')}, "
        f"no_log rc={quiet_rc} wrote={quiet_exists}, "
        f"bad_repeats rc={refused_rc} wrote={refused_exists})"
    )
    return ok


def test_report_states_what_the_record_states() -> bool:
    """AC: every recorded target gets a row, and every cell sits under its own header.

    Both halves of the output are named deliverables of this task, and every
    other check in this file reads the record — so the report was first pinned
    only by its ABSENCE case, then by "the number appears somewhere in the row",
    which is the same vacuity one column further in: swap `ttfb_cell` and
    `total_cell` in the row f-string and the row still contains both numbers,
    while the operator reads 806 ms of TOTAL under a heading that says
    "TTFB min/med/max" (mem-1785123232-2aff). So the table is PARSED and each
    cell compared under the header that names it.

    Rendered under every outcome class the record can hold, because three of the
    five columns are unfalsifiable under an all-success two-leg fixture:

    * healthy, with PER-LEG scripted timings — without them the check is
      vacuous, since over `FakeTransport` every elapsed time is a few
      microseconds and min, median, max and both legs alike all render `0.0`;
    * partial outage — the ONLY class where `succeeded` and `requested` differ,
      which is the entire reason the `n` column exists ("a median over one
      surviving sample of five is typographically identical to a clean run").
      An all-success fixture prints 5/5 whether the harness sources that column
      from the survivors or from the request count;
    * answered-but-rejected (401) — the class that makes the `status` column
      load-bearing: it is the operator's only signal that the fast number in
      front of them measures an error page;
    * direct leg skipped — the one-legged record an external capture produces.
    """
    if not _guard("report states the record"):
        return False
    probe = FakeProbe(per_origin={f"http://{PROBE_DIRECT}": (FAKE_DIRECT_TTFB, FAKE_DIRECT_TOTAL)})
    healthy, _, healthy_err = _fake_run(probe=probe)
    partial, _, partial_err = _transport_run(flaky_hosts={PROBE_HOST: {1, 3}})
    rejected, _, rejected_err = _transport_run(status_by_host={PROBE_HOST: PROBE_REJECT_STATUS})
    skipped, _, skipped_err = _transport_run(probe_direct=False)
    errors = [e for e in (healthy_err, partial_err, rejected_err, skipped_err) if e]
    classes = {
        "healthy": healthy,
        "partial-outage": partial,
        "rejected-401": rejected,
        "direct-skipped": skipped,
    }
    if errors or any(record is None for record in classes.values()):
        print(f"FAIL: the report states what the record states (fixtures: {errors})")
        return False

    problems = {
        name: _row_mismatches(record, MOD.render_report(record))
        for name, record in classes.items()
    }
    problems = {name: found for name, found in problems.items() if found}

    # Self-guards: each class must actually be able to show the mutation it is
    # here for, so a later fixture change cannot quietly make them all identical.
    def _leg(record, via):
        return next((t for t in record["targets"] if t["via"] == via), {})

    healthy_traefik, healthy_direct = _leg(healthy, "traefik"), _leg(healthy, "direct")
    partial_traefik = _leg(partial, "traefik")
    rejected_traefik = _leg(rejected, "traefik")
    discriminating = {
        # min/median/max all differ, and the TTFB triple differs from the total
        # triple, so a statistic read off the wrong end or a swapped pair of
        # cells changes the rendered text.
        "healthy stats differ": (
            len({healthy_traefik["ttfb"][s] for s in ("min_ms", "median_ms", "max_ms")}) == 3
            and _expected_row(healthy_traefik)["TTFB"] != _expected_row(healthy_traefik)["total"]
            and healthy_traefik["ttfb"]["median_ms"] != healthy_direct["ttfb"]["median_ms"]
        ),
        # succeeded != requested, so `n` is not 5/5 either way.
        "partial n is not full": (
            0 < partial_traefik.get("succeeded", 0) < partial_traefik.get("requested", 0)
        ),
        # A status the harness cannot have invented, on a leg with no successes.
        "rejected status is visible": (
            rejected_traefik.get("statuses") == [PROBE_REJECT_STATUS]
            and rejected_traefik.get("succeeded") == 0
        ),
        # One leg only, so a report that always prints two rows is caught.
        "skipped has one leg": len(skipped["targets"]) == 1,
    }

    ok = not problems and all(discriminating.values())
    print(
        f"{'OK' if ok else 'FAIL'}: the report states what the record states "
        f"(mismatches={problems or 'none'}, "
        f"fixture_discriminates={ {k: v for k, v in discriminating.items() if not v} or 'all'})"
    )
    return ok


def test_report_headline_is_the_unauthenticated_traefik_overhead() -> bool:
    """AC: the headline is `traefik - direct` median TTFB, on the path it names.

    This one line is the conclusion Step 4 exists to draw and the line 1b tells
    the operator to transcribe off the screen: invert the subtraction and
    "Traefik costs 25.0 ms" becomes "Traefik saves 25.0 ms" while the JSONL
    stays perfectly correct. The data survives; the transcript does not.

    Two things are pinned, and the second needs a token to be visible at all:

    * the VALUE and its SIGN, against the record it claims to describe;
    * the PATH SELECTOR. The line is labelled `/identity` and the filter that
      keeps it to `/identity` is invisible in an unauthenticated fixture — drop
      it and the same line prints, with the library legs' difference under the
      unauthenticated path's name. So this runs with a token AND with the
      library legs on their own timings, and asserts the two candidate numbers
      are different before comparing.

    Plus the WIRE, which is a separate fact: `main()` must print
    `render_report` of the record it wrote. That half cannot see a
    `render_report` mutation — both sides of the comparison move together — so
    it guards only that the text reaching the operator describes the record
    reaching disk.
    """
    if not _guard("report headline"):
        return False
    probe = FakeProbe(
        per_origin={
            f"https://{PROBE_HOST}/library/sections": (FAKE_LIB_TTFB, FAKE_LIB_TOTAL),
            f"http://{PROBE_DIRECT}/library/sections": (
                FAKE_LIB_DIRECT_TTFB,
                FAKE_LIB_DIRECT_TOTAL,
            ),
            f"http://{PROBE_DIRECT}/identity": (FAKE_DIRECT_TTFB, FAKE_DIRECT_TOTAL),
        }
    )
    record, _, error = _fake_run(token=PROBE_TOKEN, probe=probe)
    if record is None:
        print(f"FAIL: the report headline is the unauthenticated Traefik overhead ({error})")
        return False
    report = MOD.render_report(record)

    def _median(via, path):
        target = next(
            (t for t in record["targets"] if t["via"] == via and t["path"] == path), None
        )
        return None if target is None else target["ttfb"]["median_ms"]

    unauth_overhead = _median("traefik", MOD.UNAUTH_PATH) - _median("direct", MOD.UNAUTH_PATH)
    library_overhead = _median("traefik", "/library/sections") - _median(
        "direct", "/library/sections"
    )
    # If these ever coincide, dropping the path filter becomes unobservable and
    # every assertion below is satisfied by a report that measures the wrong pair.
    discriminating = (
        unauth_overhead != library_overhead
        and unauth_overhead != -unauth_overhead  # a zero difference hides the sign too
        and len(record["targets"]) == 4
    )
    expected = f"{unauth_overhead:+.1f} ms"
    line = next((line.strip() for line in report.splitlines() if "overhead" in line), "")
    headline_ok = (
        MOD.UNAUTH_PATH in line
        and line.endswith(expected)
        and "n/a" not in line
        and f"{library_overhead:+.1f} ms" not in line
    )

    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "report.jsonl"
        cli_rc, streams, _, cli_error = _cli_run(_cli_argv(out))
        written, parse_error = _read_records(out)
    printed_ok = (
        cli_error is None
        and parse_error is None
        and cli_rc == 0
        and len(written or []) == 1
        and MOD.render_report(written[0]) in streams.out
    )

    ok = discriminating and headline_ok and printed_ok
    print(
        f"{'OK' if ok else 'FAIL'}: the report headline is the unauthenticated Traefik overhead "
        f"(expected={expected!r} (library A/B would be {library_overhead:+.1f} ms) line={line!r}, "
        f"fixture_discriminates={discriminating}, main_printed_the_written_record={printed_ok})"
    )
    return ok


def test_the_report_goes_to_stdout_and_the_diagnostics_to_stderr() -> bool:
    """AC: the numbers land on STDOUT; notes, warnings and failures land on STDERR.

    Which stream a line lands on is part of the published contract — the Step 1b
    runbook is about to tell the operator to redirect stdout into the baseline
    file — and until now nothing here could see it: `_cli_run` merged both
    streams into one buffer, so `print(render_report(record), file=sys.stderr)`
    left every check green while the operator's `> baseline.txt` captured
    nothing but a note about their token (mem-1785123232-2aff).

    Both directions are asserted, on a run that produces some of each: the
    report must be ON stdout and NOT on stderr, and the unreachable-target
    warning must be on stderr and NOT on stdout — a warning printed to stdout
    would land inside the transcript as if it were part of the measurement.
    """
    if not _guard("report on stdout"):
        return False
    direct_host = PROBE_DIRECT.split(":")[0]
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "streams.jsonl"
        rc, streams, _, error = _cli_run(_cli_argv(out), failing_hosts={direct_host})
        written, parse_error = _read_records(out)
    if error or parse_error or not written:
        print(
            f"FAIL: the report goes to stdout and the diagnostics to stderr "
            f"({error or parse_error or 'nothing was written'})"
        )
        return False

    report = MOD.render_report(written[-1])
    # A rendered report always carries its own header row; asserting a fragment
    # too as well as the whole thing means a harness that prints a TRUNCATED
    # report to stdout and the rest to stderr cannot satisfy this either.
    fragment = f"label={PROBE_LABEL}"
    report_on_stdout = report in streams.out and fragment in streams.out
    report_not_on_stderr = fragment not in streams.err and "endpoint" not in streams.err
    warning_on_stderr = "WARNING" in streams.err and "WARNING" not in streams.out
    # The note about the absent token is a diagnostic too, and it is emitted
    # before the measurement rather than after it.
    note_on_stderr = MOD.TOKEN_ENV in streams.err and MOD.TOKEN_ENV not in streams.out
    ok = (
        rc == 1
        and report_on_stdout
        and report_not_on_stderr
        and warning_on_stderr
        and note_on_stderr
    )
    print(
        f"{'OK' if ok else 'FAIL'}: the report goes to stdout and the diagnostics to stderr "
        f"(rc={rc!r}, report_on_stdout={report_on_stdout}, report_kept_off_stderr="
        f"{report_not_on_stderr}, warning_on_stderr_only={warning_on_stderr}, "
        f"token_note_on_stderr_only={note_on_stderr}, streams={streams!r})"
    )
    return ok


def test_an_answered_but_rejected_probe_is_not_a_measurement() -> bool:
    """AC: a non-2xx contributes NO latency, and the run does not exit 0.

    The live defect this closes: the authenticated targets were gated on the
    token being PRESENT, never on it WORKING, and `time_request` only failed on
    `OSError`/`HTTPException` — so a 401 was a flawless round trip and got filed
    as a library-load measurement. Against the real Plex with a bogus token:
    `traefik/library/sections succeeded=2/2 failed=0 errors=[] statuses=[401]
    ttfb_median=66.7`, `direct/library/sections ... ttfb_median=0.382`, record
    `authenticated: true`, exit 0. A rejection is not a library load, and 0.382
    ms differenced against a real post-change number proves whatever you like
    (mem-1785123219-03c9).

    It generalises well past auth, which is why the fix is at the status and not
    at the token: a Traefik 404 or a 502 error page is answered fast by Traefik
    for a backend it never reached, and files as an excellent baseline.

    So: a rejected sample takes the same road as a dead socket — no TTFB, no
    total, no bytes, its elapsed time kept only as the `failed_after_ms`
    diagnostic — while the STATUS is retained, because that is the operator's
    only signal that they measured an error page. Driven against a healthy
    second leg so the check cannot pass on a harness that reports nothing for
    everything.
    """
    if not _guard("non-2xx is not a measurement"):
        return False
    record, transport, error = _transport_run(status_by_host={PROBE_HOST: PROBE_REJECT_STATUS})
    if record is None:
        print(f"FAIL: an answered-but-rejected probe is not a measurement ({error})")
        return False
    rejected = next((t for t in record["targets"] if t["via"] == "traefik"), {})
    healthy = next((t for t in record["targets"] if t["via"] == "direct"), {})
    rejected_ok = (
        rejected.get("succeeded") == 0
        and rejected.get("failed") == len(FAKE_TTFB)
        # Kept, not swallowed: the report's status column is what tells the
        # operator which of the two failures they are looking at.
        and rejected.get("statuses") == [PROBE_REJECT_STATUS]
        and bool(rejected.get("errors"))
        and all(str(PROBE_REJECT_STATUS) in e for e in rejected.get("errors", []))
        and all(
            (rejected.get(series) or {}).get("count") == 0
            for series in ("ttfb", "total", "bytes")
        )
        and (rejected.get("ttfb") or {}).get("median_ms") is None
        and (rejected.get("total") or {}).get("median_ms") is None
        # The round trip DID take time; it is a diagnostic, never a latency.
        and _elapsed_diagnostics(rejected, len(FAKE_TTFB))
    )
    contrast_ok = (
        healthy.get("succeeded") == len(FAKE_TTFB)
        and (healthy.get("ttfb") or {}).get("median_ms") is not None
        and not healthy.get("errors")
    )

    # ...and through the ENTRY POINT, where the exit code is what an operator
    # reading a one-shot capture actually sees. Every leg is rejected here, with
    # a token in play, which is exactly the stale-token case.
    direct_host = PROBE_DIRECT.split(":")[0]
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "rejected.jsonl"
        rc, streams, _, cli_error = _cli_run(
            _cli_argv(out),
            token=PROBE_TOKEN,
            status_by_host={PROBE_HOST: PROBE_REJECT_STATUS, direct_host: PROBE_REJECT_STATUS},
        )
        written, parse_error = _read_records(out)
    on_disk = (written or [{}])[-1]
    cli_ok = (
        cli_error is None
        and parse_error is None
        # NOT 0. The record is still written first, so nothing is lost — that is
        # exactly what 1 means.
        and rc == 1
        and len(written or []) == 1
        and bool(on_disk.get("targets"))
        and all(t.get("succeeded") == 0 for t in on_disk.get("targets", []))
        and all(t.get("statuses") == [PROBE_REJECT_STATUS] for t in on_disk.get("targets", []))
        # The operator is pointed at the actual cause rather than left to read a
        # suspiciously fast library number.
        and MOD.TOKEN_ENV in streams.err
        and str(PROBE_REJECT_STATUS) in streams.err
    )
    ok = bool(transport.opened) and rejected_ok and contrast_ok and cli_ok
    print(
        f"{'OK' if ok else 'FAIL'}: an answered-but-rejected probe is not a measurement "
        f"(rejected leg {rejected.get('succeeded')}/{rejected.get('requested')} "
        f"statuses={rejected.get('statuses')} ttfb_median="
        f"{(rejected.get('ttfb') or {}).get('median_ms')!r} errors={rejected.get('errors')}, "
        f"healthy leg measured={contrast_ok}, cli rc={rc!r} (expected 1, NOT 0) "
        f"blamed_the_token={MOD.TOKEN_ENV in streams.err}, cli_error={cli_error or parse_error})"
    )
    return ok


def test_every_request_on_the_wire_is_a_read_only_get() -> bool:
    """AC: "Non-destructive by construction: read-only GETs ... never mutate Plex state".

    The task description names this as a construction requirement, and it was the
    one property in this whole file that NOTHING observed: `conn.request("GET",
    ...)` -> `"POST"` and -> `"DELETE"` both left the shape test green, and
    DELETE survived the full `just test` gate at 34/34 exit 0. It is the only
    irreversible thing this script could ever do, to a live household Plex the
    operator is about to point it at from a hotspot with one shot at the capture.

    It was not merely unasserted, it was UNASSERTABLE: the transport fake's
    `request()` accepted `method` and discarded it, so the value could not be
    named by any check here. A fake's discarded parameters are properties no
    assertion can reach, and the hole is invisible from the assertion side
    because the assertion cannot be written at all (mem-1785124642-053b). Body is
    read for the same reason — a mutation to a writing verb usually brings one,
    and the stub now mirrors `http.client`'s positional signature so it lands
    where this check can see it.

    Driven under every outcome class the fixture can build, because the verb is
    chosen once per call site and a fixture that only ever succeeds exercises one
    of them: a healthy pair, a leg that answers non-2xx, a leg whose socket dies
    before the response, and the AUTHENTICATED probe set through `main()` — the
    library endpoints are the ones whose real-world counterparts have destructive
    siblings (`/library/sections/N/refresh`).
    """
    if not _guard("read-only GETs"):
        return False
    direct_host = PROBE_DIRECT.split(":")[0]
    _, healthy, healthy_error = _transport_run()
    _, rejected, rejected_error = _transport_run(
        status_by_host={PROBE_HOST: PROBE_REJECT_STATUS}
    )
    _, dead, dead_error = _transport_run(failing_hosts={direct_host})
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "read-only.jsonl"
        _, _, cli, cli_error = _cli_run(_cli_argv(out), token=PROBE_TOKEN)

    transports = {
        "healthy": healthy,
        f"answered {PROBE_REJECT_STATUS}": rejected,
        "dead socket": dead,
        "cli + token": cli,
    }
    errors = [e for e in (healthy_error, rejected_error, dead_error, cli_error) if e]
    methods = {name: sorted({r["method"] for r in t.requests}) for name, t in transports.items()}
    bodies = {name: sorted({repr(r["body"]) for r in t.requests}) for name, t in transports.items()}
    counts = {name: len(t.requests) for name, t in transports.items()}
    ok = (
        not errors
        # Every class really put something on the wire, and there really are four
        # of them. Without both, this passes on a fixture that observed nothing —
        # which is the shape of the very defect it exists to close, and `all()`
        # over an empty sequence is True.
        and len(transports) == 4
        and all(counts.values())
        and all(verbs == ["GET"] for verbs in methods.values())
        and all(sent == [repr(None)] for sent in bodies.values())
    )
    print(
        f"{'OK' if ok else 'FAIL'}: every request on the wire is a read-only GET with no body "
        f"(methods={methods}, bodies={bodies}, requests={counts}, errors={errors})"
    )
    return ok


def test_the_success_band_is_exactly_2xx() -> bool:
    """AC: a measurement is a 2xx — pinned just outside AND just inside both edges.

    Last round closed "a non-2xx is not a measurement", and guarded it with one
    status: 401. A range predicate sampled at one interior point is guarded on
    ONE SIDE ONLY. `200 <= s < 300` -> `< 400` stayed green, and so did
    `100 <= s < 300`, because every widening that still excludes 401 is
    invisible; only `< 500` reddened, and only because it happened to swallow the
    one status the fixture could build (mem-1785124653-a61d).

    The untested side is the REACHABLE one, verified live against this
    deployment: `--direct plex.yoonnation.com:80` answers **301** from the repo's
    own Traefik, 3/3 samples. Correct code files that as 0/3, `n/a` medians,
    `! HTTP 301 Moved Permanently` and rc=1. Under the surviving mutation the
    same command filed the redirect as a 2.4 ms measurement of `/identity`,
    printed `Traefik overhead on /identity (median TTFB): +6.3 ms` — a real 200
    differenced against a redirect — and exited 0. It is also the shape a
    mobile-hotspot capture meets: a captive portal answers 302, and Step 1c is
    taken from a hotspot, once.

    So both directions are driven. Statuses just outside each edge (1xx below,
    3xx above) plus the 4xx/5xx error pages Traefik actually serves must record
    NO latency; statuses just inside each edge (200, 201, 204, 299) must record
    one, without which a NARROWED band would be exactly as invisible as a widened
    one. Each row runs against a second leg that answered 200, so no row can pass
    on a harness that reports nothing for everything, and the 301 case is taken
    all the way through `main()` to the exit code and the report the operator
    reads.
    """
    if not _guard("2xx success band"):
        return False
    # The fixture's own discriminating power, asserted BEFORE anything is driven
    # so a later edit cannot quietly turn either half of this check vacuous:
    # `not outside` and `not inside` are both True over an EMPTY status tuple,
    # and an emptied tuple reads exactly like a passing check. Each side must
    # still straddle the edge it was written for.
    redirect = 301  # what Traefik really answers on :80; the live case
    straddles = (
        any(s < 200 for s in NON_MEASUREMENT_STATUSES)
        and redirect in NON_MEASUREMENT_STATUSES
        and 200 in MEASUREMENT_STATUSES
        and any(200 < s < 300 for s in MEASUREMENT_STATUSES)
    )
    if not straddles:
        print(
            "FAIL: the success band is exactly 2xx (the fixture no longer straddles both edges: "
            f"outside={NON_MEASUREMENT_STATUSES}, inside={MEASUREMENT_STATUSES})"
        )
        return False

    def _legs(status):
        record, _, error = _transport_run(status_by_host={PROBE_HOST: status})
        targets = (record or {}).get("targets", [])
        return (
            next((t for t in targets if t["via"] == "traefik"), {}),
            next((t for t in targets if t["via"] == "direct"), {}),
            error,
        )

    outside = []
    for status in NON_MEASUREMENT_STATUSES + (PROBE_REJECT_STATUS,):
        leg, contrast, error = _legs(status)
        good = (
            error is None
            and leg.get("succeeded") == 0
            and leg.get("failed") == len(FAKE_TTFB)
            # Kept, never swallowed: the status column is the operator's only
            # signal that what they measured was an error page.
            and leg.get("statuses") == [status]
            # `or ["-"]` so an EMPTY error list fails this rather than passing it
            # vacuously through `all()` over nothing.
            and all(str(status) in e for e in leg.get("errors") or ["-"])
            and all((leg.get(s) or {}).get("count") == 0 for s in ("ttfb", "total", "bytes"))
            and (leg.get("ttfb") or {}).get("median_ms") is None
            and (leg.get("total") or {}).get("median_ms") is None
            # The round trip did take time; it is a diagnostic, never a latency.
            and _elapsed_diagnostics(leg, len(FAKE_TTFB))
            and contrast.get("succeeded") == len(FAKE_TTFB)
        )
        if not good:
            outside.append(
                (status, leg.get("succeeded"), leg.get("statuses"),
                 (leg.get("ttfb") or {}).get("median_ms"), error)
            )

    inside = []
    for status in MEASUREMENT_STATUSES:
        leg, contrast, error = _legs(status)
        good = (
            error is None
            and leg.get("succeeded") == len(FAKE_TTFB)
            and leg.get("failed") == 0
            and leg.get("statuses") == [status]
            and not leg.get("errors")
            and leg.get("failed_after_ms") == []
            and (leg.get("ttfb") or {}).get("median_ms") is not None
            and (leg.get("total") or {}).get("median_ms") is not None
            and (leg.get("bytes") or {}).get("count") == len(FAKE_TTFB)
            and contrast.get("succeeded") == len(FAKE_TTFB)
        )
        if not good:
            inside.append(
                (status, leg.get("succeeded"), leg.get("statuses"),
                 (leg.get("ttfb") or {}).get("median_ms"), error)
            )

    # The live 3xx, end to end: the exit code the operator sees and the headline
    # they transcribe. A redirect differenced against a real 200 is the specific
    # falsehood this guards, so the headline must refuse to print a number.
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "redirect.jsonl"
        rc, streams, _, cli_error = _cli_run(
            _cli_argv(out), status_by_host={PROBE_HOST: redirect}
        )
        written, parse_error = _read_records(out)
    headline = next((l for l in streams.out.splitlines() if "overhead" in l), "")
    _, rows = _report_table(streams.out)
    redirect_row = next((row for name, row in rows.items() if name.startswith("traefik")), {})
    status_header = _header_for(list(redirect_row), "status")
    cli_ok = (
        cli_error is None
        and parse_error is None
        and rc == 1
        and len(written or []) == 1
        and "n/a" in headline
        and "+" not in headline
        and status_header is not None
        and redirect_row.get(status_header) == str(redirect)
    )

    ok = not outside and not inside and cli_ok
    print(
        f"{'OK' if ok else 'FAIL'}: the success band is exactly 2xx "
        f"(rejected {len(NON_MEASUREMENT_STATUSES) + 1 - len(outside)}/"
        f"{len(NON_MEASUREMENT_STATUSES) + 1} of {NON_MEASUREMENT_STATUSES + (PROBE_REJECT_STATUS,)}, "
        f"measured {len(MEASUREMENT_STATUSES) - len(inside)}/{len(MEASUREMENT_STATUSES)} of "
        f"{MEASUREMENT_STATUSES}, straddles_both_edges={straddles}, "
        f"wrong_outside={outside}, wrong_inside={inside}, "
        f"live-{redirect} cli rc={rc!r} (expected 1) headline={headline.strip()!r} "
        f"status_cell={redirect_row.get(status_header)!r}, cli_error={cli_error or parse_error})"
    )
    return ok


def test_cli_wires_the_token_and_the_timeout() -> bool:
    """AC: the last two inputs — $PLEX_TOKEN and `--timeout` — reach the request.

    The argv/env wires for `--host`, `--repeats`, `--out`, `--no-log`,
    `--skip-direct`, `--label` and `--vantage` are pinned elsewhere; an
    enumerated list of wires with two members missing is how the last two
    rejections started. These two are the ones left:

    * the token is what makes the AUTHENTICATED library endpoints appear at all,
      and the slow initial LIBRARY load is the plan's actual complaint — a
      baseline captured with the variable silently unread measures `/identity`
      and nothing else, and looks identical on disk to one where the operator
      never exported it;
    * `--timeout` goes two places (the connection, and the record's own
      `timeout_s`), and the record's copy is how Step 4 knows a "slow" number is
      not just a clipped one.

    Judged from the transport and from the file on disk, never from the report:
    the header actually sent is the only observation that distinguishes "the
    token was read" from "a flag was echoed into a record".
    """
    if not _guard("cli token and timeout wires"):
        return False
    with tempfile.TemporaryDirectory() as tmp:
        authed_out = pathlib.Path(tmp) / "authed.jsonl"
        authed_rc, _, authed_transport, authed_err = _cli_run(
            _cli_argv(authed_out), token=PROBE_TOKEN
        )
        authed_records, authed_parse_err = _read_records(authed_out)
        on_disk_text = authed_out.read_text(encoding="utf-8") if authed_out.exists() else ""

        anon_out = pathlib.Path(tmp) / "anon.jsonl"
        anon_rc, _, _, anon_err = _cli_run(_cli_argv(anon_out))
        anon_records, anon_parse_err = _read_records(anon_out)

    errors = [e for e in (authed_err, authed_parse_err, anon_err, anon_parse_err) if e]
    if errors or not authed_records or not anon_records:
        print(
            f"FAIL: the CLI wires $PLEX_TOKEN and --timeout "
            f"(errors={errors}, authed_records={len(authed_records or [])}, "
            f"anon_records={len(anon_records or [])})"
        )
        return False

    authed, anon = authed_records[-1], anon_records[-1]
    authed_paths = sorted({t.get("path") for t in authed.get("targets", [])})
    anon_paths = sorted({t.get("path") for t in anon.get("targets", [])})
    # The env var must CHANGE the probe set, not merely a boolean in the record.
    token_selected_targets = (
        authed.get("authenticated") is True
        and anon.get("authenticated") is False
        and set(authed_paths) > set(anon_paths)
        and anon_paths == [MOD.UNAUTH_PATH]
    )
    # ...and must reach the wire, on the authenticated requests only. The header
    # name is asserted as a literal: it is Plex's, not ours to rename.
    auth_headers = [
        r["headers"] for r in authed_transport.requests if r["path"] != MOD.UNAUTH_PATH
    ]
    unauth_headers = [
        r["headers"] for r in authed_transport.requests if r["path"] == MOD.UNAUTH_PATH
    ]
    token_sent = bool(auth_headers) and all(
        headers.get("X-Plex-Token") == PROBE_TOKEN for headers in auth_headers
    )
    token_withheld = all("X-Plex-Token" not in headers for headers in unauth_headers)
    token_not_persisted = PROBE_TOKEN not in on_disk_text

    # --timeout reaches BOTH destinations: every connection opened, and the
    # record's own copy of the setting.
    timeouts = sorted({timeout for _, _, timeout in authed_transport.opened})
    timeout_ok = (
        timeouts == [PROBE_TIMEOUT]
        and authed.get("timeout_s") == PROBE_TIMEOUT
        and PROBE_TIMEOUT != MOD.DEFAULT_TIMEOUT
    )

    ok = (
        authed_rc == 0
        and anon_rc == 0
        and token_selected_targets
        and token_sent
        and token_withheld
        and token_not_persisted
        and timeout_ok
    )
    print(
        f"{'OK' if ok else 'FAIL'}: the CLI wires $PLEX_TOKEN and --timeout "
        f"(authed_paths={authed_paths}, anon_paths={anon_paths}, "
        f"token_sent_on_auth_probes={token_sent}, token_withheld_on_anon_probes={token_withheld}, "
        f"token_in_file={not token_not_persisted}, connect_timeouts={timeouts}, "
        f"record_timeout_s={authed.get('timeout_s')!r})"
    )
    return ok


def test_a_lost_record_is_not_reported_as_a_lost_measurement() -> bool:
    """AC: a failed WRITE gets its own exit code and a legible message, not a traceback.

    `1` is the code the module docstring reserves for "a target returned no
    successful sample — the record is still written first, so nothing is lost".
    When the write itself fails, nothing is wrong with the measurement and the
    record is exactly what was lost: the same fact stated by the same number
    means the opposite thing. The runbook 1b is about to publish transcribes
    that contract for a capture taken once, on a mobile hotspot, that cannot be
    retaken — so this needs its own code (`3`) and a message naming the path,
    and the report must remain on stdout as the only surviving copy.

    Reproduced without privileges by pointing `--out` at a path whose parent is
    a regular file, so `mkdir` raises `NotADirectoryError`; the live cases the
    Critic executed (`/plex-latency.jsonl` -> `PermissionError`,
    `/proc/nope/x.jsonl` -> `FileNotFoundError`) are the same `OSError` branch.

    Also here, because it is the same class of "not a measurement failure":
    `--timeout -1` used to die mid-measurement with an uncaught `ValueError`
    from the socket layer (exit 1 plus a traceback) where `--repeats 0` is
    politely refused with 2. Bad arguments are refused BEFORE anything is
    probed — asserted against the transport, not against the exit code alone.
    """
    if not _guard("lost record exit code"):
        return False
    with tempfile.TemporaryDirectory() as tmp:
        blocker = pathlib.Path(tmp) / "not-a-directory"
        blocker.write_text("a regular file, so it cannot be anything's parent\n", encoding="utf-8")
        unwritable = blocker / "plex-latency.jsonl"
        rc, streams, transport, error = _cli_run(_cli_argv(unwritable))
        wrote_nothing = not unwritable.exists()

        bad_timeout = pathlib.Path(tmp) / "bad-timeout.jsonl"
        timeout_rc, _, timeout_transport, timeout_error = _cli_run(
            _cli_argv(bad_timeout, timeout=-1.0)
        )
        timeout_wrote = bad_timeout.exists()

    # `error` is set when an exception escaped main() — the raw-traceback
    # behaviour itself, reported as a FAIL rather than aborting the file.
    write_ok = (
        error is None
        and rc == 3
        and wrote_nothing
        # The failure is a diagnostic and belongs on stderr, next to the other
        # diagnostics...
        and str(unwritable) in streams.err
        # ...while the measurement happened and its numbers are still on STDOUT:
        # that report is now the only copy, so losing it too would be the real
        # cost, and a report emitted on the same stream as the failure is a
        # report the operator's redirect did not capture.
        and f"label={PROBE_LABEL}" in streams.out
        and bool(transport.opened)
    )
    timeout_ok = (
        timeout_error is None
        and timeout_rc == 2
        and not timeout_wrote
        # Refused before a single connection was opened, like `--repeats 0`.
        and not timeout_transport.opened
    )
    ok = write_ok and timeout_ok
    print(
        f"{'OK' if ok else 'FAIL'}: a failed write is not reported as a failed measurement "
        f"(write rc={rc!r} (expected 3, NOT 1) escaped={error!r} named_the_path="
        f"{str(unwritable) in streams.err} "
        f"report_survived_on_stdout={f'label={PROBE_LABEL}' in streams.out} "
        f"wrote_nothing={wrote_nothing}, "
        f"bad_timeout rc={timeout_rc!r} (expected 2) escaped={timeout_error!r} "
        f"probed_anyway={bool(timeout_transport.opened)})"
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
    with _env(MOD.TOKEN_ENV, PROBE_TOKEN):
        record, probe, error = _fake_run(token=PROBE_TOKEN)
        report = "" if record is None else MOD.render_report(record)
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
    test_an_answered_but_rejected_probe_is_not_a_measurement,
    test_the_success_band_is_exactly_2xx,
    test_every_request_on_the_wire_is_a_read_only_get,
    test_ttfb_and_total_summarise_the_same_samples,
    test_partial_failure_does_not_inflate_the_sample_count,
    test_label_and_vantage_are_mandatory,
    test_direct_leg_is_skippable_and_the_record_says_so,
    test_cli_appends_the_record_and_honours_its_exit_contract,
    test_report_states_what_the_record_states,
    test_report_headline_is_the_unauthenticated_traefik_overhead,
    test_the_report_goes_to_stdout_and_the_diagnostics_to_stderr,
    test_cli_wires_the_token_and_the_timeout,
    test_a_lost_record_is_not_reported_as_a_lost_measurement,
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
