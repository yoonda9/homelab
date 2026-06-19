# Runbook: Plex claim + public access URL (`plex.yoonnation.com`)

This runbook covers the **manual** Plex Media Server steps that Ansible cannot
automate: claiming the server to a Plex account (the claim token is short-lived
and account-bound) and setting the **Custom server access URLs** so the public
Traefik router at `plex.yoonnation.com` works. Run it once, after the `plex`
role has applied to CT 110 and the `vainfo`→`iHD` acceptance gate has passed.

Everything here is **outside the automation "done" scope** (design §4.3): the
`plex` role installs and configures the server and proves QSV is ready, but the
account claim and the externally-advertised URL are owner-account actions.

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

No secrets belong in this repo: the Plex account credentials and any claim token
stay in the browser session only.
