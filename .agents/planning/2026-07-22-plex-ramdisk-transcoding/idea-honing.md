# Idea Honing

Requirements clarification for: Add a ramdisk to plex for transcoding

---

## Q1: Ramdisk Size and Container RAM

Your Plex LXC container currently has **4096 MB (4 GB) RAM**. A tmpfs ramdisk consumes RAM from the container's allocation. Plex transcoding temp files can range from a few hundred MB for a single stream to several GB for multiple concurrent transcodes.

**How large should the ramdisk be, and do you want to increase the container's total RAM allocation to accommodate it?**

Some options to consider:
- **2 GB ramdisk** — handles 1–2 concurrent transcodes comfortably; may require bumping container RAM to 6–8 GB
- **4 GB ramdisk** — handles several concurrent streams; would likely need 8+ GB container RAM
- **Other size** — based on your typical usage patterns

How many concurrent transcodes do you typically run, and how much total host RAM is available on your Proxmox box?

**A1:** Typically 1–2 concurrent transcodes. Go with a **4 GB ramdisk**. The host has sufficient memory to accommodate this. Container RAM should be increased accordingly (e.g., to 8 GB to leave 4 GB for Plex itself plus the 4 GB tmpfs).

---

## Q2: Implementation Layer — Ansible, OpenTofu, or Both?

Your current infrastructure uses **OpenTofu** to define the LXC container (CPU, RAM, mounts) and **Ansible** to configure software inside it. For the ramdisk, we need to:

1. **Increase container RAM** — this is an OpenTofu change (bumping `memory` from 4096 to 8192 in `tofu/main.tf`)
2. **Create the tmpfs mount** — this could be done either way:
   - **Inside the container via Ansible** — add a systemd mount unit or `/etc/fstab` entry for a tmpfs at e.g. `/tmp/plex-transcode`
   - **At the Proxmox level via OpenTofu** — if the LXC module supports tmpfs mount points (less common for LXC)
3. **Configure Plex to use the new path** — Ansible task or manual Plex UI setting

**Should the tmpfs mount be managed by Ansible (inside the container), and the RAM increase by OpenTofu? Or do you have a preference for a different split?**

**A2:** Go with **Option B — tmpfs on the Proxmox host, bind-mounted into the container via OpenTofu**. This follows the existing bind-mount pattern and avoids cgroup memory pressure. The container RAM can stay at 4 GB. Key constraint: **host stability is paramount** — better for the container to be flaky than the host. A fixed-size tmpfs (`size=4G`) is safe since it caps RAM usage and only affects writes to that mount on overflow.

---

## Q3: Managing the Host-Level tmpfs for Reproducibility

You currently have USB drive fstab entries on the Proxmox host (e.g., `/mnt/xtra-one`, `/mnt/xtra-two`). The new tmpfs would need a similar host fstab entry like:

```
tmpfs /mnt/plex-transcode tmpfs size=4G,mode=0755,uid=100999,gid=100991 0 0
```

**How should this host-level fstab entry be managed?**

- **Ansible host playbook** — create or extend a playbook that targets the Proxmox host directly (most reproducible, fully automated)
- **Documented manual step** — add it to a runbook, apply it once by hand (simpler, matches how USB mounts were likely set up)
- **Other** — e.g., a Packer template, cloud-init, etc.

**A3:** **Documented manual step** — add the host fstab entry to a runbook. Apply once by hand. Consistent with how the USB drive mounts were set up.

---

## Q4: Configuring Plex to Use the New Transcode Path

Once the tmpfs is mounted inside the container (e.g., at `/tmp/plex-transcode` or `/transcode`), Plex needs to be told to use it instead of the default location. There are a few ways to do this:

- **Ansible automation** — modify Plex's `Preferences.xml` to set `TranscoderTempDirectory` (keeps config in code, runs on every `just play plex`)
- **Manual via Plex Web UI** — Settings → Transcoder → "Transcoder temporary directory" (simple one-time change, but not captured in code)

**Should Plex's transcode directory setting be managed by Ansible, or set manually in the Plex UI?**

**A4:** **Ansible-managed** — use `community.general.xml` module to surgically set only the `TranscoderTempDirectory` attribute in `Preferences.xml`. Stop Plex before modification, restart after. This is safe, idempotent, and won't touch the claim token or other settings. We will add `community.general` to the Ansible `requirements.yml` file to support this.

---

## Q5: Mount Paths and Verification

Two quick practical details:

**Mount paths** — I'd suggest:
- **Host**: `/mnt/plex-transcode` (consistent with your existing `/mnt/xtra-one`, `/mnt/xtra-two` convention)
- **Container**: `/transcode` (clean, short, purpose-obvious)

Do these paths work, or do you prefer something different?

**Verification** — your existing Plex role already has an acceptance gate (checking `vainfo` for hardware transcode). Should we add a similar verification task that confirms the ramdisk is mounted and accessible by the `plex` user inside the container?

**A5:** Paths confirmed:
- **Host**: `/mnt/plex-transcode`
- **Container**: `/transcode`

Yes, add a **verification task** in Ansible to confirm the ramdisk is mounted and accessible.

