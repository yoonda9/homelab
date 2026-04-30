# Home Lab Auto Deploy

Automated provisioning of a personal Proxmox VE homelab and its core services (Plex, Pi-hole, Traefik, Uptime Kuma, Bitwarden, Grafana/Prometheus/Loki, etc.). The split is deliberate:

- **OpenTofu** (`tofu/`) provisions guest VMs on Proxmox via the `bpg/proxmox` provider.
- **Ansible** (`ansible/`) bootstraps the Proxmox host, deploys LXC-hosted services directly on the host, and configures Tofu-provisioned VMs.

## Architecture

There are two distinct provisioning paths that run against the same Proxmox host but produce different artifacts:

### 1. Proxmox host bootstrap + LXC services (Ansible-only)

- `ansible/main.yml` is the umbrella, importing `bootstrap-proxmox.yml` then `services.yml`.
- `bootstrap-proxmox.yml` first runs `bootstrap-ansible.yml` (installs `uv`, builds `/opt/ansible-venv` on the Proxmox node so all subsequent Ansible runs use a consistent Python interpreter — `ansible_python_interpreter` in `group_vars/all.yml` points there) then applies the `pve_base`, `docker_host`, and `traefik` roles to the Proxmox host itself.
- `services.yml` deploys LXC-hosted services (`plex`, `pihole`, `uptimekuma`) **on the Proxmox host** via `community.proxmox.proxmox*` modules — these roles run from a Proxmox host context, not inside guests.
- Inventory: `ansible/inventory/hosts.yml` (group `proxmox_hosts`).

### 2. Guest VM provisioning (Tofu → dynamic inventory → Ansible)

End-to-end runner is `scripts/deploy_vms.sh`. It performs three steps:

1. `tofu -chdir=tofu apply` — provisions guests declared in `tofu/main.tf` (uses the `tofu/modules/linux_vm/` reusable module to clone from cloud-init templates created by `pve_base`).
2. `tofu output -json ansible_inventory | python3 scripts/tofu_to_inventory.py --output ansible/inventory/tofu_generated.yml` — emits a real Ansible YAML inventory under group `proxmox_vms`. Hosts whose `ansible_host` is null (qemu-guest-agent hasn't reported a DHCP lease yet) are skipped with a stderr warning. Hostnames starting with `ubuntu`/`centos` get `ansible_user` overrides (`ubuntu` / `cloud-user`).
3. `ansible-playbook -i ansible/inventory/tofu_generated.yml ansible/configure-vms.yml` — applies the `vm_baseline` role (and only that — heavier post-config stays in the per-service roles in path 1).

`ansible/inventory/tofu_generated.yml` is gitignored — do not edit by hand and do not commit.

The `tofu_to_inventory.py` script intentionally uses **stdlib only** (no PyYAML) to keep the runtime dependency-free; the matching test (`scripts/test_tofu_to_inventory.py`) does use PyYAML, which is fine.

### Configuration variables

All Ansible defaults live in `ansible/group_vars/all.yml`. VM definitions for the Tofu path live in `tofu/main.tf` (calls into `tofu/modules/linux_vm/`). When a VM should be provisioned by Tofu and configured by Ansible, the vmid lives in both — keep them aligned. Windows ISO-based VM provisioning is **not** implemented in the Tofu module.

## Commands

Python toolchain is `uv` (Python 3.12 pinned in `.python-version`). The project venv is `.venv/`; Ansible CLIs are `.venv/bin/ansible-playbook` etc.

```bash
# Set up / sync the venv
uv sync

# Full Tofu→Ansible VM workflow
scripts/deploy_vms.sh

# Manual Tofu steps
tofu -chdir=tofu init
tofu -chdir=tofu plan
tofu -chdir=tofu apply -auto-approve

# Manual Ansible runs
.venv/bin/ansible-playbook ansible/main.yml                 # full bootstrap + services
.venv/bin/ansible-playbook ansible/bootstrap-proxmox.yml    # just the host bootstrap
.venv/bin/ansible-playbook ansible/services.yml             # just the LXC services
.venv/bin/ansible-playbook -i ansible/inventory/tofu_generated.yml ansible/configure-vms.yml

# Syntax-check a play without running it
.venv/bin/ansible-playbook --syntax-check ansible/services.yml

# Lint
.venv/bin/ansible-lint ansible/
```

Required env / secrets:
- Proxmox API token for Tofu: pass via `pve_api_endpoint` / `pve_api_token` / `pve_node_name` (and optionally `pve_insecure`) in `tofu/terraform.tfvars` (gitignored), or environment variables.
- Proxmox API for Ansible: `pve_api_token_id` / `pve_api_token_secret` in vars (or via `community.proxmox.proxmox*` module params). On first run `pve_base` can generate a token — copy the printed secret into your vars and re-run.
- Reuse the **same** token for both Tofu and Ansible per the comment in `tofu/variables.tf`.

## Tests

Tests are **plain Python scripts**, not pytest. Each `scripts/test_*.py` is a self-contained checker that loads YAML/HCL/Python artifacts, asserts structure, prints `OK:`/`FAIL:` lines, and exits non-zero on failure. They are static checks against the Ansible task tree and Tofu config — they do **not** talk to a live Proxmox.

```bash
# Run a single test
python3 scripts/test_firewall.py

# Run them all
for t in scripts/test_*.py; do python3 "$t" || exit 1; done
```

When adding or modifying an Ansible role, add or extend the matching `scripts/test_<topic>.py`. Patterns to follow when writing one:

- Walk the task tree with a `flatten_tasks` helper that recurses into `block`/`tasks`.
- Maintain an `ALLOWED_MODULES` allow-list and a `HALLUCINATED_MODULES` deny-list (see `scripts/test_firewall.py`) — this catches LLM-invented module names like `community.proxmox.proxmox_firewall_rule`.
- End with `--syntax-check` against the relevant playbook when feasible.

## Conventions

- All Tofu-provisioned VMs are cloned from cloud-init templates built by `pve_base` (vmid 9000-series). Tofu does not build templates; Ansible does.
- The Proxmox setup is **standalone**, not clustered — avoid `/cluster/...` paths and assume one node. Node name is parametrised (`pve_node_name` in Tofu, `pve_host` and `ansible_facts.hostname` in Ansible).
- Debian release for Proxmox repo URLs is parameterised via `pve_debian_release` (currently `trixie`, i.e. PVE 9). Don't hardcode `bookworm` or `trixie` in new tasks.
- DEB822 sources only — legacy `.list` files are explicitly removed by `pve_base`. Use `ansible.builtin.deb822_repository`.
- `ansible_python_interpreter` always resolves to `/opt/ansible-venv/bin/python3` on Proxmox hosts (set in `group_vars/all.yml`); don't override unless a task targets a guest with a different interpreter path.
