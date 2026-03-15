#!/bin/bash
set -e

echo "=========================================="
echo "Verifying Kong Health Checks"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    exit 1
fi

# Check if Kong is running
if ! kubectl get pods -n kong -l app.kubernetes.io/name=kong | grep -q "Running"; then
    echo "Error: Kong is not running"
    exit 1
fi

# Get Kong Admin API pod
KONG_ADMIN_POD=$(kubectl get pods -n kong -l app.kubernetes.io/name=kong -o jsonpath='{.items[0].metadata.name}')
echo "Using Kong pod: $KONG_ADMIN_POD"

# Port-forward Kong Admin API
echo ""
echo "Setting up port-forward to Kong Admin API..."
kubectl port-forward -n kong "$KONG_ADMIN_POD" 8001:8001 &
PORT_FORWARD_PID=$!

# Wait for port-forward to be ready
sleep 3

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up port-forward..."
    kill $PORT_FORWARD_PID 2>/dev/null || true
}
trap cleanup EXIT

# Check upstreams health
echo ""
echo "=========================================="
echo "Kong Upstreams Health Status:"
echo "=========================================="

curl -s http://localhost:8001/upstreams | jq -r '.data[] | "\nUpstream: \(.name)\n  Algorithm: \(.algorithm)\n  Health Checks: \(.healthchecks.active.type // "none")"'

# Check targets health for each upstream
echo ""
echo "=========================================="
echo "Upstream Targets Health:"
echo "=========================================="

UPSTREAMS=$(curl -s http://localhost:8001/upstreams | jq -r '.data[].id')

for upstream_id in $UPSTREAMS; do
    UPSTREAM_NAME=$(curl -s http://localhost:8001/upstreams/$upstream_id | jq -r '.name')
    echo ""
    echo "Upstream: $UPSTREAM_NAME"
    curl -s http://localhost:8001/upstreams/$upstream_id/health | jq '.data[] | {target: .target, health: .health, weight: .weight}'
done

echo ""
echo "=========================================="
echo "Kong Health Check Verification Complete!"
echo "=========================================="
