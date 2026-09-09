# Linux and Talos System Setup Runbook

This runbook prepares an operations workstation and managed nodes for:

- **Day 1:** initial installation, configuration, access, validation, and baseline capture.
- **Day 2:** routine health checks, incident triage, evidence collection, and safe troubleshooting.

It covers Ubuntu, Rocky Linux, and Talos Linux. The important difference is that Ubuntu and Rocky are conventional mutable Linux systems, while Talos is an immutable, API-managed Kubernetes operating system.

**Related:** [Linux and Talos Operations](index.md) · [Slowness investigation](slowness-investigation.md) · [Command reference](slowness-commands.md)

---

## Operating principles

1. Measure before changing or restarting anything.
2. Record the hostname and timestamp with every investigation.
3. Begin with system-wide signals, then narrow down to a service, process, container, or dependency.
4. Treat a single metric as a clue, not proof. Correlate CPU, memory, storage, network, application logs, and request timings.
5. Do not install packages or use SSH on Talos nodes. Use `talosctl` for the node and `kubectl` for Kubernetes workloads.
6. Protect kubeconfig, talosconfig, SSH keys, and diagnostic archives as sensitive operational artifacts.

---

# Day 1 — Initial Setup

## 1. Identify the operating system

Run this on Ubuntu or Rocky Linux:

```bash
cat /etc/os-release
uname -a
uname -m
hostnamectl
```

Confirm the distribution, version, CPU architecture, kernel, hostname, and virtualization environment before installing anything.

## 2. Update package metadata

### Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

### Rocky Linux

```bash
sudo dnf makecache
sudo dnf upgrade -y
```

Schedule reboots according to the environment's change process. Do not reboot a production node merely because packages were updated.

## 3. Install the core operations toolkit

### Ubuntu

```bash
sudo apt install -y \
  curl \
  procps \
  sysstat \
  iproute2 \
  iputils-ping \
  iputils-tracepath \
  dnsutils \
  netcat-openbsd \
  lsof \
  strace \
  ethtool \
  util-linux \
  net-tools \
  jq \
  vim-tiny \
  tmux
```

### Rocky Linux

```bash
sudo dnf install -y \
  curl \
  procps-ng \
  sysstat \
  iproute \
  iputils \
  bind-utils \
  nmap-ncat \
  traceroute \
  lsof \
  strace \
  ethtool \
  util-linux \
  net-tools \
  jq \
  vim-minimal \
  tmux
```

If an optional Rocky Linux package is unavailable:

```bash
sudo dnf install -y epel-release
sudo dnf makecache
```

### Toolkit map

| Goal | Commands | Package family |
|---|---|---|
| CPU and load | `top`, `ps`, `vmstat` | `procps` / `procps-ng` |
| Per-CPU and process history | `mpstat`, `pidstat`, `sar` | `sysstat` |
| Storage latency | `iostat` | `sysstat` |
| Memory and swap | `free`, `vmstat`, `swapon` | `procps`, `util-linux` |
| Interfaces, routes and sockets | `ip`, `ss`, `nstat` | `iproute2` / `iproute` |
| DNS | `dig`, `getent`, `resolvectl` | `dnsutils` / `bind-utils`, system libraries |
| Connectivity | `ping`, `tracepath`, `traceroute`, `nc`, `curl` | IP utilities, Netcat, cURL |
| Files and file descriptors | `lsof`, `find`, `df`, `du` | `lsof`, core utilities |
| System calls | `strace` | `strace` |
| Interface details | `ethtool` | `ethtool` |
| Service and kernel logs | `systemctl`, `journalctl`, `dmesg` | `systemd`, `util-linux` |
| Structured output | `jq` | `jq` |

## 4. Enable performance history

`sysstat` supplies `iostat`, `mpstat`, `pidstat`, and `sar`. Enable its collector so historical data is available after an incident begins.

```bash
sudo systemctl enable --now sysstat
systemctl status sysstat --no-pager
```

Validate data collection:

```bash
sar -u 1 3
sar -r 1 3
iostat -xz 1 3
```

If historical collection is disabled by distribution policy, enable it through the distribution-supported `sysstat` configuration and document the chosen retention period.

## 5. Validate time synchronization

Accurate time is required to correlate application, kernel, Kubernetes, load-balancer, and monitoring events.

```bash
timedatectl status
date --iso-8601=seconds
```

Confirm that NTP synchronization is active. Use UTC consistently in operational records where teams span multiple regions.

## 6. Validate hostname, addressing, DNS, and routes

```bash
hostnamectl
ip -br address
ip route
getent hosts example.com
resolvectl status
```

On systems without `systemd-resolved`, `resolvectl` may not exist. Inspect `/etc/resolv.conf` instead:

```bash
cat /etc/resolv.conf
```

## 7. Validate the installed toolkit

```bash
command -v curl top ps vmstat mpstat pidstat sar iostat ip ss nstat dig nc lsof strace ethtool jq
```

Check versions for the principal tools:

```bash
curl --version
sar -V
ip -Version
jq --version
```

Any missing command should be resolved before the machine is placed into operational service.

## 8. Capture a Day 1 baseline

Collect a quiet-period baseline after the machine is configured but before normal load begins:

```bash
date --iso-8601=seconds
uptime
nproc
free -h
df -hT
df -i
ip -br address
ip route
ss -s
mpstat -P ALL 1 5
vmstat 1 5
iostat -xz 1 5
```

Store the output in the approved operations or monitoring system. A baseline makes it possible to distinguish an abnormal value from normal machine behavior.

## 9. Configure the Talos administration workstation

Do this on an administrator workstation, bastion host, or WSL environment—not inside a Talos node.

Required tools:

| Tool | Purpose |
|---|---|
| `talosctl` | Talos machine configuration, inspection, logs, services, upgrades, and recovery |
| `kubectl` | Kubernetes API and workload operations |
| `helm` | Helm-based application and platform releases |
| `jq` | JSON filtering |
| `yq` | YAML inspection and controlled transformation |
| `k9s` | Optional interactive Kubernetes interface |

Validate the client tools:

```bash
talosctl version --client
kubectl version --client
helm version
jq --version
yq --version
```

Keep the `talosctl` client compatible with the Talos version running on the nodes.

### Configure Talos and Kubernetes access

Place the approved `talosconfig` and kubeconfig on the administration workstation with restrictive permissions:

```bash
chmod 600 <PATH-TO-TALOSCONFIG>
chmod 600 <PATH-TO-KUBECONFIG>
```

Confirm the active Talos context and endpoint:

```bash
talosctl --talosconfig <PATH-TO-TALOSCONFIG> config info
```

Confirm Kubernetes access:

```bash
kubectl --kubeconfig <PATH-TO-KUBECONFIG> cluster-info
kubectl --kubeconfig <PATH-TO-KUBECONFIG> get nodes -o wide
```

Confirm Talos access to each node:

```bash
talosctl --talosconfig <PATH-TO-TALOSCONFIG> -n <NODE-IP> version
talosctl --talosconfig <PATH-TO-TALOSCONFIG> -n <NODE-IP> health
```

Do not commit kubeconfig, talosconfig, machine secrets, or generated control-plane/worker configuration containing secrets to an unprotected repository.

## 10. Capture a Talos/Kubernetes Day 1 baseline

```bash
talosctl -n <NODE-IP> get members
talosctl -n <NODE-IP> services
talosctl -n <NODE-IP> get addresses
talosctl -n <NODE-IP> get routes
talosctl -n <NODE-IP> get links
talosctl -n <NODE-IP> get mounts
talosctl -n <NODE-IP> get volumestatus
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get events -A --sort-by='.lastTimestamp'
```

Record the expected nodes, roles, versions, IPs, routes, volumes, Kubernetes system pods, and normal warning events.

---

# Day 2 — Routine Operations and Troubleshooting

## 1. Start every investigation with an incident header

```bash
date --iso-8601=seconds
hostnamectl
uptime
```

Record:

- What is slow or unavailable?
- When did it start?
- Is every user, tenant, node, or region affected?
- What changed recently?
- Can the problem be reproduced?
- What is the expected response time or baseline?

## 2. Measure the request before checking the server

```bash
curl -sS -o /dev/null -w 'DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nFirst byte: %{time_starttransfer}s\nTotal: %{time_total}s\nHTTP: %{http_code}\n' '<URL>'
```

Interpret the largest phase:

| Slow phase | Start investigating |
|---|---|
| DNS | Resolver configuration, DNS server reachability, search domains |
| Connect | Routing, firewall, load balancer, listener, connection backlog |
| TLS | Certificates, TLS negotiation, proxy/load balancer capacity |
| First byte | Application, database, cache, storage, upstream services |
| Total after first byte | Large payload, slow streaming, packet loss, client bandwidth |

Repeat the test to distinguish persistent latency from a cold connection or cache.

## 3. Perform the five-minute Linux triage

```bash
top
vmstat 1
mpstat -P ALL 1
free -h
iostat -xz 1
pidstat -dur 1
ss -s
```

Look for:

- Run queue larger than available CPUs.
- One saturated CPU core or process.
- Sustained I/O wait, disk queue, or high storage latency.
- Low available memory, active swapping, or an OOM event.
- Increasing network drops, retransmissions, or abnormal socket states.
- A process consuming abnormal CPU, memory, or I/O relative to its baseline.

Stop streaming commands with `Ctrl+C` after enough samples have been captured.

## 4. Check the affected service

```bash
systemctl status <SERVICE> --no-pager
sudo journalctl -u <SERVICE> --since '30 minutes ago' --no-pager
systemctl show <SERVICE> -p ActiveEnterTimestamp -p ExecMainStartTimestamp -p NRestarts
```

Confirm whether the service is active, repeatedly restarting, rejecting work, timing out against a dependency, or reporting resource exhaustion.

## 5. Narrow the investigation to a process

```bash
ps -eo pid,ppid,stat,comm,%cpu,%mem --sort=-%cpu | head -20
ps -eo pid,comm,%mem,rss,vsz --sort=-rss | head -20
pidstat -u -d -r -p <PID> 1
top -H -p <PID>
```

If necessary, trace the process briefly:

```bash
sudo strace -tt -T -p <PID>
```

`strace` adds overhead. Use it for a short, targeted observation and stop it with `Ctrl+C`.

## 6. Check storage and blocked processes

```bash
iostat -xz 1
pidstat -d 1
df -hT
df -i
ps -eo state,pid,ppid,wchan:30,comm,args | awk '$1 ~ /^D/'
sudo lsof +L1
```

Investigate full filesystems, exhausted inodes, deleted-but-open files, sustained device latency, and processes stuck in uninterruptible `D` state.

## 7. Check the network and DNS

```bash
ip -s link
ss -lntp
ss -antp
nstat -az | grep -iE 'Retrans|Timeout|Listen|Drop'
time getent hosts <HOST>
dig <HOST> +stats
nc -vz -w 5 <HOST> <PORT>
curl -v --connect-timeout 5 '<URL>'
```

Compare counters over time. A large historical counter is less useful than a counter that increases while the issue is reproduced.

To test the endpoint while bypassing normal DNS but preserving the hostname for TLS and HTTP:

```bash
curl -v --resolve '<HOST>:443:<IP>' 'https://<HOST>/'
```

## 8. Check limits, kernel events, and OOM activity

```bash
cat /proc/<PID>/limits
find /proc/<PID>/fd -maxdepth 1 -type l 2>/dev/null | wc -l
cat /proc/sys/fs/file-nr
sudo journalctl -k --since '1 hour ago' --no-pager
sudo journalctl -k --since '1 hour ago' --no-pager | grep -iE 'oom|out of memory|killed process|error|timeout|reset|blocked|hung|I/O|segfault|thermal'
```

Do not raise limits blindly. Determine why consumption grew and whether it reflects legitimate capacity, a leak, retry storm, or dependency failure.

## 9. Use historical performance data

```bash
sar -u
sar -r
sar -q
sar -n DEV
```

Use `sar` to determine when CPU, memory, load, or network behavior changed. Compare the incident interval with the Day 1 baseline and a known healthy period.

## 10. Perform Talos node triage

Talos has no interactive shell, package manager, or systemd. Use these from the administration workstation:

```bash
talosctl -n <NODE-IP> dashboard
talosctl -n <NODE-IP> processes
talosctl -n <NODE-IP> stats
talosctl -n <NODE-IP> services
talosctl -n <NODE-IP> dmesg
talosctl -n <NODE-IP> get addresses
talosctl -n <NODE-IP> get routes
talosctl -n <NODE-IP> get links
talosctl -n <NODE-IP> get mounts
talosctl -n <NODE-IP> get volumestatus
talosctl -n <NODE-IP> logs kubelet
talosctl -n <NODE-IP> logs containerd
talosctl health
```

### Traditional Linux to Talos mapping

| Linux habit | Talos command |
|---|---|
| `top` / `htop` | `talosctl dashboard` |
| `ps` | `talosctl processes` |
| Container statistics | `talosctl stats` |
| `systemctl status` | `talosctl services` |
| `journalctl -u SERVICE` | `talosctl logs <SERVICE>` |
| `dmesg` | `talosctl dmesg` |
| `ip address` | `talosctl get addresses` |
| `ip route` | `talosctl get routes` |
| `ip link` | `talosctl get links` |
| `mount` / `df` | `talosctl get mounts` and `talosctl get volumestatus` |
| `ls PATH` | `talosctl list <PATH>` |
| `cat FILE` | `talosctl read <PATH>` |

## 11. Perform Kubernetes workload triage

Use `kubectl` for the workload layer after checking the Talos node:

```bash
kubectl get nodes -o wide
kubectl top nodes
kubectl get pods -A -o wide
kubectl top pods -A --containers
kubectl get events -A --sort-by='.lastTimestamp'
kubectl describe pod <POD> -n <NAMESPACE>
kubectl logs <POD> -n <NAMESPACE> --all-containers --since=30m
kubectl logs <POD> -n <NAMESPACE> --all-containers --previous
kubectl get endpoints,endpointslices -n <NAMESPACE>
```

`kubectl top` requires the Kubernetes Metrics API, normally supplied by Metrics Server or another compatible implementation.

Follow the request path rather than examining random pods:

```text
Client
→ DNS
→ Load balancer / ingress
→ Kubernetes Service and EndpointSlice
→ Application pod
→ Database, cache, queue, storage, or external dependency
```

## 12. Safe remediation sequence

1. Capture timestamps, metrics, process state, events, and relevant logs.
2. Identify the constrained or failing layer.
3. Stop or reduce the source of overload when possible.
4. Restore service using the least disruptive approved action.
5. Validate the same user request that originally failed.
6. Confirm recovery through metrics and logs, not only process status.
7. Preserve evidence and document the root cause, trigger, impact, remediation, and prevention.

Avoid using restart, reboot, pod deletion, cache clearing, or limit increases as the first diagnostic action. They may restore availability while destroying evidence and leaving the cause unresolved.

---

# Operational Readiness Checklist

## Ubuntu and Rocky Linux

- [ ] OS, kernel, hostname, CPU architecture, and time synchronization verified.
- [ ] Core troubleshooting toolkit installed.
- [ ] `sysstat` collection enabled and validated.
- [ ] DNS, routes, interfaces, and required service ports validated.
- [ ] Service logs accessible through the approved privilege model.
- [ ] Day 1 CPU, memory, storage, filesystem, and network baseline captured.
- [ ] Monitoring and alerting connected.
- [ ] Log rotation and filesystem-capacity alerts tested.
- [ ] Access and escalation ownership documented.

## Talos and Kubernetes

- [ ] Compatible `talosctl`, `kubectl`, and `helm` available on the administration workstation.
- [ ] `talosconfig` and kubeconfig stored with restrictive permissions.
- [ ] Talos API and Kubernetes API access validated.
- [ ] Expected Talos nodes, routes, links, mounts, and volumes recorded.
- [ ] Kubernetes nodes, system pods, and workload namespaces healthy.
- [ ] Metrics API and centralized observability validated.
- [ ] Etcd backup and recovery procedures documented and tested separately.
- [ ] Talos machine configuration, upgrade, and rollback procedures documented.
- [ ] Break-glass access and certificate-expiry ownership documented.

---

# Quick Decision Guide

| Observation | Most likely investigation path |
|---|---|
| High load and high CPU | Identify process/thread; check traffic and recent changes |
| High load but CPU has idle capacity | Check blocked tasks, storage, NFS, locks, or uninterruptible waits |
| Low available memory with swap I/O | Find memory growth; check OOM and workload limits |
| High disk `await` or queue | Identify I/O process; check device, filesystem, volume, and backend |
| Increasing retransmissions or drops | Check interface, path, MTU, congestion, firewall, and dependency |
| Fast connection but slow first byte | Check application, database, cache, queue, and upstream calls |
| Slow normal request but fast `--resolve` request | Investigate DNS resolution |
| Repeated service or pod restarts | Inspect current and previous logs, events, probes, limits, and OOM |
| Talos node problem | Use `talosctl` for OS/runtime; use `kubectl` for workloads |

The outcome of a good investigation is not merely “the server was slow.” It is a timestamped, evidence-backed statement identifying which layer introduced latency and why.
