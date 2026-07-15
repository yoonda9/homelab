"""Shape tests for the docker_host role + Traefik configuration (Step 5).

Per design §4.3 (docker_host role), §4.4 (Traefik configuration) and task-05 —
verifies the ansible `docker_host` role brings up Traefik (HTTP-01 active,
Cloudflare DNS-01 defined) with a LAN-only `whoami` smoke route:

- roles/docker_host/ exists with tasks/main.yml and a templates/ dir holding
  compose.yml.j2 plus the Traefik static (traefik.yml.j2) + dynamic
  (dynamic.yml.j2) config templates;
- the static config defines `web` (:80, plain-HTTP Cloudflare-tunnel ingress with
  NO global redirect — a :80->:443 entrypoint redirect would loop the HTTP tunnel;
  the http->https upgrade moved to the per-router plex-web redirect) and
  `websecure` (:443) entrypoints and a SINGLE Cloudflare DNS-01 certresolver;
  `le-http` is removed (only DNS-01 issues wildcards) and staging vs prod is a
  single `caServer: "{{ acme_ca_server }}"` toggle (LE staging until Step 7);
- the active resolver on the whoami router is variable-driven ({{ acme_resolver }}),
  not a hard-coded literal, so the Step-11 flip is one variable;
- the dynamic config defines the redirect-to-https / security-headers /
  internal-allowlist middlewares and internal-allowlist carries all four internal
  source ranges (192.168.1.0/24, Tailscale 100.64.0.0/10 + fd7a:115c:a1e0::/48,
  and the broad Docker 172.16.0.0/12 for the Step-4 cloudflared hop);
- the whoami service/router is present, internal-only (carries internal-allowlist,
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
HOMEPAGE_SERVICES = TEMPLATES / "homepage-services.yaml.j2"


def _read(path: pathlib.Path) -> str:
    return path.read_text() if path.is_file() else ""


def test_role_structure_exists() -> bool:
    required = [TASKS, COMPOSE, STATIC, DYNAMIC]
    missing = [str(p.relative_to(ANSIBLE)) for p in required if not p.is_file()]
    ok = TEMPLATES.is_dir() and not missing
    print(f"{'OK' if ok else 'FAIL'}: docker_host role + templates present (missing={missing})")
    return ok


def test_entrypoints_with_redirect() -> bool:
    """web(:80) is the plain-HTTP tunnel ingress (NO global redirect); websecure(:443).

    Name kept for acceptance traceability; the assertion is retargeted to the
    Option-1 (edge-terminated TLS) invariant. cloudflared sends plain HTTP to
    traefik:80, so the `web` entrypoint must NOT carry an entrypoint-level
    redirection block — a global 301 bounces the tunnel's HTTP request to HTTPS
    and, since the tunnel re-enters on :80, loops forever (the old Error-1000 /
    redirect-loop class). The http->https upgrade instead rides the per-router
    `plex-web` redirect (dynamic.yml.j2) so the public port-forwarded plex path
    is preserved. Asserts web(:80) + websecure(:443) exist, no entrypoint-level
    redirection anywhere in the static config, and the plex-web upgrade router.
    """
    static = _read(STATIC)
    dynamic = _read(DYNAMIC)
    web = re.search(r'(?ms)^\s*web:\s*$.*?address:\s*"?:80', static) is not None
    websecure = re.search(r'(?ms)^\s*websecure:\s*$.*?address:\s*"?:443', static) is not None
    # The loop-causer: an entrypoint-level `redirections:` block must be gone.
    no_ep_redirect = re.search(r'(?s)redirections:', static) is None
    # The upgrade relocated onto the public plex-web file-provider router.
    plex_web_redirect = re.search(
        r'(?ms)^\s{4}plex-web:\s*$.*?redirect-to-https', dynamic
    ) is not None
    ok = web and websecure and no_ep_redirect and plex_web_redirect
    print(
        f"{'OK' if ok else 'FAIL'}: web(:80 plain)/websecure(:443), no entrypoint redirect, "
        f"plex-web upgrade (web={web}, websecure={websecure}, "
        f"no_ep_redirect={no_ep_redirect}, plex_web_redirect={plex_web_redirect})"
    )
    return ok


def test_both_certresolvers() -> bool:
    """Step 1: exactly one ACME certresolver — Cloudflare DNS-01 (`le-dns-cf`).

    Function name retained for acceptance traceability (task-01 §Acceptance-3);
    the assertion is retargeted to the post-migration invariant. The old
    HTTP-01 `le-http` resolver is REMOVED — only DNS-01 can issue the
    `*.{{ domain }}` wildcard, so `le-dns-cf` must be the sole resolver.
    """
    body = _read(STATIC)
    dns = re.search(r'(?s)le-dns-cf:.*?acme:.*?dnsChallenge:.*?provider:\s*cloudflare', body) is not None
    # `le-http:` as a YAML resolver key must be gone (comment mentions can't match).
    http_gone = re.search(r'(?m)^\s*le-http:\s*$', body) is None
    ok = dns and http_gone
    print(f"{'OK' if ok else 'FAIL'}: single DNS-01 certresolver le-dns-cf (cf-dns01={dns}, le-http_gone={http_gone})")
    return ok


def test_caserver_toggle_wired() -> bool:
    """Step 7: `le-dns-cf` pins `caServer` to the `acme_ca_server` toggle, now on PROD.

    The DNS-01 resolver must carry `caServer: "{{ acme_ca_server }}"` under its
    `acme` block, and `group_vars/all/vars.yml` must define `acme_ca_server` set to the
    LE **production** directory URL (staging was retired at the Step-7 flip). This
    keeps the staging->prod cutover a single variable, not a template edit. Anchors
    on the prod directory host and rejects the staging host so a regression back to
    `acme-staging-v02` reddens.
    """
    static = _read(STATIC)
    all_yml = _read(ANSIBLE / "group_vars" / "all" / "vars.yml")
    caserver = re.search(
        r'(?s)le-dns-cf:.*?acme:.*?caServer:\s*"?\{\{\s*acme_ca_server\s*\}\}',
        static,
    ) is not None
    defined = re.search(r'(?m)^acme_ca_server:\s*\S', all_yml) is not None
    prod = re.search(
        r'(?m)^acme_ca_server:\s*"?https://acme-v02\.api\.letsencrypt\.org/directory',
        all_yml,
    ) is not None
    not_staging = re.search(
        r'(?m)^acme_ca_server:\s*"?https://acme-staging-v02\.', all_yml
    ) is None
    ok = caserver and defined and prod and not_staging
    print(
        f"{'OK' if ok else 'FAIL'}: caServer wired to acme_ca_server prod toggle "
        f"(caServer={caserver}, defined={defined}, prod={prod}, not_staging={not_staging})"
    )
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
    allowlist = re.search(r'(?s)internal-allowlist:.*?ipAllowList', body) is not None
    ok = redirect and headers and allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: middlewares defined "
        f"(redirect-to-https={redirect}, security-headers={headers}, internal-allowlist={allowlist})"
    )
    return ok


def test_lan_allowlist_source_ranges() -> bool:
    # Name kept for acceptance traceability (Step-2 retarget): the allowlist is now
    # `internal-allowlist` and must carry all four internal ranges in order — the LAN
    # /24, the Tailscale CGNAT v4 range, the Tailscale ULA v6 prefix, and the broad
    # Docker private range that admits the Step-4 cloudflared hop without pinning a subnet.
    body = _read(DYNAMIC)
    ok = re.search(
        r'(?s)internal-allowlist:.*?sourceRange:'
        r'.*?192\.168\.1\.0/24.*?100\.64\.0\.0/10.*?fd7a:115c:a1e0::/48.*?172\.16\.0\.0/12',
        body,
    ) is not None
    print(
        f"{'OK' if ok else 'FAIL'}: internal-allowlist carries 192.168.1.0/24 + "
        f"100.64.0.0/10 + fd7a:115c:a1e0::/48 + 172.16.0.0/12"
    )
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
    # whoami router must carry the internal-allowlist middleware (LAN/Tailscale-only).
    router_allowlist = re.search(
        r'routers\.whoami\.middlewares\s*=\s*[^\n]*internal-allowlist', compose
    ) is not None
    # ...and must NOT be promoted to a public service.
    all_yml = _read(ANSIBLE / "group_vars" / "all" / "vars.yml")
    pub = re.search(r'(?ms)^public_services:\s*$(.*?)^\S', all_yml + "\nEOF")
    pub_block = pub.group(1) if pub else ""
    not_public = "whoami" not in pub_block
    ok = has_service and has_image and router_allowlist and not_public
    print(
        f"{'OK' if ok else 'FAIL'}: whoami internal-only "
        f"(service={has_service}, image={has_image}, internal-allowlist={router_allowlist}, not_public={not_public})"
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
            # A real token value: 20+ token chars assigned to a CF/tunnel/token key.
            if re.search(
                r'(?i)(cf_dns_api_token|cloudflare[_a-z]*token|tunnel_token)\s*[:=]\s*[A-Za-z0-9_\-]{20,}',
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


def _compose_service_block(body: str, name: str) -> str:
    """A single compose service's body under `services:` (2-space-indented key).

    Scoped to ONE service so per-service assertions (e.g. cloudflared has NO
    `ports:`) don't leak across siblings. Runs to the next 2-space service key,
    a top-level (0-indent) key like `volumes:`, or EOF.
    """
    m = re.search(
        rf'(?ms)^\s{{2}}{re.escape(name)}:\s*$(.*?)(?=^\s{{2}}\S|^\S|\Z)',
        body + "\n  EOF:",
    )
    return m.group(1) if m else ""


def _router_block(body: str, name: str) -> str:
    """A single router's body under `http.routers:` (4-space-indented key).

    Scoped to ONE router so per-router assertions (e.g. plex has NO allowlist)
    don't leak across siblings once the Step-3 `traefik-dashboard` router — which
    DOES carry internal-allowlist — joins the same `routers:` block. Runs to the
    next 4-space router key or the end of the routers section; the column-0 Jinja
    `{% if %}`/`{% endif %}` gate lines are deeper-or-shallower than 4 spaces, so
    they stay inside the owning router's slice.
    """
    routers = _routers_block(body)
    m = re.search(rf'(?ms)^\s{{4}}{re.escape(name)}:\s*$(.*?)(?=^\s{{4}}\S|\Z)', routers)
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
    """Step-9: plex is the ONLY public router — no allowlist (security-critical).

    The plex router carries security-headers but NO allowlist (neither the removed
    lan-allowlist nor the Step-2 internal-allowlist), while the internal whoami router
    carries internal-allowlist (regression guard on the allowlist split). Scoped to the
    plex router's own block (not the whole routers section) because the Step-3
    `traefik-dashboard` router now also lives under `routers:` and DOES carry
    internal-allowlist — a section-wide "allowlist not in routers" would false-fail.
    """
    plex = _router_block(_read(DYNAMIC), "plex")
    plex_no_allowlist = "allowlist" not in plex
    plex_has_headers = "security-headers" in plex
    compose = _read(COMPOSE)
    whoami_allowlist = re.search(
        r'routers\.whoami\.middlewares\s*=\s*[^\n]*internal-allowlist', compose
    ) is not None
    ok = plex_no_allowlist and plex_has_headers and whoami_allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: plex router public (no allowlist), whoami still internal "
        f"(plex_no_allowlist={plex_no_allowlist}, plex_headers={plex_has_headers}, "
        f"whoami_allowlist={whoami_allowlist})"
    )
    return ok


def test_public_services_is_exactly_plex() -> bool:
    """Step-9: group_vars public_services is exactly [plex] — nothing else promoted."""
    all_yml = _read(ANSIBLE / "group_vars" / "all" / "vars.yml")
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
    """Step-10: every extras router carries internal-allowlist + a var-driven resolver.

    Each of the four routers must include the internal-allowlist middleware (Step-2
    migration from lan-allowlist) and select its certresolver from {{ acme_resolver }}
    (NOT a hard-coded le-http/le-dns-cf literal), so the Step-11 DNS-01 flip stays one
    variable and the internal split holds as the stack grows.
    """
    compose = _read(COMPOSE)
    failures = []
    for s in EXTRAS:
        mw = re.search(
            rf'routers\.{re.escape(s)}\.middlewares\s*=\s*[^\n]*internal-allowlist', compose
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
        f"{'OK' if ok else 'FAIL'}: extras routers internal-allowlisted + var-driven resolver "
        f"(failures={failures}, hardcoded={hardcoded})"
    )
    return ok


def test_prometheus_never_public() -> bool:
    """Step-10: prometheus is never public (defense-in-depth, design §6).

    Not in public_services AND its router carries internal-allowlist.
    """
    all_yml = _read(ANSIBLE / "group_vars" / "all" / "vars.yml")
    m = re.search(r'(?ms)^public_services:\s*$(.*?)^\S', all_yml + "\nEOF")
    pub_block = m.group(1) if m else ""
    not_public = "prometheus" not in pub_block
    compose = _read(COMPOSE)
    router_allowlist = re.search(
        r'routers\.prometheus\.middlewares\s*=\s*[^\n]*internal-allowlist', compose
    ) is not None
    ok = not_public and router_allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: prometheus never public "
        f"(not_public={not_public}, router_allowlist={router_allowlist})"
    )
    return ok


def test_homepage_allowed_hosts() -> bool:
    """Step-10: homepage sets HOMEPAGE_ALLOWED_HOSTS=home.{{ domain }}.

    gethomepage/homepage (v0.9.0+) rejects any request whose Host header is not
    localhost and not listed in HOMEPAGE_ALLOWED_HOSTS. Reached ONLY through
    Traefik on Host(`home.{{ domain }}`), so without this env every real
    request hits a "Host validation failed" page and the dashboard never loads.
    """
    compose = _read(COMPOSE)
    m = re.search(r'(?ms)^\s{2}homepage:\s*$(.*?)^\s{2}\S', compose + "\n  EOF:")
    block = m.group(1) if m else ""
    ok = re.search(
        r'HOMEPAGE_ALLOWED_HOSTS\s*=\s*[^\n]*\bhome\.\{\{\s*domain\s*\}\}', block
    ) is not None
    print(f"{'OK' if ok else 'FAIL'}: homepage sets HOMEPAGE_ALLOWED_HOSTS for its proxied host")
    return ok


# Every LAN/Tailscale-only Traefik-routed service. The four monitoring extras
# (design §5 order) plus the Traefik dashboard and the whoami smoke route — all
# internal-allowlisted, none in public_services. Step 8 refreshed the
# documentation-only group_vars list so it no longer omits `traefik`/`whoami`.
INTERNAL_SERVICES = EXTRAS + ["traefik", "whoami"]


def test_internal_services_lists_all_internal() -> bool:
    """Step-8: group_vars internal_services lists every internal service.

    The four monitoring extras (design §5) plus the Traefik dashboard
    (`traefik.{{ domain }}`) and the `whoami` smoke route — the documentation-only
    list must reflect the full internal set so it does not mislead (plan Step 8).
    """
    all_yml = _read(ANSIBLE / "group_vars" / "all" / "vars.yml")
    m = re.search(r'(?ms)^internal_services:\s*$(.*?)^\S', all_yml + "\nEOF")
    block = m.group(1) if m else ""
    entries = re.findall(r'(?m)^\s*-\s*(\S+)', block)
    ok = sorted(entries) == sorted(INTERNAL_SERVICES)
    print(
        f"{'OK' if ok else 'FAIL'}: internal_services lists all internal services "
        f"{sorted(INTERNAL_SERVICES)} (entries={entries})"
    )
    return ok


def test_homepage_monitors_target_internal_urls() -> bool:
    """Step-8: Homepage siteMonitor probes point at internal service URLs.

    Off-tailnet probes to the public dashboard hostnames get a Cloudflare Access
    302 and report false-down; the `siteMonitor` targets in
    `homepage-services.yaml.j2` must instead hit the internal compose-network
    service (http://<service>:<port>), never a public `*.{{ domain }}` host.
    Anchored on the siteMonitor VALUE so the clickable `href` public links (which
    stay public by design) cannot satisfy or redden it; non-vacuous (>=1 probe).
    """
    body = _read(HOMEPAGE_SERVICES)
    monitors = re.findall(r'(?m)^\s*siteMonitor:\s*(\S+)', body)
    internal = re.compile(r'^https?://[a-z0-9][a-z0-9.-]*:\d+')
    non_internal = [
        m
        for m in monitors
        if internal.match(m) is None or re.search(r'\{\{\s*domain\s*\}\}', m)
    ]
    ok = bool(monitors) and not non_internal
    print(
        f"{'OK' if ok else 'FAIL'}: homepage siteMonitor targets are internal "
        f"service URLs (monitors={monitors}, non_internal={non_internal})"
    )
    return ok


def test_cf_token_sourced_from_vault() -> bool:
    """Step-11/Step-4: env.j2 sources both Cloudflare tokens from the vault.

    CF_DNS_API_TOKEN comes from `vault_cloudflare_dns_api_token` (Step-11) and
    TUNNEL_TOKEN from `vault_cloudflare_tunnel_token` (Step-4) — the real
    Ansible-Vault keys (siblings: vault_grafana_admin_password,
    vault_dashboard_basic_auth_hash). The earlier reference
    `cloudflare_dns_api_token` is UNDEFINED, so `default('')` rendered the DNS-01
    token EMPTY — harmless under HTTP-01 but breaks every Cloudflare DNS-01
    challenge once acme_resolver flips to le-dns-cf. This regression guard fails
    on the old text and passes only on the corrected vault keys; TUNNEL_TOKEN
    must likewise be vault-sourced, never a literal.
    """
    body = _read(ENV)
    correct = re.search(
        r'CF_DNS_API_TOKEN\s*=\s*\{\{\s*vault_cloudflare_dns_api_token\b', body
    ) is not None
    # The undefined (vault_-less) reference must be gone.
    buggy = re.search(
        r'CF_DNS_API_TOKEN\s*=\s*\{\{\s*cloudflare_dns_api_token\b', body
    ) is not None
    tunnel = re.search(
        r'TUNNEL_TOKEN\s*=\s*\{\{\s*vault_cloudflare_tunnel_token\b', body
    ) is not None
    ok = correct and not buggy and tunnel
    print(
        f"{'OK' if ok else 'FAIL'}: CF/TUNNEL tokens sourced from vault "
        f"(cf_dns={correct}, buggy_ref={buggy}, tunnel={tunnel})"
    )
    return ok


def test_cloudflared_service_block() -> bool:
    """Step-4: compose defines the outbound `cloudflared` tunnel connector (AC1).

    A `cloudflared` service that (1) pulls the concrete image via the
    `{{ docker_host_cloudflared_image }}` var (not a literal, so bumps stay one
    default), (2) runs `tunnel --no-autoupdate run`, (3) has NO `ports:` (zero
    inbound surface — nothing is reachable before the Step-5 Access gate), and
    (4) `depends_on: traefik` so the connector starts after the proxy. No
    public-hostname ingress is configured here (that is Step 5).
    """
    block = _compose_service_block(_read(COMPOSE), "cloudflared")
    present = bool(block)
    image_var = re.search(
        r'(?m)^\s*image:\s*\{\{\s*docker_host_cloudflared_image\s*\}\}', block
    ) is not None
    command = re.search(r'tunnel\s+--no-autoupdate\s+run', block) is not None
    no_ports = re.search(r'(?m)^\s*ports:\s*$', block) is None
    # depends_on names traefik (list `- traefik` or a `traefik:` condition map).
    depends = re.search(r'(?ms)^\s*depends_on:\s*.*?\btraefik\b', block) is not None
    ok = present and image_var and command and no_ports and depends
    print(
        f"{'OK' if ok else 'FAIL'}: cloudflared service block "
        f"(present={present}, image_var={image_var}, command={command}, "
        f"no_ports={no_ports}, depends_on_traefik={depends})"
    )
    return ok


def test_wildcard_dns01_gated() -> bool:
    """Step-3: the DNS-01 wildcard tls.domains rides the traefik-dashboard router, gated to le-dns-cf.

    Retargeted from the docker `whoami` label (Step-11) to the stable
    `traefik-dashboard` file-provider router in dynamic.yml.j2: proactive wildcard
    issuance must no longer depend on the docker whoami service, closing the
    per-host-cert rate-limit race (design §6). Traefik only requests a wildcard when
    a router declares `tls.domains` (main: {{ domain }}, sans: *.{{ domain }});
    HTTP-01 cannot issue wildcards, so the declaration MUST be gated on
    `acme_resolver == 'le-dns-cf'`. It must be PRESENT on traefik-dashboard and GONE
    from the whoami router (relocation, not duplication — a second wildcard request
    would reintroduce the race). Text-presence here; trim_blocks render suppresses it
    under le-http.
    """
    dash = _router_block(_read(DYNAMIC), "traefik-dashboard")
    gate = re.search(r"\{%\s*if\s+acme_resolver\s*==\s*'le-dns-cf'\s*%\}", dash) is not None
    main = re.search(r'main:\s*"?\{\{\s*domain\s*\}\}', dash) is not None
    sans = re.search(r'sans:.*?\*\.\{\{\s*domain\s*\}\}', dash, re.S) is not None
    # The wildcard must be RELOCATED off the docker whoami router, not duplicated.
    compose = _read(COMPOSE)
    whoami_wildcard_gone = re.search(r'routers\.whoami\.tls\.domains', compose) is None
    ok = gate and main and sans and whoami_wildcard_gone
    print(
        f"{'OK' if ok else 'FAIL'}: wildcard tls.domains on traefik-dashboard, gated to le-dns-cf, off whoami "
        f"(gate={gate}, main={main}, sans={sans}, whoami_gone={whoami_wildcard_gone})"
    )
    return ok


def test_dashboard_insecure_exposure_removed() -> bool:
    """Step-3: the unauthenticated dashboard surface is gone (AC1).

    The insecure `api.insecure` :8080 dashboard is removed on three fronts: no
    `:8080` publish in compose.yml.j2, no `docker_host_traefik_dashboard_port`
    default, and `api.insecure` absent from traefik.yml.j2 while `api.dashboard:
    true` stays (the dashboard is now served only via the routed api@internal
    service behind the traefik-dashboard router).
    """
    compose = _read(COMPOSE)
    defaults = _read(ROLE / "defaults" / "main.yml")
    static = _read(STATIC)
    port_unpublished = re.search(r':8080\b', compose) is None
    port_default_gone = re.search(r'(?m)^\s*docker_host_traefik_dashboard_port\s*:', defaults) is None
    insecure_absent = re.search(r'(?m)^\s*insecure\s*:\s*true', static) is None
    dashboard_on = re.search(r'(?m)^\s*dashboard\s*:\s*true', static) is not None
    ok = port_unpublished and port_default_gone and insecure_absent and dashboard_on
    print(
        f"{'OK' if ok else 'FAIL'}: insecure dashboard removed "
        f"(no_8080={port_unpublished}, no_port_default={port_default_gone}, "
        f"insecure_absent={insecure_absent}, dashboard_on={dashboard_on})"
    )
    return ok


def test_traefik_dashboard_router_present() -> bool:
    """Step-3: dynamic.yml.j2 defines the hardened traefik-dashboard router (AC2).

    A dedicated file-provider router `traefik-dashboard` on Host(`traefik.{{ domain }}`),
    websecure, serving the internal `api@internal` service behind BOTH
    internal-allowlist@file + security-headers@file, with a var-driven certResolver
    (so the Step-11 flip stays one variable). This is the stable anchor the wildcard
    relocates onto.
    """
    dash = _router_block(_read(DYNAMIC), "traefik-dashboard")
    host = re.search(r'Host\(`traefik\.\{\{\s*domain\s*\}\}`\)', dash) is not None
    websecure = re.search(r'(?s)entryPoints:.*?\bwebsecure\b', dash) is not None
    service = re.search(r'(?m)^\s*service:\s*api@internal\s*$', dash) is not None
    allowlist = re.search(r'internal-allowlist@file', dash) is not None
    headers = re.search(r'security-headers@file', dash) is not None
    var_driven = re.search(r'certResolver:\s*"?\{\{\s*acme_resolver\s*\}\}', dash) is not None
    hardcoded = re.search(r'certResolver:\s*"?le-(http|dns-cf)\b', dash) is not None
    ok = host and websecure and service and allowlist and headers and var_driven and not hardcoded
    print(
        f"{'OK' if ok else 'FAIL'}: traefik-dashboard router present "
        f"(host={host}, websecure={websecure}, api_internal={service}, "
        f"allowlist={allowlist}, headers={headers}, var_resolver={var_driven}, hardcoded={hardcoded})"
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
    """Step 1: acme_resolver is le-dns-cf — the sole (DNS-01) resolver.

    group_vars/all/vars.yml selects the DNS-01 wildcard resolver. Templates still
    reference it via {{ acme_resolver }} (covered by test_resolver_is_variable_driven
    and the extras/plex literal-free checks). `le-http` has been removed (Step 1),
    so `le-dns-cf` is the only resolver the templates can name.
    """
    all_yml = _read(ANSIBLE / "group_vars" / "all" / "vars.yml")
    ok = re.search(r'(?m)^acme_resolver:\s*le-dns-cf\s*$', all_yml) is not None
    print(f"{'OK' if ok else 'FAIL'}: group_vars acme_resolver is le-dns-cf (sole DNS-01 resolver)")
    return ok


def test_tunnel_web_routers_present() -> bool:
    """Option-1: every tunneled host has a plain-HTTP (:web) router for cloudflared.

    cloudflared points each public hostname at http://traefik:80 (edge-terminated
    TLS), so every internal host needs a `<svc>-web` router on the `web` entrypoint
    ALONGSIDE its websecure router: the four extras + whoami as docker labels, and
    `traefik-dashboard-web` in the file provider. Each web router must (1) sit on
    the `web` entrypoint, (2) bind the same backend service, (3) keep
    internal-allowlist so a WAN request via the plex :80 port-forward is still
    403'd, and (4) carry NO `tls` (the edge already terminated it; a tls router
    would not answer plain HTTP). Guards against regressing to the SNI /
    network-alias hack that caused the Error-1000 loop.
    """
    compose = _read(COMPOSE)
    dynamic = _read(DYNAMIC)
    failures = []
    for s in EXTRAS + ["whoami"]:
        web_ep = re.search(
            rf'routers\.{re.escape(s)}-web\.entrypoints\s*=\s*web\b', compose
        ) is not None
        svc = re.search(
            rf'routers\.{re.escape(s)}-web\.service\s*=\s*{re.escape(s)}\b', compose
        ) is not None
        allowlist = re.search(
            rf'routers\.{re.escape(s)}-web\.middlewares\s*=\s*[^\n]*internal-allowlist', compose
        ) is not None
        no_tls = re.search(rf'routers\.{re.escape(s)}-web\.tls\b', compose) is None
        if not (web_ep and svc and allowlist and no_tls):
            failures.append(f"{s}(ep={web_ep},svc={svc},allow={allowlist},no_tls={no_tls})")
    # The dashboard's web twin lives in the file provider on the `web` entrypoint.
    dash_web = re.search(
        r'(?ms)^\s{4}traefik-dashboard-web:\s*$.*?entryPoints:\s*.*?\bweb\b', dynamic
    ) is not None
    ok = not failures and dash_web
    print(
        f"{'OK' if ok else 'FAIL'}: tunnel <svc>-web routers present + allowlisted, no tls "
        f"(failures={failures}, traefik_dashboard_web={dash_web})"
    )
    return ok


def main() -> int:
    results = [
        test_role_structure_exists(),
        test_entrypoints_with_redirect(),
        test_both_certresolvers(),
        test_caserver_toggle_wired(),
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
        test_internal_services_lists_all_internal(),
        test_homepage_monitors_target_internal_urls(),
        test_cf_token_sourced_from_vault(),
        test_cloudflared_service_block(),
        test_wildcard_dns01_gated(),
        test_dashboard_insecure_exposure_removed(),
        test_traefik_dashboard_router_present(),
        test_traefik_image_pinned_to_concrete_v3(),
        test_no_floating_service_image_tags(),
        test_acme_resolver_is_dns_cf(),
        test_tunnel_web_routers_present(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
