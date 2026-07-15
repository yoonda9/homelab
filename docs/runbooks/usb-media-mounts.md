# Runbook: USB media drives (non-ZFS) → host automount + Plex bind mounts

This runbook covers attaching **non-ZFS USB external drives** (ext4/xfs/NTFS/
exFAT) to the Proxmox host `pve` so they **automount on boot** via `/etc/fstab`,
and wiring them into the Plex CT as additional read-only bind mounts alongside
`/tank/Media` (see `das-zfs-migration.md` for the ZFS DAS).

The split of responsibilities mirrors the DAS runbook: the **host mount is a
manual, discovery-based step** (no OpenTofu/Ansible provisions it — the drives'
UUIDs and filesystems are unknown until attached), while the **bind mount into
the CT is owned by OpenTofu** via `module "plex"`'s `bind_mounts` in
`tofu/main.tf`. The procedure is discovery-based: **read the real UUIDs and
filesystem types from `lsblk -f` output** and substitute them for `<uuid>` /
`<fstype>` throughout. **Do not hardcode `/dev/sdX` device names** — USB device
names reorder on replug and reboot; fstab entries must use `UUID=`.

> ⚠️ **No redundancy, no backups.** Same risk posture as the DAS pool: treat
> these drives as media-cache, not as the only copy of anything irreplaceable.
> Unlike ZFS there is no scrub/checksum layer here — silent corruption goes
> undetected.

---

## 1. Discovery (on `pve`)

**Discovery first — this mounts nothing.** With both drives attached:

```bash
lsblk -f          # device, FSTYPE, UUID, LABEL, current mountpoint
```

Note for each drive:

- the **UUID** (used in fstab — stable across replug/reboot),
- the **filesystem type** (`ext4`, `xfs`, `ntfs`, `exfat`) — it decides the
  mount options in step 2 and the permission model in step 3,
- where the media lives on the drive (e.g. a top-level `Media/` directory —
  step 4 binds that subdirectory, not the mount root).

If a drive shows no filesystem or an unexpected one, stop — this runbook does
not cover (re)formatting.

## 2. fstab automount (on `pve`)

Create one mount point per drive:

```bash
mkdir -p /mnt/usb1 /mnt/usb2
```

Append to `/etc/fstab`, picking the line matching each drive's filesystem:

```
# ext4/xfs — real POSIX ownership on disk (fix ownership in step 3)
UUID=<uuid>  /mnt/usb1  ext4  defaults,nofail,x-systemd.device-timeout=10s  0  2

# NTFS (kernel ntfs3 driver) — no POSIX ownership; set it at mount time
UUID=<uuid>  /mnt/usb2  ntfs3  defaults,nofail,x-systemd.device-timeout=10s,uid=0,gid=993,fmask=0137,dmask=0027  0  0

# exFAT — same idea as NTFS
UUID=<uuid>  /mnt/usb2  exfat  defaults,nofail,x-systemd.device-timeout=10s,uid=0,gid=993,fmask=0137,dmask=0027  0  0
```

Two options are non-negotiable because these are USB drives:

- **`nofail`** — without it, a detached/dead drive drops the host into
  **emergency mode at boot**, taking every CT and VM down with it.
- **`x-systemd.device-timeout=10s`** — without it, a missing drive stalls boot
  for the systemd default of **90 s per drive** before `nofail` kicks in.

Notes:

- **`ntfs3`** is the in-kernel NTFS driver (Proxmox 8+ kernels). If mounting
  fails with an unknown-fstype error, fall back to `ntfs-3g` (FUSE):
  `apt install ntfs-3g` and use fstype `ntfs-3g` in fstab.
- **`gid=993,fmask=0137,dmask=0027`** on NTFS/exFAT presents files as
  group-readable by host GID **993** — see step 3 for why that GID.
- The final `0 2` / `0 0` field: fsck ordering. Native Linux filesystems get
  `2`; NTFS/exFAT have no boot-time fsck, so `0`.

Test **without rebooting**:

```bash
systemctl daemon-reload      # regenerate mount units from fstab
mount -a                     # mount everything not yet mounted
findmnt /mnt/usb1 /mnt/usb2  # both must show the expected source + fstype
```

Then verify the automount survives a real boot: reboot `pve` once and re-run
`findmnt` (acceptance gate for this step — same spirit as the DAS runbook's
re-import check).

## 3. Ownership for the unprivileged CT

The Plex CT is **unprivileged** with a gap-free idmap tiling that punches only
host GIDs **993** (`render`) and **44** (`video`) through 1:1 (see
`das-zfs-migration.md` § "idmap fallback" and `tofu/locals.tf`). Everything
else appears as `nobody:nogroup` inside the CT. The media must therefore be
readable via one of the punched GIDs (993 is the convention) or world-readable
— match whatever `/tank/Media` does (`stat /tank/Media` to check).

- **ext4/xfs** — ownership lives on disk; fix it once on the host:

  ```bash
  chgrp -R 993 /mnt/usb1/Media
  chmod -R g+rX /mnt/usb1/Media     # or o+rX for world-readable
  ```

- **NTFS/exFAT** — no POSIX ownership on disk; `chown`/`chgrp` will not stick.
  The `gid=993,fmask=0137,dmask=0027` mount options from step 2 already present
  everything as group-readable by GID 993. Nothing to do here.

## 4. Wire the drives into the Plex CT (OpenTofu)

Add one entry per drive to the existing `bind_mounts` list in `module "plex"`
(`tofu/main.tf`), next to the `/tank/Media` entry:

```hcl
bind_mounts = [
  { host_path = "/tank/Media", ct_path = "/media", read_only = true },
  { host_path = "/mnt/usb1/Media", ct_path = "/media-usb1", read_only = true },
  { host_path = "/mnt/usb2/Media", ct_path = "/media-usb2", read_only = true },
]
```

Then `just plan` / `just apply`. **Expect a full destroy/recreate, not a
restart**: on bpg v0.110.0 a new `mount_point` entry flags its `volume` with
`# forces replacement` (observed live; regression tracked in
bpg/terraform-provider-proxmox#2507 — the v0.94.0 fix covered cloned CTs
only). The rebuild is only safe for Plex because its state dir is persisted on
host storage (`plex-claim.md` §5) — run that section's cutover checks first,
and after the apply re-run the `plex` role (`just config`) since the recreated
CT is a bare template. Afterwards, add
`/media-usb1` and `/media-usb2` as library folders inside the Plex app.

- **Bind the `Media/` subdirectory, not the mount root — deliberate.** If a
  drive is absent at boot, `/mnt/usb1` still exists as an empty directory
  (thanks to `nofail` the host boots fine), and a CT bound to it would start
  normally with an **empty `/media-usb1`** — Plex then sees an empty library
  and may mark everything deleted. Binding `/mnt/usb1/Media` — a directory that
  only exists **on the mounted filesystem** — makes the CT **fail to start
  loudly** instead. Fail-loud beats silently-empty.
- The mount must exist on the host **before** the CT starts (same ordering rule
  as the DAS runbook's mountpoint-first requirement). fstab local mounts are
  ordered before `pve-guests` by systemd, so this holds on a normal boot.

## 5. Operational caveats

- **Bind mounts are not captured by `vzdump`** and do not support CT snapshots
  — already true for `/tank/Media`, so these two add nothing new.
- **USB disconnect ≠ pool suspend, but it's not graceful either** — a cable
  bump yanks the filesystem out from under the bind mount; Plex sees I/O errors
  until the drive is remounted and the CT restarted. Prefer powered ports and
  cables that won't get bumped (same advice as the DAS).
- **Do not register these as PVE "Directory" storage** (`pvesm`/GUI) — that is
  for backups/ISOs/templates. Plain fstab + bind mount is the right mechanism
  for media.
- **If a drive is replaced**, its UUID changes: update the fstab entry
  (discovery, step 1) — the Tofu side is path-based and needs no change as long
  as the mount point and `Media/` layout stay the same.
