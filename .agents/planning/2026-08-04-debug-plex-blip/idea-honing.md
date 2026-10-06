# Requirements Clarification

## Q1: Primary Deliverable for Tracking the Blips
**Question:** What is the primary deliverable or mechanism you envision for tracking down the root cause of these sporadic Plex blips?
**Answer:** Option 4 (A comprehensive combination: an automated diagnostic capture watchdog, a reproducible log analysis pipeline/tool, and enhanced observability & instrumentation).

## Q2: Runtime Environment & Integration Strategy
**Question:** Where should the active diagnostic watchdog and exploratory log analysis scripts be deployed and executed within your homelab architecture?
**Answer:** Option 1 (In-Container (LXC CT 110) Watchdog: Embed a lightweight, event-driven log monitoring script and diagnostic capture tool directly inside the unprivileged Plex LXC container, managed cleanly via systemd service overrides in the Ansible Plex role without touching the Proxmox host OS).

