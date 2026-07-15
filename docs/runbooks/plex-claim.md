# Runbook: Plex claim + public access URL (`plex.yoonnation.com`)

This runbook covers the **manual** Plex Media Server steps that Ansible cannot
automate: claiming the server to a Plex account (the claim token is short-lived
and account-bound) and setting the **Custom server access URLs** so the public
Traefik router at `plex.yoonnation.com` works. Run it once, after the `plex`
role has applied to CT 110 and the `vainfo`→`iHD` acceptance gate has passed.

Everything here is **outside the automation "done" scope** (design §4.3): the
`plex` role installs and configures the server and proves QSV is ready, but the
account claim and the externally-advertised URL are owner-account actions.

They are also **one-time** actions: the Plex state directory is bind-mounted
from host storage (§5), so a CT rebuild comes back already claimed — sections
2–3 should never need re-running once §5 is in place.

---

## 1. Prerequisites

- The `plex` role applied cleanly to CT 110, including the post-install
  `vainfo --display drm --device /dev/dri/renderD128` gate reporting **`iHD`**
  (else hardware transcoding is not ready — fix that first).
- A **Plex account** with **Plex Pass** (required for hardware transcoding).
- LAN access to the CT at `http://192.168.1.110:32400/web`.

---

## 2. Claim the server (web wizard, token TTL ~4 min)

The claim token expires roughly **4 minutes** after it is issued and cannot be
scripted into the role, so claim interactively:

1. From a browser **on the LAN**, open `http://192.168.1.110:32400/web`.
2. Sign in with the Plex account that should own the server.
3. Complete the setup wizard. This binds the server to the account; the wizard
   exchanges a fresh claim token behind the scenes (you do not copy it manually
   in the normal flow).

> If the wizard reports the server is **unclaimed** or the token expired, reload
> `:32400/web` to issue a new token and retry — the ~4 min TTL is the usual cause
> (design §6, "Plex claim token expired").

---

## 3. Set the public access URL

Plex must advertise the public hostname so remote clients reach it through the
Traefik public router (`plex.yoonnation.com` → `http://192.168.1.110:32400`,
design §4.4):

1. In Plex: **Settings → Server → Network**.
2. Under **Custom server access URLs**, enter:

   ```
   https://plex.yoonnation.com:443
   ```

3. Save. Leave **Remote Access** otherwise on Plex's defaults; the inbound path
   is terminated by Traefik (TLS) and forwarded to `:32400`.

---

## 4. Verify

- **Hardware transcode:** force a transcode (e.g. play a file at a lower quality
  from a remote client) and confirm the Plex **Dashboard** shows
  **"Transcode (hw)"** on the active session.
- **Public reachability:** from off-LAN, `curl -I https://plex.yoonnation.com`
  returns `200`/`401` with a valid Let's Encrypt certificate (not the self-signed
  interim cert).

---

## 5. State persistence across CT rebuilds

Everything that makes this server *itself* — `Preferences.xml` (which stores the
post-claim `PlexOnlineToken` and machine identity), the library database, and
all metadata — lives under `/var/lib/plexmediaserver/` in CT 110. That path is
bind-mounted from host storage by `module "plex"` in `tofu/main.tf`:

| host (`pve`)                | CT 110                     | mode       |
| --------------------------- | -------------------------- | ---------- |
| `/tank/Server/AppData/plex` | `/var/lib/plexmediaserver` | read-write |

The host path is a plain subdirectory of the **`DASPool/Server/AppData`**
dataset (`DASPool` mounts at `/tank`), so Plex state rides that dataset's ZFS
snapshots. Note that Proxmox **vzdump excludes bind mounts** from CT backups —
the pool *is* the backup story for this data.

With the mount in place, a CT **rebuild** (destroy/recreate — e.g. flipping
`unprivileged` per the design §6 fallback, a template bump, or a `vm_id`
change) comes back claimed with libraries intact: tofu recreates the CT with
the mount, the `plex` role reinstalls the package (dpkg does not clobber the
existing state directory), and Plex reads the persisted `Preferences.xml`.

**Adding a bind mount is also a rebuild** on the pinned provider: observed
live on bpg v0.110.0, a new `mount_point` entry flags its `volume` with
`# forces replacement` in the plan, destroying and recreating the CT (a
regression tracked in bpg/terraform-provider-proxmox#2507; the v0.94.0 fix
covered cloned CTs, not template-created ones like this). Before any
`just apply` that touches `module.plex`, read the plan: `~ update in-place`
keeps the rootfs; `-/+ destroy and then create replacement` is a rebuild — it
destroys the rootfs, leans entirely on this mount for Plex state, and leaves a
bare template CT, so run the cutover checks below first and re-run the `plex`
role (`just config`) afterwards.

### Ownership (unprivileged idmap)

CT 110's uid map is a single `+100000` offset tile with no uid punches
(`tofu/locals.tf`), and the in-CT `plex` user/group are created by the
`plexmediaserver` package with **package-allocated** IDs. The host directory
must be owned by the *mapped* IDs:

The uid and the gid are allocated **independently and are frequently not
equal** (CT 110 currently holds `uid=999(plex) gid=991(plex)`), so read them
separately and never reuse one for the other:

```bash
# On pve — read the IDs as allocated inside the CT, uid and gid separately:
plex_uid=$(pct exec 110 -- id -u plex)   # e.g. 999
plex_gid=$(pct exec 110 -- id -g plex)   # e.g. 991 — NOT necessarily == uid

# Then own the state dir as those IDs +100000. Target the BASE directory, not
# just Library/: the base itself must be mapped, and `-R` covers both.
chown -R $((100000 + plex_uid)):$((100000 + plex_gid)) /tank/Server/AppData/plex
```

This must run **on the host**. Once a file carries an unmapped owner it shows
up in the CT as `65534:65534` (`nobody`), and *in-CT `root` cannot chown it
back* — `CAP_DAC_OVERRIDE`/`CAP_CHOWN` do not apply to IDs outside the userns
map. A host-side `chown` is the only repair.

The classic failure is a state-dir copy that preserved **raw in-CT ownership**
— e.g. a tar unpacked on the host, or an `rsync` from inside the CT. Those
land `999:991` on the host, which is outside CT 110's mapped range
`[100000, 165536)`, so the whole tree surfaces as `nobody`, `plex` is left with
only `other` `r-x` on mode `0755`, and PMS aborts within milliseconds:

```
PMS: failure detected. Read/write access is required for path:
/var/lib/plexmediaserver/Library/Application Support/Plex Media Server
```

The `plex` role pins the uid/gid ahead of the package install and asserts this
ownership before starting the service, so a `just play` now fails loudly with
the exact `chown` to run instead of leaving PMS crash-looping.

### Cutover order (first-time enablement)

The bind mount **shadows** whatever the CT rootfs holds at
`/var/lib/plexmediaserver`, so the host copy must be current *before* the
mount lands:

1. Stop Plex so the database is quiescent:
   `pct exec 110 -- systemctl stop plexmediaserver`.
2. If the copy at `/tank/Server/AppData/plex` is stale, re-sync it from the CT
   rootfs. With the CT stopped, `pct mount 110` exposes the rootfs at
   `/var/lib/lxc/110/rootfs`; `rsync -a` from
   `.../rootfs/var/lib/plexmediaserver/` preserves the already-shifted
   host-side ownership, then `pct unmount 110`.
3. Fix ownership as above (skip if step 2's `rsync -a` carried it over).
4. `just apply` — the CT restarts with the mount. Verify:
   `pct exec 110 -- findmnt /var/lib/plexmediaserver`.
5. Start Plex (`pct exec 110 -- systemctl start plexmediaserver`) and confirm
   `http://192.168.1.110:32400/web` shows the claimed server (no setup wizard)
   with libraries intact.

---

No secrets belong in this repo: the Plex account credentials and any claim token
stay in the browser session only. `Preferences.xml` on the host dataset DOES
hold the server's Plex token — it is outside the repo, but treat
`/tank/Server/AppData/plex` as sensitive.
