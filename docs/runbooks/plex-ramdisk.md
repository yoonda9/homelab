# Runbook: Plex transcode ramdisk (host tmpfs → CT 110 `/transcode`)

This runbook covers the **host-level `tmpfs` ramdisk** that offloads Plex
transcoding temp files off the `DASPool` ZFS pool and into RAM. A fixed **4 GB**
`tmpfs` is mounted on the Proxmox host `pve` at `/mnt/plex-transcode` via
`/etc/fstab`, and later bind-mounted into the unprivileged Plex CT (CT 110) as
`/transcode` by OpenTofu (`tofu/main.tf` `module "plex"` — Step 3) so Plex can
point `TranscoderTempDirectory` at it (Step 4).

The split of responsibilities mirrors `usb-media-mounts.md`: the **host mount is
a manual, operator-run step** on `pve` (editing `/etc/fstab` and running
`mount -a` — nothing in this repo provisions the host mount), while the **bind
mount into the CT is owned by OpenTofu**. This runbook is the repo-side
deliverable for the host half; **the apply itself is the operator's** (see §2).

> ℹ️ **Why a host tmpfs and not a container one?** A `tmpfs` created *inside*
> the CT draws from the container's cgroup memory limit and can trigger
> in-container OOM pressure. Mounting it on the **host** and binding it through
> draws from the host's main memory pool instead, and keeps the size cap under
> host control — **host stability is paramount** (better a flaky container than
> a downed host).

---

## 1. The fstab entry (on `pve`)

Add exactly one line to the host's `/etc/fstab`:

```
# Plex transcode ramdisk — 4G tmpfs, owned by the CT 110 shifted plex ids (see below)
tmpfs /mnt/plex-transcode tmpfs size=4G,mode=0755,uid=100999,gid=100991 0 0
```

Field by field:

- **`tmpfs` (fs_spec) / `tmpfs` (fs_vfstype)** — a RAM-backed filesystem; there
  is no block device, so the source pseudo-device is literally `tmpfs`.
- **`/mnt/plex-transcode`** — the mount point, consistent with the existing
  `/mnt/xtra-one` / `/mnt/xtra-two` USB convention.
- **`size=4G`** — the **fixed cap** (see §"Why a fixed `size=4G`" below).
- **`uid=100999,gid=100991`** — the **shifted** owner (see §"Shifted ownership"
  below). tmpfs applies these at mount time; there is no on-disk ownership to
  `chown`.
- **`mode=0755`** — owner (the shifted `plex`) gets `rwx`; the mount root is
  world-readable but only the owner writes. Plex runs as the owner, so it can
  create transcode temp files.
- **`0 0`** — no `dump`, and **no boot-time `fsck`** (fs pass `0`): a RAM
  filesystem is created empty on every mount, so there is nothing to check.

Unlike the USB drives in `usb-media-mounts.md`, `nofail` /
`x-systemd.device-timeout` are **not required** here: a `tmpfs` mount cannot fail
for a missing device — it always succeeds — so it can never drop the host into
emergency mode at boot.

### Shifted ownership — why `100999:100991`, not `999:991`

CT 110 is an **unprivileged** LXC. Its idmap is a single offset tile
(`tofu/locals.tf` `plex_uid_maps`): container id *N* → host id *N + 100000*
across the whole `0..65535` space. Plex runs in-CT as `plex` = **`uid=999`,
`gid=991`**, so on the host those ids appear as:

| In-CT (CT 110) | `+100000` offset | Host id | Role |
|---|---|---|---|
| `uid=999` (plex) | +100000 | **`uid=100999`** | tmpfs owner |
| `gid=991` (plex) | +100000 | **`gid=100991`** | tmpfs group |

The host mount **must** be owned by `100999:100991`. If it is owned by anything
else (e.g. a bare `999:991`, or root `0:0`), the container's idmap has no entry
that maps it back, so inside CT 110 the mount surfaces as **`nobody:nogroup`**
(the `65534` overflow ids) and Plex — running as `plex`, not `nobody` — cannot
write to it. Owning it `100999:100991` on the host is exactly what makes it read
back as `plex:plex` inside the container.

### Why a fixed `size=4G` — the host-stability cap

`tmpfs` with no `size=` defaults to **half of RAM** and grows on demand — a
transcode storm could then balloon and **OOM the host**. Pinning `size=4G`
**caps** the RAM this mount can ever consume regardless of how many concurrent
transcodes Plex starts. When the ramdisk fills, writes fail with **`ENOSPC`
("No space left on device")** and Plex fails *that* transcode gracefully — the
host and the Plex server stay up. A bounded, self-limiting failure is the whole
point: the cap trades a failed stream for a stable host.

## 2. Apply on the host — OPERATOR step

> ⚠️ **This section is run by the operator on `pve`, by hand.** Nothing in this
> repo (no OpenTofu, no Ansible, no agent) edits host `/etc/fstab` or runs
> `mount` on `pve`. The tracked runtime task for this apply is **not
> agent-closable** — it is closed only after a human runs and verifies the steps
> below.

On the Proxmox host `pve`:

```bash
mkdir -p /mnt/plex-transcode          # mount point must exist before mounting
# append the fstab line from §1 to /etc/fstab (edit by hand)
mount -a                              # mount everything in fstab not yet mounted
```

`mount -a` reads the new `/etc/fstab` line and mounts the `tmpfs` immediately —
no reboot needed. The mount point must exist **before** the CT starts; local
fstab mounts are ordered before `pve-guests` by systemd, so on a normal boot the
ramdisk is present before CT 110 comes up.

## 3. Verify (on `pve`)

```bash
findmnt /mnt/plex-transcode          # SOURCE=tmpfs, FSTYPE=tmpfs, size ~4.0G
stat /mnt/plex-transcode             # Uid: (100999/…)  Gid: (100991/…)
```

Acceptance for this step:

- `findmnt /mnt/plex-transcode` reports **`tmpfs`** as both source and fstype,
  with the size showing **4.0G** (`findmnt -o TARGET,SOURCE,FSTYPE,SIZE`).
- `stat /mnt/plex-transcode` shows **`Uid`** = **`100999`** and **`Gid`** =
  **`100991`** — the shifted `plex` owner from §1.

Only once both checks pass is the host ready for Step 3 (the OpenTofu
`bind_mounts` entry `/mnt/plex-transcode` → `/transcode`), which will
destroy/recreate CT 110 — its own separately gated, operator-timed step.

## 4. Downstream (context, not part of this runbook's apply)

- **Step 3 (OpenTofu)** adds `{ host_path = "/mnt/plex-transcode", ct_path =
  "/transcode", read_only = false }` to `module "plex"` `bind_mounts`. On
  `bpg/proxmox` v0.110.0 a new `mount_point` **destroys and recreates** the CT
  (safe because Plex state lives on host storage), so it runs behind its own
  live-ops operator gate; re-run `just config` after `just apply`.
- **Step 4 (Ansible)** sets `TranscoderTempDirectory="/transcode"` in
  `Preferences.xml` via `community.general.xml` and restarts Plex.

## 5. Operational caveats

- **The ramdisk is volatile.** Its contents vanish on every host reboot or
  `umount` — that is correct: transcode temp files are disposable. Plex
  recreates its working directory as needed.
- **If a drive/`plex` id ever changes**, the `uid=`/`gid=` in the fstab line
  must be re-derived from `999/991 + 100000`; the OpenTofu bind mount is
  path-based and needs no change as long as the mount point stays
  `/mnt/plex-transcode`.
- **Do not register this as PVE "Directory" storage** — a plain fstab `tmpfs` +
  bind mount is the right mechanism, same as the media drives.
