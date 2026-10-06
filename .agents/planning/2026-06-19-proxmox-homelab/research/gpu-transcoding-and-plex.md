# Research: Plex + Intel QSV transcoding + Plex setup

_Sources: Jellyfin/Debian HW-accel docs, Plex support, Proxmox forum/community-scripts
(verified 2026-06-19). Host iGPU = Intel UHD 770 (Alder Lake-S GT1 [8086:4680])._

## Privileged vs unprivileged LXC
- **Unprivileged is the current recommended default**; QSV transcoding works fine in an
  unprivileged LXC (GPU passthrough is not the blocker). Choose privileged only if you need
  in-container kernel **NFS client** mounts (we don't — DAS is a host ZFS bind-mount).
- **PVE 9 / AppArmor 4.1 quirk:** `intel_gpu_top` *monitoring* fails inside unprivileged LXCs
  (`Failed to initialize PMU! Permission denied`) — **transcoding still works**; run
  `intel_gpu_top` on the **host**. Avoid `lxc.apparmor.profile: unconfined`.

## Device access (ground truth for this host)
- `/dev/dri` major **226**; `renderD128` = `226:128`; `card1` = `226:1` (this host uses
  `card1`, not `card0` — observed).
- **Host GIDs OBSERVED on `pve`: `render`=993, `video`=44.** (General guides assume render=104;
  not true here — always verify with `getent group render video` and `ls -n /dev/dri/*`.)
- Preferred exposure = Proxmox **`dev0`/`dev1` device passthrough** (what bpg
  `device_passthrough` emits), which auto-handles host↔container GID translation. `gid=` is the
  **container-side** group; ensure the `plex` user is a member of render+video groups inside.

## Drivers inside the container (Gen12 → iHD, NOT i965)
UHD 770 needs the **`iHD`** driver from **`intel-media-va-driver-non-free`** (the `-non-free`
build has full **encode** support that transcoding requires). Enable Debian `non-free` /
Ubuntu `multiverse`, then:
```
apt install -y intel-media-va-driver-non-free vainfo libva-drm2 intel-gpu-tools
# intel-opencl-icd ocl-icd-libopencl1   # only if OpenCL HDR tone-mapping wanted
```
Plex ships its own ffmpeg/iHD, so the OS package is mainly for `vainfo` verification — but
installing it is the reliable route. Set `LIBVA_DRIVER_NAME=iHD` only if autodetect picks wrong.

## Verification
```
ls -l /dev/dri                                     # renderD128 + correct group inside CT
vainfo --display drm --device /dev/dri/renderD128  # must report driver "iHD"
```
`VAEntrypointEncSlice`/`EncSliceLP` under H264/HEVC profiles = HW **encode** present.
In Plex: **Activity → Dashboard** shows **"Transcode (hw)"** when working.

## Plex install + claim + reverse-proxy URLs
- **Official APT repo** (`https://repo.plex.tv/deb public main`, key from
  `downloads.plex.tv/plex-keys/PlexSign.v2.key`) → `apt install plexmediaserver`.
  (community-scripts `ct/plex.sh` automates a full unprivileged + GPU LXC if we want a reference.)
- **Claim token** from https://plex.tv/claim (format `claim-…`, **~4 min TTL**). Simplest in a
  bare LXC: browse `http://<LXC-IP>:32400/web` and sign in to claim. (Ansible can template the
  claim into first-run, but token expiry makes the web wizard the pragmatic path.)
- **Custom server access URLs** (Settings → Network): include
  `https://plex.yoonnation.com:443` so clients use the Traefik hostname. Default port 32400/TCP.
- ⚠️ **Plex Pass is REQUIRED for hardware transcoding.** (Confirm the account has it.) Since
  2025-04-29 remote streaming of personal media also requires Plex Pass / Remote Watch Pass.

## Open design decisions fed by this research
- Confirm **Plex Pass** entitlement (hard requirement for the QSV "done" criterion).
- Decide how Ansible installs/verifies the iHD stack and runs a post-deploy `vainfo` check as
  an automated acceptance gate.
- Reverse-proxy specifics for Plex live in `traefik-and-exposure.md`.

## URLs
- Intel HW accel: https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/intel/
- Plex HW transcoding: https://support.plex.tv/articles/115002178853-using-hardware-accelerated-streaming/
- Plex remote access / custom URLs: https://support.plex.tv/articles/200289506-remote-access/
- community-scripts Plex: https://community-scripts.github.io/ProxmoxVE/scripts?id=plex
- PVE9 unprivileged QSV note: https://blog.ktz.me/proxmox-9-made-unprivileged-lxcs-pointless-for-quicksync-users/
