# Bootstrap Proxmox with core services

Objective is to build a robust Proxmox VE 9.1 core services host using Ansible.

## Phase 1: Environment & Connectivity

- **Task 1.1: Install Control Node Dependencies** – Install the `community.proxmox` Ansible collection and local Python requirements, including `proxmoxer` and `requests`[cite: 6, 35, 141].
- **Task 1.2: Configure API Authentication** – Generate and configure **Proxmox API Tokens** (ID and Secret) to replace root password authentication for all Ansible operations[cite: 7, 36, 142].

## Phase 2: Host Configuration (`pve_base`)

- **Task 2.1: Modernize Repositories** – Disable the default enterprise repository and enable the **no-subscription repository** using the modern **DEB822 format** (`.sources` files)[cite: 9, 37, 143].
- **Task 2.2: Suppress Subscription Nag** – Implement a task to remove the "No valid subscription" pop-up from the Proxmox Web UI[cite: 10, 38, 144].
- **Task 2.3: Install Stability Updates** – Ensure `intel-microcode` or `amd64-microcode` is installed and the system is fully patched[cite: 11, 39, 145].
- **Task 2.4: Firmware Management (`fwupd`)** – Install `fwupd`, refresh service metadata, and ensure all system firmware (BIOS, UEFI, and connected components) is up to date[cite: 146, 170].
- **Task 2.5: Hardened SSH Access** – Configure SSH to **disable root password logins** and strictly enforce the use of SSH keys[cite: 12, 40, 147].
- **Task 2.6: UI & SSH Security** – Install and configure `Fail2Ban` with specific jails for the Proxmox Web UI (port 8006) and SSH[cite: 13, 41, 148].
- **Task 2.7: Configure PVE Firewall** – Enable the datacenter-level firewall with a **"drop by default" policy**, permitting only specific management IPs[cite: 14, 42, 149].

## Phase 3: Hardware Optimization

- **Task 3.1: Tune ZFS Memory for DAS** – Since ZFS manages your DAS, set the **ARC limit** (10% of total RAM or 4–8GB) to prevent the kernel from using excessive system RAM to cache DAS data, which could otherwise starve your services[cite: 15, 16, 77, 174].
- **Task 3.2: Set CPU Governor** – Configure the CPU scaling governor to `performance` or `schedutil` to minimize latency for real-time services[cite: 17, 44, 151].

## Phase 4: Virtual Networking & Storage

- **Task 4.1: Bridge Configuration** – Verify and configure the standard `vmbr0` Linux bridge for primary LAN traffic[cite: 19, 45, 152].
- **Task 4.2: Implement SDN (Optional)** – Create **SDN "Zones" and "Vnets"** to isolate edge services like Traefik or Bitwarden on a dedicated DMZ network[cite: 20, 21, 153].
- **Task 4.3: Automate Image Sync** – Create tasks to download the latest Debian/Ubuntu LXC templates and essential ISOs for your Docker VMs[cite: 22, 47, 154].
- **Task 4.4: Automate Cloud Image Template Provisioning** – Instead of building from scratch, download vendor-supplied cloud images (e.g., Ubuntu `.qcow2`), import them into a VM shell with VirtIO/SCSI defaults, and convert them into **Proxmox Templates** for rapid cloning[cite: 102, 110, 179].

## Phase 5: Guest Provisioning (`pve_provision`)

- **Task 5.1: Deploy Plex (LXC)** – Provision an LXC container for Plex to ensure low overhead and easier **iGPU passthrough** for hardware transcoding[cite: 24, 26, 180].
- **Task 5.2: Deploy Pi-hole (LXC)** – Provision a lightweight LXC for network-wide DNS filtering[cite: 24, 27, 181].
- **Task 5.3: Deploy Traefik (VM)** – Provision a dedicated VM for Traefik to provide **high isolation** as your primary reverse proxy[cite: 24, 25, 182].
- **Task 5.4: Deploy Official Bitwarden (VM)** – Provision a VM for the **official Bitwarden On-Premise** installation—ensuring at least 4GB of RAM and Docker Compose are present—following the [official Linux on-premise guide](https://bitwarden.com/help/install-on-premise-linux/)[cite: 115, 134, 183].

## Phase 6: Expanded Maintenance & Monitoring

- **Task 6.1: Schedule Backups** – Automate `vzdump` backup jobs to run nightly, targeting an external NAS or Proxmox Backup Server[cite: 29, 53, 193].
- **Task 6.2: Deploy Prometheus & Proxmox Exporter** – Install Prometheus on the host and deploy the `proxmox-exporter` to translate PVE-specific API data into Prometheus-compatible metrics[cite: 194].
- **Task 6.3: Deploy Health Monitoring (Telegraf/Node Exporter)** – Install and configure **Telegraf** or **Node Exporter** on the host and guests to forward granular system metrics (CPU, RAM, Disk I/O) to your data store[cite: 30, 195].
- **Task 6.4: Deploy Loki & Promtail (Log Aggregation)** – Install Loki on the host to centralize logs from Traefik, Bitwarden, and the PVE system for real-time troubleshooting[cite: 196, 201].
- **Task 6.5: Deploy Uptime Kuma** – Provision a lightweight service to monitor the availability of your web services (Plex, Bitwarden, Pi-hole) through the Traefik proxy (notifications disabled)[cite: 197, 202].
- **Task 6.6: Deploy Grafana Visualization Service** – Install and configure **Grafana as a service directly on the Proxmox host**, creating unified dashboards that pull from Prometheus (metrics) and Loki (logs)[cite: 186, 198].
