# Dev VMs: Win 10, Win 11, Ubuntu 26, CentOS Stream

_Date: 2026-04-29_

## Goal

Make it easy to provision and reprovision a small set of personal dev VMs on the existing Proxmox homelab using the existing Tofu→Ansible workflow. Initial set:

- `ubuntu26-dev` — Ubuntu 26.04 (clone of cloud-init template)
- `centos10-dev` — CentOS Stream 10 (clone of cloud-init template)
- `win10-dev` — Windows 10, ISO + autounattend install
- `win11-dev` — Windows 11, ISO + autounattend install

"Easy to configure" means: adding or modifying a VM is a single map entry plus `scripts/deploy_vms.sh`.

## Non-goals

- Active Directory / domain join.
- Cloudbase-init Windows templates (clone-from-template like Linux).
- Scripted Windows ISO download — Microsoft retail ISOs are placed in `local:iso/` manually.
- Heavy dev tooling install on Windows (Chocolatey, IDEs, etc.) — `windows_baseline` is intentionally minimal; tooling is a separate later concern.

## Architecture

Two distinct Tofu modules behind a uniform "two maps in `main.tf`" interface, plus a Windows branch in the existing Ansible inventory generator and `configure-vms.yml`.

### `tofu/main.tf`

```hcl
locals {
  cloud_templates = {
    ubuntu-24-04     = 9000
    ubuntu-26-04     = 9001
    centos-stream-10 = 9002
  }

  linux_vms = {
    ubuntu26-dev = { vmid = 310, template = "ubuntu-26-04",     memory = 4096, cores = 2, disk_gb = 120 }
    centos10-dev = { vmid = 311, template = "centos-stream-10", memory = 4096, cores = 2, disk_gb = 120 }
  }

  windows_vms = {
    win10-dev = { vmid = 320, iso = "Win10_22H2_English_x64.iso", memory = 4096, cores = 2, disk_gb = 120 }
    win11-dev = { vmid = 321, iso = "Win11_23H2_English_x64.iso", memory = 8192, cores = 4, disk_gb = 120 }
  }
}

module "linux_vm" {
  for_each            = local.linux_vms
  source              = "./modules/linux_vm"
  name                = each.key
  vmid                = each.value.vmid
  clone_from          = local.cloud_templates[each.value.template]
  memory              = each.value.memory
  cores               = each.value.cores
  disk_gb             = each.value.disk_gb
  static_ip           = try(each.value.static_ip, null)
  gateway             = try(each.value.gateway,   null)
  bridge              = "vmbr0"
  template_node       = var.pve_node_name
  default_user        = var.default_user
  default_password    = var.default_password
  ssh_authorized_keys = var.ssh_authorized_keys
  tags                = ["linux", "dev", "tofu"]
}

module "windows_vm" {
  for_each            = local.windows_vms
  source              = "./modules/windows_vm"
  name                = each.key
  vmid                = each.value.vmid
  iso_file            = each.value.iso
  memory              = each.value.memory
  cores               = each.value.cores
  disk_gb             = each.value.disk_gb
  bridge              = "vmbr0"
  template_node       = var.pve_node_name
  default_user        = var.default_user
  default_password    = var.default_password
  ssh_authorized_keys = var.ssh_authorized_keys
  tags                = ["windows", "dev", "tofu"]
}
```

`disk_gb` is explicitly required on every entry (no module default) — so disk sizing is always visible at the call site.

### `tofu/modules/linux_vm/` (rename of existing `tofu/modules/vm/`)

Adds three inputs to the existing module:

- `disk_gb` (required) — applied via `disk { size = "${var.disk_gb}G"; discard = "on"; ssd = true; datastore_id = "local-lvm" }`. Storage stays thin because `local-lvm` is an LVM-thin pool; `discard = on` returns freed blocks to the pool on `fstrim`.
- `static_ip` / `gateway` (both nullable, default `null`) — when both are non-null, the `initialization.ip_config.ipv4` block emits `address = var.static_ip` (CIDR) and `gateway = var.gateway`. When either is null, falls through to `address = "dhcp"`. Half-configured (one set, one null) fails plan with a precondition.
- `default_user`, `default_password`, `ssh_authorized_keys` — plumbed to `initialization.user_account` so the cloud-init image's default user (`ubuntu`/`cloud-user`) is replaced by a single uniform `user`. The cloud-init `user-data` also drops a `sudoers.d` entry granting passwordless sudo (`%sudo ALL=(ALL) NOPASSWD:ALL`) so Ansible's `become: true` works without the password being interactively prompted. This is the missing piece that makes Ansible able to reach the VMs at all today.

### `tofu/modules/windows_vm/` (new)

Inputs: `name`, `vmid`, `iso_file`, `memory`, `cores`, `disk_gb`, `bridge`, `template_node`, `default_user`, `default_password`, `ssh_authorized_keys`, `tags`.

Resources, in order:

1. `local_file.autounattend` — renders `templates/autounattend.xml.tftpl` via `templatefile()` with `name`, `default_user`, `default_password`, `ssh_authorized_keys`. Output written to `${path.module}/build/${var.name}-autounattend.xml`.
2. `null_resource.build_iso` — `local-exec` runs `genisoimage -o build/${var.name}-autounattend.iso -V "AUTOUNATTEND" -J -r ${rendered_xml}`. `triggers` keyed on the rendered file's hash so the ISO rebuilds on template change.
3. `proxmox_virtual_environment_file.autounattend_iso` — uploads to `local:iso/${var.name}-autounattend.iso`. Depends on the null_resource.
4. `proxmox_virtual_environment_vm.this` — VM with:
   - `bios = "ovmf"`, `efi_disk { datastore_id = "local-lvm" }`, `tpm_state { datastore_id = "local-lvm", version = "v2.0" }` — Win 11 requires both; Win 10 tolerates them.
   - Three `cdrom` entries: the install ISO at `local:iso/${var.iso_file}`, the autounattend ISO at `local:iso/${var.name}-autounattend.iso`, and `local:iso/virtio-win.iso` (so qemu-guest-agent install during FirstLogonCommands has a local source).
   - One `disk` of `var.disk_gb` GB on `local-lvm` with `discard = "on"`, `ssd = true`.
   - `agent { enabled = true }` (qemu-guest-agent installed by autounattend).
   - `network_device { bridge = var.bridge }`. DHCP at install time; static IP applied later by `windows_baseline` if `static_ip` set in inventory.

Outputs match `linux_vm`'s shape: `name`, `vmid`, `node_name`, `ipv4_address` (wrapped in `try()` so plan succeeds before the agent reports).

### `tofu/modules/windows_vm/templates/autounattend.xml.tftpl`

Single template covering Win 10 and Win 11. Key sections:

- `<settings pass="windowsPE">` — disk partitioning (UEFI: 100 MB EFI + MSR + OS), accepts EULA, sets product key to the Microsoft generic install key (eval-equivalent — does not activate; user activates afterwards).
- `<settings pass="specialize">` — sets `ComputerName = ${name}`. Disables Defender real-time scan via `Set-MpPreference`.
- `<settings pass="oobeSystem>` — locale en-US, timezone UTC, skips OOBE entirely (`HideEULAPage`, `HideOnlineAccountScreens`, `HideWirelessSetupInOOBE`, `ProtectYourPC = 3`).
  - `<UserAccounts>`: enables built-in `Administrator` with `${default_password}`, creates local `${default_user}` with `${default_password}`, adds it to `Administrators`.
  - `<AutoLogon>`: one-shot autologon as `${default_user}` for the FirstLogonCommand pass.
  - `<FirstLogonCommands>` (PowerShell):
    1. Install OpenSSH Server: `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0`
    2. Set service to auto-start, start it now, open firewall.
    3. Set default shell for SSH to PowerShell (registry).
    4. Write `${ssh_authorized_keys}` joined by newlines to `C:\ProgramData\ssh\administrators_authorized_keys` and apply the required ACL (Administrators + SYSTEM only — this is the gotcha that breaks key auth otherwise).
    5. Install qemu-guest-agent from the attached `virtio-win.iso` (`E:\guest-agent\qemu-ga-x86_64.msi /quiet`). Required — Tofu reads the VM's DHCP lease via the agent.
    6. `BypassNRO` registry tweak (Win 11 only — detected by `[System.Environment]::OSVersion`).
- `<UserData>` — generic install key.

The same template handles both versions; the few Win-11-specific bits are guarded inside FirstLogonCommands.

### `scripts/tofu_to_inventory.py`

Behavior changes:

- The Tofu `ansible_inventory` output gains a sibling `windows_dev_vms` group (emitted by `outputs.tf` from `module.windows_vm[*]`).
- The script merges it into the YAML inventory under `proxmox_vms.children.windows`.
- `ansible_user_for(hostname)` is removed entirely. Every host gets `ansible_user = var.default_user` ("user") at the group level.
- Windows hosts additionally get `ansible_shell_type: powershell`, `ansible_connection: ssh` (default; explicit for clarity), and live in the `windows` group so plays can target `hosts: windows`.
- Tests in `scripts/test_tofu_to_inventory.py` extend the fixture with `win10-dev` and assert: lands in `windows` group, has `ansible_shell_type: powershell`, no `ansible_user` per-host override, `ansible_user: user` at group level.

Output shape:

```yaml
proxmox_vms:
  hosts:
    ubuntu26-dev: { ansible_host: 192.168.x.x, vmid: 310, node_name: pve-01 }
    centos10-dev: { ansible_host: 192.168.x.x, vmid: 311, node_name: pve-01 }
  children:
    windows:
      hosts:
        win10-dev: { ansible_host: 192.168.x.x, vmid: 320, node_name: pve-01 }
        win11-dev: { ansible_host: 192.168.x.x, vmid: 321, node_name: pve-01 }
      vars:
        ansible_shell_type: powershell
  vars:
    ansible_user: user
```

### `ansible/configure-vms.yml`

Two plays. The first (existing) skips Windows; the second targets Windows only:

```yaml
- name: Configure Tofu-provisioned Linux guests
  hosts: proxmox_vms:!windows
  gather_facts: true
  become: true
  roles: [vm_baseline]

- name: Configure Tofu-provisioned Windows guests
  hosts: windows
  gather_facts: true
  roles: [windows_baseline]
```

### `ansible/roles/windows_baseline/tasks/main.yml` (new)

Minimal — mirrors `vm_baseline`:

- `ansible.windows.win_copy` writes `C:\ProgramData\ralph-banner.txt` with the same hostname/vmid/node identifying content.
- If `static_ip` is defined for the host (via Tofu output → inventory host_vars), `ansible.windows.win_powershell` runs `New-NetIPAddress` + `Set-DnsClientServerAddress` to switch from DHCP to static. Idempotent: the task first checks `Get-NetIPAddress` and skips if already correct.

### Configuration

#### `tofu/variables.tf` additions

```hcl
variable "default_user" {
  description = "Daily-driver username created on every dev VM (Linux + Windows)."
  type        = string
  default     = "user"
}

variable "default_password" {
  description = "Password for default_user and Windows Administrator. Dev-only — these VMs are not exposed externally."
  type        = string
  sensitive   = true
}

variable "ssh_authorized_keys" {
  description = "List of SSH public keys to authorize on default_user."
  type        = list(string)
}
```

#### `tofu/terraform.tfvars` (gitignored — not committed)

```hcl
pve_api_endpoint    = "https://pve.home.arpa:8006/"
pve_api_token       = "ansible-token@pam!ansible-token=<secret>"
pve_node_name       = "pve-01"
pve_insecure        = true

default_password    = "password"
ssh_authorized_keys = [
  "ssh-ed25519 AAAA... user@workstation",
]
```

A `tofu/terraform.tfvars.example` is committed alongside, with the same shape but redacted values, so future-me knows the schema.

#### Required ISOs in Proxmox `local:iso/`

Operator places these manually (one-time):

- `Win10_22H2_English_x64.iso`
- `Win11_23H2_English_x64.iso`
- `virtio-win.iso` — required. The autounattend's FirstLogonCommands installs qemu-guest-agent from this ISO; without it, the agent never reports an IP and the workflow's wait gate times out at 30 minutes. Source: `https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso`. The Windows VMs attach this as a third CD-ROM during install.

ISO filenames are referenced literally from `local.windows_vms` map values; rename in the map if the operator's filenames differ.

#### Operator dependency

`genisoimage` (or `mkisofs`) on the local machine. `scripts/deploy_vms.sh` checks `command -v genisoimage` before `tofu apply` and exits with a clear message if missing.

### Workflow (`scripts/deploy_vms.sh`)

```
1. Preflight: command -v genisoimage  ||  fail
2. tofu -chdir=tofu apply -auto-approve
3. Wait gate (NEW): poll `tofu refresh && tofu output -json ansible_inventory`
   every 30s, up to 30 minutes, until every host has non-null `ansible_host`.
   Print which hosts are still pending each iteration. Windows installs take
   ~15-25 min from boot; this is where the runtime lives.
4. tofu output -json ansible_inventory | python3 scripts/tofu_to_inventory.py
5. ansible-playbook -i ansible/inventory/tofu_generated.yml ansible/configure-vms.yml
```

The wait gate is new. Today the inventory generator already skips null-IP hosts with a warning; the runner now retries instead, so a fresh `apply` doesn't need the operator to come back and re-run inventory generation manually after Windows finishes installing.

## Tests

Tests stay in the project's existing convention (plain Python scripts under `scripts/`, no pytest, exit non-zero on failure). New / extended tests:

- `scripts/test_tofu_to_inventory.py` — extended fixture with two Windows hosts; asserts the `windows` child group exists with `ansible_shell_type: powershell`, no per-host `ansible_user` overrides, `ansible_user: user` at the top-level group, and DHCP-pending Windows hosts are still skipped with the same warning behaviour as Linux.
- `scripts/test_windows_vm_module.py` (new) — text-based smoke test mirroring `scripts/test_tofu_vm_module.py`. Asserts the Windows module declares `proxmox_virtual_environment_vm`, `proxmox_virtual_environment_file`, `null_resource`, has `bios = "ovmf"`, `efi_disk`, `tpm_state` with `version = "v2.0"`, three `cdrom` entries (install + autounattend + virtio-win), and `disk { ... discard = "on" }`. Also asserts `templates/autounattend.xml.tftpl` exists and references `${name}`, `${default_user}`, `${default_password}`, `${ssh_authorized_keys}`.
- `scripts/test_dev_vms_main.py` (new) — text-based check on `tofu/main.tf`. Asserts `local.cloud_templates` contains `ubuntu-26-04` and `centos-stream-10`, `local.linux_vms` contains both dev hosts with required keys, `local.windows_vms` contains `win10-dev` and `win11-dev` with `iso` referencing `Win10`/`Win11`. Catches accidental rename / removal.
- `scripts/test_windows_baseline_role.py` (new) — loads `ansible/roles/windows_baseline/tasks/main.yml`, asserts uses `ansible.windows.*` modules only (allow-list), maintains a `HALLUCINATED_MODULES` deny-list following the `scripts/test_firewall.py` pattern.

The existing `pve_vm_deploy` removal test (`test_step5_runner_and_removal.py`) is not affected; it asserts the deprecated role is gone and `services.yml` doesn't import it. Still true.

## Risks and tradeoffs

- **Windows install time dominates the workflow.** A Win 11 unattended install on local-lvm is 15-25 min; Linux clones are seconds. The wait gate masks this for the operator but doesn't shorten it. Acceptable for dev VMs reprovisioned occasionally; not acceptable for "fast feedback" workflows. (If this becomes painful, revisit cloudbase-init templates — non-goal for now.)
- **Per-VM autounattend ISO is an extra Proxmox file artifact.** Four Windows VMs = four ~1 MB ISOs in `local:iso/`. Cleanup on VM destroy is handled by the bpg `proxmox_virtual_environment_file` resource (Tofu deletes on destroy).
- **`password` is the actual password.** Acceptable because: dev VMs, homelab network only, no external exposure, mitigated by SSH key auth on `user`. Documented in the spec and `terraform.tfvars.example`. If you ever expose a dev VM, change `default_password` first.
- **Generic Windows install key, no activation.** VMs install in unactivated mode (cosmetic watermark, some personalization disabled). Operator activates manually if/when needed. Avoids licensing complexity in IaC.
- **Static IPs for Windows applied post-install, not in autounattend.** Slightly less "self-contained" than baking it into the answer file, but autounattend network-config is fragile (interface index ordering changes between hardware) and Ansible's PowerShell path is well-supported. Net win.
- **`genisoimage` is a new operator-machine dependency.** macOS users would need `brew install cdrtools`; Linux distros generally ship it. Documented in `scripts/deploy_vms.sh` preflight error message.
- **Rename of `tofu/modules/vm/` → `tofu/modules/linux_vm/` is a destructive Tofu state change.** Resource addresses change (`module.ubuntu26_test.proxmox_virtual_environment_vm.this` → gone, replaced by `module.linux_vm["ubuntu26-dev"].proxmox_virtual_environment_vm.this`). Existing `ubuntu26-test` and `centos10-test` VMs will be destroyed and recreated by the next apply. This is intended (replace, not coexist) and was confirmed during brainstorming, but worth flagging on the very first run.

## Implementation phases (rough)

Each phase is independently testable; concrete plan generated by `writing-plans` next.

1. Linux module rename + `disk_gb` + `default_user`/`default_password`/`ssh_authorized_keys` + optional static IP. Update `main.tf` to two-map shape with `for_each`. Existing test fleet (`ubuntu26-test`, `centos10-test`) replaced by `ubuntu26-dev`, `centos10-dev`. Inventory generator updated. End-to-end Linux dev VMs working.
2. Windows module + autounattend template + ISO build + Proxmox upload. Add `win10-dev`, `win11-dev` to map. End-to-end Windows install via SSH.
3. `windows_baseline` Ansible role + Windows static-IP support. `configure-vms.yml` two-play layout.
4. `scripts/deploy_vms.sh` wait gate + `genisoimage` preflight.
5. New tests + extension of existing tests.
