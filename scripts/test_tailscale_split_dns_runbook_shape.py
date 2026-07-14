"""Shape test for Step 6 — Tailscale split-DNS direct dual-path runbook.

Per the traefik-cloudflare-letsencrypt design §"Split-horizon (R5)" / R12 and the
canonical plan Step 6 — verifies the manual, operator-run procedure at
`docs/runbooks/tailscale-split-dns.md` documents the split-DNS override that
gives tailnet devices a **direct** origin path while off-tailnet clients keep
going through the Cloudflare tunnel + Access:

  * a Tailscale **split-DNS** (restricted nameserver / MagicDNS) override mapping
    the dashboard hosts (`*.yoonnation.com`) → **`192.168.1.111`** for tailnet
    devices,
  * the **dual-path**: on-tailnet resolves directly to the origin (admitted by
    the `internal-allowlist` middleware); off-tailnet the same name still goes
    through the **tunnel + Access**,
  * **both paths serve the same** LE **wildcard** cert (`originServerName` /
    Traefik's global store), over both **IPv4 and Tailscale IPv6**,
  * **Plex resolution is unaffected off-tailnet** — Plex keeps its **grey**
    (DNS-only) home-IP `A` record for non-tailnet clients; the override must not
    capture it.

Step 6 is primarily manual Tailscale-console configuration and is explicitly
outside the automation "done" scope; this test only gates that the runbook is
present, non-empty, and carries the required operational anchors.

Follows the repo's dual-mode shape-test convention (see
`test_runbook_shape.py`, `test_cloudflare_access_runbook_shape.py`): module-level
`test_<name>() -> bool` functions that print `OK` / `FAIL: ...` (no `assert`),
plus `main() -> int` that sums the booleans and `sys.exit`s non-zero on any
failure. Stdlib only. Regexes anchor on the inner content (mem-1781892715-142d).
The real gate is the standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "tailscale-split-dns.md"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _flat(body: str) -> str:
    # Collapse whitespace so assertions are robust to markdown line-wrapping.
    return " ".join(body.split())


def test_runbook_exists_and_nonempty() -> bool:
    body = _read(RUNBOOK)
    ok = len(body.strip()) > 0
    print(
        f"{'OK' if ok else 'FAIL'}: docs/runbooks/tailscale-split-dns.md exists "
        f"and is non-empty (chars={len(body)})"
    )
    return ok


def test_split_dns_maps_dashboards_to_origin() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    checks = {
        # The Tailscale split-DNS / MagicDNS override mechanism.
        "split-dns mechanism": re.search(
            r'split[- ]dns|restricted\s+nameserver|magicdns', flat, re.IGNORECASE
        )
        is not None,
        # It runs in the Tailscale admin console / applies to tailnet devices.
        "tailnet scope": re.search(
            r'\btailscale\b|\btailnet\b', flat, re.IGNORECASE
        )
        is not None,
        # Maps the dashboard hostname(s) to the origin IP — anchored so the
        # override target is the origin, not a stray IP elsewhere.
        "origin 192.168.1.111": re.search(r'192\.168\.1\.111', flat) is not None,
        # The zone / dashboard hosts being overridden.
        "yoonnation.com hosts": re.search(
            r'\*?\.?yoonnation\.com', flat, re.IGNORECASE
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook maps the dashboard hosts -> "
        f"192.168.1.111 via Tailscale split-DNS (missing={missing})"
    )
    return ok


def test_dual_path_on_and_off_tailnet() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    checks = {
        # On-tailnet: resolves DIRECTLY to the origin, admitted by the
        # internal-allowlist middleware (bounded gap keeps it one thought).
        "direct via internal-allowlist": re.search(
            r'internal-allowlist', flat
        )
        is not None,
        "on-tailnet direct": re.search(
            r'(?:on[- ]?tailnet|tailnet\s+device)s?\b.{0,120}?\bdirect'
            r'|\bdirect\b.{0,120}?(?:on[- ]?tailnet|tailnet)',
            flat,
            re.IGNORECASE,
        )
        is not None,
        # Off-tailnet: the same name still goes through the tunnel + Access.
        "off-tailnet via tunnel+access": re.search(
            r'off[- ]?tailnet\b.{0,160}?\btunnel\b'
            r'|off[- ]?tailnet\b.{0,160}?\baccess\b',
            flat,
            re.IGNORECASE,
        )
        is not None,
    }
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: runbook documents the on/off-tailnet "
        f"dual-path (missing={missing})"
    )
    return ok


def test_same_cert_both_paths() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    # Both paths terminate at Traefik and serve the same LE wildcard cert.
    same_cert = (
        re.search(r'same\b[^.]{0,40}?\bcert', flat, re.IGNORECASE) is not None
        or re.search(r'\bwildcard\b[^.]{0,40}?\bcert', flat, re.IGNORECASE)
        is not None
    )
    ok = same_cert and re.search(r'\bwildcard\b', flat, re.IGNORECASE) is not None
    print(
        f"{'OK' if ok else 'FAIL'}: runbook notes both paths serve the same LE "
        f"wildcard cert (same_cert={same_cert})"
    )
    return ok


def test_ipv4_and_ipv6() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    has_v4 = re.search(r'\bIPv4\b|\bv4\b', flat) is not None
    has_v6 = re.search(r'\bIPv6\b|\bv6\b', flat) is not None
    ok = has_v4 and has_v6
    print(
        f"{'OK' if ok else 'FAIL'}: runbook covers both IPv4 and IPv6 direct "
        f"resolution (v4={has_v4}, v6={has_v6})"
    )
    return ok


def test_plex_resolution_unaffected() -> bool:
    body = _read(RUNBOOK)
    flat = _flat(body)
    mentions_plex = re.search(r'\bplex\b', flat, re.IGNORECASE) is not None
    # Plex must keep its grey / DNS-only home-IP A record for non-tailnet
    # clients — the split-DNS override must not capture it.
    preserved = (
        re.search(
            r'\bplex\b.{0,200}?(?:grey|gray|dns[- ]only|home[- ]ip|A[- ]record)',
            flat,
            re.IGNORECASE,
        )
        is not None
        or re.search(
            r'(?:grey|gray|dns[- ]only|home[- ]ip|A[- ]record).{0,200}?\bplex\b',
            flat,
            re.IGNORECASE,
        )
        is not None
    )
    not_broken = (
        re.search(
            r'\bplex\b.{0,200}?(?:unaffected|not\b[^.]{0,40}?(?:break|broken|capture)|exclud)',
            flat,
            re.IGNORECASE,
        )
        is not None
        or re.search(
            r'(?:not\b[^.]{0,40}?(?:break|broken|capture)|exclud|unaffected).{0,200}?\bplex\b',
            flat,
            re.IGNORECASE,
        )
        is not None
    )
    ok = mentions_plex and preserved and not_broken
    print(
        f"{'OK' if ok else 'FAIL'}: runbook keeps off-tailnet Plex resolution "
        f"unaffected (mentions={mentions_plex}, preserved={preserved}, "
        f"not_broken={not_broken})"
    )
    return ok


TESTS = (
    test_runbook_exists_and_nonempty,
    test_split_dns_maps_dashboards_to_origin,
    test_dual_path_on_and_off_tailnet,
    test_same_cert_both_paths,
    test_ipv4_and_ipv6,
    test_plex_resolution_unaffected,
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
