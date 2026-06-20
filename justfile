# just task runner for the proxmox-homelab pipeline.
#   just            # list recipes (default)
#   just <recipe>   # plan / apply / fmt / play / gen-inventory / test
#
# Leaf recipes mirror the mise [tasks.*] 1:1 (coexistence — `mise run <task>`
# still works; cutover is Step 4). `just` is provisioned by mise (mise.toml
# [tools]); recipe bodies call the tools directly (active-mise model, PATH).

# List the available recipes.
default:
    @just --list

[working-directory: 'tofu']
plan:
    tofu plan

[working-directory: 'tofu']
apply:
    tofu apply

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
