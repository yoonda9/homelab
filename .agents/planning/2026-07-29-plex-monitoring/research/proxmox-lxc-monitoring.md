# Proxmox PVE and LXC Container Monitoring

## What Already Exists
There is currently **no Proxmox-level exporter** in the monitoring stack. The existing `node_exporter` in the Docker Compose stack on CT 111 monitors the docker-host container itself, but it does not provide metrics for the Proxmox PVE hypervisor node or for the Plex LXC container (CT 110).

### Topology (from `tofu/locals.tf` and `tofu/main.tf`)
- **PVE host `pve`** — bare-metal Proxmox hypervisor
  - **CT 110 `plex`** — unprivileged Debian 13 LXC, `192.168.1.110/24`, 6 cores, 4 GB RAM, Intel iGPU passthrough, ZFS bind mounts for media and transcode ramdisk
  - **CT 111 `docker-host`** — unprivileged Debian 13 LXC, `192.168.1.111/24`, runs Docker (nesting + keyctl enabled), hosts all reverse proxy and monitoring services

## What Needs to Be Added
`prometheus-pve-exporter` — the standard Prometheus exporter for Proxmox VE environments.

## Prometheus PVE Exporter

- **Function:** Interacts with the Proxmox VE API to collect performance data for nodes, VMs, and LXC containers.
- **LXC Metrics Include:**
  - CPU usage ratio and limits (`pve_cpu_usage_ratio`, `pve_cpu_usage_limit`)
  - Memory used and total (`pve_memory_usage_bytes`, `pve_memory_size_bytes`)
  - Root image disk usage (`pve_disk_usage_bytes`)
  - Network I/O (`pve_network_transmit_bytes`, `pve_network_receive_bytes`)
  - Disk I/O (`pve_disk_read_bytes`, `pve_disk_write_bytes`)
  - Uptime and status (`pve_up`, `pve_uptime_seconds`)
- **Source:** [GitHub - prometheus-pve/prometheus-pve-exporter](https://github.com/prometheus-pve/prometheus-pve-exporter)
- **Default port:** 9221

## Deployment Recommendation
Add to the existing Docker Compose stack on CT 111. The exporter needs to reach the Proxmox API on the PVE host — the PVE host IP (typically `192.168.1.x`, reachable from CT 111's `192.168.1.111` on the same `vmbr0` bridge) will be used as the target.

## Implementation Steps
1. **API User:** Create a `prometheus` user in Proxmox Web UI (Datacenter > Permissions > Users). Assign the **PVEAuditor** role at the `/` level. Generate an API Token.
2. **Secrets:** Store the API token in the Ansible Vault (`ansible/group_vars/all/vault.yml`) alongside the existing Cloudflare and Grafana secrets, and pass it to the container via the `.env` file (following the pattern in `env.j2`).
3. **Compose service:** Add a `pve-exporter` service to `compose.yml.j2` — scrape-only, no Traefik labels, like the existing `node-exporter` and `cadvisor` services.
4. **Prometheus config:** Add a `pve-exporter` scrape job to `prometheus.yml.j2`.
5. **Important Warning:** Do not use the `--collector.config` flag unless strictly necessary, as it triggers an individual API call for every guest and can overload the Proxmox API.

## Limitations
`prometheus-pve-exporter` provides aggregate container-level metrics from the Proxmox API, but does **not** provide:
- Per-process metrics inside the container (e.g., Plex transcoder CPU usage)
- Filesystem-level I/O detail (e.g., ZFS bind mount latency)
- TCP socket statistics (`node_sockstat_TCP_tw`, `node_netstat_Tcp_RetransSegs`)

If deeper visibility inside the Plex LXC is needed, a separate `node_exporter` would need to be installed directly inside CT 110.

## References
- [Prometheus PVE Exporter GitHub](https://github.com/prometheus-pve/prometheus-pve-exporter)
- Grafana Dashboard ID for Proxmox: `10347`
