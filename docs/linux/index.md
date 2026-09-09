# Linux and Talos Operations

Day 1 setup and Day 2 investigation runbooks for Ubuntu, Rocky Linux, Talos Linux, and Kubernetes hosts. Use them to prepare an operations workstation, capture a baseline, and locate response-path delays before changing configuration or restarting services.

## Guides

- [Linux and Talos System Setup](system-setup.md) — install the operations toolkit, validate access, capture a Day 1 baseline, and follow a Day 2 triage sequence.
- [Response-Slowness Investigation](slowness-investigation.md) — locate DNS, network, CPU, memory, storage, limit, or kernel delays with explanations of what each signal means.
- [Response-Slowness Commands](slowness-commands.md) — compact command list for the same investigation flow.

Talos nodes are immutable and API-managed. Do not install packages or use SSH on Talos; use `talosctl` for the node and `kubectl` for workloads.
