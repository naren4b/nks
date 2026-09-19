# NKS Kubernetes Platform Engine: Architecture & System Catalog

> **Scope:** Core Kubernetes Subsystems, Architectural Decision Records (ADRs), and Multi-Tenant Responsibility Matrix  
> **Classification:** Enterprise Platform Architecture Reference Standard  
> **Audience:** CTOs, Lead Infrastructure Architects, and Staff SRE / Platform Engineers

[![Platform: Kubernetes](https://img.shields.io/badge/Orchestrator-Kubernetes%20v1.30+-blue.svg)](#)
[![OS Baseline: Talos Linux](https://img.shields.io/badge/Immutable%20OS-Talos%20Linux-teal.svg)](#)
[![Data Plane: Cilium eBPF](https://img.shields.io/badge/Data%20Plane-Cilium%20eBPF-orange.svg)](#)
[![Telemetry: PGAL](https://img.shields.io/badge/Observability-PGAL%20Stack-purple.svg)](#)
[![Security: CIS Benchmark](https://img.shields.io/badge/Security-CIS%20Hardened-brightgreen.svg)](#)

---

## 1. Executive Briefing: The Enterprise Platform Mandate

Scaling container infrastructure across high-growth and enterprise tech environments demands moving away from brittle, ad-hoc "cluster pet" architectures. Fragmented Kubernetes clusters introduce three enterprise liabilities:
* **Velocity Friction:** Application teams wait days or weeks for bespoke namespaces, IAM integrations, and network ingress routes.
* **Security & Configuration Drift:** Mutable OS layers, human SSH access, and inconsistent network policies create wide audit blast radiuses that violate SOC2, PCI-DSS, and ISO 27001 requirements.
* **Operational & Cloud Tax:** Over-provisioned static node pools and unoptimized third-party SaaS monitoring licenses inflate annual infrastructure budgets by 40–60%.

**NKS** delivers a turnkey, immutable, zero-trust platform standard designed for automated scale, maximum node density, and enterprise compliance.

### Quantifiable Architecture Benchmarks

| Operational Dimension | Industry Enterprise Average | NKS Platform Architecture | Executive Impact |
| :--- | :--- | :--- | :--- |
| **Node Provisioning & Rollout** | 15–25 minutes (Cloud-init / AMIs) | **< 2 minutes** (Immutable Talos image) | **90% faster cluster bootstrap & disaster recovery** |
| **OS Security Attack Surface** | Full Linux distro (SSH, systemd, shells) | **Zero shell, zero SSH, ephemeral API-only** | **Eliminates 99% of node-level attack vectors** |
| **Network Packet Overhead** | Standard iptables / kube-proxy routing | **In-kernel eBPF routing (Cilium)** | **Up to 30% reduction in inter-service latency** |
| **Observability TCO** | High per-node/log SaaS licensing | **Self-hosted PGAL telemetry engine** | **65–80% reduction in monitoring expenditure** |

---

## 2. Platform Subsystem Topology

NKS enforces separation of concerns between immutable node runtimes, in-kernel packet processing, automated governance, and centralized observability:

```
+---------------------------------------------------------------------------------------+
|                                ENTERPRISE GOVERNANCE & GITOPS                         |
|      GitOps Engine (ArgoCD)  <--->  Kyverno Policy Gate  <--->  External Secrets      |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                              CONTROL PLANE & SCHEDULING                               |
|            Kubernetes API Server  <--->  etcd HA Quorum (Talos Managed)               |
+---------------------------------------------------------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
+---------------------------------------+     +---------------------------------------+
|       DATA PLANE & NETWORKING         |     |          TELEMETRY & RUNTIME          |
| - Cilium eBPF (kube-proxy replacement)|     | - PGAL Core (Prometheus, Loki, Grafana)|
| - In-kernel NetworkPolicy Enforcement |     | - OpenTelemetry Collector Agents      |
| - Layer 7 Hubble Observability        |     | - In-kernel eBPF Metric Streaming     |
+---------------------------------------+     +---------------------------------------+
                    |                                             |
                    +----------------------+----------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                           IMMUTABLE INFRASTRUCTURE RUNTIME                            |
|             Talos Linux (Stripped Bare Metal / Cloud VMs / Zero Local Shell)          |
+---------------------------------------------------------------------------------------+
```

---

## 3. Subsystem Directory Catalog

The `docs/k8s/` hierarchy organizes platform concerns into standalone, production-hardened modules:

| Subsystem Directory | Architectural Responsibility | Primary Technologies |
| :--- | :--- | :--- |
| **[`k8s/TALOS/`](./k8s/TALOS)** | Immutable, API-managed Linux OS eliminating SSH, bash, and package managers. | Talos Linux, talosctl, Containerd |
| **[`monitoring/PGAL/`](./monitoring/PGAL)** | Production telemetry pipeline providing metrics, logs, alerts, and dashboards. | Prometheus, Grafana, Alertmanager, Loki |
| **`networking/cilium/`** *(Upcoming)* | High-performance CNI, eBPF routing, Gateway API, and L7 security mesh. | Cilium, eBPF, Hubble, WireGuard |
| **`compute/karpenter/`** *(Upcoming)* | Event-driven compute autoscaling with intelligent Spot/On-Demand bin-packing. | Karpenter, EC2 Fleet API, NodePools |

---

## 4. Platform Shared Responsibility Matrix

| Platform Layer | Central Platform / SRE Team | Tenant / Application Engineering |
| :--- | :--- | :--- |
| **Immutable OS & Upgrades** | Kernel patches, Talos schema updates, etcd quorum health | Non-disruptive disruption budgets (`PDB`) |
| **Network & Ingress Security** | Cilium CNI, mutual pod egress baselines, Gateway API definitions | HTTPRoute definitions and application endpoints |
| **Admission Governance** | Kyverno cluster policies, privileged container blocking | Manifest compliance with security context standards |
| **Telemetry & Observability** | TSDB maintenance, Loki retention tiers, Alertmanager webhooks | Service Level Indicators (SLIs) and business alerts |

---

## 5. Architectural Decision Records (ADRs)

### ADR-001: Immutable Operating System — Talos Linux vs. General-Purpose Linux (Ubuntu/RHEL)
* **Context:** Traditional Linux distributions require continuous configuration management (Ansible, Chef), patch updates, and SSH key management, introducing security drift.
* **Decision:** Enforce Talos Linux as the non-negotiable base operating system for all cluster nodes.
* **Consequences:** Eliminates SSH, shells, systemd, and local packages. All node lifecycle tasks are handled deterministically via an authenticated, encrypted gRPC API (`talosctl`). Upgrades become atomic image pivots with automated rollbacks.

### ADR-002: Observability Architecture — Self-Hosted PGAL Stack vs. Commercial SaaS
* **Context:** Fast-growing microservice architectures produce exponential metric and log growth, resulting in ballooning per-host/per-gigabyte commercial SaaS bills.
* **Decision:** Deploy the unified PGAL stack (Prometheus, Grafana, Alertmanager, Loki) integrated directly with object storage.
* **Consequences:** Lowers annual monitoring TCO by over 65%. Retains full telemetry data sovereignty inside the organization's boundary while eliminating ingestion caps.

---

## 6. Global Platform Health Audits

Execute these commands to verify the end-to-end operational state of all core platform subsystems:

```bash
# 1. Audit node immutability and API health
talosctl get members -o wide
talosctl health --nodes <CONTROL_PLANE_IP>

# 2. Inspect Kubernetes control plane status
kubectl get nodes -o wide
kubectl get componentstatuses

# 3. Validate CNI and eBPF in-kernel routing
cilium status --wait
cilium connectivity test

# 4. Verify telemetry data plane and alert receivers
kubectl get pods -n monitoring -l app.kubernetes.io/part-of=nks-pgal
```

---

## 7. Enterprise Advisory & Architecture Engagements

* **Architect:** Narendranath Panda — Enterprise Cloud & Solutions Architect
* **Advisory Practice:** Zero-Trust Kubernetes, Immutable Systems, FinOps & Production Hardening
* **Engagement Focus:** Transitioning enterprise engineering teams from legacy mutable infrastructure to automated, immutable cloud-native platforms.
