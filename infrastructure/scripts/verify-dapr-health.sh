#!/bin/bash
set -e

echo "=========================================="
echo "Verifying Dapr Health"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    exit 1
fi

# Check Dapr system components
echo ""
echo "=========================================="
echo "Dapr System Components:"
echo "=========================================="
kubectl get pods -n dapr-system

# Check Dapr sidecar health for all services
echo ""
echo "=========================================="
echo "Dapr Sidecar Health:"
echo "=========================================="

SERVICES=(
    "auth-service"
    "user-service"
    "sandbox-service"
    "llm-service"
    "triage-agent"
    "concepts-agent"
    "code-review-agent"
    "debug-agent"
    "exercise-agent"
    "progress-agent"
    "teacher-service"
)

for service in "${SERVICES[@]}"; do
    POD=$(kubectl get pods -l app="$service" -n default -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

    if [ -z "$POD" ]; then
        echo ""
        echo "Service: $service - NOT DEPLOYED"
        continue
    fi

    echo ""
    echo "Service: $service"
    echo "  Pod: $POD"

    # Check if Dapr sidecar is running
    DAPRD_STATUS=$(kubectl get pod "$POD" -n default -o jsonpath='{.status.containerStatuses[?(@.name=="daprd")].ready}' 2>/dev/null || echo "false")

    if [ "$DAPRD_STATUS" = "true" ]; then
        echo "  Dapr Sidecar: ✓ HEALTHY"

        # Query Dapr health endpoint
        HEALTH=$(kubectl exec -n default "$POD" -c daprd -- curl -s http://localhost:3500/v1.0/healthz 2>/dev/null || echo "failed")
        echo "  Health Check: $HEALTH"
    else
        echo "  Dapr Sidecar: ✗ NOT READY"
    fi
done

echo ""
echo "=========================================="
echo "Dapr Health Verification Complete!"
echo "=========================================="
