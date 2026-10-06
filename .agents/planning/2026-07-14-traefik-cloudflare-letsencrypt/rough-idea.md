# Rough Idea

Update traefik to ensure that we are set up correctly to work with a cloudflare
managed domain with SSL certs from let's encrypt.

---

## Captured context (initial grounding, pre-clarification)

This is **not greenfield** — the `docker_host` Ansible role already implements
most of a Cloudflare + Let's Encrypt setup. Relevant existing state:

- `ansible/group_vars/all.yml`
  - `domain: yoonnation.com`
  - `acme_resolver: le-dns-cf` (DNS-01 wildcard, described in-repo as "now live
    after the Step-11 migration")
- `ansible/roles/docker_host/templates/traefik.yml.j2` (static config)
  - `entryPoints`: `web` (:80, redirects to websecure), `websecure` (:443),
    `metrics` (:8082, internal)
  - `certificatesResolvers`:
    - `le-http` — ACME HTTP-01 via the `web` entrypoint
    - `le-dns-cf` — ACME DNS-01 via Cloudflare, resolvers 1.1.1.1 / 8.8.8.8
  - `api.dashboard: true`; working-tree change adds `api.insecure: true`
- `ansible/roles/docker_host/templates/compose.yml.j2`
  - Traefik service publishes 80/443 (+ 8080 dashboard in working tree)
  - `CF_DNS_API_TOKEN=${CF_DNS_API_TOKEN:-}` env
  - `whoami` router requests the wildcard `main={{ domain }}` +
    `sans=*.{{ domain }}` under `le-dns-cf`
- `ansible/roles/docker_host/templates/env.j2`
  - `CF_DNS_API_TOKEN={{ vault_cloudflare_dns_api_token | default('') }}`
- `ansible/roles/docker_host/templates/dynamic.yml.j2`
  - Middlewares: `redirect-to-https`, `security-headers`, `lan-allowlist`
  - Public `plex` router (websecure, no lan-allowlist), cert via `acme_resolver`

Uncommitted working-tree changes at start of session (dashboard exposure):
- `defaults/main.yml`: adds `docker_host_traefik_dashboard_port: 8080`
- `compose.yml.j2`: publishes `{{ port }}:8080`
- `traefik.yml.j2`: adds `api.insecure: true`

Implication: the clarification phase should focus on **verifying correctness,
closing gaps, and hardening** the existing setup rather than building from zero.
