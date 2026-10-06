# Context — plex-monitoring

## Source
- **Type:** existing PDD implementation directory
  (`.agents/planning/2026-07-29-plex-monitoring/implementation/plan.md`, 4 numbered steps).
- **Original request:** "Implement the steps outlined in
  `.agents/planning/2026-07-29-plex-monitoring/implementation/plan.md`" — add Prometheus/Grafana
  observability for Plex: Traefik latency histogram buckets, a Proxmox PVE exporter, a Plex Media
  Server exporter, and Grafana dashboards over the result.
- **Upstream research/design:** `../research/*.md`, `../design/detailed-design.md`, `../summary.md`.
  The design is scoped to net-new work only; Traefik metrics, Prometheus, Grafana, node_exporter
  and cAdvisor already exist and are already scraped.

## Repo Patterns (verified on disk, 2026-07-29)
- **Everything is a Jinja template under one role:** `ansible/roles/docker_host/templates/` holds
  `traefik.yml.j2`, `compose.yml.j2`, `prometheus.yml.j2`, `env.j2`, `dynamic.yml.j2`,
  `grafana-dashboards.yml.j2`, `grafana-datasource.yml.j2`.
- **Traefik metrics block already exists** — `traefik.yml.j2:59-64`:
  `metrics.prometheus` with `entryPoint: metrics`, `addEntryPointsLabels`, `addServicesLabels`.
  The `metrics` entrypoint is `:8082`, internal to the compose network, never routed.
- **Prometheus scrape jobs** live in `prometheus.yml.j2` as a flat `scrape_configs` list; existing
  jobs: `prometheus`, `node-exporter`, `cadvisor`, `traefik` (target `traefik:8082`). A new exporter
  = one more `job_name` + `targets` entry, service-name addressed on the compose network.
- **Scrape-only containers** (`node-exporter`, `cadvisor`, `compose.yml.j2:177-197`) carry NO Traefik
  labels and are not published to the host — the model for `pve-exporter` and `plex-exporter`.
- **Image pins are variables**, not literals: `docker_host_<svc>_image` in
  `ansible/roles/docker_host/defaults/main.yml` (e.g. `docker_host_cadvisor_image:
  gcr.io/cadvisor/cadvisor:v0.55.1`). New exporters must follow this and be pinned to a tag.
- **Secrets:** Ansible Vault (`ansible/group_vars/all/vault.yml`) → `env.j2` →
  compose env file at mode 0600. Pattern in `env.j2`:
  `CF_DNS_API_TOKEN={{ vault_cloudflare_dns_api_token | default('') }}`. Never a committed literal;
  always `| default('')` so an unset vault var renders empty instead of failing the play.
- **Gate:** `just test` → `scripts/run_gate.py`, which runs EVERY `scripts/test_*.py` standalone
  (`python <file>`, exit code is the verdict; the glob auto-includes new files), then
  `tofu fmt -check` + `validate`, then `ansible-lint --offline` + `ansible-playbook --syntax-check`.
  Shape tests are stdlib-only, dual-mode (module-level `test_*() -> bool` + `main() -> int`).
- **Traefik template guard:** `scripts/test_traefik_config_shape.py` is the existing shape test over
  `traefik.yml.j2` / `dynamic.yml.j2` / `compose.yml.j2` — Step 1's guard belongs there, not in a new
  file. Its stated convention: anchor regexes on the INNER attribute (the actual key/value), never on
  a section opener, so an empty stub cannot satisfy the check.
- **Deploy:** `just play` (ansible-playbook site.yml) from the repo root. `just provision` also runs
  tofu apply — NOT wanted here; nothing in this project touches infrastructure.

## Integration Points
| Step | Files touched | Live surface |
|------|---------------|--------------|
| 1 | `traefik.yml.j2`, `scripts/test_traefik_config_shape.py` | Traefik restart on CT 111 |
| 2 | `vault.yml`, `env.j2`, `compose.yml.j2`, `prometheus.yml.j2`, `defaults/main.yml`, shape test | new container + PVE API user on the hypervisor |
| 3 | same set as Step 2 | new container + Plex token |
| 4 | `grafana/dashboards/*.json` under `{{ docker_host_project_dir }}`, role tasks/templates | Grafana provisioner (30s reload) |

## Acceptance Criteria
1. Every template change is rendered by `just play` without hand-editing anything on the host.
2. `just test` (the full offline gate) is GREEN after every task — new shape-test checks included.
3. Each new shape-test check is proved NON-VACUOUS by a mutation: break the template value it
   guards, the check must go RED; restore, GREEN. Guards must pin values and their enclosing block,
   not merely the presence of a key that already exists.
4. Secrets never appear as literals in git — vault-sourced, `| default('')`, rendered into `.env`.
5. Live verification (Prometheus target UP, metric present with the expected labels) is an
   OPERATOR step, recorded in `progress.md` under `## Verification Notes` with the actual query and
   output — never inferred from a successful playbook run.

## Constraints
- **Operator gates are real and are NOT agent-closable.** `just play` deploys to the live household
  Plex stack, and Steps 2/3 need credentials only the operator can mint (Proxmox `prometheus@pve`
  API token; Plex auth token). RObot/Telegram is unwired in this repo — an agent cannot ask
  interactively, so operator work is filed as an explicit OPERATOR task the operator closes.
- No infrastructure changes: no `tofu apply`, no CT create/recreate, no changes to CT 110 (Plex).
- New exporters are scrape-only: no Traefik labels, no published host ports, no new routes.
- Image tags are pinned in `defaults/main.yml`; no `:latest`.
- Do not re-open or re-mutate files closed by the unrelated in-flight `plex-optimization` work
  (`scripts/measure_plex_latency.py`, `docs/runbooks/plex-latency-baseline.md`).

## Rendering is outside the offline gate (found in Step 2a)

`just test` runs `ansible-lint --offline` and `ansible-playbook --syntax-check`, and neither
RENDERS `roles/docker_host/templates/*.j2`. A malformed YAML block or a Jinja typo inside a
template therefore passes the entire gate and first fails during an operator's `just play` —
the one run this loop cannot repeat. When a step adds or edits a template block, render it and
`yaml.safe_load` the result before handing the increment on. `logs/render-step02a-driver.py` is
the working pattern: `jinja2.Environment(trim_blocks=True, lstrip_blocks=True,
undefined=ChainableUndefined)` over `role/defaults/main.yml` plus the play-level vars
(`domain`, `acme_resolver`, `ansible_managed`), then assertions on the PARSED structure.
jinja2/pyyaml are not in `.venv`; they ship with ansible-core, at
`~/.local/share/mise/installs/pipx-ansible-core/latest/venvs/ansible-core/bin/python`.

## A guard clause can be satisfied by the comment that documents it (found in Step 2a)

These templates carry comments that NAME the flags and env vars the shape guard pins, so a
check matching free text over a sliced block passes on its own documentation. The Step-2a
mutation battery caught exactly that: deleting `command: [--no-collector.config]` left the gate
GREEN. `_strip_comments` in `scripts/test_traefik_config_shape.py` is the fix; new compose/YAML
clauses should read the stripped block and anchor on a real entry (`^\s*-\s*<value>$`), not on
substring presence.

## Rendering a config is not delivering it — and the file must be READABLE once delivered

Two standing traps in this role, both found in Step 2a's review round 2.

**Delivery.** `docker compose up -d --remove-orphans` (`tasks/main.yml`, the only task that
touches containers) does NOT touch a container whose own spec is unchanged. Every config this
role renders into `docker_host_project_dir` is a read-only BIND MOUNT, so editing one changes no
compose spec at all and the running process keeps the config it parsed at start. Prometheus has
no `--web.enable-lifecycle`, so `POST /-/reload` answers 403. **When a step's deliverable is
"service S now reads config C", the increment needs a `notify:` and a handler, and the guard must
pin that PATH — the render + `yaml.safe_load` drivers prove syntax and can never prove delivery.**

**And the restart is only the LAST hop** (round 3). Delivery is `dest` → the bind mount's host
side → its container side → the flag that names that path → the restart. Pinning only the restart
is the same vacuity one hop out, measured: moving `dest` off the mount source makes docker invent
a DIRECTORY at the missing host path and the container cannot start at all; DROPPING the mount is
silent and worst — Prometheus boots clean on the image's own default config and scrapes only
itself, every job gone, target UP, nothing erroring (`logs/delivery-step02a-f1-round3.log`, leg D);
a different file mounted there is a crash loop; `--config.file` elsewhere is the same class.
`test_rendered_configs_reach_the_service_that_reads_them` walks all of it per row of
`RELOAD_CONTRACT`; adding a render task means adding a row. Write the container-side hop as an
AGREEMENT where the image takes a config flag (check the flag against the mount's own target, not
against a literal) and as a pinned `default_path` where it does not — traefik reads
`/etc/traefik/traefik.yml` with no flag naming it, so there the path IS the contract.

**A `notify:` one indent too deep is invisible to the whole gate.** Inside the template module's
args it passes `ansible-lint --profile production` AND `ansible-playbook --syntax-check`, and
fails only at the operator's `just play` as an unsupported module parameter. The guard therefore
matches `notify:` at the task's own key indent (the module key's column), not anywhere in the
task block.

**Readability.** The handler is only half of it. Container images here run as different uids:
`traefik` runs as root (0640 root:root is fine), `prom/prometheus` runs as `nobody` (uid 65534,
`docker run --entrypoint id prom/prometheus:v3.12.0`) and CANNOT open a 0640 root:root file — it
exits on "Error loading config … permission denied" and `restart: unless-stopped` makes it a
crash loop. So the mode is part of the delivery contract and `RELOAD_CONTRACT` carries it per row.
Only the file's own mode matters, not the parent dir's: the mount names the file and traversal
happens on the host (verified with the parent still 0750).

**The other renders, measured rather than assumed** (`docker run --rm --entrypoint id <image>`):
`grafana/grafana:13.1.0` is `uid=472(grafana) gid=0(root)` and
`ghcr.io/gethomepage/homepage:v1.13.2` is `uid=0(root)`, so 0640 **root:root** is readable for
both — the GROUP bit carries them, and only Prometheus's `nobody:nobody` falls outside it. So the
mode half of this trap is Prometheus-only today. Do not generalise it to a blanket 0644; measure
the image's uid/gid, then pick the mode.

**THE MODE TRAP IS NOT HYPOTHETICAL — IT IS THE CURRENT PRODUCTION STATE.** An earlier version
of this section said the mode "only started mattering once the handler existed, because before it
the file was never re-read". False, and the live host says so. Read-only on 192.168.1.111,
2026-07-29: `stack-prometheus-1` is `Restarting`, **RestartCount 20801**, created 2026-07-15,
logging `open /etc/prometheus/prometheus.yml: permission denied` once a minute;
`/opt/stack/prometheus/prometheus.yml` is `640 root:root`; the TSDB volume has been empty since
28 May; `prometheus.yoonnation.com` answers a Traefik 404 (the docker provider drops a restarting
container, so its router does not exist) while every other dashboard routes. `restart:
unless-stopped` had been re-reading that file every ~60 s all along. So Step 2a's `0644` is the
**repair of a live two-week outage**, not a precaution taken on account of the new handler, and
both operator gates now say so. **The method matters more than the fact: the live host is one
read-only command away** — `ansible docker-host -i inventory/hosts.yml -m ansible.builtin.shell
-a '<cmd>'` from `ansible/`. Note `-a` is Jinja-templated, so `{{ .Field }}` in a `--format`
string dies with "unexpected '.'"; pipe `docker inspect` into `python3 -c` instead. When a step's
deliverable is "service S now sees config C", go look at S.

**Still open, for whoever does Step 4.** The four Grafana/Homepage renders have NO `notify:`
either, so a provisioning change reaches a running Grafana on the next unrelated recreate and not
before. Step 4 installs a dashboard JSON into that same directory and will hit the delivery half
of this. Not fixed in Step 2a — out of its scope.

**IN A REGEX GUARD OVER YAML, A FLOW-VS-BLOCK GAP IS HARMLESS ON A PRESENCE PIN AND FATAL ON AN
ABSENCE PIN.** Every clause in `scripts/test_traefik_config_shape.py` that requires something to be
there fails **closed** when it cannot see a spelling — an inline `volumes:` makes `_indented_block`
return `""` and the delivery row goes RED, which is a false RED and safe. A clause that requires
something to be **absent** fails **open** through the identical gap. `no_ports` was
`re.search(r'(?m)^\s*ports:\s*$', block) is None`, which anchors the key to the end of its line, so
`ports: ["9221:9221"]` was invisible: guard PASS 36/36, gate 35/35, and the state renders,
`yaml.safe_load`s and passes `docker compose config` (measured, `logs/calibration-step02a-f1-round4.log`
leg A) — i.e. deployable, so `just play` ships it rather than catching it. The same regex guarded
cloudflared's "zero inbound surface". **Method: grep every `is None` / `not in` clause in a shape
guard and ask which YAML spellings it cannot see.** The fix is a helper that reads all spellings
compose accepts and returns `None` only when the key is genuinely absent
(`_service_published_ports`), so the pin is on the KEY rather than on a non-empty list; say in the
docstring that pinning the key is stricter than the runtime, and give the mutation row the `strict`
class. Internal evidence beats a style argument here: `_service_command_args` in the same file
already handles both spellings and says so in its docstring.

**AND ONE LEVEL UP, WHICH IS WHERE THAT ADVICE RUNS OUT: AN ABSENCE PIN IS BOUNDED BY THE
ENUMERATION BEHIND IT — PIN THE INVARIANT THE DOCSTRING STATES, NOT THE KEY YOU THOUGHT OF.**
Reading every spelling of `ports:` is still an enumeration, and the invariant these two clauses
state is REACHABILITY. `network_mode: host` declares no `ports:` key at all, so
`_service_published_ports` returns `None`, `no_ports` is True and the guard passes 36/36 — while
the real image binds `LISTEN *:9221` in the HOST netns and an anonymous caller at this box's LAN
address gets `/metrics` HTTP 200, 3174 bytes (measured, `logs/calibration-step02a-f1-round5.log`
leg B, against a compose-network control that answers 000 with no `:9221` line in `ss -ltn` at
all). The idiom is not hypothetical: node-exporter, the neighbour these services are written from,
already carries `pid: host` one service up in the same file. **The fix is a shape change, not
another spelling: turn the absence pin into a key ALLOW-LIST** (`_service_keys` + `SCRAPE_ONLY_KEYS`
/ `OUTBOUND_ONLY_KEYS`). An allow-list fails CLOSED, so `network_mode`, `networks`, `expose`,
`hostname` and any compose key that does not exist yet all redden without anyone having enumerated
them — the same "count what is there beats find what you care about" move as the data-row count in
`test_plex_latency_runbook_shape.py`. Keep the specific pin (`no_ports`) alongside it: two pins that
fail differently, each proven SEPARATELY by relaxing the other in the guard, because one `ports:`
mutation moves both at once and a RED that cannot be attributed proves nothing. Add the honest
control too — admit `network_mode` to the allow-list and the exposure goes GREEN again, which is
what makes "this is the only pin that sees that door" a measurement.

**STATE A MITIGATION HONESTLY AND THEN SAY WHY IT IS NOT A DEFENCE.** Host networking also removes
the service from the compose network, so Prometheus can no longer resolve `pve-exporter` by name
(200 on the compose network, 000 under host mode) and the scrape breaks LOUDLY. That mitigates the
MONITORING outcome. It does nothing for the SECURITY one, and these clauses are security pins.

**HOW TO PROVE AN EXPOSURE WITHOUT EXPOSING ANYTHING.** Run the real image with a deliberately
INVALID credential aimed at a non-routable address (192.0.2.1, TEST-NET-1), probe from a throwaway
container at this box's own LAN address — never `docker exec` and never loopback, both of which
reach a binding the measurement exists to distinguish — read `ss -ltn` for the actual LISTEN line,
and print `ss` + `docker ps -a` + `docker network ls` AFTER teardown as the evidence block.

**WHEN A ROUND'S DELIVERABLE IS "DELETE A FALSE CLAIM EVERYWHERE", ENUMERATE THE ARTIFACTS AND PUT
THE TEST FILE ON THE LIST.** Round 3 corrected the "the exporter stays up and 401s" claim in
`compose.yml.j2`, `env.j2` and `defaults/main.yml` and left it verbatim in the guard's own
docstring — the third recurrence in this objective of "the docstring oversells the clause", and it
sat four bullets from a warning about that exact failure. A guard is read as code, so its prose is
the copy nobody re-reads. `grep -rn` the claim's *status code* and its *phrasing*, not just the file
you remember editing.

**A REGION'S EDGE IS NOT THE REGION'S CONTENTS — HARDENING THE LINE READER DOES NOTHING FOR THE
SLICER THAT CHOSE THE LINES.** Round 6 made `_line_class` fail CLOSED on any line at a service's key
column it could not read. Round 7 found the same clause still satisfiable, because both block
slicers ended a region at the next non-space GLYPH: `_compose_service_block` at
`(?=^\s{2}\S|^\S|\Z)`, `_router_block` at `(?=^\s{4}\S|\Z)`. A whole-line comment at the region's own
column and a column-0 Jinja `{% if %}` both match, carry no YAML key, and end no node at runtime —
and both are this repo's live idiom (compose.yml.j2:25/72/175/199 comment services at 2 spaces while
bodies use 4; dynamic.yml.j2:53/66/91 comment routers at 4 while bodies use 6; dynamic.yml.j2:84-89
gates config at column 0). Everything after such a line was invisible to every clause built on the
region, and — the part that makes it worse than a missed spelling — the truncation was **SILENT**: a
bare comment with nothing after it printed the IDENTICAL key field as the honest tree, so no output
said "I stopped reading here".

RULE: a region boundary must be decided by a line the parser can READ AS A KEY, never by a glyph,
and comments come off BEFORE slicing rather than by each caller afterwards. Put the rule in ONE
helper (`_key_bounded_block(body, name, indent)`) and make every slicer a wrapper, or the copies
drift — exactly how round 5's `_yaml_key` blind spot got inherited into `_declares_key`. It fails
CLOSED in the right direction: anything unreadable stays INSIDE the region and is judged by the
classifier, so an over-run is a false RED rather than a silent hole.

AND MEASURE THAT FAIL-CLOSED IS FREE BEFORE SHIPPING IT: old slicer vs new slicer over every region
in the delivered tree — 10 compose services + 4 routers, byte-identical content, zero unreadable
lines introduced. WHEN REVIEWING ANY GUARD BUILT ON A SLICED REGION, ask the two questions in order:
"how does an item reach the collection without going through the reader that builds it" (round 6)
and then "which lines never reached the reader at all" (round 7).

## The Grafana provisioning path (Step 4a, measured 2026-07-30) — for 4b and 4c

`grafana/grafana:13.1.0` runs as **uid 472, gid 0** (`Config.User='472'`; a uid with no explicit gid
takes gid 0). The role's files are `root:root`, so the ROOT-GROUP bits are what grant the container
access, and the delivered `0750` dirs / `0640` renders ARE readable to it — measured, including a
real server booted on the delivered tree. Do not "repair" these modes to `0644` by analogy with
`prometheus.yml`: `prom/prometheus` runs `65534:65534`, which matches neither owner nor group, and
that is the whole difference. The mode follows the CONTAINER'S IDENTITY.

The identity holds only while `compose.yml.j2` declines to override `user:` away from gid 0.
`scripts/test_grafana_provisioning_shape.py` checks both halves, and it checks ACCESS rather than a
literal mode, so `0755`/`0644` is equally acceptable to it.

**The provisioned datasource uid is `Prometheus` and it is now PINNED in
`grafana-datasource.yml.j2`.** Without that line Grafana generates one (measured:
`PBFA97CFB590B2093`), which is why nothing resolved before. **Every dashboard 4b/4c adds must
reference `uid: "Prometheus"`** on every panel, target, annotation and template variable, must be
delivered by a task whose `dest` is under `{{ docker_host_project_dir }}/grafana/dashboards/`, and
must reference at least one datasource — the guard's cross-file check is an inventory over that
`dest` and reddens on all three (rows R8/R9/R11 of `logs/red-step04a-provisioning-battery.log`). A
dashboard JSON dropped into `files/` without its delivery task reddens too.
