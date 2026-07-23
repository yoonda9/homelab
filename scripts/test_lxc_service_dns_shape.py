"""Shape test — every service CT pins its own DNS instead of inheriting the host's.

Regression pin for the 2026-07-23 outage: `just play` died on the `common`
role's very first task (`apt` with `update_cache: true`) against CT 110, and a
manual `apt update` inside the CT failed identically while SSH still worked.

The cause was not apt. `tofu/modules/lxc_service/main.tf` emitted no
`initialization { dns { ... } }` block, so PVE wrote no `nameserver:` /
`searchdomain:` key into `/etc/pve/lxc/110.conf` and copied the **PVE host's**
`/etc/resolv.conf` into the container at start. That file is owned by Tailscale
(`docs/runbooks/tailscale-split-dns.md`) and reads `nameserver 100.100.100.100`
— MagicDNS, routable only from inside the tailnet. The service CTs are not
tailnet members, so every lookup hung. SSH kept working because
`ansible/inventory/hosts.yml` addresses hosts by raw IP, which is what made the
failure look Plex-specific.

Two properties are load-bearing and are what this file exists to hold:

1. The `dns` block sits **inside** `initialization`. A `dns` block at container
   top level is not the same schema key, and a whole-file grep would not tell
   the difference — so the check parses `initialization`'s balanced body.
2. **Both** modules pass the inputs. CT 111 only survived the outage because it
   held a stale, pre-Tailscale `resolv.conf` snapshot; it was one recreate away
   from the identical break. A fix applied to `module "plex"` alone leaves that
   trap armed, and a per-file grep would still be green.

Follows the repo's shape-test convention (see `test_lxc_service_module_shape.py`,
`test_plex_ramdisk_bind_mount_shape.py`): module-level `test_<name>() -> bool`
that print `OK` / `FAIL: ...` (no `assert`), plus `main() -> int` summing them.
Stdlib only. `scripts/run_gate.py` discovers this file by glob, and `main()` sums
the `TESTS` tuple — a function not listed there is green-by-omission
(mem-1784137124-c346), so every `test_*` below is registered in `TESTS`.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MAIN_TF = REPO_ROOT / "tofu" / "main.tf"
LOCALS_TF = REPO_ROOT / "tofu" / "locals.tf"
LXC_MAIN_TF = REPO_ROOT / "tofu" / "modules" / "lxc_service" / "main.tf"
LXC_VARIABLES_TF = REPO_ROOT / "tofu" / "modules" / "lxc_service" / "variables.tf"

# Every module call that provisions a real CT must carry the inputs. Listing
# them explicitly (rather than deriving from whatever main.tf happens to
# declare) is deliberate: a new service CT should redden this test until its DNS
# is wired, not be silently exempted by its own absence.
SERVICE_MODULES = ("docker_host", "plex")

# The value that caused the outage. Pinning it as a negative keeps a future
# "just point the CTs at the host resolver" change from landing green.
MAGICDNS = "100.100.100.100"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def _strip_comments(body: str) -> str:
    """Drop `#` comments so prose about a resolver can never satisfy a check.

    This file's own HCL comments name 100.100.100.100 and `server` explicitly,
    so without stripping, the negative checks below would be structurally
    incapable of passing.
    """
    return re.sub(r"#[^\n]*", "", body)


def _balanced(body: str, opener: str) -> str:
    """Inner text of the first `<opener> ... {` block, brace-matched.

    Used for unnamed/assignment blocks (`initialization {`, `net = {`) that the
    `<kind> "<name>" { ... }` regex in the sibling shape tests cannot address.
    Brace matching rather than a lazy `.*?\\n\\}` because these blocks are
    NESTED — a lazy match would stop at the first inner closing brace.
    """
    m = re.search(re.escape(opener) + r"\s*\{", body)
    if not m:
        return ""
    depth, start = 0, m.end() - 1
    for i in range(start, len(body)):
        if body[i] == "{":
            depth += 1
        elif body[i] == "}":
            depth -= 1
            if depth == 0:
                return body[start + 1 : i]
    return ""


def _module_body(body: str, name: str) -> str:
    """Inner text of `module "<name>" { ... }` in main.tf, comments stripped."""
    block = re.search(r'module\s+"%s"\s*\{(.*?)\n\}' % re.escape(name), body, re.DOTALL)
    return _strip_comments(block.group(1)) if block else ""


def _variable_body(body: str, name: str) -> str:
    """Inner text of `variable "<name>" { ... }`, comments stripped."""
    block = re.search(
        r'variable\s+"%s"\s*\{(.*?)\n\}' % re.escape(name), body, re.DOTALL
    )
    return _strip_comments(block.group(1)) if block else ""


def _net_locals() -> str:
    """Inner text of the `net = { ... }` map in locals.tf, comments stripped."""
    return _balanced(_strip_comments(_read(LOCALS_TF)), "net =")


def _initialization_body() -> str:
    """Inner text of the module's `initialization { ... }`, comments stripped."""
    return _balanced(_strip_comments(_read(LXC_MAIN_TF)), "initialization")


def test_module_declares_dns_variables() -> bool:
    """The module exposes `dns_servers` (list) and `dns_domain` (string)."""
    body = _read(LXC_VARIABLES_TF)
    servers = _variable_body(body, "dns_servers")
    domain = _variable_body(body, "dns_domain")
    servers_ok = bool(re.search(r"type\s*=\s*list\(string\)", servers))
    domain_ok = bool(re.search(r"type\s*=\s*string", domain))
    ok = servers_ok and domain_ok
    print(
        f"{'OK' if ok else 'FAIL'}: lxc_service declares dns_servers:list(string) "
        f"and dns_domain:string (dns_servers={servers_ok}, dns_domain={domain_ok})"
    )
    return ok


def test_dns_block_is_inside_initialization() -> bool:
    """The `dns` block is nested in `initialization`, not at container top level.

    Scoped to the parsed `initialization` body: a `dns` block hoisted a level up
    is a different (nonexistent) schema key, and PVE would go back to copying the
    host resolv.conf — while a whole-file `grep dns` stayed green.
    """
    init = _initialization_body()
    ok = bool(init) and bool(re.search(r'dynamic\s+"dns"\s*\{|\bdns\s*\{', init))
    print(
        f"{'OK' if ok else 'FAIL'}: a dns block is nested inside "
        f"initialization{{}} in lxc_service/main.tf (initialization_parsed={bool(init)})"
    )
    return ok


def test_dns_uses_servers_not_deprecated_server() -> bool:
    """Uses the `servers` list attribute, not the deprecated singular `server`.

    bpg/proxmox marks `server` deprecated ("will be removed in a future
    release"), so a `server =` here is a scheduled breakage, and it also cannot
    express the router-plus-fallback pair the net locals define.
    """
    init = _initialization_body()
    dns = _balanced(init, "content") or init
    uses_servers = bool(re.search(r"\bservers\s*=", dns))
    uses_singular = bool(re.search(r"\bserver\s*=", dns))
    ok = bool(init) and uses_servers and not uses_singular
    print(
        f"{'OK' if ok else 'FAIL'}: dns block uses servers= and not the deprecated "
        f"server= (servers={uses_servers}, deprecated_server={uses_singular})"
    )
    return ok


def test_net_locals_define_dns() -> bool:
    """`local.net` carries dns_servers and dns_domain — the single definition site."""
    net = _net_locals()
    servers = bool(re.search(r"\bdns_servers\s*=\s*\[", net))
    domain = bool(re.search(r'\bdns_domain\s*=\s*"', net))
    ok = servers and domain
    print(
        f"{'OK' if ok else 'FAIL'}: locals.tf net{{}} defines dns_servers and "
        f"dns_domain (dns_servers={servers}, dns_domain={domain})"
    )
    return ok


def test_every_service_module_wires_dns() -> bool:
    """BOTH module calls pass the DNS inputs — not just the one that broke.

    docker-host survived the outage only on a stale pre-Tailscale resolv.conf
    snapshot; unwired, its next recreate inherits MagicDNS and breaks exactly as
    CT 110 did. A plex-only fix must not pass this gate.
    """
    body = _read(MAIN_TF)
    missing = []
    for name in SERVICE_MODULES:
        mod = _module_body(body, name)
        if not (
            mod
            and re.search(r"\bdns_servers\s*=", mod)
            and re.search(r"\bdns_domain\s*=", mod)
        ):
            missing.append(name)
    ok = not missing
    print(
        f"{'OK' if ok else 'FAIL'}: every service module wires dns_servers/dns_domain "
        f"(checked={list(SERVICE_MODULES)}, missing={missing})"
    )
    return ok


def test_dns_servers_exclude_tailscale_magicdns() -> bool:
    """Negative guard: the configured resolvers are not the host's MagicDNS.

    100.100.100.100 answers only for tailnet members. The service CTs are not
    tailnet members, so this exact value is what hung every lookup on CT 110.
    """
    net = _net_locals()
    servers = _balanced(net, "dns_servers =") or re.search(
        r"dns_servers\s*=\s*\[(.*?)\]", net, re.DOTALL
    )
    listed = servers.group(1) if hasattr(servers, "group") else ""
    # Premise: the list was actually parsed. Without it, a renamed key would
    # empty `listed` and vacuously satisfy the "not in" clause.
    premise = bool(re.search(r"\d", listed))
    ok = premise and MAGICDNS not in listed
    print(
        f"{'OK' if ok else 'FAIL'}: net.dns_servers excludes Tailscale MagicDNS "
        f"{MAGICDNS} (parsed={premise}, servers={listed.strip()!r})"
    )
    return ok


TESTS = (
    test_module_declares_dns_variables,
    test_dns_block_is_inside_initialization,
    test_dns_uses_servers_not_deprecated_server,
    test_net_locals_define_dns,
    test_every_service_module_wires_dns,
    test_dns_servers_exclude_tailscale_magicdns,
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
