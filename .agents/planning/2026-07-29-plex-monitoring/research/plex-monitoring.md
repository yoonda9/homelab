# Plex Application Monitoring

## What Already Exists
There is currently **no Plex-specific exporter** in the monitoring stack. Plex (CT 110, `192.168.1.110`) runs as a native service inside an unprivileged Debian 13 LXC container on the Proxmox host. Traefik routes to it via the file-provider service at `http://192.168.1.110:32400` (see `docker_host_plex_url` in `ansible/roles/docker_host/defaults/main.yml`).

## What Needs to Be Added
A Prometheus exporter that can pull stream-level metrics from Plex's API.

## Popular Exporters

### 1. plex-media-server-exporter (axsuul)
- **Focus:** Highly granular detail. Differentiates between playing, paused, and buffering states. Tracks audio vs. video transcoding and media downloads.
- **Best for:** Troubleshooting buffering issues, diagnosing transcoder load, and seeing in-depth stream quality.
- **Source:** [GitHub - axsuul/plex-media-server-exporter](https://github.com/axsuul/plex-media-server-exporter)

### 2. prometheus-plex-exporter (jsclayton)
- **Focus:** General metrics, library playback status, storage usage.
- **Best for:** Straightforward setup to track high-level server health and basic playback activity.
- **Source:** [GitHub - jsclayton/prometheus-plex-exporter](https://github.com/jsclayton/prometheus-plex-exporter)

### 3. plex_exporter (arnarg)
- **Focus:** Lightweight alternative for core Plex metrics (session counts, library size).
- **Best for:** Minimalists who only need key indicators.
- **Source:** [GitHub - arnarg/plex_exporter](https://github.com/arnarg/plex_exporter)

## Deployment Recommendation
The exporter should be added as a new service in the existing Docker Compose stack on CT 111 (`docker-host`, `192.168.1.111`). This is where Prometheus, Grafana, node_exporter, and cAdvisor already run. The exporter will reach Plex over the LAN at `192.168.1.110:32400` — the same cross-LXC path Traefik already uses.

## Key Findings
- All exporters require a **Plex Authentication Token** (retrieved via the Plex web app XML method).
- `axsuul`'s exporter is the strongest candidate for diagnosing sporadic connection issues due to its buffering-state granularity, but its maintenance status and compatibility with LXC-hosted Plex (as opposed to Docker-hosted Plex) should be verified before committing.
- The exporter does not need to run on the same host as Plex — it only needs API access.
