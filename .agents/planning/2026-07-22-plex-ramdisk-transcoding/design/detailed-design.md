# Detailed Design: Plex Ramdisk for Transcoding

## Overview
This design details the addition of a 4 GB RAM disk (`tmpfs`) to the existing Plex LXC container (CT 110) in the Proxmox homelab environment to handle Plex transcoding. The goal is to offload temporary transcode writes from the host ZFS pool (`DASPool`) to memory, improving performance and reducing unnecessary disk I/O. The architecture mounts the tmpfs on the Proxmox host and passes it through to the unprivileged container, avoiding container cgroup memory pressure.

## Detailed Requirements
- **Ramdisk Size**: 4 GB tmpfs.
- **Architecture Location**: Mounted on the Proxmox host (`pve`) and bind-mounted into the Plex container via OpenTofu.
- **Container Resources**: Container RAM stays at 4096 MB since the host-level tmpfs draws from the host's main memory pool, not the container's cgroup.
- **Host Configuration**: A manual, documented step in a runbook (fstab entry) for creating the tmpfs on the host, following the pattern of existing USB media mounts.
- **OpenTofu**: Add a bind mount for `/mnt/plex-transcode` (host) to `/transcode` (container).
- **Plex Configuration**: Use Ansible to surgically update `Preferences.xml` via the `community.general.xml` module. This requires modifying `ansible/requirements.yml` to include the `community.general` collection.
- **Verification**: Include an Ansible assertion to verify that the ramdisk is successfully mounted and writable by the `plex` user inside the container.
- **Host Stability**: Paramount. A fixed-size tmpfs (`size=4G`) guarantees memory usage will not spike uncontrollably and take down the host.

## Architecture Overview
The system relies on a host-level `tmpfs` volume mounted via `/etc/fstab` on Proxmox. OpenTofu binds this directory into the unprivileged Plex LXC (CT 110). Since the container is unprivileged with shifted UIDs, the host `tmpfs` must be explicitly owned by the shifted IDs corresponding to the `plex` user and group. Inside the container, Ansible uses `community.general.xml` to instruct Plex Media Server to route all temporary transcoding files to this new mount point (`/transcode`).

```mermaid
flowchart TD
    subgraph Host[Proxmox Host pve]
        Fstab[/etc/fstab] -->|Mounts| Tmpfs[tmpfs 4GB]
        Tmpfs -->|Path| HostMount[/mnt/plex-transcode\nuid=100999,gid=100991]
    end

    subgraph LXC[Plex CT 110 unprivileged]
        HostMount -.->|Tofu bind_mount| CTMount[/transcode]
        PlexXML[Preferences.xml\nTranscoderTempDirectory=/transcode]
        PlexApp[Plex Media Server]
        PlexXML --> PlexApp
        PlexApp -->|Writes transcodes| CTMount
    end
```

## Components and Interfaces

### 1. Host tmpfs (Proxmox /etc/fstab)
A standard `tmpfs` filesystem mounted on the Proxmox host.
- **Path**: `/mnt/plex-transcode`
- **Size**: `4G`
- **Permissions/Ownership**: Due to the unprivileged container ID mapping (UID shift +100000), the mount must be owned by `uid=100999, gid=100991`. This maps perfectly to the in-container `plex:plex` (UID 999, GID 991).

### 2. OpenTofu Bind Mount
The `module "plex"` in `tofu/main.tf` will receive a new entry in its `bind_mounts` list:
- `host_path`: `/mnt/plex-transcode`
- `ct_path`: `/transcode`
- `read_only`: `false`

### 3. Ansible Configuration
The Plex role (`ansible/roles/plex`) will be updated to:
- Stop Plex before making configuration changes.
- Use `community.general.xml` to update `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Preferences.xml`, setting `TranscoderTempDirectory="/transcode"`.
- Restart Plex.
- Include a verification task asserting that `/transcode` exists, is a directory, is mounted as a tmpfs, and is writable by the `plex` user.

## Data Models
- **Preferences.xml**: Modifying a single attribute (`TranscoderTempDirectory`). This avoids touching sensitive values like `PlexOnlineToken` or `MachineIdentifier`.
- **ID Map**:
  - `plex_uid` = `999` $\rightarrow$ `100999` (Host UID)
  - `plex_gid` = `991` $\rightarrow$ `100991` (Host GID)

## Error Handling
- **Full Ramdisk (4GB)**: If multiple concurrent transcodes exceed 4GB, the `tmpfs` will return "No space left on device" (ENOSPC). Plex handles this gracefully per stream by failing the transcode, but it will not crash the server or the host machine.
- **Missing Mount on Boot**: If the host `tmpfs` fails to mount, OpenTofu container startup will fail cleanly due to missing bind source, preventing Plex from starting in an unknown state.

## Testing Strategy
1. **Host Verification**: `findmnt /mnt/plex-transcode` confirms the host mount and parameters.
2. **Container Verification**: Ansible task asserts that `/transcode` inside CT 110 is owned by `plex:plex` and is writable.
3. **Plex Verification**: Review Plex Web UI (Settings > Transcoder) to confirm the new path is active, and trigger a media transcode while monitoring `df -h /transcode` inside the container to observe space utilization.

## Appendices

### Research Findings Summary
- **Ansible Environment**: The project currently uses `ansible.builtin`-only modules. Using `community.general.xml` requires adding `community.general` to `ansible/requirements.yml` and running `just galaxy`.
- **OpenTofu Behavior**: In `bpg/proxmox` v0.110.0, adding a `mount_point` causes the container to be fully destroyed and recreated. Because state (`/var/lib/plexmediaserver`) is securely backed by ZFS, this is a safe operation, but necessitates running `just config` after `just apply` to re-apply software configuration to the fresh template.
- **UID/GID Mapping**: Verified that `plex` uses UID 999 and GID 991, which map cleanly to the 100000 offset tile (100999 and 100991).
