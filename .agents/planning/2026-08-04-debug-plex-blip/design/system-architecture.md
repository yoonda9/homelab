# Design: System Architecture & Infrastructure Integration

## Overview & Architecture Goals
The primary architectural objective is to deploy a robust, zero-overhead diagnostic tracking suite and targeted remediation strategy for Plex Media Server without violating Proxmox VE hypervisor host isolation or introducing CPU/storage contention that could impair real-time hardware transcoding (Intel QSV). All monitoring and active watchdog services operate strictly within unprivileged container boundaries.

## High-Level Deployment Architecture

```mermaid
graph TD
    subgraph Host ["Proxmox VE Hypervisor (pve) - No Host Modifications"]
        HostState["Host State Directory (plex_state_host_path)"]
        HostMedia["ZFS Media Pool (/tank/Media)"]
        DRIDev["Intel GPU /dev/dri"]
    end
    
    subgraph CT110 ["Plex LXC Container (CT 110 - Unprivileged)"]
        PMS["Plex Media Server Service"]
        DB["SQLite DB (com.plexapp.plugins.library.db)"]
        Logs["Plex Log Directory (/var/lib/plexmediaserver/Library/.../Logs)"]
        
        subgraph WatchdogSuite ["Diagnostic Watchdog (Ansible Managed)"]
            Service["systemd Service (plex-blip-watchdog.service)"]
            Daemon["Watchdog Script (plex_blip_watchdog.py)"]
            Dump["Diagnostic JSONL Dumps (/tmp/plex-blip-diagnostics.jsonl)"]
        end
        
        PMS -->|Reads/Writes| DB
        PMS -->|Emits Warnings & Slow Queries| Logs
        Daemon -->|Passive Zero-Overhead Inotify Tail| Logs
        Daemon -->|Instant Lock Probe on Trigger: fuser / lsof| DB
        Daemon -->|Writes Structured Audit Snapshot| Dump
    end
    
    subgraph DockerHost ["Docker Host (Monitoring & Exporters)"]
        Prom["Prometheus TSDB"]
        PlexExp["plex-exporter (:9594)"]
        Prom -->|Scrapes Metrics| PlexExp
        PlexExp -->|Synchronous Media Scrapes (pre-remediation, every 300s)| PMS
    end
    
    HostState -->|Bind Mount (RW)| DB
    HostMedia -->|Bind Mount (RO): /media| PMS
    DRIDev -->|ID-Mapped GID 993/44| PMS

    style Host fill:#ffebee,stroke:#c62828
    style CT110 fill:#e3f2fd,stroke:#1565c0
    style DockerHost fill:#e8f5e9,stroke:#2e7d32
```

## Core Infrastructure Principles
1. **Hypervisor Isolation & Best-Practice Hygiene**:
   * No third-party daemons, packages, or background scripts are installed on the Proxmox host (`pve`).
   * All diagnostic capture tooling executes locally within **LXC CT 110** as user `plex` or container-local root, preserving upgrade compatibility and clean backup boundaries (`vzdump`).
2. **Infrastructure-as-Code (IaC) Integration**:
   * The diagnostic watchdog is provisioned and lifecycle-managed directly by the existing Ansible Plex role ([ansible/roles/plex/tasks/main.yml](file:///home/user/Work/homelab/ansible/roles/plex/tasks/main.yml)).
   * The Ansible role deploys the lightweight Python monitoring script and wires a resilient systemd service unit (`plex-blip-watchdog.service`) with auto-restart guarantees and resource limits.
3. **Zero-Overhead & Non-Intrusive Telemetry**:
   * To prevent adding storage contention or CPU jitter during active hardware transcoding, the watchdog avoids active polling loops or heavy database queries. It relies exclusively on passive asynchronous file system event tailing (`inotify` / event-driven log reading) and executes diagnostic snapshots only upon matching high-confidence lock contention or query stall regex patterns.
