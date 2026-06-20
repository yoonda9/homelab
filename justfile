# just task runner for the proxmox-homelab pipeline.
#   just            # list recipes (default)
#   just <recipe>   # plan / apply / fmt / play / gen-inventory / test
#   just provision  # apply -> gen-inventory -> play (composite)
#
# Leaf recipes mirror the mise [tasks.*] 1:1 (coexistence — `mise run <task>`
# still works; cutover is Step 4). Composite recipes chain the leaves via just's
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
# AUTO_APPROVE) to run unattended with `-auto-approve`.
[working-directory: 'tofu']
apply approve=AUTO:
    tofu apply {{ if approve != "" { "-auto-approve" } else { "" } }}

[working-directory: 'tofu']
fmt:
    tofu fmt -recursive

[working-directory: 'ansible']
play:
    ansible-playbook site.yml

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
