# Home Lab Auto Deploy

This project is dedicated to the automated provisioning and management of a personal homelab environment, primarily focused on Proxmox VE and a suite of core services.

## Project Overview

The objective is to create a reproducible and automated deployment pipeline for infrastructure and applications. The project aims to handle everything from base OS provisioning on Proxmox to the configuration of media servers, monitoring tools, and network services.

### Core Technologies (Planned)
*   **Hypervisor:** Proxmox VE
*   **Automation/IaC:** (Likely Ansible, Terraform, or OpenTofu - *To be confirmed as implementation begins*)
*   **Containerization:** (Likely Docker/Podman for services - *To be confirmed*)

## Key Services (Planned)

The following services are targeted for automated deployment:

*   **Networking:**
    *   Reverse Proxy (for secure external/internal access)
    *   Pi-hole (for network-wide ad blocking and DNS)
*   **Media:**
    *   Plex Media Server
    *   Calibre (e-book management)
*   **Monitoring & Metrics:**
    *   Grafana (dashboards and visualization)
    *   (Likely Prometheus or InfluxDB as a backend - *To be confirmed*)
*   **Security & Utilities:**
    *   Bitwarden (password management)

## Building and Running

*   **Status:** Initial setup phase. No automation scripts or configuration files have been implemented yet.
*   **TODO:** Define the preferred automation tool (e.g., Ansible, Terraform) and create the initial directory structure for configurations.

## Development Conventions

As this project is in its infancy, no specific conventions have been established. Future development should aim for:
*   **Declarative Infrastructure:** Preferring configuration over manual steps.
*   **Version Control:** All configurations and scripts should be tracked in this repository.
*   **Documentation:** Keeping the `README.md` and `GEMINI.md` updated as the project evolves.
