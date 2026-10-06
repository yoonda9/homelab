# Idea Honing

**Context from User:**
- The server is already port forwarding 32400 for a direct connection.
- A major problem is that the library itself takes time to load when first starting the app.
- Performance problems are not limited to playback (e.g., metadata/UI loading is slow).

**Question 1:**
Given that port 32400 is already forwarded, and the slowness is primarily when loading the library/app initially, it sounds like metadata and API requests might be the bottleneck. Is your Plex app data (specifically the database and metadata folders) stored on a solid-state drive (SSD, NVMe) or a mechanical hard disk drive (HDD)?

**Answer 1:**
It's stored directly in an LXC container as a mounted disk. Everything is backed by an SSD/NVMe drive.

**Question 2:**
Since the database is running on fast SSD/NVMe storage, I/O bottlenecks are less likely. Another common cause for a slow-loading library (metadata and UI) is the routing of the API traffic itself. Are you accessing the Plex web app/library via a custom domain (e.g., `plex.yourdomain.com`) that is proxied through Cloudflare (orange cloud), or are you connecting directly via the IP address or a non-proxied domain?

**Answer 2:**
Accessing via plex.yoonnation.com but it's not proxied (i.e., DNS-only gray cloud).

**Question 3:**
Since your domain is DNS-only, we can rule out Cloudflare proxy overhead. When you access `plex.yoonnation.com` to load the interface, does that web/API traffic route through Traefik (e.g., via port 443) before reaching Plex, or does it bypass Traefik entirely?

**Answer 3:**
That should be routed via Traefik.

**Question 4:**
Since we've narrowed it down to the Traefik routing (which might have heavy middleware or buffering affecting the API requests), I will investigate the Traefik configuration in your codebase. Do you feel this covers the main requirements for the optimization project, or are there any other performance issues or edge cases (e.g., specific devices, local vs remote, specific file types) you'd like to add before we finalize the requirements?

**Answer 4:**
This is fine, proceed.
