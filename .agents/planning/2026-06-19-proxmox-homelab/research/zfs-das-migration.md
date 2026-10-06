# Research: ZFS-on-USB DAS import + media migration runbook

_Sources: OpenZFS docs/man pages + unit files, Proxmox wiki/forum (verified 2026-06-19).
DAS = QNAP enclosure, hardware RAID0 presenting ONE block device, single-vdev ZFS pool on top.
**Migration is a one-time, MANUAL, documented task** — NOT automated (per Q6b)._

## Single hardware-RAID0 + ZFS pool: imports like any pool
ZFS sees one device / one top-level vdev; it neither knows nor cares about the controller's
RAID0 underneath. Same import mechanics as any pool. Verify with `zpool status` (one ONLINE
vdev). ⚠️ **Zero ZFS redundancy** — no self-healing of file data; any underlying member-disk
failure loses the whole pool. (Backups are out of scope per Q9, risk accepted.)

## Safe import procedure (the core of the runbook)
```
# 1. Physically move DAS to pve (power off old server first; export there if still alive)
zpool import                                      # DISCOVERY ONLY — lists pools, imports nothing
zpool import -f -d /dev/disk/by-id <poolname>     # -f: foreign hostid; by-id for USB stability
zpool set cachefile=/etc/zfs/zpool.cache <pool>   # persist auto-import across reboot
zpool status <pool>                               # verify ONLINE + by-id paths
zfs list                                          # confirm datasets + mountpoints
```
- **`-f` is needed** when the pool wasn't cleanly exported (label hostid ≠ this host). Safe for
  a physically-moved disk; dangerous ONLY if another *live* host accesses the same devices.
- **Cleaner if old host still alive:** `zpool export <pool>` there first, then import here
  **without `-f`**.
- **Always import by `/dev/disk/by-id`** for USB (`/dev/sdX` reorders on replug). If the pool
  currently uses `sdX` paths, an export + `import -d /dev/disk/by-id` converts them.

## USB-attached ZFS caveats (operational risks to document)
- A USB controller reset/disconnect can fault a device and **suspend the whole pool** (I/O
  hangs until `zpool clear` or reboot). Budget for this.
- **Keep `autotrim=off` over USB** (many bridges mishandle UNMAP/discard; has made pools
  temporarily unimportable). Check `lsblk -D` before considering trim.
- **Scrub periodically** (`zpool scrub <pool>`); some cheap multi-bay enclosures don't expose
  per-disk serials in `by-id` — verify yours does before relying on it.
- Reboot auto-import is driven by `zfs-import-cache.service` + the cachefile (Proxmox default).

## Expose a dataset to the Plex LXC (bind mount)
The dataset must be **mounted on the host first** (its `mountpoint`), then bind into the CT.
- Via Proxmox: `mp0: /tank/media,mp=/media` in `/etc/pve/lxc/<CTID>.conf`
  (or `pct set <CTID> -mp0 /tank/media,mp=/media`).
- Via bpg OpenTofu: `mount_point { volume = "/tank/media", path = "/media" }` (needs root@pam).
- **Unprivileged ownership:** host IDs shift +100000 → files show as `nobody:nogroup` inside.
  Fix by (A) `chown` host dir to the mapped uid/gid, (B) `idmap` a range back to real host IDs,
  or (C) `zfs set acltype=posixacl` + ACLs (less reliable unprivileged). Prefer A or B.
- ⚠️ Bind mounts are **not** captured by `vzdump` and don't support CT snapshots (fine — media
  is on ZFS, backups are a separate task).

## Migration runbook outline (to formalize in design/implementation)
1. **Pre-move (old server):** stop Plex/Docker; `zpool export <pool>` if reachable; note pool
   name + dataset layout; verify media checksums/inventory if desired.
2. **Physical move:** power down both; relocate DAS to pve; power up.
3. **Import:** discovery → `zpool import -f -d /dev/disk/by-id <pool>` → set cachefile.
4. **Verify:** `zpool status` ONLINE, `zfs list`, spot-check media files + counts ("raw data
   intact" = the migration acceptance gate).
5. **Set `autotrim=off`; schedule a scrub.**
6. **Wire to Plex LXC** via bind mount; chown/idmap as needed; (re)scan Plex libraries
   (metadata rebuilt).

> The runbook can't be fully validated until the DAS is attached (pool name/datasets unknown
> today). It must be **discovery-based** (read pool name from `zpool import` output).

## URLs
- zpool-import man: https://openzfs.github.io/openzfs-docs/man/master/8/zpool-import.8.html
- ZFS-8000-EY (foreign hostid): https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-EY/index.html
- Proxmox LXC (bind mounts): https://pve.proxmox.com/wiki/Linux_Container
- OpenZFS FAQ (by-id, redundancy): https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html
