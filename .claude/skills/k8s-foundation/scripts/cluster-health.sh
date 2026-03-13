#!/usr/bin/env bash
# cluster-health.sh — Full Kubernetes cluster health sweep
# Usage: bash cluster-health.sh [--namespace <ns>] [--wide] [--json]
#
# Sections: nodes, pods, deployments, daemonsets, statefulsets, PVCs, events, resources

set -euo pipefail

NAMESPACE_FLAG="--all-namespaces"
WIDE=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--namespace) NAMESPACE_FLAG="-n $2"; shift 2 ;;
    --wide)         WIDE="-o wide"; shift ;;
    --json)         OUTPUT="json"; shift ;;
    -h|--help)
      echo "Usage: bash cluster-health.sh [--namespace <ns>] [--wide] [--json]"
      echo "  --namespace, -n   Target a specific namespace (default: all)"
      echo "  --wide            Show extended output columns"
      echo "  --json            Output raw JSON (for programmatic use)"
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

divider() { echo ""; echo "══════════════════════════════════════════════════════════════"; echo "  $1"; echo "══════════════════════════════════════════════════════════════"; }

# ── 1. Cluster info ──
divider "CLUSTER INFO"
kubectl cluster-info 2>/dev/null | head -5
echo ""
echo "Server version: $(kubectl version --short 2>/dev/null | grep Server || kubectl version 2>/dev/null | grep -i server | head -1)"

# ── 2. Node status ──
divider "NODE STATUS"
kubectl get nodes $WIDE 2>/dev/null
echo ""
echo "── Node resource usage (if metrics-server available) ──"
kubectl top nodes 2>/dev/null || echo "  [metrics-server not available — skipping]"

# ── 3. Namespace overview ──
divider "NAMESPACES"
kubectl get namespaces 2>/dev/null

# ── 4. Pod health ──
divider "POD HEALTH"
echo "── All pods ──"
kubectl get pods $NAMESPACE_FLAG $WIDE 2>/dev/null

echo ""
echo "── Pods NOT Running/Succeeded ──"
kubectl get pods $NAMESPACE_FLAG --field-selector=status.phase!=Running,status.phase!=Succeeded 2>/dev/null || echo "  All pods healthy"

echo ""
echo "── Pods with restarts > 0 ──"
kubectl get pods $NAMESPACE_FLAG -o json 2>/dev/null | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', [])
found = False
for pod in items:
    ns = pod['metadata'].get('namespace','?')
    name = pod['metadata'].get('name','?')
    for cs in pod.get('status',{}).get('containerStatuses',[]):
        r = cs.get('restartCount',0)
        if r > 0:
            print(f'  {ns}/{name}: {cs[\"name\"]} restarts={r}')
            found = True
if not found:
    print('  No containers with restarts')
" 2>/dev/null || echo "  [could not parse pod data]"

# ── 5. Deployments ──
divider "DEPLOYMENTS"
kubectl get deployments $NAMESPACE_FLAG $WIDE 2>/dev/null

echo ""
echo "── Deployments not fully available ──"
kubectl get deployments $NAMESPACE_FLAG -o json 2>/dev/null | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
found = False
for d in data.get('items', []):
    ns = d['metadata'].get('namespace','?')
    name = d['metadata'].get('name','?')
    spec_replicas = d.get('spec',{}).get('replicas',0)
    available = d.get('status',{}).get('availableReplicas',0) or 0
    if available < spec_replicas:
        print(f'  {ns}/{name}: {available}/{spec_replicas} available')
        found = True
if not found:
    print('  All deployments fully available')
" 2>/dev/null || echo "  [could not parse deployment data]"

# ── 6. DaemonSets ──
divider "DAEMONSETS"
kubectl get daemonsets $NAMESPACE_FLAG $WIDE 2>/dev/null

# ── 7. StatefulSets ──
divider "STATEFULSETS"
kubectl get statefulsets $NAMESPACE_FLAG $WIDE 2>/dev/null || echo "  No statefulsets found"

# ── 8. PVCs ──
divider "PERSISTENT VOLUME CLAIMS"
kubectl get pvc $NAMESPACE_FLAG $WIDE 2>/dev/null || echo "  No PVCs found"

echo ""
echo "── PVCs not Bound ──"
kubectl get pvc $NAMESPACE_FLAG --field-selector=status.phase!=Bound 2>/dev/null || echo "  All PVCs bound"

# ── 9. Services ──
divider "SERVICES"
kubectl get services $NAMESPACE_FLAG $WIDE 2>/dev/null

# ── 10. Recent events (warnings) ──
divider "RECENT WARNING EVENTS (last 30)"
kubectl get events $NAMESPACE_FLAG --field-selector=type=Warning --sort-by='.lastTimestamp' 2>/dev/null | tail -30 || echo "  No warning events"

# ── 11. Resource quotas & limits ──
divider "RESOURCE QUOTAS"
kubectl get resourcequotas $NAMESPACE_FLAG 2>/dev/null || echo "  No resource quotas defined"

divider "LIMIT RANGES"
kubectl get limitranges $NAMESPACE_FLAG 2>/dev/null || echo "  No limit ranges defined"

# ── Summary ──
divider "SUMMARY"
TOTAL_NODES=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
READY_NODES=$(kubectl get nodes --no-headers 2>/dev/null | grep -c ' Ready' || echo 0)
TOTAL_PODS=$(kubectl get pods $NAMESPACE_FLAG --no-headers 2>/dev/null | wc -l)
RUNNING_PODS=$(kubectl get pods $NAMESPACE_FLAG --no-headers --field-selector=status.phase=Running 2>/dev/null | wc -l)
FAILED_PODS=$(kubectl get pods $NAMESPACE_FLAG --no-headers --field-selector=status.phase=Failed 2>/dev/null | wc -l)
PENDING_PODS=$(kubectl get pods $NAMESPACE_FLAG --no-headers --field-selector=status.phase=Pending 2>/dev/null | wc -l)

echo "  Nodes:   $READY_NODES/$TOTAL_NODES ready"
echo "  Pods:    $RUNNING_PODS running, $PENDING_PODS pending, $FAILED_PODS failed (total: $TOTAL_PODS)"
echo ""

if [[ "$FAILED_PODS" -gt 0 ]] || [[ "$PENDING_PODS" -gt 0 ]] || [[ "$READY_NODES" -lt "$TOTAL_NODES" ]]; then
  echo "  ⚠️  Issues detected — review sections above for details"
else
  echo "  ✅ Cluster looks healthy"
fi
