"""Shape tests for the docker_host role + Traefik configuration (Step 5).

Per design §4.3 (docker_host role), §4.4 (Traefik configuration) and task-05 —
verifies the ansible `docker_host` role brings up Traefik (HTTP-01 active,
Cloudflare DNS-01 defined) with a LAN-only `whoami` smoke route:

- roles/docker_host/ exists with tasks/main.yml and a templates/ dir holding
  compose.yml.j2 plus the Traefik static (traefik.yml.j2) + dynamic
  (dynamic.yml.j2) config templates;
- the static config defines `web` (:80, redirect->websecure) and `websecure`
  (:443) entrypoints and BOTH certresolvers (le-http httpChallenge + le-dns-cf
  Cloudflare dnsChallenge);
- the active resolver on the whoami router is variable-driven ({{ acme_resolver }}),
  not a hard-coded literal, so the Step-11 flip is one variable;
- the dynamic config defines the redirect-to-https / security-headers /
  lan-allowlist middlewares and lan-allowlist carries both the 192.168.1.0/24
  and Tailscale 100.64.0.0/10 source ranges;
- the whoami service/router is present, internal-only (carries lan-allowlist,
  NOT in public_services);
- docker_host tasks/main.yml is idempotent (no unguarded command/shell/raw,
  reusing the Step-4 guard scan) and ansible.builtin-only;
- no plaintext secret literals (the Cloudflare token is a var/env reference);
- site.yml applies docker_host to the docker_host group.

Dual-mode (module-level test_*()->bool + main()->int), stdlib only, mirroring
scripts/test_ansible_layout_shape.py (mem-1781891042-4495). Per mem-1781892715-142d
the regexes anchor on the inner attribute (the actual key/value), not just a
section opener, so an empty stub could not satisfy the check. The real gate is
the standalone exit code.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ANSIBLE = REPO_ROOT / "ansible"
ROLE = ANSIBLE / "roles" / "docker_host"
TASKS = ROLE / "tasks" / "main.yml"
TEMPLATES = ROLE / "templates"
COMPOSE = TEMPLATES / "compose.yml.j2"
STATIC = TEMPLATES / "traefik.yml.j2"
DYNAMIC = TEMPLATES / "dynamic.yml.j2"
ENV = TEMPLATES / "env.j2"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def test_role_structure_exists() -> bool:
    required = [TASKS, COMPOSE, STATIC, DYNAMIC]
    missing = [str(p.relative_to(ANSIBLE)) for p in required if not p.is_file()]
    ok = TEMPLATES.is_dir() and not missing
    print(f"{'OK' if ok else 'FAIL'}: docker_host role + templates present (missing={missing})")
    return ok


def test_entrypoints_with_redirect() -> bool:
    body = _read(STATIC)
    # web entrypoint on :80 that redirects to websecure; websecure on :443.
    web = re.search(r'(?ms)^\s*web:\s*$.*?address:\s*"?:80', body) is not None
    redirect = re.search(r'(?s)redirections:.*?to:\s*websecure', body) is not None
    websecure = re.search(r'(?ms)^\s*websecure:\s*$.*?address:\s*"?:443', body) is not None
    ok = web and redirect and websecure
    print(
        f"{'OK' if ok else 'FAIL'}: entrypoints web(:80 redirect)->websecure(:443) "
        f"(web={web}, redirect={redirect}, websecure={websecure})"
    )
    return ok


def test_both_certresolvers() -> bool:
    body = _read(STATIC)
    # le-http must use an HTTP-01 challenge; le-dns-cf a Cloudflare DNS-01 one.
    http = re.search(r'(?s)le-http:.*?acme:.*?httpChallenge', body) is not None
    dns = re.search(r'(?s)le-dns-cf:.*?acme:.*?dnsChallenge:.*?provider:\s*cloudflare', body) is not None
    ok = http and dns
    print(f"{'OK' if ok else 'FAIL'}: both certresolvers defined (le-http http01={http}, le-dns-cf cf-dns01={dns})")
    return ok


def test_resolver_is_variable_driven() -> bool:
    body = _read(COMPOSE)
    # The active resolver on the whoami router is selected from acme_resolver,
    # not a hard-coded `certresolver=le-http` literal.
    var_driven = re.search(r'certresolver\s*=\s*\{\{\s*acme_resolver\s*\}\}', body) is not None
    hardcoded = re.search(r'certresolver\s*=\s*le-(http|dns-cf)\b', body) is not None
    ok = var_driven and not hardcoded
    print(f"{'OK' if ok else 'FAIL'}: router resolver is variable-driven (var={var_driven}, hardcoded={hardcoded})")
    return ok


def test_middlewares_defined() -> bool:
    body = _read(DYNAMIC)
    redirect = re.search(r'(?s)redirect-to-https:.*?redirectScheme', body) is not None
    headers = re.search(r'(?s)security-headers:.*?headers:', body) is not None
    allowlist = re.search(r'(?s)lan-allowlist:.*?ipAllowList', body) is not None
    ok = redirect and headers and allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: middlewares defined "
        f"(redirect-to-https={redirect}, security-headers={headers}, lan-allowlist={allowlist})"
    )
    return ok


def test_lan_allowlist_source_ranges() -> bool:
    body = _read(DYNAMIC)
    # Both the LAN /24 and the Tailscale CGNAT range must be inside lan-allowlist.
    ok = re.search(
        r'(?s)lan-allowlist:.*?sourceRange:.*?192\.168\.1\.0/24.*?100\.64\.0\.0/10',
        body,
    ) is not None
    print(f"{'OK' if ok else 'FAIL'}: lan-allowlist carries 192.168.1.0/24 + 100.64.0.0/10")
    return ok


def test_whoami_internal_only() -> bool:
    compose = _read(COMPOSE)
    defaults = _read(ROLE / "defaults" / "main.yml")
    has_service = re.search(r'(?m)^\s*whoami:\s*$', compose) is not None
    # The whoami service pulls the traefik/whoami image (directly or via the
    # whoami_image default it references).
    img_literal = re.search(r'(?m)^\s*image:\s*traefik/whoami', compose) is not None
    img_var = (
        re.search(r'(?m)^\s*image:\s*\{\{\s*docker_host_whoami_image\s*\}\}', compose) is not None
        and re.search(r'(?m)^\s*docker_host_whoami_image:\s*traefik/whoami', defaults) is not None
    )
    has_image = img_literal or img_var
    # whoami router must carry the lan-allowlist middleware (LAN-only).
    router_allowlist = re.search(
        r'routers\.whoami\.middlewares\s*=\s*[^\n]*lan-allowlist', compose
    ) is not None
    # ...and must NOT be promoted to a public service.
    all_yml = _read(ANSIBLE / "group_vars" / "all.yml")
    pub = re.search(r'(?ms)^public_services:\s*$(.*?)^\S', all_yml + "\nEOF")
    pub_block = pub.group(1) if pub else ""
    not_public = "whoami" not in pub_block
    ok = has_service and has_image and router_allowlist and not_public
    print(
        f"{'OK' if ok else 'FAIL'}: whoami internal-only "
        f"(service={has_service}, image={has_image}, lan-allowlist={router_allowlist}, not_public={not_public})"
    )
    return ok


def test_tasks_idempotent_builtin_only() -> bool:
    """No unguarded command/shell/raw and no community.* collections (AC3).

    Reuses the Step-4 guard scan: every FQCN command/shell/raw module task must
    sit near a changed_when/creates/removes/when guard.
    """
    body = _read(TASKS)
    if not body:
        print("FAIL: docker_host tasks idempotent (tasks/main.yml missing)")
        return False
    unguarded = []
    for m in re.finditer(r'(?m)^\s*ansible\.builtin\.(command|shell|raw)\s*:', body):
        window = body[m.start():m.start() + 600]
        if not re.search(r'changed_when|creates|removes|when\s*:', window):
            unguarded.append(m.group(1))
    community = re.search(r'(?m)^\s*community\.', body) is not None
    ok = not unguarded and not community
    print(
        f"{'OK' if ok else 'FAIL'}: docker_host tasks idempotent + builtin-only "
        f"(unguarded={unguarded}, community={community})"
    )
    return ok


def test_no_plaintext_secrets() -> bool:
    # The Cloudflare token must be a Jinja var / compose env reference, never a
    # literal. Flag any obvious literal token assignment in the role files.
    leaks = []
    for path in sorted(ROLE.rglob("*")):
        if not path.is_file():
            continue
        for ln in _read(path).splitlines():
            # A real token value: 20+ token chars assigned to a CF/token key.
            if re.search(
                r'(?i)(cf_dns_api_token|cloudflare[_a-z]*token)\s*[:=]\s*[A-Za-z0-9_\-]{20,}',
                ln,
            ) and not re.search(r'\{\{.*\}\}|\$\{', ln):
                leaks.append(f"{path.name}: {ln.strip()[:60]}")
    ok = not leaks
    print(f"{'OK' if ok else 'FAIL'}: no plaintext secret literals in role (leaks={leaks})")
    return ok


def test_site_applies_docker_host_role() -> bool:
    site = _read(ANSIBLE / "site.yml")
    # A play that targets the docker_host group and applies the docker_host role.
    ok = re.search(r'(?s)hosts:\s*docker_host\b.*?roles:.*?\bdocker_host\b', site) is not None
    print(f"{'OK' if ok else 'FAIL'}: site.yml applies docker_host role to the docker_host group")
    return ok


def _routers_block(body: str) -> str:
    """The `http.routers:` section of dynamic.yml.j2 (up to `services:`)."""
    m = re.search(r'(?ms)^\s*routers:\s*$(.*?)(?=^\s*services:\s*$|\Z)', body)
    return m.group(1) if m else ""


def _services_block(body: str) -> str:
    """The `http.services:` section of dynamic.yml.j2 (to EOF)."""
    m = re.search(r'(?ms)^\s*services:\s*$(.*)', body)
    return m.group(1) if m else ""


def test_plex_public_router_present() -> bool:
    """Step-9: dynamic.yml.j2 defines the file-provider `plex` router (AC2/AC3)."""
    routers = _routers_block(_read(DYNAMIC))
    host = re.search(r'Host\(`plex\.\{\{\s*domain\s*\}\}`\)', routers) is not None
    websecure = re.search(r'(?s)entryPoints:.*?\bwebsecure\b', routers) is not None
    service = re.search(r'(?m)^\s*service:\s*plex\s*$', routers) is not None
    # certResolver MUST be the {{ acme_resolver }} var, NOT a hard-coded literal,
    # so the Step-11 DNS-01 flip touches one variable (mirrors whoami invariant).
    var_driven = re.search(r'certResolver:\s*"?\{\{\s*acme_resolver\s*\}\}', routers) is not None
    hardcoded = re.search(r'certResolver:\s*"?le-(http|dns-cf)\b', routers) is not None
    ok = host and websecure and service and var_driven and not hardcoded
    print(
        f"{'OK' if ok else 'FAIL'}: plex public router present "
        f"(host={host}, websecure={websecure}, service={service}, "
        f"var_resolver={var_driven}, hardcoded={hardcoded})"
    )
    return ok


def test_plex_service_backend_32400() -> bool:
    """Step-9: plex loadBalancer backend resolves to 192.168.1.110:32400 (AC4)."""
    services = _services_block(_read(DYNAMIC))
    defaults = _read(ROLE / "defaults" / "main.yml")
    has_service = re.search(r'(?m)^\s*plex:\s*$', services) is not None
    # Literal-OR-var, mirroring whoami_image: either the inline URL or a
    # docker_host_plex_url default whose value points at the Plex CT.
    url_literal = re.search(r'http://192\.168\.1\.110:32400', services) is not None
    url_var = (
        re.search(r'url:\s*"?\{\{\s*docker_host_plex_url\s*\}\}', services) is not None
        and re.search(
            r'(?m)^\s*docker_host_plex_url:\s*"?http://192\.168\.1\.110:32400', defaults
        ) is not None
    )
    ok = has_service and (url_literal or url_var)
    print(
        f"{'OK' if ok else 'FAIL'}: plex service backend -> 192.168.1.110:32400 "
        f"(service={has_service}, literal={url_literal}, var={url_var})"
    )
    return ok


def test_plex_router_is_public_not_allowlisted() -> bool:
    """Step-9: plex is the ONLY public router — no lan-allowlist (security-critical).

    The plex router carries security-headers but NOT lan-allowlist, while the
    internal whoami router still does (regression guard on the allowlist split).
    """
    routers = _routers_block(_read(DYNAMIC))
    plex_no_allowlist = "lan-allowlist" not in routers
    plex_has_headers = "security-headers" in routers
    compose = _read(COMPOSE)
    whoami_allowlist = re.search(
        r'routers\.whoami\.middlewares\s*=\s*[^\n]*lan-allowlist', compose
    ) is not None
    ok = plex_no_allowlist and plex_has_headers and whoami_allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: plex router public (no lan-allowlist), whoami still internal "
        f"(plex_no_allowlist={plex_no_allowlist}, plex_headers={plex_has_headers}, "
        f"whoami_allowlist={whoami_allowlist})"
    )
    return ok


def test_public_services_is_exactly_plex() -> bool:
    """Step-9: group_vars public_services is exactly [plex] — nothing else promoted."""
    all_yml = _read(ANSIBLE / "group_vars" / "all.yml")
    m = re.search(r'(?ms)^public_services:\s*$(.*?)^\S', all_yml + "\nEOF")
    block = m.group(1) if m else ""
    entries = re.findall(r'(?m)^\s*-\s*(\S+)', block)
    ok = entries == ["plex"]
    print(f"{'OK' if ok else 'FAIL'}: public_services is exactly [plex] (entries={entries})")
    return ok


# The four LAN/Tailscale-only extras (Step 10), in design §5 order.
EXTRAS = ["homepage", "uptime-kuma", "grafana", "prometheus"]


def test_extras_services_present() -> bool:
    """Step-10: all four extras are compose services (docker-provider routed)."""
    compose = _read(COMPOSE)
    missing = [s for s in EXTRAS if re.search(rf'(?m)^\s{{2}}{re.escape(s)}:\s*$', compose) is None]
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: extras services present (missing={missing})")
    return ok


def test_extras_internal_routers_allowlisted() -> bool:
    """Step-10: every extras router carries lan-allowlist + a var-driven resolver.

    Each of the four routers must include the lan-allowlist middleware and select
    its certresolver from {{ acme_resolver }} (NOT a hard-coded le-http/le-dns-cf
    literal), so the Step-11 DNS-01 flip stays one variable and the internal split
    holds as the stack grows.
    """
    compose = _read(COMPOSE)
    failures = []
    for s in EXTRAS:
        mw = re.search(
            rf'routers\.{re.escape(s)}\.middlewares\s*=\s*[^\n]*lan-allowlist', compose
        ) is not None
        cr = re.search(
            rf'routers\.{re.escape(s)}\.tls\.certresolver\s*=\s*\{{\{{\s*acme_resolver\s*\}}\}}',
            compose,
        ) is not None
        if not (mw and cr):
            failures.append(f"{s}(allowlist={mw},var_resolver={cr})")
    hardcoded = re.search(
        r'routers\.(?:homepage|uptime-kuma|grafana|prometheus)\.tls\.certresolver\s*=\s*le-(?:http|dns-cf)\b',
        compose,
    ) is not None
    ok = not failures and not hardcoded
    print(
        f"{'OK' if ok else 'FAIL'}: extras routers lan-allowlisted + var-driven resolver "
        f"(failures={failures}, hardcoded={hardcoded})"
    )
    return ok


def test_prometheus_never_public() -> bool:
    """Step-10: prometheus is never public (defense-in-depth, design §6).

    Not in public_services AND its router carries lan-allowlist.
    """
    all_yml = _read(ANSIBLE / "group_vars" / "all.yml")
    m = re.search(r'(?ms)^public_services:\s*$(.*?)^\S', all_yml + "\nEOF")
    pub_block = m.group(1) if m else ""
    not_public = "prometheus" not in pub_block
    compose = _read(COMPOSE)
    router_allowlist = re.search(
        r'routers\.prometheus\.middlewares\s*=\s*[^\n]*lan-allowlist', compose
    ) is not None
    ok = not_public and router_allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: prometheus never public "
        f"(not_public={not_public}, router_allowlist={router_allowlist})"
    )
    return ok


def test_homepage_allowed_hosts() -> bool:
    """Step-10: homepage sets HOMEPAGE_ALLOWED_HOSTS=homepage.{{ domain }}.

    gethomepage/homepage (v0.9.0+) rejects any request whose Host header is not
    localhost and not listed in HOMEPAGE_ALLOWED_HOSTS. Reached ONLY through
    Traefik on Host(`homepage.{{ domain }}`), so without this env every real
    request hits a "Host validation failed" page and the dashboard never loads.
    """
    compose = _read(COMPOSE)
    m = re.search(r'(?ms)^\s{2}homepage:\s*$(.*?)^\s{2}\S', compose + "\n  EOF:")
    block = m.group(1) if m else ""
    ok = re.search(
        r'HOMEPAGE_ALLOWED_HOSTS\s*=\s*[^\n]*homepage\.\{\{\s*domain\s*\}\}', block
    ) is not None
    print(f"{'OK' if ok else 'FAIL'}: homepage sets HOMEPAGE_ALLOWED_HOSTS for its proxied host")
    return ok


def test_internal_services_exactly_four() -> bool:
    """Step-10: group_vars internal_services is exactly the four extras (design §5)."""
    all_yml = _read(ANSIBLE / "group_vars" / "all.yml")
    m = re.search(r'(?ms)^internal_services:\s*$(.*?)^\S', all_yml + "\nEOF")
    block = m.group(1) if m else ""
    entries = re.findall(r'(?m)^\s*-\s*(\S+)', block)
    ok = entries == EXTRAS
    print(f"{'OK' if ok else 'FAIL'}: internal_services is exactly {EXTRAS} (entries={entries})")
    return ok


def test_cf_token_sourced_from_vault() -> bool:
    """Step-11: env.j2 sources CF_DNS_API_TOKEN from vault_cloudflare_dns_api_token.

    The actual Ansible-Vault key is `vault_cloudflare_dns_api_token` (siblings:
    vault_grafana_admin_password, vault_dashboard_basic_auth_hash). The earlier
    reference `cloudflare_dns_api_token` is UNDEFINED, so `default('')` rendered
    the token EMPTY — harmless under HTTP-01 but breaks every Cloudflare DNS-01
    challenge once acme_resolver flips to le-dns-cf. This regression guard fails
    on the old text and passes only on the corrected vault key.
    """
    body = _read(ENV)
    correct = re.search(
        r'CF_DNS_API_TOKEN\s*=\s*\{\{\s*vault_cloudflare_dns_api_token\b', body
    ) is not None
    # The undefined (vault_-less) reference must be gone.
    buggy = re.search(
        r'CF_DNS_API_TOKEN\s*=\s*\{\{\s*cloudflare_dns_api_token\b', body
    ) is not None
    ok = correct and not buggy
    print(
        f"{'OK' if ok else 'FAIL'}: CF_DNS_API_TOKEN sourced from vault_cloudflare_dns_api_token "
        f"(correct={correct}, buggy_ref={buggy})"
    )
    return ok


def test_wildcard_dns01_gated() -> bool:
    """Step-11: a router declares the DNS-01 wildcard tls.domains, gated to le-dns-cf.

    Traefik only requests a wildcard cert when a router declares `tls.domains`
    (main: {{ domain }}, sans: *.{{ domain }}). HTTP-01 cannot issue wildcards, so
    the declaration MUST be gated on `acme_resolver == 'le-dns-cf'` — an accidental
    le-http value must not request an unsatisfiable wildcard. Text-presence here;
    the dual-mode Jinja+YAML render harness proves the gate actually suppresses it
    under le-http.
    """
    body = _read(COMPOSE)
    gate = re.search(r"\{%\s*if\s+acme_resolver\s*==\s*'le-dns-cf'\s*%\}", body) is not None
    main = re.search(r'tls\.domains\[0\]\.main\s*=\s*\{\{\s*domain\s*\}\}', body) is not None
    sans = re.search(r'tls\.domains\[0\]\.sans\s*=\s*\*\.\{\{\s*domain\s*\}\}', body) is not None
    ok = gate and main and sans
    print(
        f"{'OK' if ok else 'FAIL'}: wildcard tls.domains declared + gated to le-dns-cf "
        f"(gate={gate}, main={main}, sans={sans})"
    )
    return ok


def test_traefik_image_pinned_to_concrete_v3() -> bool:
    """Services->latest-stable: docker_host_traefik_image is a concrete v3.x.y pin.

    The Traefik image must pin a concrete `traefik:v3.<minor>.<patch>` tag (the
    current stable v3 line, e.g. v3.7.5), NOT the stale `traefik:v3.3`, NOT a
    floating tag (`latest` or a bare major `v3`). Asserting CONCRETENESS +
    non-staleness (not a hardcoded literal) so future version bumps stay green
    while a regression to a floating/stale tag reddens the gate.
    """
    defaults = _read(ROLE / "defaults" / "main.yml")
    m = re.search(r'(?m)^\s*docker_host_traefik_image:\s*"?([^"\s#]+)', defaults)
    img = m.group(1) if m else ""
    # Concrete three-part semver tag on the v3 line.
    concrete = re.fullmatch(r'traefik:v3\.\d+\.\d+', img) is not None
    # Explicitly reject the stale starting value and any floating tag.
    not_stale = img != "traefik:v3.3"
    not_floating = not re.fullmatch(r'traefik:(latest|v3)', img)
    ok = concrete and not_stale and bool(not_floating)
    print(
        f"{'OK' if ok else 'FAIL'}: traefik image pinned to concrete v3.x.y "
        f"(image={img!r}, concrete={concrete}, not_stale={not_stale}, not_floating={bool(not_floating)})"
    )
    return ok


def test_no_floating_service_image_tags() -> bool:
    """Services->latest-stable: EVERY docker_host_*_image default is concrete-pinned.

    Blanket regression guard for the whole compose stack (Step-2). Parses every
    `docker_host_<name>_image:` default and asserts its tag is a concrete pin —
    a three-part `[v]MAJOR.MINOR.PATCH` version (optionally with a -suffix) — and
    NEVER a floating tag: `latest`, a bare-major (`v3`, `1`) or bare-minor (`v3.3`),
    or a missing tag. Shape, not a literal-version list, so future version bumps
    stay GREEN while any regression to a floating/stale tag reddens the gate.
    The traefik-specific check above stays as the named-example regression.
    """
    defaults = _read(ROLE / "defaults" / "main.yml")
    floating = []
    images = re.findall(
        r'(?m)^\s*(docker_host_\w*_image):\s*"?([^"\s#]+)', defaults
    )
    for var, value in images:
        # The tag is the segment after the LAST colon (registry host has no port
        # in any of these refs, so the last colon always separates the tag).
        tag = value.rsplit(":", 1)[1] if ":" in value else ""
        concrete = re.fullmatch(r'v?\d+\.\d+\.\d+(?:-[\w.]+)?', tag) is not None
        if not concrete:
            floating.append(f"{var}={value!r}(tag={tag!r})")
    # There must be image defaults to check (guard against a vacuous pass).
    ok = bool(images) and not floating
    print(
        f"{'OK' if ok else 'FAIL'}: all {len(images)} docker_host_*_image defaults "
        f"concrete-pinned (floating={floating})"
    )
    return ok


def test_acme_resolver_is_dns_cf() -> bool:
    """Step-11: the one-variable flip is committed — acme_resolver is le-dns-cf.

    group_vars/all.yml now defaults to DNS-01. Templates still select the resolver
    via {{ acme_resolver }} (covered by test_resolver_is_variable_driven and the
    extras/plex literal-free checks), so flipping back to le-http re-renders cleanly.
    """
    all_yml = _read(ANSIBLE / "group_vars" / "all.yml")
    ok = re.search(r'(?m)^acme_resolver:\s*le-dns-cf\s*$', all_yml) is not None
    print(f"{'OK' if ok else 'FAIL'}: group_vars acme_resolver is le-dns-cf (committed flip)")
    return ok


def main() -> int:
    results = [
        test_role_structure_exists(),
        test_entrypoints_with_redirect(),
        test_both_certresolvers(),
        test_resolver_is_variable_driven(),
        test_middlewares_defined(),
        test_lan_allowlist_source_ranges(),
        test_whoami_internal_only(),
        test_tasks_idempotent_builtin_only(),
        test_no_plaintext_secrets(),
        test_site_applies_docker_host_role(),
        test_plex_public_router_present(),
        test_plex_service_backend_32400(),
        test_plex_router_is_public_not_allowlisted(),
        test_public_services_is_exactly_plex(),
        test_extras_services_present(),
        test_extras_internal_routers_allowlisted(),
        test_prometheus_never_public(),
        test_homepage_allowed_hosts(),
        test_internal_services_exactly_four(),
        test_cf_token_sourced_from_vault(),
        test_wildcard_dns01_gated(),
        test_traefik_image_pinned_to_concrete_v3(),
        test_no_floating_service_image_tags(),
        test_acme_resolver_is_dns_cf(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
