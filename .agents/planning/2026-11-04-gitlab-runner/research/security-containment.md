# Research: containing a privileged-Docker GitLab runner on the homelab

Researched 2026-11-04 against repo base `3f69dcb`. Inputs: `../design/detailed-design.md` (R18/R19, Appendix D) and `repo-conventions.md`. Every claim is tagged:

- **[V]** verified: read in official docs or in upstream source, with the URL or file given.
- **[I]** inferred: my reasoning or memory of behaviour I did not re-read today. Measure before relying on it.

Nothing was changed outside this file. Source was fetched read-only from `gitlab.com/gitlab-org/gitlab-runner` `main` and `github.com/bpg/terraform-provider-proxmox` `main` (latest release **v0.120.0**, 2026-11-02 [V], <https://api.github.com/repos/bpg/terraform-provider-proxmox/releases/latest>).

## 0. The threat in one paragraph

With `privileged = true`, any job author (anyone with Developer on a project that uses the runner) is root on VM 120 [V] (<https://docs.gitlab.com/runner/security/>: "a user running a CI/CD job could gain full root access to the runner's host system"). In the design as written, root on VM 120 gets three things:

1. **Every `glrt-` token** in `/etc/gitlab-runner/config.toml`. This is the worst of the three, because it **persists past a re-image**: whoever holds the token can poll `POST /api/v4/jobs/request` from anywhere and receive future jobs of every project bound to that runner, with their CI variables and source, until the token is reset.
2. **The LAN.** In-VM nftables (R19) is advisory against root: `nft flush ruleset` removes it.
3. **The other jobs on the host:** cross-job read and tamper (§1.4).

The controls below map onto these three. The split manager (§1) removes 1. The PVE firewall (§2) or a VLAN (§3) removes 2. Nothing short of one VM per job removes 3; routine re-imaging (§4) bounds how long 3 can last.

---

## 1. Splitting the runner manager from the job host

### 1.1 Is a remote Docker daemon supported? Yes.

- **[V]** `[runners.docker]` has `host` ("Custom Docker endpoint. Default is `DOCKER_HOST` environment or `unix:///var/run/docker.sock`"), `tls_cert_path` ("A directory where `ca.pem`, `cert.pem` or `key.pem` are stored and used to make a secure TLS connection to Docker") and `tls_verify` ("Disabled by default"). Source: <https://docs.gitlab.com/runner/configuration/advanced-configuration/>.
- **[V]** In source these are `docker.Credentials{Host, CertPath (toml tls_cert_path), TLSVerify (toml tls_verify)}`, in `helpers/docker/credentials.go`. `newOfficialDockerClient` builds a moby client with `client.WithHost(c.Host)` and a transport configured from those credentials (`helpers/docker/official_docker_client.go`). This is the same client the docker executor uses for a local socket, so a remote TCP+TLS endpoint follows the same code path.
- **[V] Precedent.** The `docker+machine` executor works exactly this way: the manager drives remote dockerds over TCP+TLS. `helpers/docker/machine.go` exposes `Credentials(ctx, name) (Credentials, error)` per machine. The model is mature, not a corner case. That executor is now deprecated in favour of docker-autoscaler, which tunnels the Docker connection over the fleeting connector (SSH) instead of exposing TCP 2376. See `newDockerTunnel` / `environmentDialContext` in `executors/docker/docker.go`: "We tunnel the docker connection for remote environments."

Config shape:

```toml
[[runners]]
  executor = "docker"
  [runners.docker]
    host          = "tcp://192.168.1.120:2376"
    tls_verify    = true
    tls_cert_path = "/etc/gitlab-runner/docker-certs/gitlab-runner-pve"  # ca.pem cert.pem key.pem (client)
    privileged    = true
    volumes       = ["/certs/client", "/cache"]
```

[V] `host` is per-`[[runners]]`, so each runner block repeats it. A second job host is just another block with a different `host`.

### 1.2 What runs where with a remote daemon

| Concern | Where it happens | Evidence |
|---|---|---|
| Named volumes (`/certs/client`, `/cache`, builds) | **On the remote daemon.** The volume manager calls `m.client.VolumeCreate(...)` over the API (`executors/docker/internal/volumes/manager.go`, `createCacheVolume`). They behave exactly as they do locally: DinD-TLS sharing of `/certs/client` works unchanged. | [V] source |
| Host binds / `cache_dir` | Paths are interpreted on the **job host's** filesystem, not the manager's. Irrelevant here, since the design has no host binds (R11). | [V] `createHostBasedCacheVolume` appends a bind; [I] that the bind source is resolved by the remote daemon (it is a plain Docker bind) |
| Helper image | 1) `ImageInspect` on the remote daemon; 2) if absent, the **manager opens its local** prebuilt tarball (`gitlab-runner-helper-images` package; search paths include `../lib/gitlab-runner/helper-images`) and **streams it to the remote daemon** with `client.ImageLoad(ctx, file, true)` (or `ImageImportBlocking`); 3) only if that fails, it pulls from the registry. With `helper_image` set explicitly, it always pulls. So **the manager needs the `gitlab-runner-helper-images` package, and the job host does not need registry.gitlab.com** for the helper. | [V] `executors/docker/docker.go` `getHelperImage` / `getLocalHelperImage`; `executors/docker/internal/prebuilt/prebuilt.go` `imageLoad` (`os.Open(path)` → `client.ImageLoad`) |
| Helper arch/OS | Taken from the remote daemon's `docker info` (`info.OSType`, `info.Architecture`), not from the manager. | [V] `docker.go` ~L1508-1519 |
| Git clone, LFS, artifact and cache upload | Run **inside the helper container on the job host**, which talks to gitlab.com directly. The artifact uploader is invoked with `--token <Build.Token>`, i.e. the **per-job `CI_JOB_TOKEN`, not the `glrt-` token**. The local `/cache` is a volume on the job host (there is no S3 cache in this design). | [V] `shells/abstract.go` L1958-1962 (`artifacts-uploader --token info.Build.Token`) |
| Service health check | A `<service>-wait-for-service` container running `gitlab-runner-helper health-check`, created on the same (remote) daemon. The TCP probe runs job-host-local, and the manager waits on the container. | [V] `executors/docker/services.go` `runServiceHealthCheckContainer` |
| Build trace | The job container's attach stream goes from the job host to the manager over 2376, then from the manager to gitlab.com. | [V] (docker attach over the API) |
| Upkeep (prune timer, log caps, drain) | The prune timer and `daemon.json` stay on the **job host**. The drain (`SIGQUIT` on gitlab-runner) is on the **manager**. Upgrading `docker-ce` on the job host kills running jobs unless the **manager** is drained first, so the play becomes two-host (§1.6). | [I] from design §4.5 / R16 |

**Latency and performance [I]:** on one bridge, API round-trips are sub-millisecond (see memory: .60→.110 measured 0.046 ms of virtual bridge). The only bulk transfer over 2376 is the helper tarball when the image is missing. That is tens of MB over the LAN, and only after a prune or upgrade. Image pulls, git and artifacts all go job-host↔internet and are unaffected. I expect no measurable job-time cost.

**Known issues found:**
- **[V]** An old runner issue (11.1, 2018) had self-signed CA trouble with `tls_cert_path` combined with `tls_verify = false` (<https://gitlab.com/gitlab-org/gitlab-runner/issues/3477>). Use `tls_verify = true` with a `ca.pem` in the directory.
- **[V]** Docker refuses to start if listeners are set both in the systemd unit (`-H fd://`) and in `daemon.json` `hosts`: "causes a conflict that prevents Docker from starting" (<https://docs.docker.com/engine/daemon/remote-access/>). On Ubuntu the stock unit carries `-H fd://`, so you need a systemd drop-in that clears `ExecStart=` **or** a `hosts` entry in `daemon.json` plus a drop-in. geerlingguy.docker does not do this for you [I].
- **[V]** "Remote access without TLS is **not recommended**, and will require explicit opt-in in a future release" (same page). Use TLS only.

### 1.3 What root on the job host gets in the split model

| Asset | Single-VM design | Split (manager elsewhere) |
|---|---|---|
| `glrt-` tokens | **Yes** (config.toml) | **No.** They exist only on the manager. The job host never sees them; only `CI_JOB_TOKEN`s reach it [V §1.2] |
| Docker **client** cert/key (root on the job host's dockerd) | n/a | No. It lives on the manager |
| Docker **server** key (`server-key.pem` on the job host) | n/a | **Yes.** It lets an attacker impersonate *the daemon*, not the manager. Root on the job host already *is* the daemon, so this adds nothing unless the same server cert is reused on another host. Issue one per host, and rotate it on re-image |
| Docker **CA key** | n/a | Must **not** be on the job host [V docs.docker.com: "Guard these keys as you would a root password!"; with `tlsverify` the daemon "only allows connections from clients authenticated by a certificate signed by that CA", <https://docs.docker.com/engine/security/protect-access/>]. Keep it on the controller (vault) or on the manager. If it sits on the job host, a job can mint a client cert, which is harmless for that host but fatal if the CA is shared with another job host |
| Persistence after re-image | Yes, via the stolen token | **No.** Nothing on the job host outlives a re-image. A rebuilt job host is clean, and the manager just reconnects |
| Concurrent jobs' data | Yes | **Yes, unchanged** (§1.4) |
| LAN reach | Yes, unless §2/§3 | Yes, unless §2/§3. The job host must still reach gitlab.com and registries directly |

The manager remains a target. A compromised daemon returns API responses that the manager's moby client parses, and build logs flow through the manager. That attack surface is small compared with "is root" [I].

### 1.4 Cross-job exposure on a shared daemon (any model with more than one job per host)

- **[V]** The executor passes job variables as **container environment**: `ContainerCreate` with `Env: jobVars.StringList()` (`executors/docker/docker.go` ~L1090), and services get `Env: e.Build.GetServiceVariables(...)` (~L766). Root on the host can run `docker inspect` on any concurrent job's container and read **all of its CI variables**: masked and protected ones (when the other pipeline is on a protected ref), deploy tokens, and that job's `CI_JOB_TOKEN`. It can also `docker exec` into the container, or read its builds volume (source) and `/certs/client`.
- **Integrity [V concept / I mechanics]:** with `pull_policy = if-not-present`, a job can re-tag a backdoored image as `node:24` (or `alpine:3.22`, the default image) on the shared daemon, and later jobs of *other projects* run it. GitLab says if-not-present "should be used only for specific runners used by trusted builds and users" (<https://docs.gitlab.com/runner/security/>). Cache volumes can be poisoned the same way.
- **Persistence on the host [I]:** a job can leave a detached privileged container or a systemd unit behind. The daily prune removes only *stopped* containers and unused images, so a running implant survives until re-image.
- **Mitigations short of one VM per job:**
  - only trusted projects (already in Appendix D);
  - `concurrent` limits the window but not the capability;
  - `pull_policy = always` for the default image closes the re-tag vector but costs pulls;
  - routine re-image (§4) bounds persistence.
- **The real boundary is one ephemeral VM per job.** The docker-autoscaler docs say "each job is given a secure ephemeral instance that cannot be affected by other jobs" and show `capacity_per_instance = 1`, `max_use_count = 1` (<https://docs.gitlab.com/runner/executors/docker_autoscaler/>). GitLab's own guidance is to run `--privileged` "only on isolated and ephemeral virtual machines" (<https://docs.gitlab.com/runner/security/>). That is the fleeting/Proxmox path, which R23 puts out of scope. The split-manager model is the static version of the same architecture (manager holds the token, instances run the jobs). Adopting it now makes a later move to autoscaler a config change, not a redesign [I].

### 1.5 Can the manager be an unprivileged LXC on `pve`? Yes, probably.

- **[V]** The manager needs no local dockerd. It only needs the API client and the helper tarballs (streamed from local files, §1.2). The autoscaler docs likewise put the Docker socket on the instances.
- **[I]** In an unprivileged CT it needs:
  - the `gitlab-runner` and `gitlab-runner-helper-images` debs;
  - outbound 443 to gitlab.com;
  - TCP to `jobvm:2376`;
  - `:9252` for metrics.

  It needs no `nesting`, no `keyctl` and no device passthrough. The existing `tofu/modules/lxc_service` fits (for example CT 112, .112). Ubuntu's `gitlab-runner` package installs a systemd unit that runs as root inside the CT, which in an unprivileged CT maps to host uid 100000.
- **[I] Risk:** an LXC shares `pve`'s kernel, but the manager runs no job code. The job code runs in VM 120. That is acceptable, and much better than the reverse (jobs in an LXC, which R5 already rejects).
- **Cost [I]:** one more inventory group and play (`gitlab_runner_manager`); config.toml moves there. The job-host role keeps Docker, the TLS listener, prune and firewall. You need a client/server cert pair per job host, plus a CA (generated on the controller by an Ansible `community.crypto` task or an openssl one-shot and stored in the vault).

  Guard tests must change: config shape (`host`/`tls_*`), and two plays instead of one. The drain becomes cross-host: stop the manager's runner, then upgrade docker on the job host. The design's single-VM drain (R16) becomes a `delegate_to` on the manager.

  Roughly **+1 plan step**, and moderate guard churn.

### 1.6 Split-model caveats
- [I] The second Proxmox node is standalone, so a manager CT on `pve` driving a job VM on node 2 crosses hosts over the LAN. That is fine on TCP 2376. One manager can drive both job hosts, or run one manager per node.
- [I] 2376 on the job host must be reachable **only** from the manager's IP (PVE firewall in-rule, §2). An in-VM rule alone is not enough, because root removes it. A job can reach its own host's 2376, but it is already root there.

---

## 2. Proxmox VE firewall for VM 120, managed by OpenTofu

### 2.1 Current state of the repo [V]
- `tofu/modules/dev_vm/main.tf` `network_device { bridge = var.bridge }` sets **no** `firewall`. bpg's default is `firewall = false` ("Whether this interface's firewall rules should be used (defaults to `false`)", <https://github.com/bpg/terraform-provider-proxmox/blob/main/docs/resources/virtual_environment_vm.md>). `lxc_service`'s `network_interface` likewise sets none.
- No `firewall` resource exists anywhere under `tofu/`, `ansible/` or `docs/` (grep, 2026-11-04). The datacenter firewall state on `pve` is **unknown from the repo**. It is an operator pre-check (§2.4 step 0).
- [V] The provider authenticates with a root@pam ticket (`tofu/providers.tf`), which has the rights to manage cluster, node and VM firewall objects.

### 2.2 How the PVE firewall layers work (and the lockout risk)
- **[V]** "The firewall is completely disabled by default", and cluster-wide `enable: 1` in `cluster.fw` is the master switch. Each NIC has "its own firewall enable flag", which is "required in addition to the general firewall enable option" (<https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html>). **So the VM firewall does nothing until the datacenter firewall is enabled**, the NIC has `firewall=1`, and the VM's own options have `enable: 1`. All three are needed.
- **[V] Lockout:** once the datacenter firewall is enabled with a DROP/REJECT input policy, "traffic to all hosts will be blocked by default". The exceptions are management hosts (the auto-detected `local_network`, or a `management` ipset) on 8006, 22, 5900-5999 and 3128, plus cluster traffic. The docs say: "Please open a SSH connection to one of your Proxmox VE hosts before enabling the firewall." (<https://pve.proxmox.com/wiki/Firewall>)
- **[V] bpg footgun:** `proxmox_virtual_environment_cluster_firewall.input_policy` **defaults to `DROP`** (<https://github.com/bpg/terraform-provider-proxmox/blob/main/docs/resources/virtual_environment_cluster_firewall.md>). Declaring the resource with just `enabled = true` turns on host DROP.
- **[I] Specific risk on this host:** `pve` runs Tailscale (`tailscale-split-dns.md`; `lxc_service` comments). Access to the PVE UI or SSH over a tailnet address (100.64.0.0/10) is **not** in the auto `local_network`, so it would be cut by a host DROP policy. Any non-LAN management path would be cut too. Guests are unaffected by the *host* policy ("host-level exceptions do not apply to guests" [V]). But guests whose NIC already has `firewall=1` and whose own options say `enable: 1` start being filtered the moment the datacenter switch flips.
- **[V]** The host-level `enable` (host.fw) defaults to 1 ("Enable host firewall rules"). bpg exposes it as `proxmox_node_firewall` (the old `proxmox_virtual_environment_node_firewall` is deprecated, "will be removed in v1.0") with `enabled` defaulting to `true`.
- **[V]** The nftables backend (`proxmox-firewall`) is "tech preview" and "not suited for production use". Stay on the default iptables `pve-firewall` (bpg `nftables = false`).

**Safe posture:** enable the datacenter firewall with **`input_policy = "ACCEPT"`** (so the host chain does not default-deny) **and** `proxmox_node_firewall { node_name = "pve", enabled = false }` (host rules not generated). Only VM 120's own policy is DROP. The datacenter switch then only "arms" per-guest firewalls. [I] that `host enable=0` with `cluster enable=1` still compiles guest chains; verify with `iptables-save | grep -c 'tap120i0\|veth'` and `pve-firewall compile` (read-only) after the switch.

### 2.3 Resources and rule set (sketch, not applied)

```hcl
# dev_vm: new optional var, default false, so existing behaviour is unchanged
network_device {
  bridge   = var.bridge
  firewall = var.firewall          # gitlab_runner passes true
}

# root: once per cluster (pve is a one-node cluster; node 2 is a separate cluster, so a second provider alias)
resource "proxmox_virtual_environment_cluster_firewall" "dc" {
  enabled        = true
  input_policy   = "ACCEPT"  # NEVER take bpg's DROP default: it governs pve's own input
  output_policy  = "ACCEPT"
  forward_policy = "ACCEPT"
  ebtables       = true
}
resource "proxmox_node_firewall" "pve" { node_name = "pve"  enabled = false }  # host rules off

resource "proxmox_virtual_environment_firewall_ipset" "runner_ipfilter" {
  for_each  = local.gitlab_runners
  node_name = each.value.node
  vm_id     = each.value.vm_id
  name      = "ipfilter-net0"
  cidr { name = split("/", each.value.ip_cidr)[0] }
}

resource "proxmox_virtual_environment_firewall_options" "runner" {
  for_each      = local.gitlab_runners
  node_name     = each.value.node
  vm_id         = each.value.vm_id
  enabled       = true
  input_policy  = "DROP"
  output_policy = "ACCEPT"
  macfilter     = true    # bpg default true
  ipfilter      = true    # needs the ipfilter-net0 set above for a VM (see 2.5)
  dhcp          = false   # static IP
  radv          = false   # bpg default is TRUE: a guest must not advertise as a router
  ndp           = true    # only if the LAN uses IPv6; see 2.5
}

resource "proxmox_virtual_environment_firewall_rules" "runner" {
  for_each  = local.gitlab_runners
  node_name = each.value.node
  vm_id     = each.value.vm_id
  # NOTE: one-line rule{} blocks below are shorthand; real HCL needs one attribute per line.
  # egress: order matters, first match wins
  rule { type = "out"  action = "ACCEPT"  dest = "192.168.1.1"  proto = "udp"  dport = "53"  comment = "DNS to gateway" }
  rule { type = "out"  action = "ACCEPT"  dest = "192.168.1.1"  proto = "tcp"  dport = "53" }
  rule { type = "out"  action = "DROP"    dest = "192.168.1.0/24"             comment = "no LAN" }
  rule { type = "out"  action = "DROP"    dest = "224.0.0.0/4"                comment = "no mDNS/SSDP to LAN" }
  rule { type = "out"  action = "DROP"    dest = "255.255.255.255" }
  # split model only: rule { type="out" ... } is unnecessary, manager->jobvm is inbound
  # ingress (policy DROP)
  rule { type = "in"  action = "ACCEPT"  source = "192.168.1.0/24"  proto = "tcp"  dport = "22" }
  rule { type = "in"  action = "ACCEPT"  source = "192.168.1.111"   proto = "tcp"  dport = "9100,9252" }
  # split model: rule { type="in" action="ACCEPT" source="<manager ip>" proto="tcp" dport="2376" }
  # plus macro Ping from LAN if wanted
}
```

Facts behind the sketch:
- [V] Rule syntax (`type` in/out/forward, `dest`/`source` lists, `dport` lists, `macro`, `iface`) and the warning "verify that no rules already exist for the target ... import them first" come from <https://github.com/bpg/terraform-provider-proxmox/blob/main/docs/resources/virtual_environment_firewall_rules.md>.
- [V] Option defaults (`macfilter` true, `radv` true, `ndp` false, `input_policy` DROP, `output_policy` ACCEPT) come from <https://github.com/bpg/terraform-provider-proxmox/blob/main/docs/resources/virtual_environment_firewall_options.md>.
- [I] The PVE VM chains accept `RELATED,ESTABLISHED` before user rules, so SSH and scrape replies to LAN sources are not hit by the out-DROP. Test this live (ssh from LAN after enablement).
- [I] All container traffic, including nested DinD, leaves VM 120 through `tap120i0` → `fwbr120i0`, so it is filtered by these rules. Unlike in-VM nftables, **root in the guest cannot change them**, because they live in `/etc/pve/firewall/120.fw` on the host.
- [I] The in-VM nftables (R19) should stay as defence-in-depth and as the accident guard. The PVE rules are the enforcement layer.

### 2.4 Safe enablement sequence (operator-gated)
0. **Pre-flight (read-only on pve):**
   - `pve-firewall status`
   - `cat /etc/pve/firewall/cluster.fw` (may be absent)
   - `ls /etc/pve/firewall/`
   - `cat /etc/pve/nodes/pve/host.fw`
   - `grep -l 'firewall=1' /etc/pve/qemu-server/*.conf /etc/pve/lxc/*.conf`. Every hit is a guest that starts being filtered by its own `.fw` once the datacenter switch flips. Expect none, since neither module sets it [I].

   If any `cluster.fw`/`host.fw`/`<id>.fw` rules exist, **import** them before declaring `_firewall_rules` (bpg warning above).
1. Open a root SSH session to pve **and** have the physical or iKVM console ready, as the docs advise. Recovery is `pve-firewall stop` or editing `cluster.fw` `enable: 0` from the console.
2. Apply A (VM-scoped, inert): the `dev_vm` `firewall = true` NIC flag, plus the VM ipset, options and rules. Nothing is enforced yet because the datacenter is off. `tofu plan` must show only VM-120 objects. [I] Changing the NIC flag on a running VM may need a stop/start for the `fwbr` to be inserted. Plan a reboot of 120 (the runner drained first).
3. Apply B (the switch): `proxmox_node_firewall pve enabled=false` **first**, then `cluster_firewall enabled=true input_policy=ACCEPT`. Use two separate `-target` applies, or `depends_on`, so the host-off lands before the cluster-on.
4. Verify immediately from the open SSH session:
   - the UI on 8006 still loads, from the LAN and from the tailnet;
   - `iptables-save | grep -c PVEFW` is non-zero;
   - CT 110/111 still serve (Plex, Traefik);
   - from inside VM 120: `curl https://gitlab.com` succeeds, while `nc -zv 192.168.1.111 443`, `192.168.1.50 8006` and `192.168.1.110 32400` time out;
   - from .111: a scrape of `.120:9100` succeeds; from another LAN host: SSH to .120 succeeds while `:9100` fails.
5. Negative control that shows the layer is root-proof: on VM 120 run `nft flush ruleset` (this kills Docker NAT; restore by restarting `docker` + `ci-egress`), then repeat the `.111` probe. It must still fail. This is the test that justifies the control; per memory, mutate the arm that must be false.

### 2.5 Can the guest bypass it?
- **MAC spoofing:** blocked by `macfilter` (bpg default true) [V option exists; I mechanism: the fwbr chain drops frames whose source MAC is not the NIC's].
- **IP spoofing and ARP impersonation** (for example, claiming .111 or .1 on the LAN): blocked by `ipfilter` with `ipfilter-net0` [V]: "any outgoing traffic with a source IP not matching its interface's corresponding ipfilter set will be dropped" (<https://pve.proxmox.com/wiki/Firewall>). [V bpg doc] "For containers the configured IP addresses will be implicitly added". The doc says this only for containers, so for a **VM** the set must list 192.168.1.120 explicitly [I]. An empty set on a VM would allow only the MAC-derived link-local address, i.e. cut all IPv4. [I] ARP filtering relies on `ebtables` (cluster option, keep true).
- **Router advertisements / rogue DHCP server:** `radv = false`. The DHCP *server* direction is blocked by default [V: VMs "cannot advertise themselves as routers unless radv: 1"; note that bpg's own default for `radv` is **true**, so set it explicitly].
- **IPv6 [I, important]:** the rules above are IPv4 only. If the LAN has IPv6 (SLAAC GUA/ULA, or just link-local `fe80::`), a root job can reach LAN hosts over v6 and bypass both this rule set and the design's nftables, which match `ip daddr` only. Measure with `ip -6 addr; ip -6 route` on VM 120 and `ip -6 neigh` on .111. If there is v6, either add `out DROP dest fe80::/10, fc00::/7` (plus the LAN GUA prefix) while keeping NDP, or turn IPv6 off in the guest **and** drop all v6 out at the PVE layer (`ndp = false`).
- **Hairpin through the router's public IP [I, important]:**
  - `host-bootstrap.md` §5 port-forwards 80/443 to .111. A job connecting to the WAN IP:443 is *not* in 192.168.1.0/24, so it passes, and the router hairpins it to Traefik.
  - Traefik's `internal-allowlist` admits `192.168.1.0/24` (`ansible/roles/docker_host/templates/dynamic.yml.j2`). The hairpinned source is either .120 or the router's .1, and **both are inside the allowlist**. A CI job can therefore likely reach the *internal* dashboards (Grafana, Prometheus, Traefik) the same way any LAN client can.
  - Measure from VM 120: `curl -sk --resolve grafana.yoonnation.com:443:<WAN IP> https://grafana.yoonnation.com/` and check Traefik's access log for the source IP.
  - Fixes: add an out-DROP for the WAN IP (it is dynamic, so this is fragile); or split the allowlist CIDRs so they exclude .120 (`192.168.1.0/26`, `.64/27`, `.96/28`, `.112/29`, `.121/32`... is clumsy, and fails if the router SNATs to .1); or a VLAN (§3), whose separate subnet is excluded naturally *if* the router keeps the source on hairpin.
  - This affects the in-VM nftables design equally.
- **The router itself:** DNS on .1 is allowed by design. The router's admin UI on .1 is blocked by the LAN drop, but [I] it may also answer on the WAN IP from inside. Same measurement.
- **Re-image window [I]:** bpg `started` defaults to true, so a re-created VM boots before tofu writes its `.fw`. At that point it runs only cloud-init (no runner, no jobs), so the window is benign. Keep the firewall resources `depends_on` the VM, and add `lifecycle { replace_triggered_by = [module.gitlab_runner[each.key]] }` so a `-replace` re-creates them. [I] `qm destroy` removes `/etc/pve/firewall/<vmid>.fw`, which otherwise shows up as drift on the next plan.

### 2.6 Effort in this repo
- About 4 resources × `for_each`, one `dev_vm` variable (a new shape test: the `firewall` var defaults to false), and a cluster singleton. The singleton is new territory: a test should pin `input_policy = "ACCEPT"` by cell identity so it can't regress to bpg's DROP default.
- One operator-gated apply in two parts, plus a runbook section (enable, verify, roll back).
- Estimate: **one plan step**, about half a day including guards. The risk is concentrated in the datacenter switch, and the sequence above defuses it.

---

## 3. VLAN isolation alternative

**What it takes:**
1. **Router [I]:** it must support 802.1Q sub-interfaces or VLAN networks, a DHCP/DNS scope or static gateway for the CI subnet (for example 192.168.20.0/24), NAT to the WAN, and **inter-VLAN firewall rules** (CI → LAN DROP, LAN → CI 22 allowed, .111 → CI 9100/9252 allowed). Without the inter-VLAN rules a VLAN isolates nothing, because routers route between their own subnets by default. The repo doesn't name the router model (`host-bootstrap.md` §5 calls it "the home router"), and many ISP/consumer routers can't do this. **This is the deciding unknown.**
2. **Switch:** if pve's uplink reaches the router through a switch, that switch must be managed and VLAN-capable, with the pve port and the router port trunking the CI VLAN. If pve is cabled directly to a VLAN-capable router port, no switch change is needed.
3. **pve network:** `vmbr0` becomes `bridge-vlan-aware yes` / `bridge-vids 2-4094` [V], <https://pve.proxmox.com/wiki/Network_Configuration>. This is applied with `ifreload -a`. The docs warn "a wrong network configuration may render a node inaccessible" [V]. That makes it a console-required change on the host that also carries Plex and Traefik. It is not in tofu today (bpg has a `network_linux_bridge` resource, but importing the live `vmbr0` is its own risk) [I].
4. **VM:** `network_device { vlan_id = 20 }` [V bpg `vlan_id`], plus a new static IP, gateway and DNS in the `gitlab_runners` map. Monitoring targets and the inventory change from .120.
5. [I] Side effect: on a VLAN-aware bridge, PVE gives untagged guest ports the whole `bridge-vids` range (trunk-like) unless `trunks` is limited. Existing CTs 110/111 could then send tagged frames into VLAN 20. This is not a risk to the runner, but it widens the host's L2 surface. The tagged runner port is an access port, so the guest cannot hop VLANs. Verify with `bridge vlan show`.

**Comparison:**
- A VLAN puts enforcement in the router, outside the PVE host entirely. Root in the VM and even PVE misconfiguration can't bypass it. It also fixes the Traefik allowlist naturally (a different source subnet) and handles v6 if the router scopes it.
- But it needs hardware and router work outside the repo, a risky host network edit, and re-addressing. The **PVE firewall gives the same root-proof property for the threat in scope** (a job inside VM 120) with repo-managed, testable, revertable code.
- Effort: VLAN takes days of operator work and is gated on router capability. The PVE firewall is one plan step.
- Recommendation: the PVE firewall now. Take a VLAN only if the router supports it *and* a second untrusted workload appears.

---

## 4. Re-image as a routine recovery and hygiene control

**Mechanics:**
1. Drain: `systemctl stop gitlab-runner` on the manager (split model) or on VM 120 (single). With the SIGQUIT drop-in this waits for jobs, up to 6000 s.
2. `tofu apply -replace='module.gitlab_runner["gitlab-runner-pve"].proxmox_virtual_environment_vm.dev_vm'` (gated). Firewall resources follow via `replace_triggered_by` (§2.5).
3. `ssh-keygen -R 192.168.1.120`, since the template seal removes host keys and every clone gets new ones [V `packer/ubuntu26.pkr.hcl` seal step]. Then `just play-runner` (twice for the `changed=0` check), then `just runner-smoke`.

**Token survival [V, `gitlab-runner-registration.md` §2]:**
- The `glrt-` token is unchanged.
- The new machine-id gives a new `s_` system_id, which appears as a new runner manager under the same runner; the old one goes stale and is GC'd after about 7 days.
- No GitLab action is needed.
- In the split model the job host holds no token at all, so a job-host re-image doesn't even touch GitLab state. Only the job host's Docker server cert is re-issued (tofu/Ansible, from the controller CA).

**Time estimate [I, unmeasured]:**

| Stage | Time |
|---|---|
| Drain | 0-90 min (wait for jobs) |
| Full clone + resize on local-lvm | ~1-3 min |
| Boot + cloud-init | ~1-2 min |
| First play (Docker CE + gitlab-runner + helper-images debs, config) | ~5-10 min |
| Second play | ~1 min |
| Smoke (pulls dind) | ~1-2 min |
| **Hands-on total** | **~15-20 min** after the drain |

Measure on the first build and write the result into the runbook.

**Rotate tokens on re-image?**
- **Routine/hygiene re-image:** no. Rotation adds a vault edit and a GitLab action for no gain if no compromise is suspected.
- **Suspected compromise:** yes, in the single-VM model mandatory, because the token was readable by every job. Reset via **`POST /runners/:id/reset_authentication_token`** (Maintainer/Owner on the project, or a `manage_runner`-scoped token) [V], <https://docs.gitlab.com/api/runners/>. Note that `POST /runners/reset_authentication_token` with the *current* token needs no other credential [V, same page]: a thief can rotate the token first and lock the operator out. That is why the ID-based reset by a human is the recovery path, and why holding the token off the job host (§1) matters.
- Also rotate any CI/CD variables of projects whose jobs ran during the exposure window (§1.4).

**Periodic rebuild [I]:**
- A scheduled rebuild needs something running `tofu apply` with the root@pam ticket, which conflicts with the repo's operator gates (R22) and puts PVE root credentials on a timer.
- Recommend a **cadence instead of automation**: re-image monthly and on each gitlab-runner minor upgrade. Track it in the runbook, with a `just runner-reimage` recipe that chains drain → `-replace` → play → smoke, behind the usual gate.
- In the split model the job host carries no vault secrets, so its rebuild is lower-stakes and could later become a candidate for automation.

---

## 5. VM escape and host exposure (brief, realistic)

The realistic path out of VM 120 is the network (§2/§3), not a KVM escape. QEMU/KVM escapes are rare, high-value 0-days. The knobs below reduce surface cheaply.

| Knob | Now | Recommendation |
|---|---|---|
| CPU type | Template bootstrap uses `--cpu host` [V `scripts/bootstrap_cloud_template.sh:111`, `packer/ubuntu26.pkr.hcl:30`]; `dev_vm` sets no `cpu.type` (bpg's schema default is `qemu64` [V vm.md]; [I] what a clone inherits, so read `qm config 120` after apply) | `x86-64-v2-AES` (bpg's recommendation [V]) hides host-specific flags and makes the VM portable to the second node for migration or re-image. `host` passes the CPU's flags through, which is arguably better for guest-side Spectre mitigations [V qm docs: pcid/spec-ctrl/ssbd need setting manually "unless the selected CPU type ... already enables them"]. The security difference is marginal; keep host microcode and kernel patched on `pve`. Pick explicitly and pin it in `dev_vm` (new optional var) |
| PCI/USB passthrough | none | Keep none (`hostpci` absent). Never give the runner the iGPU that Plex uses |
| virtiofs / 9p / shared dirs | none | Keep none (R18). bpg supports `virtiofs`; a guard test could assert its absence |
| Storage | `local-lvm` thin, shared with CTs 110/111 | [I] The risk is exhaustion, not escape: a 150 GB thin volume can fill the pool and stall Plex and Traefik. Check `pvesm status` headroom, or give the runner its own datastore when the second node comes. Disk alerts already cover it (R17) |
| QEMU guest agent | `agent.enabled = true` | Direction: the *host* sends commands (shutdown, fsfreeze, exec, file-write) to the guest over virtio-serial [I; qm docs only describe "shutdown or snapshots"]. Root in the guest controls the agent, so the **data it reports is untrusted**: IPs, hostname. The design already uses the static `ipv4_configured` rather than the agent IP (good). Guest→host risk is the QEMU-side parser only [I], which is low. Keeping it is fine; disabling it means ACPI shutdown and a bpg `agent { enabled = false }` override |
| Ballooning | not set (bpg `floating` default 0, balloon off [V]) | Keep it off: a fixed 16 GB, so a job can't pressure host memory via the balloon, and memory is accounted predictably next to Plex |
| Resource caps | 8 vCPU / 16 GB | [I] A job can saturate its vCPUs and starve Plex transcodes. Consider `cpu.units` (lower weight than CTs) or `cpu.limit`, and a `rate_limit` on the NIC if upload saturation shows up |
| Secure Boot / vTPM | OVMF/q35 from template | Not a meaningful control against this threat; leave it |

---

## 6. Comparison

| Control | Protects against | Effort in this repo | Residual risk |
|---|---|---|---|
| In-VM nftables (design R19) | Accidental LAN access by a job | Already planned (`tasks/firewall.yml`) | Root job flushes it; IPv4 only; hairpin via WAN IP |
| **PVE VM firewall (§2)** | Hostile job reaching LAN, PVE API (.50), CTs; MAC/IP/ARP spoofing; rogue RA | ~1 plan step: 4 `for_each` resources, `dev_vm` `firewall` var, cluster singleton, gated two-part apply, runbook | Hairpin to Traefik via WAN IP (allowlist admits LAN sources); IPv6 unless added; a misapplied datacenter switch could lock out the host (defused by `input_policy=ACCEPT` + node `enabled=false` + console) |
| VLAN (§3) | Same as PVE firewall, enforced off-host; fixes allowlist/hairpin naturally | Days; needs VLAN-capable router (+ managed switch); risky `vmbr0` edit; re-addressing | Depends on router inter-VLAN rules being right; CTs on a VLAN-aware bridge gain trunk-like ports |
| **Split manager (§1)** | Theft of `glrt-` tokens and the persistence they give past re-image | ~1 plan step: unprivileged LXC via `lxc_service`, TLS CA/certs in vault, dockerd TCP listener drop-in, cross-host drain, config/guard churn | Cross-job reading/tampering on the shared daemon (§1.4) unchanged; manager parses a possibly-hostile daemon's API |
| **Routine re-image (§4)** | Persistence on the job host (implants, poisoned images/cache) | Small: `just runner-reimage` recipe + runbook; uses existing tofu/play | Window between compromise and next re-image; token theft persists unless split or rotated |
| Token rotation on compromise | Stolen token reuse | Runbook only (ID-based reset) | Thief can self-rotate first via the token-based endpoint; human ID reset wins it back |
| One ephemeral VM per job (autoscaler/fleeting) | Cross-job exposure, persistence, token exposure, all at once | Out of scope (R23); split manager is the stepping stone | Hypervisor-level only |
| KVM knobs (§5) | Host resource exhaustion; minor escape surface | Trivial (pin cpu.type, keep no passthrough/virtiofs/balloon) | 0-day QEMU/KVM escapes |

## 7. Recommendation

1. **Ship the design as written** (single VM, in-VM nftables), with Appendix D's "trusted projects only" rule, **plus two cheap fixes found here**:
   - IPv6 coverage in nftables (`ip6` drop to `fe80::/10`, `fc00::/7` and the LAN prefix), or v6 disabled;
   - a measured answer on the WAN-IP hairpin to Traefik. If it reaches internal dashboards, fix the Traefik allowlist or add the out-drop.
2. **Next hardening step: the PVE VM firewall** (§2), as its own gated plan step, using the two-part sequence with `input_policy = "ACCEPT"` and the host firewall disabled. It is the only in-repo control that makes the LAN fence root-proof. Its root-proof negative control is `nft flush ruleset` in the guest, after which the probe must still fail.
3. **Then the split manager** (§1) as an unprivileged LXC on `pve`. It turns "a hostile job steals every token and keeps receiving jobs after re-image" into "a hostile job owns one disposable VM until the next re-image". It also lines up with a future docker-autoscaler/fleeting-proxmox move.
4. **Make re-image routine** (§4): a `just runner-reimage` recipe, monthly and on runner upgrades, with ID-based token reset in the runbook for suspected compromise.
5. **Skip VLAN for now.** Reconsider it only if the router supports inter-VLAN firewalling and more untrusted workloads arrive. Pin `cpu.type` explicitly and keep the §5 "none" items guarded.

Sources (in addition to inline):
- <https://docs.gitlab.com/runner/executors/docker/>
- <https://gitlab.com/gitlab-org/gitlab-runner/-/raw/main/executors/docker/docker.go>
- <https://gitlab.com/gitlab-org/gitlab-runner/-/raw/main/executors/docker/internal/prebuilt/prebuilt.go>
- <https://gitlab.com/gitlab-org/gitlab-runner/-/raw/main/executors/docker/internal/volumes/manager.go>
- <https://gitlab.com/gitlab-org/gitlab-runner/-/raw/main/executors/docker/services.go>
- <https://gitlab.com/gitlab-org/gitlab-runner/-/raw/main/shells/abstract.go>
- <https://gitlab.com/gitlab-org/gitlab-runner/-/raw/main/helpers/docker/credentials.go>
- <https://gitlab.com/gitlab-org/gitlab-runner/-/raw/main/helpers/docker/machine.go>
- <https://github.com/bpg/terraform-provider-proxmox/tree/main/docs/resources> (`virtual_environment_firewall_options.md`, `_firewall_rules.md`, `_firewall_ipset.md`, `_cluster_firewall.md`, `virtual_environment_node_firewall.md`, `virtual_environment_vm.md`)
- <https://pve.proxmox.com/pve-docs/chapter-qm.html>
