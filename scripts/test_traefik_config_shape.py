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

Dual-mode (module-level test_*()->bool + main()->int), mirroring
scripts/test_ansible_layout_shape.py (mem-1781891042-4495).

STDLIB PLUS `yaml`, and the qualifier is Step-5a's — this header said "stdlib
only" while it was true and is corrected here rather than left to read as a
promise. `test_blackbox_modules_are_the_three_plex_probes` asks whether a
rendered config PARSES, and no regex answers that question; a document blackbox
refuses to load is a crash loop, not a shape defect. The import is unconditional,
never a `try/except ImportError` skip, which would be the vacuous green this repo
has already paid for twice. It widens nothing: `test_plex_watchdog_unit_shape.py`,
`test_plex_node_exporter_shape.py` and `test_plex_watchdog_deps_shape.py` already
import it the same way, so the gate as a whole has depended on PyYAML since Step
4 — measured present (6.0.3) under BOTH interpreters that can run this file,
`.venv/bin/python` (which is `sys.executable` for `run_gate.py`) and `python3`.

Per mem-1781892715-142d
the regexes anchor on the inner attribute (the actual key/value), not just a
section opener, so an empty stub could not satisfy the check. The real gate is
the standalone exit code.
"""

import ast
import inspect
import itertools
import pathlib
import re
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ANSIBLE = REPO_ROOT / "ansible"
INVENTORY = ANSIBLE / "inventory" / "hosts.yml"
PLEX_ROLE = ANSIBLE / "roles" / "plex"
ROLE = ANSIBLE / "roles" / "docker_host"
TASKS = ROLE / "tasks" / "main.yml"
HANDLERS = ROLE / "handlers" / "main.yml"
TEMPLATES = ROLE / "templates"
COMPOSE = TEMPLATES / "compose.yml.j2"
STATIC = TEMPLATES / "traefik.yml.j2"
DYNAMIC = TEMPLATES / "dynamic.yml.j2"
PROM_SCRAPE = TEMPLATES / "prometheus.yml.j2"
ENV = TEMPLATES / "env.j2"
HOMEPAGE_SERVICES = TEMPLATES / "homepage-services.yaml.j2"
MISE = REPO_ROOT / "mise.toml"


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

    THE PORTS ARE READ THROUGH `_entrypoint_address`, not spanned for — Step-2a F1,
    round 10, and this clause was wrong in BOTH directions the rule names:

    * `address:\\s*"?:80` has no right boundary, so `web` on `:8080` satisfied it
      with no second entrypoint involved. One character, and cloudflared's
      `http://traefik:80` reaches nothing.
    * and the span crossed entrypoints, so a NEW `tunnel` entrypoint on `:80`
      answered for `web` while `web` itself moved to `:9080` — every `<svc>-web`
      router still referencing `web`, i.e. the tunnel's requests arriving on an
      entrypoint no router serves.

    Both were GREEN at 36/36 and both boot on the real `traefik:v3.7.5`, which
    reports `{"web": ":8080"}` and `{"tunnel": ":80", "web": ":9080"}` from
    `/api/entrypoints` (logs/red-step02a-rework-f1-round10.log, B5/B6). The helper
    already existed for the metrics entrypoint and returns the HOST as well, so the
    bind is pinned to a peer-reachable one here for the reason the buckets clause
    states: an address has more than one field and each moves the endpoint out from
    under its caller on its own.

    AND THE OTHER PIN WAS INHERITED — Step-2a F1, round 11. Round 10 rebuilt the
    PORT half of this clause and left `plex_web_redirect` spelled
    `(?ms)^\\s{4}plex-web:\\s*$.*?redirect-to-https`: anchored on the router's NAME
    and bounded by NOTHING, so it ran to the end of the file. Every B5/B6 row
    printed `plex_web_redirect=True` and nobody asked what answered it. Two carriers
    measured, both leaving this field byte-identical to the honest tree's at guard
    PASS 36/36 (logs/red-step02a-rework-f1-round11.log, A1/A2): a documentation
    COMMENT on the NEXT router, and an ordinary sibling `apex-web` router that is
    correct in itself. The real traefik:v3.7.5 then loads
    `plex-web.mw=['security-headers@file']` and answers `GET http://plex.<domain>/`
    on :80 with **502 — it PROXIED the plain-HTTP request** where the delivered tree
    answers **301 -> https**. With no carrier the row is RED (A3), so green-vs-red
    was purely whether a neighbour held the string. A rewritten pin is exactly when
    the clause's OTHER pins get inherited.
    """
    static = _read(STATIC)
    dynamic = _read(DYNAMIC)
    web_host, web_port = _entrypoint_address(static, "web")
    ws_host, ws_port = _entrypoint_address(static, "websecure")
    web = web_port == "80" and web_host in PEER_REACHABLE_HOSTS
    websecure = ws_port == "443" and ws_host in PEER_REACHABLE_HOSTS
    # The loop-causer: an entrypoint-level `redirections:` block must be gone.
    # Decommented (round 12): this is an ABSENCE pin over the raw file, and the
    # comment four lines above the `web` entrypoint in traefik.yml.j2 exists to say
    # that there is deliberately no redirect here — one edit away from naming
    # `redirections:` and reddening a correct tree (leg D, row D1).
    no_ep_redirect = re.search(r'redirections:', _strip_comments(static)) is None
    # The upgrade relocated onto the public plex-web file-provider router — read
    # from THAT router's OWN middlewares list. `@file` is stripped because the
    # provider suffix is optional in a file-provider reference and both spellings
    # load the same middleware; this is `dash_web` in
    # `test_tunnel_web_routers_present`, one clause over.
    plex_web_redirect = any(
        v.split("@")[0] == "redirect-to-https"
        for v in _param_values(_router_block(dynamic, "plex-web"), "middlewares")
    )
    ok = web and websecure and no_ep_redirect and plex_web_redirect
    print(
        f"{'OK' if ok else 'FAIL'}: web(:80 plain)/websecure(:443), no entrypoint redirect, "
        f"plex-web upgrade (web={web} ({web_host!r}:{web_port}), "
        f"websecure={websecure} ({ws_host!r}:{ws_port}), "
        f"no_ep_redirect={no_ep_redirect}, plex_web_redirect={plex_web_redirect})"
    )
    return ok


def test_both_certresolvers() -> bool:
    """Step 1: exactly one ACME certresolver — Cloudflare DNS-01 (`le-dns-cf`).

    Function name retained for acceptance traceability (task-01 §Acceptance-3);
    the assertion is retargeted to the post-migration invariant. The old
    HTTP-01 `le-http` resolver is REMOVED — only DNS-01 can issue the
    `*.{{ domain }}` wildcard, so `le-dns-cf` must be the sole resolver.

    "SOLE" IS NOW PINNED AS AN ENUMERATION, not as one name's absence (Step-2a F1,
    round 10). `le_http` is a claim about `le-http`; the sentence above is a claim
    about every key under `certificatesResolvers:`, and the gap between the two is
    where the round-10 decoy lived — a second resolver, legitimately shaped and
    named for a cutover, answering `caServer` for the clause below while the ACTIVE
    resolver was pinned to LE staging. So the resolver names are READ, through the
    same derive-the-column allow-list the compose services use, and any key that is
    not `le-dns-cf` — or any line at that column this guard cannot read — reddens.
    Both pins stay: the enumeration is the general claim, `le_http` is the named
    regression with three rounds of spelling behind it, and the `dnsChallenge` span
    is now inside ONE resolver's own block.
    """
    body = _read(STATIC)
    dns = re.search(
        r'(?s)acme:.*?dnsChallenge:.*?provider:\s*cloudflare', _resolver_block(body, "le-dns-cf")
    ) is not None
    resolvers, unreadable = _service_key_lines(_resolvers_block(body))
    sole = resolvers == ["le-dns-cf"] and not unreadable
    # `le-http:` as a YAML resolver key must be gone, in ANY spelling (comment
    # mentions and sequence entries still can't match — see `_declares_key`). The
    # `^\s*le-http:\s*$` this replaces was blind to `le-http: {acme: {...}}`,
    # which is a whole second resolver on one line and the exact state the
    # "sole resolver" claim forbids. Round 6: it is ALSO gone if the file holds
    # any line this guard cannot read, because a second resolver can arrive as an
    # explicit-key or merge-key pair — measured, `? le-http` renders to
    # `certificatesResolvers: ['le-dns-cf', 'le-http']` inside the very check
    # that calls `le-dns-cf` the sole one.
    le_http = _declares_key(body, r'le-http')
    http_gone = not le_http
    ok = dns and http_gone and sole
    print(
        f"{'OK' if ok else 'FAIL'}: single DNS-01 certresolver le-dns-cf "
        f"(cf-dns01={dns}, le-http_gone={http_gone} (found={le_http}), "
        f"sole={sole} (resolvers={resolvers}, unreadable={unreadable}))"
    )
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
    # Asked of the ACTIVE resolver's OWN block — Step-2a F1, round 10. The span
    # this replaces started at the resolver's NAME and ran to the end of the file,
    # so a second resolver answered for the toggle while `le-dns-cf` itself carried
    # `caServer: https://acme-staging-v02…` — every public host serving a
    # browser-untrusted cert, at guard PASS 36/36, on a config the real
    # traefik:v3.7.5 boots (logs/red-step02a-rework-f1-round10.log, B7). `sole` in
    # the clause above closes the second-resolver door too; both are kept, because
    # "the toggle is on the resolver the routers use" is this clause's own claim and
    # should not depend on another clause's enumeration to be true.
    caserver = re.search(
        r'(?s)acme:.*?caServer:\s*"?\{\{\s*acme_ca_server\s*\}\}',
        _resolver_block(static, "le-dns-cf"),
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
    """Step 1: the whoami router's resolver comes from `acme_resolver`, not a literal.

    Step-2a F1, round 12, and this clause was NOT on the review's list of eleven —
    my own post-fix run found it, which is round 11's rule (1) arriving one clause
    further along: fixing the pins that WERE named reddened this one, because a
    comment recording the pre-Step-11 `certresolver=le-http` value is a FALSE RED
    here too (row A10). Both of its pins were raw whole-file searches over an
    un-comment-stripped `compose.yml.j2`, so both halves were wrong:

    * PRESENCE (`var_driven`) is a claim about the WHOAMI router — the module
      docstring says so — and it was answered by `certresolver=` text anywhere in
      the file, including a comment and including another service's label. It now
      reads whoami's own labels, like the other ten pins of this class.
    * ABSENCE (`hardcoded`) is a claim about the whole document — a literal is a
      literal wherever its label sits — so it stays document-wide and is only
      decommented.
    """
    body = _read(COMPOSE)
    # The active resolver on the whoami router is selected from acme_resolver,
    # not a hard-coded `certresolver=le-http` literal. Asked of the EFFECTIVE
    # value of that one label key (round 13's F2): existential over the entries,
    # the FIRST of two `certresolver=` lines answered for the LAST one, which is
    # the value docker keeps — and a trailing `# was:` comment answered for a
    # deleted line (round 13's F1). Both were PASS 36/36 (rows D3, R6).
    var_driven = re.fullmatch(
        r'\{\{\s*acme_resolver\s*\}\}',
        _service_label_map(body, "whoami").get(
            "traefik.http.routers.whoami.tls.certresolver", ""
        ),
    ) is not None
    hardcoded = re.search(
        r'certresolver\s*=\s*le-(http|dns-cf)\b', _strip_comments(body)
    ) is not None
    ok = var_driven and not hardcoded
    print(f"{'OK' if ok else 'FAIL'}: router resolver is variable-driven (var={var_driven}, hardcoded={hardcoded})")
    return ok


def test_middlewares_defined() -> bool:
    """The three shared middlewares exist AND each carries its own spec.

    Step-2a F1, round 10: each pin is asked of the named middleware's OWN block.
    The spans this replaces started at a middleware's NAME and ran on, so a sibling
    answered — a half-finished rename left `redirect-to-https` (the middleware the
    ONE public plain-HTTP router references) as a header-setter with no redirect at
    all, while an `upgrade-to-https` twin answered the pin. GREEN at 36/36, and the
    real traefik:v3.7.5 loads `redirect-to-https` with `["headers"]`
    (logs/red-step02a-rework-f1-round10.log, B4).
    """
    body = _read(DYNAMIC)
    redirect = re.search(
        r'(?m)^\s*redirectScheme:\s*$', _middleware_block(body, "redirect-to-https")
    ) is not None
    headers = re.search(
        r'(?m)^\s*headers:\s*$', _middleware_block(body, "security-headers")
    ) is not None
    allowlist = re.search(
        r'(?m)^\s*ipAllowList:\s*$', _middleware_block(body, "internal-allowlist")
    ) is not None
    ok = redirect and headers and allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: middlewares defined "
        f"(redirect-to-https={redirect}, security-headers={headers}, internal-allowlist={allowlist})"
    )
    return ok


# The ranges `internal-allowlist` admits: the LAN /24, Tailscale's CGNAT v4 range,
# Tailscale's ULA v6 prefix, and the broad Docker private range that admits the
# Step-4 cloudflared hop without pinning a compose subnet. Hoisted out of the regex
# it used to be spelled in (Step-2a F1, round 10) — same four values, read as a set.
INTERNAL_SOURCE_RANGES = [
    "192.168.1.0/24",
    "100.64.0.0/10",
    "fd7a:115c:a1e0::/48",
    "172.16.0.0/12",
]

# The middleware reference every internal DOCKER-provider router must carry, in
# one place because it is now pinned as an exact member of the effective
# `middlewares` value rather than as a substring of a label line (round 13's F2).
# The `@file` suffix is load-bearing and not decoration: the middleware is defined
# in dynamic.yml.j2, so without the provider suffix traefik looks it up in the
# DOCKER provider's own namespace, where no such middleware exists, and the
# reference does not resolve at all. The round-12 review called that spelling a
# disclosed LOOSENESS of the old substring pin; naming the reference closes it
# (row P6, now RED by design).
INTERNAL_ALLOWLIST_REF = "internal-allowlist@file"


def test_lan_allowlist_source_ranges() -> bool:
    """`internal-allowlist` admits EXACTLY the four internal ranges.

    Name kept for acceptance traceability (Step-2 retarget): the allowlist is now
    `internal-allowlist` and must carry the LAN /24, the Tailscale CGNAT v4 range,
    the Tailscale ULA v6 prefix, and the broad Docker private range that admits the
    Step-4 cloudflared hop without pinning a subnet.

    Step-2a F1, round 10 — the ranges are READ from that middleware's own
    `sourceRange:` list instead of chained through it with `.*?`, and two things
    change with them:

    * the chain crossed the middleware's boundary, so moving two of the four to a
      second, legitimately-shaped middleware that no router references left this
      GREEN at 36/36 while the allowlist every internal router DOES carry stopped
      admitting Tailscale v6 and the cloudflared Docker hop — i.e. the tunnel 403s.
      Confirmed on the real traefik:v3.7.5, which loads both middlewares
      (logs/red-step02a-rework-f1-round10.log, B3).
    * the chain also demanded the four in FILE ORDER, which is not part of the
      claim: `ipAllowList.sourceRange` is a set and Traefik does not care. A
      re-sort was a false RED.

    EXACTLY, and that is stricter than "carries" on purpose — `sorted(...) ==`, the
    same shape `test_public_services_is_exactly_plex` uses, because this is the one
    middleware standing between the WAN and every internal router: an ADDED range
    widens it, and `0.0.0.0/0` here would defeat it silently. A legitimate new range
    is a two-line edit (here and there), which is what a pin on a security boundary
    is for.
    """
    body = _read(DYNAMIC)
    ranges = _param_values(
        _indented_block(_middleware_block(body, "internal-allowlist"), "ipAllowList"),
        "sourceRange",
    )
    ok = sorted(ranges) == sorted(INTERNAL_SOURCE_RANGES)
    print(
        f"{'OK' if ok else 'FAIL'}: internal-allowlist admits exactly "
        f"{INTERNAL_SOURCE_RANGES} (found={ranges}, "
        f"missing={[r for r in INTERNAL_SOURCE_RANGES if r not in ranges]}, "
        f"extra={[r for r in ranges if r not in INTERNAL_SOURCE_RANGES]})"
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
    # Asked of the EFFECTIVE value of that label key on the whoami service's OWN
    # labels: `_service_labels` scopes it to the service (round 12) and
    # `_service_label_map` takes the value docker actually resolves — last wins,
    # trailing comment cut (round 13). A label on a sibling service, a trailing
    # `# was:` carrier and a duplicated allowlist-less line were each PASS 36/36.
    router_allowlist = INTERNAL_ALLOWLIST_REF in _label_members(
        _service_label_map(compose, "whoami").get(
            "traefik.http.routers.whoami.middlewares", ""
        )
    )
    # ...and must NOT be promoted to a public service. Asked of the list's parsed
    # ENTRIES, not of the block's raw text — `_top_level_list` (round 11).
    all_yml = _read(ANSIBLE / "group_vars" / "all" / "vars.yml")
    pub = _top_level_list(all_yml, "public_services")
    not_public = pub is not None and "whoami" not in pub
    ok = has_service and has_image and router_allowlist and not_public
    print(
        f"{'OK' if ok else 'FAIL'}: whoami internal-only "
        f"(service={has_service}, image={has_image}, internal-allowlist={router_allowlist}, "
        f"not_public={not_public} (public_services={pub}))"
    )
    return ok


def test_tasks_idempotent_builtin_only() -> bool:
    """No unguarded command/shell/raw and no community.* collections (AC3).

    Reuses the Step-4 guard scan: every FQCN command/shell/raw module task must
    sit near a changed_when/creates/removes/when guard.

    Step-2a F1, round 13 — the scan is DECOMMENTED, and this clause is here
    because a sweep found it, not because a review asked for it (leg F). The
    window is 600 characters of the file and the guard pattern
    `changed_when|creates|removes|when\\s*:` is UNANCHORED, so a comment inside
    the window naming any of those four words answered for an
    `ansible.builtin.command` with no guard at all — this round's carrier class,
    one clause over from the label pins, and this file's comments are long and
    right above the tasks they describe (tasks/main.yml:187-196). Measured both
    directions in logs/red-step02a-rework-f1-round13b.log, leg G.

    Disclosed price, because it is a real one: with comments off the window
    reaches FURTHER into live task lines, so a guard on a NEIGHBOURING task can
    answer where a comment used to pad the distance. That crudeness belongs to
    the inherited 600-character heuristic and is unchanged in kind; a comment
    that satisfies the pin is a defect, so the trade is taken rather than left.
    """
    body = _read(TASKS)
    if not body:
        print("FAIL: docker_host tasks idempotent (tasks/main.yml missing)")
        return False
    scan = _strip_comments(body)
    unguarded = []
    for m in re.finditer(r'(?m)^\s*ansible\.builtin\.(command|shell|raw)\s*:', scan):
        window = scan[m.start():m.start() + 600]
        if not re.search(r'changed_when|creates|removes|when\s*:', window):
            unguarded.append(m.group(1))
    community = re.search(r'(?m)^\s*community\.', scan) is not None
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


def _key_bounded_block(body: str, name: str, indent: int) -> str:
    """The body of the mapping key `name` at column `indent`, bounded by KEYS.

    THE BOUNDARY RULE, IN ONE PLACE. Step-2a F1, round 7. Round 6 made the line
    CLASSIFIER fail closed — every line at a service's own key column must be a
    key `_yaml_key` can read, or `unreadable` reddens the clause — and it is
    correct and complete for the lines it is GIVEN. The two slicers that decided
    WHICH lines it was given still failed SILENT: they ended a block at the next
    non-space GLYPH (`(?=^\\s{2}\\S|^\\S|\\Z)` for a service,
    `(?=^\\s{4}\\S|\\Z)` for a router). Two line shapes match such a lookahead,
    carry no YAML key, and end no node at runtime:

    * a whole-line COMMENT at or shallower than the block's own column. This is
      not exotic — it is these templates' own idiom: compose.yml.j2 comments its
      service groups at 2 spaces (lines 25, 72, 175, 199) while bodies use 4, and
      dynamic.yml.j2 comments its routers at 4 (lines 53, 66, 91) while bodies
      use 6. One misindent puts a body line behind one.
    * a column-0 Jinja control line (`{% if … %}`), this repo's live idiom for
      gated config (dynamic.yml.j2:84-89). Gating a service key behind a variable
      is the single most likely next edit to compose.yml.j2.

    Everything after such a line was outside the block, so every clause built on
    it — the reachability allow-lists, `no_ports`, "plex carries no allowlist" —
    was answering about a document it had stopped reading. And the truncation was
    SILENT: a bare 2-space comment with nothing after it printed the IDENTICAL
    key field as the honest tree, so no output said "I stopped here". Six states
    measured GREEN at 36/36 (logs/red-step02a-rework-f1-round7.log), every one
    rendering, `yaml.safe_load`ing with the forbidden key on the REAL service and
    passing `docker compose config` with rc=0, i.e. states `just play` SHIPS
    (logs/calibration-step02a-f1-round7.log, legs A and A').

    So the boundary is decided by a line the parser can READ AS A KEY, never by a
    glyph, and comments are stripped BEFORE slicing rather than by each caller
    afterwards. Two consequences worth stating:

    * anything else — a comment, a Jinja tag, a merge key, a construct nobody has
      thought of — stays INSIDE the block and is judged by `_line_class`, which
      already fails closed on it. The slicer no longer has an opinion about what
      it cannot read; it just refuses to end a block on it.
    * this fails CLOSED where it is wrong. If some future line really does end a
      node without being a readable key, the block over-runs into the sibling and
      the extra lines land in `unreadable` — a false RED, which is the direction
      a security pin should fail in.

    Measured free before it was prescribed: across all ten compose services and
    all five routers in the delivered tree the new blocks carry byte-identical
    content to the old ones and introduce ZERO unreadable lines
    (logs/calibration-step02a-f1-round7.log, leg B).
    """
    lines = _strip_comments(body).splitlines()
    started, out = False, []
    for line in lines:
        parsed = _yaml_key(line) if _line_class(line) == "key" else None
        if not started:
            started = bool(parsed) and parsed[0] == indent and parsed[1] == name and not parsed[2]
            continue
        if parsed and parsed[0] <= indent:
            break
        out.append(line)
    return "\n".join(out) + "\n" if started else ""


# --- THE ANCHOR RULE, IN ONE PLACE (Step-2a F1, round 8) ----------------------
#
# `_key_bounded_block` decides where a block ENDS. It says nothing about where one
# STARTS, and round 7 shipped with every caller handing it a whole document and
# taking the first key of that name ANYWHERE in it. A block is only the node its
# clause is talking about if it was reached by a PATH from the document root, so
# every slicer below names its parents and the column each one sits at, and the
# path is walked with the same key-bounded helper at every hop.
#
# Round 7 fixed a boundary that failed SILENT; this is the same defect on the
# other edge, and it is silent in the same way. A decoy block of the right shape
# earlier in the document leaves the clause printing a field BYTE-IDENTICAL to the
# honest tree's, so no output says "I read the wrong node"
# (logs/red-step02a-rework-f1-round8.log, R1/R3/R5).
#
# It fails CLOSED where it is wrong, like the boundary: an anchor that does not
# resolve returns "", `present` goes False and the clause reddens — it does not
# fall back to searching wider.
#
# Step-2a F1, round 9 completes the rule in the two ways round 8 shipped it
# incomplete. Round 8 wrote this header as a claim about the WHOLE file and then
# applied it only to the slicers the review had named; four slicers below it named
# no parent, and `_scrape_job_block` — the one this step's headline check is built
# on — took the first `- job_name:` at ANY indent and did not strip comments, so a
# `global.external_labels` block scalar of the job shape BECAME the job. So:
#
#   1. THE SWEEP IS THE RULE. Every slicer in this file, not only the ones a review
#      pointed at. `_scrape_job_block` now walks `scrape_configs:` at column 0;
#      `_indented_block` is region-relative BY CONSTRUCTION and its parent is the
#      region its caller passes, which is now said out loud in its docstring rather
#      than left to be inferred; `_render_task_block` and `_handler_block` anchor on
#      a column-0 list entry in the document root, which was already true and is now
#      stated and pinned. `_metrics_prometheus_block` and `_entrypoint_address`
#      anchor at column 0 from the root already.
#
#   2. AN ANCHOR THAT RESOLVES TO TWO NODES HAS NOT RESOLVED. The path answers
#      "which parent"; it does not answer "which of the siblings", and a Jinja
#      `{% if %}/{% else %}` either-or pair of the SAME job lives INSIDE
#      `scrape_configs`, where no path reaches it. The first branch answered while
#      the second one rendered (logs/red-step02a-rework-f1-round9.log, R4:
#      `promtool check config` rc=0 and Prometheus loads `metrics_path=None`).
#      Compose's equivalent is already closed by round 6's derive-the-column pin;
#      prometheus.yml.j2's was not. A name that resolves more than once now returns
#      "" — the same fail-closed direction an unresolved anchor already takes, and
#      for the same reason: the guard cannot know which node the clause means.
#
#      Measured free before it was prescribed (logs/calibration-step02a-f1-round9.log,
#      leg B): on the delivered tree all five scrape jobs, every `_indented_block`
#      call site, all ten compose services' `volumes:`/`command:`, all nine render
#      `src:`s and both handler names resolve exactly ONCE.
#
#   3. WHERE THE CLAIM IS UNIVERSAL, READ ALL THE SIBLINGS INSTEAD. Failing closed
#      is wrong for `targets:`, because a list of `static_configs` entries is
#      ordinary Prometheus config and the clause's claim is about EVERY target, not
#      about one. See `_indented_blocks` and `test_pve_scrape_job_is_multi_target`.
#
# Step-2a F1, round 10: THE RULE IS ABOUT SIBLINGS, NOT ABOUT SLICERS.
#
#   4. A `(?ms) … .*? …` SPAN IS AN UNSCOPED ANCHOR WEARING A DIFFERENT HAT. Round 9
#      swept every slicer and asked (3) of `static_configs`/`targets:` — and never
#      asked it of the OTHER list in the same clause. `.*?` does not care which
#      sibling each half of a claim came from, nor whether the second half is past
#      the region's own end, so a per-entity claim spelled that way is satisfiable
#      by a NEIGHBOUR. That is not one clause's bug: twelve deployable rows were
#      GREEN through the round-9 guard in EIGHT clauses across all four templates
#      (logs/red-step02a-rework-f1-round10.log), and each was confirmed on the real
#      server rather than at the parse — Prometheus building
#      `?target=pve-exporter%3A9221` from a relabel list whose two halves came from
#      different entries; Traefik loading the unauthenticated `api@internal` on the
#      ONE public router because `plex-web` answered for `service: plex` and
#      `traefik-dashboard` for `websecure`; the `web` entrypoint on `:9080` with a
#      sibling entrypoint answering for `:80`; the ACTIVE ACME resolver pinned to LE
#      STAGING with a second resolver answering for the prod toggle.
#
#      So a per-ENTITY claim is asked of ONE entity, through the same key-bounded
#      path as every other anchor: `_list_entries` slices a YAML list into its
#      entries (a mapping entry is multi-line, so `_param_values` cannot do it),
#      `_middleware_block` and `_resolver_block` complete the two anchor paths this
#      file was missing, and each clause asks its EXISTING pins of one node. Where
#      the claim is universal it still reads them all, per (3) — `hardcoded` in
#      `test_plex_public_router_present` stays section-wide because "no router
#      hard-codes a resolver" quantifies over the lot.
#
#      And an ORDER claim is answered by comparing the two entries' INDICES. Round
#      9's headline docstring already said "carries `__param_target` FROM
#      `__address__` and THEN replaces `__address__`"; once the halves are located
#      per entry, "then" costs one comparison and stops being a claim the code did
#      not check (Prometheus applies relabel rules in order, so the swap makes the
#      exporter be asked about ITSELF).
#
# Step-2a F1, round 11: THE SWEEP IS TWO GREPS, AND A CLAUSE'S OTHER PINS GET
# INHERITED.
#
#   5. A CLAUSE THAT ROLLS ITS OWN SLICER IS INVISIBLE TO A SWEEP OF THE HELPERS.
#      Round 10 wrote (4) here as a claim about this FILE and prescribed the search
#      that finds violations of it. Run against the delivered tree that search left
#      hits, and every one of them was hand-rolled: `test_homepage_allowed_hosts`
#      inlined `(?ms)^\s{2}homepage:\s*$(.*?)^\s{2}\S` and broke three settled rules
#      in one line — a GLYPH boundary (round 7), no `services:` anchor (round 8), no
#      `_strip_comments` (round 10's own carrier) — while calling no helper, so no
#      sweep had opened it. The four readers of `group_vars/all/vars.yml` were the
#      same line one file over. So the sweep is TWO greps: for `.*?` and `(?s)`, AND
#      for the SHAPE of a slicer — a `(.*?)` capture bounded by a glyph, a lookahead
#      on `^\s{N}\S`, a hand-walked `splitlines()`. `_compose_service_block` and
#      `_top_level_list` are what those hits became; neither is new machinery.
#
#   6. AND A HAND-ROLLED SLICER COSTS IN BOTH DIRECTIONS, so the rows that price a
#      fix are the same rows that find it. Comment-truncation makes a PRESENCE pin
#      redden on a tree the runtime resolves perfectly (a 2-space comment inside the
#      homepage service; a column-0 comment inside `internal_services:`) and makes
#      an ABSENCE pin — `"prometheus" not in pub_block` — TRUE about a list that
#      holds it. An absence pin over raw text is the fail-open half of this, and it
#      is why the two `not_public` pins now ask the parsed ENTRIES and treat
#      "cannot read the list" as RED (logs/red-step02a-rework-f1-round11.log,
#      A4/A6/B1/B2/B4).
#
#   7. A ROUND THAT REWRITES ONE PIN IS EXACTLY WHEN THE CLAUSE'S OTHERS GET
#      INHERITED. Round 10 rebuilt `test_entrypoints_with_redirect` around
#      `_entrypoint_address` for the PORT half and left `plex_web_redirect` as a
#      span anchored on a router NAME and bounded by nothing — printing
#      `plex_web_redirect=True` in every one of its own B5/B6 rows. Same for the
#      `websecure` pin: rewritten in `test_plex_public_router_present`, left
#      spelled `(?s)entryPoints:.*?\bwebsecure\b` one clause down in
#      `test_traefik_dashboard_router_present`. A clause with N pins is fixed when
#      all N are, and two spellings of one pin in one file is how round 5's
#      `_yaml_key` blind spot got inherited into `_declares_key`.


def _compose_services_block(body: str) -> str:
    """compose.yml.j2's top-level `services:` mapping — the anchor for a service.

    A compose file's top level also holds `volumes:`, `networks:`, `configs:` and
    — the one that matters here — any number of `x-` EXTENSION FIELDS, which the
    spec sanctions and the runtime IGNORES entirely. Anything under those is not
    a service and must not be able to answer for one.
    """
    return _key_bounded_block(body, "services", 0)


def _compose_service_block(body: str, name: str) -> str:
    """A single compose service's body under `services:` (2-space-indented key).

    Scoped to ONE service so per-service assertions (e.g. cloudflared has NO
    `ports:`) don't leak across siblings. Runs to the next key at 2 spaces or
    shallower — the next service, or the end of `services:` — see
    `_key_bounded_block` for why the boundary is a KEY and not a glyph.

    Step-2a F1, round 8: the `services:` hop is the fix, and it is round 7's own
    helper applied one level up rather than any new machinery. Without it this
    took the first 2-space key called `name` anywhere in the document, so a
    top-level `x-pve-exporter-doc:` holding a decoy `pve-exporter:` BECAME the
    service and the real one under `services:` was never read. Measured on the
    delivered tree: `ports: ["9221:9221"]` on the REAL service reddens this
    clause with no decoy present and goes GREEN at 36/36 with one, printing
    `keys_allowed=True (keys=['image','restart','environment','command'],
    unexpected=[], unreadable=[]), no_ports=True (published=None)` — the honest
    tree's field, verbatim — while the artifact renders, `yaml.safe_load`s with
    `ports` on the REAL service and `docker compose config` resolves
    `published: '9221'` (logs/calibration-step02a-f1-round8.log, leg A). The
    whole gate said `PASS: 35/35` over that tree.

    The decoy is a state `just play` ships, which is what separates it from the
    other way to shadow a service: an ordinary DUPLICATE `pve-exporter:` key
    under `services:` fools the unscoped anchor identically, but compose-go
    rejects the file outright (`mapping key "pve-exporter" already defined`,
    rc=1), so it never reaches a host. The `x-` field is the deployable form and
    the reason this is a hole rather than a curiosity (leg C).

    Measured free before it was prescribed: across the delivered tree every
    service block is byte-identical under the scoped anchor, and the three
    `*-data` keys under top-level `volumes:` correctly stop resolving as
    "services" — no clause slices those (leg B).
    """
    return _key_bounded_block(_compose_services_block(body), name, 2)


def _http_block(body: str) -> str:
    """dynamic.yml.j2's top-level `http:` mapping — the anchor for a router.

    Traefik's dynamic schema repeats `routers:` and `services:` under `tcp:` and
    `udp:` as well as `http:`, so a bare "first `routers:` at any indent" reads
    whichever section comes first in the file. That is not hypothetical config:
    a `tcp:` section is how one would route a raw TLS passthrough, and it is one
    edit away from this file.
    """
    return _key_bounded_block(body, "http", 0)


def _routers_block(body: str) -> str:
    """The `http.routers:` section of dynamic.yml.j2.

    Step-2a F1, round 8. The review named the unscoped `routers:` anchor without
    asking for it, so it was MEASURED rather than assumed
    (logs/red-step02a-rework-f1-round8.log), and it turned out to cost on BOTH
    sides — which is why it is fixed here with the compose anchor rather than
    left for a later round:

    * a legitimate `tcp:` section carrying nothing forbidden at all is a FALSE
      RED today — three presence clauses (`plex public router present`, the
      wildcard `tls.domains` gate, `traefik-dashboard router present`) redden on
      a tree that is entirely correct, because they are reading the TCP section.
    * and in the same state `test_plex_router_is_public_not_allowlisted` prints
      `plex_no_allowlist=True` while the rendered artifact really does carry
      `internal-allowlist@file` on plex — i.e. the ONE public router silently off
      the WAN, inside the clause that exists to prevent exactly that.

    The gate does fail closed on that pair (3/36), so it was never a shipping
    hole and the review was right not to demand it. It is fixed because the
    ANCHOR rule, like the boundary rule DEC-041 settled, is worth having in one
    place: two anchor conventions in one file is how round 5's `_yaml_key` blind
    spot got inherited into `_declares_key`. DEC-043.
    """
    return _key_bounded_block(_http_block(body), "routers", 2)


def _services_block(body: str) -> str:
    """The `http.services:` section of dynamic.yml.j2.

    Same anchor path as `_routers_block`, and deliberately so: `tcp.services:`
    holds `address:` backends rather than `url:` ones, so an unscoped anchor
    would have `test_plex_service_backend_32400` answering about a different
    node type entirely.
    """
    return _key_bounded_block(_http_block(body), "services", 2)


def _middlewares_block(body: str) -> str:
    """The `http.middlewares:` section of dynamic.yml.j2.

    Step-2a F1, round 10, and the same anchor path as `_routers_block` for the same
    reason: Traefik's dynamic schema repeats `middlewares:` under `tcp:` as well as
    `http:`, and a `tcp.middlewares:` entry is an `ipAllowList` too — so an
    unscoped anchor has the LAN allowlist clause answering about a middleware no
    HTTP router can reference.
    """
    return _key_bounded_block(_http_block(body), "middlewares", 2)


def _middleware_block(body: str, name: str) -> str:
    """One middleware's body under `http.middlewares:` (4-space-indented key).

    The missing hop. `test_middlewares_defined` and
    `test_lan_allowlist_source_ranges` both spanned from a middleware's NAME with
    `.*?` and neither stopped at its body, so a sibling answered for it: a
    half-finished rename left the middleware the public `plex-web` router
    references as a header-setter with no `redirectScheme` at all while a renamed
    twin answered the pin, and two of the four source ranges moved to a middleware
    no router references while the four-range chain still matched across the
    boundary. Both measured on the real `traefik:v3.7.5`, which loads
    `redirect-to-https` with `["headers"]` and no redirect
    (logs/red-step02a-rework-f1-round10.log, B4/B3).
    """
    return _key_bounded_block(_middlewares_block(body), name, 4)


def _dynamic_service_block(body: str, name: str) -> str:
    """One file-provider service's body under `http.services:` (4-space key).

    Step-2a F1, round 10: `test_plex_service_backend_32400` asked `plex:` of the
    services SECTION and the backend URL of the section too, so a second service
    answered for the first — Traefik loading
    `plex -> http://127.0.0.1:32400` (traefik's own loopback, a 502 for the one
    public host) while a `plex-direct` service carried the honest URL
    (logs/red-step02a-rework-f1-round10.log, B2).
    """
    return _key_bounded_block(_services_block(body), name, 4)


def _resolvers_block(body: str) -> str:
    """traefik.yml.j2's top-level `certificatesResolvers:` mapping."""
    return _key_bounded_block(body, "certificatesResolvers", 0)


def _resolver_block(body: str, name: str) -> str:
    """One ACME resolver's body under `certificatesResolvers:` (2-space key).

    Step-2a F1, round 10. `test_caserver_toggle_wired` spanned
    `le-dns-cf:.*?acme:.*?caServer: {{ acme_ca_server }}` over the whole static
    file, so a SECOND resolver answered for the toggle while the ACTIVE one — the
    one every router selects through `acme_resolver` — was pinned to
    `acme-staging-v02`: every public host serving a browser-untrusted cert, at
    guard PASS 36/36, on a file the real traefik boots
    (logs/red-step02a-rework-f1-round10.log, B7). The clause's own docstring
    promised "a regression back to `acme-staging-v02` reddens".
    """
    return _key_bounded_block(_resolvers_block(body), name, 2)


def _router_block(body: str, name: str) -> str:
    """A single router's body under `http.routers:` (4-space-indented key).

    Scoped to ONE router so per-router assertions (e.g. plex has NO allowlist)
    don't leak across siblings once the Step-3 `traefik-dashboard` router — which
    DOES carry internal-allowlist — joins the same `routers:` block. Runs to the
    next key at 4 spaces or shallower, or the end of the routers section; the
    column-0 Jinja `{% if %}`/`{% endif %}` gate lines are not keys, so they stay
    inside the owning router's slice.

    Same boundary helper as `_compose_service_block`, and deliberately so: round
    7's finding was raised against the service slicer, but `_router_block` ended
    a router on the same glyph, and a 4-space comment is dynamic.yml.j2's own
    router-level comment idiom. Measured, not assumed — with the old boundary an
    allowlist entry behind such a comment leaves `test_plex_router_is_public_not_
    allowlisted` GREEN while the rendered artifact really does allowlist the ONE
    public router, i.e. plex goes unreachable from the WAN
    (logs/calibration-step02a-f1-round7.log, leg A'). Fixing the rule once is
    what keeps the two from drifting apart again.
    """
    return _key_bounded_block(_routers_block(body), name, 4)


def test_plex_public_router_present() -> bool:
    """Step-9: dynamic.yml.j2 defines the file-provider `plex` router (AC2/AC3).

    EVERY PRESENCE PIN IS ASKED OF THE `plex` ROUTER'S OWN BLOCK — Step-2a F1,
    round 10, and this is the highest-severity row the round-10 sweep turned up.
    All four used to be matched over the whole `routers:` section while the claim is
    about ONE router, and by round 3 that section holds four siblings that answer
    for each other: `plex-web` carries the same `Host(...)` rule and the same
    `service: plex`, and `traefik-dashboard` carries `websecure` and the var-driven
    `certResolver`. So a `plex` router rewritten to

        entryPoints: [web] / service: api@internal

    printed `host=True, websecure=True, service=True, var_resolver=True` — this
    field byte-identical to the honest tree's — at guard PASS 36/36, and the real
    traefik:v3.7.5 loaded `plex -> api@internal` on `web` with only
    `security-headers@file` (logs/red-step02a-rework-f1-round10.log, B1). Since plex
    is by design the ONE router carrying no allowlist, that is the unauthenticated
    Traefik API on the WAN port-forward — reached by the sibling clause's own
    `plex_no_allowlist=True`.

    `hardcoded` stays SECTION-WIDE, per (3) of the anchor rule: "no router
    hard-codes a resolver" quantifies over all of them, and narrowing it to `plex`
    would have dropped the only pin covering `plex-web`.
    """
    dynamic = _read(DYNAMIC)
    routers = _routers_block(dynamic)
    plex = _router_block(dynamic, "plex")
    host = re.search(r'Host\(`plex\.\{\{\s*domain\s*\}\}`\)', plex) is not None
    websecure = "websecure" in _param_values(plex, "entryPoints")
    service = _pins_scalar(plex, "service", "plex")
    # certResolver MUST be the {{ acme_resolver }} var, NOT a hard-coded literal,
    # so the Step-11 DNS-01 flip touches one variable (mirrors whoami invariant).
    var_driven = re.search(r'certResolver:\s*"?\{\{\s*acme_resolver\s*\}\}', plex) is not None
    hardcoded = re.search(r'certResolver:\s*"?le-(http|dns-cf)\b', routers) is not None
    ok = host and websecure and service and var_driven and not hardcoded
    print(
        f"{'OK' if ok else 'FAIL'}: plex public router present "
        f"(host={host}, websecure={websecure}, service={service}, "
        f"var_resolver={var_driven}, hardcoded={hardcoded})"
    )
    return ok


def test_plex_service_backend_32400() -> bool:
    """Step-9: plex loadBalancer backend resolves to 192.168.1.110:32400 (AC4).

    Step-2a F1, round 10: `plex:` and its URL are both asked of the `plex` SERVICE's
    own block. Asked of the section, a second service answered for the first — the
    delivered URL demoted to a `plex-direct` service nobody routes to while `plex`
    itself pointed at `http://127.0.0.1:32400`, which is traefik's own loopback and
    a 502 for the one public host. GREEN at 36/36, and the real traefik:v3.7.5 loads
    exactly that (logs/red-step02a-rework-f1-round10.log, B2).
    """
    dynamic = _read(DYNAMIC)
    services = _dynamic_service_block(dynamic, "plex")
    defaults = _read(ROLE / "defaults" / "main.yml")
    has_service = bool(services.strip())
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
    whoami_allowlist = INTERNAL_ALLOWLIST_REF in _label_members(
        _service_label_map(compose, "whoami").get(
            "traefik.http.routers.whoami.middlewares", ""
        )
    )
    ok = plex_no_allowlist and plex_has_headers and whoami_allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: plex router public (no allowlist), whoami still internal "
        f"(plex_no_allowlist={plex_no_allowlist}, plex_headers={plex_has_headers}, "
        f"whoami_allowlist={whoami_allowlist})"
    )
    return ok


def test_public_services_is_exactly_plex() -> bool:
    """Step-9: group_vars public_services is exactly [plex] — nothing else promoted.

    Step-2a F1, round 11: the list is read through `_top_level_list`, so a column-0
    comment cannot end it three entries early. This is the clause whose whole job is
    "nothing else promoted" and it printed `entries=['plex']` about a list holding
    `['plex', 'prometheus']` (B1).
    """
    all_yml = _read(ANSIBLE / "group_vars" / "all" / "vars.yml")
    entries = _top_level_list(all_yml, "public_services")
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
        # Each router's two PRESENCE pins are asked of the EFFECTIVE value of one
        # label key on that service's own labels (rounds 12 and 13). Every weaker
        # spelling of this pin has been measured GREEN on a broken tree: the
        # allowlist dropped behind a `# was:` line above (A4) or trailing the line
        # itself (R3), a resolver hard-coded to a literal `le-staging` with the
        # var-driven line kept as a comment (A7/R6), and the same literal simply
        # appended as a SECOND `certresolver=` entry with no comment anywhere, which
        # is the value docker keeps (D3) — and this clause is the reason the Step-11
        # flip is supposed to be one variable.
        labels = _service_label_map(compose, s)
        mw = INTERNAL_ALLOWLIST_REF in _label_members(
            labels.get(f"traefik.http.routers.{s}.middlewares", "")
        )
        cr = re.fullmatch(
            r'\{\{\s*acme_resolver\s*\}\}',
            labels.get(f"traefik.http.routers.{s}.tls.certresolver", ""),
        ) is not None
        if not (mw and cr):
            failures.append(f"{s}(allowlist={mw},var_resolver={cr})")
    # ABSENCE pin, so it stays as WIDE as the document — a certresolver literal for
    # one of these routers is a literal wherever its label sits. Decommented only,
    # because a comment recording the pre-Step-11 `le-http` value was a FALSE RED on
    # a fully correct tree (row A10).
    hardcoded = re.search(
        r'routers\.(?:homepage|uptime-kuma|grafana|prometheus)\.tls\.certresolver\s*=\s*le-(?:http|dns-cf)\b',
        _strip_comments(compose),
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
    pub = _top_level_list(all_yml, "public_services")
    not_public = pub is not None and "prometheus" not in pub
    compose = _read(COMPOSE)
    router_allowlist = INTERNAL_ALLOWLIST_REF in _label_members(
        _service_label_map(compose, "prometheus").get(
            "traefik.http.routers.prometheus.middlewares", ""
        )
    )
    ok = not_public and router_allowlist
    print(
        f"{'OK' if ok else 'FAIL'}: prometheus never public "
        f"(not_public={not_public} (public_services={pub}), router_allowlist={router_allowlist})"
    )
    return ok


# plex-monitoring Step 1: the latency histogram boundaries, in SECONDS, ascending.
#
# TRAEFIK_DEFAULT_BUCKETS is what the pinned image emits with no `buckets` key at
# all — read off the binary itself, not off memory or off client_golang:
#
#     $ docker run --rm traefik:v3.7.5 traefik --help | grep -A1 buckets
#     --metrics.prometheus.buckets  (Default: "0.100000, 0.300000, 1.200000, 5.000000")
#
# It is here so the check below can assert EXPECTED differs from it. Pinning the
# default as "custom" is non-vacuous against the FILE and totally vacuous against
# the objective: the emitted `le` series is byte-identical either way, so the
# paired operator verification cannot fail. Traefik does NOT use client_golang's
# DefBuckets for this histogram.
TRAEFIK_DEFAULT_BUCKETS = [0.1, 0.3, 1.2, 5.0]

# EXPECTED is calibrated against the quantity this histogram actually observes.
# `traefik_entrypoint_request_duration_seconds` is SERVER-SIDE handler duration: it
# does NOT include TCP connect, the TLS handshake, or client transit. So the
# client-side totals in docs/runbooks/plex-latency-baseline.md — remote /identity
# TTFB 157/293/486 ms, and the "+9.4 ms Traefik overhead" that is really an
# HTTPS-through-Traefik vs plain-HTTP-direct delta, i.e. mostly the TLS handshake —
# are the WRONG ruler for it. An earlier revision of this list was built on them.
#
# Measured, not argued (logs/calibration-step01a-server-side-duration.log:
# traefik:v3.7.5, controllable-think-time backend, asyncio TCP proxy injecting
# 100 ms RTT in front, bucket/_sum/_count delta scraped per leg):
#
#   leg                            client TTFB   recorded server-side mean
#   instant backend, no WAN delay      41.2 ms            0.392 ms
#   instant backend, +100 ms RTT      151.0 ms            0.379 ms
#   backend 200 ms, no WAN delay      241.2 ms          200.542 ms
#   backend 200 ms, +100 ms RTT       351.4 ms          200.540 ms
#
# Rows 3/4 are the proof: client TTFB differs by 110 ms, the recorded mean is
# identical to three decimals. Hence the three bands below:
#
#  * 0.00025..0.001 — the floor, and where the plan's own Demo query lands. An
#    empty-backend request through this proxy records 0.392 ms mean (none under
#    0.25 ms, 19/20 under 0.5 ms), and this repo's LAN capture puts direct-to-Plex
#    /identity at 0.327 ms median. A 0.0005 floor would bury every /identity in
#    bucket one — the same defect this list was rewritten to fix, two orders down.
#  * 0.0025..0.25 — the working band for authenticated queries (/library/sections)
#    and for any real backend think-time.
#  * 1.0..30.0 — the streaming tail. The response write DOES reach this metric,
#    but only once the body outgrows the socket buffers: a 4 MB body to a slow
#    reader still recorded 3.6 ms (buffers absorbed it), while 16 MB at ~2 MB/s
#    recorded 6.96 s against 8.44 s at the client. Video responses are far past
#    that threshold, so client backpressure is visible here and needs seconds.
EXPECTED_BUCKETS = [
    0.00025, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25,
    1.0, 5.0, 30.0,
]


def _metrics_prometheus_block(body: str) -> str:
    """Slice the `prometheus:` mapping out of the static config's `metrics:` section.

    Two hops, so a `buckets` key that drifts to the top level — or under `metrics:`
    but outside `prometheus:` — is OUTSIDE the returned text and cannot satisfy the
    check. Terminates on the first line indented no deeper than `prometheus:` itself.
    """
    m = re.search(r'(?ms)^metrics:\s*$\n(.*?)(?=^\S|\Z)', body)
    if not m:
        return ""
    p = re.search(r'(?ms)^\s{2}prometheus:\s*$\n(.*?)(?=^\s{0,2}\S|\Z)', m.group(1))
    return p.group(1) if p else ""


def _block_scalar(block: str, key: str) -> str | None:
    """A scalar `key: value` inside an already-sliced block, or None if absent.

    Horizontal-whitespace classes only, same reason as `_bucket_values`: a `\\s*`
    after the colon runs past the newline and captures the next line. Returns the
    raw token so the diagnostic can PRINT what it found — `entryPoint=websecure`
    says more than `metrics_entrypoint=False`.

    AND THE HORIZONTAL CLASS IS YAML'S, NOT PYTHON'S (Step-5c F1, round 5). This
    was `[^\\S\\n]` on both separators with `(\\S+)` for the value — three
    unicode classes deciding where a value a runtime receives begins and ends.
    YAML's separation space is `s-white ::= s-space | s-tab` (YAML 1.2 §6.1) and
    its line break is `b-char ::= LF | CR` (§5.4), so a plain scalar ends at a
    space, a tab or a line break and at NOTHING ELSE: U+00A0 and U+3000 are
    scalar CONTENT. `\\S` stopped at one and the trailing `[^\\S\\n]*` then ate
    it, so `service: plex<U+00A0>` on ONE twin read `plex` and compared EQUAL to
    its sibling — `PASS: 42/42` while the pinned `traefik:v3.7.5` answered
    `status='disabled'`, *the service "plex\\u00a0@file" does not exist*, HTTP
    404 for the host, and the sibling in the SAME FILE still 200: one router
    refused, not the document, so `just play` succeeds and the gate is green
    (logs/critic-step05c-r4-service-scalar.log 10/10, `-guard.log` 9/9).

    THE ASCII HALF OF THE FOLD IS FAITHFUL AND STAYS. Three trailing ASCII
    spaces resolve `backend` at the engine (same log, T1) and a TAB is a
    separator either side of the value (logs/red-step05c-rework-r5-engine.log
    E1/E2), which is why the narrowing is to `s-white` and not to nothing. The
    `\\r?` before `$` is `b-char`'s other half: a CR ends the scalar for YAML,
    so it must not land inside the value token either.

    EVERY CALLER READS A YAML DOCUMENT SOME RUNTIME PARSES, so this one edit is
    the same question answered for all eight — and the engines answer it
    differently, which is the reason to fix the READER rather than the row:
    prometheus REFUSES `scrape_interval: 60s<U+00A0>` at load (loud) and ACCEPTS
    `metrics_path: /pve<U+00A0>`, scraping a path no line of the file wrote
    (silent); traefik's static config takes `entryPoint: metrics<U+00A0>` as an
    entrypoint that does not exist and serves no metrics at all (same log,
    P1/P2/P3). Price on the delivered tree: ZERO — no template under
    `templates/` holds one non-`s-white` whitespace character, all 8 measured
    (logs/red-step05c-rework-r5-blockscalar.log M0).

    THE LEADING POSITION IS COVERED BY THE SAME EDIT AND IS LOUD AT THE ENGINE:
    `service:<U+00A0>plex` now lands INSIDE the value token, so the reader
    reddens — and traefik refuses the WHOLE document for it (the review's C1),
    so the two agree. Trailing is the silent vector; saying which is which is
    part of the claim.

    WHAT IS NOT NARROWED, STATED AS A PRICE: the token comes back RAW, quotes
    included, so `service: "plex"` on one side and `service: plex` on the other
    compare UNEQUAL while YAML resolves both to `plex` and traefik answers 200
    for the host (same log, E3). That is a FALSE RED with a one-line escape —
    loud, and the opposite direction from the whitespace class this round is
    about. Unquoting here would change what seven other callers compare and is
    not this round's measurement.
    """
    m = re.search(rf'(?m)^[ \t]*{re.escape(key)}:[ \t]*([^ \t\r\n]+)[ \t]*\r?$', block)
    return m.group(1) if m else None


def _pins_scalar(block: str, key: str, value: str) -> bool:
    """Does `block` pin `key:` to exactly `value`? — the same reader, one place.

    Step-5c F1, round 5. Three rows asked a `service:` clause with a hand-rolled
    `re.search(r'(?m)^\\s*service:\\s*<value>\\s*$', block)` while the twin row
    asked it through `_block_scalar`, and the class question then had to be
    answered four times — which is exactly the state the ANCHOR RULE above says
    is how a blind spot gets inherited ("two anchor conventions in one file").
    They were all on `\\s`, so `service: api@internal<U+00A0>` was `True` here
    and a disabled router at the engine.

    It is a strict behavioural equivalent of the regex it replaces apart from
    that class: same first match, same indentation tolerance, same refusal of a
    re-quoted `"api@internal"` (measured over a 1120-block grid through BOTH
    implementations, logs/red-step05c-rework-r5-differential.log D1-D3 — every
    one of the 480 disagreements is one direction, old accepted / new refuses,
    and every disagreeing block carries a non-`s-white` character; the pre-edit
    reader is reconstructed to its own sha256 rather than paraphrased).

    AND IT IS WHAT COVERS THE TWO-SIDED EDIT. The twin row compares a twin to
    its SIBLING, so a U+00A0 appended to BOTH is invisible to it by
    construction — both sides read equal and both routers are dead. These pins
    are absolute, so they are the cover for that case, and leaving them on
    Python's class would have left the whole clause uncovered for it
    (logs/red-step05c-rework-r5-blockscalar.log R1).
    """
    return _block_scalar(block, key) == value


# Bind hosts a peer on the compose network can reach. Empty (Traefik's own `:8082`
# form) and `0.0.0.0` are the IPv4 spellings of "all interfaces", `[::]` the IPv6
# one; all three are MEASURED benign, not assumed — logs/calibration-step01a-bind-host.log
# scrapes each from a separate container by service name and reads
# peer_scrape=200 with 14 entrypoint series, identical to the control. Anything
# else — `127.0.0.1` above all — is a host the process still listens on and still
# answers ITSELF while the scraper gets nothing.
PEER_REACHABLE_HOSTS = ("", "0.0.0.0", "[::]")


def _entrypoint_address(body: str, name: str) -> tuple:
    """(host, port) of `entryPoints.<name>.address` in the static config.

    Same two-hop shape as `_metrics_prometheus_block`, so an `address:` belonging
    to a different entrypoint cannot answer for this one.

    Returns the HOST as well as the port, and that is not tidiness: an address has
    more than one field and each is an independent way to move the endpoint out
    from under its scraper. A port-only parse is green through
    `":8082" -> "127.0.0.1:8082"` (mem-1785294475-ebe4). The `\\[...\\]` branch is
    first so the IPv6 form's own colons are not mistaken for the port separator.
    """
    m = re.search(r'(?ms)^entryPoints:\s*$\n(.*?)(?=^\S|\Z)', body)
    if not m:
        return (None, None)
    e = re.search(
        rf'(?ms)^\s{{2}}{re.escape(name)}:\s*$\n(.*?)(?=^\s{{0,2}}\S|\Z)', m.group(1)
    )
    if not e:
        return (None, None)
    a = re.search(
        r'(?m)^[^\S\n]*address:[^\S\n]*"?(\[[^\]]*\]|[^":\s]*):(\d+)', e.group(1)
    )
    return (a.group(1), a.group(2)) if a else (None, None)


def _scrape_configs_block(body: str) -> str:
    """prometheus.yml.j2's top-level `scrape_configs:` list — a job's anchor.

    A Prometheus config's top level also holds `global:`, `alerting:`,
    `rule_files:` and `remote_write:`, and a `global.external_labels` value may be
    any string — including a block scalar shaped exactly like a scrape job.
    Nothing under those keys is a job and none of it may answer for one.
    """
    return _key_bounded_block(body, "scrape_configs", 0)


def _scrape_job_block(body: str, job: str) -> str:
    """One scrape job's body under `scrape_configs:`, up to the next `- job_name:`.

    Scoped to ONE job for the same reason `_compose_service_block` is scoped to
    one service: a per-job assertion (`metrics_path: /pve`) must not be
    satisfiable by a sibling job's keys. The job name is anchored to end-of-line
    so `prometheus` cannot answer for `pve-exporter`.

    Step-2a F1, round 9: the `scrape_configs:` hop is the fix, and — like the
    `services:` hop one round earlier — it is round 7's own `_key_bounded_block`
    applied one level up rather than any new machinery. It closes two doors at
    once, because that helper strips comments BEFORE slicing:

    * without the hop this took the first `- job_name: <name>` at ANY indent in
      the document. A `global.external_labels` value holding a block scalar of
      the job shape therefore BECAME the job, and with the real job stripped of
      `metrics_path: /pve` and its `__param_target` relabel the clause printed
      `metrics_path='/pve', path_pinned=True, address_rewritten=True` — the
      honest tree's field, verbatim — at guard PASS 36/36. The artifact renders,
      `yaml.safe_load`s, and `promtool check config` on the real
      prom/prometheus:v3.6.0 returns rc=0; what Prometheus then loads is
      `metrics_path=None` and no `__param_target`, i.e. the target reads UP with
      ZERO `pve_*` series — verbatim the no-op this step exists to prevent
      (logs/calibration-step02a-f1-round9.log, leg A; R1/R2/R3).
    * the job body is no longer satisfiable by its own documentation, which
      matters here more than anywhere else in this file: the pve-exporter job
      carries a nine-line comment naming `metrics_path`, `/pve` and
      `__param_target` precisely because those are the pins.

    And the second half of the anchor rule, which the path cannot supply: if the
    name resolves MORE THAN ONCE inside `scrape_configs:` this returns "" and the
    clause reddens. A Jinja `{% if %}/{% else %}` either-or pair of the same job
    is inside the anchored region, so the path does not see it; the first branch
    answered while the second one rendered, again at promtool rc=0 (R4). Two jobs
    of one name is not a state Prometheus itself will load, so the guard is not
    being asked to pick — it is being asked to stop guessing.

    Measured free before it was prescribed (leg B): on the delivered tree every
    job name resolves exactly once, three of the five job blocks are
    byte-identical, and `traefik` and `pve-exporter` differ ONLY by their
    comments being stripped. That is a price, not a free lunch, and it is the
    direction `_strip_comments` already takes file-wide.
    """
    region = _scrape_configs_block(body)
    heads = list(re.finditer(
        rf'(?m)^[^\S\n]*-[^\S\n]*job_name:[^\S\n]*{re.escape(job)}[^\S\n]*$', region
    ))
    if len(heads) != 1:
        return ""
    tail = region[heads[0].end():]
    nxt = re.search(r'(?m)^[^\S\n]*-[^\S\n]*job_name:', tail)
    return tail[:nxt.start()] if nxt else tail


def _scrape_job_names(body: str) -> list:
    """EVERY `job_name:` under `scrape_configs:`, unquoted, in document order.

    Step-7a. The sibling of `_scrape_job_block` and deliberately not built out of
    it: that helper answers "give me THIS job", which presupposes a name, and the
    alert rules ask the opposite question — "is the name this expr cites a job
    this stack actually scrapes?". An expr naming a job that does not exist is
    the silent half of `params.module`'s class one file over: nothing is invalid
    anywhere, the rule loads at `promtool` rc=0, and it matches no series and
    fires never.

    Anchored at `_scrape_configs_block` for the reason that helper gives — a
    `global.external_labels` block scalar may be shaped exactly like a job, and
    none of it is one.
    """
    return [_yaml_unquote(m.group(1)) for m in re.finditer(
        r'(?m)^[^\S\n]*-[^\S\n]*job_name:[^\S\n]*(\S.*?)[^\S\n]*$',
        _scrape_configs_block(body),
    )]


def _rule_files_entries(body: str) -> list:
    """A Prometheus config's `rule_files:` entries, unquoted, or [] when absent.

    Step-7a, and ONE reader because two claims consume it: the row this template
    adds to `RELOAD_CONTRACT` derives its container-side path from here (there is
    no `--rule.file` flag and no image default — the path is named by ANOTHER
    rendered file, which is what makes `rule_files:` the third carrier that walk
    has to know about), and `test_prometheus_rule_files_names_the_render`
    quantifies over the same list for the glob refusal. Two regexes over one
    question is the drift this file spent Step-2a rounds 13-15 closing.

    Top-level, at column 0 (`_key_bounded_block(..., 0)`), the same anchor
    `_scrape_configs_block` takes: `rule_files` is a document-root key, and a
    `rule_files:` nested inside some other mapping is not the one Prometheus
    loads.

    Entries that are not scalars — a flow collection, a block mapping — come back
    as `None` rather than being dropped, so a caller cannot mistake an unreadable
    list for an empty one.
    """
    return [
        None if (s := _scalar_entry(entry)) is None else _yaml_unquote(s)
        for entry in _list_entries(_key_bounded_block(body, PROM_RULES_KEY, 0))
    ]


def _watchdog_emitted(source: str) -> tuple:
    """(metric family names, `_event` type names) the watchdog SOURCE emits.

    Step-7a. `ast` and not a text scan, for the reason `far_end_is_held` gives
    about citations: the watchdog's own comments name `TX_STALL`, `TX_HELD` and
    `SLOW_QUERY` in prose three lines above the code that emits them, and design
    §5.2's metric names are quoted in a header block there too — so a `grep` for
    either would be answered by the file's DOCUMENTATION and would stay green
    over a program that emits nothing at all. Comments are not in the tree.

    Families are every `plex_*` string CONSTANT in the module (both carriers: the
    `family(...)` calls and the `_SQLITE_GAUGES` tuple literal). Event types are
    the first argument of each `_event(...)` call, which is exact — the trigger
    classifier has one such call per branch.

    Returns two EMPTY sets on a source that will not parse, which fails the
    clauses closed: a citation check whose far end is unreadable must not read as
    agreement.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return frozenset(), frozenset()
    families = {
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and re.fullmatch(r'plex_[a-z0-9_]+', node.value)
    }
    events = {
        node.args[0].value for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == PLEX_WATCHDOG_EVENT_FN
        and node.args and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }
    return frozenset(families), frozenset(events)


def _static_targets(block: str) -> list:
    """Every `targets:` entry under one scrape job's `static_configs:`, RAW.

    Row 5c is the FOURTH caller — pve's, plex-exporter's and
    plex-node-exporter's clauses each carried their own copy of this expression,
    and three more copies would be seven. One reader, so the rule cannot drift
    between them.

    The rule it carries is `_indented_blocks`, PLURAL, and Step-2a F1 round 9 is
    why: Prometheus takes `static_configs` as a LIST and scrapes every entry in
    it, so the singular read left `target_is_pve_host=True` over a config that
    loads `['192.168.1.50', '203.0.113.9']` — the exporter interrogating a
    caller-chosen host with the homelab's PVE credential
    (logs/calibration-step02a-f1-round9.log, leg A, R5).

    RAW, quotes included, and that is the seam rather than an oversight:
    `_yaml_unquote` is the CALLER's to apply because the callers compare
    different things. Two of them compare a whole `host:port` token, 5c's
    compares a URL whose authority half is a Jinja reference, and
    `test_pve_scrape_job_is_multi_target` PRINTS the raw list in its diagnostic.
    Unquoting here would silently change what that clause reports.
    """
    return re.findall(
        r'(?m)^[^\S\n]*-[^\S\n]*(\S.*?)[^\S\n]*$',
        "\n".join(_indented_blocks(_indented_block(block, "static_configs"), "targets")),
    )


def _relabel_entry_fields(entry: str) -> tuple:
    """`(fields, unreadable)` for ONE `relabel_configs` entry's own key column.

    The same two halves `_service_key_lines` returns, for the same reason, one
    nesting level down: `_relabel_triplet` locates a hop by two of its keys and
    then has to say what ELSE the entry declares, and an absence pin naming the
    fields somebody thought of fails OPEN one field past its edge.

    The `-` is replaced by a SPACE rather than stripped, because an entry's
    first key shares its line with it and the column is what tells that key from
    a nested one. `- source_labels: [__address__]` and the `target_label:` under
    it then sit at one column, which is the column this reader reports on;
    anything deeper belongs to a value, not to the entry.

    `unreadable` is the half that makes the allow-list complete rather than
    merely intended: a `<<` merge key, an explicit-key pair or a line this file's
    `_yaml_key` cannot parse comes back here and the caller reddens on it,
    instead of being dropped on the floor and counted as no field at all.
    """
    lines = [
        re.sub(r'^([^\S\n]*)-(?=[^\S\n]|$)', lambda m: m.group(1) + " ", ln, count=1)
        for ln in entry.splitlines() if ln.strip()
    ]
    if not lines:
        return {}, []
    top = min(len(ln) - len(ln.lstrip()) for ln in lines)
    fields, unreadable = {}, []
    for line in lines:
        if len(line) - len(line.lstrip()) != top:
            continue
        if _line_class(line) == "key":
            _, key, value = _yaml_key(line)
            fields[key] = value
        else:
            unreadable.append(line.strip())
    return fields, unreadable


def _flow_sequence(value: str) -> list | None:
    """A YAML FLOW sequence's members, unquoted, or None if it is not one.

    `source_labels: [__address__]` is the only shape `_relabel_triplet` locates
    — the block form puts the label on its own line, where that helper's
    single-line pattern does not match it and the hop reads MISSING — so this
    reader is deliberately narrow: it answers the members of a `[…]` and None
    for everything else, which the caller reports as a hop whose source list it
    could not read rather than as an empty one.

    `_yaml_unquote` per member for `PLEX_JOB_KEYS`' reason: `[__address__]` and
    `["__address__"]` are one list with two spellings, and an arm that told them
    apart would be pinning a typography (measured: logs/builder-5c-r2-arms.log
    M10/M11).
    """
    v = value.strip()
    if not (v.startswith("[") and v.endswith("]")):
        return None
    inner = v[1:-1].strip()
    return [_yaml_unquote(m.strip()) for m in inner.split(",")] if inner else []


# Every field a Prometheus `relabel_config` entry may declare (v3.12.0, the
# image this row is measured against). `_RELABEL_HOP_FIELDS` is a SUBSET of this
# per hop, so what the allow-list excludes is a relation between two constants
# and not a sentence somebody has to keep true by hand.
_PROM_RELABEL_FIELDS = (
    "source_labels", "separator", "regex", "modulus", "target_label",
    "replacement", "action",
)

# The spelling of each excluded field that CHANGES NOTHING — its documented
# default, written out. This is the allow-list's PRICE, and it is here as a
# constant because the sentence that used to stand in for it was false of every
# field it named (DEC-318): it said the excluded fields "change what the hop
# writes or whether it writes at all". Every one of them has a default, and a
# default written out explicitly is a no-op the wire cannot tell from the
# delivered tree — so each of these is a WORKING document this guard reds.
# Measured, both legs from one mutation, with the CONTROL live in the same run:
# logs/builder-5c-r3-price.log.
#
# `target_label` is absent because it is allowed on all three hops and therefore
# never excluded; `modulus`'s entry is the value the field is ignored at under
# `action: replace`, which is what its default 0 also is.
_RELABEL_NOOP_SPELLING = {
    "source_labels": "source_labels: []",
    "separator": 'separator: ";"',
    "regex": "regex: (.*)",
    "modulus": "modulus: 0",
    "replacement": "replacement: $1",
    "action": "action: replace",
}

# The fields each hop's read MODELS, and therefore the only ones its entry may
# declare. Sourced from what `_relabel_triplet` actually asks of the entry: the
# two `carry`/`keep` hops are a copy from one label to another, and `dial`'s
# `replacement:` IS its value.
_RELABEL_HOP_FIELDS = {
    "carry": ("source_labels", "target_label"),
    "keep": ("source_labels", "target_label"),
    "dial": ("target_label", "replacement"),
}

# The label each copying hop reads FROM, compared as a whole list rather than
# searched: a second member is concatenated with the default `;` separator and
# the write silently becomes a value nothing named (wire W5).
_RELABEL_HOP_SOURCE = {"carry": "__address__", "keep": "__param_target"}


def _relabel_triplet(block: str, exporter: str) -> tuple:
    """`(defects, hops)` for one multi-target job's `__param_target` walk.

    THE FOURTH SPELLING WAS THE PRESCRIPTION, and this is the reuse row 5c's
    record asked for: `pve-exporter` carried this walk inline, 5c adds three more
    jobs of the same shape, and four unrelated copies is where they start to
    differ. The rows behind the read live at
    `test_pve_scrape_job_is_multi_target`, which won them; what is repeated here
    is only the rule they establish.

    `relabel_configs` is a LIST, so every half of every hop is asked of ONE
    ENTRY (`_list_entries`). Step-2a F1 round 10: until then each half was a
    `(?ms) … .*? …` span over the whole block, and `.*?` does not care which
    entry the halves came from — three deployable rows printed a field
    BYTE-IDENTICAL to the honest tree's at guard PASS 36/36 with `promtool check
    config` rc=0. The `(?:-\\s*)?` prefix is because an entry's first key shares
    its line with the `-`; the trailing `\\s*$` is so `__param_target` cannot be
    answered by a longer label that merely starts with it.

    THE THREE HOPS, and each defect NAMES the one that is missing because they
    fail differently — row 5c's acceptance 4 is exactly that the reds are
    distinguishable:

    * `carry` — `__param_target` taken from `__address__`. Missing, the
      multi-target exporter is asked about its DEFAULT target: pve-exporter's
      `target` defaults to `localhost`, so it interrogates its own container, and
      blackbox's `/probe` answers HTTP 400 with no `probe_*` series at all.
    * `keep` — `instance` taken from `__param_target`. THE SILENT ONE, which is
      why it is a hop here and was not pinned at all before this row: the probe
      still runs and every series is correct except its identity — all of them
      are attributed to the exporter's own address, so 5c's three jobs collapse
      onto one `instance` and design §4.6's differential cannot be read.
    * `dial` — `__address__` replaced by the exporter. Missing, Prometheus dials
      the PROBED host directly on the wrong port and path.

    ORDER IS PART OF TWO HOPS AND NOT OF THE THIRD, stated rather than applied
    uniformly: relabel rules run in written order, so `carry` must precede
    `dial` (or `__param_target` is taken from an `__address__` already overwritten
    — the exporter asked about ITSELF, measured as `?target=pve-exporter%3A9221`)
    and must precede `keep` (or `instance` is taken from a label not yet set).
    `keep` against `dial` is UNORDERED: `keep` reads `__param_target`, which
    `dial` does not touch, so either sequence produces the same label set and a
    guard demanding one of them would be forbidding a config that works.

    THE LIST IS THE TRIPLET AND NOTHING ELSE, which is the repair of a sentence
    this docstring shipped and DEC-316 charged. It used to say a later entry
    overwriting `__param_target` "is green here, and it fails loudly at deploy".
    That is false, measured — at my own hands on real prom/prometheus:v3.12.0 +
    prom/blackbox-exporter:v0.28.0 against a stub origin, on renders of the
    shipped templates (logs/builder-5c-r2-wire.log, W4): `promtool check config`
    rc=0, the target UP, and `probe_success 0` carried on
    `instance="http://origin/identity"` — the same origin the CONTROL row probes
    at `probe_success 1`. Nothing is loud. The graph blames a healthy Plex and
    design §5.3's `PlexUnreachable` fires an outage alert about it.

    So the entries OUTSIDE the three hops are a defect, not a residual. W7 is
    why the pin is the LIST and not a write-count per label: a fourth entry
    `action: labeldrop` / `regex: instance` writes no `target_label` at all,
    rc=0, `up 1`, `probe_success 1` — and `instance` is back to
    `blackbox-exporter:9115`, undoing the keep hop in perfect silence.

    AND THE FIELDS INSIDE A HOP ARE THE SAME CLASS, which is the half the old
    paragraph's boundary missed entirely. An entry this reader reports PRESENT
    can still be made not to fire or to write something else, and both leave a
    VALID config (same log): `regex:` matching no address on the carry hop is
    rc=0 with `up 0` and the job's `probe_*` series ABSENT ENTIRELY — a state
    `probe_success == 0` cannot match (W1, the class already filed at
    `task-1786159639-39db`); `replacement:` on the same hop redirects the probe
    and the `instance` label follows it (W2). A second `source_labels` member is
    the same silence one layer down — concatenated with the default `;`
    separator, rc=0, `probe_success 1`, `instance="http://origin/identity;http"`
    (W5). Hence `_RELABEL_HOP_FIELDS`, an allow-list rather than an absence pin
    for `PLEX_JOB_KEYS`' reason, plus `_relabel_entry_fields`' unreadable half.

    WHERE THE CLASS ENDS, measured rather than assumed: `action: labeldrop` on a
    hop is `promtool` rc=1, *"labeldrop action requires only 'regex', and no
    other fields"* (W3). That one was never silent, so the class is the fields
    that leave a valid config — and the control matters, because without it this
    paragraph would be claiming a hole where the runtime already stands.

    THE PRICE IS EVERY EXCLUDED FIELD, NOT THE ONE THAT WAS NOTICED — DEC-318,
    and the correction of a sentence this file shipped one constant above.
    `action: replace` written out EXPLICITLY is the DEFAULT action and is
    byte-identical to the delivered tree at the wire (W6), and SO IS EVERY OTHER
    FIELD THIS ALLOW-LIST EXCLUDES, in its own default spelling: `separator:
    ";"`, `regex: (.*)` and `modulus: 0` on all three hops, `replacement: $1` on
    the two copying ones, and `source_labels: []` on `dial` — which is the field
    the charge's own five did not reach, because it is excluded there and
    nowhere else. Driven with the CONTROL live in the same run, both legs from
    ONE mutation of the shipped template (logs/builder-5c-r3-price.log): every
    one is `promtool` rc=0 carrying the untouched render's own `up`,
    `probe_success`, `instance` and series count, and every one REDS here. A
    field with a default always has BOTH spellings and an allow-list refuses
    both, which is why the old sentence read true — the non-default spellings
    beside them really do change the wire (W1 takes the job's `probe_*` series
    away entirely; W2 redirects the probe), and this battery carries them as the
    contrast rows N1/N2 rather than leaving the two cases to be conflated again.

    The standing cost is therefore one document per (hop, field) pair, and the
    count is READ OFF the constants by
    `test_relabel_allow_list_prices_every_field_it_excludes` at every run rather
    than typed here, because a number in prose is a measurement sentence with
    nothing arming it. It is taken deliberately: the door out is one string in
    `_RELABEL_HOP_FIELDS` — and that clause reds if it is walked through without
    the price following it — whereas the door out of an absence pin is another
    round of this. DEC-317.

    What is still NOT modelled, stated narrowly this time because a "what is NOT
    modelled" paragraph is an ARM's claim in prose and the last one was driven
    only after it shipped: relabelling that reaches a job from OUTSIDE its own
    `relabel_configs` key. This reader is handed one block and opens one key in
    it, so a `metric_relabel_configs:` beside it is invisible HERE. It is not
    invisible everywhere — for the three blackbox jobs it is a key outside
    `BLACKBOX_JOB_KEYS` and their clause reddens on it — but
    `test_pve_scrape_job_is_multi_target` has no key allow-list, so on that job
    it is open. Named rather than closed: this row owns the entries under one
    key, and a second key is the pve clause's to pin.
    """
    entries = _list_entries(_indented_block(block, "relabel_configs"))

    def _entry(*patterns):
        return next(
            (i for i, e in enumerate(entries)
             if all(re.search(p, e) for p in patterns)),
            None,
        )

    hops = {
        "carry": _entry(
            r'(?m)^\s*(?:-\s*)?source_labels:[^\n]*__address__',
            r'(?m)^\s*(?:-\s*)?target_label:[^\S\n]*__param_target\s*$',
        ),
        "keep": _entry(
            r'(?m)^\s*(?:-\s*)?source_labels:[^\n]*__param_target',
            r'(?m)^\s*(?:-\s*)?target_label:[^\S\n]*instance\s*$',
        ),
        "dial": _entry(
            r'(?m)^\s*(?:-\s*)?target_label:[^\S\n]*__address__\s*$',
            rf'(?m)^\s*(?:-\s*)?replacement:[^\S\n]*"?{re.escape(exporter)}"?\s*$',
        ),
    }
    defects = []
    if hops["carry"] is None:
        defects.append(
            "no entry carries __address__ into __param_target — the exporter is "
            "asked about its own default target, not about the configured one"
        )
    if hops["keep"] is None:
        defects.append(
            "no entry keeps __param_target as `instance` — SILENT: the probe "
            f"still runs and every series is attributed to {exporter}"
        )
    if hops["dial"] is None:
        defects.append(
            f"no entry replaces __address__ with {exporter!r} — Prometheus dials "
            "the probed host itself instead of the exporter"
        )
    for later, why in (
        ("dial", "__param_target would be taken from an __address__ already "
                 "overwritten — the exporter asked about ITSELF"),
        ("keep", "`instance` would be taken from a __param_target not yet set"),
    ):
        if hops["carry"] is not None and hops[later] is not None \
                and not hops["carry"] < hops[later]:
            defects.append(
                f"the carry hop is entry {hops['carry']} but {later} is entry "
                f"{hops[later]}: {why}"
            )
    for name, allowed in _RELABEL_HOP_FIELDS.items():
        if hops[name] is None:
            continue
        fields, unreadable = _relabel_entry_fields(entries[hops[name]])
        extra = sorted(k for k in fields if k not in allowed)
        if extra or unreadable:
            defects.append(
                f"the {name} hop (entry {hops[name]}) declares {extra} outside "
                f"{list(allowed)}, unreadable={unreadable} — a field beside the "
                "copy can decide whether the hop fires and what it writes while "
                "leaving a config Prometheus loads, and this allow-list refuses "
                "it in EVERY spelling including the default ones that change "
                "nothing (_RELABEL_NOOP_SPELLING, the priced cost)"
            )
        want = _RELABEL_HOP_SOURCE.get(name)
        if want is not None:
            members = _flow_sequence(fields.get("source_labels", ""))
            if members != [want]:
                defects.append(
                    f"the {name} hop reads source_labels={members} (raw "
                    f"{fields.get('source_labels', '')!r}), want [{want!r}] — "
                    "extra members are joined with the default `;` separator, "
                    "so the hop writes a value nothing in this file names"
                )
    outside = [
        i for i in range(len(entries)) if i not in set(hops.values())
    ]
    if outside:
        defects.append(
            "relabel_configs holds entries outside the triplet at "
            f"{outside} ({[entries[i].strip().splitlines()[0] for i in outside]})"
            " — a later write wins, and one that writes no target_label at all "
            "(labeldrop) takes the keep hop's `instance` back to the exporter "
            "with the probe still succeeding"
        )
    return defects, hops


def _scrape_target_port(body: str, job: str, host: str) -> str | None:
    """Port of `<host>:<port>` in prometheus.yml.j2's `<job>` static target."""
    block = _scrape_job_block(body, job)
    if not block:
        return None
    t = re.search(rf'(?m)^[^\S\n]*-[^\S\n]*{re.escape(host)}:(\d+)[^\S\n]*$', block)
    return t.group(1) if t else None


_DURATION_UNITS = {
    "ms": 0.001, "s": 1.0, "m": 60.0, "h": 3600.0,
    "d": 86400.0, "w": 604800.0, "y": 31536000.0,
}


def _duration_seconds(value: str | None) -> float | None:
    """A Prometheus duration (`30s`, `1m`, `1m30s`) in seconds, or None.

    Returns a NUMBER so two durations can be COMPARED, which is the whole reason
    this exists: `scrape_timeout <= scrape_interval` is a relation Prometheus
    enforces at load time (it refuses the config outright), and a string compare
    of `30s` against `1m` gets it backwards. The plex-exporter job is the first
    in this file to set either key.

    Fails CLOSED on anything Prometheus itself would refuse: a bare number
    (`60`), a unit it does not know, or a negative value all return None, and
    every caller treats None as "the pair is not there". Prometheus' own grammar
    is a sequence of `<int><unit>` chunks, so the compound form is accepted here
    for the same reason it is accepted there — `1m30s` is one duration, not two.
    """
    if not value:
        return None
    v = _yaml_unquote(value)
    if not re.fullmatch(r'(?:\d+(?:ms|[smhdwy]))+', v):
        return None
    return sum(
        int(num) * _DURATION_UNITS[unit]
        for num, unit in re.findall(r'(\d+)(ms|[smhdwy])', v)
    )


def _effective_scrape_pair(body: str, block: str) -> dict:
    """What Prometheus ACTUALLY scrapes one job at — interval and timeout, seconds.

    Step 4d shipped this read inline; row 5c is the fourth and fifth job to need
    it and the row that says so — three copies of a resolution rule is where the
    copies start disagreeing. `PROM_DEFAULT_SCRAPE_TIMEOUT` is here rather than
    at each call site for the same reason: a job that sets NEITHER key is not a
    job with no timeout, it is a job on Prometheus' own 10 s, and a clause that
    read `None` there would be comparing a pair that is not the pair the process
    uses.

    The dict keeps the raw halves as well as the resolved ones because both are
    claims a caller may need to make, and they are DIFFERENT claims:
    `timeout_fits` is about the EFFECTIVE pair (it is the relation Prometheus
    refuses a config over), while `interval_is_job_local` is about
    `job_interval` alone — 4d's own rows, where `global` is 15 s too, so deleting
    the job's key leaves the effective read unchanged and GREEN.
    """
    global_block = _key_bounded_block(body, "global", 0)
    job_interval = _duration_seconds(_block_scalar(block, "scrape_interval"))
    job_timeout = _duration_seconds(_block_scalar(block, "scrape_timeout"))
    global_interval = _duration_seconds(_block_scalar(global_block, "scrape_interval"))
    global_timeout = _duration_seconds(_block_scalar(global_block, "scrape_timeout"))
    return {
        "interval": job_interval if job_interval is not None else global_interval,
        "timeout": (
            job_timeout if job_timeout is not None
            else global_timeout if global_timeout is not None
            else PROM_DEFAULT_SCRAPE_TIMEOUT
        ),
        "job_interval": job_interval,
        "job_timeout": job_timeout,
        "global_interval": global_interval,
        "global_timeout": global_timeout,
    }


def _bucket_values(block: str) -> list | None:
    """The `buckets:` value as floats — flow (`[a, b]`) or block (`- a`) form.

    Returns None when the key is absent, which is a different failure from a key
    present with the wrong values; the diagnostic prints the parsed list either way.
    """
    # `[^\S\n]` and not `\s`: a greedy `\s*` runs past the newline and swallows the
    # first `- 0.1` item of a block sequence into the inline group.
    m = re.search(r'(?m)^[^\S\n]*buckets:[^\S\n]*(.*)$', block)
    if not m:
        return None
    num = r'-?\d+(?:\.\d+)?'
    inline = m.group(1).strip()
    if inline.startswith("["):
        raw = re.findall(num, inline)
    else:
        raw = []
        # m.end() sits before the key line's newline, so drop it before splitting.
        for line in block[m.end():].lstrip("\n").splitlines():
            item = re.match(rf'\s*-\s*({num})\s*$', line)
            if not item:
                break
            raw.append(item.group(1))
    return [float(x) for x in raw]


def test_prometheus_histogram_buckets_tuned() -> bool:
    """plex-monitoring Step-1: metrics.prometheus pins the custom latency buckets.

    Pins the VALUES in ascending order and pins them INSIDE the
    `metrics.prometheus` block — presence of the key `buckets` anywhere in the file
    is not the claim. Three pins, each failing differently:

    * `matches` — the template's list equals EXPECTED, inside the two-hop slice.
    * `expected_ascending` / `expected_len` — EXPECTED is itself strictly ascending
      and 13 long, so a later edit of the constant cannot quietly relax the
      ordering or the resolution it exists to pin. Printed separately: a dropped
      boundary and a reordering are different defects and a RED should say which.
    * `is_custom` — EXPECTED differs from TRAEFIK_DEFAULT_BUCKETS. Without this the
      whole check is satisfiable by writing out the pinned image's own default,
      which changes bytes on disk and nothing in the emitted `le` series. That is
      exactly what this check shipped as first; see the constants above.

    ...and five EXISTENCE pins, because boundaries pin the shape of a series whose
    EXISTENCE was unguarded, and the switches that delete it sit inches above the
    key they qualify. Every one of these was GREEN here — and GREEN through the
    whole `just test` gate — until they were added. Measured on the rendered
    artifact and traefik:v3.7.5 (logs/calibration-step01a-emission-surface.log;
    the control row in every case is the OTHER histogram still reporting 14
    series, which is what makes it a lost series rather than a dead container):

    * `entrypoint_labels` — `addEntryPointsLabels: true`. Flipped to false the
      proxy stays up and emits ZERO `traefik_entrypoint_*`, so the plan's own Demo
      query returns nothing while the service histogram is untouched at 14.
    * `service_labels` — `addServicesLabels: true`. Flipped to false the service
      histogram vanishes; `entrypoint - service` is Traefik's own overhead, i.e.
      the decision variable Steps 2-4 are built on.
    * `entry_point` — `entryPoint: metrics`. Deleted, Traefik falls back to its
      default entrypoint name `traefik` (`traefik --help`), :8082 still answers,
      and BOTH families are gone from it.
    * `port_agrees` — the port of that entrypoint's `address` equals the port
      prometheus.yml.j2's `traefik` scrape job targets. Both sides are DERIVED, so
      moving the endpoint and the scraper together stays green (that pairing is
      what proves this is an agreement and not a hard-coded 8082); moving either
      one alone reddens. Live, `:8082 -> :8083` on the template alone leaves the
      scrape port unreachable with the series intact one port over.
    * `peer_reachable` — the HOST half of that same address. A port pin alone is
      green through `":8082" -> "127.0.0.1:8082"`, which is the same defect one
      token to the left and the silent one of the two: measured on the rendered
      artifact (logs/calibration-step01a-bind-host.log), the proxy still answers
      200 on `websecure` AND the endpoint still answers 200 on the container's own
      loopback, so nothing is down — only a PEER, which is the network position
      Prometheus occupies, gets nothing at all (peer_scrape=000, 0 series of
      either family, against 200 and 14/14 on the control). The clause is an
      allow-list of the all-interfaces spellings (`PEER_REACHABLE_HOSTS`), not a
      ban on host prefixes; `0.0.0.0:8082` and `[::]:8082` scrape 200 from a peer
      exactly like the pristine form and must stay green.

    Two of these are deliberately STRICTER than the runtime, and say so rather
    than implying a regression they do not cause: the label switches default to
    `true` in Traefik (`traefik --help`), so deleting them still emits, and
    renaming the entrypoint on BOTH sides at the same port is runtime-equivalent
    yet reddens `entry_point`. Both keep the emission surface explicit in the file
    instead of inherited from an upstream default or a moving name. The pins
    carrying the actual runtime contract are `port_agrees` and `peer_reachable`
    TOGETHER — an address has more than one field, and each field moves the
    endpoint out from under the scraper on its own.
    """
    static = _read(STATIC)
    block = _metrics_prometheus_block(static)
    found_block = bool(block.strip())
    values = _bucket_values(block)
    expected_ascending = all(
        a < b for a, b in zip(EXPECTED_BUCKETS, EXPECTED_BUCKETS[1:])
    )
    expected_len = len(EXPECTED_BUCKETS) == 13
    is_custom = EXPECTED_BUCKETS != TRAEFIK_DEFAULT_BUCKETS
    matches = values == EXPECTED_BUCKETS
    # The emission surface: family enabled, endpoint where the scraper looks.
    # These two `.lower()` calls stay, for `verify_ssl_off`'s reason and not by
    # habit: these are YAML BOOLEANS and traefik:v3.7.5's own loader folds them.
    # Measured, both spellings on the pinned image, one request through `web`:
    # `true` and `True` are byte-identical — status running, /metrics 200, the
    # same single `traefik_entrypoint_requests_total` and
    # `traefik_service_requests_total` series (logs/calibration-step03a-yaml-bool.log).
    # Contrast `env_pinned` in `test_plex_exporter_service_block`, which lost its
    # `.lower()` this round because THAT runtime is case-sensitive.
    entrypoint_labels = (_block_scalar(block, "addEntryPointsLabels") or "").lower() == "true"
    service_labels = (_block_scalar(block, "addServicesLabels") or "").lower() == "true"
    entry_point = _block_scalar(block, "entryPoint")
    ep_host, ep_port = (
        _entrypoint_address(static, entry_point) if entry_point else (None, None)
    )
    scrape_port = _scrape_target_port(_read(PROM_SCRAPE), "traefik", "traefik")
    port_agrees = ep_port is not None and ep_port == scrape_port
    peer_reachable = ep_host is not None and ep_host in PEER_REACHABLE_HOSTS
    ok = (
        found_block and expected_ascending and expected_len and is_custom and matches
        and entrypoint_labels and service_labels and entry_point == "metrics"
        and port_agrees and peer_reachable
    )
    print(
        f"{'OK' if ok else 'FAIL'}: metrics.prometheus pins histogram buckets "
        f"{EXPECTED_BUCKETS} (block={found_block}, in_block={values}, "
        f"expected_ascending={expected_ascending}, expected_len={expected_len}, "
        f"is_custom={is_custom}, entrypoint_labels={entrypoint_labels}, "
        f"service_labels={service_labels}, entry_point={entry_point}, "
        f"port_agrees={port_agrees} ({entry_point}:{ep_port} vs scrape traefik:{scrape_port}), "
        f"peer_reachable={peer_reachable} (bind host {ep_host!r}))"
    )
    return ok


# plex-monitoring Step 2a: the Proxmox VE exporter, repo side. The token VALUE
# and the deploy are Step 2b (operator) and nothing below touches them.
#
# `prometheus-pve-exporter` is a MULTI-TARGET exporter, and that one fact decides
# the shape of every check here. PVE metrics are served from
# `/pve?target=<host>&cluster=1&node=1`; the default `/metrics` path serves only
# the exporter's OWN scrape/process metrics. So a job pointed at
# `pve-exporter:9221` with no `metrics_path` answers **200** -> the target reads
# **UP** in Status->Targets -> and there are **zero `pve_*` series`. Target-level
# health cannot tell that failure from success, which is why the repo-side pin
# has to: PVE_MULTI_TARGET_PATH and the `__param_target` relabel are the sharp
# checks, not "a job named pve-exporter exists". Same class as the Step-1 bucket
# defect above — a change that looks like a change but isn't — caught before
# deploy instead of after.
PVE_MULTI_TARGET_PATH = "/pve"
# What a job with no `metrics_path` scrapes instead. Here so the check can assert
# the pinned path DIFFERS from it, the way `is_custom` asserts EXPECTED_BUCKETS
# differs from Traefik's default: without that clause the check is satisfiable by
# the exact no-op it exists to forbid.
PVE_EXPORTER_DEFAULT_PATH = "/metrics"
PVE_EXPORTER_ADDRESS = "pve-exporter:9221"
# The URL params the job sends explicitly. THEY ARE THE EXPORTER'S OWN DEFAULTS,
# and this comment used to say the opposite. Measured against the shipped image:
# `pve_exporter/http.py` declares
# `def on_pve(self, module='default', target='localhost', cluster='1', node='1')`,
# and A/B'ing the running container against a stub PVE API that logs request
# paths gives an IDENTICAL API-call set and metric set with the params and with
# no params at all (`cluster=0&node=0` makes zero calls, as the control).
# So these pins are STRICTER THAN THE RUNTIME CONTRACT — same honesty rule as
# `addEntryPointsLabels`/`addServicesLabels` above, which also default to on.
# They are kept because explicit beats implicit against a default that upstream
# may move, and because upstream's own README writes them out; they are NOT what
# makes `pve_up{id="lxc/110"}` exist. The pins carrying the actual runtime
# contract are `metrics_path: /pve` and the `__param_target` relabel.
PVE_REQUIRED_PARAMS = {"cluster": "1", "node": "1"}
# The env var carrying the secret, and the vault key behind it. Named once and
# used on BOTH sides (env.j2 assigns it, compose dereferences it) so the checks
# can assert the two AGREE rather than hard-coding the string twice.
PVE_TOKEN_ENV = "PVE_TOKEN_VALUE"
PVE_VAULT_KEY = "vault_pve_api_token"
# The env vars compose MUST take from role defaults, and the defaults var behind
# each. Same agreement shape as `port_agrees`: both the compose check and the
# defaults check read this map, so a rename on one side alone reddens, and a
# value edited into compose as a LITERAL (a realm-less `PVE_USER=prometheus`, a
# token name that no longer matches the minted ID) cannot satisfy either.
# Measured, not assumed: with `PVE_TOKEN_NAME` deleted from the compose block the
# real 3.9.0 image answers `/pve` with HTTP 500, `proxmoxer ... "No valid
# authentication credentials were supplied"`, and makes zero PVE API calls.
PVE_DEFAULT_VARS = {
    "PVE_USER": "docker_host_pve_user",
    "PVE_TOKEN_NAME": "docker_host_pve_token_name",
}
# Non-secret PVE coordinate, committed since before this step (mise.toml,
# PROXMOX_VE_ENDPOINT). It belongs in role defaults, NOT the vault — the checks
# below assert the two spellings agree instead of pinning the literal twice.
PVE_API_HOST = "192.168.1.50"
# Step-2a F1, round 5. The keys a service reachable ONLY over the internal
# compose network is allowed to declare. This is an allow-list and not a list of
# forbidden keys on purpose: a forbidden-key list is an absence pin, it is
# bounded by whoever wrote it, and it fails OPEN one key past its edge. Three
# rejections walked that edge outwards — the block spelling of `ports:`, then
# every spelling of `ports:`, then `network_mode: host`, which needs no `ports:`
# key at all. Measured on the real prompve/prometheus-pve-exporter:3.9.0, same
# image, same command, same env, ONE service key different
# (logs/calibration-step02a-f1-round5.log, leg B):
#   compose network, no ports  ->  ss -ltn has no :9221 line, and an anonymous
#                                  GET http://192.168.1.60:9221/metrics is 000
#   network_mode: host         ->  LISTEN *:9221 in the HOST netns, and the same
#                                  anonymous GET is HTTP 200, 3174 bytes
# Every evasion renders, parses with the key landing as a real service key, and
# `docker compose config` returns rc=0 (leg A) — so `just play` SHIPS them; none
# is a syntax error the operator would catch.
# Membership is deliberately narrow: these are the keys the two services declare
# today, so anything new — `networks:`, `expose:`, `hostname:`, or a compose key
# that does not exist yet — reddens and has to be argued for in the clause that
# claims the service is unreachable. That is STRICTER THAN THE RUNTIME for the
# benign ones (`expose:` publishes nothing on its own, `networks: [default]` is
# the implicit membership spelled out), and it is the point: this clause cannot
# be satisfied by a key nobody enumerated.
# Round 6 completes that claim, which until then held only for keys the guard
# could READ: an allow-list is bounded by its parser, and `_service_key_lines`
# used to DISCARD every line `_yaml_key` could not parse, so a key arriving
# without a parsable key line was invisible to the list. It now fails CLOSED on
# those lines instead — see `_line_class` for the four deployable spellings that
# were green through this constant, and for what `doc`/`seq` are exempted for.
SCRAPE_ONLY_KEYS = {"image", "restart", "environment", "command"}
OUTBOUND_ONLY_KEYS = {"image", "restart", "environment", "command", "depends_on"}

# --- plex-monitoring Step 3: the Plex Media Server exporter -------------------
# Named once each and consumed on BOTH sides wherever two files have to agree
# (compose declares the service, prometheus.yml scrapes it), the same shape
# `PVE_TOKEN_ENV` and `PVE_DEFAULT_VARS` use: a rename on one side alone reddens.
PLEX_EXPORTER_SERVICE = "plex-exporter"
PLEX_EXPORTER_PORT = "9594"
PLEX_EXPORTER_ADDRESS = f"{PLEX_EXPORTER_SERVICE}:{PLEX_EXPORTER_PORT}"
# THE trap this step exists to avoid, and it points the OTHER WAY from Step 2's.
# `pve-exporter` is multi-target, so its job needs `metrics_path: /pve` or it
# reads UP with zero series. This exporter is NOT: `config.ru` mounts
# `Prometheus::Middleware::Exporter` and the collector runs only when
# `PATH_INFO == "/metrics"` exactly, so it serves its metrics on the plain
# default path and every key of the Step-2 shape is wrong here — a
# `metrics_path` is a 404, `params` are ignored, and a `__param_target` relabel
# has nothing to rewrite. Copying the neighbouring job is the cheapest possible
# regression, which is why the absence of these three keys is pinned rather than
# left to review.
#
# AND IT IS PINNED AS AN ALLOW-LIST, not as the absence of those three (round 7).
# An absence pin is bounded by the enumeration behind it and fails OPEN past its
# edge — the same defect `_service_key_lines` was written for one file over, found
# here by the r7 review: `file_sd_configs:` on this job loads a second set of
# targets from disk, `scheme: https` sends every scrape at a TLS port this exporter
# does not serve, and both are `promtool check config` rc=0 on the pinned
# prom/prometheus:v3.12.0 (logs/red-step03a-jinja-key-pre.log, leg P) while the
# three-key enumeration read GREEN at PASS 39/39. These are the keys the job MAY
# declare; everything else, invented or not yet invented, is outside.
PLEX_JOB_KEYS = ("scrape_interval", "scrape_timeout", "static_configs")
# The env var carrying the secret and the vault key behind it, used on both
# sides (env.j2 assigns it, compose dereferences it) — see PVE_TOKEN_ENV.
PLEX_TOKEN_ENV = "PLEX_TOKEN"
PLEX_VAULT_KEY = "vault_plex_token"
# The exporter's Plex address, and the role-defaults var that must supply it.
# `docker_host_plex_url` predates this step (it is the backend Traefik's file
# provider already uses for the public Plex router), so this is a REUSE pin: a
# second literal spelling of the Plex CT address is the defect.
PLEX_ADDR_ENV = "PLEX_ADDR"
PLEX_URL_VAR = "docker_host_plex_url"
PLEX_EXPORTER_IMAGE_VAR = "docker_host_plex_exporter_image"
# Configuration is env-var only on this image — `collector.rb`'s `initialize`
# reads exactly these, there is no config file and no CLI flag, so the service
# carries NO `command:` (one region fewer than `pve-exporter`). Values are the
# image's own defaults except where noted; they are written out and pinned for
# the reason `PVE_REQUIRED_PARAMS` gives — explicit beats implicit against a
# default upstream may move — and this exporter's last release was 2024-12-22,
# so "upstream may move" is a live risk rather than a slogan.
#
#   PORT     — the port the scrape job dials. Pinned as an AGREEMENT with the
#              job's target below, not as two copies of 9594.
#   PLEX_TIMEOUT / PLEX_RETRIES_COUNT
#            — per-request budget inside a scrape that runs the library sweep
#              SYNCHRONOUSLY. Retries multiply that budget, so 0 is what keeps
#              the job's own `scrape_timeout` meaningful.
#   PLEX_SSL_VERIFY
#            — `docker_host_plex_url` is plain HTTP over the LAN, so this is
#              inert today and pinned so that a future https:// move is a
#              deliberate edit rather than a silent one.
#   METRICS_PREFIX
#            — LOAD-BEARING for everything downstream: it is the first token of
#              every series name 3b falsifies on (`plex_media_count`,
#              `plex_sessions_count`) and every Step-4 dashboard query. It is
#              the image's default, so nothing in the container reddens if it
#              moves — only the queries, silently, at read time.
#   METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS
#            — how often the synchronous library sweep runs. Paired with the
#              job's interval/timeout below; the two are one budget.
PLEX_EXPORTER_ENV = {
    "PORT": PLEX_EXPORTER_PORT,
    "PLEX_TIMEOUT": "10",
    "PLEX_RETRIES_COUNT": "0",
    "PLEX_SSL_VERIFY": "true",
    "METRICS_PREFIX": "plex",
    "METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS": "1800",
}
# Prometheus' own default scrape timeout, applied to any job that does not set
# one. `PLEX_TIMEOUT` alone is 10 s PER REQUEST and the library sweep issues one
# request per section (plus one more per `show` section) inside the scrape, so a
# job left on this default cannot complete a sweep. Here so the check can assert
# the pinned timeout EXCEEDS it, the way `is_custom` asserts the buckets differ
# from Traefik's own default: without that clause the pair is satisfiable by
# writing out the numbers that were already in force.
PROM_DEFAULT_SCRAPE_TIMEOUT = 10.0

# --- plex-blip Step 4d: CT 110's node-exporter --------------------------------
# The one job in this file whose target is NOT on the compose network. CT 110 is
# a separate LXC, so the scrape crosses the LAN and every coordinate it needs
# lives in a role this file may READ and must not edit.
#
# THE JOB NAME IS NOT `node-exporter`: that name is taken at the top of the
# template by the docker host's OWN exporter, and `_scrape_job_block` returns ""
# for a name that resolves twice, so a collision reddens rather than picks. Two
# jobs emitting the same `node_*` families are told apart downstream by `job` and
# by `instance`, which is why neither needs a relabel.
PLEX_NODE_JOB = "plex-node-exporter"
# The inventory coordinates, named ONCE and consumed twice — the expression the
# template must carry is built from them, and the census below looks the same
# names up in `inventory/hosts.yml`. Renaming the constant alone therefore
# cannot pass: the template stops matching, and pointing the template back at
# the new name reddens the census unless the inventory really carries it.
PLEX_INVENTORY_GROUP = "plex"
PLEX_INVENTORY_HOST = "plex"
# THE ONE SPELLING THIS FILE'S OWN LINE READER ACCEPTS, and it is a constraint
# rather than a preference. `PROM_SCRAPE` is a member of `LINE_READ_TEMPLATES`,
# so every `{{ }}` it carries must `fullmatch` `_LINE_BOUNDED_EXPR` — a bare
# reference with at most `| default(<literal>)`. Measured against the compiled
# regex rather than read off it: `hostvars['plex'].ansible_host` and
# `hostvars['plex']['ansible_host']` pass; the rename-robust
# `hostvars[groups['plex'] | first].ansible_host` is REFUSED ("not a bare
# reference — its output is computed, not shown"), as is the `[0]` form.
#
# So the accepted spelling names the host as a LITERAL, and `gen_inventory.py`
# takes that name from tofu's `plex_name` output (:76) while the GROUP name is
# structural (:74) — a literal agreeing with generated data. The discharge is the
# `inventory_has_host` census below: a tofu rename reds this gate instead of
# silently pointing the job at a host `hostvars` does not have.
PLEX_NODE_TARGET_EXPR = f"{{{{ hostvars['{PLEX_INVENTORY_HOST}'].ansible_host }}}}"
# The far end of the port relation. `plex_node_exporter_listen_address` is what
# the plex role's drop-in passes to `--web.listen-address`, so the port the
# exporter BINDS and the port this job DIALS are one decision — and this file
# must not make it twice. `0.0.0.0` is a bind wildcard and not a scrape host, so
# only the PORT half relates; comparing the addresses whole can only ever be red.
PLEX_ROLE_DEFAULTS = PLEX_ROLE / "defaults" / "main.yml"
PLEX_NODE_LISTEN_VAR = "plex_node_exporter_listen_address"
# `task-1786167365-e571` is why only ONE end of the port relation is read out of
# the plex role. A guard that compares a render against the variable it rendered
# FROM is a tautology — that row left its suite 9/9 GREEN over a 203/EXEC crash
# loop — so the second end here is this template's own literal port, never a
# second read of the plex default.
#
# THE OTHER HALF OF THE RELATION — that something in the plex role still PASSES
# that variable to `--web.listen-address`, or the default is a value nothing
# reads — IS NOT CHECKED HERE, AND THAT IS DELIBERATE. It is already held by the
# clause named below, which shipped one wave earlier and names this row by task
# key in its own docstring. Two guards over one fact is `task-1786153086-9f13`'s
# class one level up, and it was measured to be worse in BOTH directions: a
# file-wide substring here goes GREEN when the flag is hardcoded and the variable
# survives in a comment / on an `Environment=` line / on a different flag, and it
# goes RED on `{{var}}` and `{{  var  }}` — legal Jinja reformats the cited clause
# deliberately normalises (`_normalise_refs`, with a comment saying why).
#
# A citation is only worth one parser while the cited clause EXISTS and RUNS, so
# `far_end_is_held` reads that module with `ast`: the function must be defined
# and must be reached by that module's own code — which in a `scripts/test_*.py`
# file is what puts it in the gate (`run_gate.py` globs this directory and runs
# each file's `__main__`).
PLEX_NODE_FAR_END_SUITE = REPO_ROOT / "scripts" / "test_plex_node_exporter_shape.py"
PLEX_NODE_FAR_END_CLAUSE = "test_the_listen_address_is_a_variable_the_scrape_job_can_pin"
# The watchdog writes the `.prom` this job exists to collect, and its refresh
# cadence is a plain keyword default with no CLI flag in the shipped unit — so
# 15.0 s is what actually runs. Design §4.5 sets the scrape at 15 s: one decision
# with an end in each role, which is `task-1786159059-184b`'s subject. Pinned as
# an EQUALITY, because the relation that survives the mutation that row measured
# (the default moved to 86400.0) is equality and not `<=`.
PLEX_WATCHDOG_SOURCE = PLEX_ROLE / "files" / "plex_blip_watchdog.py"
PLEX_WATCHDOG_REFRESH_PARAM = "textfile_refresh_sec"
# Same allow-list shape as `PLEX_JOB_KEYS`, and for the same reason: an absence
# pin fails open one key past its edge. `metrics_path` is the key that matters —
# node-exporter serves the plain default path, so a `/pve`-style path copied off
# the neighbouring job is a 404 whose target reads DOWN with the series nowhere.
PLEX_NODE_JOB_KEYS = ("scrape_interval", "scrape_timeout", "static_configs")

# --- plex-blip-manual-triage Step 5a: the blackbox-exporter ------------------
# Named once and consumed on BOTH sides, the `PLEX_EXPORTER_ADDRESS` shape: this
# row defines the modules, and row `5c`'s scrape jobs carry them as a `module=`
# query parameter. That parameter is a JOIN NO PROCESS CHECKS — a job naming a
# module `blackbox.yml` does not define gets HTTP 400 from `/probe` and the
# target reads DOWN with no series and nothing erroring in either config — so
# `5c` must read its `params.module` values against THIS tuple rather than
# against literals of its own, exactly as `PLEX_EXPORTER_ADDRESS` is read on both
# the compose and the prometheus.yml side.
BLACKBOX_SERVICE = "blackbox-exporter"
BLACKBOX_CONFIG = TEMPLATES / "blackbox.yml.j2"
# Design §4.6's three probes. `5a` shipped the two that need no credential and
# said so here: "`5b` therefore ADDS a member — set equality below means the tuple
# and the template move together, which is the point." This is that edit, and it
# is the whole of what the tuple is for: `5c` reads THIS for its `params.module`
# values, so a name added to the template and not here reddens as loudly as one
# named by a scrape job and never defined.
BLACKBOX_DIRECT_MODULE = "plex_identity_direct"
BLACKBOX_PROXIED_MODULE = "plex_identity_proxied"
# Step 5b. The DB-TOUCHING probe, and the only one of the three that needs a
# credential — which is why it is a row of its own rather than a third entry in
# `5a`'s commit. `/identity` answered HTTP 200 through the whole five-minute
# outage of 2026-08-07 while `/status/sessions` reached 101,394 ms
# (research/live-blip-2026-08-07-case-study.md), so this is the probe the
# differential is actually made of.
BLACKBOX_SESSIONS_MODULE = "plex_sessions"
BLACKBOX_MODULES = (
    BLACKBOX_DIRECT_MODULE, BLACKBOX_PROXIED_MODULE, BLACKBOX_SESSIONS_MODULE
)
# The header that carries the token, pinned as a NAME rather than as "a headers
# block exists". A DIFFERENT header name — `X-Plex-Token2`, `X_Plex_Token`, the
# token sent as `Authorization` — reaches Plex as no credential, and blackbox
# answers `/probe` with HTTP 200 and `probe_success 0` for an auth rejection, so
# the TARGET READS UP either way and a mistyped header key is invisible at the
# target level.
#
# CASE IS THE ONE DIFFERENCE THAT IS NOT A DIFFERENT HEADER, and this comment
# used to claim otherwise in the same words the clause did — the second spelling
# of a false measurement sentence, which is the class this row was rejected for
# once already. `x-plex-token:` in the config arrives on the wire as this exact
# byte string because Go's `Header.Set` canonicalises, measured at
# logs/builder-5b-r2-wire.log. The set equality still reds on it; see
# `test_blackbox_sessions_probe_carries_the_vault_token` for why that false-RED
# is deliberate, why the falsifier is at metric level, and what it costs to get
# there.
BLACKBOX_TOKEN_HEADER = "X-Plex-Token"
# The compose service is scrape-only like `pve-exporter`/`plex-exporter`, plus
# the ONE key those two do not have: it is the first scrape target in this stack
# that reads a rendered config, so it carries `volumes:`. Spelled as its own
# constant rather than by widening `SCRAPE_ONLY_KEYS`, which would hand a bind
# mount to two services that must not have one.
BLACKBOX_SERVICE_KEYS = SCRAPE_ONLY_KEYS | {"volumes"}
# THE MODE IS A MEASUREMENT AND IT CONTRADICTS THE ROUTING THAT ORDERED IT.
# The row was cut saying "prom/blackbox-exporter runs as nobody (uid 65534)
# exactly like prom/prometheus, so 0644 is correct here for the same reason".
# Measured at this row's own parent (logs/builder-5a-image-identity.log) against
# the pinned images themselves:
#
#     prom/prometheus:v3.12.0         Config.User "nobody"   id -> uid=65534
#     prom/blackbox-exporter:v0.28.0  Config.User ""         id -> uid=0(root)
#
# `prom/*` is not one identity. Blackbox declares NO `USER`, so it runs as root
# like `traefik:v3.7.5` and 0640 root:root is readable to it — the mode that
# publishes nothing. 0644 here would be a world-readable file chosen for a reason
# that is false of this image, and it would prejudge `5b`, which adds a live Plex
# token to THIS FILE. That collision is dissolved rather than deferred: root
# reads 0640, so `5b` needs no `owner: 65534` / `0600` pair and no exemption --
# it inherits a mode that already withholds the token from every other user on
# the docker host.
#
# WHAT THIS RESTS ON, so a later edit knows what it is breaking: the compose
# service must not override `user:`. That is not asserted here; it is held by
# `keys_allowed` in `test_blackbox_exporter_service_block`, whose allow-list
# fails closed on `user:` like on any other unenumerated key — the same standing
# the grafana modes have through `test_grafana_provisioning_shape.py`.
BLACKBOX_MODE = "0640"
# THE UID, AND WHERE IT WAS MEASURED — printed by the Step-5b clause rather than
# left in a comment, because it is the fact that decides which invariant this
# file's mode actually carries. `Config.User` is EMPTY on this image and `id -u`
# inside it answers 0, so there is no owner/mode pair here the process cannot
# read and "readable to the container" is NOT what any mode pin below is for.
# What survives is the WORLD bit. Re-measured at this row's own parent rather
# than carried from the routing's log.
BLACKBOX_UID = 0
BLACKBOX_UID_EVIDENCE = "logs/builder-5b-headers-probe.log"

# --- plex-blip-manual-triage Step 5c: the three blackbox scrape jobs ----------
# THE JOB NAMES ARE A CROSS-STEP RELATION AND NOT A CHOICE. Design §5.3 writes
# Step 7's alert rules as `probe_duration_seconds{job="blackbox-plex-identity"}`,
# `{job="blackbox-plex-sessions"}` and `probe_success{job=~"blackbox-plex.*"}`, so
# a rename here leaves three rules matching nothing and firing never — the
# absent-series class this objective measured twice on the way in
# (`task-1786159639-39db` and `task-1786167833-1152`, both closed at `7b`), and
# the one that is invisible because an alert that never fires looks exactly like
# an alert with nothing to say.
#
# THIS CONSTANT IS NO LONGER THE FAR END. At `5c` Step 7 did not exist, so what
# was pinned was the shared PREFIX — and that was a tautology, since
# `BLACKBOX_JOBS`' keys are f-strings built from it. `7a` shipped the rules, so
# `names_are_the_shipped_fan_in` reads the `job=~` patterns out of
# `plex-blip-rules.yml.j2` and `per_job_door` reads the absence door's jobs
# against what those rules select out of `prometheus.yml.j2`. The prefix survives
# as the spelling the three names share, not as anything a clause proves.
BLACKBOX_JOB_PREFIX = "blackbox-plex"
# `blackbox-exporter:9115` — the service name is the constant compose is already
# held to, and the port is the image's own EXPOSE, measured here rather than read
# off a README: `docker inspect prom/blackbox-exporter:v0.28.0` gives
# `ExposedPorts {"9115/tcp":{}}` with `Cmd` = `--config.file=…` and `User` empty
# (logs/builder-5c-image-port.log). compose declares no `ports:` for this service
# precisely because nothing outside the compose network may reach it.
BLACKBOX_PORT = "9115"
BLACKBOX_ADDRESS = f"{BLACKBOX_SERVICE}:{BLACKBOX_PORT}"
# The probe endpoint, and it is the `metrics_path: /pve` lesson in a third
# variant. blackbox serves `/metrics` too — its OWN process metrics — so a job
# that leaves `metrics_path` at Prometheus' default reads UP, produces zero
# `probe_*` series, and errors nowhere. There is no "write out the default
# explicitly" no-op for this clause to be satisfied by (the two paths are
# different endpoints, not a value and its default), which is why this pin has no
# `path_is_not_default` twin the way the pve row does.
BLACKBOX_PROBE_PATH = "/probe"
BLACKBOX_PARAM_MODULE = "module"
# blackbox clamps every probe to `Prometheus' scrape-timeout header minus
# --timeout-offset`, whose default is 0.5 s — the fact blackbox.yml.j2 states at
# :56-59 and again at :144-147, where it calls each module's own `timeout:` "a
# ceiling, not a floor" and says 5c's `scrape_timeout` is what will actually bind.
# That sentence is a claim about THIS row's numbers, so this row holds it: a
# module timeout the effective scrape timeout cannot reach is a value nothing
# reads. `plex_sessions` is where it bites — its 30 s is argued at length against
# the 5 s alert threshold of design §4.6, and Prometheus' own 10 s default would
# clip every measurement at 9.5 s with nothing anywhere reporting a defect.
BLACKBOX_TIMEOUT_OFFSET = 0.5
# The variable that already holds CT 110's address (this role's defaults, for
# Traefik's public Plex router) and the file-provider router whose rule already
# holds the public hostname. NEITHER IS RE-TYPED HERE: a second spelling is "two
# literals that agree until one moves", the c6c4/e627 class this objective
# charged three times in Step 4 alone. The direct probes carry the variable as a
# bare reference; the proxied probe's host is READ OUT of dynamic.yml.j2's router
# rule at check time, so retargeting either end moves the guard with it.
PLEX_URL_REF = f"{{{{ {PLEX_URL_VAR} }}}}"
DYNAMIC_PLEX_ROUTER = "plex"
PROXIED_SCHEME = "https://"
# (module, effective scrape interval in seconds, path, whether the origin is the
# LAN address or the public route). Design §4.6's table, and the modules come
# from `BLACKBOX_MODULES` rather than from three literals of their own — the
# `module=` query parameter is a JOIN NO PROCESS CHECKS: a job naming a module
# `blackbox.yml` does not define gets HTTP 400 from `/probe`, so the target reads
# DOWN with no series and neither config is invalid.
BLACKBOX_JOBS = {
    f"{BLACKBOX_JOB_PREFIX}-identity": {
        "module": BLACKBOX_DIRECT_MODULE,
        "interval": 15.0,
        "path": "/identity",
        "proxied": False,
    },
    f"{BLACKBOX_JOB_PREFIX}-sessions": {
        "module": BLACKBOX_SESSIONS_MODULE,
        "interval": 60.0,
        "path": "/status/sessions",
        "proxied": False,
    },
    f"{BLACKBOX_JOB_PREFIX}-proxied": {
        "module": BLACKBOX_PROXIED_MODULE,
        "interval": 15.0,
        "path": "/identity",
        "proxied": True,
    },
}
# The allow-list shape `PLEX_JOB_KEYS` established, for the reason stated there:
# an absence pin is bounded by the enumeration behind it and fails OPEN one key
# past its edge. What it keeps out here is a credential — `basic_auth:`,
# `authorization:` and `bearer_token_file:` are all legal scrape-config keys and
# all of them would put a secret in the 0644 render this row's fence forbids —
# and `scheme:`/`file_sd_configs:`, the two `promtool` accepts at rc=0 that the
# Step-3 row measured on the neighbouring job.
BLACKBOX_JOB_KEYS = (
    "metrics_path", "params", "scrape_interval", "scrape_timeout",
    "static_configs", "relabel_configs",
)
# The prometheus render's own comment, and the sentence that LICENSES its 0644.
# `ansible/roles/docker_host/tasks/main.yml` says the scrape config "carries no
# credential (the PVE token is an env var from the 0600 .env)" and therefore that
# world-read costs nothing. Row 5c is the first row to write scrape jobs that
# COULD carry one — a `params:` entry, a `?X-Plex-Token=` suffix on a target —
# so the sentence stops being background and becomes a thing to hold.
PROM_NO_CREDENTIAL_PROSE = "carries no credential"

# --- plex-blip-manual-triage Step 5d: how long the TSDB keeps a blip ----------
PROMETHEUS_SERVICE = "prometheus"
PROMETHEUS_RETENTION_FLAG = "--storage.tsdb.retention.time"
# 90 DAYS, AND THE NUMBER IS THIS OBJECTIVE'S OWN UNIT OF EVIDENCE. The fault
# every other row here instruments is sporadic and is read by CORRELATING WEEKS
# (research/live-blip-2026-08-07-case-study.md), so the window has to be longer
# than the interval between two occurrences, not longer than one of them.
PROMETHEUS_RETENTION = "90d"
# WHAT THE STACK RUNS TODAY — measured on the process, not read off the docs.
# The compose `command:` REPLACES the image's CMD (that sentence belongs to
# `no_command` in `test_plex_exporter_service_block` and is cited, not
# re-spelled), and today that list is one `--config.file` entry, so no retention
# is set anywhere and the binary takes its built-in default: row K of
# `PROMETHEUS_RETENTION_EVIDENCE` logs `msg="TSDB retention updated"
# duration=15d`. Nothing warns, and `=15d` written out EXPLICITLY is a document
# the binary loads at rc=0 (row N of the same log) — which is why the clause
# below reads the VALUE and would be the `658f`/`9cb9` presence-only class if it
# read anything less.
PROMETHEUS_RETENTION_DEFAULT = "15d"
# `--storage.tsdb.path` IS NOT SET AND MUST NOT BE SET TO `/prometheus`, and the
# whole of that is a measurement. `docker image inspect prom/prometheus:v3.12.0`
# gives `WorkingDir=/prometheus`, `User=nobody` and a `Cmd` carrying
# `--storage.tsdb.path=/prometheus`; the binary's own `--help` gives
# `--storage.tsdb.path="data/"`, RELATIVE. Driven both ways against a host
# directory bind-mounted at `/prometheus` rather than left as that inference
# (rows K and L of `PROMETHEUS_RETENTION_EVIDENCE`):
#
#     K  no path flag (TODAY)                 -> /prometheus/data/{wal,queries.active}
#     L  CONTROL, the image's own CMD value   -> /prometheus/{wal,queries.active}
#
# So the TSDB already lives inside the `prometheus-data` volume, one level down,
# and survives the recreate this row's change causes. Restoring the flag the
# image CMD had is therefore the SILENT trap and not the repair: run L starts the
# server on an empty directory while every existing block sits at
# `/prometheus/data`, still on the volume and invisible to the process — no
# error, no crash loop, and the retention this row sets would be applied to
# nothing. Hence the clause admits every spelling that RESOLVES to the directory
# absence resolves to, and reds on the trap.
#
# RESOLVES, not equals — round 2, and the first spelling of this pin was a
# false-RED on a correct tree. `data/` is the flag's OWN DOCUMENTED DEFAULT
# written out, and an explicit value equal to the default cannot be a defect;
# the equality against `PROMETHEUS_TSDB_DIR` reddened on it anyway. So the reader
# below does what the binary does — join the value onto the image WORKDIR — and
# every row of that join is measured, not inferred (`logs/builder-5d-r2-
# premises.log`, one live container per row, `wal` located on the bind mount):
#
#     P0  no path flag (TODAY)                  -> /prometheus/data/wal   ADMIT
#     P1  --storage.tsdb.path=data/             -> /prometheus/data/wal   ADMIT
#     P1b --storage.tsdb.path=data              -> /prometheus/data/wal   ADMIT
#     P1c --storage.tsdb.path=/prometheus/data  -> /prometheus/data/wal   ADMIT
#     P2  --storage.tsdb.path=/prometheus       -> /prometheus/wal        RED
PROMETHEUS_TSDB_PATH_FLAG = "--storage.tsdb.path"
PROMETHEUS_TSDB_PATH_DEFAULT = "data/"
PROMETHEUS_WORKDIR = "/prometheus"
PROMETHEUS_TSDB_DIR = "/prometheus/data"
# THE SIBLING KNOB, AND IT IS THE ONLY SILENT ONE. A value-pin on the time flag
# is undone by the OTHER flag that bounds the same TSDB, not only by another
# spelling of the same flag: `--storage.tsdb.retention.size=1MB` beside a green
# `=90d` is rc=0, and the process logs `duration=90d size=1MiB` and prunes in
# minutes (row S2). The binary's own `--help` relates the two in ONE sentence —
# "If neither this flag nor \"storage.tsdb.retention.size\" is set, the retention
# time defaults to 15d". Every OTHER knob that could bound the same thing was
# driven and every one of them REFUSES TO START, which is why exactly one is
# pinned here and the rest are named instead of guarded (same log):
#
#     X1  --storage.tsdb.retention=90d            rc=1  unknown long flag
#     X2  --storage.tsdb.retention.percentage=50  rc=1  unknown long flag
#                                                 (the log line prints the field;
#                                                  no flag sets it)
#     X3  --storage.agent.retention.max-time=4h   rc=3  "can only be used in
#                                                  agent mode"
#     X4  --storage.tsdb.retention.size=1MB       rc=0  STARTS  <-- the hole
#
# Under `restart: unless-stopped` X1-X3 are a crash loop an operator sees. X4 is
# a healthy container that keeps a day of data while the clause prints 90d.
PROMETHEUS_SIZE_CAP_FLAG = "--storage.tsdb.retention.size"
PROMETHEUS_RETENTION_EVIDENCE = "logs/builder-5d-premises.log"
PROMETHEUS_SIBLING_EVIDENCE = "logs/builder-5d-r2-premises.log"

# --- plex-blip-manual-triage Step 7a: design 5.3's alert rules ----------------
# The FIRST rule file this stack has ever had: `rule_files:` is zero hits across
# `ansible/` at `2e8280c`, so Prometheus has been evaluating nothing since it was
# provisioned and every detection in this objective has depended on a human
# noticing a paused stream.
PROM_RULES = TEMPLATES / "plex-blip-rules.yml.j2"
PROM_RULES_KEY = "rule_files"
PROM_RULES_GROUP = "plex-blip"
# THE SPELLING IS A LITERAL PATH AND A GLOB IS REFUSED, and both halves are
# measured on the pinned `prom/prometheus:v3.12.0` rather than argued
# (`PROM_RULES_LITERAL_EVIDENCE`, five `promtool` legs with a positive control in
# each direction):
#
#     B   rule_files: [<literal>], file present      rc=0  "SUCCESS: 1 rule files
#                                                          found" + "SUCCESS: 7
#                                                          rules found"
#     C   rule_files: [<literal>], file ABSENT       rc=1  "… does not point to an
#                                                          existing file"
#     C2  rule_files: ["…/rules/*.yml"], dir EMPTY   rc=0  "… is valid prometheus
#                                                          config file syntax",
#                                                          and the "N rule files
#                                                          found" line is simply
#                                                          ABSENT
#     C3  the same GLOB with the file present        rc=0  both SUCCESS lines
#
# C2 against its own control C3 is the whole argument: a render that fails to
# land is INVISIBLE under the glob and rc=1 under the literal, on one character.
#
# WHERE THE LOUDNESS LIVES IS PROMTOOL, NOT THE PROCESS, and saying so is what
# keeps this clause from being stronger than what it measured. Driven live
# (`PROM_RULES_DELIVERY_EVIDENCE`, rows D5/D5b/D6): a LITERAL path that does not
# exist is `running restarts=0`, `Completed loading of configuration file`, and
# `/api/v1/rules` -> `{"groups":[]}` — byte-for-byte the glob-over-an-empty-dir
# leg. So the literal buys nothing at runtime and everything at `promtool check
# config`, which is exactly why `7c` (validate-before-restart) is the row that
# converts it into a guard an operator ever sees.
PROM_RULES_GLOB_CHARS = "*?["
PROM_RULES_LITERAL_EVIDENCE = "logs/builder-7a-literal-vs-glob.log"
# `notify: Restart prometheus`, MEASURED and not taken by analogy with the four
# rows already in `RELOAD_CONTRACT` (`PROM_RULES_DELIVERY_EVIDENCE`, one live
# container per row, `evaluation_interval: 15s` so +40s is two-plus cycles):
#
#     D1  POST /-/reload                        403 "Lifecycle API is not enabled."
#     D2  EDIT IN PLACE, same inode, +40s       the container SEES the new bytes and
#                                               the process serves the OLD rule set
#     D3  ATOMIC REPLACE, new inode, +40s       the container cannot even SEE the new
#                                               bytes — a single-FILE bind holds the
#                                               old inode, and `os.replace` is what
#                                               `ansible.builtin.template` does
#     D4  CONTROL, docker restart               same container id, new inode visible,
#                                               new rule set served
#
# So the handler is required TWICE OVER here, which is one more reason than
# `prometheus.yml`'s row has: the process does not re-read rule files, AND the
# mount does not follow ansible's write. D3 is the interesting one — it means a
# rules edit is not merely undelivered but INVISIBLE inside the container until
# something re-establishes the mount.
PROM_RULES_DELIVERY_EVIDENCE = "logs/builder-7a-handler-question.log"
# 0644, the same digits `prometheus.yml.j2` carries and NOT copied from it: the
# mode was driven on this file, root:root, against the pinned image
# (`PROM_RULES_MODE_EVIDENCE`, `docker run --entrypoint id` -> uid 65534(nobody)):
#
#     0640  `state=restarting restarts=7`, `Error loading rule file patterns from
#           config … open /etc/prometheus/rules/plex-blip-rules.yml: permission
#           denied` — verbatim the crash loop that left this stack's TSDB empty
#           from 2026-05-28 to 2026-07-29
#     0644  `running restarts=0`, `/api/v1/rules` -> groups=['plex-blip']
#
# And note the asymmetry against the two legs above: an UNREADABLE rules file is
# LOUD while a MISSING one is silent. `world_read_is_licensed` is what pays for
# the world bit; these rules carry no credential and the render task says so.
PROM_RULES_MODE = "0644"
PROM_RULES_MODE_EVIDENCE = "logs/builder-7a-rules-mode.log"
# Design §5.3 (`design/detailed-design.md:583-605`), in the document's own order,
# with each alert's `expr:` and its `for:` — `None` where the design writes no
# `for:`, which `PlexTransactionHoldStorm` does because `increase(...[5m])`
# already carries its own window. NO `labels:` and NO `annotations:` are pinned
# here and none are shipped: the source carries neither, plan.md's
# severity+summary bullet is an obligation on `7d`, and a clause asserting them
# at `7a` would be a sentence stronger than the file it guards.
#
# THE `expr` COLUMN IS THE ALERT, and it arrived one round late. Round 1 pinned
# `(alert, for)` and read the exprs only for RESOLVING COORDINATES — metric
# families, job labels, the `event_type` VALUE — which leaves the threshold, the
# comparison operator, the range window and the label KEY held by nothing, i.e.
# nothing held whether an alert can ever fire. Eight mutants were `PASS: 54/54`
# (`logs/builder-7a-r2-mutants-RED.log`), including `PlexWatchdogProbeBroken`
# INVERTED to `== 1` — the meta-guard firing exactly when the watchdog is healthy
# and never when it has died — and `PlexProbeSlow` raised `0.5` -> `500`, which
# retires R10's headline detection while every reader in the stack agrees the
# alert is present.
#
# NOTHING ELSE IN THE STACK CLOSES IT, and that is measured rather than argued:
# `promtool check rules` on the pinned image is rc=0 `SUCCESS: 7 rules found` on
# ALL EIGHT, byte-identical to the delivered leg, and three live containers
# (delivered / inverted / inert) are identical on state, restart count, rule
# count, startup log and ERROR count — the only byte that differs anywhere is the
# `query` field of `/api/v1/rules`, which nothing in this repo reads. That is the
# same "loads clean, matches nothing, fires never" shape the readers below exist
# for, stated generally in this clause's own docstring at round 1 and then not
# applied to its own table.
#
# The exprs are compared WHITESPACE-NORMALISED (`" ".join(expr.split())`), so
# rewrapping a long expr is not a false RED while every character that carries
# meaning is held. The far end is the literal here and not `detailed-design.md`:
# `.agents/` is git-ignored and that document is untracked, so a guard reading it
# would be ABSENT in a fresh clone.
#
# THE DESIGN'S SEVEN ARE A SEPARATE CONSTANT FROM THE SHIPPED SEQUENCE as of
# `7b`, which appends three `absent()` doors. Keeping the halves apart is what
# lets the §5.3-verbatim claim above stay literally true while the FILE grows:
# `PLEX_BLIP_ALERTS` is what the render carries, `PLEX_BLIP_DESIGN_ALERTS` is
# what the design wrote, and the difference is exactly `PLEX_BLIP_ABSENCE_ALERTS`.
PLEX_BLIP_DESIGN_ALERTS = (
    ("PlexProbeSlow",
     'probe_duration_seconds{job="blackbox-plex-identity"} > 0.5', "1m"),
    ("PlexSessionsProbeStalled",
     'probe_duration_seconds{job="blackbox-plex-sessions"} > 5', "1m"),
    ("PlexUnreachable",
     'probe_success{job=~"blackbox-plex.*"} == 0', "30s"),
    ("PlexExporterScrapeFailing",
     'up{job="plex-exporter"} == 0', "2m"),
    ("PlexSqliteWalOversized",
     "plex_sqlite_wal_bytes > 8388608", "15m"),
    ("PlexTransactionHoldStorm",
     'increase(plex_watchdog_events_total{event_type="TX_HELD"}[5m]) > 3', None),
    ("PlexWatchdogProbeBroken",
     "plex_watchdog_probe_status == 0", "10m"),
)
# THE SEVEN EXPRS' COORDINATES ARE JOINS NOTHING AT RUNTIME CHECKS, which is the
# `params.module` argument one file over said in full: an alert whose `job=` names
# a job this stack does not scrape matches no series and fires never, and an
# alert with no series to match looks exactly like an alert with nothing to say.
# `prometheus.yml.j2`'s own 5c comment deferred the exact-match half in writing —
# "Step 7 does not exist yet, so the guard pins the shared blackbox-plex prefix
# and says so" — and this is that half. That comment has been rewritten to record
# the landing rather than the deferral, so the quoted sentence is history and not
# a citation. Every coordinate below is read out of the far end rather than
# spelled twice, so the pairs move together or redden.
PLEX_BLIP_EXPR_READERS = {
    # `job="X"`, NOT `job=~`: the negative lookahead is load-bearing, since
    # `job=~"blackbox-plex.*"` would otherwise be read as an exact job name that
    # no scrape config can ever carry.
    "exact_job": r'\bjob\s*=(?!~)\s*"([^"]*)"',
    "regex_job": r'\bjob\s*=~\s*"([^"]*)"',
    "event_type": r'\bevent_type\s*=(?!~)\s*"([^"]*)"',
    # The watchdog's families. Bounded to `plex_` on purpose: `up`,
    # `probe_success` and `probe_duration_seconds` are Prometheus' and blackbox's
    # OWN series, produced by the scrape rather than by anything this repo
    # writes, so there is no far end in-tree to read them against and pretending
    # otherwise would be a guard that pins its own literal.
    "watchdog_metric": r'\b(plex_[a-z0-9_]+)',
}
# `_event("TX_HELD", …)` in the watchdog, read by `ast` and not by grep: the
# source's own comment block names TX_STALL/TX_HELD/SLOW_QUERY in prose three
# lines above the code, so a text scan would be answered by the documentation.
PLEX_WATCHDOG_EVENT_FN = "_event"

# --- plex-blip-manual-triage Step 7b: the absence doors -----------------------
# ALL SEVEN OF THE DESIGN'S RULES COMPARE A SERIES TO A CONSTANT, and a
# comparison over an ABSENT series matches nothing — so each of them is silent
# exactly when the thing it guards has stopped producing. `7b` adds three
# `absent()` DOORS, one per PRODUCER rather than one per rule, because the
# absences are shared: the three blackbox jobs vanish together with the blackbox
# exporter, `up{job="plex-exporter"}` vanishes only with its scrape config, and
# the watchdog's four families vanish together with its `.prom`.
PLEX_BLIP_ABSENCE_EVIDENCE = "logs/builder-7b-absence-doors.log"
# THE GUARD'S OWN MEASUREMENT, and it is separate from the one above on purpose:
# `PLEX_BLIP_ABSENCE_EVIDENCE` is `promtool test rules` proving the DOORS fire,
# `PLEX_BLIP_ABSENCE_GUARD_EVIDENCE` is DEC-328's three charges re-run as mutants
# proving the CLAUSE reddens. Round 1 shipped the first without the second and
# every charge was a green mutant: a fourth door on a residue metric (twice, at
# two `for:` values) and a fourth `blackbox-plex-*` job in the scrape config all
# left every arm `True`. The harness is `logs/builder-7b-r2-mutants.py`; it
# restores the tree with a byte compare after each leg.
PLEX_BLIP_ABSENCE_GUARD_EVIDENCE = "logs/builder-7b-r2-green.log"
# WHICH DOOR OPENS FOR WHICH INPUT: the metric a comparison rule reads -> (the
# alert that opens its door, the metric THAT alert calls `absent()` on). The two
# metrics differ on four of six rows and every one of those is a measured join,
# not a convenience:
#
#   probe_duration_seconds -> probe_success   ONE scrape produces both. blackbox
#       returns `probe_success 0` on a failed probe, so `probe_success` is absent
#       exactly when `probe_duration_seconds` is, and a second door over the
#       duration series would fire on the same event twice.
#   plex_sqlite_wal_bytes        -> plex_sqlite_db_bytes
#   plex_watchdog_events_total   -> plex_sqlite_db_bytes
#   plex_watchdog_probe_status   -> plex_sqlite_db_bytes
#       and these three are the interesting ones, because ONLY ONE of the
#       watchdog's families is published unconditionally and it is not any of the
#       three above. `render_textfile_metrics` OMITS A FAMILY WHOSE MEASUREMENT IS
#       NULL rather than publishing a zero (its own docstring says why: "a zero is
#       indistinguishable from a freshly checkpointed WAL once it is a point on a
#       graph"), and the probe/event families are populated only from the TRIGGER
#       branch while the sqlite gauges go out on the idle poll every
#       `textfile_refresh_sec` (15.0 s, `plex_blip_watchdog.py:634`).
#
#       Driven on the real CLI at this row's hands, both directions
#       (`PLEX_BLIP_ABSENCE_EVIDENCE`, legs W1/W2):
#
#         never triggered, WAL checkpointed   130 B, `plex_sqlite_db_bytes` ALONE
#         never triggered, WAL live           3 gauges: wal + db + shm
#
#       So a door over `absent(plex_watchdog_probe_status)` would be FIRING on
#       every healthy stack that has not blipped (measured by
#       `task-1786159639-39db`, which this row CLOSES), and a door over
#       `absent(plex_sqlite_wal_bytes)` would be firing on every checkpointed
#       database — the second one was the draft of THIS constant and the CLI run
#       above is what refused it. `plex_sqlite_db_bytes` is the family that is
#       there whenever the document is, so its absence is the document's absence:
#       watchdog dead, `--textfile-dir` unset, or the `.prom` unreadable to
#       node-exporter's uid (measured by `task-1786167833-1152`, closed here; the
#       mode it names is still pinned by nothing and that is OPEN at
#       `task-1786230668-0902`). What this door does NOT detect is the restart
#       case, OPEN at `task-1786230651-63ba` — re-filed, not papered over, and
#       both successors are cited by id here so a fresh clone can find them
#       without `.agents/`, which is git-ignored.
PLEX_BLIP_ABSENCE_DOORS = {
    "probe_success": ("PlexBlackboxProbesAbsent", "probe_success"),
    "probe_duration_seconds": ("PlexBlackboxProbesAbsent", "probe_success"),
    "up": ("PlexExporterTargetAbsent", "up"),
    "plex_sqlite_wal_bytes": ("PlexWatchdogTextfileAbsent", "plex_sqlite_db_bytes"),
    "plex_watchdog_events_total": (
        "PlexWatchdogTextfileAbsent", "plex_sqlite_db_bytes"),
    "plex_watchdog_probe_status": (
        "PlexWatchdogTextfileAbsent", "plex_sqlite_db_bytes"),
}
# WHAT `7b` DOES NOT CLOSE, and it is READ BY `residue_unwatched` rather than
# printed: no `absent()` in the rules file may name a key of this table. A metric
# here is one whose OWN absence is not alertable — absent in a state that is
# HEALTHY, so a door over it pages on the good state — with the measurement that
# established that and the OPEN task that owns the remedy. Round 1 narrated this
# sentence and no predicate held it, so a fourth door on `plex_sqlite_wal_bytes`
# was `PASS` while the same `print` still listed it as unwatched (DEC-328 C1).
PLEX_BLIP_ABSENCE_RESIDUE = {
    "plex_watchdog_probe_status":
        "absent by design until the first trigger — a never-triggered watchdog "
        "serves 130 B of plex_sqlite_db_bytes alone (measured, leg W1). An "
        "alertable liveness series is watchdog surface, not rule surface "
        "(task-1786230651-63ba)",
    "plex_sqlite_wal_bytes":
        "absent by design whenever the WAL is checkpointed — the same 130 B "
        "document (leg W1) against the three-gauge one with a live writer (leg "
        "W2). Its absence is a HEALTHY database, so a door over it would page on "
        "the good state",
}
# THE DOOR NAMES EVERY JOB SEPARATELY AND A REGEX IS REFUSED INSIDE `absent()`,
# and this is the row's own defect class one step in: `absent()` returns a sample
# only when its selector matches NOTHING, so `absent(probe_success{job=~
# "blackbox-plex.*"})` is EMPTY while one of the three jobs is still reporting —
# silent exactly when two of three probes have vanished. Measured with its
# control at `PLEX_BLIP_ABSENCE_EVIDENCE`.
#
# WHICH JOBS THE DOOR MUST NAME IS NOT SPELLED HERE. It is resolved at check time
# out of `prometheus.yml.j2` through the selectors of the rules this door covers,
# because the first draft compared the door to `BLACKBOX_JOBS` — a TEST CONSTANT
# — and a fourth `blackbox-plex-*` job joining the scrape config left the arm
# `True` while its docstring claimed set equality "in both directions"
# (DEC-328 C2, the `task-1786203094-588c` shape one clause over).
PLEX_BLIP_ABSENCE_PER_JOB_DOOR = "PlexBlackboxProbesAbsent"
# Which scrape job feeds each door, so the `for:` below is read against the
# cadence in `prometheus.yml.j2` rather than chosen by feel. `doors_agree` holds
# these keys EQUAL to the doors the rules file carries: without that the cadence
# loop was a quantifier over this dict alone, and a door absent from it had no
# `for:` checked by anything (DEC-328 C1b).
PLEX_BLIP_ABSENCE_SOURCE_JOBS = {
    "PlexBlackboxProbesAbsent": tuple(sorted(BLACKBOX_JOBS)),
    "PlexExporterTargetAbsent": (PLEX_EXPORTER_SERVICE,),
    "PlexWatchdogTextfileAbsent": (PLEX_NODE_JOB,),
}
# A DOOR'S `for:` OUTLASTS FOUR MISSED SCRAPES of the slowest job that feeds it,
# read out of the template's own `scrape_interval` (`_effective_scrape_pair`).
# Four rather than one because a door is an ALARM ABOUT THE ALARM: a single
# missed scrape is a stale marker and a restarted exporter, and paging on it
# would retire the door within a week. The relation moves if a cadence changes —
# raising `blackbox-plex-sessions` to `2m` reddens `for: 5m` rather than quietly
# converting the door into a same-scrape tripwire.
PLEX_BLIP_ABSENCE_MIN_MISSES = 4
# PromQL words that are not metric names. Everything else an expr can carry that
# looks like an identifier is a FUNCTION and is followed by `(`, which
# `_promql_selectors` excludes by lookahead rather than by an enumeration that
# would fail open one function past its edge.
PROMQL_KEYWORDS = frozenset({
    "and", "or", "unless", "by", "without", "on", "ignoring", "group_left",
    "group_right", "offset", "bool", "start", "end",
})
# The three doors, in the order the render carries them, in the same
# `(alert, expr, for)` shape as the design's seven.
PLEX_BLIP_ABSENCE_ALERTS = (
    ("PlexBlackboxProbesAbsent",
     'absent(probe_success{job="blackbox-plex-identity"}) or '
     'absent(probe_success{job="blackbox-plex-sessions"}) or '
     'absent(probe_success{job="blackbox-plex-proxied"})', "5m"),
    ("PlexExporterTargetAbsent",
     'absent(up{job="plex-exporter"})', "5m"),
    ("PlexWatchdogTextfileAbsent",
     "absent(plex_sqlite_db_bytes)", "10m"),
)
PLEX_BLIP_ALERTS = PLEX_BLIP_DESIGN_ALERTS + PLEX_BLIP_ABSENCE_ALERTS

# --- plex-blip-manual-triage Step 7d: severity + summary on every rule --------
# plan.md's second Tests bullet — "every alert has `severity` and a `summary`
# annotation" — is an OBLIGATION on this step and NOT a property of design §5.3,
# which ships its seven rules with NO `labels:` and NO `annotations:` block at
# all (premise 4, measured at the wave cut: `promtool check rules` on §5.3
# verbatim is rc=0 `SUCCESS: 7 rules found`, so the source is sound but silent on
# both keys). `7d` adds them to all TEN rules the render carries — the design's
# seven plus `7b`'s three `absent()` doors — and this guard holds every rule to
# BOTH, PER-RULE over the PARSED render rather than by counting occurrences, so a
# rule added later without either reddens instead of shrinking a total nobody
# reads. It is a separate clause from `test_plex_blip_alert_rules_are_design_5_3`
# on purpose: that one pins the `(alert, expr, for)` sequence and is deliberately
# BLIND to labels/annotations (it reads three keys per rule), which is what let
# the design-5.3 claim above stay literally true across `7b`'s growth.
ALERT_SEVERITY_LABEL = "severity"
ALERT_SUMMARY_ANNOTATION = "summary"
# The two severities Prometheus and Grafana render natively and this stack ships;
# a typo'd level (`warn`, `crit`) is a value no dashboard filters on, so it is
# caught here rather than sorted into a silent bucket. `severity` PRESENCE is the
# obligation; holding it to this set is the anti-typo companion, not a new one.
ALERT_SEVERITY_LEVELS = frozenset({"warning", "critical"})
# ACCEPTANCE 2, and it is a WORDING PROPERTY rather than an exact sentence.
# `PlexExporterScrapeFailing` fires when the metrics EXPORTER stops answering,
# which the current single-panel dashboard invites an operator to read as the
# media server being down (design R5, plan.md:540) — a different fault with a
# different first move. Its summary must therefore NAME the real failure (the
# exporter / scrape / metrics path) and must NOT be misreadable as "Plex is
# down". Pinning the property and not the sentence lets the wording be rewritten
# without a false RED, while a summary that drifts back into the conflation the
# alert's own name exists to prevent still reddens.
EXPORTER_SCRAPE_FAILING_ALERT = "PlexExporterScrapeFailing"
EXPORTER_DOWN_MISREADINGS = (
    "plex is down", "plex down", "plex is unreachable", "plex unreachable",
    "plex is offline", "plex offline", "server is down",
    "media server is down",
)
EXPORTER_REAL_FAULT_WORDS = ("exporter", "scrape", "metric")

# THE WORLD-READ FENCE IS A COLUMN NOW, because this role gained a SECOND
# world-readable render. `prom/prometheus:v3.12.0` runs as uid 65534, so every
# file it must open is 0644 root:root or the crash loop both files were measured
# into, and 0644 publishes each of them to every user on the docker host. The
# licence is one sentence (`PROM_NO_CREDENTIAL_PROSE`) and one leak scan
# (`_credential_spellings`), so both renders are walked by ONE clause rather than
# the rules render arriving beside a check that names only its neighbour — the
# "next render task walks straight past the table" defect `RELOAD_CONTRACT`'s own
# header predicted and Step 4a then committed.
WORLD_READ_LICENCE = (PROM_SCRAPE, PROM_RULES)

# --- the field census, and it is LOAD-BEARING rather than prose ---------------
# `prom/blackbox-exporter:v0.28.0` unmarshals its config STRICTLY: a field it
# does not know is `Error loading config` and exit 1, which `restart:
# unless-stopped` turns into the crash loop this role has already served once.
# A Python YAML parser accepts every one of those documents, so the reading
# clause's `parses=True` was GREEN over a config that cannot start — measured on
# the pinned binary at logs/critic-5a-r2-parser-vs-process.log and, unfakeably,
# at logs/critic-5a-r2-gate-under-typo.log, where a ONE-CHARACTER typo
# (`valid_status_code`) leaves the WHOLE GATE reading `43/43`.
#
# A KNOWN FIELD WITH A WRONG-TYPED VALUE IS THE SAME rc=1, and scoring only the
# NAMES left that half open for a whole round (DEC-291 charge 1). `timeout: 5s`
# -> `timeout: 5` is ONE DELETED CHARACTER; the binary answers `cannot unmarshal
# !!int 5 into time.Duration` and exits, and the WHOLE GATE printed `43/43` over
# it (logs/critic-5a-r3-gate-under-timeout.log). So each name below carries the
# VALUE SHAPE this document gives it, and the census is a name -> predicate map
# rather than a set.
#
# EVERY PREDICATE IS A MEASUREMENT OF THE PINNED BINARY, NOT A READING OF GO'S
# TYPE SYSTEM, and that is not pedantry — three of the obvious ones are traps
# (logs/builder-5a-r4-binary-probe{,2}.log, 49 documents at `--config.check`):
#
#     prober: 3 / method: 7 / preferred_ip_protocol: 4      LOADS
#     method: {a: b} / prober: {a: b} / …: [a]              REFUSES
#         -> go-yaml v3 fills a Go string field from the RAW SCALAR whatever its
#            tag is, and refuses only a container. So `_bb_scalar`, and an
#            `isinstance(v, str)` predicate would false-RED on all three.
#     ip_protocol_fallback: on / True                       LOADS
#     ip_protocol_fallback: 'false' / 0 / 1 / [] / maybe    REFUSES
#         -> PyYAML's `bool` is exactly this line, on all seven rows.
#     timeout: 1m30s / .5s / -5s / 100us / '5s'             LOADS
#     timeout: 5 / 0 / 5sec / [5s]                          REFUSES
#         -> Go durations CONCATENATE, so the quantifier goes round the whole
#            group; `^\d+(\.\d+)?(ms|s|m|h)$` false-REDs on `1m30s`.
#     valid_status_codes: [] / [200, 204]                   LOADS
#     valid_status_codes: 200 / {} / [true] / ['200']       REFUSES
#         -> a possibly-EMPTY list of non-bool ints. `[]` loading is why the
#            predicate does not require a member.
#
# STEP 5b ADDS `headers`, AND IT IS A TRAP IN THE OPPOSITE DIRECTION FROM THE
# THREE ABOVE — measured, 23 documents, logs/builder-5b-headers-probe.log:
#
#     headers: {X-Plex-Token: abc} / {} / two keys / ~      LOADS
#     headers: {X-Plex-Token: 5 / true / ~ / 1.5}          LOADS
#     headers: {200: abc} / {on: abc}                       LOADS
#     headers: abc / 5 / [X-Plex-Token]                     REFUSES
#     headers: {X-Plex-Token: [a]} / {X-Plex-Token: {a: b}} REFUSES
#         -> the Go field is `map[string]string`, NOT a string, so `_bb_scalar`
#            — the honest predicate for `prober`, where a raw scalar fills a
#            string — is a FALSE-ACCEPT here on `headers: abc` (rc=1, crash
#            loop). And the raw-scalar rule that makes `prober: 3` load applies
#            ONE LEVEL DOWN instead: a non-container VALUE loads, a container
#            value is `cannot unmarshal !!seq into string`. So the predicate is
#            a mapping whose values are each `_bb_scalar` — the same measured
#            notion of "a Go string field takes any raw scalar", reused rather
#            than re-derived — plus `None`, because a bare `headers:` LOADS and
#            a predicate that redded it would false-RED a document the binary
#            accepts (the `[]`-loads lesson one row up).
#
# THESE MAPS ARE THIS DOCUMENT'S VOCABULARY, NOT A COPY OF BLACKBOX'S SCHEMA,
# and that distinction is the whole design. Each is the fields the row PINS plus
# the ones its reading clause declares "NOT PINNED, deliberately" — the same
# allow-list idiom as `BLACKBOX_SERVICE_KEYS` two constants up, which does not
# enumerate every legal compose key either. So the census in that docstring is
# now the thing the test reads, and a partial list stops being a claim about the
# fields it omits.
#
# THE DIRECTION IT FAILS IS DECLARED. A field blackbox accepts but this census
# has not learned REDS: `min_version` under `tls_config` LOADS on the binary and
# reds here (logs/builder-5a-r3-{red,green}.log, D6). `headers:` was the other
# named example and that cost HAS NOW BEEN PAID: `5b` added it to the map below
# in the same commit as the module that needs it, the identical cost
# `BLACKBOX_MODULES` imposed on the same row for its module NAME. Written in the
# past tense on purpose — the sibling docstring records the same event and the
# two must not drift into one landed and one pending (DEC-302 charge 1's class).
# It fails closed, and the next field pays what this one did.
_GO_DURATION = re.compile(r"^[+-]?((\d+(\.\d*)?|\.\d+)(ns|us|µs|ms|s|m|h))+$")


def _bb_mapping(value) -> bool:
    """A block, not a scalar: `http: yes` is `cannot unmarshal !!str into
    config.plain`, rc=1."""
    return isinstance(value, dict)


def _bb_bool(value) -> bool:
    """A YAML bool. PyYAML's boundary IS the binary's, measured on all seven
    spellings: `on`/`True`/`yes`/`false` load, `'false'`/`0`/`[]` refuse."""
    return isinstance(value, bool)


def _bb_scalar(value) -> bool:
    """Anything that is not a container. go-yaml v3 fills a string field from
    the raw scalar text, so `prober: 3` LOADS and only `!!map`/`!!seq` refuse."""
    return not isinstance(value, (dict, list))


def _bb_duration(value) -> bool:
    """A Go `time.Duration` STRING. Concatenated components and a leading sign
    are legal (`1m30s`, `-5s`, `.5s`); a bare int is not, and that is the
    one-character edit the whole gate used to read `43/43` over."""
    return isinstance(value, str) and bool(_GO_DURATION.match(value))


def _bb_int_list(value) -> bool:
    """A `[]int`, possibly EMPTY — `valid_status_codes: []` loads. `bool` is
    excluded because it is an `int` in Python and `!!bool` into `int` is rc=1."""
    return isinstance(value, list) and all(
        isinstance(item, int) and not isinstance(item, bool) for item in value)


def _bb_string_map(value) -> bool:
    """A Go `map[string]string`, possibly EMPTY or NULL.

    Step-5b, and every clause of it is a row of logs/builder-5b-headers-probe.log
    rather than a reading of the struct tag:

    * a bare `headers:` (PyYAML `None`) LOADS — so `None` is accepted here, for
      the same reason `valid_status_codes: []` does not require a member.
    * a SCALAR refuses (`cannot unmarshal !!str \\`abc\\` into map[string]string`),
      which is why this is not `_bb_scalar`: that predicate is correct for
      `prober`, where go-yaml fills a Go STRING from the raw scalar, and it would
      be a false-ACCEPT here over an exit-1 crash loop.
    * a non-container VALUE loads whatever its tag — `5`, `true`, `~`, `1.5` are
      all rc=0 — because the raw-scalar rule applies to the map's string VALUES.
      A list or mapping value is `cannot unmarshal !!seq into string`, rc=1.
    """
    return value is None or (
        isinstance(value, dict) and all(_bb_scalar(v) for v in value.values())
    )


BLACKBOX_TOP_FIELDS = {"modules": _bb_mapping}
BLACKBOX_MODULE_FIELDS = {
    "prober": _bb_scalar, "timeout": _bb_duration, "http": _bb_mapping,
}
BLACKBOX_HTTP_FIELDS = {
    # pinned by the reading clause
    "fail_if_not_ssl": _bb_bool, "tls_config": _bb_mapping,
    # declared unpinned: meaning vs tuning, see that clause's census
    "method": _bb_scalar, "valid_status_codes": _bb_int_list,
    "preferred_ip_protocol": _bb_scalar, "ip_protocol_fallback": _bb_bool,
    "follow_redirects": _bb_bool,
    # Step 5b: the token. Enumerated here in the SAME commit that turns the knob,
    # which is the cost `5a` declared this allow-list would impose on this row
    # (its L1) — and it is the fail-closed direction.
    "headers": _bb_string_map,
}
BLACKBOX_TLS_FIELDS = {"insecure_skip_verify": _bb_bool}


def _indented_key_lines(body: str, key: str) -> list:
    """Every line in `body` that opens a block under a key named `key`.

    The prefix tolerates YAML sequence dashes (`- targets:`) and counts them as
    part of the indent, so nesting under a list item slices the same way as
    nesting under a plain mapping key.
    """
    return list(re.finditer(
        rf'(?m)^([^\S\n]*(?:-[^\S\n]+)*){re.escape(key)}:[^\S\n]*$', body
    ))


def _block_under(body: str, match) -> str:
    """The lines after `match` indented deeper than the key it opened."""
    indent = len(match.group(1))
    lines = []
    for line in body[match.end():].lstrip("\n").splitlines():
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        lines.append(line)
    return "\n".join(lines)


def _indented_blocks(body: str, key: str) -> list:
    """EVERY block under a key named `key` in this region.

    Step-2a F1, round 9. The plural read, for the one call site whose claim is
    UNIVERSAL over the siblings: `targets:` under `static_configs:`. Prometheus
    takes `static_configs` as a LIST and scrapes every entry in it, so a second
    `- targets:` is ordinary config rather than an ambiguity to fail closed on —
    and the singular read left `target_is_pve_host=True` while the rendered
    artifact passed `promtool check config` at rc=0 with
    `targets=['192.168.1.50', '203.0.113.9']`, i.e. the exporter asked to
    interrogate a caller-chosen host with the homelab's PVE credential
    (logs/calibration-step02a-f1-round9.log, leg A, R5). "Which of the siblings"
    has two right answers and this is the other one: read them all and let the
    clause quantify over the lot.
    """
    return [_block_under(body, m) for m in _indented_key_lines(body, key)]


def _indented_block(body: str, key: str) -> str:
    """The lines under `key:` that are indented deeper than it, or "" if absent.

    Sliced by indentation so a key named `cluster` elsewhere in the job (or in a
    sibling job) cannot answer for the URL parameter that actually produces the
    per-guest series. Used for `params:`, `relabel_configs:`, `static_configs:`
    and a compose service's `volumes:`/`command:`.

    ANCHOR, per the rule above: this slicer is REGION-RELATIVE by construction —
    its parent is the region its caller passes, and every caller here passes one
    that was itself anchored by a path (`_scrape_job_block`,
    `_compose_service_block`). It has no document of its own to walk, which is
    why it names no column; that is a property worth stating rather than leaving
    to be inferred, because round 8's header claimed a universal rule that four
    slicers below it did not follow.

    Step-2a F1, round 9: a key that resolves MORE THAN ONCE in the region returns
    "" and reddens its clause, the same fail-closed direction an unresolved
    anchor takes. Measured free on the delivered tree — `params`,
    `relabel_configs`, `static_configs`, `targets` and all ten compose services'
    `volumes:`/`command:` resolve exactly once (leg B). Where repetition is
    LEGITIMATE the caller takes `_indented_blocks` instead; `targets:` is the
    only such site today and it is named there.
    """
    ms = _indented_key_lines(body, key)
    return _block_under(body, ms[0]) if len(ms) == 1 else ""


def _strip_comments(block: str) -> str:
    """A block with its `#` comments removed — whole-line AND trailing.

    The comments in these templates DESCRIBE the invariants they sit above, so a
    check matching free text over the raw block is satisfiable by its own
    documentation. Not hypothetical: the Step-2a mutation battery deleting the
    `command: [--no-collector.config]` entry left the guard GREEN, because the
    comment one line up still contained the flag name
    (logs/mutation-step02a-pve-exporter.log, first run).

    Step-2a F1, round 13 — the SECOND HALF of that sentence, and the round-12
    review's own carrier written one way over. Dropping a line whose FIRST
    non-space character is `#` closes ONE SPELLING of the carrier, not the
    carrier: an INLINE (trailing) comment survived this function and therefore
    survived every reader built on it —

        _key_bounded_block -> _compose_service_block -> _indented_block
                           -> _list_entries -> _service_labels

    — and the pins' own `[^\\n]*` tails cross the `#`, so the comment needs no
    line of its own. This is the ONE function that whole chain funnels through,
    which is why the fix is three lines here and not a sweep: an AST census of
    the guard's own unanchored reads returns dozens of sites, and they are all
    downstream of this. Eight rows were PASS 36/36 on the round-12 guard with a
    trailing `# was:` carrying the deleted string
    (logs/red-step02a-rework-f1-round13.log, R1-R7 + R9/R9b): whoami's,
    grafana's, prometheus's and the whoami-web twin's `internal-allowlist`
    dropped, a resolver hard-coded to `le-staging`, `homepage-web` moved to
    `websecure` AND repointed at grafana's backend (the Error-1000 class), and
    env.j2's CF / PVE token assignments DELETED while the rendered `.env` carries
    no such key. The no-carrier controls are RED, so green-vs-red was purely
    whether a comment held the string; `docker compose config` returns rc=0 on
    every row, and on the pinned traefik:v3.7.5 with labels taken OUT OF THE
    RENDERED TEMPLATE a client outside all four allowlisted ranges gets 200 where
    the delivered tree answers 403
    (logs/review-step02a-rework-f1-round13b.log).

    It also clears FALSE REDS in the other direction: a trailing comment
    recording the deliberate ABSENCE of `<svc>-web.tls` reddened a fully correct
    tree through the absence pins (row R8).

    `\\s+#` requires whitespace before the `#`, which is YAML's own rule for a
    trailing comment (`a=b#c` is the value `b#c`), and the price is measured, not
    argued: there are ZERO inline-comment sites in the twelve files this guard
    reads today (leg D census, printed row by row). Where a future value really
    does contain ` #` the cut SHORTENS the subject, so the pin sees less text and
    fails CLOSED.
    """
    return "\n".join(
        re.sub(r'\s+#.*$', '', ln)
        for ln in block.splitlines()
        if not ln.lstrip().startswith("#")
    )


def _list_entries(block: str) -> list:
    """A YAML sequence's ENTRIES, one string each, sliced at the `-` column.

    Step-2a F1, round 10 — the answer to (4) in the anchor rule above for the case
    `_param_values` cannot serve: an entry that is a MAPPING spans several lines
    (`- source_labels: […]` / `  target_label: …`), so the thing a per-entry claim
    has to be asked of is the entry's whole text, not a scalar value.

    The column is derived from the block's own shallowest non-blank line, the same
    derive-it-from-the-block move `_service_key_lines` makes, so a re-indent of the
    file cannot silently return ONE entry containing everything. Comments come off
    first — a comment inside a relabel list names `__param_target`, `/pve` and
    `__address__` precisely because those are the pins (see `_strip_comments`).
    Lines before the first `-` are dropped: they belong to the key, not to an
    entry.

    Prototyped and priced by the round-10 review before it was prescribed
    (logs/review-step02a-rework-f1-round10d.log): on the delivered tree the
    `relabel_configs` list slices into 3 entries and the other four scrape jobs
    carry no `relabel_configs` at all, so the cost of asking per entry is zero.
    """
    lines = [ln for ln in _strip_comments(block).splitlines() if ln.strip()]
    if not lines:
        return []
    col = min(len(ln) - len(ln.lstrip()) for ln in lines)
    entries, cur = [], None
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if indent == col and re.match(r'-(?:\s|$)', line.lstrip()):
            if cur is not None:
                entries.append("\n".join(cur))
            cur = [line]
        elif cur is not None:
            cur.append(line)
    if cur is not None:
        entries.append("\n".join(cur))
    return entries


def _yaml_unquote(scalar: str) -> str:
    """One matched quote pair off a raw scalar — EXACTLY the layer YAML removes.

    Step-3a F1, round 3, and the other half of the criterion `_kv_entries` states.
    Round 2 deleted a `.lower()` that normalized a pinned value further than the
    runtime does; the review then found a `.strip('"\\'')` in the same expression
    doing the same thing one operator over. Both are gone from
    `test_plex_exporter_service_block`, where the value arrives ALREADY unquoted
    by `_kv_entries` and any further normalization is pure tolerance.

    The readers that call THIS are the other case: they hold a raw regex capture
    that nothing has unquoted yet, so removing quotes is the parser's own work
    being done once. `.strip("'\\"")` was the wrong instrument for it —
    `str.strip(chars)` removes every leading and trailing character in the set,
    which is not a rule YAML has. Measured on the pinned `prom/prometheus:v3.12.0`
    against a stub at the real service name
    (logs/calibration-step03a-doubled-quotes.log, `-s2.log`):

        - plex-exporter:9594        S1  target UP, up=1,
                                        scrapeUrl http://plex-exporter:9594/metrics
        - "plex-exporter:9594"      S2  IDENTICAL to S1 — one layer, and YAML owns it.
                                        This is the spelling the strip exists for
        - '"plex-exporter:9594"'    S3  promtool ACCEPTS it, and the target is DOWN:
                                        scrapeUrl http://"plex-exporter:9594"/metrics,
                                        `invalid port ":9594\\"" after host`, up=0

    S3 is the hole: `.strip` took BOTH layers, so the pin was satisfied by a
    scalar YAML resolves WITH its inner quotes. It is a weaker hole than F1's —
    the target reads DOWN and `up 0` exists, so it is the visible class rather
    than the silent-healthy one that has been rejected on four times — but the
    guard was green on a tree whose scrape cannot work, and one layer costs
    nothing (row S2, and the delivered gate is unchanged at 35/35).

    So: strip a quote only where the PARSER that hands the value to the runtime
    strips it, and strip exactly as MUCH as that parser does.

    WHICH IS ALSO WHY THE STRIP TAKES YAML'S WHITESPACE AND NOT PYTHON'S (Step-5c
    F1, round 4). A bare `.strip()` is the unicode class; YAML strips `s-white`
    (space, tab) and the line break, so U+00A0 and U+3000 are scalar CONTENT.
    That is the same over-strip as S3 one class over — `rule:<U+00A0>"Host(`h`)"`
    had its U+00A0 removed HERE, the quote pair then matched, and the guard read a
    clean rule while the value the parser hands traefik begins with a character
    its rule lexer calls illegal (`status='disabled'`, HTTP 404 for that host).
    Row N9/N10 of logs/red-step05c-rework-r4-gowhitespace.py: `PASS: 42/42` before
    the narrowing, and it survived a fix to `_router_rule`'s own separator class
    because this strip is downstream of it.
    """
    m = re.fullmatch(r'(?s)(["\'])(.*)\1', scalar.strip(" \t\r\n"))
    return m.group(2) if m else scalar.strip(" \t\r\n")


def _top_level_list(body: str, key: str) -> list | None:
    """A column-0 YAML sequence's entries, or None when this guard cannot read it.

    Step-2a F1, round 11. `group_vars/all/vars.yml`'s `public_services:` and
    `internal_services:` were read by FOUR hand-rolled slicers spelled
    `(?ms)^<key>:\\s*$(.*?)^\\S` — the shape round 11's sweep grep looks for, and the
    same three settled rules broken as `test_homepage_allowed_hosts`: a GLYPH
    boundary, no comment stripping, hand-rolled so no helper sweep reached it. A
    whole-line comment at column 0 is that file's OWN idiom (it opens five comment
    blocks there), and it ended the block. Two of the four pins are ABSENCE pins, so
    they failed OPEN: `prometheus` and `whoami` each PROMOTED into
    `public_services` behind such a comment left `public_services is exactly [plex]
    (entries=['plex'])` and `not_public=True` at guard PASS 36/36, while `ansible`
    loads `public_services=['plex', 'prometheus']` — the state the two clauses exist
    to forbid, in the list `vars.yml` says must not mislead a future operator
    (logs/red-step02a-rework-f1-round11.log, B1/B2; B3, the same promotion with no
    comment, is RED). And the fourth pin failed the other way: a column-0 comment
    inside a CORRECT `internal_services:` is a false RED (B4).

    So the region comes from `_key_bounded_block` like every other block here, and
    the entries are CLASSIFIED rather than pattern-scraped: anything that is not a
    blank, a document marker or a plain scalar sequence entry returns None and
    reddens the caller — the fail-closed direction an unresolved anchor already
    takes, and the reason absence pins may ask this instead of asking the raw text.
    """
    block = _key_bounded_block(body, key, 0)
    if not block.strip():
        return None
    entries = []
    for line in block.splitlines():
        cls = _line_class(line)
        if cls in ("blank", "doc"):
            continue
        # A mapping entry (`- name: x`), a nested block or any line the classifier
        # cannot read is not a service name: refuse to guess which one it meant.
        item = re.match(r'[^\S\n]*-[^\S\n]+(\S+)[^\S\n]*$', line) if cls == "seq" else None
        if not item:
            return None
        entries.append(_yaml_unquote(item.group(1)))
    return entries


def _param_values(params: str, key: str) -> list:
    """One key's SCALAR list values — flow (`key: ['1']`) or block (`- '1'`) form.

    Prometheus takes `params` as map-of-lists, and both spellings are legal YAML
    for the same request, so the check must accept either. Quotes are stripped:
    `'1'` and `1` are the same query string.

    Round 10 reuses it for the other scalar lists in these templates — a router's
    `entryPoints:`, an `ipAllowList`'s `sourceRange:`, a compose service's
    `depends_on:` — for the same reason it exists: both spellings are ordinary YAML
    and a clause that reads only one of them fails in the direction that reddens a
    correct tree. It is bounded by the key's own indent already, so it answers
    about ONE node; entries that are MAPPINGS need `_list_entries` instead.
    """
    m = re.search(rf'(?m)^([^\S\n]*){re.escape(key)}:[^\S\n]*(.*)$', params)
    if not m:
        return []
    indent, inline = len(m.group(1)), m.group(2).strip()
    if inline.startswith("["):
        # A flow sequence may WRAP across lines — ordinary YAML, and it used to read
        # as an EMPTY list here, which is a false RED on a correct tree (round 10's
        # price leg found it on `sourceRange`). Gather until the closing bracket.
        text = inline
        if "]" not in text:
            for line in params[m.end():].lstrip("\n").splitlines():
                text += " " + line.strip()
                if "]" in line:
                    break
        text = text[1:text.rindex("]")] if "]" in text else text[1:]
        return [_yaml_unquote(v) for v in text.split(",") if v.strip()]
    if inline:
        return [_yaml_unquote(inline)]
    values = []
    for line in params[m.end():].lstrip("\n").splitlines():
        item = re.match(r'\s*-\s*(\S+)\s*$', line)
        if not item or len(line) - len(line.lstrip()) <= indent:
            break
        values.append(_yaml_unquote(item.group(1)))
    return values


# plex-monitoring Step 2a, F1. A config file the role RENDERS is not a config the
# service has READ. `docker compose up -d --remove-orphans` (tasks/main.yml, the
# only thing that touches containers) leaves a container whose own spec is
# unchanged Running — the scrape config is a read-only BIND MOUNT, so a new job
# in prometheus.yml changes no compose spec at all. Prometheus has no
# `--web.enable-lifecycle`, so `POST /-/reload` answers 403. Reproduced end to
# end on real `prom/prometheus:v3.12.0`: start on the pre-2a config, land the 2a
# change, run the exact role command -> same container id, same StartedAt, job
# set UNCHANGED, `pve_up` -> []. Control: `docker compose restart prometheus` ->
# the job appears. So without a handler the operator's ONE irreproducible run in
# Step 2b cannot produce its falsifier, and the target does not read DOWN — it
# does not EXIST, which is the one failure mode a "check Status->Targets" ask
# cannot diagnose.
#
# The precedent was three tasks up in the same file (traefik.yml.j2 notifies
# `Restart traefik`); a render task added later simply never got one. Both rows
# are pinned here so the DELIVERY path — not just the file's content — is the
# guarded thing, and so the next render task added to this role has a check that
# already names the invariant.
# A RESTART IS ONLY THE LAST HOP (Step-2a F1, round 3). Delivery is
#
#     the render task's `dest` -> the HOST side of a bind mount -> the
#     CONTAINER side of that mount -> the path the process is told to read
#     -> the restart that makes it re-read
#
# and a clause pinning only the last hop is the same vacuity one hop out. Four
# mutations passed the round-2 version of this check, each measured at runtime on
# real `prom/prometheus:v3.12.0`: moving `dest` off the mount source makes docker
# create a DIRECTORY at the missing host path and the container cannot start at
# all (OCI "not a directory"); DROPPING the mount is the silent one and the worst
# — Prometheus boots CLEAN on the image's own default config and scrapes only
# itself, so every job disappears with the target reading UP and nothing erroring
# anywhere; mounting a different host file there is a config-load crash loop; and
# `--config.file` pointed elsewhere is the same class. A fifth passed the ENTIRE
# gate including `ansible-lint --profile production` and `--syntax-check`: a
# `notify:` indented one level too deep, inside the template module's args, which
# Ansible reads as an unsupported module parameter and which therefore fails at
# the operator's `just play` — the one run this loop cannot repeat.
#
# So the rows below carry the whole path, and the container-side hop is written
# as an AGREEMENT wherever the image lets it be one (the `port_agrees` shape):
# `config_flag` is checked against the mount's own target rather than against a
# literal, so moving the config's container path on both sides stays green while
# moving it on one side reddens. Where the image has no such flag the path IS the
# contract and gets pinned as `default_path`.
#
# The other half of "delivered" is that the service can READ the file once it
# restarts, and the two rows need DIFFERENT modes for that. `traefik:v3.7.5` runs
# as root, so 0640 root:root is readable. `prom/prometheus:v3.12.0` runs as
# `nobody` (uid 65534 — `docker run --entrypoint id`), so the same 0640 is
# `permission denied`, Prometheus exits non-zero on "Error loading config", and
# `restart: unless-stopped` turns it into a crash loop. Measured both ways
# against the real image; 0644 with the parent dir still 0750 boots clean,
# because the bind mount names the FILE and traversal happens on the host.
# The scrape config holds no secret — the PVE token reaches the exporter through
# `.env` (0600) as an env var and never appears here — so world-read costs
# nothing.
#
# CORRECTED, and it is not a nuance (F2, round 3): an earlier version of this
# comment said the mode "mattered only once the restart existed — before it an
# unreadable config was inert". That is FALSE. `restart: unless-stopped` has been
# re-reading the file every ~60s all along, and the live host proves it: on
# 192.168.1.111 `stack-prometheus-1` is `Restarting (2)` with
# `open /etc/prometheus/prometheus.yml: permission denied` once a minute, the file
# is 640 root:root, the TSDB volume has been empty since 28 May, and
# prometheus.yoonnation.com answers a Traefik 404 (a restarting container is
# dropped by the docker provider, so its router does not exist) while every other
# dashboard routes. The 0644 here is therefore not a precaution taken on account
# of the new restart — it is the REPAIR of a live outage that predates this step,
# and the operator tasks say so.
# THE OWNER COLUMN, Step 5b — and it closes the `RELOAD_CONTRACT` half of
# `task-1786187620-633b`, which recorded that not one of these rows pinned an
# owner while `BLACKBOX_MODE`'s whole argument was about `root:root 0640`.
#
# READABILITY IS NOT THE REASON, and saying so is the point of this comment. The
# obvious rationale — "root:root is what the process can read" — is FALSE of the
# file this row cares about: `prom/blackbox-exporter:v0.28.0` runs as uid 0, and
# uid 0 bypasses the permission bits, so five owner/mode pairs mounted `:ro` into
# it are all READ=ok (`logs/planner-step05b-owner-mode.log`, re-measured for the
# identity half at logs/builder-5b-headers-probe.log). A guard whose printed
# reason is "the container could not read it" would be asserting something that
# never happens — the guard-rationale-disagrees-with-the-file defect this
# objective has charged five times.
#
# What the column IS: the other half of a mode. `0640` means nothing without the
# owner it is 0640 FOR, and `owner: 65534` on a 0640 file hands group-read to a
# different identity than the one the comment above the render names. It is a
# FILESYSTEM FACT the role already writes on all five renders, pinned so that
# changing it is deliberate.
#
# ONE SPELLING, FIVE READERS. All five renders agree today, so the pair lives in
# a constant rather than being written out five times: five literals that agree
# is the defect class this suite has charged on `--output-dir`, on the watchdog
# program path and on the node-exporter binary. A row that must legitimately
# differ writes its own tuple, which is what makes this a COLUMN and not a
# global.
RENDER_OWNER = ("root", "root")

RELOAD_CONTRACT = {
    # rendered template -> every hop between the render task and the process
    "traefik.yml.j2": {
        "service": "traefik",
        "owner": RENDER_OWNER,
        "mode": "0640",
        # traefik:v3.7.5 reads its static config from this path with no flag
        # naming it, so HERE the container-side path IS the runtime contract.
        "config_flag": None,
        "default_path": "/etc/traefik/traefik.yml",
    },
    "prometheus.yml.j2": {
        "service": "prometheus",
        "owner": RENDER_OWNER,
        "mode": "0644",
        # Prometheus is TOLD where to look, so the container-side path is free —
        # what must hold is that the flag names the mount's own target.
        "config_flag": "--config.file",
        "default_path": None,
    },
    # Step-4a F1, round 3. The two GRAFANA PROVISIONING renders are the third and
    # fourth rows of this class, and they arrive here for the reason the comment
    # above `_render_task_block` predicted: this table exists "so the next render
    # task added to this role has a check that already names the invariant", and
    # the Step-4a build added three renders that walked straight past it.
    #
    # MEASURED, not assumed by analogy (`logs/red-step04a-r3-battery.log` leg D,
    # `logs/red-step04a-r3-provider-poll.log`, real grafana/grafana:13.1.0):
    #
    #   D1  datasource.yml edited under the LIVE mount, +40s   url UNCHANGED
    #   P1  a second PROVIDER entry added under it, +40s       still ONE dashboard
    #   D2/P2  `docker restart`, same container                BOTH delivered
    #   D5  a DASHBOARD JSON edited under the same mount, +40s the new title, NO restart
    #
    # So both PROVISIONING files are start-only and both need the handler, while
    # the dashboard JSON copy must NOT get one — D5 is the row that says the
    # third grafana render is deliberately absent from this table rather than
    # forgotten, and P1 is the row that says the provider file is not (the
    # provider POLLS its dashboards; it does not re-read itself).
    #
    # The pair is spelled as two rows and not one because each render can be
    # edited alone: dropping the notify from either is a file that stops reaching
    # the process, and a single row would leave the other unpinned.
    "grafana-datasource.yml.j2": {
        "service": "grafana",
        "owner": RENDER_OWNER,
        "mode": "0640",
        "config_flag": None,
        # A DIRECTORY, not a path: grafana/grafana:13.1.0 SCANS
        # `$GF_PATHS_PROVISIONING/datasources` and reads every file in it, so the
        # file's own NAME is this repo's to choose while the directory is the
        # image's (row N1: the same body delivered as `other.yml` provisions
        # identically). The subdirectory is NOT free — row N2 puts the file at
        # the provisioning root and the datasource is never provisioned at all.
        # Pinning the full path would have reddened a rename that works, which is
        # the "guard forbids the real answer" failure this repo has already hit.
        "default_path": None,
        "default_dir": "/etc/grafana/provisioning/datasources",
    },
    "grafana-dashboards.yml.j2": {
        "service": "grafana",
        "owner": RENDER_OWNER,
        "mode": "0640",
        "config_flag": None,
        "default_path": None,
        "default_dir": "/etc/grafana/provisioning/dashboards",
    },
    # plex-blip-manual-triage Step 5a — the FIFTH row, and it is here because the
    # paragraph above says it should be: this table exists "so the next render
    # task added to this role has a check that already names the invariant", and
    # the blackbox config is the next render task this role has gained.
    #
    # `--config.file` and not a `default_path`, which is a MEASUREMENT of the
    # image rather than a copy of the prometheus row: `docker inspect
    # prom/blackbox-exporter:v0.28.0` shows `Cmd` = `["--config.file=/etc/
    # blackbox_exporter/config.yml"]`, i.e. the container-side path is supplied by
    # a FLAG the compose `command:` overrides, so the flag must agree with the
    # mount's own target and the literal `/etc/blackbox_exporter/config.yml` is
    # this repo's to move. Pinning that literal would have reddened a rename that
    # works on both sides — the "guard forbids the real answer" failure the
    # grafana rows were written to avoid one step earlier.
    #
    # THE MODE IS THE ONE FIELD THAT IS NOT COPIED FROM ANY ROW ABOVE. See
    # `BLACKBOX_MODE`: this image runs as ROOT (measured, and the routing that
    # ordered this row said the opposite), so 0640 root:root is readable AND
    # withholds the token row `5b` puts in this same file.
    "blackbox.yml.j2": {
        "service": BLACKBOX_SERVICE,
        "owner": RENDER_OWNER,
        "mode": BLACKBOX_MODE,
        "config_flag": "--config.file",
        "default_path": None,
    },
    # plex-blip-manual-triage Step 7a — the SIXTH row, arriving by the route the
    # paragraph above prescribes rather than being backfilled after a review
    # found it missing.
    #
    # THE CONTAINER-SIDE HOP IS A THIRD CARRIER AND THAT IS THE WHOLE REASON THIS
    # ROW IS INTERESTING. The five rows above resolve `reads_it` one of two ways:
    # a `command:` FLAG the compose spec carries (prometheus, blackbox), or a path
    # the IMAGE fixes (traefik, and the grafana pair's `default_dir`). A rule file
    # is neither — Prometheus has no `--rule.file` flag and no built-in rules
    # path, and the only thing that names this file is `rule_files:` inside
    # ANOTHER template this same role renders. So the hop is `named_in`, read
    # through `_rule_files_entries`, and the relation the acceptance asks for —
    # the render's `dest` and the `rule_files:` value are ONE thing, not two
    # literals that agree — is spelled here rather than as a second literal
    # anywhere. Moving the file moves both ends or reddens; that is the c6c4/e627
    # class this objective has already charged twice.
    #
    # THE HANDLER IS REQUIRED AND IT IS MEASURED (`PROM_RULES_DELIVERY_EVIDENCE`,
    # rows D1-D4). The four rows above each earned their `notify:` on ONE finding
    # — the process does not re-read. This file has TWO: the process does not
    # re-read rule files (D2 — the container sees the new bytes and serves the old
    # rule set 40s later), and a single-FILE bind mount does not even follow
    # ansible's atomic replace (D3 — the container cannot see the new bytes at
    # all). `docker restart` delivers both (D4).
    #
    # THE MODE IS 0644 AND IT WAS DRIVEN ON THIS FILE (`PROM_RULES_MODE`): 0640
    # root:root under the pinned image is `restarts=7` with `permission denied` on
    # the rule path — the same crash loop that emptied this stack's TSDB for two
    # weeks — and NOT an inference from the prometheus.yml row's digits.
    "plex-blip-rules.yml.j2": {
        "service": PROMETHEUS_SERVICE,
        "owner": RENDER_OWNER,
        "mode": PROM_RULES_MODE,
        "config_flag": None,
        "default_path": None,
        "named_in": PROM_SCRAPE,
    },
}


def _render_task_scalar(task: str, key: str):
    """The scalar value a render task's `ansible.builtin.template:` gives `key`.

    Step-5b. ONE reader for `mode`, `owner` and `group`, and for the mode read a
    second time by `test_blackbox_sessions_probe_carries_the_vault_token` — the
    world bit and the reload contract must not be able to disagree about which
    line they are looking at. A second regex over the same key in a second clause
    is the two-readers-drift defect this file spent Step-2a rounds 13-15 on.

    Returns `None` when the key is absent, which every caller distinguishes from
    a present-but-wrong value: those are different reds.

    NOT `\\d+`, deliberately: the previous mode reader was `"?(\\d+)"?` and so an
    `owner: root` would have been invisible to it, while a `mode: u=rw,g=r`
    (which `ansible.builtin.template` accepts) read as ABSENT rather than as
    unpinned. Taking the raw scalar and letting the caller interpret it means the
    world-bit clause can red on a symbolic mode instead of silently not seeing it.
    """
    match = re.search(
        rf'(?m)^[^\S\n]*{re.escape(key)}:[^\S\n]*(\S.*?)[^\S\n]*$', task or ""
    )
    return match.group(1) if match else None


def _render_task_validate(task: str) -> str | None:
    """A render task's `validate:` command folded to one line, or None if absent.

    Step-7c. `ansible.builtin.template`'s `validate:` is a `>-` folded scalar
    here — the command spans several indented lines under the key — so a
    single-line reader like `_render_task_scalar` would see only the block
    indicator. This joins the continuation lines the way YAML folds a `>` block
    (one space per line break) so the caller reads the exact command string
    ansible will run with `%s` replaced by the temp render. Horizontal-whitespace
    classes only on the key line, same reason as `_block_scalar`; a continuation
    line is any line more indented than the `validate:` key, so a `notify:` back
    at the task-key indent ends the scalar rather than being folded into it.
    """
    m = re.search(r'(?m)^([ \t]*)validate:[ \t]*(.*?)[ \t]*\r?$', task or "")
    if not m:
        return None
    key_indent = len(m.group(1).expandtabs())
    head = m.group(2).strip()
    # A block-scalar indicator (`>`, `>-`, `|`, `|+`, ...) carries no content.
    parts = [] if re.fullmatch(r'[>|][+-]?', head) else ([head] if head else [])
    for line in task[m.end():].splitlines():
        if not line.strip():
            continue
        lead = line[: len(line) - len(line.lstrip(" \t"))]
        if len(lead.expandtabs()) <= key_indent:
            break
        parts.append(line.strip())
    return " ".join(parts) if parts else None


def _render_task_block(body: str, src: str) -> str:
    """The `ansible.builtin.template` task block that renders `src`.

    Sliced from the `- name:` line that opens the task holding `src: <src>` to
    the next task at the same indent, so a `notify:` belonging to a NEIGHBOURING
    task cannot answer for this one — the specific way a whole-file grep for
    "notify: Restart prometheus" would be vacuous here, since the string would
    then be satisfied by the traefik task next door.

    ANCHOR, per the rule above: a task is a column-0 list entry of tasks/main.yml
    (`\\n- name:`), which is the document root of an Ansible task file, so this
    already walked a path and the rule is stated rather than changed. Step-2a F1,
    round 9 adds only the second half: a `src:` rendered by TWO tasks — a
    plausible stage-then-swap edit — returns "" rather than the first of them.
    The review measured that the wrong pick happens to redden anyway (the second
    task carries no `notify:`), so this is not a hole being closed; it is the
    incidental being removed, because "fails closed because the decoy was
    careless" is not the same claim as "fails closed". Measured free: all nine
    `src:` values in the delivered tree resolve exactly once
    (logs/calibration-step02a-f1-round9.log, leg B).
    """
    ms = list(re.finditer(rf'(?m)^\s*src:\s*{re.escape(src)}\s*$', body))
    if len(ms) != 1:
        return ""
    start = body.rfind("\n- name:", 0, ms[0].start())
    if start == -1:
        return ""
    end = body.find("\n- ", start + 1)
    return body[start:end if end != -1 else len(body)]


def _handler_block(body: str, name: str) -> str:
    """The handler named `name` in handlers/main.yml, or "" if there is none.

    ANCHOR, per the rule above: a handler is a column-0 list entry of the
    document root (`^-\\s*name:`), so this one already carried no anchor defect —
    which is worth saying, because the round-8 header claimed that of the whole
    file without checking. Step-2a F1, round 9 adds the resolves-once half for
    the same reason as `_render_task_block`: two handlers of one name is a state
    the guard cannot pick between, and both handler names in the delivered tree
    resolve exactly once (leg B).
    """
    ms = list(re.finditer(rf'(?m)^-\s*name:\s*{re.escape(name)}\s*$', body))
    if len(ms) != 1:
        return ""
    end = body.find("\n- ", ms[0].end())
    return body[ms[0].start():end if end != -1 else len(body)]


def _norm_path(path: str) -> str:
    """A path with surrounding quotes stripped and `{{ var }}` spacing collapsed.

    The render task quotes its `dest` and compose does not, and either side may
    space a Jinja expression differently; normalising both here is what lets the
    two be compared as the SAME string instead of pinned as two literals.
    """
    return re.sub(r'\{\{\s*(.*?)\s*\}\}', r'{{\1}}', _yaml_unquote(path))


# The value a per-entry reader records for a key whose ENTRY IT COULD NOT READ.
# Nothing pinned in these templates can equal it, so every caller reddens on it: the
# value compares unequal, `_label_members` yields it as its only member, and
# `_bind_mount_target` finds no source matching the render `dest`.
UNREADABLE = "<UNREADABLE ENTRY>"


def _unreadable(out: dict, key=None) -> dict:
    """Record an entry a reader could not decode — the FAIL-CLOSED half of last-wins.

    Step-3a F1, round 5. Every reader below builds a map the runtime resolves LAST
    WINS, and every one of them used to `continue` past an entry its regex could not
    read. Assignment never REMOVES anything, so the skip left the EARLIER value
    standing while the runtime took the entry the guard could not read: the delivered
    entry IS the fallback, which is exactly the state fail-closed has to exclude.
    The round-4 docstring on `_kv_entries` asserted the opposite ("its key is simply
    absent and the caller reddens") — true only when nothing precedes it.

    ONE rule, stated here because the class is the READER and not the region:

        readable        -> assign it (last wins).
        unreadable, key discernible from the entry -> that ONE key is UNREADABLE.
        unreadable, no key at all -> every key assigned SO FAR is UNREADABLE.

    The third clause is bounded by last-wins and not by caution: an entry with no
    discernible key could be about any key that precedes it, while a key assigned
    LATER by a readable entry genuinely does win at the runtime, so poisoning
    forward would be stricter than the runtime rather than equal to it.

    An entirely ABSENT key needs no poison — the callers already redden on it (rows
    C2/C3), which is what makes "absent" fail-closed and a stale value not.

    Price, measured on the delivered templates: ZERO. Every `environment:`, `labels:`
    and `volumes:` entry and every `.env` line reads today, so no row of the gate
    moves (logs/red-step03a-unreadable-entry.log, delivered tree PASS 39/39 in both
    modes).
    """
    if key is not None:
        out[key] = UNREADABLE
        return out
    return dict.fromkeys(out, UNREADABLE)


# A Jinja construct: an expression, a statement, or a comment. All three render to
# something this guard cannot know, and all three are legal mid-token.
#
# BOTH ENDS, round 8. A construct is a delimited SPAN, and every caller here reads
# a key out of a field some Jinja-blind splitter produced — `spec.split(":")`,
# `line.split("=", 1)`. A construct that straddles the separator therefore lands
# its OPEN in one field and its CLOSE in the NEXT, and matching only the open lets
# the second field read as resolvable while the first absorbs the evidence:
#
#     - {{ dir }}/legacy.yml{{ ':/etc/prometheus/prometheus.yml' }}:ro
#       \_____________ field 0 (source) ____/ \__ field 1, the KEY __/
#
# Field 1 carries no `{{` at all, so round 7's predicate passed it, the entry filed
# under the phantom key `/etc/prometheus/prometheus.yml' }}`, and the DELIVERED bind
# kept standing while compose resolved the shadow onto the real target (rc=0, four
# spellings, logs/red-step03a-jinja-close-pre.log rows M1/M2/M3/M7). Half a
# delimiter pair is still a Jinja construct; the guard cannot resolve either half.
_JINJA_DELIM = re.compile(r'\{[{%#]|[}%#]\}')


def _resolvable_key(key: str) -> bool:
    """True when `key` is a key this guard can RESOLVE — i.e. carries no Jinja.

    Step-3a F1, round 7, and the KEY side of the same class round 6 closed on the
    ACCEPT side. Round 6 taught every per-entry reader to read a scalar only where
    the PARSER produces one; what it did not ask is what the scalar it accepted is
    then USED as. In four regions the answer is: as the KEY of a map the runtime
    resolves LAST WINS.

        volumes:      the mount TARGET          (`_service_mount_map`)
        environment:  the name before `=`       (`_kv_entries`)
        labels:       the name before `=`       (`_kv_entries`)
        the `.env`    the name before `=`       (`_env_assignments`)

    THIS GUARD READS TEMPLATES, so a key can be Jinja — and a Jinja key is not a
    key, it is a promise of one. The reader has no idea which:

        - {{ docker_host_project_dir }}/legacy.yml:{{ '/etc/prometheus/prometheus.yml' }}:ro

    Round 6 accepted `{{` on BOTH halves of a mount spec ("a Jinja expression may
    render to either half"), which is true of the SOURCE — that is a value, and
    seven delivered entries spell it — and false of the TARGET, which is the key.
    Filed under `{{'/etc/prometheus/prometheus.yml'}}` the entry matches nothing,
    so the DELIVERED bind keeps standing at the real target while ansible renders
    the two onto one path and compose hands the container the shadow. Measured
    rc=0 on the real parser, and the process reads the shadow file
    (logs/red-step03a-jinja-key-pre.log, rows J1/J2/J3 GREEN at PASS 39/39).

    So the answer is the one `_unreadable` already gives for an entry with no
    discernible key: an opaque key could be ANY key, including one already
    assigned, so it poisons keyless. It cannot poison itself — there is no "itself"
    to poison.

    `{%` and `{#` count too, and that is deliberately stricter than the runtime: a
    `{% if %}`-wrapped assignment really might not be there at all. It is the same
    refusal `_scrape_job_block` already makes for a Jinja either-or pair of one job
    ("the guard is not being asked to pick — it is being asked to stop guessing").

    ROUND 8 — THE KEY THIS IS ASKED ABOUT CAME OUT OF A JINJA-BLIND SPLIT. Every
    call site hands over a FIELD, not a token: `spec.split(":")[1]` here,
    `line.split("=", 1)[0]` at the other four. A Jinja construct is a delimited
    SPAN, so one that CONTAINS the separator moves the field boundary and puts its
    OPEN in the previous field — where round 6 is right to allow it, that being the
    source/value side — leaving this predicate a field with only a CLOSE in it:

        - {{ dir }}/legacy.yml{{ ':/etc/prometheus/prometheus.yml' }}:ro

    Field 1 is `/etc/prometheus/prometheus.yml' }}`, which starts with `/`, passes
    `_short_mount_fields`' shape test, and carried no `{{` for the old predicate to
    see. Four spellings measured GREEN at `PASS: 39/39` before this and RED after,
    each one `docker compose config` rc=0 resolving the shadow onto the real target
    (logs/red-step03a-jinja-close-{pre,post}.log, rows M1/M2/M3/M7).

    So `_JINJA_DELIM` matches BOTH ends. That is a fix at the DELIMITER rather than
    at the spelling: wherever the boundary falls, one half of the pair is in the
    field this reads, and half a construct is no more resolvable than a whole one.
    The severity is stated where it was measured (leg S of the same log): the
    ordinary spellings are already fail-CLOSED — a role variable holding the tail
    (no `:` in the template text), a bare `{{ ':' }}` separator, a `{% if %}` pair
    (its `{% endif %}` puts an OPEN back in the target field) — so reaching this
    needs a literal `:` inside the braces. A completeness hole, not a likely
    accident, and silent in exactly the way the class above is silent.

    PRICE, counted on the delivered tree in all four regions (leg D of the same
    log): ZERO. 17 `volumes:` entries — 7 with Jinja in the SOURCE, 0 in the
    TARGET; 16 `environment:` and 55 `labels:` entries — 19 with Jinja in the
    VALUE, 0 in a KEY; 5 `.env` assignments — 5 with Jinja in the VALUE, 0 in a
    key. Jinja belongs on the value side in this repo's idiom, which is why
    poisoning the key side costs nothing.
    """
    return not _JINJA_DELIM.search(key)


# ---------------------------------------------------------------------------
# THE PRECONDITION EVERY READER ABOVE SHARES: one template line is one rendered
# line. Round 9's F1 broke it at `_strip_comments`; these three patterns are the
# absence pin that closes it for ALL of them at once. See
# `test_templates_render_line_for_line`.
# ---------------------------------------------------------------------------

_JINJA_OPENER = re.compile(r'\{[{%#]')
_JINJA_CLOSERS = {"{{": "}}", "{%": "%}", "{#": "#}"}

# A REFERENCE — `name`, `name.attr`, `name[0]`, `name['k']`. Its whole output is
# ONE variable's value, so the template text bounds it as far as text can.
_JINJA_REF = (
    r"[A-Za-z_][A-Za-z0-9_]*"
    r"(?:\.[A-Za-z_][A-Za-z0-9_]*|\[\s*\d+\s*\]"
    r"|\[\s*'[^'\\\n]*'\s*\]|\[\s*\"[^\"\\\n]*\"\s*\])*"
)
# A literal whose text the TEMPLATE SHOWS IN FULL: no backslash and no real
# newline. Every escape spelling of a line feed starts with a backslash — the
# `n` form, the hex form, the octal form, the unicode form and the named form —
# so excluding the backslash excludes the class rather than one spelling.
_JINJA_LITERAL = r"'[^'\\\n]*'|\"[^\"\\\n]*\"|\d+|[Tt]rue|[Ff]alse|[Nn]one|omit"
_LINE_BOUNDED_EXPR = re.compile(
    rf"\s*{_JINJA_REF}\s*(?:\|\s*default\(\s*(?:{_JINJA_LITERAL})\s*\)\s*)?"
)
# `if`/`elif`/`else`/`endif` SELECT template text; they never produce or repeat
# any. `for`, `include`, `import`, `set`, `macro`, `call`, `filter`, `raw` all
# can, which is why they are not here.
_LINE_BOUNDED_STMT = re.compile(r'\s*(?:if|elif|else|endif)\b')
# `{%-` / `-%}` (and the `+` forms) are the renderer's OWN whitespace operators:
# they eat the whitespace on that side of the tag, NEWLINES INCLUDED. They are the
# one spelling a column-0 tag can still use to join lines, so they are refused
# before the keyword is even read. The expression side never needed this — a
# marker lands inside the body and `_LINE_BOUNDED_EXPR` is a `fullmatch`; only
# this predicate is a `match`, and that asymmetry was the round-10 hole's twin.
_WS_CONTROL_MARKER = re.compile(r'^[-+]|[-+]$')

# The templates whose LINE STRUCTURE the readers above depend on. `defaults`,
# `tasks` and `handlers` carry Jinja too and are deliberately absent: YAML parses
# THEM before Ansible evaluates the expression, so a newline in a value lands
# inside a scalar and cannot manufacture a key.
LINE_READ_TEMPLATES = (
    COMPOSE, STATIC, DYNAMIC, PROM_SCRAPE, ENV, HOMEPAGE_SERVICES, BLACKBOX_CONFIG,
    PROM_RULES,
)


def _neutralise_refs(text: str) -> str:
    """`text` with every Jinja reference replaced by a placeholder SCALAR.

    Step-5a. The gate cannot render: `jinja2` is `ModuleNotFoundError` under both
    interpreters that run these files (re-measured at this row's parent, and the
    reason `test_plex_watchdog_unit_shape.py` pins a reference CHAIN rather than a
    rendered equality). A parser, though, only needs the document's STRUCTURE, and
    substituting a scalar for each reference preserves it exactly when every
    construct is a line-bounded reference expanding to one scalar — which is not
    an assumption about this template but a property `LINE_READ_TEMPLATES`
    membership already enforces on it.

    Quoted deliberately: a bare `{{ x }}` at a value position is already valid
    YAML (a flow mapping), so an unquoted substitution would parse either way and
    the placeholder would be doing nothing. `{{ x }}:{{ y }}` at a KEY position is
    not, and that is the shape a URL or a `host:port` value takes here.
    """
    return re.sub(r'\{\{.*?\}\}', "'<REF>'", text)


# The tag PyYAML resolves a plain `<<` key to. Named rather than spelled inline
# because `_no_duplicate_keys` is the only reader and its two uses of the concept
# — do not construct it, do still count it — must not drift apart.
_YAML_MERGE_TAG = "tag:yaml.org,2002:merge"


class _StrictLoader(yaml.SafeLoader):
    """`yaml.SafeLoader` that REFUSES a duplicate — or unhashable — mapping key.

    Step-5a, and it is a repair of this row's own first cut rather than a
    precaution. `yaml.safe_load` accepts a duplicated key and silently keeps the
    LAST one, so the mutant that duplicates `prober:` was GREEN through a clause
    whose whole claim is that the document PARSES. The runtime disagrees, and
    measured on the pinned image rather than argued from the spec:

        prom/blackbox-exporter:v0.28.0 --config.check on those same bytes
        level=ERROR msg="Error loading config" err="error parsing config file:
        yaml: unmarshal errors: line 58: mapping key \\"prober\\" already
        defined at line 57"                     (logs/builder-5a-mutants.log, M19)

    That is a non-zero exit at start, which `restart: unless-stopped` turns into
    the crash loop this role has already served for two weeks over a config the
    process could not read. A parser that accepts documents the process refuses
    is not modelling the process — so the gate's reader is the strict one, and
    the duplicate is a `yaml.YAMLError` here exactly as it is there.

    AND THE SENTENCE ABOVE IS SYMMETRIC, which cost this row a round (DEC-294
    charge 1): a parser that REFUSES documents the process ACCEPTS is not
    modelling it either, and the first cut of `_no_duplicate_keys` did exactly
    that to every `<<:` merge key — a refusal `yaml.safe_load` never had. Both
    directions are now scored as a table rather than as this prose, in
    `test_the_blackbox_reader_refuses_exactly_what_the_exporter_refuses`, with
    every verdict measured on the pinned binary.

    WHAT THIS CLASS DOES *NOT* CLOSE, said here because its own sentence above is
    wider than its code: strictness of the SYNTAX is not strictness of the
    FIELDS. `prom/blackbox-exporter:v0.28.0` unmarshals into a Go struct and
    exits 1 on a field it does not know — a one-character typo
    (`valid_status_code`) is `Error loading config` at rc=1 while every YAML
    parser in existence reads that document happily. That half is closed at the
    READING CLAUSE, by `_blackbox_field_defects` against a per-level allow-list,
    and not here: it is a fact about blackbox's schema rather than about YAML.
    """


def _no_duplicate_keys(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        if key_node.tag == _YAML_MERGE_TAG:
            # A `<<:` MERGE KEY IS NOT CONSTRUCTED HERE, AND IT IS STILL COUNTED
            # — DEC-294 charge 1, and the two halves are two different defects.
            #
            # CONSTRUCTED: `SafeConstructor` has no constructor for the merge
            # tag, because `construct_mapping` FLATTENS the key away before it
            # would ever reach one. Scanning ahead of that flattening reversed
            # the order, so `construct_object` raised "could not determine a
            # constructor" and the clause printed `parses=False` about a document
            # `--config.check` exits 0 on — the mirror image of the sentence this
            # loader exists to keep, and a regression against the `safe_load` it
            # replaced. Stepping over the node hands the flattening back to
            # `construct_mapping`, which already does it correctly: flattening
            # HERE instead is the door that looks obvious and is a trap, because
            # PyYAML PREPENDS the merged pairs, so a merged-and-overridden key —
            # what a merge key is FOR — is then seen twice and reds as a
            # duplicate (measured 5/5, logs/builder-5a-r5-merge-door.log).
            #
            # COUNTED: `<<` is still a mapping key, and go-yaml v3 refuses a
            # mapping that carries it twice — `mapping key "<<" already defined
            # at line 7`, rc=1, the crash loop. A skip that also skipped the
            # bookkeeping would give up this class's own refusal for exactly the
            # key it is reaching over. The literal is the spelling the binary's
            # refusal prints, and it collides only with a QUOTED `'<<'`, which
            # that same binary refuses as an unknown field anyway.
            key = "<<"
        else:
            key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in seen
        except TypeError:
            # A YAML COMPLEX KEY (`? [a, b]` / `? {a: b}`) IS UNHASHABLE, and
            # membership on it raises `TypeError` — which is NOT a
            # `yaml.YAMLError`, so it would walk straight past the reading
            # clause's own `except` and take the suite out with a traceback:
            # rc=1 with ZERO `FAIL` lines, the crashed-reader shape this loader
            # was written to repair (DEC-286 charge 2, measured at
            # logs/critic-5a-r2-crashed-reader.log). The process refuses the
            # same bytes — `cannot unmarshal !!seq into string`, rc=1 — so the
            # reader refuses them too, and in the currency the clause catches.
            # Caught by BEHAVIOUR rather than by an isinstance list of the
            # unhashable types, so a shape nobody enumerated still fails closed.
            raise yaml.constructor.ConstructorError(
                None, None,
                # The TAG and not `repr(key)`: an unfilled deep=False sequence
                # reprs as `[]`, which names nothing. `!!seq` is also the noun
                # the binary's own refusal uses.
                f"unhashable key of type {key_node.tag} at line "
                f"{key_node.start_mark.line + 1}",
                key_node.start_mark,
            ) from None
        if duplicate:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key {key!r}", key_node.start_mark
            )
        seen.add(key)
    return yaml.constructor.SafeConstructor.construct_mapping(loader, node, deep)


_StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys
)


def _unbounded_block_tag(text: str, start: int, end: int, body: str) -> str:
    """Why this `{% %}` tag can change the LINE it is on — `""` when it cannot.

    Step-3a F1, round 10. Round 9 declared `if`/`elif`/`else`/`endif` line-bounded
    because they "SELECT template text and never produce any". That is true of the
    STATEMENT and false of the LINE, because the renderer that deploys these files
    has an opinion about the newline next to a block tag:

        trim_blocks   = True    ansible-core 2.21.1, plugins/action/template.py:58
        lstrip_blocks = False   the next line, :59 — and the role overrides neither

    `trim_blocks` DELETES the newline immediately after a `%}`. So a block tag at
    the END of a content line takes the NEXT line with it — two lines to every
    text-level reader in this module, ONE line to compose:

        - shadow.note=harmless{% if true %}
        - traefik.http.routers.prometheus.middlewares=internal-allowlist@file,…
        - traefik.http.services.prometheus.loadbalancer.server.port=9090{% endif %}

    renders as `- shadow.note=harmless      - traefik.http.routers.prometheus…`,
    ONE unpinned label, and the effective label map has
    `traefik.http.routers.prometheus.middlewares = None` with `entrypoints` and
    `tls` still standing — Prometheus published on the WAN entrypoint with NO
    `internal-allowlist`, the Error-1000 class, deployable and silent. Guard
    `PASS: 40/40` before this function existed (rows T1/T1b,
    logs/red-step03a-trim-blocks-pre.log; `docker compose config --format json`
    rc=0 agrees, leg B).

    THREE CLAUSES, EACH WITH ITS OWN MEASURED ROW — none is here on principle:

    (1) NOTHING BEFORE THE TAG, and that means NOTHING, not "no non-whitespace".
        Leading whitespace is content under `lstrip_blocks=False`: the indent
        survives, the newline after `%}` does not, so an INDENTED tag alone on its
        line re-indents the following line. Row T4 puts `      {% if true %}` above
        a COLUMN-0 label entry — outside the block to every reader here, INSIDE it
        at 6 spaces to compose, effective middlewares `security-headers@file`,
        allowlist gone, guard `PASS: 40/40` before the clause.

    (2) NOTHING AFTER THE TAG. A tag at column 0 with content after it merges
        nothing — the newline it would delete is not adjacent — but the line still
        reads as a Jinja tag to every reader here and as a fully-formed entry to
        compose. Row T2 appends `{% if true %}      - …middlewares=…` after the
        last pinned label: guard `PASS: 40/40`, compose effective
        `security-headers@file`. Placement is what made this reachable, and the
        contrast is recorded rather than hidden — the SAME row written ABOVE a
        pinned label is red only incidentally (the column-0 line ends the block
        early, so `prometheus-web`'s own labels go missing, row T2c).

    (3) NO WHITESPACE-CONTROL MARKER. `-%}` eats every whitespace character after
        the tag, the next line's indentation included, which is exactly the join
        clauses (1) and (2) forbid — a column-0 tag alone on its line is NOT
        enough while the marker is legal. `{%-` was already refused, because its
        body starts with `-` and `_LINE_BOUNDED_STMT` wants the keyword first;
        this is the mirror of an asymmetry, not a new idea (row Bm). HONESTLY
        BOUNDED: at the `labels:` site the dedent it produces is LOUD —
        `docker compose config` rc=1, "did not find expected key" (row T3) — so
        this clause is completeness at price zero, not a severity row, and it is
        claimed as nothing more.

    PRICE: ZERO. The delivered tree carries exactly two block tags, both in
    dynamic.yml.j2 and both already alone at column 0 with no marker
    (`{% if acme_resolver == 'le-dns-cf' %}` / `{% endif %}`), so every clause
    above is free today (leg P of the same log).

    WHAT THIS DOES NOT CLOSE, unchanged from round 9: DESTRUCTION. A column-0
    `{% if False %}` around a pinned line still deletes it, and this function
    accepts that tag. Row D1 re-runs round 9's measurement — fail-closed at the
    two sites the shadow would use, via poison that already existed — which is two
    sites and still not a proof.
    """
    if _WS_CONTROL_MARKER.search(body):
        return ("a whitespace-control marker — `{%-`/`-%}` eat the newline beside "
                "the tag, so the line joins whatever the marker faces")
    if not _LINE_BOUNDED_STMT.match(body):
        return "a statement that can produce or repeat text"
    head = text.rfind("\n", 0, start) + 1
    tail = text.find("\n", end)
    tail = len(text) if tail == -1 else tail
    if start != head or end != tail:
        return ("a block tag sharing its line — `trim_blocks` deletes the newline "
                "after `%}`, so the rest of the line merges with the next one")
    return ""


def _line_manufacturing_jinja(text: str) -> list:
    """Every Jinja construct in `text` this guard cannot bound to ONE rendered line.

    Returns `(line_number, construct, why)` triples — empty means the file's line
    structure survives rendering, which is the precondition every reader in this
    module is built on.

    The scan is deliberately crude and fail-CLOSED. It takes each opener to the
    FIRST matching closer, so a construct containing its own closer inside a
    string literal ends early and the remainder reads as unresolvable rather than
    as safe. Tokenizing Jinja properly would be a second parser to get wrong, and
    this guard has already paid for one (round 8's `_short_mount_fields`).

    A `{%` tag is asked about by `_unbounded_block_tag`, which needs the tag's
    OFFSETS and not just its body: round 10's hole is that `{% if %}` is bounded as
    a STATEMENT and not as a LINE, and where the tag sits on its line is the whole
    of the difference.
    """
    out, i = [], 0
    while True:
        m = _JINJA_OPENER.search(text, i)
        if m is None:
            return out
        opener = m.group(0)
        closer = _JINJA_CLOSERS[opener]
        end = text.find(closer, m.end())
        line = text.count("\n", 0, m.start()) + 1
        if end == -1:
            span = text[m.start():m.start() + 60].splitlines()[0]
            return out + [(line, span, f"no closing `{closer}`")]
        span = text[m.start():end + len(closer)]
        i = end + len(closer)
        body = span[len(opener):-len(closer)]
        if "\n" in span:
            out.append((line, span.splitlines()[0][:60],
                        "the construct itself spans lines"))
        elif opener == "{#":
            out.append((line, span[:60],
                        "a Jinja comment renders to nothing the guard read"))
        elif opener == "{%":
            why = _unbounded_block_tag(text, m.start(), i, body)
            if why:
                out.append((line, span[:60], why))
        elif not _LINE_BOUNDED_EXPR.fullmatch(body):
            out.append((line, span[:60],
                        "not a bare reference — its output is computed, not shown"))


# The ONE conditional region this repo deliberately ships: dynamic.yml.j2 gates
# the DNS-01 wildcard `tls.domains` on `traefik-dashboard`, because HTTP-01 cannot
# issue a wildcard. Two other checks already hold the ends of it —
# `test_traefik_dashboard_wildcard_domains` asserts the gate is there and
# `test_acme_resolver_is_dns_cf` pins the variable that decides it — and this one
# says there is NOTHING ELSE.
#
# Declared as a full INVENTORY: the condition AND the lines it wraps, compared as
# a MULTISET. Rounds 6 and 7 both rejected absence pins bounded by an enumeration
# because they fail open past the enumeration's edge, and a declaration keyed on a
# SIGNATURE has the same edge one level in — measured, not argued, in
# logs/red-step03a-r11-unasked-clauses.log:
#
#   X4  a SECOND, byte-identical region is invisible to a SET (multiplicity)
#   X6  a second region with this condition, this wrapped-line COUNT and this
#       FIRST line, wrapping DIFFERENT lines, is invisible to a
#       `(file, condition, count, first)` key (the body)
#
# Neither is a severity row — this condition is TRUE on the delivered tree, so a
# region carrying it emits — and they are recorded as the completeness rows they
# are. The severity lives in X1/X2/X3, where a FALSE condition deletes.
DECLARED_CONDITIONAL_REGIONS = (
    (
        "dynamic.yml.j2",
        "acme_resolver == 'le-dns-cf'",
        (
            '        domains:',
            '          - main: "{{ domain }}"',
            '            sans:',
            '              - "*.{{ domain }}"',
        ),
    ),
)

# A `-` marker is accepted HERE on purpose: `_unbounded_block_tag` refuses it, and
# a region this scan could not SEE is a region it could not report. The two
# clauses answer different questions and both must be asked of the same tag.
_IF_TAG = re.compile(r'\{%-?\s*if\s+(.+?)\s*-?%\}')
_ENDIF_TAG = re.compile(r'\{%-?\s*endif\s*-?%\}')


def _conditional_regions(text: str) -> tuple:
    """`(regions, unbalanced)` for `text` — every `{% if %}`…`{% endif %}` region.

    A region is `(line, condition, wrapped_lines)`, the wrapped lines verbatim
    (right-stripped) and INCLUDING blanks, so the caller can compare WHAT is
    gated and not merely how much. `unbalanced` is `(line, why)` for an
    unclosed `{% if %}` or an `{% endif %}` that closes nothing — both are Jinja
    errors at render time, and both mean this scan's own idea of the regions is
    wrong, so they are reported rather than skipped.

    Read from the STRIPPED line, which is wider than `_unbounded_block_tag`
    allows: a tag that shares its line or sits indented is refused by
    `test_templates_render_line_for_line` already, and a scan that could not see
    such a tag would hand its region to nobody.
    """
    regions, unbalanced, stack = [], [], []
    lines = text.splitlines()
    for n, line in enumerate(lines, 1):
        stripped = line.strip()
        opened = _IF_TAG.fullmatch(stripped)
        if opened:
            stack.append((n, opened.group(1).strip()))
        elif _ENDIF_TAG.fullmatch(stripped):
            if not stack:
                unbalanced.append((n, "`{% endif %}` closes no `{% if %}`"))
                continue
            start, cond = stack.pop()
            regions.append(
                (start, cond, tuple(ln.rstrip() for ln in lines[start:n - 1]))
            )
    unbalanced += [(n, f"`{{% if {cond} %}}` is never closed") for n, cond in stack]
    return regions, unbalanced


def _opens_flow_collection(entry: str) -> bool:
    """True when a sequence entry's value is a YAML FLOW collection, not a scalar.

    Step-3a F1, round 6 — the ACCEPT side of `_unreadable`, and the half round 5's
    sweep never asked about. `_unreadable` is reached only when a reader's readable
    regex FAILS, so a reader that MIS-PARSES is never unreadable and the poison is
    never reached. `_service_mount_map`'s spec regex accepted anything containing a
    colon; a flow mapping is exactly that, and it decoded into a phantom pair while
    the DELIVERED bind kept standing at the shadowed target (rows A1-A6).

    What decides flow-vs-scalar is the entry's FIRST content character, which is why
    this is one shared predicate rather than a per-reader regex: `[` or `{` opens a
    collection, anything else opens a scalar.

    TWO SPELLINGS ARE NOT FLOW AND BOTH MATTER HERE:

        - "{type: bind, …}"     a QUOTED `{` is a string scalar to YAML, so the
                                runtime receives the literal text and this must
                                return False (the caller then rejects it on shape,
                                which is where compose rejects it too).
        - {{ docker_host_project_dir }}/traefik.yml:/etc/traefik/traefik.yml:ro
                                `{{` opens a JINJA expression, and this guard is
                                pointed at a TEMPLATE, not at YAML. The round-6
                                review priced the naive test: "the spec starts with
                                `{`" reddens SEVEN DELIVERED entries. `{` NOT
                                followed by `{` is 0 today, so the correct
                                discriminator is free (logs/red-step03a-accept-side.log,
                                R leg: 17 entries read, 7 of them Jinja-opening).
    """
    m = re.match(r'(?s)\s*-\s*(?P<q>["\'])?(?P<rest>.*)', entry)
    if not m or m.group("q"):
        return False
    rest = m.group("rest").lstrip()
    return rest.startswith("[") or (rest.startswith("{") and not rest.startswith("{{"))


def _scalar_entry(entry: str) -> str | None:
    """A sequence entry's SCALAR value, or None when the parser hands over no scalar.

    Step-3a F1, round 6. The rule every per-entry reader's readable branch now starts
    from, stated once so the accept-side sweep can require it: read a scalar only
    where the PARSER produces a scalar. The two shapes that produce none are the ones
    the readers used to swallow or half-read:

        a FLOW collection   `- {type: bind, …}` / `- [a, b]` — a mapping or a list,
                            never the string a `KEY=VALUE` or `SOURCE:TARGET` reader
                            is looking at.
        a MULTI-LINE entry  a block mapping (`- type: bind` + continuation lines) or
                            a folded plain scalar — `\\S.*?` has no DOTALL, so this
                            already returned no match; making it explicit is what
                            lets the sweep check the branch instead of the regex.

    Surrounding quotes come off for the reason `_kv_entries` gives about
    `- "PVE_VERIFY_SSL=false"`: that is one layer YAML itself removes.

    THE WHITESPACE CLASS IS YAML'S, NOT PYTHON'S (Step-5c F1, round 4). This was
    `\\s*-\\s*…\\s*`, and `_kv_entries` states the trailing one as "the whitespace
    YAML really does drop". YAML drops `s-white ::= s-space | s-tab` (YAML 1.2
    §6.1) — U+00A0 and U+3000 are plain-scalar CONTENT, so `\\s` dropped bytes the
    parser keeps: `- traefik.http.routers.whoami-web.rule=Host(`h`)<U+00A0>` read
    as a clean rule here while docker handed traefik one ending in a character its
    lexer calls illegal, and the whole guard was `PASS: 42/42` with that router
    disabled (logs/red-step05c-rework-r4-gowhitespace-PRE.log N11/N12). ASCII rows
    P3/P4 are unmoved — those really are dropped (row C3).
    """
    if _opens_flow_collection(entry):
        return None
    m = re.fullmatch(r'[ \t]*-[ \t]*(?P<q>["\']?)(?P<spec>\S.*?)(?P=q)[ \t]*', entry)
    return m.group("spec") if m else None


# A mount's third field is an options list, not a path: `ro`, `rw`, `z`, `ro,rslave`.
_MOUNT_MODE = re.compile(r'[A-Za-z]+(?:,[A-Za-z]+)*')
# A named volume, as compose spells one: no slash, no dot-slash, no Jinja.
_VOLUME_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]*')


def _short_mount_fields(spec: str) -> list | None:
    """`[SOURCE:]TARGET[:MODE]` split into its fields — or None if this is not compose

    SHORT syntax at all.

    Step-3a F1, round 6, and the general form the review asked for: the readable
    branch accepts ONLY what compose accepts as short syntax, and everything else
    goes to `_unreadable`. Two independent tests, because either alone leaves a row
    green (measured, logs/red-step03a-accept-side.log):

        FIELD COUNT + MODE   a flow mapping splits into four `:`-fields once it
                             carries `type:`/`source:`/`target:`, so a count test
                             catches A1/A2/A6 — and NOT A3, whose keys are written
                             in the other order.
        TARGET IS ABSOLUTE   catches A4, whose middle field is ` X, target`. It does
                             NOT catch A3: reversed, the middle field is
                             ` /etc/prometheus/prometheus.yml, source`, which starts
                             with `/` and passes. `_opens_flow_collection` is what
                             settles A3, and the reason the predicate is about the
                             entry's first character rather than about its fields.

    A Jinja expression may render to either half, so `{{` passes the SHAPE test on
    both sides; everything the delivered tree spells is here (`/`,
    `/var/run/docker.sock`, `{{ … }}/traefik.yml`, `prometheus-data`, and the
    `ro,rslave` mode on `- /:/host`). Shape is all this answers — round 7 rejected
    the sentence that used to end here ("so `{{` is accepted on both sides"), because
    a Jinja TARGET is well-shaped and still unusable: the target is the caller's map
    KEY, and `_resolvable_key` is where that is settled. Keeping the split here means
    the caller can tell "not a short mount at all" from "a short mount I cannot file".

    THE SPLIT ITSELF IS JINJA-BLIND and stays that way (round 8). `str.split(":")`
    cannot see that a construct spans the separator, so the fields it returns may
    not be the fields the RUNTIME sees — `{{ ':/etc/…' }}` puts the boundary inside
    the braces. Teaching this function to tokenize Jinja would be a second parser to
    get wrong; instead the consequence is caught where it lands, in the caller's KEY:
    a straddling construct necessarily leaves a delimiter in the field after the
    separator, and `_resolvable_key` matches both ends of the pair.
    """
    fields = spec.split(":")
    if not 1 <= len(fields) <= 3:
        return None
    if len(fields) == 3 and not _MOUNT_MODE.fullmatch(fields[2].strip()):
        return None
    target = _norm_path(fields[1] if len(fields) >= 2 else fields[0])
    if not target.startswith(("/", "{{")):
        return None
    if len(fields) >= 2:
        source = _norm_path(fields[0])
        if not (source.startswith(("/", "./", "../", "~", "{{"))
                or _VOLUME_NAME.fullmatch(source)):
            return None
    return fields


def _service_mount_map(service_block: str) -> dict:
    """A service's bind mounts as the `{container target: host source}` map docker

    resolves — keyed by the TARGET, because that is the runtime's own key, and
    LAST WINS.

    Step-2a F1, round 14, F2: `volumes:` is the fourth region of `_kv_entries`'
    class (a string sequence the runtime maps by an in-string key) and the read
    that missed it was this one. Two mounts onto the SAME container-side target
    are legal YAML and legal compose — nothing is duplicated as far as any parser
    is concerned — and only the last survives; a second `/srv/legacy/prometheus.yml`
    appended after the delivered entry was PASS 36/36 printing
    `2/2 paths whole, broken={}` while `docker compose config` rc=0 kept ONLY
    `/srv/legacy/prometheus.yml` at that target and the container read that file
    (logs/red-step02a-rework-f1-round14.log, rows V1/V2; the delete-controls
    VC1/VC2 are RED). That is the Step-2a delivery defect round 2 added the
    render task and handler for, reintroduced one line lower and invisible.

    The PROCESS was asked, not just compose (logs/red-step02a-rework-f1-round14b.log,
    the pinned `prom/prometheus:v3.12.0`, shipped shape, no published ports): the
    delivered single mount loads the rendered file (`/api/v1/status/config` echoes
    it back, `scrape_interval=37s`, `jobs=['pve']`), the shadowed pair loads the
    SHADOW (`scrape_interval=1m31s`, `jobs=['legacy']`) from a container that starts
    normally, and the deleted mount loads the image's own default (15s, `jobs=
    ['prometheus']`, i.e. scraping nothing but itself — the case this clause's
    docstring was already written against). Which file the process READ is the
    claim `test_rendered_configs_reach_the_service_that_reads_them` makes, so it is
    the thing measured rather than compose's answer about its own model.

    Named volumes (`prometheus-data:/prometheus`) land here too; they are simply
    never equal to a render task's `dest`, so they answer nothing.

    Entries come through `_list_entries`, so this is the same funnel as
    `_service_labels`/`_service_env_map` — decommented, sliced at the `-` column.

    THE SECOND LIVE SITE OF `_unreadable`'s CLASS, and round 5 found it here after
    the review bounded that class at `_kv_entries`. The claim this docstring used to
    make — "a long-form mount spans several lines and no single-line spec matches it,
    so it is skipped and its target is absent" — is the round-4 fail-closed claim
    verbatim, and false for the same reason: skipping it leaves the DELIVERED bind
    standing at that target, and the two shapes it skips both WIN at the runtime.
    Measured on real `docker compose` v5.3.1 with `busybox:1.37`, two entries onto
    one target (logs/green-step03a-unreadable-entry-process.log):

        - ./a.txt:/data/f.txt:ro      then  - /data/f.txt
            compose resolves ONE mount, `type: volume` — the bind is GONE, and the
            container finds a DIRECTORY at that path (`cat: Is a directory`). A
            single-part short entry is an ANONYMOUS VOLUME: it takes the target and
            has no host source, so its target is recorded UNREADABLE rather than
            skipped.
        - ./a.txt:/data/f.txt:ro      then  - type: bind / source: ./b.txt / target: …
            compose resolves ONE mount and the container reads `b.txt`. Long form
            wins outright; nothing in this reader parses a mapping entry, so it
            poisons every target read so far.

    Both are silent by exactly the route this clause's own docstring names: with the
    rendered `prometheus.yml` displaced, Prometheus starts on the image's default and
    scrapes nothing but itself.

    Named volumes (`prometheus-data:/prometheus`) land here too; they are simply
    never equal to a render task's `dest`, so they answer nothing.
    """
    out = {}
    for entry in _list_entries(_indented_block(service_block, "volumes")):
        spec = _scalar_entry(entry)
        parts = _short_mount_fields(spec) if spec is not None else None
        if parts is None:
            # Not compose SHORT syntax — a flow or block long-form mount, which WINS
            # outright at the runtime. Nothing here names a target we may trust, so
            # every target read so far is poisoned.
            out = _unreadable(out)
            continue
        target = _norm_path(parts[1] if len(parts) >= 2 else parts[0])
        if not _resolvable_key(target):
            # Round 7: the target is THIS MAP'S KEY, and a Jinja one names no key at
            # all — it may render onto any target here, so it poisons keyless rather
            # than filing itself under a key nothing can match.
            out = _unreadable(out)
        elif len(parts) >= 2:
            out[target] = _norm_path(parts[0])
        else:
            # An anonymous volume: the target is the whole spec and there is no host
            # source, so this target can no longer answer for any render `dest`.
            out = _unreadable(out, target)
    return out


def _bind_mount_target(service_block: str, host_path: str) -> str | None:
    """The container-side path `host_path` is EFFECTIVELY bind-mounted at, or None.

    Returning None is the interesting answer: it means the file the role writes
    is not the file this service reads at any target — either the render `dest`
    moved, or the mount did, or the mount was deleted, or (round 14) a later
    entry took the target away from it. Docker treats the first three the same
    way at `up` time (it invents the missing host path as a DIRECTORY) and the
    fourth not at all; every one of them is silent, and the deleted-mount case is
    the quietest: Prometheus starts on the image's own default config and scrapes
    nothing but itself.

    Asked of `_service_mount_map`, so the question is the runtime's question —
    which host file ends up at each target — and not "does an entry mentioning
    this host path exist". A host path mounted at two DIFFERENT targets returns
    None as well: both mounts are live, so there is no single answer for
    `reads_it` to be derived from, and a guard that picked one would be picking.

    THE HOST PATH NEED NOT BE THE MOUNT ITSELF (Step-4a F1, round 3). The two
    grafana rows render INTO a mounted DIRECTORY — `dest` is
    `…/grafana/provisioning/datasources/datasource.yml` under a
    `…/grafana/provisioning` mount — and an equality-only read returns None for
    every one of them, reddening a tree that is correct. That is not a
    hypothetical: the review that asked for these rows flagged it in advance,
    because a row copied verbatim from the two above would have failed closed for
    the wrong reason and read as "the fix does not work".

    So a host path that lies UNDER a mount source resolves to its own place
    inside that mount's target, which is the path the process actually opens.
    The set-of-one rule is unchanged and now also covers NESTED mounts: a file
    under both `…/provisioning` and `…/provisioning/datasources` has two live
    answers, docker resolves it by the deeper one, and a guard that picked would
    again be picking.
    """
    want = _norm_path(host_path)
    hits = set()
    for target, src in _service_mount_map(service_block).items():
        src, target = src.rstrip("/"), target.rstrip("/")
        if src == want:
            hits.add(target)
        elif want.startswith(src + "/"):
            # `src + "/"`, never a bare prefix: `…/grafana/provisioning-old` must
            # not answer for a file under `…/grafana/provisioning`. UNREADABLE
            # and named volumes fall out here too — neither is a path a `dest`
            # can sit under.
            hits.add(target + want[len(src):])
    return hits.pop() if len(hits) == 1 else None


def _service_labels(body: str, name: str) -> list:
    """One compose service's `labels:` ENTRIES, one string each.

    Step-2a F1, round 12 — and the shape of pin the round-11 sweep could not
    return. Both greps that sweep prescribes look for a REGION: a span (`.*?`,
    `(?s)`) or a hand-rolled slicer (a `(.*?)` capture bounded by a glyph, a
    lookahead on `^\\s{N}\\S`). A pin with NEITHER is invisible to both —

        re.search(r'routers\\.grafana\\.middlewares\\s*=\\s*[^\\n]*internal-allowlist', compose)

    a raw whole-file substring search over an UN-COMMENT-STRIPPED
    `compose.yml.j2`. There were ELEVEN of those in SIX clauses and they were the
    clauses carrying the internal-vs-public split, so the comment-carrier rule
    round 11 applied to `test_homepage_allowed_hosts` had never been applied one
    file over to the pins that pin the allowlist itself.

    Two carriers, and that is why the read is SERVICE-SCOPED and not merely
    decommented (logs/red-step02a-rework-f1-round12.log):

    * an ordinary `# was: traefik.http.routers.<r>.middlewares=internal-allowlist@file,…`
      documentation comment — this repo's own migration idiom. With
      `internal-allowlist@file` DELETED from a router and that comment above it,
      the guard stayed at PASS 36/36 (rows A1, A4, A5), `docker compose config`
      returned rc=0 RESOLVING `routers.whoami.middlewares=security-headers@file`,
      i.e. a state `just play` ships, and on the pinned `traefik:v3.7.5` with the
      real docker provider a client outside all four allowlisted ranges got
      HTTP 200 where the delivered tree answers 403
      (logs/review-step02a-rework-f1-round12b.log). `dynamic.yml.j2` says :80/:443
      are WAN port-forwarded to this host, so that middleware is the only thing
      between the forward and Grafana/Prometheus/Homepage/Uptime-Kuma.
    * a LABEL on a DIFFERENT service. `_strip_comments` alone closes the first
      door and not this one: with grafana's own allowlist dropped and the same
      label placed on `whoami`, a strip-only fix was still GREEN (leg E, E2) — so
      the pin has to be asked of the labels that actually govern the router.

    The entries are `_list_entries(_indented_block(_compose_service_block(...)))`:
    three helpers that already exist, and `_compose_service_block` strips comments
    via `_key_bounded_block`, which is the point. Everything fails CLOSED — a
    missing service, a `labels:` key that resolves more than once, or a labels
    MAPPING instead of a sequence returns `[]` and reddens the caller (row P5,
    disclosed: mapping form is legal compose and the runtime treats it the same,
    and it was RED before this change too).

    ABSENCE pins do NOT come through here, deliberately. "No `tls` label on the
    `<svc>-web` twin" and "no `tls.domains` left on whoami" are claims about the
    whole document — a `tls` label for router X sitting on service Y still
    configures router X — so narrowing them to one service would fail OPEN. Those
    three read `_strip_comments(compose)`: as wide as the raw search, minus the
    comment carrier that made them FALSE REDS on correct trees (rows A8/A9/A10).
    """
    return _list_entries(_indented_block(_compose_service_block(body, name), "labels"))


def _kv_entries(entries: list) -> dict:
    """`- KEY=VALUE` sequence entries as the map their runtime resolves, LAST WINS.

    Step-2a F1, round 14 — and the CRITERION that bounds this class, which is why
    it is stated on the shared reader instead of on each caller. Rounds 13 and 14
    both fixed regions of one shape, and the shape is not "compose labels" or "a
    .env":

        a duplicate YAML **KEY** is caught by somebody — `just test`'s own
        ansible-lint reddens `yaml[key-duplicates]` (exit 2) on a second
        `docker_host_pve_user:`, compose refuses a duplicated SERVICE key
        (`mapping key already defined`), promtool refuses a duplicated
        prometheus.yml key (`field already set`), and `_indented_block` returns
        "" for a key that resolves twice (round 9) — while a duplicate entry in a
        **STRING SEQUENCE THE RUNTIME MAPS BY AN IN-STRING KEY** is invisible to
        every linter, because nothing is duplicated as far as YAML is concerned.

    Four regions in the files this guard reads meet that criterion, and they are
    the four `_kv_entries` / `_service_mount_map` / `_env_assignments` now read as
    maps: `labels:` and the `.env` document (round 13), `environment:` and
    `volumes:` (round 14). `command:` is the FIFTH and it is read the same way by
    BOTH of its consumers — `no_collector_config` takes the LAST of the
    `--collector.config`/`--no-collector.config` argparse pair, and `reads_it`
    takes the LAST `--config.file=` via `_last_flag_value` (Finalizer, round 15:
    round 14 named this region and fixed only the first of the two). Round 13's
    own bound ("exactly the labels
    SEQUENCE and the .env document") was an enumeration with no rule behind it,
    which is how it came to be short by two regions in the same file; a criterion
    can be CHECKED against the guard's reads, and leg S of
    logs/red-step02a-rework-f1-round14.log does exactly that.

    AN ENTRY THIS CANNOT READ IS THE ONE THING IT MUST NOT SKIP (Step-3a F1,
    round 5). This docstring used to claim the opposite — "an entry this cannot read
    as a single-line `- key=value` … is skipped, so its key is simply absent and the
    caller reddens" — in the round the `.strip()` was deleted from it. `out[key] =
    val` never removes anything, so the skip left the EARLIER readable value standing
    while the runtime resolved the region LAST WINS and took the entry the guard could
    not read. Fail-closed needs there to be nothing to fall back to; here the
    delivered entry IS the fallback, and the spelling that reaches it is compose's own
    documented host pass-through:

        - PLEX_ADDR                 no `=` at all. `docker compose config` rc=0
                                    resolves `PLEX_ADDR: null` and the variable is
                                    ABSENT from the process environment, which is
                                    `collector.rb:11`'s `|| "http://localhost:32400"`
                                    — the exporter probes its OWN container at 200
                                    with `plex_up 0` and the target still UP.
        - …whoami.middlewares       the same shape in `labels:`: compose resolves the
                                    label to `""`, and on pinned `traefik:v3.7.5` an
                                    empty middlewares label is effect-identical to no
                                    label at all — the request the allowlist must 403
                                    gets 200, with the router `enabled` and no error
                                    logged. Eleven routers spell that label.

    So every unread entry goes through `_unreadable`, where the rule and the price
    are stated. Surrounding quotes still come off, because `- "PVE_VERIFY_SSL=false"`
    is the same env var to docker.

    THE VALUE IS RETURNED AS THE PARSER HANDS IT OVER, and that is the third and
    last normalization this reader lost (Step-3a F1, round 4). `.lower()` went in
    round 2 and `.strip('"\\'')` in round 3, both from the clauses DOWNSTREAM of
    here; the `.strip()` that survived was in this expression, so `env_pinned`,
    `port_agrees` AND `addr_from_var` all read through it, and whitespace is not a
    layer YAML removes either:

        a PLAIN scalar loses its leading/trailing whitespace as a WHOLE, and the
        whole scalar is `KEY=value` — so a space AFTER the `=` is INTERNAL to it
        and survives; inside `"KEY=value "` YAML strips nothing at all.

    Measured on the REAL rendered template with `docker compose config`:
    `- PLEX_SSL_VERIFY= true` resolves to `' true'`, `- "METRICS_PREFIX=plex "` to
    `'plex '`, and `docker compose run … | cat -A` prints them into the process
    environment (`logs/green-step03a-whitespace-process.log`). Eleven whitespace
    spellings of the six pinned keys were PASS 39/39 before the deletion and are
    RED after it, at ZERO price (logs/red-step03a-whitespace.log ->
    `green-…log`): `PLEX_SSL_VERIFY=' true'` is 200 with the FULL series set and
    verification silently OFF, while `METRICS_PREFIX=' plex'` and `PORT=' 9594'`
    cannot boot at all.

    What the REGEX still folds is the parser's own work, which is why the price
    rows stay green: `\\s*-\\s*` is the sequence indicator, and the trailing `\\s*`
    is the whitespace YAML really does drop — after a PLAIN scalar (`- KEY=10   `
    is `10`, row P3) and after a closing quote (`- "PORT=9594"   `, row P4). One
    layer, on the side the parser owns.
    """
    out = {}
    for entry in entries:
        spec = _scalar_entry(entry)
        m = re.fullmatch(r'(?P<key>[^\s"\'=]+)=(?P<val>.*)', spec) if spec else None
        if m and _resolvable_key(m.group("key")):
            out[m.group("key")] = m.group("val")
            continue
        # The key is still legible in every unreadable shape that names one — a bare
        # `- KEY`, a mapping entry `- KEY: v`, a plain scalar folded over two lines —
        # so the poison lands on that key alone; a keyless entry poisons what precedes
        # it (`_unreadable`). Two shapes name no key this reader may trust and both
        # poison keyless: a FLOW mapping, whose old fallback the round-6 review
        # measured landing on `{PLEX_ADDR` with the real `PLEX_ADDR` left standing,
        # and (round 7) a JINJA key, which is the same phantom one layer up —
        # `- {{shadow_key}}=http://stolen:1` parsed CLEANLY here and filed itself
        # under `{{shadow_key}}` while compose resolved PLEX_ADDR to the shadow.
        named = (None if _opens_flow_collection(entry)
                 else re.match(r'\s*-\s*["\']?(?P<key>[^\s"\':=]+)', entry))
        key = named.group("key") if named else None
        out = _unreadable(out, key if key is not None and _resolvable_key(key) else None)
    return out


def _service_env_map(body: str, name: str) -> dict:
    """One compose service's `environment:` as the map DOCKER resolves.

    Step-2a F1, round 14 — the third region of `_kv_entries`' class, and the one
    carrying the credential this task exists to wire. `environment:` is a YAML
    SEQUENCE of `KEY=VALUE` strings, so a repeated key is no parser's duplicate
    key: `docker compose config` returns rc=0, no stderr, and the LAST entry's
    value. Five pinned keys were read with a whole-block `re.search`, i.e. FIRST
    entry wins, so all five were PASS 36/36 on a tree `just play` ships with the
    wrong effective value (logs/red-step02a-rework-f1-round14.log, O1-O5; the
    delete-controls C1-C5 are RED, so green-vs-red was purely whether a second
    assignment followed the pinned one).

    The override rows are QUIETER than the deletions the clauses were written
    against, measured on the real `prompve/prometheus-pve-exporter:3.9.0` by the
    round-14 review: with `PVE_USER` DELETED the container EXITS at startup
    (`FileNotFoundError: /etc/prometheus/pve.yml`, the crash loop
    `test_pve_exporter_service_block` cites), but with `PVE_USER=''` it stays
    RUNNING and sends `Authorization: PVEAPIToken=!prometheus=<token>` — a
    credential PVE cannot authenticate, from a container that looks healthy.

    Round 13's funnel pointed one key over: `_compose_service_block` ->
    `_indented_block` -> `_list_entries` -> `_kv_entries`, so it is service-scoped
    (round 12) and decommented (round 13) for free, and labels and environment
    share ONE parse rather than two copies of it.
    """
    return _kv_entries(
        _list_entries(_indented_block(_compose_service_block(body, name), "environment"))
    )


def _service_label_map(body: str, name: str) -> dict:
    """One compose service's labels as the `{key: value}` map DOCKER resolves.

    Step-2a F1, round 13, and the class with no comment in it at all — so
    `_strip_comments` cannot be the fix. Docker labels are a MAP. A duplicate key
    in the `labels:` SEQUENCE is legal YAML (nothing is duplicated as far as the
    parser is concerned — they are two strings in a list), docker collapses them
    LAST-WINS, and round 12's pins were EXISTENTIAL over the entries
    (`any(re.search(..., e) for e in _service_labels(...))`). So the FIRST entry
    answered for a value the runtime had already replaced: one duplicated
    `routers.whoami.middlewares=security-headers@file` appended after the correct
    line was PASS 36/36, `docker compose config` rc=0 resolving the key to the
    allowlist-less value, and the server answered 403 delivered -> 200 duplicated
    on the effective map (logs/red-step02a-rework-f1-round13.log D1-D4;
    logs/review-step02a-rework-f1-round13e.log, legs H1/H2).

    So the pins ask for the EFFECTIVE VALUE of a named key, not for the existence
    of a matching entry.

    ROUND 14 CORRECTS THIS DOCSTRING'S OWN BOUND, which is the one claim round 13
    rested on. It said the collapsing surfaces were "exactly (1) the labels
    SEQUENCE and (2) the `.env` document" and that "nothing else in this guard
    reads a region the runtime flattens". That was an enumeration of regions with
    no rule behind it, and it was short by TWO regions of the same shape in the
    same file: `environment:` (`_service_env_map`) and `volumes:`
    (`_service_mount_map`), one of them carrying the PVE credential. The rule that
    replaces it — a string sequence the runtime maps by an IN-STRING key is
    invisible to every linter, while a real duplicate KEY is caught by somebody —
    lives on `_kv_entries`, where it can be checked against the guard's reads
    instead of re-enumerated.

    Built on `_service_labels`, so it inherits round 12's service scoping (a
    label on a sibling service cannot answer) and round 13's decommenting (the
    trailing comment is off the value before it is split); the `- key=value`
    parse itself is `_kv_entries`, shared with `environment:` since round 14, so
    the two regions cannot drift apart. Fail-closed behaviour is stated there.
    """
    return _kv_entries(_service_labels(body, name))


def _label_members(value: str) -> list:
    """A comma-separated label value's members, whitespace trimmed.

    Traefik reads `middlewares` and `entrypoints` as comma-separated lists, so
    membership is the claim ("this router carries the allowlist"), and a list is
    unordered as far as that claim goes. Split from the EFFECTIVE value
    (`_service_label_map`), never from the raw entry text — which is the whole
    point of round 13's F2.

    THE PER-MEMBER `.strip()` STAYS, and it is measured rather than assumed
    (Step-3a F1, round 4's sweep). It is the one other place in this guard that
    strips whitespace off a value a runtime receives, and it is live on the
    allowlist claim: eleven routers here spell the label as the two-member list
    `internal-allowlist@file,security-headers@file`, so if Traefik did NOT trim,
    `…@file, security-headers@file` would be green here while the allowlist did
    not run — fail-OPEN, worse than the F1 it came from. Measured on the pinned
    `traefik:v3.7.5` with the DOCKER provider and both middlewares from the file
    provider, `internal-allowlist` given a sourceRange the request is not in, so a
    403 proves the reference resolved and the middleware ran
    (logs/sweep-step03a-whitespace-label-list.log):

        internal-allowlist@file,security-headers@file    S1  enabled, 403 (control)
        internal-allowlist@file, security-headers@file   S2  IDENTICAL to S1 —
         internal-allowlist@file,security-headers@file   S3  Traefik's own decoder
        internal-allowlist@file ,security-headers@file   S4  trims each member, and
        internal-allowlist@file,security-headers@file    S5  the API reports the
                                                            refs already trimmed
        nonexistent@file,security-headers@file           S6  CONTROL: router
                                                            `disabled`, error
                                                            `middleware … does not
                                                            exist`, GET -> 404

    So this fold MIRRORS the parser, the way `verify_ssl_off`'s `.lower()` mirrors
    `config.py:54` and unlike `_kv_entries`' deleted `.strip()`. S6 also settles
    the severity question the row raises: an unresolvable reference DISABLES the
    router rather than silently serving without the middleware.
    """
    return [m.strip() for m in value.split(",") if m.strip()]


def _env_assignments(body: str) -> dict:
    """A `.env` template as the `{key: value}` map COMPOSE resolves — last wins.

    Step-2a F1, round 13: F2 one file over. A `.env` is line-based, not YAML, so
    a duplicate assignment is not a duplicate key any parser objects to — compose
    just takes the LAST one. `PVE_TOKEN_VALUE` duplicated with an EMPTY value
    after the vault-sourced line was PASS 36/36 while `docker compose config`
    resolved the variable to `""`, i.e. the exporter reaches PVE with no
    credential and every scrape 500s (row D5, measured with a stand-in vault
    value so the row says something the delivered render does not).

    Comments come off first, which is the same clause's round-12 finding
    (env.j2's idiom is a comment ABOVE each assignment naming the very key it
    documents) plus round 13's trailing form (rows R9/R9b).

    THE THIRD SITE OF `_unreadable`'s CLASS — and the one where the fix is to READ
    the spelling, not to poison it, because compose's dotenv reads it too. The
    round-5 review called this reader immune and BOUNDED the class at `_kv_entries`
    on the strength of one spelling: a line with no `=`, which dotenv really does
    ignore, so skipping it mirrors the parser. `export KEY=…` is a second spelling
    and it is not that one. Measured on real `docker compose` v5.3.1, an interpolated
    `${PLEX_TOKEN:-}` read out of the project `.env`
    (logs/green-step03a-unreadable-entry-process.log, leg E):

        PLEX_TOKEN=real-token                               control  -> `real-token`
        PLEX_TOKEN=real-token / export PLEX_TOKEN=           E1      -> `` EMPTY
        PLEX_TOKEN=real-token / export PLEX_TOKEN=stolen     E2      -> `stolen`
        PLEX_TOKEN=real-token / PLEX_TOKEN (no `=`)          E3      -> `real-token`
        PLEX_TOKEN=real-token /   export   PLEX_TOKEN=…      E4      -> the last one

    E1 is the vault hop going EMPTY behind a guard reading the vault-sourced line
    above it: /metrics 500s with zero series and the target DOWN, which is Step 3b's
    failure list. So the `export` prefix is part of the assignment form here, and E3
    is the price row that keeps this from becoming a poison — a non-assignment line
    is skipped because THE PARSER skips it, not because the reader gave up.
    """
    out = {}
    for line in _strip_comments(body).splitlines():
        m = re.fullmatch(r'\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)', line)
        if m:
            out[m.group(1)] = m.group(2).strip()
        elif not _resolvable_key(line.split("=", 1)[0]):
            # Round 7, and the reason this reader needs a poison after all. E3 above
            # is skipped because DOTENV skips it — a literal line with no `=` assigns
            # nothing. A line whose KEY HALF is Jinja is the opposite case: it may
            # render into an assignment of any name, and `{{ 'PLEX_TOKEN' }}=stolen`
            # did exactly that — skipped here, resolved to `stolen` by compose's own
            # dotenv, with the vault-sourced line above it still answering the guard.
            out = _unreadable(out)
    return out


def _service_command_args(service_block: str) -> list:
    """A compose service's `command:` entries, list form or inline, decommented.

    Both spellings are in this file (`command: tunnel --no-autoupdate run` for
    cloudflared, a list for prometheus), and the comments above these blocks name
    the very flags they document — see `_strip_comments`.

    Entries come back UNQUOTED, for the reason `_kv_entries` gives about
    `- "PVE_VERIFY_SSL=false"`: `- '--config.file=/etc/prometheus/prometheus.yml'`
    is the same argv element to docker, so quoting it is a spelling choice and a
    guard that reddened on it would be a FALSE RED on a correct tree. Measured
    (row P1, logs/finalizer-step02a-adversarial-pre.log): before this, quoting
    that one entry took `test_rendered_configs_reach_the_service_that_reads_them`
    RED while `docker compose config` resolved it identically.
    """
    m = re.search(r'(?m)^([^\S\n]*)command:[^\S\n]*(.*)$', _strip_comments(service_block))
    if not m:
        return []
    if m.group(2).strip():
        args = m.group(2).strip().split()
    else:
        args = re.findall(
            r'(?m)^\s*-\s*(\S.*?)\s*$',
            _indented_block(_strip_comments(service_block), "command"),
        )
    return [re.sub(r'^(["\'])(.*)\1$', r"\2", a) for a in args]


def _last_flag_value(args: list, flag: str) -> str | None:
    """The value of the LAST `--flag=value` OR `--flag value` in an argv, or None.

    `command:` is the fifth region meeting the criterion `_kv_entries` states —
    a sequence the runtime resolves by an in-string key, invisible to every YAML
    linter because nothing is duplicated as far as YAML is concerned. Round 14
    named it and fixed only ONE of its two consumers: `no_collector_config`
    already takes the LAST of the `--collector.config`/`--no-collector.config`
    argparse pair, while `reads_it` was still membership (`f"{flag}={target}" in
    args`), so a decoy `--config.file=/etc/prometheus/decoy.yml` appended after
    the delivered entry left the clause GREEN (row G1,
    logs/finalizer-step02a-adversarial-pre.log). This is the second consumer.

    LAST, not first, is the runtime's own answer where the process accepts a
    repeat at all. Where it does not — `prom/prometheus` is kingpin, which
    refuses (`flag config.file cannot be repeated`, exit 2) rather than picking —
    the flag names a file the service never reads either way, so the clause's
    claim ("the rendered config REACHES the service that reads it") is false in
    both runtimes and this reddens for both. That refusal is why the row was a
    LOUD artifact and not a blocker: an instant crash loop under
    `restart: unless-stopped`, not the silent-healthy container of F1/F2.

    AND THE FLAG NAME IS AN IN-STRING KEY LIKE ANY OTHER (round 7). Membership was
    fixed round 15; what stayed was the assumption that an arg this reader cannot
    attribute to a flag belongs to no flag. `- {{ shadow_flag }}` is one arg to
    YAML, renders to `--config.file=/srv/monitoring/legacy.yml`, and does not start
    with `--config.file=` in the TEMPLATE — so it was skipped and the delivered
    flag answered for it. Same shape as the `volumes:` target and the
    `environment:` name, fifth region, so it takes the same predicate: an arg whose
    flag half is opaque means NO flag here can be read, and UNREADABLE is never
    equal to the mount target the caller compares it against.

    This row is LOUD at the runtime and is stated as such rather than counted with
    F1: prometheus is kingpin and refuses the repeat outright. It is
    guard-correctness — the same polarity round 6 recorded for the `environment:`
    flow mapping — and the price is zero, since no delivered `command:` arg carries
    Jinja at all (`--config.file=…`, `--path.rootfs=/host`, `--no-collector.config`).

    AND THE RUNTIME ACCEPTS TWO SPELLINGS OF THE JOIN, WHICH IS WHY THIS READS
    BOTH (5d round 4, DEC-306 charge). Until this round the match was
    `a.startswith(f"{flag}=")` and nothing else. kingpin also takes the two-token
    `--flag value` form, and a `command:` LIST is exactly where that spelling is
    natural to write — two sequence entries, which `docker compose` hands the
    daemon as two argv elements verbatim. An ABSENCE-shaped pin built on the
    `=`-only reader is therefore only as wide as this reader's spelling census,
    and it fails OPEN: measured through real ansible-core + `docker compose up
    -d` (logs/critic-5d-r3-live-space.log, re-driven at this round's hands in
    logs/builder-5d-r4-render.log), `--storage.tsdb.retention.size` + `1MB` as
    two entries is `restarts=0` with the process logging `duration=90d
    size=1MiB` — a healthy container pruned to a megabyte in minutes — while
    `no_size_cap` printed `True (…=None, want absent)`. The path flag split the
    same way put `wal/` directly in `/prometheus`, the SILENT trap
    `test_prometheus_retention_outlives_the_blip_window` documents, with
    `tsdb_path_ok=True`.

    A VALUE pin fails CLOSED on the same gap, which is the other half of the
    asymmetry and the reason this is ONE edit: the split spelling read as `None`,
    so `retention_pinned` reddened — on a CORRECT tree
    (`--storage.tsdb.retention.time` + `90d`), and so did `reads_it` on a split
    `--config.file` (rows M7/C1, logs/builder-5d-r4-redfirst.log). This file
    already calls false-RED-on-a-correct-tree a defect class in
    `_service_command_args`; closing the hole and closing the false-RED are the
    same three lines.

    THE VALUE OF A BARE FLAG IS THE NEXT ARG, and where there is no such arg to
    take — the flag is last, or the next arg is itself a flag — the answer is
    `UNREADABLE` rather than absence, for the reason this helper already gives one
    paragraph up: an arg this reader cannot attribute to a flag must not be read
    as no flag at all. Rows N1/N2 are those two shapes, both GREEN before this
    edit. That the runtime ALSO refuses them (kingpin wants an argument for the
    flag) is not what licenses the polarity — fail-closed is, since a guard that
    cannot read a list has nothing true to say about what is absent from it.
    """
    if any(not _resolvable_key(a.split("=", 1)[0]) for a in args):
        return UNREADABLE
    hits = []
    for i, a in enumerate(args):
        if a.startswith(f"{flag}="):
            hits.append(a.split("=", 1)[1])
        elif a == flag:
            nxt = args[i + 1] if i + 1 < len(args) else None
            hits.append(UNREADABLE if nxt is None or nxt.startswith("-") else nxt)
    return hits[-1] if hits else None


def _yaml_key(line: str) -> tuple | None:
    """`(indent, key, inline value)` for one YAML mapping line, or None.

    The key is returned UNQUOTED, because `ports:`, `"ports":` and `'ports':` are
    three spellings of one service key and YAML gives all three the same meaning.
    Step-2a F2, round 5: every clause here that located a key with a bare
    `^\\s*<key>:` regex was blind to the quoted forms — `"ports": ["9221:9221"]`
    on `pve-exporter` left the guard at 36/36 while the rendered file parses to
    `services.pve-exporter.ports == ['9221:9221']` and `docker compose config`
    returns rc=0 (logs/calibration-step02a-f1-round5.log, leg A).

    Sequence entries (`- "80:80"`, `- PVE_USER={{ … }}`) do not match: a line
    whose first non-space character is `-` is an item, not a key, and reading one
    as a key is how a `volumes:` entry would masquerade as a service key.
    """
    m = re.match(
        r'([^\S\n]*)(?:"([^"]+)"|\'([^\']+)\'|([A-Za-z_][\w.\-]*))[^\S\n]*:'
        r'(?:[^\S\n]+(.*))?$',
        line,
    )
    if not m:
        return None
    return len(m.group(1)), (m.group(2) or m.group(3) or m.group(4)), (m.group(5) or "").strip()


# A YAML document marker and a sequence entry. Neither can introduce a mapping
# key on its own line, and both are legitimate content in the bodies scanned
# here (`---` opens defaults/main.yml; the bucket ladder and the DNS resolver
# list in traefik.yml.j2 are sequences), so `_line_class` names them rather than
# lumping them in with the lines it cannot read. Everything ELSE that is not a
# parsable key is `unreadable`, and unreadable is what the callers fail on.
_YAML_DOC_MARKER = re.compile(r'[^\S\n]*(?:---|\.\.\.)[^\S\n]*$')
_YAML_SEQ_ENTRY = re.compile(r'[^\S\n]*-(?:[^\S\n]|$)')


def _line_class(line: str) -> str:
    """`blank` | `doc` | `seq` | `key` | `unreadable` for one YAML line.

    Step-2a F1, round 6, and the end of a four-round walk. Round 3 read one
    spelling of `ports:`, round 4 read all three, round 5 correctly stopped
    enumerating and made the reachability clauses key ALLOW-LISTS — and was
    rejected anyway, because an allow-list is bounded by the PARSER that builds
    it and that parser fails OPEN: `_yaml_key` reads only `[A-Za-z_][\\w.-]*:`
    and the callers SILENTLY DISCARDED every line it could not read. A key that
    arrives without a parsable key line was therefore invisible to the allow-list
    that claimed to catch "any compose key that does not exist yet".

    Four spellings measured, each landing `network_mode: host` as a REAL parsed
    service key with `docker compose config` rc=0, i.e. states `just play` SHIPS
    (logs/calibration-step02a-f1-round6.log, leg A): a merge key `<<: *hostnet`
    aliasing a top-level `x-` extension field, the same merge inline
    (`<<: {network_mode: host}`), YAML explicit-key syntax (`? network_mode` on
    one line, `: host` on the next), and a Jinja-emitted key
    (`{{ 'network_mode: host' }}`). Two more through `_declares_key`: an
    explicit-key second resolver rendering to
    `certificatesResolvers: ['le-dns-cf', 'le-http']`, and an explicit-key
    `vault_pve_api_token` in plaintext role defaults.

    So the answer is not a fifth enumeration of spellings — it is to classify
    EVERY line and let the callers fail CLOSED on the ones that cannot be read.
    Reading more spellings extends the walk; refusing to guess ends it.

    `doc` and `seq` are named and exempted because they carry no key by
    construction and both occur in the delivered tree. Everything else — merge
    keys, explicit-key syntax, Jinja emissions, and any construct nobody has
    thought of — is `unreadable`, without anyone having enumerated it.
    """
    if not line.strip():
        return "blank"
    if _YAML_DOC_MARKER.fullmatch(line):
        return "doc"
    if _YAML_SEQ_ENTRY.match(line):
        return "seq"
    return "key" if _yaml_key(line) else "unreadable"


def _declares_key(body: str, pattern: str) -> list:
    """Reasons `body` may declare a mapping key matching `pattern`; empty = none.

    A list rather than a bool so the caller's printed field can say WHICH line
    answered — a bare boolean cannot distinguish "the forbidden key is here"
    from "there is a line I cannot read", and those want different fixes.

    Two ways to land on the list, and the second is the round-6 fix:

    * a readable key whose name matches `pattern`. Located through `_yaml_key`,
      so the quoted spellings count and a `- item` line does not (Step-2a F2,
      round 5: the `re.search(r'(?m)^\\s*<key>:\\s*$', body) is None` this
      replaced was blind both to `"le-http":` and — because of the `\\s*$` — to
      `le-http: {acme: {…}}`, a whole second resolver on one line).
    * ANY `unreadable` line in the body. An absence pin cannot honestly claim a
      key is gone from a document it cannot fully read, and this helper backs two
      absence pins whose subjects (a second ACME resolver, a vaulted secret in
      plaintext defaults) are exactly what an unreadable line can smuggle in.

    That second clause is a whole-body condition, not a column-scoped one, which
    is deliberately stricter than it needs to be: an unreadable line nowhere near
    `certificatesResolvers:` still reddens `http_gone`. It costs nothing today —
    traefik.yml.j2 and defaults/main.yml contain ZERO unreadable lines as
    delivered (logs/calibration-step02a-f1-round6.log, leg B) — and the looser
    alternative would need a rule for which columns can hold the key, which is
    the enumeration this fix exists to stop writing.

    Reads the COMMENT-STRIPPED body, because the templates comment the very
    invariants they pin (see `_strip_comments`), so a commented-out `le-http:`
    neither matches nor reddens.
    """
    reasons = []
    for line in _strip_comments(body).splitlines():
        kind = _line_class(line)
        if kind == "unreadable":
            reasons.append(f"unreadable line: {line.strip()!r}")
        elif kind == "key" and re.fullmatch(pattern, _yaml_key(line)[1]):
            reasons.append(_yaml_key(line)[1])
    return reasons


def _service_key_lines(service_block: str) -> tuple:
    """`(keys, unreadable)` for a compose service's OWN key column.

    "Its own body" is the shallowest column in the block: `image`, `restart`,
    `environment`, `command` for `pve-exporter`, and NOT the `- PVE_USER=…`
    entries under `environment` or the `published:` line inside a long-form port
    entry. Derived from the block rather than pinned at four spaces, so a
    re-indent of the whole file does not silently empty the list.

    This is what turns the scrape-only invariant from an ABSENCE pin into a
    PRESENCE one. An absence pin is bounded by the enumeration behind it and
    fails OPEN past its edge, which is how this clause was rejected three rounds
    running: round 3 for seeing only the block spelling of `ports:`, round 4 for
    reading three spellings of `ports:` while the invariant it states is
    reachability, and reachability has doors that declare no `ports:` key at all.

    THE SECOND RETURN VALUE IS THE ROUND-6 FIX, and without it the allow-list is
    only as complete as `_yaml_key`: every line at the key column that is not a
    readable key comes back in `unreadable`, and the callers redden on it. That
    is what makes "any compose key that does not exist yet lands outside the
    allow-list" true rather than merely intended — a merge key, an explicit-key
    pair or a Jinja-emitted key is now RED for the same reason `network_mode:`
    is, instead of being dropped on the floor (see `_line_class`).

    The COLUMN is derived from every non-blank line, not only from the parsable
    ones, so a line SHALLOWER than the real keys cannot move the column and take
    the whole allow-list out of scope with it. That row is stricter than the
    runtime — a mapping whose keys sit at two columns is not a state compose
    accepts — and it is pinned because the failure it prevents is the guard
    reading an empty key list and calling it allowed.
    """
    lines = [ln for ln in _strip_comments(service_block).splitlines() if ln.strip()]
    if not lines:
        return [], []
    top = min(len(ln) - len(ln.lstrip()) for ln in lines)
    keys, unreadable = [], []
    for line in lines:
        if len(line) - len(line.lstrip()) != top:
            continue
        if _line_class(line) == "key":
            keys.append(_yaml_key(line)[1])
        else:
            unreadable.append(line.strip())
    return keys, unreadable


def _service_published_ports(service_block: str) -> list | None:
    """A service's `ports:` entries in EVERY YAML spelling, or None if absent.

    The distinction the return type carries is the whole point: `None` means the
    service declares no `ports:` key at all — the only state the scrape-only and
    outbound-only services want — while a list (even an empty one) means the key
    is there and something has to justify it.

    Step-2a F1, round 4. The clauses that pin this absence used to be
    `re.search(r'(?m)^\\s*ports:\\s*$', block) is None`, which anchors the key to
    the END of its line and therefore sees ONLY the block spelling. The flow
    spelling is invisible to it, and that is the asymmetry that makes this a
    defect rather than a style point: every other flow-vs-block gap in this file
    fails CLOSED (an inline `volumes:` makes `_indented_block` return "" and the
    delivery row goes RED), but a clause pinning an ABSENCE fails OPEN — a
    one-line `ports: ["9221:9221"]` on `pve-exporter` left this guard at 36/36
    and the whole gate at 35/35. It renders, `yaml.safe_load` parses it to a real
    list and `docker compose config` calls it valid, so it is a DEPLOYABLE state
    and not a syntax error the operator's `just play` would catch. Measured on
    the real `prompve/prometheus-pve-exporter:3.9.0` with 9221 published: `/pve`
    and `/metrics` answer an unauthenticated caller and the `target` query
    parameter is caller-controlled, so with 2b's token in place that is an
    unauthenticated read of the entire PVE API from anywhere on the LAN.

    All three spellings compose accepts are read: the flow list, the short block
    list (`- "9221:9221"`), and the long block syntax (`- target: 9221` /
    `published: 9221`), whose first line is an entry like any other here. The KEY
    is located through `_yaml_key`, so the quoted spellings (`"ports":`,
    `'ports':`) are read too — round 4's `^\\s*ports:` could not see them
    (Step-2a F2, round 5). Reads the COMMENT-STRIPPED block, because these
    templates comment the very invariants they pin (see `_strip_comments`).
    """
    lines = _strip_comments(service_block).splitlines()
    for i, line in enumerate(lines):
        parsed = _yaml_key(line)
        if not parsed or parsed[1] != "ports":
            continue
        indent, _, inline = parsed
        if inline.startswith("["):
            return [_yaml_unquote(v) for v in inline[1:-1].split(",") if v.strip()]
        if inline:
            return [_yaml_unquote(inline)]
        entries = []
        for nxt in lines[i + 1:]:
            if not nxt.strip():
                continue
            if len(nxt) - len(nxt.lstrip()) <= indent:
                break
            item = re.match(r'\s*-\s*(\S.*?)\s*$', nxt)
            if item:
                entries.append(_yaml_unquote(item.group(1)))
        return entries
    return None


def test_rendered_configs_reach_the_service_that_reads_them() -> bool:
    """Step-2a F1: a config the role RENDERS is a config the process has READ.

    Seven pins per row of `RELOAD_CONTRACT`, walked as one PATH rather than
    checked as independent strings — every hop below has been observed to break
    on its own while the others held:

    * `notified` — the render task carries a `notify:`, at the task's OWN key
      indent (the same column as the module key) and sliced to that task's block.
      Both qualifiers are load-bearing: a whole-file grep would be answered by
      the traefik task next door, and a `notify:` one level deeper sits inside
      the module's args, where it passes ansible-lint AND `--syntax-check` and
      fails only at the operator's `just play`.
    * `handler` — a handler with exactly the notified name exists. This hop is
      what makes the pin an agreement instead of two literals: rename the handler
      alone and the row reddens, rename both sides together and it does not.
    * `restarts` — that handler runs `docker compose restart <service>` in
      `docker_host_project_dir`, and the service is the one this template
      configures. A handler that restarts the WRONG service is green against any
      name-only check and delivers nothing.
    * `in_compose` — the service it restarts is defined in compose.yml.j2;
      `docker compose restart <unknown>` is an error, not a no-op.
    * `mounted` — the file the task WRITES is the file the service MOUNTS: the
      task's `dest` is the host side of one of that service's bind mounts. This
      is the hop whose absence is silent — drop the mount and Prometheus starts
      clean on the image's default config, scraping only itself, with the target
      reading UP and nothing erroring anywhere.
    * `reads_it` — the process is pointed at the CONTAINER side of that same
      mount: `--config.file=<the mount's own target>` where the image takes such
      a flag, the image's documented default DIRECTORY where it scans one
      (`default_dir`, the two grafana rows — the filename is this repo's, the
      directory is the image's), the path ANOTHER of this role's templates names
      for it (`named_in`, Step-7a's rules row — Prometheus has no `--rule.file`
      flag and no built-in rules path, so `rule_files:` in `prometheus.yml.j2` is
      the only thing that points at it), or its documented default path where it
      does none of those. Derived
      from the mount rather than pinned as a literal, so moving the container-side
      path consistently stays green and moving it on one side alone reddens.
      Read via `_last_flag_value`, not membership: `command:` is a sequence the
      runtime resolves by an in-string key, so a decoy `--config.file=` appended
      after the delivered one used to leave this GREEN. See that helper.
    * `mode` — the rendered file is readable by the uid the service runs as.
      See `RELOAD_CONTRACT`: the rows want different modes, and the prometheus
      row is repairing an outage that is live right now.
    * `owner` — Step-5b, and it is the OTHER HALF of that mode rather than a
      second spelling of it: `0640` says nothing until you know whose 0640 it is,
      and `owner: 65534` under the same digits hands group-read to an identity no
      comment in this role names. Pinned as the filesystem fact it is, from the
      `RENDER_OWNER` column — and NOT because the process could not otherwise
      read the file, which is measurably false for the blackbox row (uid 0
      bypasses the bits; see that constant). This closes the `RELOAD_CONTRACT`
      half of `task-1786187620-633b`.

    NOT pinned, deliberately: that a restart is the ONLY delivery mechanism.
    Adding `--web.enable-lifecycle` plus a POST would also work, and forbidding
    it would make this check about the implementation rather than the outcome.
    """
    tasks, handlers, compose = _read(TASKS), _read(HANDLERS), _read(COMPOSE)
    broken = {}
    for src, row in RELOAD_CONTRACT.items():
        service, want_mode = row["service"], row["mode"]
        task = _render_task_block(tasks, src)
        module = re.search(r'(?m)^([^\S\n]*)ansible\.builtin\.template:[^\S\n]*$', task)
        notify = re.search(
            r'(?m)^' + " " * len(module.group(1)) + r'notify:[^\S\n]*(\S.*?)[^\S\n]*$', task
        ) if module else None
        name = _yaml_unquote(notify.group(1)) if notify else None
        handler = _handler_block(handlers, name) if name else ""
        restarts = re.search(
            rf'(?m)^\s*cmd:\s*docker compose restart {re.escape(service)}\s*$', handler
        ) is not None and re.search(
            r'(?m)^\s*chdir:\s*"?\{\{\s*docker_host_project_dir\s*\}\}"?\s*$', handler
        ) is not None
        service_block = _compose_service_block(compose, service)
        in_compose = bool(service_block.strip())
        dest = re.search(r'(?m)^\s*dest:\s*(\S.*?)\s*$', task)
        target = _bind_mount_target(service_block, dest.group(1)) if dest else None
        flag = row["config_flag"]
        want_dir = row.get("default_dir")
        named_in = row.get("named_in")
        if flag:
            reads_it = target is not None and target == _last_flag_value(
                _service_command_args(service_block), flag
            )
        elif named_in:
            # Step-7a, the THIRD carrier: no flag names this file and the image
            # fixes no path for it — ANOTHER template this role renders does, via
            # `rule_files:`. Membership and not equality, because that key is a
            # LIST: Prometheus loads every entry, so what must hold is that this
            # render's mount target is one of the files the config asks for.
            # `_rule_files_entries` is the same reader
            # `test_prometheus_rule_files_names_the_render` quantifies over.
            reads_it = target is not None and target in _rule_files_entries(
                _read(named_in)
            )
        elif want_dir:
            # The image SCANS a directory (grafana provisioning): the file's name
            # is ours, its directory is the image's. `rsplit` and not
            # `startswith`, so a file one level DEEPER — which grafana does not
            # read — is not accepted by a prefix that happens to match.
            reads_it = target is not None and target.rsplit("/", 1)[0] == want_dir
        else:
            reads_it = target is not None and target == row["default_path"]
        mode = _render_task_scalar(task, "mode")
        mode_ok = mode is not None and mode.strip('"\'') == want_mode
        want_owner, want_group = row["owner"]
        owner = _render_task_scalar(task, "owner")
        group = _render_task_scalar(task, "group")
        owner_ok = (owner is not None and owner.strip('"\'') == want_owner
                    and group is not None and group.strip('"\'') == want_group)
        if not (task and name and handler and restarts and in_compose
                and target and reads_it and mode_ok and owner_ok):
            broken[src] = (
                f"task={bool(task)} notify={name!r} handler={bool(handler)} "
                f"restarts_{service}={restarts} in_compose={in_compose} "
                f"dest={_norm_path(dest.group(1)) if dest else None} "
                f"mounted_at={target!r} reads_it={reads_it} "
                f"(via {flag or (named_in.name + ' ' + PROM_RULES_KEY + ':' if named_in else 'default ' + str(want_dir or row['default_path']))}) "
                f"mode={mode} (want {want_mode}) "
                f"owner={owner}:{group} (want {want_owner}:{want_group})"
            )
    ok = not broken
    print(
        f"{'OK' if ok else 'FAIL'}: rendered configs reach the service that reads them "
        f"({len(RELOAD_CONTRACT) - len(broken)}/{len(RELOAD_CONTRACT)} paths whole, "
        f"broken={broken})"
    )
    return ok


def test_plex_blip_rules_render_is_validated_against_the_pinned_image() -> bool:
    """Step-7c: the rules render cannot reach the running process unvalidated.

    A malformed rules file does not degrade Prometheus — it STOPS it. Measured on
    the pinned `prom/prometheus:v3.12.0` at the wave cut (`logs/planner-step07-live.log`,
    leg 'bad'): one unparseable `expr` and the container is `exited`, logging
    `could not parse expression`, and under this repo's `restart: unless-stopped`
    that is the crash-loop class already recorded at :2072 (`RestartCount 20801`,
    TSDB empty for two weeks). It is the FIRST of this role's renders whose bad
    output takes the process down rather than being ignored, so `grep -c validate:`
    on `tasks/main.yml` was ZERO before this row.

    `ansible.builtin.template`'s OWN `validate:` is the gate, not a check-afterwards
    task: a `validate:` that fails leaves the DEST UNCHANGED, so the good file
    stays and the `notify: Restart prometheus` handler never fires — a separate
    task would have already overwritten the good file before checking it. Driven
    as a real delivery against a live container in `logs/builder-7c-delivery.log`
    (good render → new container id on the new rules; bad render → play FAILED, dest
    byte-identical, SAME container id still serving the old rules — the fresh-`up -d`
    leg cannot test that, mem-1786224903-8344).

    Five pins, one relation:

    * present — the RULES render carries a `validate:`.
    * validates the RENDER — the command carries `%s`, the temp file ansible
      writes and is about to copy, not a fixed path. Validating any other path
      passes while the new bytes go unread.
    * `check rules` — the validator actually PARSES rules, so an unparseable
      `expr` is rc!=0. A vacuous `validate: /bin/true %s` is the hole this pin
      closes; `test_plex_blip_rules_validate_gate.py` drives the shipped command
      RED on a bad render and GREEN on a good one.
    * promtool from the PINNED image — `{{ docker_host_prometheus_image }}`, the
      SAME variable `compose.yml.j2`'s prometheus service runs, read back out of
      that service block rather than re-spelled. A host `promtool` or a second
      literal tag is the c6c4/e627 two-literals-that-agree class: the validator
      would drift from the process it guards.
    * no literal tag — `prom/prometheus` appears NOWHERE in the command as a
      string, only as the variable, so the relation above is the only carrier.
    """
    tasks, compose = _read(TASKS), _read(COMPOSE)
    task = _render_task_block(tasks, PROM_RULES.name)
    cmd = _render_task_validate(task)
    service_block = _compose_service_block(compose, PROMETHEUS_SERVICE)
    image = re.search(r'(?m)^\s*image:\s*(\S.*?)\s*$', service_block)
    image_val = image.group(1) if image else ""
    var = re.compile(r'\{\{\s*docker_host_prometheus_image\s*\}\}')

    present = bool(cmd)
    validates_render = present and "%s" in cmd
    checks_rules = present and "check rules" in cmd
    runs_promtool = present and "promtool" in cmd
    pinned_var = present and var.search(cmd) is not None
    # the compose service really runs that same variable — the pin is a relation,
    # not a lone literal that happens to name the right image.
    compose_runs_var = var.search(image_val) is not None
    no_literal_tag = present and "prom/prometheus" not in cmd

    ok = (present and validates_render and checks_rules and runs_promtool
          and pinned_var and compose_runs_var and no_literal_tag)
    print(
        f"{'OK' if ok else 'FAIL'}: plex-blip rules render is validated against the "
        f"pinned image (present={present} validates_render={validates_render} "
        f"check_rules={checks_rules} promtool={runs_promtool} "
        f"pinned_image_var={pinned_var} compose_runs_var={compose_runs_var} "
        f"no_literal_tag={no_literal_tag}; cmd={cmd!r})"
    )
    return ok


def test_relabel_allow_list_prices_every_field_it_excludes() -> bool:
    """Step-5c r3: `_RELABEL_HOP_FIELDS`' excluded set is ENUMERATED and PRICED.

    This clause reads no file. It holds one relation between three constants,
    and it exists because the sentence that used to carry that relation was
    prose and was false (DEC-318): the allow-list excluded five fields with the
    justification that each "changes what the hop writes or whether it writes at
    all", when every one of them has a default whose explicit spelling is a
    byte-identical no-op the guard reds anyway. A justification a reader quotes
    to price the cost has to be a thing the suite can red on, so:

    * `unknown` — every field the allow-list ALLOWS is a real relabel field.
      A typo (`target_labels`) would silently forbid the field it meant to
      permit, and `_relabel_triplet`'s defect text would name a field Prometheus
      has never heard of.
    * `unpriced` — every field the allow-list EXCLUDES has a no-op spelling
      recorded. This is the arm that made the r2 charge's own door short by one:
      the charge named five fields and the excluded set is SIX, because
      `source_labels` is excluded on `dial` and nowhere else.
    * `unused` — and nothing is priced that is not excluded, so widening the
      allow-list (the declared door out, DEC-317) cannot leave a stale price
      behind it.
    * `mis_spelled` — each priced spelling is a spelling OF ITS OWN FIELD. The
      table is two columns and nothing else relates them, so a row edited by
      hand can name one field and demonstrate another.

    WHAT IT DOES NOT DO, said plainly because the defect it repairs was an
    over-claiming sentence: it does not drive any of these spellings, and it
    cannot tell a TRUE default from a plausible one. That the wire cannot
    distinguish them from the delivered tree is a MEASUREMENT, and it lives at
    logs/builder-5c-r3-price.log — 15 documents, each one `promtool` rc=0 with
    the CONTROL's own `up`, `probe_success`, `instance` and series count, each
    one RED in this suite. Re-spelling `separator: ";"` as `separator: ';'` is
    GREEN here and that is correct rather than a hole: what this clause holds is
    that the priced set and the excluded set are the same set and that each row
    demonstrates the field it names, so neither can drift without a red.

    The COUNT is printed from the constants rather than typed into a docstring,
    for the reason this row keeps rediscovering: a number in prose is a
    measurement sentence with nothing arming it.
    """
    unknown = {
        hop: sorted(set(allowed) - set(_PROM_RELABEL_FIELDS))
        for hop, allowed in _RELABEL_HOP_FIELDS.items()
    }
    unknown = {hop: bad for hop, bad in unknown.items() if bad}
    excluded = {
        hop: tuple(f for f in _PROM_RELABEL_FIELDS if f not in allowed)
        for hop, allowed in _RELABEL_HOP_FIELDS.items()
    }
    union = sorted({f for fields in excluded.values() for f in fields})
    unpriced = [f for f in union if f not in _RELABEL_NOOP_SPELLING]
    unused = [f for f in _RELABEL_NOOP_SPELLING if f not in union]
    mis_spelled = {
        f: s for f, s in _RELABEL_NOOP_SPELLING.items()
        if not s.startswith(f"{f}:")
    }
    priced = [(hop, f) for hop, fields in excluded.items() for f in fields]
    ok = not unknown and not unpriced and not unused and not mis_spelled
    print(
        f"{'OK' if ok else 'FAIL'}: the relabel-hop allow-list prices every "
        f"field it excludes ({len(priced)} no-op documents over {len(union)} "
        f"fields and {len(_RELABEL_HOP_FIELDS)} hops — the standing cost, "
        f"measured at logs/builder-5c-r3-price.log; excluded="
        f"{ {hop: list(f) for hop, f in excluded.items()} }, unpriced={unpriced}, "
        f"unused={unused}, unknown={unknown}, mis_spelled={mis_spelled})"
    )
    return ok


def test_pve_scrape_job_is_multi_target() -> bool:
    """Step-2a: the pve-exporter scrape job uses the MULTI-TARGET shape.

    THE check of this step — the one that reddens on the no-op described above,
    and the reason the others exist at all. Five pins, each failing differently.
    Two of them carry the runtime contract and three do not, and saying which is
    which is part of the check (a docstring that oversells a clause is what let
    the Step-1 bucket no-op survive two rounds):

    * `path_pinned` — LOAD-BEARING. The job sets `metrics_path: /pve`. Absent,
      Prometheus scrapes `/metrics`, which answers 200 with the exporter's own
      five `pve_*` self-metrics and nothing about PVE. Verified against the
      running 3.9.0 image, not read off a README.
    * `address_rewritten` — LOAD-BEARING. `relabel_configs` carries
      `__param_target` from `__address__` and then replaces `__address__` with
      the exporter. Without the rewrite Prometheus dials the PVE host directly on
      the wrong port/path; and `target` defaults to `localhost` in the exporter,
      so a missing `__param_target` makes it interrogate its own container rather
      than fail loudly.

      THREE HOPS SINCE ROW 5c, NOT TWO, and the third is the reason that row
      extracted `_relabel_triplet` rather than copying this one. The
      `__param_target -> instance` entry has been in this template since Step 2
      with a comment explaining it and NOTHING pinning it: deleting it left this
      clause printing `address_rewritten=True` over a scrape that still works and
      attributes every `pve_*` series to the exporter container instead of to the
      PVE host. Which hop is missing is now named in the defect list rather than
      inferred from three booleans.

      Every half is asked of ONE list ENTRY, and the "and then" is a comparison
      of the entries' indices — Step-2a F1, round 10. Until then each half was
      a `(?ms) … .*? …` span over the whole block, and `.*?` does not care which
      entry the halves came from, so three deployable rows printed
      `address_rewritten=True (param_target=True, replacement=True)` —
      BYTE-IDENTICAL to this field on the honest tree — at guard PASS 36/36 with
      `promtool check config` rc=0, and the REAL Prometheus on the rendered
      artifact built (logs/red-step02a-rework-f1-round10.log, A1-A3):

        - order swap, the rules applying in the order written:
          `?target=pve-exporter%3A9221` — the exporter asked about ITSELF;
        - cross-entry replacement, `pve-exporter:9221` demoted one entry down to a
          provenance label: `http://192.168.1.50:8006/pve?…` — the request dialed
          at the PVE API instead of the exporter;
        - cross-entry source via the one-character typo `__adress__`, with the
          `instance` entry above answering the regex: `/pve?cluster=1&node=1` with
          no `target=` at all, which is verbatim the state this docstring names.

      These fail LOUD at deploy — the real 3.9.0 exporter answers HTTP 500 with
      zero `pve_*` series for both wrong targets, so the target reads DOWN rather
      than UP-with-zero-series. They are pinned anyway because the operator's Step-2b
      run is ONE irreproducible pass and this clause is the one that decides whether
      it can produce its falsifier.

      WHICH WRITE WINS IS NOW CHECKED, and this paragraph used to say it was
      not. It named a third entry overwriting `__param_target` as green here
      (logs/review-step02a-rework-f1-round10e.log) and priced it "it also fails
      loudly" — a price DEC-316 measured false one caller over, where the same
      shape is `promtool` rc=0 with the alert firing at a healthy host. Since
      that round `_relabel_triplet` pins the LIST rather than three memberships:
      an entry outside the triplet is a defect, and so is a field beside the
      copy inside one. It did not need a model of relabel ACTIONS after all —
      it needed the entries the model does not cover to be named rather than
      allowed (logs/builder-5c-r2-arms.log M14/M15 drive both on THIS job).
    * `path_is_not_default` — the pinned constant DIFFERS from
      `PVE_EXPORTER_DEFAULT_PATH`. Without this clause a later edit satisfies the
      check by writing out the default explicitly, which is the same no-op with
      one more line of YAML (cf. `is_custom` on the buckets above).
    * `params_ok` — `cluster=1` and `node=1`, and STRICTER THAN THE RUNTIME
      CONTRACT: both already default to `'1'` in the shipped image's
      `on_pve(...)` signature, so a config without them is byte-identical in
      effect (measured by A/B against a stub PVE API — see PVE_REQUIRED_PARAMS).
      This clause pins explicitness, NOT the existence of the per-guest series.
      An earlier version of this docstring claimed `cluster=1` was "the check
      that reddens on the no-op"; that was false, and the false claim had also
      reached the template comment, the runtime task and plan.md.
    * `target_is_pve_host` — the scrape TARGET is the PVE API host, not the
      exporter. In a multi-target exporter the target is the thing being asked
      about; pointing it at `pve-exporter` makes the exporter interrogate itself.
    """
    body = _read(PROM_SCRAPE)
    block = _scrape_job_block(body, "pve-exporter")
    present = bool(block.strip())
    path = _block_scalar(block, "metrics_path")
    path_pinned = path == PVE_MULTI_TARGET_PATH
    path_is_not_default = PVE_MULTI_TARGET_PATH != PVE_EXPORTER_DEFAULT_PATH
    params = _indented_block(block, "params")
    missing_params = {
        k: _param_values(params, k)
        for k, v in PVE_REQUIRED_PARAMS.items()
        if v not in _param_values(params, k)
    }
    params_ok = not missing_params
    # The target is the PVE host — literal, or the role-defaults var holding it.
    # The read is PLURAL and the round-9 rows behind that live at
    # `_static_targets`, which row 5c extracted from this call site and two
    # others; the claim below quantifies over ALL of them (`all(...)`), which is
    # what that helper exists to make possible.
    targets = _static_targets(block)
    target_is_pve_host = bool(targets) and all(
        PVE_API_HOST in t or "docker_host_pve_api_host" in t for t in targets
    )
    # `_relabel_triplet` — row 5c's extraction of the read this clause won, now
    # shared with the three blackbox jobs. It is STRICTER here than the inline
    # version was, by exactly one hop: the `instance` entry this template has
    # carried since Step 2 was described in its own comment and pinned by
    # nothing, so `__param_target -> instance` could be deleted with this clause
    # still printing `address_rewritten=True`. That is the silent hop — the
    # scrape still works and every `pve_*` series is attributed to the exporter
    # container instead of to the PVE host.
    triplet_defects, hops = _relabel_triplet(block, PVE_EXPORTER_ADDRESS)
    address_rewritten = not triplet_defects
    ok = (
        present and path_pinned and path_is_not_default and params_ok
        and target_is_pve_host and address_rewritten
    )
    print(
        f"{'OK' if ok else 'FAIL'}: pve-exporter scrape job is multi-target "
        f"(present={present}, metrics_path={path!r}, path_pinned={path_pinned}, "
        f"path_is_not_default={path_is_not_default}, params_ok={params_ok} "
        f"(missing={missing_params}), target_is_pve_host={target_is_pve_host} "
        f"(targets={targets}), address_rewritten={address_rewritten} "
        f"(hops={hops}, defects={triplet_defects}))"
    )
    return ok


def test_pve_exporter_service_block() -> bool:
    """Step-2a: compose defines `pve-exporter` as a scrape-only service.

    Modeled on node-exporter/cadvisor: reachable only by Prometheus over the
    internal compose network, never routed and never published.

    * `image_var` — pulled via `{{ docker_host_pve_exporter_image }}`, so version
      bumps stay one default (the concrete-pin shape itself is enforced for every
      `docker_host_*_image` by `test_no_floating_service_image_tags`).
    * `keys_allowed` — THE reachability pin, and the one that does not depend on
      anybody having enumerated the right forbidden key. Two halves, and the
      field prints both: the service may declare only `SCRAPE_ONLY_KEYS`
      (`unexpected`), AND every line at its key column must be a key this guard
      can actually READ (`unreadable`). The second half is round 6's, and
      without it the first is only as complete as `_yaml_key` — a merge key, an
      explicit-key pair or a Jinja-emitted key was dropped on the floor and left
      the allow-list green while `network_mode: host` landed on the resolved
      service (`_line_class`, and logs/calibration-step02a-f1-round6.log). See
      `SCRAPE_ONLY_KEYS` for the runtime measurement and for which members are
      stricter than the runtime.
    * `no_traefik_labels` / `no_ports` — the two doors that have been measured
      end to end, kept as pins of their own so a RED says WHICH one opened.
      They fail differently from `keys_allowed` and from each other: a Traefik
      label puts an unauthenticated read of the whole PVE API behind a router,
      while a published port puts it on the LAN with no router at all — measured
      on the real image with 9221 published, `/pve` and `/metrics` answer an
      unauthenticated caller and `target` is caller-controlled. `no_ports` reads
      EVERY YAML spelling via `_service_published_ports` (block, flow, long form,
      and the quoted key), and pins the KEY rather than a non-empty list: an
      empty `ports: []` publishes nothing and still reddens, which is stricter
      than the runtime and deliberate, because such a key has no reason to exist
      in a scrape-only service and is one edit away from one that publishes.
      Both are cheap to regress into by copying a neighbouring service block —
      and that is not hypothetical for the network keys: node-exporter, the
      model this service is written from, carries `pid: host` one service up.
    * `defaults_vars` — the two identity env vars are present AND take their
      value from the role-defaults variable named in `PVE_DEFAULT_VARS`, not from
      a literal. `PVE_USER` is what activates env-var configuration at all:
      without it the exporter ignores `PVE_TOKEN_NAME`/`PVE_TOKEN_VALUE` and
      falls back to an on-disk `/etc/prometheus/pve.yml` that this image does not
      ship, so `cli.py:110` opens it unguarded and the process dies at STARTUP
      with `FileNotFoundError`, which `restart: unless-stopped` turns into a
      crash loop. Measured on the real image, everything else intact:
      `State.Status=restarting`, RestartCount 8, curl exit 7 connection refused
      (logs/calibration-step02a-f3.log, A). It does NOT stay up and serve 401s —
      there is no listener and no scrape at all. `PVE_TOKEN_NAME` is what makes
      the token resolve at all — deleting it gets HTTP 500 "No valid
      authentication credentials were
      supplied" and zero PVE API calls from the real image. Before this clause
      existed, deleting the `PVE_TOKEN_NAME` line left the whole gate GREEN: the
      guard pinned an optimisation flag and a pair of runtime no-op params and
      left AUTHENTICATION unguarded. Deriving from the defaults var rather than
      matching `PVE_USER=\\S+` also closes the realm hole — a `prometheus` with
      the `@pve` stripped in COMPOSE was green while the defaults-side realm
      check saw nothing.
    * `verify_ssl_off` — the PVE cert is self-signed (`PROXMOX_VE_INSECURE=true`,
      mise.toml). Left at the default `true`, every scrape errors on the TLS
      handshake and the target is DOWN.
    * `no_collector_config` — `--no-collector.config` drops one PVE API call per
      guest. Stricter than the runtime contract (the exporter works without it),
      and pinned deliberately: it is a deploy-time cost that is invisible from
      the repo and easy to lose in an edit.

    Every clause reads the COMMENT-STRIPPED block (`_strip_comments`) and anchors
    on a real YAML entry, because the comments here name the very flags and env
    vars being pinned.
    """
    block = _strip_comments(_compose_service_block(_read(COMPOSE), "pve-exporter"))
    present = bool(block.strip())
    image_var = re.search(
        r'(?m)^\s*image:\s*\{\{\s*docker_host_pve_exporter_image\s*\}\}', block
    ) is not None
    no_traefik_labels = re.search(r'traefik\.', block) is None
    keys, unreadable_keys = _service_key_lines(block)
    extra_keys = sorted(set(keys) - SCRAPE_ONLY_KEYS)
    keys_allowed = not extra_keys and not unreadable_keys
    published = _service_published_ports(block)
    no_ports = published is None
    restart = re.search(r'(?m)^\s*restart:\s*unless-stopped\s*$', block) is not None
    # Round 14 (F1): the three env pins below read the EFFECTIVE value docker
    # resolves for each named key (`_service_env_map`, last wins) instead of
    # scanning the block for a matching entry. `environment:` is a SEQUENCE of
    # `KEY=VALUE` strings, so a second assignment is no parser's duplicate key —
    # all three were PASS 36/36 with the wrong effective value on a tree
    # `just play` ships (rows O1/O2/O4), and the empty spelling is quieter than
    # the deletion each docstring was written against: the container stays
    # RUNNING and authenticates with a credential PVE rejects.
    env_map = _service_env_map(_read(COMPOSE), "pve-exporter")
    unwired_vars = [
        env for env, var in PVE_DEFAULT_VARS.items()
        if re.fullmatch(rf'\{{\{{\s*{var}\s*\}}\}}', env_map.get(env, "")) is None
    ]
    defaults_vars = not unwired_vars
    # This `.lower()` STAYS, unlike the two deleted from `env_pinned` in
    # `test_plex_exporter_service_block`: THIS runtime case-folds too, so the
    # fold mirrors the process rather than narrowing the pin. Measured in the
    # pinned image, `pve_exporter/config.py:54`:
    # `confvals['verify_ssl'] = env['PVE_VERIFY_SSL'].lower() not in ['false', '0']`.
    # `False` and `false` are one value to this exporter; `True`/`true` are two
    # to the plex one. The rule is the runtime's own sensitivity, not a habit.
    verify_ssl_off = env_map.get("PVE_VERIFY_SSL", "").lower() == "false"
    # `--collector.config` and `--no-collector.config` are ONE argparse
    # BooleanOptionalAction on this image, so the LAST of the pair wins and a pin
    # on the presence of the negative form was green with the collector back ON
    # (row X1). Same class as the env keys, one notch weaker — hence the same
    # last-wins read, of the pair rather than of the whole arg list.
    config_flags = [
        a for a in _service_command_args(block)
        if a in ("--collector.config", "--no-collector.config")
    ]
    no_collector_config = bool(config_flags) and config_flags[-1] == "--no-collector.config"
    ok = (
        present and image_var and no_traefik_labels and keys_allowed and no_ports
        and restart and defaults_vars and verify_ssl_off and no_collector_config
    )
    print(
        f"{'OK' if ok else 'FAIL'}: pve-exporter compose service is scrape-only "
        f"(present={present}, image_var={image_var}, "
        f"no_traefik_labels={no_traefik_labels}, "
        f"keys_allowed={keys_allowed} (keys={keys}, unexpected={extra_keys}, "
        f"unreadable={unreadable_keys}), "
        f"no_ports={no_ports} (published={published!r}), "
        f"restart={restart}, defaults_vars={defaults_vars} "
        f"(unwired={unwired_vars}), "
        f"verify_ssl_off={verify_ssl_off}, no_collector_config={no_collector_config})"
    )
    return ok


def _vault_token_hops(env_key: str, vault_key: str, service: str) -> dict:
    """The vault -> `.env` -> `${VAR:-}` chain for ONE secret env var, as clauses.

    Step-3a. Two secrets now travel the identical three hops (`PVE_TOKEN_VALUE`
    since Step 2a, `PLEX_TOKEN` from this step) and a third has since Step 4
    (`TUNNEL_TOKEN`, pinned one test over). The mechanics are the same four
    reads, so they are written ONCE: a second copy is a second thing to fix when
    a hop is found to be readable the wrong way, and this file's whole Step-2a
    history is rounds 13-15 fixing the same defect in region after region
    because each region had its own reader. Both callers keep their own
    docstrings, because what the hops are FOR differs; what they ARE does not.

    Every read is the effective-value read, not a presence scan — see
    `_env_assignments` (a `.env` is line-based, so compose takes the LAST
    assignment) and `_service_env_map` (`environment:` is a string SEQUENCE
    docker resolves last-wins). Both were measured PASS 36/36 with the wrong
    effective value before rounds 13/14 fixed them.

    `leaks` scans the whole role rather than the two templates, because the pin
    is "this secret is nowhere in plaintext", and a line holding a Jinja
    expression or a `${...}` dereference is the indirection itself rather than a
    literal. The match is CASE-INSENSITIVE (Step-3a, row T6): the env var is
    SHOUTED but the Ansible spelling of the same thing is not, so a
    `docker_host_plex_token: <value>` landing in plaintext role defaults — which
    is exactly the shape `test_pve_non_secret_coordinates_in_defaults` forbids
    one file over — walked straight past a case-sensitive scan.
    """
    env_value = _env_assignments(_read(ENV)).get(env_key, "")
    return {
        "env_from_vault": re.search(rf'\{{\{{\s*{vault_key}\b', env_value) is not None,
        "env_defaults_empty": re.search(
            rf"\{{\{{\s*{vault_key}\s*\|\s*default\(''\)\s*\}}\}}", env_value
        ) is not None,
        "compose_indirection": re.fullmatch(
            rf'\$\{{{env_key}:?-?\}}',
            _service_env_map(_read(COMPOSE), service).get(env_key, ""),
        ) is not None,
        "leaks": [
            f"{path.name}: {ln.strip()[:60]}"
            for path in sorted(ROLE.rglob("*"))
            if path.is_file()
            for ln in _read(path).splitlines()
            if re.search(rf'(?i){env_key}\s*[:=]\s*[A-Za-z0-9_\-]{{20,}}', ln)
            and not re.search(r'\{\{.*\}\}|\$\{', ln)
        ],
    }


def test_pve_token_sourced_from_vault() -> bool:
    """Step-2a: the PVE token reaches the container from the vault, never a literal.

    Same three-hop shape as CF_DNS_API_TOKEN: vault key -> `.env` (env.j2) ->
    `${VAR:-}` in compose. Four pins:

    * `env_from_vault` — env.j2 assigns `PVE_TOKEN_VALUE` from
      `vault_pve_api_token`.
    * `env_defaults_empty` — with `| default('')`. This is the clause that makes
      Step 2a landable and green BEFORE the operator mints anything in 2b:
      without the filter an undefined vault key fails the render, and the whole
      secret/reference split this task is built on stops working.
    * `compose_indirection` — compose dereferences the SAME name from the sibling
      `.env` (`${PVE_TOKEN_VALUE:-}`), never an inline value. Both sides are
      derived from `PVE_TOKEN_ENV`, so renaming one alone reddens — the
      agreement, not two hard-coded copies of a string.
    * `no_literal` — no `PVE_TOKEN_VALUE=<20+ token chars>` anywhere in the role
      (`test_no_plaintext_secrets` covers only the Cloudflare/tunnel keys).
    """
    # Decommented (round 12, leg D): env.j2's own idiom is a comment ABOVE each
    # assignment naming the very key it documents, so both pins below were one
    # commented-out example away from being satisfied by a file that assigns nothing.
    # Measured: the `PVE_TOKEN_VALUE=` line deleted with that comment left behind was
    # GREEN, and the rendered `.env` then carries no PVE token at all (row D2).
    # Round 13 (F2, one file over): both pins now read the EFFECTIVE value compose
    # resolves for that name — `_env_assignments`, last wins — because a `.env` is
    # line-based, so a duplicate assignment is no parser's duplicate key. The
    # vault-sourced line followed by `PVE_TOKEN_VALUE=` was PASS 36/36 while
    # `docker compose config` resolved the variable EMPTY, i.e. the exporter
    # reaches PVE with no credential (row D5).
    # Round 14 (F1): the compose side reads the EFFECTIVE value too. A second
    # `PVE_TOKEN_VALUE=` appended after the indirection was PASS 36/36 while
    # `docker compose config` resolved the variable EMPTY — the same defect round
    # 13 fixed in the `.env` one file over, in the region its bound omitted, and
    # on the one key this whole task exists to deliver (row O3).
    # Step-3a: the four reads moved to `_vault_token_hops`, shared with the Plex
    # token, which travels the identical three hops.
    hops = _vault_token_hops(PVE_TOKEN_ENV, PVE_VAULT_KEY, "pve-exporter")
    env_from_vault = hops["env_from_vault"]
    env_defaults_empty = hops["env_defaults_empty"]
    compose_indirection = hops["compose_indirection"]
    leaks = hops["leaks"]
    ok = env_from_vault and env_defaults_empty and compose_indirection and not leaks
    print(
        f"{'OK' if ok else 'FAIL'}: {PVE_TOKEN_ENV} sourced from {PVE_VAULT_KEY} "
        f"via .env (env_from_vault={env_from_vault}, "
        f"env_defaults_empty={env_defaults_empty}, "
        f"compose_indirection={compose_indirection}, "
        f"no_literal={not leaks} (leaks={leaks}))"
    )
    return ok


def test_pve_non_secret_coordinates_in_defaults() -> bool:
    """Step-2a: the non-secret PVE coordinates live in role defaults, not the vault.

    Only the token VALUE is a secret. The API host, the user and the token NAME
    are not, and putting them in the vault is what makes a step look more gated
    than it is (it is what parked this objective for an iteration).

    * `host_agrees` — the defaults' API host equals the endpoint already
      committed in `mise.toml` (`PROXMOX_VE_ENDPOINT`). Derived from the existing
      spelling rather than pinned twice, so a real PVE move touches both and stays
      green while a drift in one reddens.
    * `user_realm` — `PVE_USER` names a realm (`prometheus@pve`). Measured, in
      the same pass that deleted the other status-code claim from this file: PVE
      answers a realm-less token `401 Unauthorized`, but the exporter raises
      `proxmoxer.core.ResourceException` and serves the scrape HTTP 500, so
      Prometheus records the SAME `lastError` as a missing token and the realm is
      visible only in the exporter's own `docker logs`
      (logs/calibration-step02a-f3.log, C). That is exactly why it is pinned
      here: it is the failure the operator cannot diagnose from the metric side.
      Both this check and the compose
      one read the SAME `PVE_DEFAULT_VARS` map, so the realm is pinned on the
      side that holds the value and compose is pinned to consume it — neither
      half can be satisfied alone.
    * `token_name` — the token NAME default exists; 2b's minted token ID must
      match it.
    * `no_secret_in_defaults` — no token VALUE and no `vault_*` assignment leaked
      into the (plaintext, committed) defaults file.
    """
    defaults = _read(ROLE / "defaults" / "main.yml")
    host = re.search(r'(?m)^\s*docker_host_pve_api_host:\s*"?([^"\s#]+)', defaults)
    # Decommented (round 12, leg D, row D7): the agreement is the point of this pin,
    # and `mise.toml` commenting an old endpoint out is the ordinary way an endpoint
    # moves — the raw read let that comment answer for a live assignment somewhere else.
    mise_endpoint = re.search(
        r'PROXMOX_VE_ENDPOINT\s*=\s*"([^"]+)"', _strip_comments(_read(MISE))
    )
    host_agrees = bool(host) and bool(mise_endpoint) and host.group(1) in mise_endpoint.group(1)
    user = re.search(
        rf'(?m)^\s*{PVE_DEFAULT_VARS["PVE_USER"]}:\s*"?([^"\s#]+)', defaults
    )
    user_realm = bool(user) and re.fullmatch(r'[^@\s]+@[^@\s]+', user.group(1)) is not None
    token_name = re.search(
        rf'(?m)^\s*{PVE_DEFAULT_VARS["PVE_TOKEN_NAME"]}:\s*"?([^"\s#]+)', defaults
    )
    # Any spelling of the key, not the bare one: this is the pin that says a
    # vaulted secret has not been copied into plaintext role defaults, and a
    # quoted `"vault_pve_api_token":` parses to the same key while a
    # `^\s*vault_\w+\s*:` regex reads straight past it (`_declares_key`).
    leaked_secret = _declares_key(defaults, r'(?i)vault_\w+|docker_host_pve_token_value')
    no_secret_in_defaults = not leaked_secret
    ok = host_agrees and user_realm and bool(token_name) and no_secret_in_defaults
    print(
        f"{'OK' if ok else 'FAIL'}: non-secret PVE coordinates in role defaults "
        f"(host={host.group(1) if host else None!r} agrees with mise "
        f"PROXMOX_VE_ENDPOINT={host_agrees}, user={user.group(1) if user else None!r} "
        f"realm={user_realm}, token_name={token_name.group(1) if token_name else None!r}, "
        f"no_secret_in_defaults={no_secret_in_defaults} (found={leaked_secret}))"
    )
    return ok


def test_plex_scrape_job_is_single_target() -> bool:
    """Step-3a: the plex-exporter scrape job is an ORDINARY single-target job.

    THE check of this step, and it is the mirror image of
    `test_pve_scrape_job_is_multi_target` one screen up. That job's load-bearing
    pin is the PRESENCE of `metrics_path: /pve`; this job's is the ABSENCE of a
    `metrics_path` at all, because `axsuul/plex-media-server-exporter` serves its
    metrics on the plain default path (`config.ru` mounts
    `Prometheus::Middleware::Exporter`, and the collector runs only when
    `PATH_INFO == "/metrics"` exactly). The two jobs sit ten lines apart in one
    template and every key that is mandatory in one is wrong in the other, so
    "somebody copies the neighbour" is the failure mode this check is for.

    * `present` — the job resolves exactly ONCE inside `scrape_configs:`
      (`_scrape_job_block`). Stated first because every other clause here is an
      ABSENCE, and an absence pin over an empty block is the definition of
      vacuous: without this, deleting the whole job is GREEN.
    * `target_is_exporter` — LOAD-BEARING. Every entry of every `targets:` list
      in the job is exactly `plex-exporter:9594`, the compose service name on the
      internal network. `all(...)` over `_indented_blocks`, plural, for the reason
      round 9 established one job over: `static_configs` is a LIST and Prometheus
      scrapes every entry of it, so reading the first `- targets:` leaves a
      second, unrelated target invisible. Unlike the PVE job the target here IS
      the exporter — there is nothing to interrogate on its behalf.
    * `no_multi_target_shape` — LOAD-BEARING, and the copy-paste pin. The job's
      OWN key column may hold only `PLEX_JOB_KEYS`, which is what keeps
      `metrics_path`, `params` and `relabel_configs` out: a `metrics_path: /pve`
      here is a 404 and the target reads DOWN, `params` are ignored, and a
      `__param_target` relabel has nothing to rewrite. That state is DEPLOYABLE,
      not a syntax error somebody would catch — with `/pve` copied onto this job
      `promtool check config` is rc=0 and the real prom/prometheus:v3.12.0 builds
      the target at `scrapeUrl=http://plex-exporter:9594/pve` (R6, same log).

      AN ALLOW-LIST AND NOT THOSE THREE NAMES (round 7). This clause used to be
      `_declares_key` over an enumeration, which is an absence pin, and an absence
      pin fails open exactly one key past its edge: `file_sd_configs:` — a second
      set of targets read off disk — and `scheme: https` against an exporter that
      speaks plain HTTP were both PASS 39/39 at promtool rc=0
      (logs/red-step03a-jinja-key-pre.log, rows G1/G2). It is the same correction
      `_service_key_lines` exists for on the compose side, and it is that helper
      doing the work here, so the two properties come with it: the column is
      derived from the block rather than pinned, and every line at that column the
      parser cannot read lands in `unreadable_keys` and reddens this too — a
      Jinja-emitted `{{ 'metrics_path: /pve' }}` included (row G4).
    * `pair_present` / `timeout_fits` — the job sets BOTH `scrape_interval` and
      `scrape_timeout`, and the timeout does not exceed the interval. Not a style
      rule: Prometheus REFUSES to load a config whose `scrape_timeout` is greater
      than its `scrape_interval`, so the pair moves together or nothing scrapes
      at all — `promtool check config` on the pinned prom/prometheus:v3.12.0
      answers `FAILED: … scrape timeout greater than scrape interval for scrape
      config with job name "plex-exporter"`, rc=1, for the over-long timeout AND
      for a job-local `scrape_timeout: 30s` written WITHOUT its interval, which
      inherits the 15 s global one (logs/calibration-step03a-scrape-budget.log,
      R2/R3).

      THE PLAN SAID THAT REFUSAL IS CAUGHT BY `promtool check config` INSIDE
      `just test`. IT IS NOT, and the correction is why this clause is a pin
      rather than a comment: `just test` runs 35 steps — 30 shape scripts, tofu
      fmt/init/validate, ansible-lint, `ansible-playbook --syntax-check` — and
      not one of them is promtool or renders this template at all. Nothing in
      this repo's gate loads a Prometheus config. So the guard is the only thing
      standing between an unloadable scrape config and the operator's `just
      play`, and the half-pair Prometheus DOES accept is the one it has to catch
      on its own: `scrape_interval: 60s` with no timeout is rc=0 and loads with
      the 10 s default still in force (R4) — a job whose sweep scrape cannot
      finish, from a config nothing complains about.
    * `budget_raised` — the pinned pair is BIGGER than what was already in force,
      i.e. `scrape_interval` exceeds the file's own `global.scrape_interval` and
      `scrape_timeout` exceeds Prometheus' 10 s default. This is the
      `is_custom` clause of the buckets check, transplanted: without it the whole
      pair is satisfiable by writing out `15s`/`10s`, which changes bytes on disk
      and nothing about the scrape. And the budget is the real risk here —
      `collect_media_metrics` runs SYNCHRONOUSLY inside the scrape request and
      issues one `/library/sections/<key>/all` per section (plus a second per
      `show` section) every `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS`, while
      `PLEX_TIMEOUT` alone is 10 s per request. Every thirtieth minute one scrape
      does the sweep; on the default budget that scrape is the one that fails.
      The global is READ, not pinned as `15`, so raising the global raises this
      floor with it.
    """
    body = _read(PROM_SCRAPE)
    block = _scrape_job_block(body, PLEX_EXPORTER_SERVICE)
    present = bool(block.strip())
    targets = _static_targets(block)
    target_is_exporter = bool(targets) and all(
        _yaml_unquote(t) == PLEX_EXPORTER_ADDRESS for t in targets
    )
    job_keys, unreadable_keys = _service_key_lines(block)
    extra_keys = [k for k in job_keys if k not in PLEX_JOB_KEYS]
    no_multi_target_shape = present and not extra_keys and not unreadable_keys
    # The RAW halves, not the effective ones: this clause's `pair_present`
    # requires the job to set BOTH keys itself, which is a different claim from
    # the one `_effective_scrape_pair` resolves for its callers.
    pair = _effective_scrape_pair(body, block)
    interval, timeout = pair["job_interval"], pair["job_timeout"]
    global_interval = pair["global_interval"]
    pair_present = interval is not None and timeout is not None
    timeout_fits = pair_present and timeout <= interval
    budget_raised = (
        pair_present and global_interval is not None
        and interval > global_interval and timeout > PROM_DEFAULT_SCRAPE_TIMEOUT
    )
    ok = (
        present and target_is_exporter and no_multi_target_shape
        and pair_present and timeout_fits and budget_raised
    )
    print(
        f"{'OK' if ok else 'FAIL'}: plex-exporter scrape job is single-target "
        f"(present={present}, target_is_exporter={target_is_exporter} "
        f"(targets={targets}, want={PLEX_EXPORTER_ADDRESS!r}), "
        f"no_multi_target_shape={no_multi_target_shape} (keys={job_keys}, "
        f"unexpected={extra_keys}, unreadable={unreadable_keys}), "
        f"pair_present={pair_present} (interval={interval}s, timeout={timeout}s), "
        f"timeout_fits={timeout_fits}, budget_raised={budget_raised} "
        f"(global_interval={global_interval}s, default_timeout={PROM_DEFAULT_SCRAPE_TIMEOUT}s))"
    )
    return ok


def test_plex_exporter_service_block() -> bool:
    """Step-3a: compose defines `plex-exporter` as a scrape-only service.

    Same scrape-only shape as `pve-exporter` — reachable only by Prometheus over
    the internal compose network, never routed and never published — so the
    reachability clauses below are the same three, reading the same helpers, and
    what they measured on the real image is written up there rather than twice.
    What is new here is the configuration surface: this exporter takes NO CLI
    flags and NO config file, so everything it does is decided by `environment:`.

    * `image_var` / `image_default` — compose pulls
      `{{ docker_host_plex_exporter_image }}` and role defaults declare that
      variable. Both hops, because they fail differently and only one of them is
      covered elsewhere: `test_no_floating_service_image_tags` reddens on a
      default whose tag is not a concrete three-part version, but it says nothing
      about a default that is MISSING — and an undefined variable renders as an
      empty `image:` line, which is a compose error at `just play` rather than
      anything this gate would have said.
    * `keys_allowed` / `no_traefik_labels` / `no_ports` — the reachability pins;
      see `test_pve_exporter_service_block` and `SCRAPE_ONLY_KEYS` for what each
      one is worth and which are stricter than the runtime.
    * `no_command` — this service declares NO `command:`. `SCRAPE_ONLY_KEYS`
      admits the key because `pve-exporter` needs it, so the allow-list cannot
      make this claim and it is pinned on its own. It is not a tidiness rule:
      configuration here is env-var only (`collector.rb`'s `initialize`), so a
      `command:` cannot configure anything — it REPLACES the image's CMD, and the
      most likely one to appear is `--no-collector.config` copied off the service
      above, which this image would not recognise.
    * `addr_from_var` — `PLEX_ADDR` is `{{ docker_host_plex_url }}`, the default
      that already carries the Plex CT address for Traefik's file provider. The
      reuse is the pin: a second literal is a second thing to move when the CT
      does. And the failure it prevents is a quiet one — `PLEX_ADDR` defaults to
      `http://localhost:32400` inside the container, so an absent or misspelled
      value makes the exporter probe ITSELF, and every scrape then answers 200
      with `plex_up 0` while the target reads UP.
    * `env_pinned` — every key of `PLEX_EXPORTER_ENV` is present with the pinned
      value, read as the map docker resolves (`_service_env_map`, LAST WINS), so
      a second `PLEX_TIMEOUT=` appended after the first cannot leave this green
      with the first entry's value. That is round 14's class and this
      `environment:` block is the largest instance of it in the file.
      `METRICS_PREFIX` is the one whose loss is invisible: it names every series
      3b falsifies on and every Step-4 query, and nothing in the container
      complains if it moves.

      The comparison is BYTE-FOR-BYTE against what `_kv_entries` returns, and
      that is the clause, not a detail. This expression normalized TWICE and
      both normalizations were holes, found one round apart:

        `.lower()` on both sides (deleted round 2). `collector.rb` interpolates
        `@metrics_prefix` raw into every series name and compares
        `@plex_ssl_verify != "true"`, so the fold admitted `METRICS_PREFIX=PLEX`
        — every series renamed to `PLEX_*` at HTTP 200 with the target UP — and
        `PLEX_SSL_VERIFY=True`, which turns `VERIFY_NONE` on while the correct
        `true` is the spelling that fails loud (logs/review-step03a-case.log,
        logs/red-step03a-case-lower.log).

        `.strip('"\'')` on the value (deleted round 3). `_kv_entries` already
        removes the quotes that are ORDINARY YAML — the ones around the WHOLE
        entry, `- "METRICS_PREFIX=plex"`, which is `plex` to docker because its
        regex anchors the quote OUTSIDE `key=val`. Quotes around the VALUE alone
        are INSIDE the scalar: `docker compose config` on the real rendered
        template resolves `- METRICS_PREFIX="plex"` to `"plex"` WITH them, and
        they reach the process environment verbatim. Stripping them a second
        time admitted all EIGHT value-quoted spellings of these six keys at
        `PASS: 39/39` (logs/red-step03a-value-quotes.log). The live, silent one
        is `PLEX_TIMEOUT="10"`: `collector.rb:13` is `ENV[...]&.to_i` and
        `'"10"'.to_i` is 0 in Ruby, so every request times out inside the rescue
        that reports it as `plex_up 0` — 200, container healthy, target UP, and
        `plex_media_count` / `plex_sessions_count` ABSENT, which is Step 3b's
        failure list verbatim. `PLEX_SSL_VERIFY="true"` reaches `VERIFY_NONE` by
        the same string compare as `True` did, and a quoted
        `METRICS_MEDIA_COLLECTING_INTERVAL_SECONDS` makes the synchronous
        library sweep run on EVERY scrape.

        `.strip()` on the value, in `_kv_entries` itself (deleted round 4).
        The two deletions above were made in THIS clause while the reader all
        three of `env_pinned`, `port_agrees` and `addr_from_var` share still
        normalized whitespace — and whitespace is the operator with the widest
        reach of the three, because YAML keeps it: `- PLEX_SSL_VERIFY= true`
        resolves to `' true'` and `- "METRICS_PREFIX=plex "` to `'plex '`, both
        of them into the process environment (measured through `cat -A`,
        logs/green-step03a-whitespace-process.log). ELEVEN spellings of these six
        keys were `PASS: 39/39`, the full 35-step gate included, and they land in
        the same two buckets as the quotes did: `PLEX_SSL_VERIFY=' true'` takes
        the `VERIFY_NONE` branch of the same string compare at HTTP 200 with the
        full series set, while `METRICS_PREFIX=' plex'` and `PORT=' 9594'` cannot
        boot at all (logs/review-step03a-r4-whitespace-process.log, leg B).

      **The criterion, stated to be checkable rather than remembered: normalize
      a pinned value only where the PARSER that hands it to the runtime
      normalizes it, and only that far — never to buy a spelling tolerance the
      runtime does not grant.** Both halves of that sentence have a keeper on the
      other side of them. Folding to WIDEN a detector is right, which is why
      `_vault_token_hops`' `(?i)` `leaks` scan keeps its fold; folding where the
      RUNTIME folds too is right, which is why `verify_ssl_off` in
      `test_pve_exporter_service_block` keeps its `.lower()` —
      `pve_exporter/config.py:54` is `env['PVE_VERIFY_SSL'].lower() not in
      ['false', '0']`, so there the fold MIRRORS the process instead of
      outrunning it. And that same clause has no value-strip, correctly:
      `PVE_VERIFY_SSL="false"` reddens, because the quotes leave verification ON
      and the handshake against the self-signed PVE cert fails
      (logs/red-step03a-value-quotes.log row D1).

      `addr_from_var`, one bullet up, is the correct version of this clause and
      always was: it `re.fullmatch`es with no normalization at all, and row E1
      confirms it reddens on a value-quoted `PLEX_ADDR`. The deletions make
      `env_pinned` and `port_agrees` agree with their own neighbour.
    * `port_agrees` — the `PORT` the container listens on is the port the scrape
      job dials. Both sides derive from `PLEX_EXPORTER_PORT`, so this is the
      agreement rather than 9594 written out twice; moving one side alone reddens
      here and in `test_plex_scrape_job_is_single_target` at once. It carried the
      second copy of the value-strip and lost it in the same round, for the same
      reason: `PORT="9594"` is `bad URI "tcp://0.0.0.0:\"9594\""` to the image's
      `puma -b` CMD, so a guard that tolerates the quotes is green on a tree that
      cannot boot.
    """
    compose = _read(COMPOSE)
    block = _strip_comments(_compose_service_block(compose, PLEX_EXPORTER_SERVICE))
    present = bool(block.strip())
    image_var = re.search(
        rf'(?m)^\s*image:\s*\{{\{{\s*{PLEX_EXPORTER_IMAGE_VAR}\s*\}}\}}', block
    ) is not None
    image_default = re.search(
        rf'(?m)^\s*{PLEX_EXPORTER_IMAGE_VAR}:\s*"?(\S+)',
        _strip_comments(_read(ROLE / "defaults" / "main.yml")),
    )
    no_traefik_labels = re.search(r'traefik\.', block) is None
    keys, unreadable_keys = _service_key_lines(block)
    extra_keys = sorted(set(keys) - SCRAPE_ONLY_KEYS)
    keys_allowed = present and not extra_keys and not unreadable_keys
    no_command = present and "command" not in keys
    published = _service_published_ports(block)
    no_ports = published is None
    restart = re.search(r'(?m)^\s*restart:\s*unless-stopped\s*$', block) is not None
    env_map = _service_env_map(compose, PLEX_EXPORTER_SERVICE)
    addr_from_var = re.fullmatch(
        rf'\{{\{{\s*{PLEX_URL_VAR}\s*\}}\}}', env_map.get(PLEX_ADDR_ENV, "")
    ) is not None
    wrong_env = {
        key: env_map.get(key)
        for key, want in PLEX_EXPORTER_ENV.items()
        if env_map.get(key, "") != want
    }
    env_pinned = not wrong_env
    # A BYTE-FOR-BYTE compare against what `_kv_entries` returns: no `.lower()`,
    # no `.strip('"\'')` and — since round 4 deleted it from the shared reader
    # itself — no whitespace fold either. All three normalizations belong to the
    # PARSER, and `_kv_entries` applies exactly the ones that are real here (the
    # sequence indicator, and the trailing whitespace YAML itself drops).
    # See the `env_pinned` bullet above for the criterion and the measurements.
    port_agrees = env_map.get("PORT", "") == PLEX_EXPORTER_PORT
    ok = (
        present and image_var and bool(image_default) and no_traefik_labels
        and keys_allowed and no_command and no_ports and restart
        and addr_from_var and env_pinned and port_agrees
    )
    print(
        f"{'OK' if ok else 'FAIL'}: plex-exporter compose service is scrape-only "
        f"(present={present}, image_var={image_var}, "
        f"image_default={bool(image_default)} "
        f"({image_default.group(1) if image_default else None!r}), "
        f"no_traefik_labels={no_traefik_labels}, "
        f"keys_allowed={keys_allowed} (keys={keys}, unexpected={extra_keys}, "
        f"unreadable={unreadable_keys}), no_command={no_command}, "
        f"no_ports={no_ports} (published={published!r}), restart={restart}, "
        f"addr_from_var={addr_from_var} (PLEX_ADDR={env_map.get(PLEX_ADDR_ENV)!r}), "
        f"env_pinned={env_pinned} (wrong={wrong_env}), "
        f"port_agrees={port_agrees} (want {PLEX_EXPORTER_PORT}))"
    )
    return ok


def test_plex_token_sourced_from_vault() -> bool:
    """Step-3a: the Plex token reaches the container from the vault, never a literal.

    The same three hops as `PVE_TOKEN_VALUE` and `CF_DNS_API_TOKEN`, read by the
    same `_vault_token_hops` — vault key -> `.env` (env.j2) -> `${VAR:-}` in
    compose. What differs is what each hop is worth HERE:

    * `env_from_vault` / `env_defaults_empty` — `PLEX_TOKEN` comes from
      `vault_plex_token` with `| default('')`. The filter is what makes THIS task
      landable: the operator does not read the token out of Plex until 3b, so
      without it every `just play` between now and then fails the render.
    * `compose_indirection` — compose dereferences the same name from the sibling
      `.env` (`${PLEX_TOKEN:-}`), never an inline value. Both sides derive from
      `PLEX_TOKEN_ENV`.
    * `no_literal` — the token VALUE appears nowhere in the role as plaintext.
      `test_no_plaintext_secrets` covers only the Cloudflare/tunnel keys.

    Worth stating because 3b's falsifier list rests on it: an EMPTY token is not
    a quiet state here. `plex_up` comes from Plex's `/identity`, which takes no
    token, so it answers `1` regardless — but every series a dashboard reads
    comes from the token-gated `/library/sections` and `/status/sessions`. What
    the collector rescues is `HTTP::Error` — a CONNECTION-level failure — and a
    rejected token escapes it by at least TWO paths, not the one this docstring
    used to name: `send_plex_api_request` ends in `JSON.parse`, so a non-JSON
    body raises `JSON::ParserError` (row B), while a JSON error body raises
    `NoMethodError` on the missing `Directory` in `collect_media_metrics`
    instead (row C). Either way a rejected token 500s the whole `/metrics`
    response and the target reads DOWN, with ZERO series — `plex_up` included,
    since the collector sets it to 1 and it never reaches the wire. Cite the
    rescue narrowly wherever it appears: a TLS handshake failure is not an
    `HTTP::Error` either, so it 500s here too rather than degrading.
    That is the expected pre-3b state, and it is confirmed against a stub rather
    than against Plex — logs/calibration-step03a-token.log.
    """
    hops = _vault_token_hops(PLEX_TOKEN_ENV, PLEX_VAULT_KEY, PLEX_EXPORTER_SERVICE)
    ok = (
        hops["env_from_vault"] and hops["env_defaults_empty"]
        and hops["compose_indirection"] and not hops["leaks"]
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {PLEX_TOKEN_ENV} sourced from {PLEX_VAULT_KEY} "
        f"via .env (env_from_vault={hops['env_from_vault']}, "
        f"env_defaults_empty={hops['env_defaults_empty']}, "
        f"compose_indirection={hops['compose_indirection']}, "
        f"no_literal={not hops['leaks']} (leaks={hops['leaks']}))"
    )
    return ok


def _yaml_block_by_key(body: str, key: str) -> str:
    """`_key_bounded_block` at whatever column `key` happens to sit on.

    Every other caller of that helper knows its column because the document is
    one this repo writes. `ansible/inventory/hosts.yml` is GENERATED by
    `scripts/gen_inventory.py`, so its nesting is the generator's to move, and a
    column pinned here would turn a reformat into a false RED on a job that still
    points at the right host. The key is located first and its own indent handed
    back to the slicer, which keeps the boundary rule in one place.

    Fails CLOSED in the direction that matters: a key that opens no block (an
    inline `plex: something`) is skipped, and a key that is nowhere returns "",
    so every clause built on this reddens rather than quantifying over nothing.
    """
    for line in _strip_comments(body).splitlines():
        parsed = _yaml_key(line) if _line_class(line) == "key" else None
        if parsed and parsed[1] == key and not parsed[2]:
            return _key_bounded_block(body, key, parsed[0])
    return ""


def _address_port(address: str | None) -> str | None:
    """The PORT half of a `host:port` listen address, or None.

    `0.0.0.0:9100` is a bind address: the host half is a wildcard meaning "every
    interface", not a name anything dials. Only the port crosses to the scrape
    side, so only the port is returned and the caller cannot accidentally compare
    the halves that do not relate.

    Refuses what it does not understand — no colon, or a port that is not
    decimal — because the alternative is inventing a port for a job that then
    scrapes it. The bare `:9100` form node-exporter also accepts comes back as
    `9100`, since `rpartition` gives it an empty host and a real port.
    """
    if not address:
        return None
    _, sep, port = _yaml_unquote(address).rpartition(":")
    return port if sep and re.fullmatch(r'\d+', port) else None


def _signature_default_number(source: str, param: str) -> float | None:
    """A numeric keyword DEFAULT in a Python signature, read with `ast`.

    Reading a value out of `plex_blip_watchdog.py` by regex would match the
    docstring that describes it as readily as the signature that sets it, and
    importing the module to ask it directly would execute a program this guard
    has no business running. `ast` reads the artifact the interpreter reads.

    REFUSES rather than guesses, three ways, because a default this cannot see is
    a relation that silently stops being pinned: a file that does not parse, a
    parameter that appears in more than one signature (nothing here can say which
    one the unit reaches), and a default that is not a literal number — a
    computed or variable default has no value at read time, and `True` is not a
    duration however well `bool` subclasses `int`.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = node.args
        positional = args.posonlyargs + args.args
        pairs = list(zip(positional[len(positional) - len(args.defaults):], args.defaults))
        pairs += [(a, d) for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None]
        for arg, default in pairs:
            if arg.arg != param:
                continue
            if not isinstance(default, ast.Constant):
                return None
            if isinstance(default.value, bool) or not isinstance(default.value, (int, float)):
                return None
            found.append(float(default.value))
    return found[0] if len(found) == 1 else None


def _defines_and_references(source: str, name: str) -> tuple[bool, bool]:
    """Does `source` define a module-level `name`, and does its CODE use it?

    What arms a citation to another guard. `run_gate.py` globs
    `scripts/test_*.py` and runs each file's `__main__`, so a shape-test clause
    reaches the gate only by being defined AND reached from that module's own
    `main()`; a function that is merely defined is dead code the gate never
    scores, and a citation to dead code is a fact nothing holds.

    THE SECOND HALF IS SCORED AS A `Name` LOAD, NOT AS A CALL, and the
    difference is measured rather than guessed: this file registers its checks
    by CALLING them in `main()`, while `test_plex_node_exporter_shape.py`
    registers them as REFERENCES in a `TESTS` tuple that `main()` then maps over
    (which is also what its own `test_every_test_function_is_registered_in_tests`
    scores). A reader that demanded `ast.Call` would red on the second spelling
    with the clause fully live — a false-RED of exactly the kind this clause
    replaced. A `Name` load covers both, because `f()` loads `f` too.

    Read with `ast` and not by substring FOR THE SAME REASON THIS CLAUSE
    REPLACED A SUBSTRING: `name in source` is satisfied by the function's name
    appearing in a comment, or in a docstring that describes deleting it. The
    definition is required at module level because a nested `def` is not what
    `main()` can reach.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False, False
    defined = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
        for node in tree.body
    )
    referenced = any(
        isinstance(node, ast.Name)
        and node.id == name
        and isinstance(node.ctx, ast.Load)
        for node in ast.walk(tree)
    )
    return defined, referenced


def _own_docstring() -> str:
    """The CALLING function's own docstring, found through the running frame.

    A clause cannot name its own docstring without writing its own name inside
    itself, which would be one more literal of exactly the kind this pair of
    helpers exists to relate — and a rename would then raise `NameError` out of
    a guard instead of redding it. The frame's `co_name` follows a rename for
    free. A caller that is not a module-level function returns "", which reds
    the clause reading it rather than silently passing.

    THE ONE INTERPRETER FLAG THAT WOULD BLIND THIS is `-OO`, which discards
    docstrings: every clause reading its own prose would then red. `run_gate.py`
    runs each shape test as `[sys.executable, <path>]` with no flags, so that is
    a statement about reach rather than a live risk — and redding is the safe
    direction for it to fail in.
    """
    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None
    if caller is None:
        return ""
    return getattr(globals().get(caller.f_code.co_name), "__doc__", None) or ""


def _prose_citations(doc: str, module: str) -> list:
    """Every `module::<name>` spelling `doc` carries, in order.

    ARMING A CITATION'S CONSTANT IS NOT ARMING THE CITATION. A `path::clause`
    written into prose is a SECOND literal of the fact the constant holds, and
    nothing relates the two: rename the cited clause, fix the constant the RED
    names, and the sentence beside it goes on naming a function that exists in
    no file while the suite is green. That was measured as the minimal repair a
    future engineer makes, not as a contrived edit.

    WHAT IS RETURNED IS EVERY SPELLING, NOT A YES/NO, so the caller can require
    them all to agree. A `bool` here would fail open on the interesting case —
    two prose copies of which only one was updated.

    WHITESPACE IS REMOVED FROM `doc` BEFORE THE SEARCH, so re-wrapping a
    93-character qualified name across two lines is not a RED. That tolerance
    is deliberate and is the same one `_normalise_refs` gives a legal Jinja
    reformat: round 1 of this row was rejected for a check that redded on a
    spelling the subject was free to use, and a citation's line breaks are the
    author's business.

    A SUBSTRING IS THE RIGHT INSTRUMENT HERE AND IT IS NOT THE SECOND PARSER
    THIS ROW DELETED: the subject IS prose, and this never opens the cited
    module — `_defines_and_references` holds that end, and holds it with `ast`
    precisely because a name in a comment is not a name anything runs.
    """
    return re.findall(
        rf"{re.escape(module)}::([A-Za-z_]\w*)", re.sub(r"\s+", "", doc)
    )


def test_plex_node_exporter_scrape_job() -> bool:
    """Step-4d: CT 110's node-exporter is scraped, with its PORT read off the role.

    The first job in this file whose target is not a compose service name, and
    the first whose two ends live in two different Ansible roles. `ansible/site.yml`
    runs `docker_host` and `plex` as SEPARATE plays, so this template cannot
    render a `plex` role default even though that default is what decides the
    port — the relation therefore lives HERE, in the guard, and that is the
    design rather than a compromise.

    * `present` — the job resolves exactly ONCE inside `scrape_configs:`
      (`_scrape_job_block`), which also settles the name collision: `node-exporter`
      is already taken at the top of the file by the docker host's own exporter,
      and a duplicate name returns "" rather than picking a block.
    * `single_target` / `host_is_inventory_ref` — exactly one target entry,
      quantified over every `targets:` list under `static_configs:`
      (`_indented_blocks`, plural, for the reason round 9 established one job
      over: `static_configs` is a LIST and Prometheus scrapes every entry of it).
      Its host half is the Jinja reference `PLEX_NODE_TARGET_EXPR`, NOT a second
      copy of the address — `docker_host_plex_url` in this role's defaults
      already holds one spelling of CT 110's IP, and a second one is the defect
      this clause exists to refuse.
    * `inventory_has_host` — what discharges the literal inside that expression.
      `hostvars['plex']` names the host as a bare string because this file's own
      `_LINE_BOUNDED_EXPR` refuses the rename-robust `groups['plex'] | first`
      form (measured against the compiled regex), and that name comes from
      tofu's `plex_name` output through `gen_inventory.py`. So the census asks
      `inventory/hosts.yml` whether a host of that name really sits under that
      group WITH an `ansible_host`: a tofu rename reds the gate here instead of
      rendering a target Ansible cannot resolve.
    * `port_follows_exporter` — LOAD-BEARING, and the whole reason this row
      exists. The target's port is compared against the port half of
      `plex_node_exporter_listen_address` read out of the plex role's defaults,
      so the port the exporter BINDS and the port this job DIALS cannot move
      apart.

      THE SECOND END IS THIS TEMPLATE'S OWN LITERAL, NEVER THE SAME VARIABLE
      TWICE. `task-1786167365-e571` is that mistake one file over — `runs_exporter`
      compared a rendered argv against the variable it rendered FROM, which is a
      tautology, and retargeting the variable left the suite 9/9 GREEN over a
      203/EXEC crash loop.
    * `far_end_is_held` — the OTHER half of that relation, held by CITATION
      rather than re-checked here. That the plex role still passes the variable
      to `--web.listen-address` (without which the default is a value nothing
      reads and the port relation is nominal) is asserted by
      `test_plex_node_exporter_shape.py::test_the_listen_address_is_a_variable_the_scrape_job_can_pin`,
      which names THIS row by task key in its own docstring.

      A SECOND SPELLING WAS MEASURED WORSE IN BOTH DIRECTIONS, which is why this
      is a citation and not a check. `PLEX_NODE_LISTEN_REF in <drop-in>` — a
      file-wide substring — goes GREEN on the flag hardcoded with the variable
      kept in a comment, on an `Environment=` line, or passed to a DIFFERENT
      flag, all three of which the cited clause reds; and it goes RED on the
      legal Jinja reformats `{{var}}` and `{{  var  }}`, which the cited clause
      tolerates on purpose (`_normalise_refs`). Weaker AND more brittle at once,
      and the brittle half is the live one — a false-RED tripwire in the gate on
      a spelling the repo has a commented decision to accept.

      SO WHAT IS CHECKED HERE IS THE CITATION ITSELF: `_defines_and_references`
      reads that module with `ast` and requires the clause to be DEFINED and
      REACHED BY CODE, because `run_gate.py` globs `scripts/test_*.py` and runs
      each file's `__main__` — a clause that drops out of that module's `TESTS`
      tuple stops being in the gate, and this docstring would then cite a fact
      nothing holds.
    * `far_end_prose_agrees` — THE CITATION IS SPELLED TWICE AND BOTH COPIES
      ARE NOW HELD. `PLEX_NODE_FAR_END_CLAUSE` is what the clause above reads;
      the qualified name three paragraphs up is a SECOND literal of the same
      fact, written where the reader is, and until this field nothing related
      them. Measured as the minimal repair a future engineer makes rather than
      as a contrived edit (`logs/builder-4d-r3-citation.py` R2): rename the
      cited clause consistently — its `def` and its entry in that module's
      `TESTS` tuple, which leaves the cited suite 9/9 GREEN by its own
      registration census — then fix ONLY what the RED names, the constant, and
      this suite came back GREEN with the sentence naming a function that
      existed in NO file in the repo. `git grep -lF 'def <that name>'` returned
      nothing while the gate passed.

      `_prose_citations` reads THIS docstring — not this file, which would be
      the file-wide substring this row was opened to delete — and requires
      every `<suite>::<clause>` spelling in it to be the constant, so a stale
      second copy cannot hide behind a fresh first one. It is deliberately
      blind to line breaks: the qualified name is 93 characters and re-wrapping
      it is the author's business, not a defect (round 1's rejection was a
      check that redded on a legal reformat).
    * `no_multi_target_shape` — the job's OWN key column may hold only
      `PLEX_NODE_JOB_KEYS`, the allow-list shape `test_plex_scrape_job_is_single_target`
      established (an absence pin fails open one key past its edge, and
      `_service_key_lines` reddens on any line at that column it cannot read).
      What it keeps out is `metrics_path`: the pve-exporter job ten lines up NEEDS
      one and node-exporter serves the plain default path, so a path copied off
      the neighbour is a 404, the target reads DOWN, and the failure is invisible
      until a dashboard is empty. `params` and a `__param_target` relabel are the
      same copy, and there is nothing here to interrogate on another host's behalf.
    * `interval_follows_refresh` — the scrape cadence is pinned BY RELATION to the
      watchdog's own `textfile_refresh_sec` default, which is `task-1786159059-184b`:
      design §4.5 sets both at 15 s, that row measured the default moving to
      86400.0 with the watchdog suite still 92/92 GREEN, and nothing related the
      two. A textfile collector re-serves whatever is on disk, so the cadence that
      decides the graph's resolution is the SLOWER of the pair; scraping fifteen
      seconds apart a file rewritten once a day is 5760 identical samples and one
      real one.

      EQUALITY AND NOT `<=`, stated as a claim about what this catches: `<=` reads
      as the honest inequality (over-scraping only wastes samples) and leaves
      184b's own mutation GREEN, since 15 <= 86400. The interval is read
      EFFECTIVELY — the job's own `scrape_interval` if it sets one, otherwise the
      file's `global` — because that is what Prometheus scrapes at, and a
      template that only inherited would still be pinned to the refresh.
    * `interval_is_job_local` — the job carries its OWN `scrape_interval` key.
      SEPARATE FROM THE CLAUSE ABOVE, and one of them cannot do the other's job:
      `global` is also 15s today, so DELETING the job's key leaves the effective
      read at 15.0 and `interval_follows_refresh` GREEN. The template says the
      interval is "job-local rather than inherited so that this job's cadence is
      a property of this job" and that "a change to the global interval must not
      coarsen it silently" — a mechanism sentence a value-preserving mutant walks
      straight past, which is `task-1786170786-3fb1`. An allow-list of key names
      (`no_multi_target_shape`) cannot close it either: it says which keys MAY
      appear, never which MUST.
    * `timeout_fits` — the effective timeout does not exceed the effective
      interval. Prometheus REFUSES to load a config that gets this backwards, so
      the whole file stops scraping rather than this job alone, and nothing in
      this repo's gate loads a Prometheus config (`test_plex_scrape_job_is_single_target`
      measured that at length). The default this job leaves in force is
      `PROM_DEFAULT_SCRAPE_TIMEOUT`, read here rather than assumed absent.
    """
    body = _read(PROM_SCRAPE)
    block = _scrape_job_block(body, PLEX_NODE_JOB)
    present = bool(block.strip())
    targets = [_yaml_unquote(t) for t in _static_targets(block)]
    single_target = len(targets) == 1
    host_halves = [t.rpartition(":")[0] for t in targets]
    port_halves = [t.rpartition(":")[2] for t in targets]
    host_is_inventory_ref = bool(targets) and all(
        h == PLEX_NODE_TARGET_EXPR for h in host_halves
    )
    exporter_port = _address_port(
        _block_scalar(_read(PLEX_ROLE_DEFAULTS), PLEX_NODE_LISTEN_VAR)
    )
    port_follows_exporter = (
        bool(targets) and exporter_port is not None
        and all(p == exporter_port for p in port_halves)
    )
    far_end_defined, far_end_referenced = _defines_and_references(
        _read(PLEX_NODE_FAR_END_SUITE), PLEX_NODE_FAR_END_CLAUSE
    )
    far_end_is_held = far_end_defined and far_end_referenced
    far_end_prose = _prose_citations(_own_docstring(), PLEX_NODE_FAR_END_SUITE.name)
    far_end_prose_agrees = bool(far_end_prose) and all(
        cited == PLEX_NODE_FAR_END_CLAUSE for cited in far_end_prose
    )
    host_block = _yaml_block_by_key(
        _yaml_block_by_key(_yaml_block_by_key(_read(INVENTORY), PLEX_INVENTORY_GROUP), "hosts"),
        PLEX_INVENTORY_HOST,
    )
    inventory_has_host = bool(_block_scalar(host_block, "ansible_host"))
    job_keys, unreadable_keys = _service_key_lines(block)
    extra_keys = [k for k in job_keys if k not in PLEX_NODE_JOB_KEYS]
    no_multi_target_shape = present and not extra_keys and not unreadable_keys
    pair = _effective_scrape_pair(body, block)
    interval, timeout = pair["interval"], pair["timeout"]
    job_interval, global_interval = pair["job_interval"], pair["global_interval"]
    refresh = _signature_default_number(
        _read(PLEX_WATCHDOG_SOURCE), PLEX_WATCHDOG_REFRESH_PARAM
    )
    interval_follows_refresh = (
        interval is not None and refresh is not None and interval == refresh
    )
    interval_is_job_local = job_interval is not None
    timeout_fits = interval is not None and timeout <= interval
    ok = (
        present and single_target and host_is_inventory_ref and inventory_has_host
        and port_follows_exporter and far_end_is_held and far_end_prose_agrees
        and no_multi_target_shape and interval_follows_refresh
        and interval_is_job_local and timeout_fits
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {PLEX_NODE_JOB} scrape job follows the plex role "
        f"(present={present}, single_target={single_target} (targets={targets}), "
        f"host_is_inventory_ref={host_is_inventory_ref} "
        f"(want={PLEX_NODE_TARGET_EXPR!r}), inventory_has_host={inventory_has_host} "
        f"({PLEX_INVENTORY_GROUP}/{PLEX_INVENTORY_HOST} in {INVENTORY.name}), "
        f"port_follows_exporter={port_follows_exporter} "
        f"(exporter_port={exporter_port}, job_ports={port_halves}), "
        f"far_end_is_held={far_end_is_held} ({PLEX_NODE_FAR_END_SUITE.name}::"
        f"{PLEX_NODE_FAR_END_CLAUSE} defined={far_end_defined} "
        f"referenced={far_end_referenced}), "
        f"far_end_prose_agrees={far_end_prose_agrees} "
        f"(prose spellings={far_end_prose}), no_multi_target_shape="
        f"{no_multi_target_shape} (keys={job_keys}, unexpected={extra_keys}, "
        f"unreadable={unreadable_keys}), interval_follows_refresh="
        f"{interval_follows_refresh} (interval={interval}s, "
        f"{PLEX_WATCHDOG_REFRESH_PARAM}={refresh}s), interval_is_job_local="
        f"{interval_is_job_local} (job_scrape_interval={job_interval}s, "
        f"global={global_interval}s), timeout_fits={timeout_fits} "
        f"(timeout={timeout}s))"
    )
    return ok


def test_blackbox_exporter_service_block() -> bool:
    """Step-5a: compose defines `blackbox-exporter` as a scrape-only service.

    The third service of the `pve-exporter` / `plex-exporter` class and the first
    one that READS A RENDERED CONFIG, so it is that shape plus exactly one key.
    Only the clauses that differ from those two are argued here; for
    `keys_allowed` and `no_ports` — what each half closes, and which spellings
    were measured green through earlier versions of them — see
    `test_pve_exporter_service_block`, which is where those rows were won.

    * `keys_allowed` — the allow-list is `BLACKBOX_SERVICE_KEYS`, i.e.
      `SCRAPE_ONLY_KEYS` plus `volumes`, spelled as its own constant so the bind
      mount is granted to THIS service and not to the two that must never have
      one. It carries a second job here that it does not carry there: it is what
      holds the 0640 mode of `BLACKBOX_MODE` up. That mode is correct because the
      image declares no `USER` and the process runs as root, and `user: "65534"`
      on this service would make the same file unreadable — an unenumerated key,
      so this clause reddens on it. The mode's rationale and its guard are
      therefore in different places on purpose, and each says so.
    * `no_traefik_labels` — a `/probe` endpoint takes its TARGET from a caller
      -supplied query parameter, so a router in front of it is an open HTTP
      client on the internal network, not merely an exposed dashboard. This is
      the `pve-exporter` argument one notch sharper, and it is why the service
      mirrors the node-exporter block (compose.yml.j2's "Scrape targets only"
      group) rather than the prometheus one.
    * `config_flag` — the compose `command:` names the container-side path
      through `--config.file`. Read here as PRESENCE of the flag only; the
      AGREEMENT between that flag's value and the mount's own target is the
      `reads_it` hop of `test_rendered_configs_reach_the_service_that_reads_them`
      and is not restated (two guards over one fact is `task-1786153086-9f13`'s
      class). What this adds that the walk cannot: the image supplies its own
      `--config.file=/etc/blackbox_exporter/config.yml` in `Cmd`, so a compose
      block with NO `command:` at all still boots and reads the image's default
      path — with the mount landing somewhere else entirely and the exporter
      serving its built-in modules. That is a live state, not a crash, and the
      walk's `reads_it` sees it only because this flag is absent.
    """
    block = _strip_comments(_compose_service_block(_read(COMPOSE), BLACKBOX_SERVICE))
    present = bool(block.strip())
    image_var = re.search(
        r'(?m)^\s*image:\s*\{\{\s*docker_host_blackbox_exporter_image\s*\}\}', block
    ) is not None
    no_traefik_labels = re.search(r'traefik\.', block) is None
    keys, unreadable_keys = _service_key_lines(block)
    extra_keys = sorted(set(keys) - BLACKBOX_SERVICE_KEYS)
    keys_allowed = not extra_keys and not unreadable_keys
    published = _service_published_ports(block)
    no_ports = published is None
    restart = re.search(r'(?m)^\s*restart:\s*unless-stopped\s*$', block) is not None
    config_flag = _last_flag_value(_service_command_args(block), "--config.file")
    flag_present = config_flag is not None
    ok = (
        present and image_var and no_traefik_labels and keys_allowed and no_ports
        and restart and flag_present
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {BLACKBOX_SERVICE} compose service is scrape-only "
        f"(present={present}, image_var={image_var}, "
        f"no_traefik_labels={no_traefik_labels}, "
        f"keys_allowed={keys_allowed} (keys={keys}, unexpected={extra_keys}, "
        f"unreadable={unreadable_keys}), "
        f"no_ports={no_ports} (published={published!r}), "
        f"restart={restart}, config_flag={flag_present} (value={config_flag!r}))"
    )
    return ok


def _blackbox_field_defects(doc) -> tuple:
    """`(unknown names, mistyped values)` in `doc`, both as dotted paths.

    Step-5a, DEC-286 and DEC-291. One walk, four levels, each scored against the
    map that names what may live there and WHAT SHAPE IT MUST HAVE — the
    `keys_allowed` idiom of `test_blackbox_exporter_service_block` one axis over,
    applied to the config document instead of the compose service.

    TWO LISTS AND NOT ONE, because they are two different sentences about the
    document: `plex_identity_direct.retries` is a field blackbox has never heard
    of, and `plex_identity_direct.timeout=5` is a field it knows given something
    it cannot unmarshal. Both are `Error loading config`, rc=1 and a crash loop
    under `restart: unless-stopped`; merging them would make the clause print
    `unknown=[…timeout…]` about a field this row PINS BY NAME, which is a red
    that lies about what broke.

    EVERY PATH LEAVES THROUGH ONE f-STRING, and that is the repair rather than a
    style choice. DEC-291 charge 2 was the TOP level taking a different code
    path from the three below it (`sorted(set(doc) - …)` against
    `f"{name}.{k}"`): PyYAML is YAML 1.1, so `on`/`no`/`yes` and bare numbers at
    a KEY position resolve to `bool`/`int`, and one such key beside any other
    unknown field made `sorted` compare `str` with `bool` — `TypeError`, rc=1,
    ZERO `FAIL` lines, the crashed-reader shape this row has now grown three
    times. A `str()` at that one site would have closed the instance; scoring
    every level through the SAME helper closes the class, because there is no
    longer a level that can diverge. `no:` is the row that proves it matters in
    both directions: go-yaml v3 reads it as the STRING, so the BINARY ACCEPTS a
    document PyYAML hands this walk as `False` (logs/builder-5a-r4-census.log,
    X4) — the two parsers disagree and it was the guard that broke.

    THE PATH THEREFORE NAMES THE RESOLVED KEY, NOT THE SOURCE SPELLING, and that
    is worth knowing before reading a red at 07:00: `on: 1` in the file prints as
    `unknown=['True']`, because PyYAML resolved the scalar and threw the spelling
    away long before this walk saw it. The line number is not recoverable here
    either; the field IS, which is what the red is for.

    TOTAL OVER MALFORMED DOCUMENTS, like the reading clause it serves: a level
    that is not a mapping is SKIPPED rather than walked, because a module whose
    `http:` is a scalar is already the subject of `probers`/`tls_differential`
    and a second reader crashing on it would be that same shape again.

    The paths are returned rather than a bool so the clause can PRINT the
    offending field, which is this suite's standing rule: a red names what broke.
    """
    unknown, mistyped = [], []

    def _score(prefix, level, census):
        for key, value in level.items():
            path = f"{prefix}{key}"
            shape = census.get(key)
            if shape is None:
                unknown.append(path)
            elif not shape(value):
                mistyped.append(f"{path}={value!r}")

    if not isinstance(doc, dict):
        return [], []
    _score("", doc, BLACKBOX_TOP_FIELDS)
    modules = doc.get("modules")
    if not isinstance(modules, dict):
        return sorted(unknown), sorted(mistyped)
    for name, mod in modules.items():
        if not isinstance(mod, dict):
            continue
        _score(f"{name}.", mod, BLACKBOX_MODULE_FIELDS)
        http = mod.get("http")
        if not isinstance(http, dict):
            continue
        _score(f"{name}.http.", http, BLACKBOX_HTTP_FIELDS)
        tls = http.get("tls_config")
        if isinstance(tls, dict):
            _score(f"{name}.http.tls_config.", tls, BLACKBOX_TLS_FIELDS)
    return sorted(unknown), sorted(mistyped)


# The legal YAML that may stand between the top of a file and its first KEY
# while carrying no prose: a document start, and the directives that may precede
# one. A BOM is stripped separately — it is a character on the first line rather
# than a line of its own.
#
# SKIP ONLY WHAT THE BINARY TAKES, and that rule is this constant's whole defect
# history (DEC-309). Round 3 shipped `^(?:---|%\S.*)$` — EVERY `%` directive,
# generalised from the one `%TAG` row it had measured — and `%YAML 1.2` is a
# document `prom/blackbox-exporter:v0.28.0` REFUSES outright ("found incompatible
# YAML document"), because go-yaml v3 implements YAML 1.1. That is the version
# anyone writing a config today reaches for, rc=1 under `restart: unless-stopped`
# is the crash loop this role served for two weeks, and this reader walked past
# it into a GREEN the parent `1f29d08` had RED.
#
# FITTED TO 26 PROLOGUES driven through real ansible-core 2.21.1 into that
# image's own `--config.check`, not to go-yaml's source
# (logs/builder-5b-r4-red.log legs B and C, logs/builder-5b-r4-legd.log; all 26
# plus the shipped file are re-driven as a biconditional against the SUITE in
# logs/builder-5b-r4-door.log, 27 rows).
#   TAKEN, rc=0 — 13. `---`; `--- # comment`; `---` + a blank line; a UTF-8 BOM;
#           `%TAG !e! …` + `---`; `%YAML 1.1` + `---` with one space, with two
#           spaces, with a TAB, with a trailing comment, and with a comment LINE
#           between the directive and the `---`; `%TAG` and `%YAML 1.1` together;
#           and `---` or `%YAML 1.1` + `---` placed BELOW this file's 48-line
#           header instead of above it.
#   REFUSED, rc=1 — 13. `----`; `...`; a bare `%TAG` + `---`; `%TAG` with no
#           `---`; `%YAML 1.1` with no `---`; `%YAML 1.1` given TWICE; `%YAML
#           1.0`, `%YAML 1.2`, `%YAML 1.10`, `%YAML 2.0`, lower-case `%yaml 1.1`
#           and an unknown `%FOO bar`, each + `---`; and `%YAML 1.2` + `---`
#           BELOW the header.
# The `(?:\s.*)?` tails are two of those rows rather than caution: `--- # comment`
# and `%YAML 1.1 # comment` are both rc=0 on the binary, and round 3's spelling
# RED the first of them (logs/builder-5b-r4-red.log leg C).
#
# Which of the REFUSED rows this reader is the one to red, and which belong to the
# reading clause's `parses`, is `_leading_comment_block`'s own paragraph.
_YAML_PROLOGUE = re.compile(r"^(?:---(?:\s.*)?|%TAG\s.*|%YAML\s+1\.1(?:\s.*)?)$")
BLACKBOX_PROLOGUE_EVIDENCE = "logs/builder-5b-r4-{red,legd}.log"


def _is_yaml_directive(line) -> bool:
    """Is this line a `%` directive? BOM-tolerant, like the reader above it.

    Read on `_leading_comment_block`'s STOP line, where it is a document fact
    rather than a formatting one: every `%` prologue that reader refuses to walk
    past is one the binary refuses too. The seven are enumerated in that reader's
    own docstring, which is also where the converse is disclaimed.

    IT IS INDENTATION-TOLERANT TOO, AND THAT IS A MEASUREMENT RATHER THAN AN
    INTENTION. An indented `%YAML 1.1` is not a directive at all in YAML, and both
    this predicate and `_YAML_PROLOGUE` see it as one because both read the
    `.strip()`ped line. The binary refuses both indented spellings, and so does
    the suite — `1.1` through the reading clause's `parses` and `1.2` through this
    predicate, so the verdicts agree by different routes rather than by design
    (logs/builder-5b-r4-mutants.log rows A2/A3).
    """
    return bool(line) and line.lstrip("\ufeff").strip().startswith("%")


def _leading_comment_block(text: str) -> tuple:
    """The `#` header a reader meets before a document's first KEY.

    Returns `(block, stopped_at)` — the comment lines, and the line this reader
    refused to read past, so a caller can say what it could not see instead of
    reporting an absence as a fact about the prose.

    THE FIRST KEY, AND NOT THE FIRST NON-COMMENT LINE, and that distinction is
    this function's whole defect history (DEC-305 charge 2). Round 2 shipped the
    weaker spelling, and a YAML DOCUMENT START is neither blank nor a comment:
    prepending `---` — ordinary YAML, and what `compose.yml.j2` in the SAME role
    directory and the SAME `LINE_READ_TEMPLATES` tuple already opens with — made
    the preamble EMPTY. Measured through real ansible-core 2.21.1 into
    `prom/blackbox-exporter:v0.28.0 --config.check`
    (`logs/builder-5b-r3-red.log` leg A): `---` rc=0 "Config file is ok", a
    `%TAG` directive + `---` rc=0, a UTF-8 BOM rc=0 — three documents the binary
    TAKES, on which the guard printed "own header is 0 line(s),
    names_the_header=False, unannounced=['plex_sessions']", all three false of a
    48-line header that names both. A prose-locating reader that breaks on "the
    first non-comment line" inherits every legal prologue the format allows.

    IT STOPS ON ANYTHING IT DOES NOT RECOGNISE, deliberately — an unknown
    construct ends the header rather than letting this reader wander into the
    document body and score a per-module comment. That is why the stop line is
    RETURNED: an empty block is a statement about this reader, and the caller
    prints it as one.

    A LINE, NOT A DOCUMENT, and DEC-309 is what that distinction cost. Round 3
    read "recognise the prologue" as "recognise the `%` family" and skipped
    `%YAML 1.2` — see `_YAML_PROLOGUE`, where the 26 measured prologues now live.
    The split those rows support is this:

    * Every `%` line this reader will NOT walk past is one the binary refuses on
      its own. Seven of them, measured: `%YAML 1.0`, `%YAML 1.2`, `%YAML 1.10`,
      `%YAML 2.0`, `%yaml 1.1`, `%FOO bar`, a bare `%TAG`. So the caller reds
      `prologue_loads` off the stop line via `_is_yaml_directive`, and it holds
      wherever the directive SITS — a `%YAML 1.2` below this file's 48-line
      header is rc=1 on the binary too, and there the header is intact and reads
      true, so no prose arm could ever have caught it.
    * The converse does NOT hold, and this reader does not pretend otherwise. A
      document can be refused for a reason that is not any one line — `%YAML 1.1`
      given TWICE, or either directive with no `---` after it. All three are the
      reading clause's `parses`, which reds all three; measured at HEAD rather
      than assumed (`logs/builder-5b-r4-red.log` leg B). Re-spelling them here
      would be the second-reader drift this file has already paid for.

    ONE MEASURED DISAGREEMENT, AND IT IS NOT THIS READER'S. `%YAML` + a TAB +
    `1.1` is rc=0 on the binary and a PyYAML `while scanning a directive`, so the
    suite reds a config that runs — through `parses`, one clause over. Filed as
    `task-1786198184-88d8` against the reader-vs-binary biconditional
    (`task-1786189577-e019`'s subject) rather than papered over here.

    Scoped to the header on purpose: the per-module comments are attributions
    ("this module came from Step 5b"), which stay true for ever, while the header
    is an ORIENTATION a later reader trusts for what the file contains.
    """
    kept = []
    stopped_at = None
    for line in text.splitlines():
        stripped = line.lstrip("\ufeff").strip()
        if not stripped or stripped.startswith("#"):
            kept.append(line)
            continue
        if _YAML_PROLOGUE.match(stripped):
            continue
        stopped_at = line
        break
    return "\n".join(kept), stopped_at


def _credential_spellings(text: str) -> list:
    """Every spelling of a live credential a template of this role can carry.

    Step 5b named this scan inline while `prometheus.yml.j2` was a file no row
    was editing; row 5c edits it, and the fence that says the token must not
    enter it is now read by TWO clauses — 5b's, which asserts the fact, and
    5c's, which asserts that the render's world-read bit is LICENSED by it. Two
    regexes over one question is the drift this file spent Step-2a rounds 13-15
    closing, so there is one.

    Three spellings and each is a real hop rather than a synonym: `vault_*` is
    the ansible-vault variable itself, `X-Plex-Token` (any casing — Go's
    `Header.Set` canonicalises, logs/builder-5b-r2-wire.log) is the header a
    `params:` block or a `?X-Plex-Token=` target suffix would name, and
    `PLEX_TOKEN` is the env var `env.j2` assigns. A scrape config that smuggles
    the credential has to write one of them.

    WHAT IT DOES NOT SEE, named so it is not mistaken for a proof: a token
    LITERAL, pasted with none of these names around it. That is
    `test_no_plaintext_secrets`' subject and it is a different reader.
    """
    return sorted(set(
        re.findall(r'\bvault_\w+', text)
        + re.findall(rf'(?i){re.escape(BLACKBOX_TOKEN_HEADER)}', text)
        + re.findall(rf'\b{re.escape(PLEX_TOKEN_ENV)}\b', text)
    ))


def _credential_modules(modules) -> list:
    """Module names whose `http.headers` carries the token header, any casing.

    CASE-INSENSITIVE, and that is a measurement rather than caution: a config
    spelling `x-plex-token:` reaches the wire as `X-Plex-Token` because Go's
    `Header.Set` canonicalises, and the probe reads `probe_success 1`
    (logs/builder-5b-r2-wire.log). Such a document is a credential-bearing file
    whatever `header_key` thinks of its spelling, so the arm that scores the
    file's own header must see it.

    TOTAL OVER MALFORMED DOCUMENTS, like every other reader here: a module whose
    `http:` is a scalar is already `probers`' subject and a second reader
    crashing on it is the crashed-reader shape this row has grown three times.
    """
    found = []
    for name, mod in (modules.items() if isinstance(modules, dict) else ()):
        http = mod.get("http") if isinstance(mod, dict) else None
        headers = http.get("headers") if isinstance(http, dict) else None
        if isinstance(headers, dict) and any(
            str(key).lower() == BLACKBOX_TOKEN_HEADER.lower() for key in headers
        ):
            found.append(name)
    return sorted(found, key=str)


def test_blackbox_modules_are_the_three_plex_probes() -> bool:
    """Step-5a: the blackbox config PARSES and defines exactly `BLACKBOX_MODULES`.

    RENAMED AT `5b`, from `…_are_the_two_token_free_probes`, and the rename is
    the point rather than tidying. `5a` shipped the two probes that need no
    credential and this clause was named for that fact; `5b` adds
    `plex_sessions`, which carries a live Plex token, so a clause named "the two
    token-free probes" would print OK over a document that is neither. A guard
    whose name disagrees with the file it guards is the defect this objective has
    charged repeatedly — and the count is now read from `BLACKBOX_MODULES` in
    every arm below, so the NAME is the last place a number was written twice.
    (`progress.md`'s Step-5a verification table cites the old name; that row
    records what was true at `5a` and is annotated rather than rewritten.)

    WHAT THIS CLAUSE DOES NOT COVER, so the split is legible: the SESSIONS
    module's own token wiring — the header key, the vault reference, the world
    bit and the owner — is `test_blackbox_sessions_probe_carries_the_vault_token`.
    This one still asks only what it always asked: does the document parse, is
    every field known and typed, and is the module SET exactly the tuple `5c`
    reads.

    THE JOIN NOTHING ELSE CHECKS. Row `5c` writes three scrape jobs whose
    `params.module` values are the names defined here, and no process reconciles
    the two: blackbox answers `/probe?module=<unknown>` with HTTP 400, so
    Prometheus records the target DOWN and both files stay individually valid.
    The names therefore live in ONE tuple that both sides read (`BLACKBOX_MODULES`)
    and this clause pins that tuple against the template as a SET EQUALITY — a
    module defined but unnamed by the tuple reddens as loudly as one named and
    undefined, because a name added here without `5c` is the same broken join
    seen from the other end.

    PARSED, NOT GREPPED, and that is the acceptance criterion this row was cut
    with. A regex over `^  (\\w+):` reads a module name out of a document blackbox
    itself refuses to load — a duplicated key, a tab, a mis-indented `prober` —
    and the exporter exits non-zero at start, which `restart: unless-stopped`
    turns into the crash loop this repo has already paid for once. So the text
    goes through a YAML parser — `_StrictLoader`, for the reason two paragraphs
    down — and its FIELDS through the census `fields_known` reads.

    THE PARSE IS OF THE RENDERED DOCUMENT, and the two halves that make that true
    rather than merely intended:

    * `jinja2 is ModuleNotFoundError under both gate interpreters` (measured
      again at this row's parent, `.venv/bin/python` and `python3`), so this
      cannot render and then parse. `_neutralise_refs` substitutes each `{{ … }}`
      for a placeholder SCALAR instead, which models the render exactly when
      every construct is a line-bounded reference whose output is one scalar.
    * that precondition is not assumed: `BLACKBOX_CONFIG` is a member of
      `LINE_READ_TEMPLATES`, so `test_templates_render_line_for_line` already
      refuses every construct that could do anything else — a filter, a call, a
      `{% for %}`, a multi-line expression — for this file as for the other six.

    At `5a` the substitution was a NO-OP — that config was token-free and carried
    no Jinja at all — and it was written anyway so that row `5b` could add
    `{{ vault_plex_token | default('') }}` to the sessions module without a guard
    standing in its way. THAT PREDICTION IS NOW SPENT AND IT HELD: `5b` added the
    reference and flipped no clause here. Row S1 of `5a`'s mutation battery was
    the control that said the substitution worked rather than merely existed;
    from `5b` on it is load-bearing on the shipped bytes, and the placeholder
    scalar is what this walk sees where the token is.

    THE LOADER IS `_StrictLoader` AND NOT `yaml.safe_load`, which is this row's
    own first cut being repaired: `safe_load` takes a DUPLICATED key and keeps
    the last one, while the pinned exporter refuses the same bytes at config load
    and exits — see that class for the measurement.

    `prober` IS PINNED HERE BECAUSE NOTHING AT RUNTIME PINS IT, and the sentence
    this paragraph replaces (DEC-294 charge 2) said the opposite: that blackbox
    "refuses a module without one at config-load", i.e. the loud rc=1 crash loop
    the census below exists for. That is FALSE, and filing the defect in the
    wrong bucket is the whole harm — it licenses a later reader to drop `probers`
    as redundant with a binary that checks nothing. Driven on the pinned image,
    each row a config and a live container (logs/builder-5a-r5-prober-premise.log):

        no `prober` key at all   --config.check rc=0   Running=true Restarts=0
        `prober: ""`             rc=0                  Running=true Restarts=0
        `prober: nonsense`       rc=0                  Running=true Restarts=0

    What breaks is the PROBE. `/probe?module=…` on those three answers HTTP 400
    `Unknown prober ""` with no `probe_*` series at all, so Prometheus records
    the target DOWN while both configs are valid and both processes are healthy
    — the SILENT join the paragraph above describes for module NAMES, one field
    down, and `probers` is its only reader. The control is what makes that
    readable rather than an everything-is-broken artefact: the same dead target
    under `prober: http` answers HTTP 200 and `probe_success 0`, a probe that RAN
    and failed, which is a different fact from one that could not be dispatched.

    THE OTHER HALF OF THE PIN IS SEMANTIC AND WAS ALWAYS TRUE. A module whose
    `prober` says `tcp` loads, dispatches, and answers 200 — a connect test that
    reports `probe_success 1` against a Plex that is listening and 500ing, green
    metrics for a broken server, which is the exact failure mode design §4.6
    exists to rule out. Nothing above touches that; `tcp` is a working module
    measuring the wrong thing, and `<absent>` is a module that cannot run.

    THE TLS DIFFERENTIAL IS THREE FIELDS AND NOT ONE, and this row's first cut
    got the reason wrong rather than merely getting the coverage short. It pinned
    `fail_if_not_ssl` alone and said that field protects certificate RENEWAL.
    That sentence is measurably FALSE on the pinned binary, driven against a
    CA-minted leaf whose `notAfter` is 2026-06-01
    (logs/critic-5a-tls-differential.log, re-run at this parent as
    logs/builder-5a-r2-tls-differential.log): against the expired host the
    proxied module reports `probe_success 0` WITH the field (E1) and equally 0
    WITHOUT it (E2), while `insecure_skip_verify: true` reports 1 (E3) — and all
    three report 1 against a valid cert (F1-F3), so E is a differential and not
    an everything-is-zero artefact. Renewal is therefore carried by
    `tls_config.insecure_skip_verify` and by nothing else.

    So each field is pinned for what it actually buys, and the third arm is a
    NEGATIVE:

    * `proxied_refuses_plain` — `fail_if_not_ssl: true` on the proxied module.
      What this really buys is the PLAIN-HTTP refusal: against `http://` the
      proxied module reads 0 with the field and 1 without it (G1/G2). Traefik
      carries a per-router http->https upgrade, so without it a probe would
      report the redirect target's health and call the TLS path green.
    * `cert_verified` — `tls_config.insecure_skip_verify` present and explicitly
      `False`. Present AND explicit, because the template spends four lines
      making this field load-bearing for renewal and a claim whose subject is a
      default has no line to red on: deleting the block (H2) is scored exactly
      like flipping it (H1).
    * `direct_accepts_plain` — the DIRECT module must NOT carry
      `fail_if_not_ssl` at all. This is the same differential killed from the
      other end and it is the arm nothing would have thought to write: the direct
      module probes `http://<plex>:32400/identity`, so the field that is correct
      one module down makes this one report `probe_success 0` FOR EVER (H3a=1,
      H3b=0) — a permanent "the origin is down" that no certificate, restart or
      Plex fix can clear.

    NOT PINNED, deliberately, and the line is meaning vs tuning. The census is
    complete rather than illustrative, because a partial list reads as a claim
    about the fields it omits: `timeout`, `method`, `valid_status_codes`,
    `preferred_ip_protocol`, `ip_protocol_fallback` and `follow_redirects` are
    every remaining field either module carries, and each one changes how
    expensive or how strict a probe is — knobs the operator may legitimately turn
    once real probe latency is on a graph (5e). Losing one changes a NUMBER;
    losing `prober`, or any of the three TLS arms above, changes what the number
    MEANS.

    THAT CENSUS IS NOW READ BY THE TEST — `fields_known`, DEC-286, and it is the
    half of "parses" this clause used to only claim. Two sentences above promise
    the reader models the process: that a document blackbox refuses at config
    load is a non-zero exit at start and, under `restart: unless-stopped`, the
    crash loop this repo has already paid for. `_StrictLoader` made that true of
    the SYNTAX. It is false of the FIELDS, because
    `prom/blackbox-exporter:v0.28.0` unmarshals into a Go struct and refuses a
    field it does not know, and no YAML parser refuses anything of the sort —
    driven against the pinned binary, each row the shipped bytes with one edit
    (logs/critic-5a-r2-parser-vs-process.log, re-driven here as
    logs/builder-5a-r3-{red,green}.log):

        `valid_status_code`, one character      rc=1  <- was GREEN at 45/45
        `tls_config` at MODULE level            rc=1  <- was GREEN at 45/45
        an unknown module field (`retries`)     rc=1  <- was GREEN at 45/45

    and under the first of those the WHOLE GATE printed `43/43` over a config
    that cannot start (logs/critic-5a-r2-gate-under-typo.log). So the pinned
    fields plus the census above are now a per-level allow-list
    (`BLACKBOX_{TOP,MODULE,HTTP,TLS}_FIELDS`, walked by
    `_blackbox_field_defects`), scored exactly like `keys_allowed` 40 lines up
    and `names_exact` in this very clause. A typo reds where the process would
    refuse to start, and it reds NAMING THE FIELD.

    AND `values_typed` IS THE OTHER HALF OF THAT SAME SENTENCE — DEC-291 charge
    1, and scoring only the NAMES left it open for a round. `unmarshals into a Go
    struct` is a claim about VALUES as much as about fields: a name the struct
    knows, given something it cannot decode, is the identical `Error loading
    config` and the identical crash loop. Measured on the same binary
    (logs/builder-5a-r4-census.log), each row the shipped bytes with one edit:

        `timeout: 5s` -> `5`, ONE CHARACTER          rc=1  <- was GREEN at 45/45
        `valid_status_codes: [200]` -> `200`         rc=1  <- was GREEN at 45/45
        `ip_protocol_fallback: maybe`                rc=1  <- was GREEN at 45/45
        `valid_status_codes: ["two hundred"]`        rc=1  <- was GREEN at 45/45
        `follow_redirects: 0`                        rc=1  <- was GREEN at 45/45

    and under the FIRST of those the whole gate printed `43/43` all over again
    (logs/critic-5a-r3-gate-under-timeout.log) — the same size of edit, and the
    same outage, as the typo that bought the census in the first place.

    THE PREDICATES ARE MEASUREMENTS AND NOT TYPE-SYSTEM REASONING, which is
    stated at the constants and repeated here because it is the part a later
    reader will be tempted to "tidy": `prober: 3`, `method: 7` and
    `preferred_ip_protocol: 4` all LOAD on the pinned binary, so the obvious
    `isinstance(v, str)` is a FALSE-RED three times over and the honest predicate
    only excludes containers. 49 documents at `--config.check`, both directions,
    at logs/builder-5a-r4-binary-probe{,2}.log.

    THE COST IS DECLARED, BECAUSE IT IS PAID BY THE NEXT ROW. This allow-list is
    the vocabulary of THIS document, not a copy of blackbox's schema, so a field
    the binary accepts and the census has not learned reds too: `min_version:
    TLS12` under `tls_config` LOADS on the pinned binary and reds here (D6), and
    so does the `headers:` that row `5b` must add to send `vault_plex_token`
    (L1). Neither is a trap — `5b` is already adding a member to
    `BLACKBOX_MODULES` for its module name, and this is the same one-line edit
    in the same commit, in the same direction: fail-closed, and it makes the
    census the thing that must move when the document does. THAT COST WAS PAID AT
    `5b`, EXACTLY AS DESCRIBED AND WITH ONE SURPRISE: `headers` entered the map as
    `_bb_string_map` in the same commit as the module that needs it, and the
    predicate is 23 measured documents rather than a struct tag
    (logs/builder-5b-headers-probe.log) — because the field is a trap in the
    OPPOSITE direction from the three named above. `headers: abc` is rc=1 where
    `prober: 3` LOADS, so `_bb_scalar` would have been a FALSE-ACCEPT over a
    crash loop, and the raw-scalar rule applies one level down to the map's
    values instead. A legal knob turned
    WITHIN the census stays green, and the value half is held to the same
    standard: `valid_status_codes: [200, 204]` (L2), `timeout: 1m30s`,
    `preferred_ip_protocol: ip5`, `method: GETT` and `valid_status_codes: []`
    all LOAD and all stay GREEN. That is what says this is a vocabulary and not
    a freeze — and `1m30s` is there because Go durations CONCATENATE, so the
    first predicate anyone writes reds a document the binary accepts.

    THE PRINT IS TOTAL OVER MALFORMED DOCUMENTS, which is a property of this
    clause and not a style note. Every field above is read through an
    `isinstance` gate and reported with an explicit `<absent>` /
    `<not a mapping>` sentinel, because a module whose `http:` is a SCALAR used
    to raise `AttributeError` out of the f-string — rc=1 with ZERO `FAIL` lines,
    the crashed-reader shape, which defeats this row's own promise that a red
    names the failing FIELD. Row P1 of the battery is that document.
    """
    text = _read(BLACKBOX_CONFIG)
    present = bool(text.strip())
    try:
        doc = yaml.load(_neutralise_refs(text), Loader=_StrictLoader)
        parse_error = None
    except yaml.YAMLError as exc:
        doc, parse_error = None, str(exc).splitlines()[0]
    parses = isinstance(doc, dict)
    modules = doc.get("modules") if parses else None
    mapping = isinstance(modules, dict)
    # `key=str` ON BOTH SORTS, for the reason `_blackbox_field_defects` states
    # at length: PyYAML hands back a `bool` for a module named `no:` and a
    # bare-`sorted` over mixed types is a `TypeError` — rc=1 naming nothing.
    # `not_http` needs it as much as `names` does, and nothing charged that one:
    # it is only silent today because the module that reproduces it happens to
    # carry `prober: http`.
    names = sorted(modules, key=str) if mapping else []
    names_exact = names == sorted(BLACKBOX_MODULES)
    not_http = sorted((
        name for name, mod in (modules or {}).items()
        if not isinstance(mod, dict) or mod.get("prober") != "http"
    ), key=str) if mapping else []
    probers = mapping and not not_http
    def _field(mapping_or_not, key):
        """Report `key` without ever assuming the container is a mapping.

        The sentinels are the point: `<absent>` and `<not a mapping>` are the two
        states a bare `.get()` chain collapses into `None` on its way to an
        `AttributeError`, and they are exactly what the reader needs to tell a
        deleted field from a malformed document.
        """
        if not isinstance(mapping_or_not, dict):
            return "<not a mapping>"
        return mapping_or_not.get(key, "<absent>")

    proxied = (modules or {}).get(BLACKBOX_PROXIED_MODULE) if mapping else None
    direct = (modules or {}).get(BLACKBOX_DIRECT_MODULE) if mapping else None
    proxied_http = proxied.get("http") if isinstance(proxied, dict) else None
    direct_http = direct.get("http") if isinstance(direct, dict) else None
    proxied_tls = proxied_http.get("tls_config") if isinstance(proxied_http, dict) else None
    proxied_refuses_plain = _field(proxied_http, "fail_if_not_ssl") is True
    cert_verified = _field(proxied_tls, "insecure_skip_verify") is False
    direct_accepts_plain = _field(direct_http, "fail_if_not_ssl") == "<absent>"
    tls_differential = proxied_refuses_plain and cert_verified and direct_accepts_plain
    unknown_fields, mistyped_fields = _blackbox_field_defects(doc)
    fields_known = not unknown_fields
    values_typed = not mistyped_fields
    ok = (
        present and parses and mapping and names_exact and probers
        and tls_differential and fields_known and values_typed
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {BLACKBOX_CONFIG.name} defines exactly the "
        f"{len(BLACKBOX_MODULES)} design-4.6 probe modules "
        f"(present={present}, parses={parses} "
        f"(error={parse_error!r}), modules_mapping={mapping}, "
        f"names_exact={names_exact} (found={names}, want={sorted(BLACKBOX_MODULES)}), "
        f"probers={probers} (not_http={not_http}), "
        f"proxied_refuses_plain={proxied_refuses_plain} "
        f"({BLACKBOX_PROXIED_MODULE}.http.fail_if_not_ssl="
        f"{_field(proxied_http, 'fail_if_not_ssl')!r}), "
        f"cert_verified={cert_verified} "
        f"({BLACKBOX_PROXIED_MODULE}.http.tls_config.insecure_skip_verify="
        f"{_field(proxied_tls, 'insecure_skip_verify')!r}), "
        f"direct_accepts_plain={direct_accepts_plain} "
        f"({BLACKBOX_DIRECT_MODULE}.http.fail_if_not_ssl="
        f"{_field(direct_http, 'fail_if_not_ssl')!r}), "
        f"fields_known={fields_known} (unknown={unknown_fields}), "
        f"values_typed={values_typed} (mistyped={mistyped_fields}))"
    )
    return ok


def test_blackbox_sessions_probe_carries_the_vault_token() -> bool:
    """Step-5b: the `/status/sessions` probe sends the VAULT token, and the file
    that carries it is not world-readable.

    THE SILENT FAILURE THIS CLAUSE EXISTS FOR, stated first because it is what
    makes every arm below a metric-level pin rather than a target-level one.
    Plex answers an unauthenticated `/status/sessions` with HTTP 401, and
    blackbox reports an auth rejection as HTTP 200 on `/probe` with
    `probe_success 0` — a probe that RAN and failed. So the TARGET READS UP
    either way and `up{job=…}` is 1 whether the token arrives or not. A misspelt
    header key is therefore invisible everywhere except in the value of
    `probe_success`, which is exactly the series `5c`'s job and design §5.3's
    alerts consume. That is a different fact from `5a`'s neighbouring shape — a
    module name no config defines is HTTP 400 with ZERO `probe_*` series — and
    the two must not be conflated when reading a red at 07:00.

    Hence `header_key`: the DISTINGUISHING config is the key NAME, and pinning
    "a headers block exists" would be green over `X-Plex-Token2`,
    `X_Plex_Token`, or the token sent as `Authorization` — three genuinely
    different headers that reach Plex as no credential at all.

    NOT "every other spelling", which is what this paragraph used to say and is
    measurably false in exactly one direction (DEC-302 charge 3). CASE is not a
    spelling difference on the wire: a config carrying `x-plex-token:` arrives at
    the origin as `X-Plex-Token` — Go's `Header.Set` canonicalises — and the
    probe reads `probe_success 1` against a recording origin
    (logs/builder-5b-r2-wire.log, driven beside a control that sends the
    canonical spelling and is byte-identical). The set equality below reds on
    that document anyway. That is kept, and it is a benign false-RED rather than
    a hole: it fails CLOSED, it is one casing of one key in a file whose every
    other line is pinned to a literal, and the alternative — a case-insensitive
    compare — would quietly accept a second header differing from this one only
    in case, which is the shape a token leaking to a second destination takes.
    `_credential_modules` DOES fold case, because the question it asks is
    "does this file carry a credential" and the answer there is the wire's.

    * `module_defined` / `header_key` — `BLACKBOX_SESSIONS_MODULE` exists in the
      PARSED document and its `http.headers` keys are exactly
      `[BLACKBOX_TOKEN_HEADER]`. Set equality, the fail-closed direction and the
      same idiom as `names_exact` and the field census: a second header is a
      one-line edit HERE, in the commit that adds it. That is deliberate — a
      second header on this module is the shape a token leaking to a second
      destination takes.
    * `token_from_vault` — the header's value is the SINGLE EXISTING vault
      spelling: `{{ vault_plex_token | default('') }}`, read from
      `PLEX_VAULT_KEY` so this clause and
      `test_plex_token_sourced_from_vault` cannot drift onto two different
      variables. The `| default('')` filter is pinned, not tolerated: it is what
      lets the repo-side wiring render and stay green before the operator has
      stored a value, which `env.j2:27-45` spends nineteen lines saying about
      this very variable. Without it an undefined vault key fails the render and
      every `just play` between now and then dies.
    * `single_vault_ref` — the only `vault_*` name anywhere in this template is
      that one. The row was cut with "do NOT add a second vault variable", and an
      arm that only checks the header line would be green over a second secret
      introduced three lines down.
    * `no_token_literal` — EVERY `X-Plex-Token:` line in the whole file is that
      reference, not just the one inside the sessions module. `token_from_vault`
      is scoped to the module block by construction, so a second header line
      under a DIFFERENT module — the obvious way a literal gets pasted in while
      debugging — is precisely what it cannot see.
    * `token_render_is_quoted` — and every such line renders the reference
      QUOTED. This arm replaces a SENTENCE, and it is narrower than the sentence
      was, because the measurement DEC-305 charge 1 forced came back narrower.
      18 YAML-significant token first characters x three spellings, through real
      ansible-core 2.21.1 into `prom/blackbox-exporter:v0.28.0 --config.check`,
      with the value read BACK OUT by a parser rather than eyeballed
      (`logs/builder-5b-r3-red.log` leg B, `logs/builder-5b-r3-quotestyle.log`).
      INTACT out of 18: double-quoted 16, single-quoted 17, BARE 4. Bare REFUSES
      the config on eleven first characters — under `restart: unless-stopped`
      that is the crash loop this role served for two weeks — and on three more
      (`&`, `#`, `!`) it loads at rc=0 carrying something that is not the token,
      which is a probe reporting `probe_success 0` for ever with no config error
      to read. The guard could not tell bare from quoted before this arm: the
      bare template was 47/47 GREEN (leg C).

      EITHER QUOTE STYLE, AND THE REASON IS THE SCOPE OF THE CLAIM RATHER THAN
      ANY DOCUMENT THIS BUYS. What the 18 rows separate is QUOTED from BARE, so
      that is what the arm may say; single-quoted at 17/18 and double at 16/18 do
      not differ by a row this arm could honestly rest on.

      AND IT BUYS NO DOCUMENT, WHICH IS THE CORRECTION DEC-309 CHARGE 2 FORCED.
      Round 3 argued the width here by saying the narrow spelling "would red the
      spelling that measured BEST". It would not: the suite reds the
      single-quoted template ANYWAY, `FAIL: 2/47`, and FIVE of the reds are this
      clause's own — `module_defined`, `header_key`, `token_from_vault`,
      `no_token_literal`, `header_prose_current` — while `token_render_is_quoted`
      is the one arm that says True (re-measured at this row's own parent,
      `logs/builder-5b-r4-charge2.log` leg B, the whole red line captured
      verbatim). The width is INERT on that template, and a sentence claiming
      otherwise is the `8784` class in the paragraph round 3 was sent to repair
      for being one.

      WHAT MAKES IT INERT is `_neutralise_refs`, and the cause is measured rather
      than plausible (`logs/builder-5b-r4-charge2.log` leg C): it substitutes
      `'<REF>'`, a SINGLE-quoted placeholder, so the single-quoted template
      becomes `X-Plex-Token: ''<REF>''` and THIS FILE's own parse of it is a
      PyYAML `ParserError` — "while parsing a block mapping" — which is why
      `module_defined` now PRINTS the parse error instead of reporting a broken
      document as a missing module. The binary, for its part, takes both renders
      at rc=0 with the token intact (leg A), so "measured best" remains true of
      the WIRE and is false only as a claim about this suite. Adopting the better
      spelling is a change to that helper, not to that line, and it is not this
      row's.

      AND QUOTING IS NOT A UNIVERSAL DEFENCE — that over-claim is exactly what
      charge 1 struck, and the template's paragraph now carries the two rows
      that falsify it. A `"` first character reproduces INSIDE the quotes
      (`X-Plex-Token: ""TOKEN"`) and the render is rc=1 `did not find expected
      key`, the document broken by the quoting meant to prevent it. A `\\` is the
      silent one: a YAML DOUBLE-quoted scalar processes escapes, so `\\P` is
      U+2029 and the config loads at rc=0 carrying a token that is NOT the
      operator's, while the bare and single-quoted spellings of that same token
      are intact. Filed as `task-1786195905-16ec` rather than fixed here,
      because the fix is a JSON-escaping filter and a SECOND filter is what
      `test_templates_render_line_for_line` refuses on a `LINE_READ_TEMPLATES`
      member — this row's own description's fence 1, with "do not flip a clause".

    THE READ IS A JOIN OF THE PARSE AND THE RAW TEXT, and it has to be. The
    parse is what proves the header sits under this module's `http:` and nowhere
    else; but `_neutralise_refs` replaces every `{{ … }}` with a placeholder
    scalar before the loader sees it, so the parsed value CANNOT carry the
    reference. The raw slice is taken from the same module's block
    (`_indented_key_lines` + `_block_under`), so the two halves are about one
    module rather than about the file in general.

    THE WORLD BIT IS THE SURVIVING INVARIANT, AND READABILITY IS NOT THE REASON.
    The premise this row was cut from said `prom/*` runs as `nobody`, so
    `0640 root:root` would be a crash loop and the door was `owner: 65534` /
    `0600`. That is measurably FALSE for this image and the premise is struck in
    `plan.md`: `Config.User` is EMPTY and `id -u` answers `{BLACKBOX_UID}`, and
    five owner/mode pairs mounted `:ro` into it — `65534:65534` 0640/0600,
    `root:root` 0640/0600/0644 — are READ=ok on ALL FIVE, because uid 0 bypasses
    the permission bits. There is no pair in this row's space the process cannot
    read, so a guard arming "the container could not read it" would assert
    something that never happens.

    What 0644 DOES do is publish a live Plex API token to every user on the
    docker host, and falsify a load-bearing sentence at
    `ansible/roles/docker_host/tasks/main.yml:118-122`: that the 0644 prometheus
    render "carries no credential … so world-read costs nothing". So:

    * `world_bit_withheld` — a PROPERTY of the mode, not the digits `0640`.
      `int(mode, 8) & 0o004` must be clear, so 0600 does not false-RED and 0644
      cannot pass. A SYMBOLIC mode (`u=rw,g=r`, which `ansible.builtin.template`
      accepts) reds rather than being invisible — see `_render_task_scalar`,
      which is why this clause does not carry a `\\d+` reader of its own.
    * `prom_carries_no_credential` — and this arm is aimed at row `5c`, not at
      today. `prometheus.yml.j2` is NOT touched by this row, and its
      carries-no-credential sentence is re-asserted as a CHECK: no `vault_*`
      reference, no `X-Plex-Token`, no `PLEX_TOKEN` in it. `5c` writes three
      scrape jobs against these modules, and the one thing it must not do is
      move the token into the 0644 file — which would be silently correct at
      runtime and would falsify the sentence that licenses that mode.

    * `prologue_loads` — THE HEADER READER'S STOP LINE, READ AS A DOCUMENT FACT,
      and it is here because the arm below cannot carry it. `_leading_comment_block`
      walks past the prologue the binary TAKES; every `%` line it will not walk
      past is one the binary REFUSES (seven measured rows, `_YAML_PROLOGUE`).
      Round 3 skipped the whole `%` family and turned `%YAML 1.2` — rc=1 "found
      incompatible YAML document", because go-yaml v3 is YAML 1.1 — from the RED
      the parent `1f29d08` printed into a GREEN (DEC-309 charge 1). Narrowing the
      skip list is half the repair; this arm is the other half, because the
      narrowing only reds a directive standing ABOVE the header. Put the same
      `%YAML 1.2` BELOW those 48 lines and the binary still refuses it at rc=1
      while the header parses, names the token and names the module, so
      `header_prose_current` reads TRUE over a config that cannot start
      (`logs/builder-5b-r4-legd.log`). One arm, both positions.

    * `header_prose_current` — the template's OWN HEADER, scored against the
      parsed document as a biconditional (DEC-302 charge 1). Round 1 shipped the
      token under a comment block that still called this file's contents "the
      TWO THAT NEED NO CREDENTIAL" and `/status/sessions` a future row 5b, in
      the commit whose own message gives "a clause named for two token-free
      probes must not print OK over a document carrying a live token" as its
      reason for renaming a clause. Nothing read those lines, so they rot
      silently, and `5c` — which the stale paragraph named — is a row that takes
      its `params.module` values from this file's neighbourhood.

      SO THE PROSE IS HELD TO THE DOCUMENT AND NOT TO A PHRASE. If any module
      carries the token header (`_credential_modules`, case-folded because the
      wire folds it), the header block must name `BLACKBOX_TOKEN_HEADER` and
      every such module BY NAME; if none does, it must not name the header at
      all. Both directions red: reverting the header to `5a`'s text reds with
      `unannounced=['plex_sessions']`, and deleting the module's `headers:`
      block reds the OTHER way on prose that now over-claims. Scoped to the
      LEADING comment block only — the per-module comments are attributions
      ("this module came from Step 5b"), which stay true for ever, and legislating
      over them would put a false-RED tripwire on legitimate prose, which is
      `task-1786173528-f7de`'s filed defect.

    ONE ARM NOBODY ASKED FOR, AND IT IS THE SAME DIFFERENTIAL KILLED FROM A THIRD
    END. `sessions_accepts_plain`: this module must NOT carry `fail_if_not_ssl`.
    Its target is plain HTTP to the Plex container on the compose network, so the
    field that is CORRECT on the proxied module makes this one report
    `probe_success 0` FOR EVER — a permanent "the origin is down" no certificate,
    restart or Plex fix can clear, and on THIS module it would be indistinguishable
    from the token being wrong, which is the one thing this clause exists to make
    visible. The direct module's identical arm lives in the clause above because
    each row pins the module it ships; what differs is the PREDICATE, and
    deliberately: that one spells the arm `== "<absent>"`, which false-REDs on
    `fail_if_not_ssl: false` — runtime-identical to absent on the real exporter,
    and filed as `task-1786184652-0a6a`. This arm is `is not True`, the spelling
    that filing recommends. Two spellings of one idea is normally the defect; here
    the older one is a KNOWN defect under a filed row that is not this row's to
    close, and re-spelling it would propagate the false-RED to a second module.

    NOT PINNED HERE, deliberately, because it is pinned better one clause over:
    the owner/group of this render. `RELOAD_CONTRACT` gained a `RENDER_OWNER`
    column at this row, walked by
    `test_rendered_configs_reach_the_service_that_reads_them` across all five
    renders — the `task-1786187620-633b` half that recorded none of them pinning
    an owner. Repeating it here would be the second-reader drift this file has
    already paid for; the constant's own comment carries the "readability is not
    the reason" sentence.
    """
    text = _read(BLACKBOX_CONFIG)
    # The parse error is KEPT AND PRINTED, the reading clause's treatment
    # (`parses=False (error=…)`), because without it `module_defined=False` reports
    # a whole-document `ParserError` as "this module is not defined" — a printed
    # reason false of a file whose module is right there. DEC-309 charge 2, and the
    # document that produces it is not hypothetical: the SINGLE-quoted spelling of
    # the token line makes this file's own `_neutralise_refs` output
    # `X-Plex-Token: ''<REF>''` (logs/builder-5b-r4-charge2.log leg C).
    try:
        doc = yaml.load(_neutralise_refs(text), Loader=_StrictLoader)
        parse_error = None
    except yaml.YAMLError as exc:
        doc, parse_error = None, str(exc).splitlines()[0]
    modules = doc.get("modules") if isinstance(doc, dict) else None
    sessions = modules.get(BLACKBOX_SESSIONS_MODULE) if isinstance(modules, dict) else None
    module_defined = isinstance(sessions, dict)
    sessions_http = sessions.get("http") if module_defined else None
    headers = sessions_http.get("headers") if isinstance(sessions_http, dict) else None
    # `key=str` for the reason the clause above states at length: PyYAML is YAML
    # 1.1, so a header spelled `on:` comes back as a `bool` and a bare `sorted`
    # over mixed types is a `TypeError` — rc=1 naming nothing, the crashed-reader
    # shape this row has grown three times.
    header_keys = sorted(headers, key=str) if isinstance(headers, dict) else []
    header_key = header_keys == [BLACKBOX_TOKEN_HEADER]
    fail_if_not_ssl = (
        sessions_http.get("fail_if_not_ssl", "<absent>")
        if isinstance(sessions_http, dict) else "<not a mapping>"
    )
    sessions_accepts_plain = fail_if_not_ssl is not True

    # The RAW half of the join: the sessions module's own block, so a header line
    # belonging to a different module cannot answer for this one.
    openers = _indented_key_lines(text, BLACKBOX_SESSIONS_MODULE)
    module_block = _block_under(text, openers[0]) if len(openers) == 1 else ""
    header_line = re.compile(
        rf'(?m)^[^\S\n]*{re.escape(BLACKBOX_TOKEN_HEADER)}:[^\S\n]*(\S.*?)[^\S\n]*$'
    )
    in_module = header_line.search(module_block)
    header_value = in_module.group(1) if in_module else None
    # The single existing spelling, `env.j2:46`, with its filter. This pattern
    # answers "which variable, with which filter" and NOT "quoted how" — the
    # quoting is a second fact with its own measurement and its own arm
    # (`token_render_is_quoted`), so a mutant that unquotes reds on the arm whose
    # sentence it falsifies rather than on this one.
    #
    # `"?` IS THE DOUBLE QUOTES AND THE BARE FORM, AND THAT IS THE WHOLE OF IT.
    # The comment here used to say the quotes were "OPTIONAL", which is false of
    # the single-quoted spelling — this pattern does not match it (DEC-309 charge
    # 2). Widening it would be inert anyway: on that template the document does
    # not reach this line, because `_neutralise_refs` has already made the parse
    # a `ParserError` and `module_defined` is the arm that reds, printing it.
    vault_reference = re.compile(
        rf'"?\{{\{{\s*{re.escape(PLEX_VAULT_KEY)}\s*\|\s*default\(\'\'\)\s*\}}\}}"?'
    )
    token_from_vault = bool(header_value) and vault_reference.fullmatch(header_value) is not None
    vault_refs = sorted(set(re.findall(r'\b(vault_\w+)\b', text)))
    single_vault_ref = vault_refs == [PLEX_VAULT_KEY]
    every_header_value = header_line.findall(text)
    literal_headers = [
        value for value in every_header_value
        if vault_reference.fullmatch(value) is None
    ]
    no_token_literal = bool(every_header_value) and not literal_headers
    # THE QUOTING IS A MEASUREMENT, so it gets an arm rather than a sentence.
    # EITHER quote style and not the double one alone, because the arm may claim
    # only what was measured: what the 18 rows separate is QUOTED from BARE
    # (4/18), not one quote style from the other. On EVERY token line, for
    # `no_token_literal`'s reason — a second header line under a different module
    # is how an unquoted one gets pasted in while debugging.
    unquoted_headers = [
        value for value in every_header_value
        if not (len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'")
    ]
    token_render_is_quoted = bool(every_header_value) and not unquoted_headers

    task = _render_task_block(_read(TASKS), BLACKBOX_CONFIG.name)
    mode_text = _render_task_scalar(task, "mode")
    mode_digits = (mode_text or "").strip('"\'')
    try:
        # Fails CLOSED: a mode this cannot read octally is reported as unpinned
        # rather than silently skipped.
        world_bit_withheld = not int(mode_digits, 8) & 0o004
    except ValueError:
        world_bit_withheld = False
    prom_leaks = _credential_spellings(_read(PROM_SCRAPE))
    prom_carries_no_credential = not prom_leaks

    # THE FILE'S OWN HEADER IS THE THIRD READER OF THIS FACT, and prose is where
    # it rots. Scored as a BICONDITIONAL against the parsed document, so it is
    # armed in both directions rather than being a phrase this clause requires.
    # WHOLE TOKENS, never substrings: the claim is "this name appears", and a
    # bare `in` is a claim about a FRAGMENT. `plex_sessions` renamed by appending
    # a suffix is not named by a header still saying `plex_sessions`, and one
    # renamed by dropping a character IS a substring of it — both green under
    # `in` and both red here (mem-1786173563-eb5c, met on the prose side).
    preamble, preamble_stop = _leading_comment_block(text)
    # AND THE STOP LINE IS A DOCUMENT FACT BEFORE IT IS A PROSE ONE. A `%` line
    # that reader will not walk past is a prologue the binary REFUSES (seven rows,
    # measured — `_YAML_PROLOGUE`), so this file would not start at all, and the
    # prose arm below cannot be the one to say so: the header ABOVE such a
    # directive is intact and reads true, which is exactly the position row
    # `logs/builder-5b-r4-legd.log` measures at rc=1.
    prologue_loads = not _is_yaml_directive(preamble_stop)
    credential_modules = _credential_modules(modules)
    preamble_names_header = re.search(
        rf"(?i)\b{re.escape(BLACKBOX_TOKEN_HEADER)}\b", preamble
    ) is not None
    unannounced = [
        name for name in credential_modules
        if re.search(rf"\b{re.escape(str(name))}\b", preamble) is None
    ]
    header_prose_current = (
        (preamble_names_header and not unannounced) if credential_modules
        else not preamble_names_header
    )

    # What the reader could not see is named as such. An empty block is a fact
    # about THIS READER — `names_the_header` and `unannounced` are then its
    # blindness rather than the file's prose, and saying so is the difference
    # between a red someone can act on and DEC-305 charge 2.
    preamble_note = (
        f"the reader stopped at {preamble_stop!r}" if preamble.strip() else
        f"AND THIS READER SAW NO HEADER AT ALL — it stopped at "
        f"{preamble_stop!r}, so the two facts after the colon are what it could "
        f"not read and not what the file says"
    )

    ok = (
        module_defined and header_key and token_from_vault and single_vault_ref
        and no_token_literal and token_render_is_quoted and sessions_accepts_plain
        and world_bit_withheld and prom_carries_no_credential
        and prologue_loads and header_prose_current
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {BLACKBOX_SESSIONS_MODULE} sends "
        f"{PLEX_VAULT_KEY} as the {BLACKBOX_TOKEN_HEADER} header and "
        f"{BLACKBOX_CONFIG.name} withholds it from the world "
        f"(module_defined={module_defined} (parse error={parse_error!r}), "
        f"header_key={header_key} "
        f"({BLACKBOX_SESSIONS_MODULE}.http.headers keys={header_keys}, "
        f"want=[{BLACKBOX_TOKEN_HEADER!r}]), "
        f"token_from_vault={token_from_vault} (value={header_value!r}), "
        f"single_vault_ref={single_vault_ref} (found={vault_refs}), "
        f"no_token_literal={no_token_literal} "
        f"({len(every_header_value)} {BLACKBOX_TOKEN_HEADER} line(s), "
        f"not the vault reference: {literal_headers}), "
        f"token_render_is_quoted={token_render_is_quoted} "
        f"(unquoted: {unquoted_headers} — over 18 YAML-significant token first "
        f"characters the value survives intact 16 times double-quoted and 17 "
        f"single-quoted but only 4 BARE: bare refuses the config on 11 and "
        f"loads at rc=0 carrying something other than the token on 3), "
        f"sessions_accepts_plain={sessions_accepts_plain} "
        f"({BLACKBOX_SESSIONS_MODULE}.http.fail_if_not_ssl={fail_if_not_ssl!r} — "
        f"true would be a permanent probe_success 0 against a plain-HTTP "
        f"target, indistinguishable from a rejected token), "
        f"world_bit_withheld={world_bit_withheld} (mode={mode_text!r} — 0644 "
        f"would publish a live Plex API token to every user on the docker host "
        f"and falsify the carries-no-credential sentence the prometheus render's "
        f"own 0644 rests on), "
        f"prom_carries_no_credential={prom_carries_no_credential} "
        f"({PROM_SCRAPE.name} leaks={prom_leaks}), "
        f"prologue_loads={prologue_loads} "
        f"(the header reader stopped at {preamble_stop!r} — a `%` prologue it "
        f"will not walk past is one this exporter REFUSES at rc=1, measured on "
        f"seven of them at {BLACKBOX_PROLOGUE_EVIDENCE}, and `restart: "
        f"unless-stopped` turns that into a crash loop; a `%YAML 1.2` BELOW this "
        f"header is the same rc=1 with the prose still reading true, so this arm "
        f"and not the one after it is where that document dies), "
        f"header_prose_current={header_prose_current} "
        f"({BLACKBOX_CONFIG.name}'s own header is "
        f"{len(preamble.splitlines())} line(s), {preamble_note}, and modules "
        f"carrying a credential are {credential_modules or 'NONE'}: "
        f"names_the_header={preamble_names_header}, unannounced={unannounced} — "
        f"a header that calls this file credential-free, or calls a module that "
        f"has LANDED a future row, is what {BLACKBOX_SESSIONS_MODULE} shipped "
        f"over), "
        f"runs_as_uid={BLACKBOX_UID} — readability is NOT what any mode here "
        f"buys, uid 0 bypasses the bits; measured at {BLACKBOX_UID_EVIDENCE})"
    )
    return ok


# The document a merge-key refactor of THIS row's two modules actually produces.
# Held as a constant because two clauses read it: the table below scores whether
# it is accepted, and `merge_resolves` scores what it RESOLVES TO.
BLACKBOX_MERGE_OVERRIDE = """modules:
  plex_identity_direct: &common
    prober: http
    timeout: 5s
    http:
      method: GET
  plex_identity_proxied:
    <<: *common
    timeout: 9s
    http:
      method: GET
"""

# (label, document, the PINNED BINARY's verdict, which half must refuse it).
#
# The verdict column is a MEASUREMENT and never a reading of the YAML spec: each
# row was driven through `prom/blackbox-exporter:v0.28.0 --config.check` at
# logs/builder-5a-r5-merge-door.log, and the `<<` rows disagree with what any of
# the three obvious implementations would predict.
BLACKBOX_READER_ROWS = (
    ("R1 plain document, no merge key",
     "modules:\n  plex_identity_direct:\n    prober: http\n    timeout: 5s\n",
     True, None),
    ("R2 the idiomatic dedup: an anchor and `<<:`",
     "modules:\n  plex_identity_direct: &c\n    prober: http\n    timeout: 5s\n"
     "  plex_identity_proxied:\n    <<: *c\n",
     True, None),
    ("R3 `<<:` plus an explicit override of a merged key",
     BLACKBOX_MERGE_OVERRIDE, True, None),
    ("R4 `<<: [*a, *b]`, a sequence of anchors",
     "modules:\n  a: &one\n    prober: http\n  b: &two\n    timeout: 5s\n"
     "  plex_identity_direct:\n    <<: [*one, *two]\n",
     True, None),
    ("R5 TWO `<<:` keys in one mapping",
     "modules:\n  a: &one\n    prober: http\n  b: &two\n    timeout: 5s\n"
     "  plex_identity_direct:\n    <<: *one\n    <<: *two\n",
     False, "loader"),
    ("R6 `<<:` beside a duplicated explicit key",
     "modules:\n  plex_identity_direct: &c\n    prober: http\n"
     "  plex_identity_proxied:\n    <<: *c\n    timeout: 5s\n    timeout: 9s\n",
     False, "loader"),
    ("R7 a duplicate INSIDE the merged anchor",
     "modules:\n  plex_identity_direct: &c\n    prober: http\n    prober: tcp\n"
     "  plex_identity_proxied:\n    <<: *c\n",
     False, "loader"),
    ("R8 `<<: 5`, a merge that cannot resolve",
     "modules:\n  plex_identity_direct:\n    <<: 5\n    prober: http\n",
     False, "loader"),
    ("R9 a duplicated key, no merge in sight",
     "modules:\n  plex_identity_direct:\n    prober: http\n    prober: tcp\n",
     False, "loader"),
    ("R10 an unhashable `? [a, b]` key",
     "? [a, b]\n: 1\nmodules:\n  plex_identity_direct:\n    prober: http\n",
     False, "loader"),
    ("R11 `<<:` at the top level, pulling in an unknown field",
     "x_defaults: &top\n  modules:\n    plex_identity_direct:\n"
     "      prober: http\n<<: *top\n",
     False, "census"),
)


def _blackbox_reader_verdict(text: str):
    """`None` if the gate's reader accepts `text`, else WHICH HALF refused it.

    The reader is the two steps `test_blackbox_modules_are_the_two_token_free_
    probes` performs on the rendered config, in that order and with the same
    `_neutralise_refs` in front, because a reader assembled differently here
    would be a third parser of the same document rather than a test of the one
    that ships.
    """
    try:
        doc = yaml.load(_neutralise_refs(text), Loader=_StrictLoader)
    except yaml.YAMLError:
        return "loader"
    if not isinstance(doc, dict):
        return "not a mapping"
    unknown, mistyped = _blackbox_field_defects(doc)
    return "census" if (unknown or mistyped) else None


def test_the_blackbox_reader_refuses_exactly_what_the_exporter_refuses() -> bool:
    """Step-5a, DEC-294 charge 1: the gate's reader, scored in BOTH directions.

    `_StrictLoader` exists because `yaml.safe_load` ACCEPTS documents the pinned
    exporter refuses, and its own docstring states the rule it was built to keep:
    a parser that accepts documents the process refuses is not modelling the
    process. THE CONVERSE BREAKS THE SAME SENTENCE, and it broke it here. The two
    modules share five of seven `http` fields, so the idiomatic dedup is an
    anchor and a `<<:` merge key — `--config.check` rc=0, the exporter starts on
    it — and the shipped loader printed `parses=False (error="could not determine
    a constructor for the tag 'tag:yaml.org,2002:merge'")`. A REGRESSION against
    the loader it replaced, since `yaml.safe_load` takes that document, and a red
    that lies about what broke: it names the document when the reader is what is
    wrong. Row `5b` adds a THIRD module sharing these fields, which is exactly
    when someone reaches for an anchor.

    So this clause is not "test the test". It is the ROUND'S OWN GENERALISATION
    applied to its own reader — *a door proved against a REFUSES list is half a
    door* — turned into the thing that reds when the next tightening forgets it.
    Every verdict below was driven through `prom/blackbox-exporter:v0.28.0
    --config.check` (logs/builder-5a-r5-merge-door.log); none of it is a reading
    of the YAML spec, and three rows are why that distinction is not pedantry.

    THE REPAIR IS ONE `continue` AND THE OBVIOUS ONE IS A TRAP, measured before
    it was written. `loader.flatten_mapping(node)` ahead of the scan is what
    anyone writes first; PyYAML PREPENDS the merged pairs to `node.value`, so a
    key that is both merged AND explicitly overridden — the entire point of a
    merge key — is seen twice and reds as `duplicate key 'timeout'`. R3 is that
    document. The door that holds is to step over the merge-TAGGED key node and
    let `SafeConstructor.construct_mapping` do the flattening it already does.

    R5 IS THE ROW THAT PROVED THE PROVED DOOR SHORT, and it is the reason this
    table has ten rows rather than the five that came with the charge. `<<` is
    still a mapping KEY, so a mapping carrying it twice is
    `mapping key "<<" already defined at line 7` on the binary — rc=1, the crash
    loop — while a door that merely skips every merge-tagged node parses it
    happily. The duplicate refusal this whole class exists for was about to be
    given up for exactly the key the repair was reaching over. So the scan skips
    the merge node's CONSTRUCTION and not its BOOKKEEPING: `<<` enters `seen`
    under the spelling the binary's own refusal prints.

    R6-R10 ARE THE REFUSALS THE CLASS WAS WRITTEN FOR, kept: a duplicate beside a
    merge, a duplicate inside the merged anchor, an unresolvable `<<: 5` (which
    `flatten_mapping` raises as a `ConstructorError`, i.e. still a
    `yaml.YAMLError`, so the reader fails CLOSED and in the currency the reading
    clause catches), a duplicate with no merge in sight, and the unhashable
    complex key.

    AND THE SOURCE COLUMN IS LOAD-BEARING, not decoration. R11 is refused by the
    binary too, and for a reason that has nothing to do with merges: the merged
    document carries `x_defaults` at the top level and this exporter unmarshals
    strictly. `_blackbox_field_defects` is what must red it, NOT the loader —
    scoring only "did something refuse" would let the two halves swap roles
    silently, which is the way a tightening of one usually quietly loosens the
    other. That is the same both-halves discipline `_StrictLoader`'s own closing
    paragraph draws between SYNTAX and FIELDS.

    `merge_resolves` is the last arm and it is about SEMANTICS rather than
    acceptance: a door that skipped merges without flattening them would parse
    R3 and hand the reading clause a module with no `prober` at all. So the
    resolved module is asserted whole — the merged key present, the overridden
    one taking the EXPLICIT value, which is the precedence go-yaml applies too.
    """
    offenders = []
    for label, text, loads, refused_by in BLACKBOX_READER_ROWS:
        got = _blackbox_reader_verdict(text)
        if (got is None) != loads:
            offenders.append(
                f"{label}: binary={'LOADS' if loads else 'REFUSES'}, "
                f"reader={got or 'accepts'}")
        elif got is not None and got != refused_by:
            offenders.append(f"{label}: refused by {got!r}, want {refused_by!r}")
    try:
        resolved = yaml.load(BLACKBOX_MERGE_OVERRIDE, Loader=_StrictLoader)
        merged_module = resolved["modules"][BLACKBOX_PROXIED_MODULE]
    except Exception as exc:                       # noqa: BLE001 - reported, not raised
        merged_module = f"<{type(exc).__name__}>"
    merge_resolves = merged_module == {
        "prober": "http", "timeout": "9s", "http": {"method": "GET"},
    }
    ok = not offenders and merge_resolves
    print(
        f"{'OK' if ok else 'FAIL'}: the gate's {BLACKBOX_CONFIG.name} reader "
        f"refuses exactly what the pinned exporter refuses "
        f"(rows={len(BLACKBOX_READER_ROWS)}, offenders={offenders}, "
        f"merge_resolves={merge_resolves} (resolved={merged_module}))"
    )
    return ok


def test_blackbox_scrape_jobs_probe_plex() -> bool:
    """Step-5c: three `/probe` jobs, each a REFERENCE to something that exists.

    Design §4.6's probes, and the row's whole difficulty is that almost every
    coordinate here is already spelled somewhere else in the repo — the module
    names in `blackbox.yml.j2`, the LAN address in this role's defaults, the
    public hostname in `dynamic.yml.j2`'s router rule, the exporter's port in the
    image. A job that re-types any of them is "two literals that agree until one
    moves", which is the class this objective charged three times in Step 4
    alone. So every pin below is a RELATION, and the constants it reads are the
    ones the OTHER end is already held to.

    * `parses` — `prometheus.yml.j2` loads as YAML through `_neutralise_refs`,
      the same `_StrictLoader` the blackbox reader uses. It is here because this
      row is the one that makes it interesting: two of the three targets START
      with a Jinja reference, and the placeholder is a single-quoted scalar, so
      an UNQUOTED `{{ docker_host_plex_url }}/identity` is a `ParserError` while
      an unquoted `https://plex.{{ domain }}/identity` is fine — measured at this
      row's hands (logs/builder-5c-target-spellings.log) with the pve target as
      the control. THE DISCRIMINATOR IS THE VALUE'S FIRST CHARACTER, NOT THE
      CONCATENATION, and that matters because the comment at :129-135 of the
      template generalises its own case the other way ("it is the only one that
      CONCATENATES") — true of that line, false as a rule, and the proxied target
      is the counterexample. Nothing renders this template as YAML in production
      (Jinja runs first), so what this arm buys is that the guard's own readers
      are looking at the document they think they are.
    * `route_is_one_host` — the proxied target's host is READ OUT of
      `dynamic.yml.j2`'s `plex` router rule (`_rule_hosts`), not typed here. That
      rule is the definition of the public path this probe exists to measure, so
      a `Host()` change moves the probe with it; a rule this guard cannot read
      fails CLOSED to the empty set and reddens rather than comparing nothing.
    * `names_are_the_shipped_fan_in` — THE FAR END THAT WAS MISSING AT `5c` AND
      LANDED AT `7a` (`task-1786203094-588c`, closed by this clause). Until Step 7
      existed there was no live document selecting on these names, so the clause
      pinned that all three carried `BLACKBOX_JOB_PREFIX` — and that was a
      TAUTOLOGY, because `BLACKBOX_JOBS`' keys are f-strings BUILT from that
      prefix. `all(job.startswith(PREFIX))` is True by construction and printed
      True under every mutant: renaming all three jobs off design §5.3's prefix
      in the template AND the constant together was `PASS: 50/50`
      (`logs/critic-5c-arms.log` C1).

      What replaced it reads the `job=~` patterns OUT OF `plex-blip-rules.yml.j2`
      — the rules this stack actually ships — and requires every name in
      `BLACKBOX_JOBS` to be `re.fullmatch`ed by one of them. Both ends now move
      or the pair reddens, and it fails CLOSED twice over: no `job=~` in the rules
      file at all is `shipped_fan_in == []` and RED rather than a vacuous `all()`
      over nothing, and a pattern that does not compile is the same.

      NOT the same relation as `regex_job` in
      `test_plex_blip_alert_rules_are_design_5_3`, which faces the other way: that
      one holds the RULES FILE to the scrape config (a regex fanning in to the
      wrong set), this one holds the SCRAPE CONFIG to the rules (a job renamed out
      of the alert's reach). C1 renames both ends of `regex_job` together and
      stays green there; here it reddens.
    * `modules_exhaust_the_config` — the `module=` values the three jobs carry,
      taken together, are exactly `BLACKBOX_MODULES`. THE JOIN NOTHING AT RUNTIME
      CHECKS: a job naming a module `blackbox.yml` does not define gets HTTP 400
      from `/probe` — the target reads DOWN, no `probe_*` series exist, and
      NEITHER config is invalid. Set equality rather than three memberships,
      because the other direction is a module `5a`/`5b` defined and nothing
      probes: a probe configured, deployed, and never taken.
    * per-job `module` — and this one is about PAIRING rather than existence. All
      three names could be present with `/status/sessions` probed by
      `plex_identity_direct`, which sends no token: Plex answers 401, blackbox
      reports HTTP 200 with `probe_success 0`, and the target reads UP the whole
      time. So each job's module is pinned against its own row of the table.
    * per-job `metrics_path` — `/probe`. blackbox also serves `/metrics`, its own
      process metrics, so the DEFAULT path answers 200 with a page full of
      `blackbox_*` and zero `probe_*`: the target reads UP and the dashboard is
      empty. That is the `pve-exporter` lesson (`path_pinned`) in its third
      variant, and it has no `path_is_not_default` twin because the two paths are
      different ENDPOINTS rather than a value and its default — there is no
      "write the default out explicitly" no-op for this pin to be satisfied by.
    * per-job `target` — exactly one, and it is a reference. The two direct
      probes carry `{{ docker_host_plex_url }}` with a path suffix, so
      retargeting that variable moves both; the proxied one is
      `https://` + the router's own host + `/identity`. The list is compared
      whole (`== [want]`), not searched, because a SECOND entry under
      `static_configs` is scraped too — Step-2a F1 round 9 measured that exact
      shape loading a caller-chosen host into a multi-target exporter, and
      `/probe` is a multi-target exporter that will dial anything it is given.
    * per-job `relabel_configs` — the triplet, per hop, via `_relabel_triplet`;
      which hop is missing is in the defect text. The `keep` hop is the silent
      one and the reason that helper exists: without it the probes still run and
      all three land on one `instance` label — the exporter's — so design §4.6's
      whole differential reads as one line. Since DEC-316 the read is of the
      LIST and not of three memberships: a fourth entry, and a field beside the
      copy inside a hop, are both defects here, because each one leaves a config
      `promtool` accepts while the probe goes somewhere the file does not name.
      That helper's docstring holds the measurements and the one price.
    * per-job `keys_allowed` — `BLACKBOX_JOB_KEYS`. What it keeps out is a
      credential: `basic_auth:`, `authorization:` and `bearer_token_file:` are
      ordinary scrape-config keys and every one of them would put a secret into
      the 0644 render that `test_prometheus_render_is_world_read_only_unpaid`
      forbids. An allow-list rather than an absence pin, for the reason
      `PLEX_JOB_KEYS` gives: an absence pin fails OPEN one key past its edge.
    """
    body = _read(PROM_SCRAPE)
    try:
        doc = yaml.load(_neutralise_refs(body), Loader=_StrictLoader)
        parse_error = None
    except yaml.YAMLError as exc:
        doc, parse_error = None, str(exc).splitlines()[0]
    parses = isinstance(doc, dict)
    proxied_hosts = sorted(_rule_hosts(
        _router_rule(_router_block(_read(DYNAMIC), DYNAMIC_PLEX_ROUTER))
    ))
    route_is_one_host = len(proxied_hosts) == 1
    try:
        shipped_fan_in = sorted({
            p for p in re.findall(
                PLEX_BLIP_EXPR_READERS["regex_job"], _read(PROM_RULES)
            ) if re.compile(p)
        })
    except re.error:
        shipped_fan_in = []
    unselected = sorted(
        job for job in BLACKBOX_JOBS
        if not any(re.fullmatch(p, job) for p in shipped_fan_in)
    )
    names_are_the_shipped_fan_in = bool(shipped_fan_in) and not unselected
    defects, found_modules, hops_by_job = {}, [], {}
    for job, spec in BLACKBOX_JOBS.items():
        block = _scrape_job_block(body, job)
        if not block.strip():
            defects[job] = ["does not resolve exactly once inside scrape_configs:"]
            continue
        bad = []
        path = _block_scalar(block, "metrics_path")
        if path != BLACKBOX_PROBE_PATH:
            bad.append(
                f"metrics_path={path!r}, want {BLACKBOX_PROBE_PATH!r} — the "
                "default serves the exporter's OWN metrics, so the target reads "
                "UP with zero probe_* series"
            )
        modules = _param_values(
            _indented_block(block, "params"), BLACKBOX_PARAM_MODULE
        )
        found_modules += modules
        if modules != [spec["module"]]:
            bad.append(
                f"params.{BLACKBOX_PARAM_MODULE}={modules}, want "
                f"[{spec['module']!r}] — /probe answers HTTP 400 for a module "
                f"{BLACKBOX_CONFIG.name} does not define, and the WRONG defined "
                "module probes the right URL with the wrong method or credential"
            )
        targets = [_yaml_unquote(t) for t in _static_targets(block)]
        if spec["proxied"] and not route_is_one_host:
            bad.append(
                f"{DYNAMIC.name}'s {DYNAMIC_PLEX_ROUTER} router pins "
                f"{proxied_hosts} — this target has no single far end to follow"
            )
        else:
            want = (
                f"{PROXIED_SCHEME}{proxied_hosts[0]}{spec['path']}"
                if spec["proxied"] else f"{PLEX_URL_REF}{spec['path']}"
            )
            if targets != [want]:
                bad.append(f"targets={targets}, want [{want!r}]")
        triplet_defects, hops = _relabel_triplet(block, BLACKBOX_ADDRESS)
        hops_by_job[job] = hops
        bad += triplet_defects
        keys, unreadable = _service_key_lines(block)
        extra = [k for k in keys if k not in BLACKBOX_JOB_KEYS]
        if extra or unreadable:
            bad.append(f"keys outside the allow-list: {extra}, unreadable: {unreadable}")
        if bad:
            defects[job] = bad
    modules_exhaust_the_config = sorted(found_modules) == sorted(BLACKBOX_MODULES)
    ok = (
        parses and route_is_one_host and names_are_the_shipped_fan_in
        and modules_exhaust_the_config and not defects
    )
    print(
        f"{'OK' if ok else 'FAIL'}: the {len(BLACKBOX_JOBS)} {BLACKBOX_SERVICE} "
        f"jobs probe Plex by reference (parses={parses} (error={parse_error!r}), "
        f"route_is_one_host={route_is_one_host} ({DYNAMIC.name} "
        f"{DYNAMIC_PLEX_ROUTER} router hosts={proxied_hosts}), "
        f"names_are_the_shipped_fan_in={names_are_the_shipped_fan_in} "
        f"({PROM_RULES.name} selects on {shipped_fan_in}; unselected="
        f"{unselected}), modules_exhaust_the_config="
        f"{modules_exhaust_the_config} (jobs name={sorted(found_modules)}, "
        f"{BLACKBOX_CONFIG.name} defines={sorted(BLACKBOX_MODULES)}), "
        f"dialled_at={BLACKBOX_ADDRESS!r}, hops={hops_by_job}, defects={defects})"
    )
    return ok


def test_blackbox_scrape_cadence_is_what_prometheus_runs() -> bool:
    """Step-5c: the interval/timeout pair of each probe job, read EFFECTIVELY.

    Step 4d built this instrument (`_effective_scrape_pair`, `_duration_seconds`,
    `PROM_DEFAULT_SCRAPE_TIMEOUT`) and this row is its second user rather than a
    second spelling of it. Four fields, and they close four different doors:

    * `interval_is_job_local` — each job sets its OWN `scrape_interval`. SEPARATE
      from the cadence pin below and neither can do the other's job: `global` is
      15 s, so DELETING the key on the two 15 s jobs leaves the effective read at
      15.0 and every other field here GREEN, while a later change to the global
      interval silently coarsens two probes whose whole purpose is resolution.
      That is `task-1786170786-3fb1`, met one job over at 4d.
    * `cadence_matches_design` — 15 s / 60 s / 15 s, design §4.6. `/identity` is
      unauthenticated and does no database work, so 15 s costs Plex essentially
      nothing (R8); `/status/sessions` touches session state and is deliberately
      the rare one. THIS FIELD SHADOWS THE NEXT ONE and saying so is part of the
      claim: it is a DIGIT contract, so the obvious mutant for `timeout_fits` —
      dropping an interval below its timeout — reds here too, and a criterion
      driven only that way would not tell the two apart. The arm that isolates
      `timeout_fits` moves the TIMEOUT instead (sessions to 90 s, interval
      untouched); both rows are at logs/builder-5c-arms.log.
    * `timeout_fits` — the EFFECTIVE timeout does not exceed the EFFECTIVE
      interval. `<=` AND NOT THE `<` plan.md:348 ASKS FOR, and this row measured
      the boundary rather than citing the template comment that already says so:
      `promtool check config` on prom/prometheus:v3.12.0, one job at a 60 s
      interval — 59 s rc=0, 60 s rc=0, 61 s rc=1 "scrape timeout greater than
      scrape interval" (logs/builder-5c-timeout-boundary.log). Equality LOADS, so
      a `<` here would be a guard forbidding a config the runtime accepts. When
      it is violated Prometheus refuses the WHOLE file, so every job in it stops
      — including the four this row did not touch.
    * `module_timeout_binds` — THE FIELD THAT IS NOT ABOUT THIS FILE. blackbox
      clamps each probe to Prometheus' own scrape-timeout header minus
      `--timeout-offset` (0.5 s), so the module's `timeout:` is a ceiling and the
      SCRAPE timeout is what actually binds — `blackbox.yml.j2` says exactly that
      at :56-59 and :144-147, and both sentences are claims about numbers that
      live HERE. `plex_sessions` is where it bites: its 30 s is argued at length
      against the 5 s `probe_duration_seconds` alert of design §4.6, because "a
      timeout AT the alert threshold clips the measurement exactly where it
      becomes interesting". Left on Prometheus' 10 s default, that 30 s is a
      value nothing can reach — every stall recorded as a 9.5 s failure, no
      config invalid, nothing to read anywhere. The two 15 s jobs are the other
      direction and they are why the read must be EFFECTIVE: they set no
      `scrape_timeout` at all, so the pair being compared is 10.0 s from
      `PROM_DEFAULT_SCRAPE_TIMEOUT` against a 5 s module, and a clause reading
      `None` there would be comparing a pair the process does not use.

      It is a ONE-DIRECTION relation on purpose. A scrape timeout far ABOVE the
      module's is not a defect — the module still stops itself at its own value —
      so the pin is that the module's number is REACHABLE, not that the two agree.
    """
    body = _read(PROM_SCRAPE)
    try:
        modules = (yaml.load(
            _neutralise_refs(_read(BLACKBOX_CONFIG)), Loader=_StrictLoader
        ) or {}).get("modules")
    except yaml.YAMLError:
        modules = None
    defects, measured = {}, {}
    for job, spec in BLACKBOX_JOBS.items():
        block = _scrape_job_block(body, job)
        if not block.strip():
            defects[job] = ["does not resolve exactly once inside scrape_configs:"]
            continue
        pair = _effective_scrape_pair(body, block)
        module = (modules or {}).get(spec["module"]) if isinstance(modules, dict) else None
        module_timeout = _duration_seconds(
            module.get("timeout") if isinstance(module, dict) else None
        )
        measured[job] = {
            "interval": pair["interval"], "timeout": pair["timeout"],
            "job_interval": pair["job_interval"], "job_timeout": pair["job_timeout"],
            f"{spec['module']}.timeout": module_timeout,
        }
        bad = []
        if pair["job_interval"] is None:
            bad.append(
                "no job-local scrape_interval — the effective read follows "
                f"global ({pair['global_interval']}s) and a change there "
                "coarsens this probe silently"
            )
        if pair["interval"] != spec["interval"]:
            bad.append(
                f"effective interval {pair['interval']}s, design 4.6 gives this "
                f"probe {spec['interval']}s"
            )
        if pair["interval"] is None or pair["timeout"] > pair["interval"]:
            bad.append(
                f"scrape_timeout {pair['timeout']}s EXCEEDS scrape_interval "
                f"{pair['interval']}s — Prometheus refuses the whole file, so "
                "every job in it stops (measured: 61s vs 60s is rc=1, 60s vs 60s "
                "is rc=0, logs/builder-5c-timeout-boundary.log)"
            )
        if module_timeout is None:
            bad.append(
                f"{BLACKBOX_CONFIG.name}'s {spec['module']} declares no timeout "
                "this reader can resolve, so nothing here can be compared to it"
            )
        elif pair["timeout"] - BLACKBOX_TIMEOUT_OFFSET < module_timeout:
            bad.append(
                f"the effective scrape timeout {pair['timeout']}s minus "
                f"blackbox's --timeout-offset {BLACKBOX_TIMEOUT_OFFSET}s is "
                f"below {spec['module']}'s own {module_timeout}s — that module "
                "timeout is a value nothing can reach, and every stall past "
                f"{pair['timeout'] - BLACKBOX_TIMEOUT_OFFSET}s is recorded as a "
                "failure at that number rather than as its real duration"
            )
        if bad:
            defects[job] = bad
    ok = not defects
    print(
        f"{'OK' if ok else 'FAIL'}: the {len(BLACKBOX_JOBS)} probe jobs run at "
        f"design 4.6's cadence with a timeout their module can reach "
        f"(default_timeout={PROM_DEFAULT_SCRAPE_TIMEOUT}s, "
        f"timeout_offset={BLACKBOX_TIMEOUT_OFFSET}s, measured={measured}, "
        f"defects={defects})"
    )
    return ok


def test_prometheus_rule_files_names_the_render() -> bool:
    """Step-7a: `rule_files:` is a LITERAL path and it is THIS role's render.

    Prometheus evaluated nothing at all before this row — `rule_files` is zero
    hits across `ansible/` at `2e8280c` — so the key arriving is the whole of the
    change, and the two ways it can arrive wrong are opposites.

    * `key_present` / `entries_readable` — the key exists at the document root
      and every entry is a SCALAR. Fails closed on a flow collection or a block
      mapping, which `_rule_files_entries` returns as `None` rather than dropping.

    * `all_literal` — NO entry carries a glob metacharacter. This is the pin the
      acceptance asks for by name, and the reason is measured rather than
      stylistic (`PROM_RULES_LITERAL_EVIDENCE`, five `promtool` legs on the pinned
      `prom/prometheus:v3.12.0`, each direction with its own control): a glob
      matching ZERO files is rc=0 `is valid prometheus config file syntax` with
      the `SUCCESS: N rule files found` line simply ABSENT (leg C2, control C3
      being the same glob with the file present), while a literal path that does
      not exist is rc=1 `does not point to an existing file` (leg C, control B).
      A render that fails to land is therefore invisible or loud purely as a
      function of this one spelling, and this row ships the loud one.

      SAID EXACTLY AS FAR AS IT WAS MEASURED, because the acceptance also forbids
      a clause stronger than its evidence: the loudness is `promtool`'s and NOT
      the running process's. Driven live (`PROM_RULES_DELIVERY_EVIDENCE`, rows
      D5b/D6), a literal naming a missing file and a glob over an empty directory
      are the SAME container — `running restarts=0`, `Completed loading of
      configuration file`, `/api/v1/rules` -> `{"groups":[]}`. So this pin buys a
      validator's exit code and nothing else until `7c` runs one before the
      restart handler fires; it is a precondition for that row, not a substitute.

    * `names_the_render` — the entries are EXACTLY the container-side paths this
      role's rule renders are mounted at, derived through `_bind_mount_target`
      from each render task's own `dest`. Set equality in both directions and
      that is the point: a subset would let `rule_files:` ask for a file nothing
      renders (rc=1 at `promtool`, `groups: []` live), and a superset would let a
      render land somewhere the config never asks about (silent — leg C2's shape
      without even needing a glob). One relation, spelled once; the far end is
      `RELOAD_CONTRACT`'s `named_in` hop reading this same list.

    NOT CLAIMED HERE: that any of these alerts can FIRE. Four of the seven cannot
    match an absent series at all — `absent()` is the door and it is measured at
    the wave cut, not here — and `7b` is the row that owns it. A clause asserting
    otherwise would be the sentence-stronger-than-its-guard class this objective
    has charged repeatedly.
    """
    prom, tasks, compose = _read(PROM_SCRAPE), _read(TASKS), _read(COMPOSE)
    entries = _rule_files_entries(prom)
    key_present = bool(entries)
    entries_readable = all(e is not None for e in entries)
    globbed = sorted(
        e for e in entries
        if e is not None and any(c in e for c in PROM_RULES_GLOB_CHARS)
    )
    all_literal = not globbed
    rendered = {}
    for src, row in RELOAD_CONTRACT.items():
        if row.get("named_in") != PROM_SCRAPE:
            continue
        task = _render_task_block(tasks, src)
        dest = re.search(r'(?m)^\s*dest:\s*(\S.*?)\s*$', task)
        rendered[src] = _bind_mount_target(
            _compose_service_block(compose, row["service"]), dest.group(1)
        ) if dest else None
    want = {t for t in rendered.values() if t is not None}
    names_the_render = (
        bool(want) and all(t is not None for t in rendered.values())
        and entries_readable and set(entries) == want
    )
    ok = key_present and entries_readable and all_literal and names_the_render
    print(
        f"{'OK' if ok else 'FAIL'}: {PROM_SCRAPE.name}'s {PROM_RULES_KEY}: is a "
        f"literal path naming this role's render (key_present={key_present}, "
        f"entries={entries}, entries_readable={entries_readable}, "
        f"all_literal={all_literal} (glob metacharacters "
        f"{PROM_RULES_GLOB_CHARS!r}; globbed={globbed} — a glob matching zero "
        f"files is promtool rc=0 with the 'N rule files found' line absent, "
        f"measured with its control at {PROM_RULES_LITERAL_EVIDENCE}), "
        f"names_the_render={names_the_render} (renders mounted at {rendered}))"
    )
    return ok


def test_plex_blip_alert_rules_are_design_5_3() -> bool:
    """Step-7a: the seven alerts of design §5.3, and every coordinate RESOLVES.

    The alert set is the design's (`design/detailed-design.md:583-605`) and it is
    pinned as an ORDERED sequence with each `expr:` and each `for:`, so a rule
    silently dropped — `PlexWatchdogProbeBroken` above all, the meta-guard that
    exists because a diagnostic tool failed silently for 34 runs — reddens rather
    than shrinking a count nobody reads.

    THE `expr` BODIES ARE HELD LITERALLY, and the argument two paragraphs down is
    exactly why. An alert loads at `promtool` rc=0 and fires never whether its
    `job=` names nothing OR its threshold is a thousand times too high, and both
    are indistinguishable from an alert with nothing to say. Round 1 applied that
    sentence to four COORDINATES and not to the table, and eight mutants —
    `PlexWatchdogProbeBroken` inverted to `== 1`, `PlexProbeSlow` raised to
    `> 500`, `[5m]` widened to `[500m]`, `event_type` respelled to `eventtype` —
    were `PASS: 54/54` past every reader below, past `promtool` and past three
    live containers. `PLEX_BLIP_ALERTS` now carries the exprs; the write-up and
    the measurements are on that constant.

    THE EXPRS' COORDINATES ARE STILL READ AGAINST THEIR FAR ENDS, and that is not
    made redundant by the literal column: the literal holds the rules file to
    ONE agreed text, while the readers hold that text to the REST OF THE STACK,
    so renaming a `job_name:` in `prometheus.yml.j2` or a metric family in the
    watchdog source reddens here even when both sides of a rename look tidy and
    nobody touched this file. Each is read against its far end rather than
    spelled a second time:

    * `exact_job` — every `job="X"` is a `job_name:` under `scrape_configs:` in
      `prometheus.yml.j2`.
    * `regex_job` — `job=~"blackbox-plex.*"` is stronger than membership: the set
      of this file's job names that the regex matches must EQUAL `BLACKBOX_JOBS`.
      This is the half `prometheus.yml.j2`'s own 5c comment deferred in writing —
      "Step 7 does not exist yet, so the guard pins the shared blackbox-plex
      prefix and says so" — and it closes in both directions: a fourth
      `blackbox-plex-*` job silently joining the regex's fan-in reddens too,
      because `PlexUnreachable` would then alert on a probe nobody decided it
      should cover. That comment now records the landing, so the sentence quoted
      here is history rather than a live citation.
    * `watchdog_metric` — every `plex_*` family is one the watchdog SOURCE emits,
      read by `ast` (`_watchdog_emitted`) because that file names its own metrics
      in prose and a grep would be answered by the documentation.
    * `event_type` — `TX_HELD` is a type the watchdog's classifier really emits.
      A label value is the quietest coordinate of the four: `increase(...{
      event_type="TX_HELED"}[5m])` is a valid expr over an empty selector.

    Fully anchored, as Prometheus anchors: `re.fullmatch`, so `blackbox-plex.*`
    cannot be satisfied by a job that merely CONTAINS the prefix.

    NOT PINNED, and each absence is deliberate — this list is what a later hat
    reads to know what is still open, so an absence missing from it is the defect
    the round-1 charge was written on:

    * `labels:` / `annotations:` — design §5.3 carries none, and plan.md's
      "every alert has `severity` and a `summary`" is an obligation on `7d`, not a
      property of the source. Pinning them here would redden the file this row is
      required to ship.
    * that any alert FIRES. Every one of the seven compares a series to a
      constant and cannot match an ABSENT one — `plex_watchdog_probe_status == 0`
      returns an empty vector exactly when the watchdog has stopped producing,
      which is the only moment the meta-guard exists for. That is measured at the
      wave cut with a positive control, and `7b` shipped the three `absent()`
      doors that cover it: the coverage relation lives in
      `test_absent_series_doors_cover_every_alert_input` and the firability in
      `PLEX_BLIP_ABSENCE_EVIDENCE`, not here.
    * `up{job="plex-exporter"}`, `probe_success`, `probe_duration_seconds` — the
      metric NAMES are Prometheus' and blackbox's own, produced by the scrape
      rather than by anything in this repo, so there is no in-tree far end to read
      them against and `watchdog_metric` is bounded to `plex_` rather than
      pretending otherwise. Their `job=` labels ARE checked, above.
    """
    body = _read(PROM_RULES)
    try:
        doc = yaml.load(_neutralise_refs(body), Loader=_StrictLoader)
        parse_error = None
    except yaml.YAMLError as exc:
        doc, parse_error = None, str(exc).splitlines()[0]
    groups = doc.get("groups") if isinstance(doc, dict) else None
    groups = groups if isinstance(groups, list) else []
    one_group = (
        len(groups) == 1 and isinstance(groups[0], dict)
        and groups[0].get("name") == PROM_RULES_GROUP
    )
    rules = groups[0].get("rules") if one_group else None
    rules = [r for r in rules if isinstance(r, dict)] if isinstance(rules, list) else []
    found = tuple(
        (
            r.get("alert"),
            " ".join(r["expr"].split()) if isinstance(r.get("expr"), str)
            else r.get("expr"),
            r.get("for"),
        )
        for r in rules
    )
    alerts_are_the_design = found == PLEX_BLIP_ALERTS
    job_names = _scrape_job_names(_read(PROM_SCRAPE))
    families, events = _watchdog_emitted(_read(PLEX_WATCHDOG_SOURCE))
    unresolved = {}
    for rule in rules:
        expr = rule.get("expr")
        if not isinstance(expr, str):
            unresolved[rule.get("alert")] = ["expr is not a scalar"]
            continue
        bad = []
        for job in re.findall(PLEX_BLIP_EXPR_READERS["exact_job"], expr):
            if job not in job_names:
                bad.append(
                    f'job="{job}" is not a job_name in {PROM_SCRAPE.name} '
                    f"(scraped={job_names}) — this rule matches no series"
                )
        for pattern in re.findall(PLEX_BLIP_EXPR_READERS["regex_job"], expr):
            try:
                fan_in = {j for j in job_names if re.fullmatch(pattern, j)}
            except re.error as exc:
                bad.append(f'job=~"{pattern}" does not compile ({exc})')
                continue
            if fan_in != set(BLACKBOX_JOBS):
                bad.append(
                    f'job=~"{pattern}" fans in to {sorted(fan_in)}, want '
                    f"{sorted(BLACKBOX_JOBS)} — the exact-match far end "
                    f"{PROM_SCRAPE.name}'s 5c comment deferred to this step"
                )
        for metric in re.findall(PLEX_BLIP_EXPR_READERS["watchdog_metric"], expr):
            if metric not in families:
                bad.append(
                    f"{metric} is not a family {PLEX_WATCHDOG_SOURCE.name} emits "
                    f"(emitted={sorted(families)})"
                )
        for event in re.findall(PLEX_BLIP_EXPR_READERS["event_type"], expr):
            if event not in events:
                bad.append(
                    f'event_type="{event}" is not a type '
                    f"{PLEX_WATCHDOG_SOURCE.name} emits (emitted={sorted(events)})"
                )
        if bad:
            unresolved[rule.get("alert")] = bad
    # Report the DIVERGING rows and not both 7-tuples: an expr is ~70 characters,
    # so dumping `found` beside `PLEX_BLIP_ALERTS` is 1,000 characters in which a
    # reader has to spot `== 1` by eye. `zip_longest` because a dropped or added
    # rule must be named too, and that is the failure this sequence exists for.
    divergences = [
        f"#{i}: want {want!r}, found {got!r}"
        for i, (want, got) in enumerate(
            itertools.zip_longest(PLEX_BLIP_ALERTS, found), start=1
        )
        if want != got
    ]
    ok = bool(doc) and one_group and alerts_are_the_design and not unresolved
    print(
        f"{'OK' if ok else 'FAIL'}: {PROM_RULES.name} carries design 5.3's "
        f"{len(PLEX_BLIP_DESIGN_ALERTS)} alerts plus 7b's "
        f"{len(PLEX_BLIP_ABSENCE_ALERTS)} absence doors — the (alert, expr, for) "
        f"sequence literally, and every coordinate resolving "
        f"(parses={bool(doc)} (error={parse_error!r}), one_group={one_group} "
        f"(want {PROM_RULES_GROUP!r}), alerts_are_the_design="
        f"{alerts_are_the_design} (divergences={divergences}), "
        f"unresolved={unresolved} — no clause here claims any of these FIRE; "
        f"that is test_absent_series_doors_cover_every_alert_input's)"
    )
    return ok


def test_every_alert_carries_severity_and_summary() -> bool:
    """Step-7d: every rule ships `labels.severity` + `annotations.summary`.

    plan.md's second Tests bullet is an obligation on this step, not a property
    of design §5.3 — the source carries neither key (premise 4). This guard reads
    the PARSED render and holds EVERY rule to both, per-rule, so a rule added
    later without them reddens rather than passing on a count that stays high.
    `severity` is also held to `{warning, critical}` — the two levels Prometheus
    and Grafana render natively — so a typo lands here rather than in a bucket no
    dashboard filters on.

    ACCEPTANCE 2 is a SEPARATE arm and it is a WORDING PROPERTY, not a sentence:
    `PlexExporterScrapeFailing`'s summary must NAME the real fault (exporter /
    scrape / metrics) and must NOT be misreadable as "Plex is down", because the
    single-panel dashboard already invites that conflation (design R5) and the
    two faults have different first moves. Pinning the property lets the wording
    be rewritten freely while a drift back into "Plex is down" still reddens; the
    alert must also EXIST for the arm to have bitten, so its absence is a defect
    here too.

    NOT this clause's job: that the alerts FIRE (that is the `promtool test rules`
    unit suite in `test_plex_blip_alert_rules_promtool.py`), the `(alert, expr,
    for)` sequence (`test_plex_blip_alert_rules_are_design_5_3`), or the absence
    doors' coverage (`test_absent_series_doors_cover_every_alert_input`). This one
    reads labels and annotations and nothing else.
    """
    body = _read(PROM_RULES)
    try:
        doc = yaml.load(_neutralise_refs(body), Loader=_StrictLoader)
        parse_error = None
    except yaml.YAMLError as exc:
        doc, parse_error = None, str(exc).splitlines()[0]
    groups = doc.get("groups") if isinstance(doc, dict) else None
    groups = groups if isinstance(groups, list) else []
    one_group = (
        len(groups) == 1 and isinstance(groups[0], dict)
        and groups[0].get("name") == PROM_RULES_GROUP
    )
    rules = groups[0].get("rules") if one_group else None
    rules = [r for r in rules if isinstance(r, dict)] if isinstance(rules, list) else []
    missing = {}
    for r in rules:
        name = r.get("alert")
        labels = r.get("labels") if isinstance(r.get("labels"), dict) else {}
        anns = r.get("annotations") if isinstance(r.get("annotations"), dict) else {}
        severity = labels.get(ALERT_SEVERITY_LABEL)
        summary = anns.get(ALERT_SUMMARY_ANNOTATION)
        bad = []
        if not (isinstance(severity, str) and severity in ALERT_SEVERITY_LEVELS):
            bad.append(
                f"labels.{ALERT_SEVERITY_LABEL}={severity!r} "
                f"(want one of {sorted(ALERT_SEVERITY_LEVELS)})"
            )
        if not (isinstance(summary, str) and summary.strip()):
            bad.append(
                f"annotations.{ALERT_SUMMARY_ANNOTATION}={summary!r} "
                "(want a non-empty string)"
            )
        if bad:
            missing[name] = bad
    # ACCEPTANCE 2 — the wording property, read off the exporter alert's summary.
    exporter = next(
        (r for r in rules if r.get("alert") == EXPORTER_SCRAPE_FAILING_ALERT), None
    )
    exporter_defect = None
    if exporter is None:
        exporter_defect = (
            f"{EXPORTER_SCRAPE_FAILING_ALERT} is absent — acceptance 2 has "
            "nothing to bite"
        )
    else:
        anns = exporter.get("annotations") if isinstance(
            exporter.get("annotations"), dict) else {}
        summary = anns.get(ALERT_SUMMARY_ANNOTATION)
        low = summary.lower() if isinstance(summary, str) else ""
        misreads = [p for p in EXPORTER_DOWN_MISREADINGS if p in low]
        names_fault = any(w in low for w in EXPORTER_REAL_FAULT_WORDS)
        if misreads or not names_fault:
            exporter_defect = (
                f"summary={summary!r}: misreads-as-down={misreads}, "
                f"names-real-fault={names_fault} — must name one of "
                f"{EXPORTER_REAL_FAULT_WORDS} and none of "
                f"{EXPORTER_DOWN_MISREADINGS}"
            )
    ok = (
        bool(doc) and one_group and bool(rules)
        and not missing and exporter_defect is None
    )
    print(
        f"{'OK' if ok else 'FAIL'}: every one of {PROM_RULES.name}'s {len(rules)} "
        f"rules carries labels.{ALERT_SEVERITY_LABEL} in "
        f"{sorted(ALERT_SEVERITY_LEVELS)} and a non-empty "
        f"annotations.{ALERT_SUMMARY_ANNOTATION} "
        f"(parses={bool(doc)} (error={parse_error!r}), one_group={one_group}, "
        f"missing={missing}), and {EXPORTER_SCRAPE_FAILING_ALERT}'s summary is "
        f"unmisreadable as 'Plex is down' (exporter_defect={exporter_defect})"
    )
    return ok


def _promql_selectors(expr: str) -> list:
    """Every INSTANT SELECTOR in a PromQL expr as `(metric, labels)`.

    A metric name is an identifier that is NOT followed by `(` — which is what
    separates `probe_success` from `absent`, `increase` and every other function
    without an enumeration of function names that would fail OPEN one function
    past its edge. The label block is consumed with the metric, so label KEYS
    (`job`, `event_type`) are never mistaken for series, and the handful of bare
    words PromQL reserves are refused by `PROMQL_KEYWORDS`.

    Returns a LIST rather than a set: a door that names the same job twice is a
    defect this shape can see and a set would hide.

    `(?![a-z0-9_])` after the identifier is load-bearing and it cost a round to
    notice: without it the engine BACKTRACKS a function name one character to
    satisfy the `(?!\\s*\\()` lookahead, and `increase(...)` is reported as a
    metric named `increas`. Measured — the RED it produced is in
    `logs/builder-7b-red.log`.

    A RECORDING-RULE NAME FAILS CLOSED rather than being read wrong. `:` is out of
    the identifier class on purpose, so `job:plex_probe:rate5m > 3` yields the
    bogus `job` (the lookbehind then refuses the two tail segments), which is not
    a key of `PLEX_BLIP_ABSENCE_DOORS` and reddens `doors_complete`. This file
    ships no recording rule today; the shape means the first one arrives as a RED
    asking to be read properly, not as a silently uncovered series.
    """
    return [
        (m.group(1), m.group(2) or "")
        for m in re.finditer(
            r'(?<![\w:])([a-z_][a-z0-9_]*)(?![a-z0-9_])(\{[^}]*\})?(?!\s*\()', expr
        )
        if m.group(1) not in PROMQL_KEYWORDS
    ]


def _promql_absent_args(expr: str) -> tuple:
    """`(args, readable)` — what every `absent(...)` in `expr` is called on.

    `args` is a list of `(metric, labels)`. `readable` is False when the count of
    `absent(` occurrences does not equal the count parsed, which is how this
    fails CLOSED: `absent(rate(x[5m]))` and `absent(a or b)` are legal PromQL
    this reader cannot decompose, and returning a SHORT list for them would read
    as "that door is not there" in one clause and "no regex inside absent" as
    vacuously true in another. A door this reader cannot read is a RED.
    """
    args = [
        (m.group(1), m.group(2) or "")
        for m in re.finditer(
            r'\babsent\s*\(\s*([a-z_][a-z0-9_]*)\s*(\{[^}]*\})?\s*\)', expr
        )
    ]
    return args, len(args) == len(re.findall(r'\babsent\s*\(', expr))


def _strip_absent(expr: str) -> str:
    """`expr` with every readable `absent(...)` span removed.

    What is left is what the rule compares to a CONSTANT, so a metric surviving
    this is a metric whose absence needs a door.
    """
    return re.sub(
        r'\babsent\s*\(\s*[a-z_][a-z0-9_]*\s*(?:\{[^}]*\})?\s*\)', " ", expr
    )


def test_absent_series_doors_cover_every_alert_input() -> bool:
    """Step-7b: every series a rule COMPARES has an `absent()` door, per-job.

    THE DEFECT THIS ROW EXISTS FOR IS SILENCE, NOT WRONGNESS. Every one of design
    §5.3's seven rules compares a series to a constant, and a comparison over an
    ABSENT series returns an empty vector — so each rule goes quiet exactly when
    the thing it guards has stopped producing. Measured at the wave cut on a live
    `prom/prometheus:v3.12.0` with a positive control
    (`logs/planner-step07-live.log`): with the series absent,
    `plex_watchdog_probe_status == 0` and `probe_success{job=~"blackbox-plex.*"}
    == 0` are both EMPTY while `absent(plex_watchdog_probe_status)` returns 1 and
    the control `up{job="prometheus"} == 1` returns a real sample. The emptiness
    is the semantics and the instrument works.

    WHICH RULES ARE DOORS IS READ OUT OF THE FILE (`file_doors`: any rule whose
    expr calls `absent(`), and every arm below that exempts a door or quantifies
    over one quantifies over that set rather than over
    `PLEX_BLIP_ABSENCE_DOORS`' values. The round-1 charge was written on the
    other arrangement: three constants narrated a fourth door and no predicate
    read them, so adding one was `PASS` past every arm here.

    * `doors_agree` — `file_doors`, the doors `PLEX_BLIP_ABSENCE_DOORS` maps to,
      and `PLEX_BLIP_ABSENCE_SOURCE_JOBS`' keys are ONE set. This is what makes
      `for_outlasts_the_scrape` a quantifier over the file instead of over
      "each door someone remembered to enumerate": without it a fourth door at
      `for: 15s` is green, because the cadence loop iterates the source-jobs
      table and nothing related its keys to the rules file.

    * `residue_unwatched` — NO `absent()` IN THIS FILE NAMES A KEY OF
      `PLEX_BLIP_ABSENCE_RESIDUE`. That table's metrics are absent in states
      that are HEALTHY, so a door over one pages on the good state, and
      `absent(plex_sqlite_wal_bytes)` in particular is the draft this row
      already refused on the CLI (leg D, `rc=1` in both healthy legs). Until
      this arm existed the table was reached by an f-string and by no predicate:
      the fourth door was `PASS` while the same `print` went on listing its
      metric as unwatched — a report contradicting itself inside one line.

    * `doors_complete` — every metric that survives `_strip_absent` on a
      non-door rule is a key of `PLEX_BLIP_ABSENCE_DOORS`. This is the clause
      that reddens when a LATER rule arrives reading a series nothing watches:
      the metric set is read out of the rules FILE, so an eighth alert over a new
      family is a RED here rather than a silent eighth blind spot. It is
      FAMILY-granular while the row's thesis is per-JOB, and that residue is
      filed rather than papered over at `task-1786231423-747a`.

    * `doors_present` — each door named in that table is a rule in this file and
      it calls `absent()` on the metric the table names. Both halves are read
      from the file; the table is the map between them.

    * `doors_are_absent_only` — a door rule is `absent(...)`s and nothing else,
      quantified over `file_doors`. A door that also carried a comparison would
      be a rule with two jobs, and the `or` between them means the comparison
      arm can never be REACHED while the absence arm has a sample.

    * `per_job_door` — THE ROW'S OWN DEFECT CLASS, ONE STEP IN, and it is
      measured rather than reasoned. `absent()` returns a sample only when its
      selector matches NOTHING, so a single `absent(probe_success{job=~
      "blackbox-plex.*"})` is silent while any ONE of the three jobs still
      reports — two probes gone, door shut. The shipped door therefore names
      each job in its own `absent()`, and THE FAR END IS THE SCRAPE CONFIG: the
      wanted set is every `job="X"` the rules this door covers name plus every
      `job_name:` in `prometheus.yml.j2` their `job=~` patterns fan in to, so a
      fourth `blackbox-plex-*` job joining the scrape config without joining the
      door reddens here. Against `BLACKBOX_JOBS` — the first draft of this arm —
      it did not: that is `task-1786203094-588c`'s half-relation shape, in the
      round that closed 588c, and the door was being compared to a test
      constant while the docstring claimed "both directions". It fails CLOSED
      three ways: no covered alerts, no jobs selected, or a `job=~` that does
      not compile are each a RED rather than a vacuous equality of empty sets.

    * `no_regex_inside_absent` — the general form of the same fact, over every
      door rather than the one: `job=~` inside an `absent()` anywhere in this file
      is refused.

    * `for_outlasts_the_scrape` — each door's `for:` is at least
      `PLEX_BLIP_ABSENCE_MIN_MISSES` times the slowest `scrape_interval` among the
      jobs that feed it, READ OUT of `prometheus.yml.j2` rather than spelled here.
      A door is an alarm about the alarm, so one missed scrape must not page.
      `doors_agree` is what makes it a quantifier over every door in the file.

    NOT CLOSED HERE, and `PLEX_BLIP_ABSENCE_RESIDUE` is a table read by
    `residue_unwatched` rather than a sentence, so pointing a door at one of its
    metrics later is a RED. The watchdog OMITS a family whose measurement is null
    rather than publishing a zero, so two of its series are absent in states that
    are perfectly healthy: `plex_watchdog_probe_status` until the first trigger,
    and `plex_sqlite_wal_bytes` whenever the WAL is checkpointed. Both were driven
    on the real CLI here — a never-triggered watchdog with the WAL checkpointed
    serves 130 bytes of `plex_sqlite_db_bytes` alone, and the same watchdog with a
    live writer serves wal+db+shm — and that measurement is what chose the door's
    metric, having first refused the draft that watched the WAL gauge. The
    restart case therefore stays open against the WATCHDOG, not against this
    file: no rule can tell "restarted" from "healthy, never blipped" while the two
    produce the same document. `task-1786159639-39db` is CLOSED by this row and
    that residue is re-filed as `task-1786230651-63ba`; the `.prom`'s own mode,
    the input side of the same door, is `task-1786230668-0902`.
    """
    body = _read(PROM_RULES)
    try:
        doc = yaml.load(_neutralise_refs(body), Loader=_StrictLoader)
        parse_error = None
    except yaml.YAMLError as exc:
        doc, parse_error = None, str(exc).splitlines()[0]
    groups = doc.get("groups") if isinstance(doc, dict) else None
    groups = groups if isinstance(groups, list) else []
    rules = groups[0].get("rules") if len(groups) == 1 and isinstance(
        groups[0], dict) else None
    rules = [r for r in rules if isinstance(r, dict)] if isinstance(rules, list) else []
    exprs = {
        r.get("alert"): " ".join(r["expr"].split())
        for r in rules if isinstance(r.get("expr"), str)
    }
    fors = {r.get("alert"): r.get("for") for r in rules}
    door_names = {door for door, _ in PLEX_BLIP_ABSENCE_DOORS.values()}
    # WHICH RULES ARE DOORS IS READ OUT OF THE FILE, not off the table. Every
    # arm below that exempts a door, or quantifies over one, quantifies over
    # THIS set; `doors_agree` then holds it equal to both tables, so a door the
    # file gains without either table gaining it is a RED here rather than a
    # rule no arm reaches.
    file_doors = {
        alert for alert, expr in exprs.items() if re.search(r'\babsent\s*\(', expr)
    }
    defects = []
    # `doors_agree` — the file's doors, the map's doors and the cadence table's
    # keys are ONE set. Without it `for_outlasts_the_scrape` iterates
    # PLEX_BLIP_ABSENCE_SOURCE_JOBS, whose keys nothing relates to the file, and
    # a fourth door at `for: 15s` is green because no arm looks at it.
    doors_agree = file_doors == door_names == set(PLEX_BLIP_ABSENCE_SOURCE_JOBS)
    if not doors_agree:
        defects.append(
            f"doors disagree: {PROM_RULES.name} carries {sorted(file_doors)}, "
            f"PLEX_BLIP_ABSENCE_DOORS maps to {sorted(door_names)}, "
            f"PLEX_BLIP_ABSENCE_SOURCE_JOBS keys "
            f"{sorted(PLEX_BLIP_ABSENCE_SOURCE_JOBS)} — a door outside all three "
            f"is a rule no arm here reaches"
        )
    # `residue_unwatched` — PLEX_BLIP_ABSENCE_RESIDUE is a PREDICATE, not a
    # print. Each of its metrics is absent in a state that is HEALTHY (leg W1's
    # 130-byte document), so a door over one pages on the good state — and
    # `absent(plex_sqlite_wal_bytes)` specifically is the draft this row already
    # refused on the CLI. Without this arm the table was reached by an f-string
    # only: a fourth door on a residue metric was PASS while the same line went
    # on printing that metric as "still open".
    watched_residue = sorted({
        f"{alert}: absent({metric})"
        for alert, expr in exprs.items()
        for metric, _ in _promql_absent_args(expr)[0]
        if metric in PLEX_BLIP_ABSENCE_RESIDUE
    })
    residue_unwatched = not watched_residue
    if watched_residue:
        defects.append(
            f"{watched_residue} — every metric in PLEX_BLIP_ABSENCE_RESIDUE is "
            f"absent in a HEALTHY state, so a door over it fires on the good "
            f"state; the residue names the measurement that refused each"
        )
    # `doors_complete` — what the comparison rules read, against the table.
    uncovered = sorted({
        metric
        for alert, expr in exprs.items() if alert not in file_doors | door_names
        for metric, _ in _promql_selectors(_strip_absent(expr))
        if metric not in PLEX_BLIP_ABSENCE_DOORS
    })
    doors_complete = not uncovered
    if uncovered:
        defects.append(
            f"{uncovered} are compared to a constant with no absent() door — "
            f"each is silent exactly when its producer has stopped"
        )
    # `doors_present` — the table's map, in the file.
    doors_present = True
    for metric, (door, door_metric) in sorted(PLEX_BLIP_ABSENCE_DOORS.items()):
        expr = exprs.get(door)
        if expr is None:
            doors_present = False
            defects.append(f"{metric}'s door {door!r} is not a rule in this file")
            continue
        args, readable = _promql_absent_args(expr)
        if not readable:
            doors_present = False
            defects.append(f"{door}'s absent() calls are not all plain selectors")
            continue
        if door_metric not in {m for m, _ in args}:
            doors_present = False
            defects.append(
                f"{door} does not call absent() on {door_metric!r} "
                f"(calls it on {sorted({m for m, _ in args})})"
            )
    # `doors_are_absent_only` — quantified over the FILE's doors, so a door the
    # table has not heard of is still held to carrying no comparison arm.
    doors_are_absent_only = True
    for door in sorted(file_doors):
        args, readable = _promql_absent_args(exprs[door])
        leftover = _promql_selectors(_strip_absent(exprs[door]))
        if not readable or leftover:
            doors_are_absent_only = False
            defects.append(
                f"{door} is not absent()s alone (readable={readable}, "
                f"also compares {leftover})"
            )
    # `per_job_door` — SET EQUALITY AGAINST THE SCRAPE CONFIG, both directions.
    # The far end is `prometheus.yml.j2`, resolved through the selectors of the
    # rules this door covers: every `job="X"` they name plus every job name the
    # file really scrapes that their `job=~` patterns fan in to. Against
    # `BLACKBOX_JOBS` this was the 588c tautology one clause over — the door was
    # compared to a test constant, so a fourth `blackbox-plex-*` job joining the
    # scrape config left it True.
    covered_alerts = sorted(
        alert for alert, expr in exprs.items() if alert not in file_doors
        and any(
            PLEX_BLIP_ABSENCE_DOORS.get(metric, (None, None))[0]
            == PLEX_BLIP_ABSENCE_PER_JOB_DOOR
            for metric, _ in _promql_selectors(_strip_absent(expr))
        )
    )
    scraped_jobs = _scrape_job_names(_read(PROM_SCRAPE))
    selected_jobs, unreadable_patterns = set(), []
    for alert in covered_alerts:
        selected_jobs.update(
            re.findall(PLEX_BLIP_EXPR_READERS["exact_job"], exprs[alert]))
        for pattern in re.findall(
                PLEX_BLIP_EXPR_READERS["regex_job"], exprs[alert]):
            try:
                selected_jobs.update(
                    j for j in scraped_jobs if re.fullmatch(pattern, j))
            except re.error as exc:
                unreadable_patterns.append(f'{alert}: job=~"{pattern}" ({exc})')
    per_expr = exprs.get(PLEX_BLIP_ABSENCE_PER_JOB_DOOR, "")
    per_args, per_readable = _promql_absent_args(per_expr)
    door_jobs = sorted(
        j for _, labels in per_args
        for j in re.findall(PLEX_BLIP_EXPR_READERS["exact_job"], labels)
    )
    per_job_door = (
        per_readable and bool(covered_alerts) and bool(selected_jobs)
        and not unreadable_patterns and door_jobs == sorted(selected_jobs)
    )
    if not per_job_door:
        defects.append(
            f"{PLEX_BLIP_ABSENCE_PER_JOB_DOOR} names jobs {door_jobs}, want "
            f"{sorted(selected_jobs)} once each — the jobs {covered_alerts} "
            f"select out of {PROM_SCRAPE.name} (readable={per_readable}, "
            f"patterns={unreadable_patterns}); absent() over a regex is EMPTY "
            f"while any one of them still reports"
        )
    # `no_regex_inside_absent` — the same fact over every door.
    regexed = sorted({
        f"{alert}: {labels}"
        for alert, expr in exprs.items()
        for _, labels in _promql_absent_args(expr)[0]
        if re.search(PLEX_BLIP_EXPR_READERS["regex_job"], labels)
    })
    no_regex_inside_absent = not regexed
    if regexed:
        defects.append(f"job=~ inside absent(): {regexed}")
    # `for_outlasts_the_scrape` — the cadence is read, not spelled.
    prom = _read(PROM_SCRAPE)
    cadence, for_outlasts_the_scrape = {}, True
    for door, jobs in sorted(PLEX_BLIP_ABSENCE_SOURCE_JOBS.items()):
        intervals = [
            _effective_scrape_pair(prom, _scrape_job_block(prom, job))["interval"]
            for job in jobs
        ]
        held = _duration_seconds(fors.get(door))
        want = (
            max(i for i in intervals if i is not None) * PLEX_BLIP_ABSENCE_MIN_MISSES
            if all(i is not None for i in intervals) and intervals else None
        )
        cadence[door] = {"for_s": held, "want_at_least_s": want}
        if want is None or held is None or held < want:
            for_outlasts_the_scrape = False
            defects.append(
                f"{door} for={fors.get(door)!r} ({held}s) does not outlast "
                f"{PLEX_BLIP_ABSENCE_MIN_MISSES} missed scrapes of {list(jobs)} "
                f"(intervals={intervals}, want >= {want}s)"
            )
    ok = (
        bool(doc) and doors_agree and residue_unwatched and doors_complete
        and doors_present and doors_are_absent_only and per_job_door
        and no_regex_inside_absent and for_outlasts_the_scrape
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {PROM_RULES.name}'s "
        f"{len(file_doors)} absent() doors cover every series its rules compare "
        f"(parses={bool(doc)} (error={parse_error!r}), "
        f"doors_agree={doors_agree} (file={sorted(file_doors)}), "
        f"residue_unwatched={residue_unwatched} (no door over "
        f"{sorted(PLEX_BLIP_ABSENCE_RESIDUE)}), "
        f"doors_complete={doors_complete}, doors_present={doors_present}, "
        f"doors_are_absent_only={doors_are_absent_only}, "
        f"per_job_door={per_job_door} (jobs={door_jobs}, "
        f"{PROM_SCRAPE.name} selects {sorted(selected_jobs)} through "
        f"{covered_alerts}), "
        f"no_regex_inside_absent={no_regex_inside_absent}, "
        f"for_outlasts_the_scrape={for_outlasts_the_scrape} ({cadence}), "
        f"defects={defects} — firability driven live at "
        f"{PLEX_BLIP_ABSENCE_EVIDENCE}; DEC-328's three charges re-measured at "
        f"{PLEX_BLIP_ABSENCE_GUARD_EVIDENCE})"
    )
    return ok


def test_prometheus_retention_outlives_the_blip_window() -> bool:
    """Step-5d: the prometheus `command:` keeps the TSDB for 90 days.

    Every measurement named here was driven at this row's own hands against the
    pinned `prom/prometheus:v3.12.0`: round 1 in `PROMETHEUS_RETENTION_EVIDENCE`,
    the sibling-knob census and the path-spelling rows in
    `PROMETHEUS_SIBLING_EVIDENCE`. The WORKDIR / `--storage.tsdb.path` half is
    written up on `PROMETHEUS_TSDB_DIR` and the knob census on
    `PROMETHEUS_SIZE_CAP_FLAG`, rather than twice.

    FIVE conjuncts, and the two this file did not have at round 1 are `no_size_cap`
    and the resolving form of `tsdb_path_ok`.

    * `retention_pinned` — `--storage.tsdb.retention.time=90d` is read out of the
      RENDERED `command:` list by `_service_command_args`, which decomments the
      block before it splits it. That is what makes "not out of a comment" true
      BY CONSTRUCTION rather than by assertion, and it is not a hypothetical
      here: the entry this row adds is documented by a comment directly above it
      that names the flag and both numbers.

      READ BY VALUE, NEVER BY PRESENCE. `--storage.tsdb.retention.time=15d` is a
      document `prom/prometheus` LOADS — rc=0, `duration=15d`, no warning, no
      crash loop (row N) — so a presence-only clause would be green over a stack
      that had silently gone back to `PROMETHEUS_RETENTION_DEFAULT`, which is the
      exact regression this row exists to prevent and the class filed twice
      already as `task-1786128505-658f`.

      `_last_flag_value` takes the LAST occurrence, for the reason given there.
      Its inherited sentence needs inverting for THIS flag and the inversion is
      measured rather than assumed: a repeated
      `--storage.tsdb.retention.time` is `flag
      'storage.tsdb.retention.time' cannot be repeated`, rc=2 (row 3 of the same
      log) — kingpin refuses rather than picks. So first-vs-last is LOUD here,
      an instant failure to start, and no clause below claims to be closing a
      silence that the runtime already closes.

    * `no_size_cap` — `--storage.tsdb.retention.size` is ABSENT from the same
      list. This is the conjunct round 1 did not have, and it is the sibling-knob
      hole rather than another spelling of the pinned flag: `=90d` and
      `--storage.tsdb.retention.size=1MB` sit side by side at rc=0, the process
      logs `duration=90d size=1MiB`, and a TSDB capped at a megabyte is pruned in
      minutes while `retention_pinned` above still reads `90d` and this line
      still prints "keeps its TSDB for 90d". Silent-healthy, no crash loop —
      exactly the failure class this row exists to prevent, one arm over.

      ABSENCE, not a value, because there is no disk cap this stack wants and a
      later row that wants one pays by moving this pin rather than by editing a
      number. The census that says ONE conjunct closes the axis is on
      `PROMETHEUS_SIZE_CAP_FLAG`: the three other knobs that could bound the same
      TSDB all refuse to start. The config-file side of BOTH flags is closed by
      `no_config_side_retention` below, so this is the flag side of the same axis
      and not a second door.

      AN ABSENCE PIN IS EXACTLY AS WIDE AS ITS READER'S SPELLING CENSUS, and that
      is the third census this one conjunct rests on — round 4's charge. Round 3
      shipped it over an `=`-only reader while kingpin takes `--flag value` too,
      so two `command:` entries delivered the cap at `restarts=0`, `size=1MiB`,
      and THIS LINE printed `no_size_cap=True (…=None, want absent)`. `absent`
      now means absent in BOTH joins (`_last_flag_value`), and the split form
      whose value cannot be attributed reads `UNREADABLE`, which is not `None`
      and reds here.

    * `tsdb_path_ok` — the path flag is absent today, and the clause admits every
      spelling that RESOLVES to `PROMETHEUS_TSDB_DIR` rather than the one that
      equals it. It reds on `/prometheus`, which is the obvious edit and the
      silent one.

      RESOLVING IS THE REPAIR, AND THE EQUALITY IT REPLACES WAS A FALSE-RED ON A
      CORRECT TREE: `--storage.tsdb.path=data/` is the flag's own documented
      default written out, it lands the TSDB in the same place as no flag at all
      (rows P0/P1), and round 1's clause reddened on it. The reader here does
      what the binary does — join the value onto the image WORKDIR — so the four
      admitted spellings on `PROMETHEUS_TSDB_DIR` are one rule and not a list.
      Its boundary, stated because `PurePosixPath` sets it: `.` components and
      trailing slashes collapse, `..` does NOT, so `data/../data` would RED. That
      is the conservative direction on a spelling no tree carries, and this file
      already calls false-RED-on-a-correct-tree a defect class in
      `_service_command_args`.

      RESOLVING THE VALUE IS NOT RESOLVING THE JOIN — the same round-4 charge as
      `no_size_cap`'s, met from the other side. Round 3 resolved four spellings
      of the VALUE and still read the FLAG in one, so `--storage.tsdb.path` +
      `/prometheus` as two `command:` entries ran at `restarts=0` with `wal/`
      landing directly in `/prometheus` — the silent trap this very clause
      documents — while this line printed `tsdb_path_ok=True (value=None …)`.
      Both joins are read now, and `UNREADABLE` composes rather than needing a
      branch: it is a string, so the WORKDIR join carries it to a directory that
      is not `PROMETHEUS_TSDB_DIR` and reds.

    * `no_config_side_retention` — `prometheus.yml` declares no `storage:` key.
      This is an ABSENCE pin and it is deliberate, because the precedence runs
      the opposite way from the intuition: with the FLAG at 30d and the config
      field `storage: {tsdb: {retention: {time: 90d}}}` at 90d, the process logs
      `duration=90d` (row H of the planner's own premises log,
      logs/planner-step05d-premises.log). THE CONFIG FILE WINS. A retention field
      added there would therefore override this row's flag while every clause
      above stayed green — the flag would still read `90d` and would mean
      nothing. Priced at zero on the delivered tree: `prometheus.yml.j2`'s
      top-level keys are `global` and `scrape_configs`. It fails CLOSED, and a
      later row that wants the successor spelling pays by moving the pin here.

    WHICH IS THE OTHER THING THIS ROW OWES: THE FLAG IS DEPRECATED AND SAYS SO
    NOWHERE THE OPERATOR WOULD SEE. `--help` on the pinned binary prints
    "[DEPRECATED] … This flag has been deprecated, use the
    storage.tsdb.retention.time field in the config file instead", and the
    successor is live in v3.12.0 (`promtool` rc=0, `duration=90d`). But the
    running process logs ZERO lines matching /deprecat/ across every row of the
    evidence log, so nothing at runtime would ever have told us. 5d ships the
    FLAG anyway, and the reason is the delivery relation rather than taste: the
    successor lives in `prometheus.yml`, a `:ro` mount whose delivery path is
    `notify: Restart prometheus` — the opposite path — and it would put retention
    back inside the file 5c has just fenced.

    AND THE DELIVERY RELATION IS THE INVERSE OF EVERY OTHER RENDER IN THIS ROLE,
    so it is stated with the rows that decide it and not by analogy. Four rows of
    real `docker compose`, one service, changing only `command:`
    (logs/planner-step05d-premises.log): A create, id `ea064a88`; B CONTROL, `up
    -d` over an UNCHANGED file, SAME id — so `up -d` really is a no-op over an
    unchanged spec, which is what makes C readable; C `command:` changed, `up
    -d`, compose prints `Recreated`, id `4ce73c98`. A `command:` entry IS the
    service spec, so `just play` delivers this change with NO handler. Row D is
    why a handler must not be added anyway: `command:` changed then `docker
    compose restart` leaves the SAME id and the running process still carrying
    the OLD argv while the file on disk says otherwise. A `notify: Restart
    prometheus` copied off the `prometheus.yml` task would not be merely
    redundant — it would deliver NOTHING while looking like delivery.
    """
    block = _strip_comments(_compose_service_block(_read(COMPOSE), PROMETHEUS_SERVICE))
    present = bool(block.strip())
    args = _service_command_args(block)
    retention = _last_flag_value(args, PROMETHEUS_RETENTION_FLAG)
    retention_pinned = retention == PROMETHEUS_RETENTION
    size_cap = _last_flag_value(args, PROMETHEUS_SIZE_CAP_FLAG)
    no_size_cap = size_cap is None
    tsdb_path = _last_flag_value(args, PROMETHEUS_TSDB_PATH_FLAG)
    tsdb_dir = str(
        pathlib.PurePosixPath(PROMETHEUS_WORKDIR)
        / (tsdb_path if tsdb_path is not None else PROMETHEUS_TSDB_PATH_DEFAULT)
    )
    tsdb_path_ok = tsdb_dir == PROMETHEUS_TSDB_DIR
    prom_keys, prom_unreadable = _service_key_lines(_strip_comments(_read(PROM_SCRAPE)))
    no_config_side_retention = "storage" not in prom_keys and not prom_unreadable
    ok = (
        present
        and retention_pinned
        and no_size_cap
        and tsdb_path_ok
        and no_config_side_retention
    )
    print(
        f"{'OK' if ok else 'FAIL'}: {PROMETHEUS_SERVICE} keeps its TSDB for "
        f"{PROMETHEUS_RETENTION} (present={present}, "
        f"retention_pinned={retention_pinned} (value={retention!r}, want="
        f"{PROMETHEUS_RETENTION!r}, and UNSET means {PROMETHEUS_RETENTION_DEFAULT} "
        f"silently — {PROMETHEUS_RETENTION_EVIDENCE} row K), "
        f"no_size_cap={no_size_cap} ({PROMETHEUS_SIZE_CAP_FLAG}={size_cap!r}, want "
        f"absent — set beside a green 90d the process logs size=1MiB and prunes "
        f"in minutes, {PROMETHEUS_SIBLING_EVIDENCE} row S2), "
        f"tsdb_path_ok={tsdb_path_ok} (value={tsdb_path!r} resolves against "
        f"WORKDIR {PROMETHEUS_WORKDIR!r} to {tsdb_dir!r}, want "
        f"{PROMETHEUS_TSDB_DIR!r}), "
        f"no_config_side_retention={no_config_side_retention} "
        f"({PROM_SCRAPE.name} top-level keys={sorted(prom_keys)}, "
        f"unreadable={prom_unreadable}))"
    )
    return ok


def test_prometheus_render_is_world_read_only_unpaid() -> bool:
    """Step-5c: `prometheus.yml`'s 0644 is LICENSED, not merely written down.

    THE FENCE, and this row is the first one that could breach it. Every other
    job in this file scrapes an exporter that needs no credential; 5c's three
    take a URL from a `params:`/`__param_target` shape that would carry a token
    just as happily — `?X-Plex-Token=` on a target, an `X-Plex-Token` params
    entry, a `bearer_token_file:` on the job. And this render is delivered
    **0644**, world-readable, on the reasoning written into the render task
    itself: the scrape config "carries no credential (the PVE token is an env var
    from the 0600 .env)", so publishing it costs nothing.

    THAT SENTENCE IS THE LICENCE AND NOTHING HELD IT. `RELOAD_CONTRACT` pins the
    0644 digits and `test_blackbox_sessions_probe_carries_the_vault_token` pins
    that this template carries no credential spelling — two true facts with
    nothing relating them, so a future row could add a token to the scrape config
    and leave both green while the mode that published it stayed pinned. What is
    NEW here is the implication, and only that: the digits stay
    `RELOAD_CONTRACT`'s to own and the leak scan is one reader
    (`_credential_spellings`) that both clauses call, so this is not a second
    spelling of either fact.

    * `world_read_is_licensed` — an implication and not a conjunction. If the
      render withholds the world bit this clause has no claim to make (0640 is
      the mode `blackbox.yml` legitimately uses one task down, and forbidding it
      here would forbid the safer state). If the render PUBLISHES the file, then
      the template must carry no credential AND the task's own comment must still
      say so.
    * `rationale_agrees` — the biconditional, in the shape
      `header_prose_current` took at 5b, because a load-bearing sentence rots in
      exactly two directions. The comment claims the file is credential-free: it
      must say so while that is true, and must NOT say so once it is false. A
      credential arriving alongside a quietly deleted sentence is the state this
      arm exists for — the mode would then be unlicensed with nothing in the
      diff reading as a lie.

    STEP-7a MADE IT A COLUMN. The role now renders TWO world-readable files, for
    one reason — `prom/prometheus:v3.12.0` runs as uid 65534 and 0640 root:root is
    a `permission denied` crash loop on either of them (driven on both; see
    `PROM_RULES_MODE`) — and a clause naming only `prometheus.yml.j2` would have
    left the second one published with nothing holding the sentence that pays for
    it. `WORLD_READ_LICENCE` is the walk and the arms per row are unchanged. The
    rules file is a ROW and not an exception because a rule expr can carry the
    credential exactly as a scrape target can: a label matcher is an ordinary
    place to write `X-Plex-Token`, and `_credential_spellings` is the same reader
    either way.
    """
    tasks = _read(TASKS)
    seen, defects = {}, {}
    for template in WORLD_READ_LICENCE:
        task = _render_task_block(tasks, template.name)
        mode_text = _render_task_scalar(task, "mode")
        mode_digits = (mode_text or "").strip('"\'')
        try:
            # Fails CLOSED, `world_bit_withheld`'s rule one file over: a mode this
            # cannot read octally is treated as PUBLISHING, so an unreadable mode
            # demands the licence rather than being waved through.
            world_readable = bool(int(mode_digits, 8) & 0o004)
        except ValueError:
            world_readable = True
        leaks = _credential_spellings(_read(template))
        claims_no_credential = PROM_NO_CREDENTIAL_PROSE in task
        world_read_is_licensed = (
            not world_readable or (not leaks and claims_no_credential)
        )
        rationale_agrees = claims_no_credential == (not leaks)
        seen[template.name] = (
            f"mode={mode_text!r} world_readable={world_readable} "
            f"credential_spellings={leaks} "
            f"claims_no_credential={claims_no_credential}"
        )
        if not (world_read_is_licensed and rationale_agrees):
            defects[template.name] = (
                f"world_read_is_licensed={world_read_is_licensed} "
                f"rationale_agrees={rationale_agrees}"
            )
    ok = not defects
    print(
        f"{'OK' if ok else 'FAIL'}: the {len(WORLD_READ_LICENCE)} world-readable "
        f"render modes are paid for (rows={seen}, licence="
        f"{PROM_NO_CREDENTIAL_PROSE!r} in {TASKS.name}'s own render task, "
        f"defects={defects} — 0644 publishes these files to every user on the "
        f"docker host, and the only thing that makes that free is the sentence "
        f"the render task writes above the mode)"
    )
    return ok


def test_homepage_allowed_hosts() -> bool:
    """Step-10: homepage sets HOMEPAGE_ALLOWED_HOSTS=home.{{ domain }}.

    gethomepage/homepage (v0.9.0+) rejects any request whose Host header is not
    localhost and not listed in HOMEPAGE_ALLOWED_HOSTS. Reached ONLY through
    Traefik on Host(`home.{{ domain }}`), so without this env every real
    request hits a "Host validation failed" page and the dashboard never loads.

    THE SERVICE IS SLICED BY THE SAME HELPER AS EVERY OTHER ONE — Step-2a F1,
    round 11. This clause rolled its own slicer,
    `(?ms)^\\s{2}homepage:\\s*$(.*?)^\\s{2}\\S`, and so broke three settled rules in
    one line while calling no helper, which is why no sweep had opened it: a GLYPH
    boundary (round 7), no `services:` anchor (round 8), and no `_strip_comments`
    (round 10's carrier). It cost in BOTH directions, measured
    (logs/red-step02a-rework-f1-round11.log): the env deleted while the service's
    OWN comment spells `HOMEPAGE_ALLOWED_HOSTS=home.{{ domain }}` out is GREEN at
    36/36 while `docker compose config` resolves
    `services.homepage.environment=None`, i.e. every request through Traefik gets
    the "Host validation failed" page (A4; A5 without the comment is RED) — and a
    2-space comment inside the service, this file's own group-comment column, is a
    FALSE RED on a tree the runtime resolves perfectly (A6).

    Round 14 (F1) asks the same question of the EFFECTIVE env map: `environment:`
    is a sequence docker collapses last-wins, and a second
    `HOMEPAGE_ALLOWED_HOSTS=` appended after the correct entry was PASS 36/36
    while `docker compose config` resolved the variable EMPTY — the A4 outcome
    again, reached without touching the correct line (row O5).
    """
    ok = re.search(
        r'\bhome\.\{\{\s*domain\s*\}\}',
        _service_env_map(_read(COMPOSE), "homepage").get("HOMEPAGE_ALLOWED_HOSTS", ""),
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
    entries = _top_level_list(all_yml, "internal_services")
    ok = entries is not None and sorted(entries) == sorted(INTERNAL_SERVICES)
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
    # Decommented (round 12, leg D), for both directions of the same defect: the two
    # PRESENCE pins were satisfiable by env.j2's own documentation comments (rows
    # D3/D4 — the assignment deleted, the comment left, guard GREEN, the rendered
    # `.env` missing the token), and the `buggy` ABSENCE pin reddened a correct tree
    # when a comment merely RECORDED the old undefined reference (row D6).
    # Round 13 (F2): the two PRESENCE pins read the EFFECTIVE value compose
    # resolves for each name (`_env_assignments`, last wins) — see the PVE clause
    # for the row that measured it. The ABSENCE pin stays a claim about the whole
    # DOCUMENT: an undefined reference is wrong wherever it sits, and narrowing it
    # to the last assignment would fail OPEN.
    assignments = _env_assignments(_read(ENV))
    correct = re.search(
        r'\{\{\s*vault_cloudflare_dns_api_token\b', assignments.get("CF_DNS_API_TOKEN", "")
    ) is not None
    # The undefined (vault_-less) reference must be gone.
    buggy = re.search(
        r'CF_DNS_API_TOKEN\s*=\s*\{\{\s*cloudflare_dns_api_token\b',
        _strip_comments(_read(ENV)),
    ) is not None
    tunnel = re.search(
        r'\{\{\s*vault_cloudflare_tunnel_token\b', assignments.get("TUNNEL_TOKEN", "")
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

    "Zero inbound surface" is a claim about REACHABILITY, so it is pinned the
    same two ways as the scrape-only invariant on `pve-exporter`, and every
    finding against that clause has applied verbatim here — the same regex, the
    same evasions, one clause over:

    * `keys_allowed` — the service may declare only `OUTBOUND_ONLY_KEYS`, and
      every line at its key column must be one this guard can READ. The first
      half closes the door that needs no `ports:` key: `network_mode: host` on
      this service renders, `yaml.safe_load`s with `network_mode` as a real
      service key and `docker compose config` returns rc=0, so `just play` ships
      it (logs/calibration-step02a-f1-round5.log, leg A), and it puts whatever
      the container binds in the host netns on every interface. The second half
      closes the same door spelled so that no key LINE exists to read — a merge
      key `<<: *hostnet` off a top-level `x-` field lands `network_mode: host`
      on this service just as squarely, and was green through round 5's
      allow-list (logs/calibration-step02a-f1-round6.log, leg A).
    * `no_ports` — reads every YAML spelling through `_service_published_ports`,
      including the flow list that was GREEN through the round-3 regex and the
      quoted key that was GREEN through round 4's.
    """
    block = _compose_service_block(_read(COMPOSE), "cloudflared")
    present = bool(block)
    image_var = re.search(
        r'(?m)^\s*image:\s*\{\{\s*docker_host_cloudflared_image\s*\}\}', block
    ) is not None
    command = re.search(r'tunnel\s+--no-autoupdate\s+run', block) is not None
    keys, unreadable_keys = _service_key_lines(block)
    extra_keys = sorted(set(keys) - OUTBOUND_ONLY_KEYS)
    keys_allowed = not extra_keys and not unreadable_keys
    published = _service_published_ports(block)
    no_ports = published is None
    # depends_on names traefik (list `- traefik` or a `traefik:` condition map),
    # read INSIDE the key's own block — Step-2a F1, round 10. The span this replaces
    # ran past `depends_on:` to the end of the service, so `depends_on: []` plus a
    # later `TUNNEL_ORIGIN_SERVER_NAME=traefik` — a plausible env line that merely
    # NAMES the host — printed `depends_on_traefik=True` at guard PASS 36/36 over a
    # compose file that parses with `depends_on: []`
    # (logs/red-step02a-rework-f1-round10.log, B8). Both YAML spellings are still
    # accepted, for the reason `_param_values` exists.
    stripped = _strip_comments(block)
    depends = "traefik" in _param_values(stripped, "depends_on") or re.search(
        r'(?m)^\s*traefik:\s*$', _indented_block(stripped, "depends_on")
    ) is not None
    ok = present and image_var and command and keys_allowed and no_ports and depends
    print(
        f"{'OK' if ok else 'FAIL'}: cloudflared service block "
        f"(present={present}, image_var={image_var}, command={command}, "
        f"keys_allowed={keys_allowed} (keys={keys}, unexpected={extra_keys}, "
        f"unreadable={unreadable_keys}), "
        f"no_ports={no_ports} (published={published!r}), depends_on_traefik={depends})"
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
    # An ABSENCE pin, so it stays as wide as the document (a `routers.whoami.tls.domains`
    # label configures that router from whichever service carries it) and is only
    # DECOMMENTED — the relocation comment one line above spelling the label path was a
    # FALSE RED on a correct tree (round 12, row A9).
    compose = _strip_comments(_read(COMPOSE))
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
    # Decommented (round 12, leg D, row D5): an ABSENCE pin over the raw file, and a
    # comment recording that the insecure :8080 surface was removed is a false RED.
    port_unpublished = re.search(r':8080\b', _strip_comments(compose)) is None
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

    `websecure` IS READ FROM THE ROUTER'S OWN `entryPoints` LIST — Step-2a F1,
    round 11, and it is the same pin round 10 rewrote one clause up in
    `test_plex_public_router_present` while leaving this spelling here. The span it
    replaces (`(?s)entryPoints:.*?\\bwebsecure\\b`) stopped at neither the list's end
    nor the key's, so anything later in the router's body answered for it: with
    `entryPoints: [web]` and one middleware REFERENCE named `redirect-to-websecure`
    (this file already names one `redirect-to-https`), the whole field printed
    `websecure=True` at guard PASS 36/36 and the real traefik:v3.7.5 loaded
    `traefik-dashboard` on `['web']` — i.e. `https://traefik.<domain>`, the direct
    LAN/Tailscale path and the only one that serves the wildcard cert this router
    requests, with no router at all, and the dashboard's two routers stacked on the
    tunnel's entrypoint (logs/red-step02a-rework-f1-round11.log, A7; A8 is the same
    move with no carrier, RED).
    """
    dash = _router_block(_read(DYNAMIC), "traefik-dashboard")
    host = re.search(r'Host\(`traefik\.\{\{\s*domain\s*\}\}`\)', dash) is not None
    websecure = "websecure" in _param_values(dash, "entryPoints")
    service = _pins_scalar(dash, "service", "api@internal")
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
        # (1)-(3) are PRESENCE pins about the twin this service defines, so each reads
        # the EFFECTIVE value of one label key on that service's own labels (rounds 12
        # and 13). All three have been measured GREEN on the Error-1000 regression this
        # clause exists to guard — `homepage-web` moved to `websecure` AND repointed at
        # GRAFANA's backend — three ways: with both old lines kept as `# was:` comments
        # above (row A6), with them trailing the mutated lines (R7), and with the wrong
        # values simply APPENDED as duplicate keys and no comment anywhere, which is
        # what docker resolves (D4).
        labels = _service_label_map(compose, s)
        web_ep = "web" in _label_members(
            labels.get(f"traefik.http.routers.{s}-web.entrypoints", "")
        )
        svc = labels.get(f"traefik.http.routers.{s}-web.service") == s
        allowlist = INTERNAL_ALLOWLIST_REF in _label_members(
            labels.get(f"traefik.http.routers.{s}-web.middlewares", "")
        )
        # (4) is an ABSENCE pin: a `tls` label for this twin configures it from
        # whichever service carries it, so the claim stays document-wide and is only
        # decommented. A comment EXPLAINING the deliberate absence of that very label
        # was a FALSE RED on a correct tree (row A8).
        no_tls = re.search(
            rf'routers\.{re.escape(s)}-web\.tls\b', _strip_comments(compose)
        ) is None
        if not (web_ep and svc and allowlist and no_tls):
            failures.append(f"{s}(ep={web_ep},svc={svc},allow={allowlist},no_tls={no_tls})")
    # The dashboard's web twin lives in the file provider on the `web` entrypoint —
    # read from THAT router's own entryPoints list (Step-2a F1, round 10). The span
    # this replaces was anchored on the router's name but bounded by nothing, so it
    # was answered by whatever came after: today the router is LAST in the section
    # and nothing does, but one ORDINARY reorder changes that, and the reorder was
    # measured rather than assumed — with the twin moved above `plex-web` and set to
    # `websecure`, `plex-web`'s `- web` answered the pin at guard PASS 36/36 while
    # the real traefik:v3.7.5 loaded `traefik-dashboard-web` on `websecure`, i.e.
    # traefik.<domain> with no plain-HTTP router for the tunnel to reach
    # (logs/red-step02a-rework-f1-round10.log, B9).
    dash_block = _router_block(dynamic, "traefik-dashboard-web")
    dash_web = "web" in _param_values(dash_block, "entryPoints")
    # CLAUSES (2), (3) AND (4) ARE ASKED OF THIS ROUTER TOO — round 11, and the
    # finding is that they were not. This docstring states all four and names this
    # router; the loop above asks all four of the compose twins; the one member
    # handled "specially" because it lives in the file provider was asked clause
    # (1) only. FOUR ORDINARY-YAML mutations were `PASS: 40/40` — no carrier of any
    # kind is needed for an UNASKED clause (rows P1-P4,
    # logs/red-step03a-r11-unasked-clauses.log): the `middlewares:` block deleted;
    # the `- internal-allowlist@file` entry alone deleted with security-headers
    # kept, so it reads as a tidy-up; the service repointed; a `tls:` block added.
    # The allowlist row went to the pinned traefik:v3.7.5 with a client outside all
    # four allowlisted ranges: `GET /api/http/routers` -> HTTP 200 with the whole
    # router table, where the delivered tree answers 403 — this router is on the
    # `web` entrypoint and dynamic.yml.j2 records :80/:443 as WAN port-forwarded
    # here. Negative control N1 (the same removal on `whoami-web`, where the
    # clauses ARE asked) is RED with `allow=False`: the check was not broken, it
    # was unasked of one router.
    #
    # Each clause is read from the router's OWN block, the same shape the compose
    # twins are read with: `_param_values` for the middleware list (both YAML
    # spellings), and `tls` as an ABSENCE over that block only — the websecure twin
    # legitimately carries one three routers up.
    dash_svc = _pins_scalar(dash_block, "service", "api@internal")
    dash_allow = INTERNAL_ALLOWLIST_REF in _param_values(dash_block, "middlewares")
    dash_no_tls = re.search(r'(?m)^\s*tls:', dash_block) is None
    if not (dash_svc and dash_allow and dash_no_tls):
        failures.append(
            f"traefik-dashboard-web(svc={dash_svc},allow={dash_allow},"
            f"no_tls={dash_no_tls})"
        )
    ok = not failures and dash_web
    print(
        f"{'OK' if ok else 'FAIL'}: tunnel <svc>-web routers present + allowlisted, no tls "
        f"(failures={failures}, traefik_dashboard_web={dash_web})"
    )
    return ok


WEB_TWIN_SUFFIX = "-web"

# The plain-HTTP twins the delivered tree carries, as a FLOOR for the discovery
# below — six tunnel twins plus the WAN-port-forwarded `plex-web`. The row
# quantifies over what it DISCOVERS, so a twin added later is covered without
# touching this; the floor exists so a discovery that finds fewer than the
# delivered tree has cannot pass by finding nothing (row A1/A2).
EXPECTED_WEB_TWINS = frozenset(
    [f"{s}{WEB_TWIN_SUFFIX}" for s in EXTRAS + ["whoami"]]
    + ["traefik-dashboard-web", "plex-web"]
)

# What the DOCKER provider resolves a router's service to when the router carries
# no `.service` label and its container declares none either: a name derived from
# the container, which no line of this template states. Not a value to compare —
# a marker that both sides landed on the same unstated default.
CONTAINER_DERIVED_SERVICE = "<container-derived>"


def _matched_paren(text: str, open_idx: int) -> int | None:
    """Index of the `)` closing the `(` at `open_idx`, or None when none does.

    Backtick-quoted spans are skipped WHOLE, so a `)` inside a matcher argument
    cannot close the call. An unclosed backtick, and a `(` that never closes,
    both return None — this reader has no reading, rather than a capture that
    runs to the end of the line.
    """
    depth = 0
    i = open_idx
    while i < len(text):
        ch = text[i]
        if ch == "`":
            end = text.find("`", i + 1)
            if end < 0:
                return None
            i = end + 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


# The ONE `Host(...)` argument this reader models: a single backtick-quoted
# scalar carrying at least one non-blank character. A LIST is not traefik's
# grammar — on the pinned `traefik:v3.7.5` `Host` takes exactly one parameter
# ("unexpected number of parameters; got 2, expected one of [1]") and refuses a
# blank one ("empty args for matcher Host"), DISABLING that router. The capture
# is what the caller reads, so the shape accepted and the value taken are one
# grammar rather than two. A parenthesis or a backtick inside the argument is
# refused rather than read — `Host(`{{ domain | default('x') }}`)` is a Jinja
# CALL whose rendered value this reader does not evaluate, and the seam fails
# closed on what it cannot read.
#
# THE SEPARATOR OUTSIDE THE BACKTICKS IS THE ENGINE'S LEXER, and this reader's
# was Python's until Step-5c round 4 (`\s*`, the UNICODE class). Traefik parses a
# rule with `vulcand/predicate` over Go's `go/parser.ParseExpr`, whose whitespace
# is exactly the four characters in `_GO_SPACE` — U+00A0 and U+3000 are ILLEGAL
# CHARACTERS to it ("error while parsing rule …: illegal character U+00A0",
# router `status='disabled'`, HTTP 404 for the host, while another router in the
# same file still answers 200; logs/critic-step05c-r3-unicode-space.log). Read as
# a separator here they cost the compared SET nothing, so the twin equalled its
# sibling at `PASS: 42/42` with the router it exists to be missing.
#
# INSIDE the backticks the class stays `\s`, and that is a different engine seam
# rather than an oversight: a raw Go string literal carries any byte, and what
# refuses a blank argument is traefik's own emptiness check
# ("empty args for matcher Host"), which is `strings.TrimSpace` — Go's UNICODE
# class. Where the two classes disagree at all (Python also calls U+001C-U+001F
# space; row W1 of logs/red-step05c-rework-r4-gowhitespace.py enumerates the
# difference over Latin-1) this reader refuses what the engine would accept,
# which is a LOUD false refusal with a one-line escape, not a silent pass.
_GO_SPACE = " \t\r\n"
_HOST_ARG_RE = re.compile(r'[ \t\r\n]*`([^`()]*[^`()\s][^`()]*)`[ \t\r\n]*')


def _rule_host_args(rule: str) -> list | None:
    """The `Host(...)` arguments of a rule that is a pure DISJUNCTION of `Host`
    calls, in file order — and None for EVERY other expression.

    A Traefik rule is a boolean expression over matchers, not a bag of matcher
    arguments, so the operators are part of the claim. This walks the expression
    and accepts exactly one shape:

        Host(`a`) [ || Host(`b`) ]…

    ONE argument per call, because that is the engine's arity and not a taste:
    the accept side of a guard may not model a spelling the runtime refuses. A
    second argument, or a blank one, DISABLES that router on the pinned
    `traefik:v3.7.5` while the rest of the file loads — so the disjunction is
    the only way to name two hosts, and it is the spelling that works
    (`Host(`a`) || Host(`b`)` answers 200 for both and 404 for a third;
    logs/critic-step05c-r2-empty-arg-runtime.log C4).

    Everything else is None, which the caller turns into the empty set and then
    REFUSES rather than compares (a refusal on either side is a defect, so two
    unreadable rules cannot score as agreement):

      `!Host(`h`)`                    a matcher-level NOT is the exact COMPLEMENT
                                      of the host it names — the same set, and a
                                      404 for the host the twin exists to double
      `Host(`h`) && PathPrefix(`/x`)` a conjunction narrows what the router
                                      answers for to a subset this reader does
                                      not model (and `&& Host(`h`)` narrows it to
                                      NOTHING: a request carries one host)
      `Host(`h`) || PathPrefix(`/x`)` a disjunction with an unmodelled matcher
                                      answers for MORE than the set
      `Host(`h`, `h`)`                an argument LIST — the SET is unchanged, so
                                      a one-sided duplicate compared EQUAL to the
                                      sibling while traefik answered 404 for the
                                      host (rework round 3, review F1;
                                      logs/critic-step05c-r2-comma-arg.log R1/R1b)
      `Host(`h`, ``)` / `Host(` `)`   a blank argument: refused HERE rather than
                                      dropped by a truthiness filter downstream,
                                      which read all of ``Host(`h`, ``)``,
                                      ``Host(`h`) || Host(``)`` and
                                      ``Host(`h`, ` `)`` as `{h}` while traefik
                                      disabled every one of them
                                      (logs/critic-step05c-r2-empty-arg-runtime.log)
      `(Host(`h`))`                   grouping is not modelled
      `HostRegexp(`^h$`)`             a name that is not exactly `Host` — it
                                      matches hosts at runtime and pins none
                                      (row M10), and this is also why `HostSNI(`
                                      is not read as `Host(`

    AND THE SEPARATORS BETWEEN THOSE TERMS ARE THE ENGINE'S TOO (round 4). The
    skip below was `rule[i].isspace()`, Python's UNICODE class, while the arity
    above had already been taken to the engine — one reader, two lexers. See
    `_GO_SPACE`: a `Host(`h`)<U+00A0>` on ONE side read to the same set as its
    plain sibling at `PASS: 42/42` while traefik disabled that router, which is
    the arity finding's own shape one seam over. A guard that parses a language
    the runtime also parses makes a claim about the runtime's LEXER with every
    character class it uses, so a host-language builtin (`str.isspace`, `\\s`) is
    where that claim gets made by accident.

    The name must abut its `(` exactly as the previous reader's `Host\\(` required,
    so this refusal is a strict NARROWING of that reader: every rule it still
    reads, it reads to the same set, and the ones it stops reading it refuses
    (logs/red-step05c-rework-r2-differential.py, 42 expressions through BOTH
    implementations — the pre-fix file reconstructed to its own sha256).

    MEASURED, because "traefik would reject it" would have refuted the whole
    finding — it does not: on the pinned `traefik:v3.7.5` with the real file
    provider, `!Host(`plex.test`)` and `Host(…) && PathPrefix(…)` are both
    ACCEPTED (`status='enabled'`, rule echoed back) and answer HTTP 404 for the
    host they must serve (logs/critic-step05c-rule-operator-runtime.log, 7/7).
    Silent, not loud — which is what makes it this row's business.
    """
    args, i, expect_term = [], 0, True
    while i < len(rule):
        if rule[i] in _GO_SPACE:
            i += 1
            continue
        if expect_term:
            m = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\(').match(rule, i)
            if not m or m.group(1) != "Host":
                return None
            close = _matched_paren(rule, m.end() - 1)
            if close is None:
                return None
            inner = rule[m.end():close]
            arg = _HOST_ARG_RE.fullmatch(inner)
            if arg is None:
                return None
            args.append(arg.group(1))
            i, expect_term = close + 1, False
        elif rule.startswith("||", i):
            i, expect_term = i + 2, True
        else:
            return None
    return None if expect_term else args


def _rule_hosts(rule: str | None) -> frozenset:
    """The hostnames a Traefik rule expression PINS with `Host(...)`.

    A SET, because `Host(`a`) || Host(`b`)` and `Host(`b`) || Host(`a`)` are one
    claim about which hosts a router answers for, and the twin/sibling comparison
    is about that claim rather than about the byte string. The set is only a
    faithful reading of a rule whose OPERATORS this reader has modelled, which is
    `_rule_host_args`' whole job — a rule it cannot read that way, and a rule
    absent altogether, both fail CLOSED to the EMPTY set here. The caller refuses
    an empty set on either side rather than comparing it: two empties are EQUAL,
    and calling that agreement is the fail-open rows M11 and N9 exist for.

    Every argument that reaches here is non-blank because the GRAMMAR says so,
    which is why nothing is filtered out at this seam. The filter this replaces
    (`if h.strip()`) DROPPED a blank argument and kept the rest, so
    ``Host(`h`, ``)`` and ``Host(`h`) || Host(``)`` read `{h}` — equal to a plain
    sibling — while traefik disabled the router for "empty args for matcher
    Host". A silent drop inside a reader is the same fail-open as a silent
    exemption: the refusal belongs where the shape is decided.
    """
    if rule is None:
        return frozenset()
    args = _rule_host_args(rule)
    if args is None:
        return frozenset()
    return frozenset(args)


def _router_rule(block: str) -> str | None:
    """A file-provider router's `rule:` scalar, or None when it declares none.

    Not `_block_scalar`: that reader takes one `\\S+` token, and every rule in
    dynamic.yml.j2 holds a SPACE inside its Jinja (`Host(`plex.{{ domain }}`)`),
    so it would return `"Host(`plex.{{` and the backtick would never close. The
    whole rest of the line is the scalar; `_yaml_unquote` takes the one quote
    layer YAML owns, so `"…"` and `'…'` are the same rule (row C3).

    THE SEPARATION SPACE IS YAML'S, NOT PYTHON'S (Step-5c F1, round 4). This was
    `[^\\S\\n]*` on both sides of the key, and YAML's `s-white` is `s-space |
    s-tab` (YAML 1.2 §6.1): after `rule:` a U+00A0 is scalar CONTENT, not a
    separator, so the reader skipped it and unquoted a clean rule while the value
    the parser hands traefik begins with a character its rule lexer calls illegal
    (logs/red-step05c-rework-r4-gowhitespace-PRE.log N9/N10, `PASS: 42/42`). A TAB
    is a separator and stays one (row C4). The indentation side keeps `[ \\t]` too:
    a tab there is invalid YAML, and traefik refuses the WHOLE document for it —
    loud, so it is not a vector this reader has to model, only one it must not
    silently accept.
    """
    m = re.search(r'(?m)^[ \t]*rule:[ \t]*(.*)$', block)
    return _yaml_unquote(m.group(1)) if m else None


def _compose_service_names(body: str) -> list:
    """Every compose service key, in file order.

    Through `_compose_services_block` + `_yaml_key`, so an `x-` extension field's
    contents cannot masquerade as a service and the quoted spellings count — the
    same two rules `_compose_service_block` is built on.
    """
    return [
        key[1]
        for key in (_yaml_key(line) for line in _compose_services_block(body).splitlines())
        if key and key[0] == 2
    ]


def _dynamic_router_names(body: str) -> list:
    """Every file-provider router key under `http.routers:`, in file order."""
    return [
        key[1]
        for key in (_yaml_key(line) for line in _routers_block(body).splitlines())
        if key and key[0] == 4
    ]


def _label_router_names(labels: dict) -> list:
    """Router names one compose service's labels define, deduplicated.

    The name is the segment between `routers.` and the NEXT dot, which is where
    traefik's own label grammar splits it — so `routers.whoami.tls.certresolver`
    names `whoami`, not `whoami.tls`.
    """
    return sorted({
        m.group(1)
        for k in labels
        for m in [re.fullmatch(r'traefik\.http\.routers\.([^.]+)\.(.+)', k)]
        if m
    })


def _compose_router_service(labels: dict, router: str) -> str | None:
    """The backend a DOCKER-provider router lands on, or None when unreadable.

    MEASURED against the pinned `traefik:v3.7.5` with the real docker provider,
    one container per row, every container removed in a `finally`
    (logs/calibration-step05c-web-twin-service-default.py / .log, 7/7) — because
    the delivered websecure siblings (`routers.whoami`, `.homepage`, …) carry no
    `.service` label at all, so "the sibling's service" is a RUNTIME DEFAULT and
    a guard that encodes one it has not measured is this loop's own recurring
    defect:

      A  no `.service`, ONE `traefik.http.services.<n>.*` on the same container
         -> the router lands on that DECLARED service (`rA -> declaredA`)
      B  an explicit `.service` wins over a second declared service
      C  no `.service`, TWO declared services -> the router is ABSENT from
         `/api/http/routers` entirely. Ambiguity is LOUD, so this returns None
         and the caller reddens rather than guessing which one
      D  no `.service`, ZERO declared -> a name derived from the CONTAINER
         (`rD -> cal05c-d`), which no line of compose.yml.j2 states. Returned as
         the CONTAINER_DERIVED_SERVICE marker so a twin and a sibling that are
         BOTH silent still compare equal — they do land on one backend — while a
         twin that names something explicit does not compare equal to it
      E  the delivered shape (silent sibling + `.service=<s>` twin) resolves both
         routers to the ONE declared service
    """
    explicit = labels.get(f"traefik.http.routers.{router}.service")
    if explicit:
        return explicit
    declared = sorted({
        m.group(1)
        for k in labels
        for m in [re.fullmatch(r'traefik\.http\.services\.([^.]+)\.(.+)', k)]
        if m
    })
    if len(declared) == 1:
        return declared[0]
    return CONTAINER_DERIVED_SERVICE if not declared else None


def _twin_defects(sibling_exists, twin_hosts, sib_hosts, twin_svc, sib_svc) -> list:
    """Why one `<svc>-web` twin does not double its sibling; empty = it does.

    Reasons rather than a bool, for the reason `_declares_key` returns a list:
    "the twin answers for another host" and "this guard cannot read what it
    answers for" want different fixes, and a bare False says neither.

    "pins no Host() disjunction" is the one phrase for both ways a rule can be
    unreadable, because they are one state: no `Host(...)` at all, and a boolean
    expression `_rule_host_args` refuses (`!Host(…)`, `&& PathPrefix(…)`, a
    parenthesised group) both mean this reader has NO set of hosts for that side
    and must not compare one.
    """
    reasons = []
    if not sibling_exists:
        reasons.append("no websecure sibling")
    if not twin_hosts:
        reasons.append("twin pins no Host() disjunction")
    if not sib_hosts:
        reasons.append("sibling pins no Host() disjunction")
    if twin_hosts and sib_hosts and twin_hosts != sib_hosts:
        reasons.append(f"hosts {sorted(twin_hosts)} != {sorted(sib_hosts)}")
    if twin_svc is None or sib_svc is None:
        reasons.append(f"unreadable service (twin={twin_svc!r}, sibling={sib_svc!r})")
    elif twin_svc != sib_svc:
        reasons.append(f"service {twin_svc!r} != {sib_svc!r}")
    return reasons


def test_web_twins_double_their_websecure_sibling() -> bool:
    """Every `<svc>-web` twin answers for its SIBLING'S host, on its BACKEND.

    Step-3a round-12's finding, and it is symmetric and pre-existing rather than
    anything round 11 introduced: `test_tunnel_web_routers_present` asks each
    twin four clauses — entrypoint, service, allowlist, no-tls — and asks NONE of
    them WHICH HOST it answers for. The `rule` was unasked of every twin, compose
    AND file provider, so ordinary one-line edits were `PASS: 41/41` on the full
    guard with the real templates (logs/review-step03a-r12-rule-clause.log, 5/5):
    `whoami-web` -> `home.<domain>`, `prometheus-web` -> `plex.<domain>`,
    `traefik-dashboard-web` -> `plex.<domain>`. The negative control is the same
    file: the WEBSECURE routers' rules ARE pinned, so the same edit one router up
    is RED.

    IT IS THE ONE FINDING IN THIS WAVE WITH A MEASURED LIVE CONSEQUENCE. With the
    dashboard's web twin repointed at the ONE public host, on the pinned
    `traefik:v3.7.5` from a client outside every allowlisted range,
    `plex.<domain>:80/api/http/routers` answers **HTTP 403** where the delivered
    tree answers **301** — the WAN plex HTTP->HTTPS upgrade is dead — and
    `traefik.<domain>:80` answers **HTTP 404**, the tunnel host having lost its
    plain-HTTP router entirely (logs/review-step03a-r12-public-router.log, S3).
    Never a 200: this is availability, not a WAN fail-open.

    AND THE `service` CLAUSE OF `plex-web` COMES WITH IT (the task's S1), because
    the claim is one claim. `plex-web` is the twin of the ONE router that carries
    no allowlist, and `service: api@internal` on it is `PASS: 41/41` today —
    latent only because the pinned `redirect-to-https` middleware still 301s. The
    two-step version (service repointed AND the redirect deleted) reaches HTTP 200
    with the whole router table from outside every allowlisted range, and it is
    the redirect pin one clause over that is holding that door.

    SO THE ROW IS QUANTIFIED OVER WHAT IT DISCOVERS, NOT OVER A ROSTER. Every
    round of this file that asked one member fewer clauses than its peers has been
    rejected for it — the file provider's twin was asked clause (1) only (round
    11), and `plex-web` is asked nothing at all today. Both providers are walked
    the same way here: names off the document, sibling = the name minus `-web`,
    and every clause read from the router's OWN carrier (`_service_label_map` for
    docker, `_router_block` for the file provider), so a label on a sibling
    service and a neighbouring router's body cannot answer.

    THE COMPARISON IS STRUCTURAL, NOT A LITERAL. `Host(...)` sets are compared
    twin-to-sibling, so renaming a host on both sides is GREEN (row C2), adding an
    `|| Host(...)` alternative to both is GREEN (C4), and re-quoting the scalar is
    GREEN (C3) — while every one-sided edit is RED. An empty set on EITHER side is
    refused before any comparison: two empties are equal, and calling that
    agreement is the fail-open M11 (both rules deleted) and M9 (the twin's rule
    deleted) exist to catch.

    AND A RULE IS A BOOLEAN EXPRESSION, SO THE OPERATORS ARE PART OF THE CLAIM.
    `_rule_host_args` reads only a disjunction of `Host(...)` calls and refuses
    every other expression to that same empty set, because a set of arguments
    alone cannot tell `Host(`h`)` from its exact complement `!Host(`h`)`, nor
    from `Host(`h`) && PathPrefix(`/x`)` which answers for `h` under one path
    only. Both are ACCEPTED by the pinned `traefik:v3.7.5` and answer HTTP 404
    for the host the twin exists to double (rework round 2, review F1;
    logs/critic-step05c-rule-operator-runtime.log 7/7,
    logs/red-step05c-rework-r2-operators.log rows N1-N11) — silent, so the
    sentence at the top of this docstring would otherwise be false while the row
    was green. `||` between `Host(...)` alternatives stays readable, which is
    what keeps C4 a legitimate edit rather than a refusal.

    ANTI-VACUITY IS THE FLOOR PLUS THE COUNT. The row prints how many twins it
    examined and reddens when the discovery loses any twin the delivered tree has
    (`EXPECTED_WEB_TWINS`), so "found nothing, therefore nothing is wrong" is not
    a state this can pass in.
    """
    compose = _read(COMPOSE)
    dynamic = _read(DYNAMIC)
    examined, failures = [], []

    for service in _compose_service_names(compose):
        labels = _service_label_map(compose, service)
        routers = _label_router_names(labels)
        for twin in [r for r in routers if r.endswith(WEB_TWIN_SUFFIX)]:
            sibling = twin[: -len(WEB_TWIN_SUFFIX)]
            examined.append(twin)
            reasons = _twin_defects(
                sibling in routers,
                _rule_hosts(labels.get(f"traefik.http.routers.{twin}.rule")),
                _rule_hosts(labels.get(f"traefik.http.routers.{sibling}.rule")),
                _compose_router_service(labels, twin),
                _compose_router_service(labels, sibling),
            )
            if reasons:
                failures.append(f"{twin}@docker({'; '.join(reasons)})")

    router_names = _dynamic_router_names(dynamic)
    for twin in [r for r in router_names if r.endswith(WEB_TWIN_SUFFIX)]:
        sibling = twin[: -len(WEB_TWIN_SUFFIX)]
        examined.append(twin)
        twin_block = _router_block(dynamic, twin)
        sib_block = _router_block(dynamic, sibling)
        reasons = _twin_defects(
            sibling in router_names,
            _rule_hosts(_router_rule(twin_block)),
            _rule_hosts(_router_rule(sib_block)),
            _block_scalar(twin_block, "service"),
            _block_scalar(sib_block, "service"),
        )
        if reasons:
            failures.append(f"{twin}@file({'; '.join(reasons)})")

    missing = sorted(EXPECTED_WEB_TWINS - set(examined))
    ok = bool(examined) and not missing and not failures
    print(
        f"{'OK' if ok else 'FAIL'}: every <svc>-web twin answers for its sibling's host "
        f"on its backend (examined={len(examined)}, missing={missing}, failures={failures})"
    )
    return ok


def test_templates_render_line_for_line() -> bool:
    """No template this guard reads carries Jinja that can MANUFACTURE a line.

    Step-3a F1, round 9, and the one clause that is about the whole module rather
    than about a region. Round 9's review reached past `_resolvable_key` entirely:

        #{{ '\\n' }}PLEX_TOKEN=stolen-shadow

    is ONE line to `_strip_comments`, which drops it as a comment, and TWO to the
    runtime — a bare `#`, then a live assignment that compose's dotenv takes LAST.
    No key ever carries a delimiter because no key is ever presented.

    THE CARRIER IS THE NEWLINE, NOT THE `#`, AND THAT DECIDED WHERE THIS GOES.
    The review priced a fix inside `_strip_comments` ("strip only when the
    comment's Jinja is a simple reference"). I built its rows first and then three
    more with no `#` anywhere, and the extra rows are GREEN on the round-8 tree at
    `PASS: 39/39` (logs/red-step03a-line-manufacture-pre.log):

        V1  .env       SHADOW_NOTE=harmless{{ CHR10 }}PLEX_TOKEN=stolen-shadow
        V2  compose    - SHADOW_NOTE=harmless{{ CHR10 }}      - PLEX_ADDR=http://stolen:1
        V3  compose    - shadow.note=harmless{{ CHR10 }}      - traefik.http.routers
                         .prometheus.middlewares=security-headers@file

    `_strip_comments` is never consulted on any of the three: the guard files one
    unpinned key (`SHADOW_NOTE`, `shadow.note`) and reads the delivered line above
    it as it always did. V3 is the Error-1000 class — prometheus's
    `internal-allowlist` gone from the effective label map — with no comment
    involved. A fix at `_strip_comments` closes N1-N3 and leaves those standing.

    So the claim is made where the readers' shared PRECONDITION lives: every
    reader in this module — `_strip_comments`, `_list_entries`, `_kv_entries`,
    `_env_assignments`, `_service_key_lines`, `_service_published_ports`,
    `_indented_block`, `_declares_key`, and the TEN that never call
    `_strip_comments` at all (leg S of the same log lists them from the guard's
    own AST) — decides STRUCTURE from TEXT, and every one of them
    is sound exactly when one template line renders to one line. Asking each in
    turn "can Jinja manufacture or destroy this?" is what has cost five rounds
    (rounds 5-9, one function each). Asked ONCE, here, it covers all of them.

    THE RULE, and it is about what the TEMPLATE SHOWS rather than what Jinja does:
    a construct is line-bounded when its output is either one variable's value or
    literal text the template spells out in full. That is a bare reference,
    optionally `| default(<literal>)`, plus `if`/`elif`/`else`/`endif` — which
    select template text and never produce any, AND (round 10) must own their line
    at column 0 with no whitespace-control marker, because
    `ansible.builtin.template` renders with `trim_blocks=True` and a block tag
    beside content moves the line boundary even though the statement emits
    nothing. `_unbounded_block_tag` carries that half, its three clauses and the
    rows behind them. Everything else — a string
    literal carrying an escape, any other filter, a call, `{% for %}`,
    `{% include %}`, `{% set %}`, a `{# #}` comment, a construct spanning lines,
    an unclosed one — is refused. Not "detect the newline": a guard that reads
    template TEXT cannot evaluate Jinja, so the honest move is to refuse the text
    it cannot bound.

    PRICE, counted on the delivered tree and printed construct by construct:
    ZERO. 77 constructs across the six templates — 70 bare references, 5
    `| default('')` in env.j2's vault hops, and dynamic.yml.j2's one
    `{% if acme_resolver == 'le-dns-cf' %}` / `{% endif %}` pair — all
    line-bounded (logs/green-step03a-line-manufacture-price.log, leg P). Leg V of
    the same log is the vacuity half: ten probes, one per clause, each rejected
    for its OWN reason, and five ACCEPT probes covering every delivered shape, so
    no clause is either idle or a false red.

    ROUND 10 — AND THE RENDERER IS PART OF THE CLAIM. The clause above about
    `if`/`elif`/`else`/`endif` was measured under the wrong renderer: round 9's
    battery rendered with `jinja2.Environment(keep_trailing_newline=True)` and NO
    `trim_blocks`, while `ansible.builtin.template` renders with
    `trim_blocks=True` — the delivered dynamic.yml.j2 is 109 template lines and
    107 rendered lines, so the instrument disagreed with deployment on the
    DELIVERED tree before any mutation. Every row here is re-measured at the
    deployed settings (`trim_blocks=True, lstrip_blocks=False,
    keep_trailing_newline=True`, pinned from ansible-core's own source in leg R of
    logs/red-step03a-trim-blocks-post.log), which is the only reason the merge
    rows T1/T1b/T2/T4 are visible at all. `_unbounded_block_tag` holds the fix and
    the rows; price stays ZERO because the delivered pair is already column-0 and
    marker-free.

    TWO RESIDUALS, both stated because neither is closed:

    (1) A bare `{{ var }}` whose VARIABLE VALUE contains a newline manufactures a
        line this pin cannot see, since it reads text and the value is not in the
        text. Every delivered construct is a reference, so this is the whole
        remaining surface of the class, and it needs a hostile VALUE rather than
        hostile template text. The review disclosed the same residual against its
        own proposal; it is a property of reading templates as text, not of
        either fix.

    (2) DESTRUCTION — `{% if False %}` around a line the guard pins — is the other
        direction and is NOT closed by this clause, because dynamic.yml.j2 spells
        the conditional legitimately. Measured rather than assumed at the two
        sites the shadow would use (same log, rows D1/D2): both fail CLOSED
        already, the `.env` because `_env_assignments` poisons on a key half
        carrying `{%`, the `volumes:` entry because `_service_mount_map` does.
        That is two sites, not a proof; it is an enumeration gap and it is named
        as one.

    A future template that genuinely needs a `{% for %}` will redden this. That is
    the intended reading: the response is to teach this clause what the loop can
    emit, not to drop it — the alternative is a guard whose line numbers are a
    guess.
    """
    offenders = {}
    for path in LINE_READ_TEMPLATES:
        found = _line_manufacturing_jinja(_read(path))
        if found:
            offenders[path.name] = [f"L{n}: {c!r} — {why}" for n, c, why in found]
    ok = not offenders
    print(
        f"{'OK' if ok else 'FAIL'}: templates render line-for-line "
        f"(files={len(LINE_READ_TEMPLATES)}, offenders={offenders})"
    )
    return ok


def test_no_undeclared_conditional_region() -> bool:
    """Every line this guard reads as evidence is a line the renderer EMITS.

    Step-3a F1, round 11, and it is the OTHER direction of round 10's clause.
    `_unbounded_block_tag` closed the MERGE direction — a `{% %}` tag may no
    longer share its line, sit indented, or carry a whitespace-control marker —
    and by refusing every other spelling it makes the COLUMN-0 STANDALONE TAG the
    one accepted carrier. That is precisely the shape that DELETES the lines it
    wraps, so narrowing the spellings BLESSED the surviving one.

    Rounds 9 and 10 each disclosed "destruction is not closed" and each bounded it
    at the same two sites round 9 happened to use — the `.env` (`_env_assignments`)
    and compose `volumes:` (`_service_mount_map`) — both of which fail closed on
    `{%` poison that predates either round. THE THIRD FILE WAS NEVER ASKED, and it
    is the one where a column-0 line is ORDINARY: dynamic.yml.j2 is in
    `LINE_READ_TEMPLATES`, its structure lives at column 0, it SHIPS such a gate at
    line 84, and `_router_block`'s own docstring says the gate lines "are not keys,
    so they stay inside the owning router's slice" — this guard is not blind to
    them, it is TAUGHT TO READ STRAIGHT THROUGH. A disclosed residual has to be
    bounded at every site the readers cover, not at the two the last rows used.

    MEASURED on the real template, full guard, reverted in a `finally`
    (logs/red-step03a-r11-unasked-clauses.log, rows X1-X3), with the gate spelled
    the way this repo spells its own (`{% if acme_resolver == 'le-http' %}`, no new
    variable required):

        X1  traefik-dashboard-web's `middlewares:` block wrapped
            guard `PASS: 40/40`  |  rendered `middlewares=None`, and on the pinned
            traefik:v3.7.5 a client OUTSIDE all four allowlisted ranges gets
            `GET /api/http/routers` -> HTTP 200 with the whole router table, where
            the delivered tree answers 403. That router is on the `web`
            entrypoint and :80/:443 are WAN port-forwarded to this host.
        X2  the same on the websecure twin      X3  the middleware DEFINITION

    THE DECLARATION IS AN INVENTORY, NOT A MEMBERSHIP TEST. Rounds 6 and 7 both
    rejected absence pins bounded by an enumeration because they fail open past
    the enumeration's edge; the same argument applies one level in, to a
    declaration keyed on a SIGNATURE rather than on the region itself, and both
    edges were measured before this shape was chosen (rows X4 and X6 — a
    byte-identical duplicate defeats a set, and a same-condition/same-count/
    same-first-line region wrapping different lines defeats a signature key).
    Neither is a severity row and neither is claimed as one: the declared
    condition is TRUE on the delivered tree, so a region carrying it EMITS. The
    severity is X1-X3, where a FALSE condition deletes.

    BOUNDED, AND THE FIX IS NOT CREDITED WITH THEM: the same column-0 false gate
    in compose `labels:` (row B1) is already fail-closed, and row X5 — the
    delivered region replaced by a same-signature decoy — is already caught by
    `test_traefik_dashboard_wildcard_domains`, which reads the `sans` it moved.
    This clause reddens X5 too, on its own terms, which is the point of keying on
    the body rather than borrowing another check's coverage.

    PRICE: ZERO. Exactly one `{% if %}` region exists across the six line-read
    templates, and it is the declared one. A future gate reddens this until it is
    declared here — the intended reading, because declaring it means saying out
    loud which pinned lines now depend on a branch this guard cannot evaluate.

    NOT CLOSED, and stated rather than implied: the truth value of the condition.
    Nothing in this module evaluates Jinja, so a region wrapping a pinned line is
    judged by its declaration and never by what it renders to. `le-dns-cf` is
    pinned in group_vars by `test_acme_resolver_is_dns_cf`, which is the only
    reason the declared region is known to emit, and ansible's variable precedence
    means an inventory-level override is outside what any of these three checks
    can see.
    """
    outstanding = list(DECLARED_CONDITIONAL_REGIONS)
    offenders = []
    for path in LINE_READ_TEMPLATES:
        regions, unbalanced = _conditional_regions(_read(path))
        offenders += [f"{path.name}:{n} {why}" for n, why in unbalanced]
        for line, cond, wrapped in regions:
            key = (path.name, cond, wrapped)
            if key in outstanding:
                # One declared region accounts for exactly ONE region found.
                outstanding.remove(key)
                continue
            first = next((w.strip() for w in wrapped if w.strip()), "")
            offenders.append(
                f"{path.name}:{line} `{cond}` wraps {len(wrapped)} line(s) "
                f"from {first!r} — undeclared"
            )
    missing = [f"{name}: `{cond}`" for name, cond, _ in outstanding]
    ok = not offenders and not missing
    print(
        f"{'OK' if ok else 'FAIL'}: no undeclared conditional region in the "
        f"{len(LINE_READ_TEMPLATES)} line-read templates "
        f"(declared={len(DECLARED_CONDITIONAL_REGIONS)}, offenders={offenders}, "
        f"missing_declared={missing})"
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
        test_prometheus_histogram_buckets_tuned(),
        test_rendered_configs_reach_the_service_that_reads_them(),
        test_relabel_allow_list_prices_every_field_it_excludes(),
        test_pve_scrape_job_is_multi_target(),
        test_pve_exporter_service_block(),
        test_pve_token_sourced_from_vault(),
        test_pve_non_secret_coordinates_in_defaults(),
        test_plex_scrape_job_is_single_target(),
        test_plex_exporter_service_block(),
        test_plex_token_sourced_from_vault(),
        test_plex_node_exporter_scrape_job(),
        test_blackbox_exporter_service_block(),
        test_blackbox_modules_are_the_three_plex_probes(),
        test_blackbox_sessions_probe_carries_the_vault_token(),
        test_the_blackbox_reader_refuses_exactly_what_the_exporter_refuses(),
        test_blackbox_scrape_jobs_probe_plex(),
        test_blackbox_scrape_cadence_is_what_prometheus_runs(),
        test_prometheus_rule_files_names_the_render(),
        test_plex_blip_alert_rules_are_design_5_3(),
        test_every_alert_carries_severity_and_summary(),
        test_absent_series_doors_cover_every_alert_input(),
        test_plex_blip_rules_render_is_validated_against_the_pinned_image(),
        test_prometheus_retention_outlives_the_blip_window(),
        test_prometheus_render_is_world_read_only_unpaid(),
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
        test_web_twins_double_their_websecure_sibling(),
        test_templates_render_line_for_line(),
        test_no_undeclared_conditional_region(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
