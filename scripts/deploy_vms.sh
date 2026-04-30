#!/usr/bin/env bash
# Usage: scripts/deploy_vms.sh
#
# End-to-end runner for the OpenTofu + Ansible Proxmox VM workflow.
# 1. Preflight: confirm `genisoimage` is on PATH (the Windows module's
#    null_resource local-exec invokes it to build the per-VM
#    autounattend ISO; failing fast here surfaces a missing dependency
#    before `tofu apply` runs).
# 2. OpenTofu provisions the guest VMs declared under tofu/.
# 3. Wait gate: poll `tofu output -json ansible_inventory` every 30s
#    for up to 30 minutes until every host publishes its
#    qemu-guest-agent IP. Hosts whose `ansible_host` is null/empty are
#    printed each iteration; the gate exits non-zero on timeout.
# 4. tofu output -json ansible_inventory is piped through
#    scripts/tofu_to_inventory.py to regenerate
#    ansible/inventory/tofu_generated.yml from live state.
# 5. ansible-playbook applies the baseline configuration role to every
#    Tofu-provisioned host via ansible/configure-vms.yml.
#
# Requires: tofu, python3, genisoimage, ansible-playbook on PATH (or
# the project's .venv/bin/ansible-playbook). Proxmox API credentials
# must be exported (PROXMOX_VE_API_TOKEN) or supplied via
# tofu/terraform.tfvars.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

INVENTORY_OUT="ansible/inventory/tofu_generated.yml"

echo >&2 "==> step 0: preflight checks"
if ! command -v genisoimage >/dev/null 2>&1; then
	echo >&2 "ERROR: 'genisoimage' is required to build the per-VM Windows autounattend ISO but is not on PATH."
	echo >&2 "       Install via 'sudo apt install genisoimage' (Debian/Ubuntu) or 'brew install cdrtools' (macOS)."
	exit 1
fi

echo >&2 "==> step 1: tofu apply (provision guest VMs from tofu/)"
tofu -chdir=tofu apply -auto-approve

# Wait-gate parameters: 30-minute timeout, 30-second polling interval.
# Override via WAIT_TIMEOUT_SECS / WAIT_INTERVAL_SECS env vars when
# debugging on a slow Windows install.
wait_timeout_secs="${WAIT_TIMEOUT_SECS:-1800}"
wait_interval_secs="${WAIT_INTERVAL_SECS:-30}"

echo >&2 "==> step 2: wait for every guest to publish its qemu-guest-agent IP (timeout=${wait_timeout_secs}s, interval=${wait_interval_secs}s)"
deadline=$(( $(date +%s) + wait_timeout_secs ))
while :; do
	tofu -chdir=tofu refresh >/dev/null
	pending=$(
		tofu -chdir=tofu output -json ansible_inventory \
			| python3 -c '
import json
import sys

inv = json.load(sys.stdin)
pending = []
for group in inv.values():
    if not isinstance(group, dict):
        continue
    for host, attrs in (group.get("hosts") or {}).items():
        if not (isinstance(attrs, dict) and attrs.get("ansible_host")):
            pending.append(host)
print(" ".join(sorted(pending)))
'
	)
	if [ -z "$pending" ]; then
		echo >&2 "==> all guests reported ansible_host"
		break
	fi
	now=$(date +%s)
	if [ "$now" -ge "$deadline" ]; then
		echo >&2 "ERROR: wait gate timed out after ${wait_timeout_secs}s; still pending: $pending"
		exit 1
	fi
	echo >&2 "    pending: $pending (sleeping ${wait_interval_secs}s)"
	sleep "$wait_interval_secs"
done

echo >&2 "==> step 3: regenerate Ansible inventory from tofu output"
tofu -chdir=tofu output -json ansible_inventory \
	| python3 scripts/tofu_to_inventory.py --output "$INVENTORY_OUT"

echo >&2 "==> step 4: ansible-playbook configure-vms.yml against the generated inventory"
ansible-playbook -i "$INVENTORY_OUT" ansible/configure-vms.yml
