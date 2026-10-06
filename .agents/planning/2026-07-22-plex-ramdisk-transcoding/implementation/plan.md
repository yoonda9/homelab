# Implementation Plan: Plex Ramdisk for Transcoding

## Checklist

- [ ] **Step 1:** Add Ansible Dependency (`community.general`)
- [ ] **Step 2:** Document and Provision Host tmpfs
- [ ] **Step 3:** Wire tmpfs into Plex Container via OpenTofu
- [ ] **Step 4:** Configure Plex Transcoder via Ansible

---

## Detailed Steps

### Step 1: Add Ansible Dependency (`community.general`)

**Objective**: Ensure the Ansible environment has the necessary collection to parse and edit XML files idempotently.

- **Implementation**:
  - Open `ansible/requirements.yml`.
  - Add the `community.general` collection to the `collections` list (create the list if it doesn't exist).
- **Test Requirements**:
  - Run `just galaxy` in the `ansible/` directory.
  - Verify that `community.general` is successfully downloaded into the `ansible/galaxy_roles/` or equivalent collections path without errors.
- **Demo**: Show that the local Ansible environment now contains the `community.general` collection by running `ansible-galaxy collection list -p ansible/galaxy_roles/` (or the respective path).

### Step 2: Document and Provision Host tmpfs

**Objective**: Document the host-level tmpfs mount procedure for reproducibility and manually apply it to the Proxmox host to prepare for the container bind mount.

- **Implementation**:
  - Create a new section in `docs/runbooks/usb-media-mounts.md` (or a dedicated `plex-ramdisk.md` runbook) detailing the `fstab` entry:
    ```
    tmpfs /mnt/plex-transcode tmpfs size=4G,mode=0755,uid=100999,gid=100991 0 0
    ```
  - SSH into the Proxmox host (`pve`).
  - Create the mount directory: `mkdir -p /mnt/plex-transcode`.
  - Append the entry to `/etc/fstab`.
  - Run `systemctl daemon-reload` and `mount -a`.
- **Test Requirements**:
  - Run `findmnt /mnt/plex-transcode` on the host to ensure it mounts correctly as `tmpfs`.
  - Run `stat /mnt/plex-transcode` and verify the `Uid` is `100999` and `Gid` is `100991`.
- **Demo**: The host has a 4GB tmpfs actively mounted with the correct shifted IDs, ready to be consumed by the container.

### Step 3: Wire tmpfs into Plex Container via OpenTofu

**Objective**: Pass the host tmpfs through to the unprivileged Plex container so it is available at `/transcode`.

- **Implementation**:
  - Edit `tofu/main.tf`, specifically the `module "plex"` block.
  - Append a new dictionary to the `bind_mounts` list:
    ```hcl
    {
      host_path = "/mnt/plex-transcode"
      ct_path   = "/transcode"
      read_only = false
    }
    ```
  - Run `just apply`.
- **Test Requirements**:
  - Acknowledge that the Tofu apply will destroy and recreate CT 110.
  - After apply finishes, run `just config` to quickly re-apply the baseline Ansible state to the fresh container.
  - SSH into CT 110 or use `lxc-attach` to verify that `df -h /transcode` shows a `tmpfs` mount of size `4.0G`, and `stat /transcode` shows ownership by `plex:plex`.
- **Demo**: The Plex container is running, and the `/transcode` directory is visible inside it, backed by the host's RAM, with correct unprivileged ownership.

### Step 4: Configure Plex Transcoder via Ansible

**Objective**: Instruct Plex to route its temporary transcoding files to the new ramdisk using an automated, idempotent Ansible task.

- **Implementation**:
  - Edit `ansible/roles/plex/tasks/main.yml`.
  - Add a task using `community.general.xml` to set the `TranscoderTempDirectory` attribute on the `/Preferences` xpath to `/transcode`.
  - Ensure the task modifies `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Preferences.xml`.
  - Wrap this task so that the Plex service is safely stopped before modification, and restarted after (or use a handler).
  - Add an assertion/verification task that checks if `/transcode` is mounted and writable by the `plex` user.
- **Test Requirements**:
  - Run `just play` to apply the updated role.
  - Assertions in the playbook must pass cleanly.
  - Re-run `just play` to ensure the `xml` modification is strictly idempotent (reports "ok", not "changed").
- **Demo**: Open the Plex Web UI, navigate to Settings > Transcoder, and visually confirm "Transcoder temporary directory" is `/transcode`. Start a stream that requires transcoding (e.g., forcing a lower bitrate) and observe files populating inside `/transcode` (via SSH) without touching the host ZFS disks.
