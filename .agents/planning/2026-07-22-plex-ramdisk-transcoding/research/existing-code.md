# Research: Existing Codebase Patterns

## Key Findings

### 1. Ansible Role Constraints

**Critical**: The Plex Ansible role is explicitly **`ansible.builtin`-only**. The comment in
`ansible/roles/plex/tasks/main.yml` states:

> ansible.builtin-only (the ansible-core venv has no community.*)

This means `community.general.xml` **cannot be used** without first installing
the `community.general` collection. Alternatives for modifying Plex's
`Preferences.xml`:

- `ansible.builtin.replace` with regex to set the `TranscoderTempDirectory` attribute
- `ansible.builtin.lineinfile` with backreference regex
- `ansible.builtin.command` wrapping `xmlstarlet` or `sed`

### 2. OpenTofu Bind Mount Pattern

Adding a new `bind_mounts` entry is straightforward — the variable accepts:

```hcl
{ host_path = string, ct_path = string, read_only = optional(bool, false) }
```

**⚠️ Critical caveat**: Adding a new `mount_point` entry causes a **full
destroy/recreate** of the CT (bpg/proxmox provider v0.110.0 limitation —
tracked in bpg/terraform-provider-proxmox#2507). This is safe because Plex
state is persisted on host storage, but requires a post-apply `just config`
(Ansible) to reconfigure the bare template.

### 3. UID/GID Mapping for tmpfs Ownership

The tmpfs on the host must be owned by the **shifted** IDs:

| In-CT ID | Host ID | Purpose |
|---|---|---|
| UID 999 (plex) | UID 100999 | tmpfs owner |
| GID 991 (plex) | GID 100991 | tmpfs group |

The fstab entry should use `uid=100999,gid=100991`.

### 4. USB Mount Pattern (Template for Runbook)

Host fstab entries for USB drives use:
- `nofail` — prevents boot failure if mount unavailable
- `x-systemd.device-timeout=10s` — limits boot stall

For tmpfs, `nofail` is not needed (tmpfs always succeeds), but the pattern
is useful for the runbook format.

### 5. Existing Bind Mounts in `module "plex"`

Current mounts:
1. `/tank/Media` → `/media` (RO) — DAS ZFS media
2. `/tank/Server/AppData/plex` → `/var/lib/plexmediaserver` (RW) — state
3. `/mnt/xtra-one` → `/mnt/xtra-one` (RO) — USB drive 1
4. `/mnt/xtra-two` → `/mnt/xtra-two` (RO) — USB drive 2

New mount would be:
5. `/mnt/plex-transcode` → `/transcode` (RW) — ramdisk

### 6. Ansible Execution Flow

- `just config` = `gen-inventory` + `play` (runs `ansible/site.yml`)
- Play 3 in `site.yml` targets `hosts: plex` with `roles: [plex]`
- The plex role handles: apt setup → ID pinning → package install → GPU groups → systemd override → service start → vainfo gate

### 7. Handler Pattern

The existing handler `Restart plexmediaserver` uses `daemon_reload: true`.
The TranscoderTempDirectory change would need a Plex restart (not just
daemon-reload), so the existing handler pattern works.
