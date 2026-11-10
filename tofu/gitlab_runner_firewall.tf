# Proxmox firewall for the gitlab-runner VMs (design §4.10, plan Step 10c; gate 2506).
# Every resource here is gated on var.gitlab_runner_firewall_stage by count/for_each:
#   0 = nothing (rollback)   1 = each VM's ipset, options and rules (the default)
# pve's datacenter and node firewalls are NOT managed here. They were already on
# (cluster.fw enable: 1, policy_in DROP; host.fw enable: 1) before gate 2506, so these
# per-VM objects are live as soon as they exist. No resource may touch the datacenter
# or node firewall: the retired stage-2 singletons would have set the datacenter input
# policy to ACCEPT and turned pve's node firewall off.
# scripts/test_gitlab_runner_firewall_shape.py guards the gating, the key lines, and
# the absence of any pve-wide firewall resource.

locals {
  # Per-VM firewall objects exist from stage 1.
  gitlab_runner_fw_vms         = var.gitlab_runner_firewall_stage >= 1 ? local.gitlab_runners : {}
  gitlab_runner_docker_host_ip = split("/", local.net.docker_host_cidr)[0]
}

# ipfilter on a VM needs an explicit ipfilter-net0 set holding its address.
resource "proxmox_virtual_environment_firewall_ipset" "ipfilter" {
  for_each  = var.gitlab_runner_firewall_stage >= 1 ? local.gitlab_runners : {}
  node_name = each.value.node
  vm_id     = each.value.vm_id
  name      = "ipfilter-net0"

  cidr {
    name = split("/", each.value.ip_cidr)[0]
  }

  depends_on = [module.gitlab_runner]
}

resource "proxmox_virtual_environment_firewall_options" "vm" {
  for_each      = var.gitlab_runner_firewall_stage >= 1 ? local.gitlab_runners : {}
  node_name     = each.value.node
  vm_id         = each.value.vm_id
  enabled       = true
  input_policy  = "DROP"
  output_policy = "ACCEPT"
  macfilter     = true
  ipfilter      = true
  radv          = false
  dhcp          = false
  ndp           = false

  depends_on = [proxmox_virtual_environment_firewall_ipset.ipfilter]
}

resource "proxmox_virtual_environment_firewall_rules" "vm" {
  for_each  = var.gitlab_runner_firewall_stage >= 1 ? local.gitlab_runners : {}
  node_name = each.value.node
  vm_id     = each.value.vm_id

  # Egress: DNS to the router first, then drop the LAN, tailnet, multicast, broadcast, IPv6.
  rule {
    type    = "out"
    action  = "ACCEPT"
    proto   = "udp"
    dest    = local.net.gateway
    dport   = "53"
    comment = "dns udp to router"
  }
  rule {
    type    = "out"
    action  = "ACCEPT"
    proto   = "tcp"
    dest    = local.net.gateway
    dport   = "53"
    comment = "dns tcp to router"
  }
  rule {
    type    = "out"
    action  = "DROP"
    dest    = "10.0.0.0/8"
    comment = "rfc1918"
  }
  rule {
    type    = "out"
    action  = "DROP"
    dest    = "172.16.0.0/12"
    comment = "rfc1918"
  }
  rule {
    type    = "out"
    action  = "DROP"
    dest    = "192.168.0.0/16"
    comment = "rfc1918"
  }
  rule {
    type    = "out"
    action  = "DROP"
    dest    = "100.64.0.0/10"
    comment = "tailnet cgnat"
  }
  rule {
    type    = "out"
    action  = "DROP"
    dest    = "224.0.0.0/4"
    comment = "multicast"
  }
  rule {
    type    = "out"
    action  = "DROP"
    dest    = "255.255.255.255"
    comment = "broadcast"
  }
  rule {
    type    = "out"
    action  = "DROP"
    dest    = "::/0"
    comment = "all ipv6"
  }

  # Ingress: SSH from the LAN; node-exporter and runner metrics from Prometheus only.
  rule {
    type    = "in"
    action  = "ACCEPT"
    proto   = "tcp"
    source  = "192.168.1.0/24"
    dport   = "22"
    comment = "ssh from lan"
  }
  rule {
    type    = "in"
    action  = "ACCEPT"
    proto   = "tcp"
    source  = local.gitlab_runner_docker_host_ip
    dport   = "9100,9252"
    comment = "prometheus scrape"
  }

  depends_on = [proxmox_virtual_environment_firewall_options.vm]
}
