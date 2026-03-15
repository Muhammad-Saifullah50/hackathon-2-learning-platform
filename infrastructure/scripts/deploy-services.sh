#!/bin/bash
set -e

echo "=========================================="
echo "Deploying LearnFlow Microservices"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    echo "Run './infrastructure/scripts/setup-minikube.sh' first"
    exit 1
fi

# Check if Dapr is running
if ! kubectl get pods -n dapr-system -l app=dapr-operator | grep -q "Running"; then
    echo "Error: Dapr is not running"
    echo "Run './infrastructure/scripts/deploy-dapr.sh' first"
    exit 1
fi

# Check if Dapr components are applied
if ! kubectl get components -n default | grep -q "learnflow-pubsub"; then
    echo "Error: Dapr components not found"
    echo "Run 'kubectl apply -f infrastructure/kubernetes/dapr/components.yaml' first"
    exit 1
fi

echo ""
echo "Deploying all microservices with Dapr sidecars..."
echo ""

# Deploy services
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
    echo "Deploying $service..."
    kubectl apply -f "infrastructure/kubernetes/services/${service}.yaml"
done

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Verify deployments
echo ""
echo "=========================================="
echo "Service Deployment Status:"
echo "=========================================="

for service in "${SERVICES[@]}"; do
    echo ""
    echo "Service: $service"
    kubectl get pods -l app="$service" -n default

    # Check if Dapr sidecar is injected (should show 2/2 containers)
    POD_STATUS=$(kubectl get pods -l app="$service" -n default -o jsonpath='{.items[0].status.containerStatuses[*].name}' 2>/dev/null || echo "")
    if echo "$POD_STATUS" | grep -q "daprd"; then
        echo "  ✓ Dapr sidecar injected"
    else
        echo "  ✗ Dapr sidecar NOT injected"
    fi
done

echo ""
echo "=========================================="
echo "All services deployed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run './infrastructure/scripts/test-service-invocation.sh' to test Dapr service invocation"
echo "2. Deploy Kong routes: './infrastructure/scripts/sync-kong-config.sh'"
echo ""
