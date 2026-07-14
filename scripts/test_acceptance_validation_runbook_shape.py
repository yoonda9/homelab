"""Shape test for Step 8 — acceptance-validation runbook (Traefik+Cloudflare+LE).

Per the traefik-cloudflare-letsencrypt design §7 (Testing Strategy) and the
canonical plan Step 8 — verifies `docs/runbooks/acceptance-validation.md` is
extended past the original Step-12 rebuild-from-code checklist with the design's
full E2E acceptance strategy for the tunnel + Access + dual-path stack:

  * the load-bearing security gate — a **WAN direct** `https://<home-IP>:443`
    hit carrying a **dashboard `Host` header** must return **403** (the Plex
    port-forward opens `:443` for every Host; `internal-allowlist` is the gate),
  * the **direct dual-path** over **IPv4 and IPv6** → `192.168.1.111` for tailnet
    devices,
  * Cloudflare **Access allow/deny by identity** through the tunnel,
  * the production flip landed — **browser-trusted LE prod** cert with **no
    leftover staging cert** and **no `noTLSVerify`** remaining on any ingress,
  * the objective's terminal condition — a full pass prints **`LOOP_COMPLETE`**.

Plus a docs-wide regression guard that the removed `le-http` / `api.insecure`
config names do not linger anywhere under `docs/runbooks/`.

The acceptance run itself (live `pve` + DAS + WAN) is manual, human-confirmed and
outside the automation "done" scope; this test only gates that the runbook
documents the required checks. It complements
`test_mise_config_shape.py::test_acceptance_runbook_documents_reproducibility`,
which still guards the rebuild-from-code cycle in the same file.

Follows the repo's dual-mode shape-test convention (see
`test_tailscale_split_dns_runbook_shape.py`,
`test_cloudflare_access_runbook_shape.py`): module-level `test_<name>() -> bool`
functions that print `OK` / `FAIL: ...` (no `assert`), plus `main() -> int` that
sums the booleans and `sys.exit`s non-zero on any failure. Stdlib only. Regexes
anchor on the inner content (mem-1781892715-142d). The real gate is the
standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOKS = REPO_ROOT / "docs" / "runbooks"
RUNBOOK = RUNBOOKS / "acceptance-validation.md"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _flat(body: str) -> str:
    # Collapse whitespace so assertions are robust to markdown line-wrapping.
    return " ".join(body.split())


def test_runbook_exists_and_nonempty() -> bool:
    body = _read(RUNBOOK)
    ok = len(body.strip()) > 0
    print(
        f"{'OK' if ok else 'FAIL'}: docs/runbooks/acceptance-validation.md exists "
        f"and is non-empty (chars={len(body)})"
    )
    return ok


def test_wan_direct_443_returns_403() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    checks = {
        # The direct WAN hit is on :443 to the home IP (not the tunnel CNAME).
        "wan direct :443": re.search(
            r'\bWAN\b.{0,200}?:443|:443.{0,200}?\bWAN\b', flat, re.IGNORECASE
        )
        is not None,
        # It carries a dashboard Host header (spoofed Host to a dashboard name).
        "dashboard Host header": re.search(
            r'\bHost\b.{0,80}?(?:grafana|dashboard|yoonnation)', flat, re.IGNORECASE
        )
        is not None,
        # And the load-bearing expectation is a 403.
        "expects 403": re.search(
            r':443.{0,240}?\b403\b|\b403\b.{0,240}?:443'
            r'|\bHost\b.{0,240}?\b403\b',
            flat,
            re.IGNORECASE,
        )
        is not None,
        # internal-allowlist is named as the load-bearing gate.
        "internal-allowlist gate": re.search(r'internal-allowlist', flat)
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook gates WAN direct :443 + dashboard "
        f"Host -> 403 (missing={missing})"
    )
    return ok


def test_direct_dual_path_v4_v6() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    checks = {
        "origin 192.168.1.111": re.search(r'192\.168\.1\.111', flat) is not None,
        "ipv4": re.search(r'\bIPv4\b|\bv4\b', flat) is not None,
        "ipv6": re.search(r'\bIPv6\b|\bv6\b', flat) is not None,
        # Framed as the direct (tailnet/LAN) path, not the tunnel.
        "direct path": re.search(
            r'\bdirect\b.{0,120}?(?:tailnet|LAN|192\.168\.1\.111)'
            r'|(?:tailnet|LAN).{0,120}?\bdirect\b',
            flat,
            re.IGNORECASE,
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook covers the direct dual-path over "
        f"v4+v6 -> 192.168.1.111 (missing={missing})"
    )
    return ok


def test_access_allow_deny_by_identity() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    mentions_access = re.search(r'\bAccess\b', flat) is not None
    # Both sides of the identity gate: an allowed identity loads, a different
    # one is denied.
    allow = re.search(r'\ballow', flat, re.IGNORECASE) is not None or re.search(
        r'sign\s*in|logs?\s*in|loads', flat, re.IGNORECASE
    ) is not None
    deny = re.search(r'\bden(?:y|ied)\b', flat, re.IGNORECASE) is not None
    identity = re.search(
        r'identity|SSO|MFA|emmanuelx08@gmail\.com|different\b[^.]{0,40}?(?:account|identity|Google)',
        flat,
        re.IGNORECASE,
    ) is not None
    ok = mentions_access and allow and deny and identity
    print(
        f"{'OK' if ok else 'FAIL'}: runbook checks Access allow/deny by identity "
        f"(access={mentions_access}, allow={allow}, deny={deny}, identity={identity})"
    )
    return ok


def test_prod_cert_no_leftover_staging() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    # Browser-trusted prod cert...
    prod_trusted = re.search(
        r'browser[- ]?trusted|prod(?:uction)?\b[^.]{0,40}?(?:cert|LE|Let)',
        flat,
        re.IGNORECASE,
    ) is not None
    # ...and explicitly no leftover staging cert.
    no_staging = re.search(
        r'no\b[^.]{0,60}?staging|staging\b[^.]{0,40}?(?:gone|removed|no longer)',
        flat,
        re.IGNORECASE,
    ) is not None
    ok = prod_trusted and no_staging
    print(
        f"{'OK' if ok else 'FAIL'}: runbook confirms prod cert + no leftover "
        f"staging cert (prod_trusted={prod_trusted}, no_staging={no_staging})"
    )
    return ok


def test_no_tlsverify_remains() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    # The check must state that no noTLSVerify is left on any ingress.
    ok = re.search(
        r'no\b[^.]{0,40}?noTLSVerify|noTLSVerify\b[^.]{0,60}?'
        r'(?:remov|gone|no longer|none|no ingress)',
        flat,
        re.IGNORECASE,
    ) is not None
    print(
        f"{'OK' if ok else 'FAIL'}: runbook checks no noTLSVerify remains on any "
        f"ingress"
    )
    return ok


def test_loop_complete_terminal() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    # The objective's terminal condition: a full acceptance pass prints
    # LOOP_COMPLETE.
    ok = "LOOP_COMPLETE" in body and re.search(
        r'LOOP_COMPLETE\b[^.]{0,80}?(?:pass|complete|sign)'
        r'|(?:all\b[^.]{0,40}?pass|full\b[^.]{0,40}?pass|complete|sign[- ]?off)'
        r'[^.]{0,80}?LOOP_COMPLETE',
        flat,
    ) is not None
    print(
        f"{'OK' if ok else 'FAIL'}: runbook documents printing LOOP_COMPLETE on a "
        f"full acceptance pass"
    )
    return ok


def test_docs_purged_of_stale_refs() -> bool:
    # Regression guard: the removed config names must not linger in any runbook.
    stale = re.compile(r'le-http|api\.insecure')
    offenders = {}
    for md in sorted(RUNBOOKS.glob("*.md")):
        hits = [
            i + 1
            for i, line in enumerate(md.read_text().splitlines())
            if stale.search(line)
        ]
        if hits:
            offenders[md.name] = hits
    ok = not offenders
    print(
        f"{'OK' if ok else 'FAIL'}: no le-http/api.insecure references remain in "
        f"docs/runbooks (offenders={offenders})"
    )
    return ok


TESTS = (
    test_runbook_exists_and_nonempty,
    test_wan_direct_443_returns_403,
    test_direct_dual_path_v4_v6,
    test_access_allow_deny_by_identity,
    test_prod_cert_no_leftover_staging,
    test_no_tlsverify_remains,
    test_loop_complete_terminal,
    test_docs_purged_of_stale_refs,
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
