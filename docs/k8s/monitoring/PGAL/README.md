# Enterprise Observability Subsystem: PGAL Stack

> **Architecture:** Prometheus, Grafana, Alertmanager & Loki (PGAL)  
> **Classification:** Production Addon / Reliability Data Plane  
> **Audience:** CTOs (TCO, FinOps & Data Sovereignty), Staff SREs (High-Cardinality, Alert Hygiene & Runbooks)

[![Subsystem: Monitoring](https://img.shields.io/badge/Subsystem-Monitoring%20%26%20Telemetry-purple.svg)](#)
[![Log Retention: S3 Tiered](https://img.shields.io/badge/Logs-Loki%20Object%20Storage-orange.svg)](#)
[![Metrics: TSDB NVMe](https://img.shields.io/badge/Metrics-Prometheus%20TSDB-red.svg)](#)
[![Alerting: Multi--Burn--Rate](https://img.shields.io/badge/Alerting-SLO%20Multi--Burn--Rate-blue.svg)](#)

---

## 1. Executive Briefing: The Observability Cost & Governance Problem

Commercial SaaS observability vendors (Datadog, Dynatrace, New Relic) enforce pricing structures anchored on host count, custom metric indexing, and log volume ingestion. As workloads scale, organizations face a costly dilemma: either throttle telemetry fidelity to curb bills or endure unpredictable monthly cost overruns.

The **NKS PGAL Subsystem** provides a cloud-native, open-source telemetry engine that enforces full data sovereignty, eliminating recurring SaaS license costs without compromising query performance.

### Economic & Operational Benchmark

| Dimension | Commercial SaaS (Datadog/New Relic) | NKS PGAL Architecture Benchmark | Executive Impact |
| :--- | :--- | :--- | :--- |
| **Annualized Cost at Scale** | $150–$350 / node / month + ingestion surcharges | **Compute + S3 storage only (~$35/node/mo)** | **65–80% reduction in annual monitoring TCO** |
| **Data Residency & Compliance** | Data transferred to third-party vendor clouds | **100% In-VPC / Private boundary** | Eliminates SOC2 / GDPR / HIPAA exfiltration risks |
| **Log Storage Footprint** | Heavy inverted indices across all string tokens | **Label-only indexing with S3 chunk compaction** | **75% reduction in log storage overhead** |
| **Alerting Standard** | Static CPU/RAM thresholds (high alert noise) | **Multi-window, multi-burn-rate SLO alerts** | Drastically reduces false alerts; protects MTTR |

---

## 2. End-to-End Telemetry Architecture

```
                    [ APPLICATIONS / WORKLOAD PODS ]
                      │ (Exposes /metrics)      │ (Streams to stdout/stderr)
                      ▼                         ▼
            [ Prometheus Agents ]       [ Promtail / Vector DaemonSet ]
             - Scrape Relabeling         - Stream Filtering & Label Extraction
             - Metric Dropping Rules     - In-Flight Chunk Compression
                      │                         │
                      ▼ (Pull / Push)           ▼ (gRPC Stream)
           +--------------------+     +--------------------+
           |  PROMETHEUS CORE   |     |     LOKI CORE      |
           |  - Local TSDB WAL  |     |  - In-Memory Index |
           |  - Fast NVMe Head  |     |  - S3 Object Chunk |
           +--------------------+     +--------------------+
                      │                         │
         (Alerts)     │                         ▼
            ▼         │               [ Object Storage (S3/MinIO) ]
     +--------------+ │                - 30-Day Automated Lifecycle Tier
     | ALERTMANAGER | │
     | - Dedup      | │
     | - Inhibition | └───────────┬───────────┘
     | - PagerDuty  |             │
     +--------------+             ▼
                       +----------------------+
                       |     GRAFANA CORE     |
                       | - Unified Dashboards |
                       | - Trace-Log Linking  |
                       | - Fine-Grained RBAC  |
                       +----------------------+
```

---

## 3. Architecture Decision Records (ADRs)

### ADR-PGAL-001: Loki Object-Storage vs. OpenSearch / Elasticsearch Full-Text Indexing
* **Context:** Indexing full unstructured log payloads in Elasticsearch requires massive JVM heap allocations and high-IOPS persistent storage.
* **Decision:** Standardize on Grafana Loki for log aggregation.
* **Consequences:** Loki indexes only container metadata labels and flushes compressed gzip chunks directly to object storage (S3). This cuts memory consumption by over 60%, removes dedicated Elasticsearch storage management, and allows seamless unified correlation with Prometheus metrics in Grafana.

### ADR-PGAL-002: Multi-Window Multi-Burn-Rate Alerts vs. Static Resource Thresholds
* **Context:** Paging engineers on static thresholds (e.g., `Node CPU > 85%`) generates alert fatigue, as temporary spikes rarely correlate with user-facing service disruptions.
* **Decision:** Implement Google SRE-style multi-burn-rate alerting targeting Service Level Objectives (SLOs).
* **Consequences:** Alertmanager evaluates error budget consumption over dual time windows (1h/5m for critical pages; 6h/30m for ticket alerts). On-call engineers are paged only when user-impacting error budgets are actively depleting.

---

## 4. Production Hardening: High-Cardinality Controls

High-cardinality label explosions are the primary failure mode of Prometheus TSDB. NKS embeds defensive relabeling rules directly at admission and scrape time:

```yaml
# Drop volatile ephemeral labels and unused high-frequency metrics at scrape time
metricRelabelings:
  - action: drop
    sourceLabels: [__name__]
    regex: "(container_tasks_state|http_request_duration_seconds_created|net_conntrack_dialer_.*)"
  - action: labeldrop
    regex: "(pod_template_hash|controller_revision_hash|uuid)"
```

### Storage Retention Strategy
* **Prometheus TSDB:** High-performance NVMe EBS volume allocated for a strict 7-day operational window (`--storage.tsdb.retention.time=7d`). Long-term analysis is offloaded to remote-write storage (Thanos/VictoriaMetrics).
* **Loki Logs:** Chunks flushed after 15 minutes or 1.5MB threshold; object storage lifecycle rules automatically expire logs older than 30 days.

---

## 5. Verification & Day-2 Operational Runbook

### Step 1: Subsystem Health & Scrape Verification
```bash
# Verify statefulsets, daemonsets, and collector health
kubectl get statefulset,daemonset,pods -n monitoring -l app.kubernetes.io/part-of=nks-pgal

# Validate Prometheus active targets and scrape success rate
kubectl port-forward svc/prometheus-k8s 9090:9090 -n monitoring &
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'
```

### Step 2: Test Alertmanager Routing & Dead-Man's Switch
```bash
# Verify Alertmanager configuration and active silences
curl -s http://localhost:9093/api/v2/status | jq '.cluster'

# Emit synthetic critical alert to validate downstream notification routing
curl -XPOST http://localhost:9093/api/v2/alerts -H "Content-Type: application/json" -d '[
  {
    "labels": {
      "alertname": "SyntheticPipelineValidation",
      "severity": "critical",
      "team": "platform-sre"
    },
    "annotations": {
      "summary": "Synthetically verifying Alertmanager webhook delivery",
      "description": "Validation test executed during Day-2 health check"
    }
  }
]'
```

---

## 6. Enterprise Advisory & Bespoke Observability Engagements

* **Advisory Scope:** Datadog/SaaS exit strategies, Grafana/Prometheus enterprise consolidation, FinOps cost chargeback via Kubecost/OpenCost, and automated SLO/SLI alerting framework design.
* **Architect:** Narendranath Panda — Enterprise Cloud Solutions Architect
