# Runbook: DAS → ZFS migration (`/tank`) + host `/tank/Media` for Plex

This runbook covers the **one-time, manual** migration of the QNAP DAS and its
ZFS pool onto the Proxmox host `pve`, and establishes the host **`/tank/Media`**
path that the Plex CT bind-mounts as `/media` in Step 7.

The migration is **explicitly outside the automation "done" scope** (per the
design): no OpenTofu or Ansible code provisions it, and it cannot be fully
validated until the DAS is physically attached. The procedure is therefore
**discovery-based** — the pool name and dataset layout are unknown until the
disk is imported, so you **read the pool name from `zpool import` output** and
substitute it for `<pool>` throughout. **Do not hardcode a pool name.**

> **Hardware (design §3):** the DAS is a QNAP enclosure in hardware **RAID0**
> presenting **one** block device, with a **single-vdev** ZFS pool on top. ZFS
> imports it like any single-vdev pool; it neither knows nor cares about the
> controller's RAID0 underneath.
>
> ⚠️ **Zero ZFS redundancy.** RAID0 means any underlying member-disk failure
> loses the whole pool, and ZFS cannot self-heal file data (no redundant copy to
> repair from). Backups are out of scope (risk accepted) — treat this pool as
> media-cache, not as the only copy of anything irreplaceable.

---

## 1. Pre-move (old server)

Done on the machine the DAS is currently attached to, **if it is still
reachable**. A clean export here is the safest path — it clears the pool's
hostid so the import on `pve` needs no `-f`.

1. Stop everything writing to the pool (Plex, Docker, any sync jobs).
2. Note the **pool name** and dataset layout for reference:

   ```bash
   zpool status
   zfs list
   ```

3. Export the pool so it can be cleanly imported elsewhere:

   ```bash
   zpool export <pool>
   ```

> If the old host is dead/unreachable, skip the export — you will import with
> `-f` in step 3 instead. That is safe for a **physically moved** disk; it is
> dangerous **only** if another *live* host still has these devices online.

## 2. Physical move

1. Power down **both** machines (old server and `pve`).
2. Relocate the DAS enclosure to `pve`; connect its USB cable.
3. Power up `pve`.

## 3. Discovery + import (on `pve`)

**Discovery first — this imports nothing.** Read the real pool name from the
output and use it for `<pool>` below.

```bash
zpool import                                      # DISCOVERY ONLY — lists importable pools
```

Then import the pool **by `/dev/disk/by-id`** (USB `/dev/sdX` names reorder on
replug; `by-id` paths are stable):

```bash
zpool import -f -d /dev/disk/by-id <pool>         # -f: foreign hostid (skip -f if you exported cleanly in step 1)
zpool set cachefile=/etc/zfs/zpool.cache <pool>   # persist auto-import across reboot
zfs set mountpoint=/tank <pool>                   # host mountpoint -> /tank
```

- **`-f`** forces an import when the pool's on-disk label carries a different
  hostid than `pve` (i.e. it was not cleanly exported). Safe for a moved disk;
  omit it if step 1's `zpool export` succeeded.
- **`-d /dev/disk/by-id`** pins the pool to stable device paths. If the pool
  currently references `sdX` paths, this import converts them.
- **`cachefile=/etc/zfs/zpool.cache`** is what `zfs-import-cache.service` reads
  to **auto-import the pool on every reboot** (the Proxmox default). Without it,
  the pool will not come back automatically after a restart.
- **`mountpoint=/tank`** sets the host mount root. Media then lives under
  **`/tank/Media`**, which Step 7 binds into the Plex CT as `/media`.

## 4. Verify media intact (migration acceptance gate)

This is the **acceptance gate** for the migration — do not proceed until it
passes.

```bash
zpool status <pool>     # the single vdev must be ONLINE, listed by its by-id path
zfs list                # datasets present with the expected mountpoints under /tank
```

Then **spot-check that the media is intact**: browse `/tank/Media`, confirm
expected directories, and compare file **counts** against the old server (and
checksums if you captured them in step 1). When `zpool status` is ONLINE and the
**raw data is intact**, the migration has succeeded.

## 5. Operational hardening (ZFS-on-USB caveats)

USB-attached ZFS has sharp edges. Apply these once the pool is imported:

```bash
zpool set autotrim=off <pool>     # keep TRIM OFF over USB
zpool scrub <pool>                # run now, and schedule periodically
```

- **`autotrim=off`** — many USB bridges mishandle UNMAP/discard, which has made
  pools temporarily unimportable. Leave autotrim **off** over USB; check
  `lsblk -D` before ever reconsidering.
- **Periodic `scrub`** — schedule `zpool scrub <pool>` regularly to catch bit
  rot early (detection only; RAID0 has no redundancy to repair from).
- **USB pool-suspend risk** — a USB controller reset or cable disconnect can
  fault a device and **suspend the whole pool**: all I/O hangs until you run
  `zpool clear <pool>` (or reboot). Budget for this; prefer a powered hub and a
  cable that won't get bumped.
- **Auto-import on reboot** is driven by `zfs-import-cache.service` + the
  cachefile set in step 3 — verify the pool re-imports after a test reboot.

## 6. Wire `/tank/Media` into the Plex CT (forward ref → Step 7)

The dataset must be **mounted on the host first** (its `mountpoint`, set in
step 3) before it can be bound into a container.

**Interim placeholder.** Before the real media is migrated, create an empty
host directory so Step 7's bind-mount mechanics can be validated end-to-end:

```bash
mkdir -p /tank/Media
```

Once the pool's `mountpoint=/tank` is set and its media dataset is mounted, the
**real `/tank/Media`** supersedes this empty placeholder (same path).

The Plex CT then binds it (Step 7 owns the implementation):

```
# /tank/Media on the host  ->  /media inside the CT (read-only: Plex only reads)
bind_mounts = [{ host_path = "/tank/Media", ct_path = "/media", read_only = true }]
```

- **Unprivileged ownership (Step 7's job).** Under an unprivileged CT, host IDs
  shift **+100000**, so files under `/media` appear as **`nobody:nogroup`**
  inside the container. Step 7 fixes this by either `chown`-ing the host
  directory to the mapped uid/gid **or** mapping an `idmap` range back to the
  real host IDs. Flagged here so Step 7 has the context; do not attempt the fix
  in this runbook.
- **Bind mounts are not captured by `vzdump`** and do not support CT snapshots.
  That is acceptable — the media lives on ZFS and backups are a separate,
  out-of-scope task.

### idmap fallback: privileged container (`unprivileged = false`)

Step 7 (now implemented) punches host GIDs **993** (`render`) and **44**
(`video`) straight through the unprivileged CT's idmap (a gap-free tiling
generated from `local.host_gids`), so the container can open `/dev/dri` and
read `/media` while staying unprivileged. This is the default and preferred
path.

If, on a live `just apply`, the idmap fights GPU or DAS access — `vainfo`
cannot open `/dev/dri/renderD128`, `/media` still shows `nobody:nogroup`, or the
CT refuses to start because the provider could not apply the create-time idmap
(needs **bpg ≥ 0.108.0** + provider `ssh { agent = true }`) — fall back to a
**privileged** container:

1. Re-check the host GIDs match the tiling: `getent group render video` on `pve`
   (expected `render:x:993`, `video:x:44`). If they differ, fix
   `local.host_gids` in `tofu/locals.tf` and re-apply — the tiling regenerates.
2. **Check the `/etc/subgid` delegations first** — if the CT won't start with
   `newgidmap: gid range [44-45) -> [44-45) not allowed` (or `[993-994)`), the
   punch GIDs are not delegated to `root` in `/etc/subgid`. This is the host-side
   prereq (`root:44:1` + `root:993:1`, uid side needs nothing) documented in
   **`host-bootstrap.md` § "Delegate the Plex CT punch GIDs in /etc/subgid"** —
   add those lines on `pve` *before* reaching for the privileged escape hatch.
3. If the idmap still misbehaves, flip the switch in `tofu/main.tf`:

   ```hcl
   module "plex" {
     # ...
     unprivileged = false   # fallback: privileged CT, no idmap needed
   }
   ```

   A privileged CT maps IDs 1:1 by default, so the `gid_maps`/`uid_maps` tiling
   becomes a no-op and `/dev/dri` + `/media` are reachable without punches.
4. `just apply` to recreate the CT, then re-verify `/dev/dri` access and
   `/media` ownership inside the container.

Privileged is the escape hatch, not the goal — prefer the unprivileged idmap and
only flip if it cannot be made to work.
