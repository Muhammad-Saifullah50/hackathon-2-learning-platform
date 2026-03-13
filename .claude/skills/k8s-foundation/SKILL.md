---
name: k8s-foundation
description: >
  Kubernetes cluster health checking and basic Helm chart operations. Use when the user asks to:
  (1) Check cluster health, node status, pod health, or resource usage,
  (2) Run a cluster health sweep or diagnostics,
  (3) Install or upgrade Helm charts with values files or set overrides,
  (4) Find common Helm chart install commands (nginx-ingress, cert-manager, prometheus, PostgreSQL, Redis, etc.),
  (5) Troubleshoot unhealthy pods, pending PVCs, or failed deployments,
  (6) Get a cluster overview or summary.
  Triggers: "check cluster", "cluster health", "helm install", "helm upgrade", "deploy chart",
  "install nginx ingress", "install cert-manager", "install prometheus", "pod status", "node status",
  "k8s health", "kubernetes diagnostics".
---

# k8s-foundation

Kubernetes cluster health checks and Helm chart install/upgrade workflows.

## Prerequisites

- `kubectl` configured with a valid kubeconfig
- `helm` v3+ installed
- Optional: `metrics-server` deployed for resource usage data

## Workflows

### 1. Cluster Health Check

Run the bundled health sweep script:

```bash
bash scripts/cluster-health.sh
```

Options:
- `--namespace <ns>` — scope to a single namespace (default: all)
- `--wide` — show extended output columns
- `--help` — show usage

The script checks these areas in order:
1. Cluster info and server version
2. Node status and resource usage (requires metrics-server)
3. Namespaces
4. Pod health — all pods, non-running pods, pods with container restarts
5. Deployments — all and those not fully available
6. DaemonSets
7. StatefulSets
8. PVCs — all and those not Bound
9. Services
10. Recent warning events (last 30)
11. Resource quotas and limit ranges
12. Summary with pass/fail indicator

**Interpreting results:** The summary section shows a quick pass/fail. If issues are detected, scroll up to the relevant section for details. Common problems:
- Nodes `NotReady` — check kubelet logs, node resources
- Pods `CrashLoopBackOff` — check `kubectl logs <pod>` and `kubectl describe pod <pod>`
- PVCs `Pending` — check StorageClass availability and PV provisioner
- Deployments under-replicated — check events, resource limits, node capacity

### 2. Helm Chart Install

```bash
# Add repo (one-time)
helm repo add <repo-name> <repo-url>
helm repo update

# Install with defaults
helm install <release-name> <repo-name>/<chart-name> \
  --namespace <ns> --create-namespace

# Install with values file
helm install <release-name> <repo-name>/<chart-name> \
  --namespace <ns> --create-namespace \
  -f values.yaml

# Install with inline overrides
helm install <release-name> <repo-name>/<chart-name> \
  --namespace <ns> --create-namespace \
  --set key1=val1 \
  --set key2=val2
```

### 3. Helm Chart Upgrade

```bash
# Upgrade with values file
helm upgrade <release-name> <repo-name>/<chart-name> \
  --namespace <ns> \
  -f values.yaml

# Upgrade with inline overrides
helm upgrade <release-name> <repo-name>/<chart-name> \
  --namespace <ns> \
  --set image.tag=v2.0.0

# Install-or-upgrade (idempotent)
helm upgrade --install <release-name> <repo-name>/<chart-name> \
  --namespace <ns> --create-namespace \
  -f values.yaml
```

### 4. Verify a Helm Release

```bash
# List releases
helm list --namespace <ns>

# Check release status
helm status <release-name> --namespace <ns>

# See applied values
helm get values <release-name> --namespace <ns>
```

## Common Charts Reference

For repo URLs, install commands, and recommended values for popular charts (nginx-ingress, cert-manager, kube-prometheus-stack, metrics-server, Loki, PostgreSQL, Redis, MinIO, External Secrets), see [references/common-charts.md](references/common-charts.md).

## Troubleshooting Quick Reference

| Symptom | Diagnostic command | Common fix |
|---|---|---|
| Pod `CrashLoopBackOff` | `kubectl logs <pod> -n <ns> --previous` | Fix app config or resource limits |
| Pod `ImagePullBackOff` | `kubectl describe pod <pod> -n <ns>` | Fix image name/tag, check registry auth |
| Pod `Pending` | `kubectl describe pod <pod> -n <ns>` | Insufficient resources or no matching node |
| PVC `Pending` | `kubectl describe pvc <pvc> -n <ns>` | Check StorageClass, CSI driver |
| Node `NotReady` | `kubectl describe node <node>` | Check kubelet, disk/memory pressure |
| Helm install fails | `helm install --debug --dry-run ...` | Validate values and chart version |
| Helm upgrade conflict | `helm history <release> -n <ns>` | Roll back: `helm rollback <release> <rev>` |
