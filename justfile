# just task runner for the proxmox-homelab pipeline.
#   just            # list recipes (default)
#   just <recipe>   # plan / apply / fmt / play / gen-inventory / test
#   just provision  # apply -> gen-inventory -> play (composite)
#
# `just` is the sole task interface — the former mise [tasks.*] were removed in
# the Step-4 cutover. Composite recipes chain the leaves via just's
# left-to-right dependency ordering (a non-zero recipe aborts the chain).
# `just` is provisioned by mise (mise.toml [tools]); recipe bodies call the
# tools directly (active-mise model, PATH).

# Auto-approve switch: `apply` stays interactive unless AUTO_APPROVE is set in
# the env (or the `approve` arg is passed explicitly).
AUTO := env_var_or_default("AUTO_APPROVE", "")

# List the available recipes.
default:
    @just --list

[working-directory: 'tofu']
plan:
    tofu plan

# Apply the Tofu plan. Interactive by default; pass `approve=1` (or set
# AUTO_APPROVE) to run unattended with `-auto-approve`. A preflight guard aborts
# the apply if PROXMOX_VE_API_TOKEN is set in the env — it would shadow the
# root@pam ticket and 403 the Plex CT device-passthrough create.
[working-directory: 'tofu']
apply approve=AUTO:
    python {{ justfile_directory() }}/scripts/preflight_tofu_auth.py
    tofu apply {{ if approve != "" { "-auto-approve" } else { "" } }}

[working-directory: 'tofu']
fmt:
    tofu fmt -recursive

[working-directory: 'ansible']
play:
    ansible-playbook site.yml

# acme_ca_server (group_vars/all/vars.yml) is ALREADY LE prod, so an ordinary
# `just play` renders the prod CA — but acme.json is keyed by resolver name
# (le-dns-cf), so if the store still holds an older (e.g. staging) cert Traefik
# reuses it and never re-issues. This runs the playbook with the gated reset
# (docker_host_acme_reset=true): stop Traefik -> empty acme.json at 0600 -> start.
#
# Force a fresh LE production wildcard (one-shot ACME reset; rate-limited 5/week).
[working-directory: 'ansible']
play-prod:
    ansible-playbook site.yml -e docker_host_acme_reset=true

# Install/refresh the pinned Galaxy roles (ansible/requirements.yml) into the
# vendored ansible/galaxy_roles/ dir. The result is committed so the offline
# gate (just test) and `just play` resolve the roles on disk with no network.
[working-directory: 'ansible']
galaxy:
    ansible-galaxy role install -r requirements.yml -p galaxy_roles

# Render ansible/inventory/hosts.yml from `tofu output` (runs from repo root).
gen-inventory:
    python scripts/gen_inventory.py

# Run the full offline backpressure gate (shape-tests + tofu + ansible).
test:
    python scripts/run_gate.py

# --- Composite recipes (chains over the leaf recipes) ------------------------

# Provision infrastructure only (Tofu apply). Inherits apply's approve hatch.
infra approve=AUTO: (apply approve)

# Re-render the inventory from Tofu state, then run the Ansible playbook.
config: gen-inventory play

# Full provision: apply infra -> regenerate inventory -> run the playbook.
provision approve=AUTO: (apply approve) gen-inventory play

# Tear down the Tofu-managed infrastructure (interactive).
[working-directory: 'tofu']
destroy:
    tofu destroy

# --- Template recipes (Packer dev-VM builds) ---------------------------------
# The scripts validate `os` and exit non-zero on an unknown short-name, so the
# justfile forwards the arg unchanged — no re-validation here (avoids drift).

# Build one dev-VM template: `just build {ubuntu26|fedora|windows11}`.
build os:
    scripts/build_template.sh {{os}}

# Build all three dev-VM templates in sequence.
build-all: (build "ubuntu26") (build "fedora") (build "windows11")

# One-time cloud source-template bootstrap: `just bootstrap {ubuntu26|fedora}`.
bootstrap os:
    scripts/bootstrap_cloud_template.sh {{os}}
