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
  6. the harness is import-safe and offline-safe — `scripts/run_gate.py` runs
     this file with NO network, so the test must never perform a real request,
  7. neither the JSONL record nor the stdout report echoes the token.

Behaviour is exercised, not grepped: the record-building and statistics paths
run end to end against an INJECTED fake prober with scripted timings, under a
socket guard that raises on any real connect. Sentinel inputs are values that
appear nowhere else in the repo (mem-1784140865-9b40) so a check cannot pass by
coincidence with a default, and each check is registered in `TESTS` — a
`test_*` function missing from that tuple is green-by-omission
(mem-1784137124-c346).

Follows the repo's dual-mode shape-test convention (see
`test_plex_ramdisk_bind_mount_shape.py`): module-level `test_<name>() -> bool`
printing `OK` / `FAIL: ...` (no `assert`), plus `main() -> int` summing them.
Stdlib only.
"""

import contextlib
import datetime
import importlib.util
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
