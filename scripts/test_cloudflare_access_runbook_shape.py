"""Shape test for Step 5 — Cloudflare Access-before-ingress runbook.

Per the traefik-cloudflare-letsencrypt design §4 (manual Cloudflare front door)
and the canonical plan Step 5 — verifies the manual, operator-run procedure at
`docs/runbooks/cloudflare-access.md` documents the **load-bearing ordering** and
the identity/ingress details an operator needs to gate the dashboards behind
Cloudflare Access before any tunnel ingress is published:

  * **ordering is load-bearing** — create the Access application + policy
    **before** publishing the tunnel ingress (else a dashboard is momentarily
    reachable unauthenticated),
  * **one self-hosted Access application per dashboard hostname** (NOT a
    `*.yoonnation.com` wildcard — fragile w.r.t. Plex),
  * identity gating — Google IdP (+ one-time-PIN fallback), **MFA**, policy
    allows **only** `emmanuelx08@gmail.com` with an implicit deny,
  * per-host tunnel ingress → `https://traefik:443` with
    `originRequest.originServerName` = the hostname and `noTLSVerify: true`
    **only during staging** (removed at the Step-7 prod flip),
  * **Plex is excluded** — it stays public via the port-forward, never through
    the Cloudflare tunnel/Access (media ToS).

Step 5 is primarily manual Cloudflare configuration and is explicitly outside
the automation "done" scope; this test only gates that the runbook is present,
non-empty, and carries the required operational anchors.

Follows the repo's dual-mode shape-test convention (see
`test_runbook_shape.py`, `test_traefik_config_shape.py`): module-level
`test_<name>() -> bool` functions that print `OK` / `FAIL: ...` (no `assert`),
plus `main() -> int` that sums the booleans and `sys.exit`s non-zero on any
failure. Stdlib only. Regexes anchor on the inner content (mem-1781892715-142d).
The real gate is the standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "cloudflare-access.md"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def test_runbook_exists_and_nonempty() -> bool:
    body = _read(RUNBOOK)
    ok = len(body.strip()) > 0
    print(
        f"{'OK' if ok else 'FAIL'}: docs/runbooks/cloudflare-access.md exists "
        f"and is non-empty (chars={len(body)})"
    )
    return ok


def test_ordering_access_before_ingress() -> bool:
    body = _read(RUNBOOK)
    checks = {
        # The load-bearing rule stated as prose: Access must exist BEFORE the
        # ingress is published. Anchored so a stray "before" elsewhere can't
        # satisfy it — the same sentence must mention publishing/ingress.
        "access-before-ingress": re.search(
            r'before\b[^\n]*\b(?:publish\w*|ingress)\b', body, re.IGNORECASE
        )
        is not None,
        # An explicit FIRST … THEN sequencing of the two operator actions.
        "FIRST marker": re.search(r'\bFIRST\b', body) is not None,
        "THEN marker": re.search(r'\bTHEN\b', body) is not None,
        # The rationale: an un-gated ingress momentarily exposes a dashboard.
        "unauthenticated-exposure rationale": re.search(
            r'unauthenticated', body, re.IGNORECASE
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook states the load-bearing "
        f"Access-before-ingress ordering (missing={missing})"
    )
    return ok


def test_per_host_self_hosted_not_wildcard() -> bool:
    body = _read(RUNBOOK)
    checks = {
        # Self-hosted application type.
        "self-hosted app": re.search(
            r'self[- ]hosted', body, re.IGNORECASE
        )
        is not None,
        # One application PER dashboard hostname (per-host, not one shared app).
        "per hostname": re.search(
            r'per\b[^\n]*\bhost(?:name)?\b', body, re.IGNORECASE
        )
        is not None,
        # Explicit warning against a wildcard Access app.
        "not a wildcard": re.search(
            r'\bnot\b[^\n]*\*\.\{?\s*domain', body, re.IGNORECASE
        )
        is not None
        or re.search(
            r'\bnot\b[^\n]*\*\.yoonnation\.com', body, re.IGNORECASE
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook requires per-host self-hosted apps "
        f"(not a wildcard) (missing={missing})"
    )
    return ok


def test_identity_policy() -> bool:
    body = _read(RUNBOOK)
    checks = {
        # Google identity provider.
        "google idp": re.search(r'google', body, re.IGNORECASE) is not None,
        # One-time-PIN fallback IdP.
        "one-time-pin fallback": re.search(
            r'one[- ]time[- ]pin|\bOTP\b', body, re.IGNORECASE
        )
        is not None,
        # Multi-factor enforced.
        "mfa": re.search(r'\bMFA\b|multi[- ]factor', body, re.IGNORECASE)
        is not None,
        # Allow ONLY the single operator identity.
        "single allow": re.search(r'emmanuelx08@gmail\.com', body) is not None,
        # Implicit deny for everyone else.
        "implicit deny": re.search(r'implicit\s+deny|\bdeny\b', body, re.IGNORECASE)
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook pins the identity policy "
        f"(Google IdP + MFA + single allow + deny) (missing={missing})"
    )
    return ok


def test_ingress_target_staging_only_notlsverify() -> bool:
    body = _read(RUNBOOK)
    checks = {
        # Ingress points at the Traefik origin over HTTPS on 443.
        "https://traefik:443": re.search(
            r'https://traefik:443', body
        )
        is not None,
        # SNI carried so the LE wildcard is presented for the right host.
        "originServerName": re.search(
            r'origin(?:Request\.)?originServerName|originServerName', body
        )
        is not None,
        # noTLSVerify is staging-only and removed at the prod flip (Step 7).
        "noTLSVerify staging-only": re.search(
            r'noTLSVerify', body
        )
        is not None
        and re.search(r'stag', body, re.IGNORECASE) is not None,
        "removed at prod flip": re.search(
            r'Step\s*7|prod(?:uction)?\s+flip|remove\w*[^\n]*noTLSVerify'
            r'|noTLSVerify[^\n]*remov', body, re.IGNORECASE
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook specifies the per-host ingress "
        f"target + staging-only noTLSVerify (missing={missing})"
    )
    return ok


def test_plex_excluded_from_tunnel() -> bool:
    body = _read(RUNBOOK)
    # Collapse whitespace so the assertion is robust to markdown line-wrapping
    # (the exclusion sentence spans wrapped lines); bounded gaps keep it from
    # matching an unrelated "plex" and "tunnel" far apart in the document.
    flat = " ".join(body.split())
    mentions_plex = re.search(r'\bplex\b', flat, re.IGNORECASE) is not None
    excluded = (
        # "... plex ... not ... tunnel/Access/proxy ..." within one sentence.
        re.search(
            r'\bplex\b.{0,160}?\bnot\b.{0,80}?(?:tunnel|access|proxy)',
            flat,
            re.IGNORECASE,
        )
        is not None
        # or Plex tied to its own public port-forward / grey DNS path.
        or re.search(
            r'\bplex\b.{0,160}?(?:port[- ]forward|grey|dns[- ]only)',
            flat,
            re.IGNORECASE,
        )
        is not None
    )
    ok = mentions_plex and excluded
    print(
        f"{'OK' if ok else 'FAIL'}: runbook excludes Plex from the tunnel/Access "
        f"(mentions={mentions_plex}, excluded={excluded})"
    )
    return ok


TESTS = (
    test_runbook_exists_and_nonempty,
    test_ordering_access_before_ingress,
    test_per_host_self_hosted_not_wildcard,
    test_identity_policy,
    test_ingress_target_staging_only_notlsverify,
    test_plex_excluded_from_tunnel,
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
