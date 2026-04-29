#!/usr/bin/env bash
# Usage: scripts/deploy_vms.sh
#
# End-to-end runner for the OpenTofu + Ansible Proxmox VM workflow.
# 1. OpenTofu provisions the guest VMs declared under tofu/.
# 2. tofu output -json ansible_inventory is piped through
#    scripts/tofu_to_inventory.py to regenerate
#    ansible/inventory/tofu_generated.yml from live state.
# 3. ansible-playbook applies the baseline configuration role to every
#    Tofu-provisioned host via ansible/configure-vms.yml.
#
# Requires: tofu, python3, ansible-playbook on PATH (or the project's
# .venv/bin/ansible-playbook). Proxmox API credentials must be exported
# (PROXMOX_VE_API_TOKEN) or supplied via tofu/terraform.tfvars.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

INVENTORY_OUT="ansible/inventory/tofu_generated.yml"

echo >&2 "==> step 1: tofu apply (provision guest VMs from tofu/)"
tofu -chdir=tofu apply -auto-approve

echo >&2 "==> step 2: regenerate Ansible inventory from tofu output"
tofu -chdir=tofu output -json ansible_inventory \
	| python3 scripts/tofu_to_inventory.py --output "$INVENTORY_OUT"

echo >&2 "==> step 3: ansible-playbook configure-vms.yml against the generated inventory"
ansible-playbook -i "$INVENTORY_OUT" ansible/configure-vms.yml
