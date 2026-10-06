# Traefik and Docker-Host Monitoring

## What Already Exists

The docker-host LXC (CT 111, `192.168.1.111`) already has a comprehensive monitoring foundation. The following are **already deployed and scraping**:

| Component | Status | Config Location |
|---|---|---|
| **Traefik Prometheus metrics** | ✅ Enabled on `:8082` (internal `metrics` entrypoint) with `addEntryPointsLabels` and `addServicesLabels` | `traefik.yml.j2` lines 59–64 |
| **Prometheus scraping Traefik** | ✅ `job_name: traefik`, target `traefik:8082` | `prometheus.yml.j2` lines 26–29 |
| **node_exporter** | ✅ Running as a Docker container with `--path.rootfs=/host` and `pid: host` | `compose.yml.j2` lines 177–184 |
| **Prometheus scraping node_exporter** | ✅ `job_name: node-exporter`, target `node-exporter:9100` | `prometheus.yml.j2` lines 16–19 |
| **cAdvisor** | ✅ Running as a privileged Docker container with device, sys, and Docker socket mounts | `compose.yml.j2` lines 186–197 |
| **Prometheus scraping cAdvisor** | ✅ `job_name: cadvisor`, target `cadvisor:8080` | `prometheus.yml.j2` lines 21–24 |

### Topology Clarification
Traefik does **not** run in a standalone VM. It runs as a Docker container inside CT 111, an unprivileged Debian 13 LXC container with nesting and keyctl enabled. `node_exporter` runs as a sibling Docker container in the same Compose stack, not as a system service. Because it mounts the host rootfs at `/host` with `pid: host`, it reports the LXC container's metrics (not the PVE host's).

## What Needs to Change

### 1. Add histogram `buckets` to Traefik metrics config
The existing Traefik metrics configuration does **not** define custom histogram buckets. Without explicit buckets, Traefik uses Go's default histogram boundaries, which may not align with meaningful latency thresholds for Plex streaming.

**Current config** (`traefik.yml.j2`):
```yaml
metrics:
  prometheus:
    entryPoint: metrics
    addEntryPointsLabels: true
    addServicesLabels: true
```

**Proposed change** — add `buckets`:
```yaml
metrics:
  prometheus:
    entryPoint: metrics
    addEntryPointsLabels: true
    addServicesLabels: true
    buckets:
      - 0.1
      - 0.3
      - 1.2
      - 5.0
```

This is the **only** change needed to Traefik's configuration.

### 2. Consider enabling Traefik access logs
The current `traefik.yml.j2` has no `accessLog` block. Enabling access logging would provide per-request detail (status codes, response times, client IPs) that is invaluable for diagnosing individual sporadic failures — something aggregate Prometheus counters cannot do.

## Key Metrics Already Available
Since Traefik metrics and node_exporter are already scraping, the following are queryable in Prometheus **right now**:

- `traefik_entrypoint_requests_total` — request counts by entrypoint and HTTP status code
- `traefik_entrypoint_request_duration_seconds` — latency (default histogram buckets)
- `traefik_service_requests_total` — per-service request counts (including the `plex@file` service)
- `node_network_transmit_bytes_total` / `node_network_receive_bytes_total` — network I/O for CT 111
- `node_filefd_allocated` — open file descriptors
- Container-level CPU/memory/network via cAdvisor

## References
- [Traefik Metrics Documentation](https://doc.traefik.io/traefik/observability/metrics/prometheus/)
