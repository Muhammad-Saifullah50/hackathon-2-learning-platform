#!/bin/bash
set -e

echo "=========================================="
echo "Deploying Dapr Subscriptions"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    exit 1
fi

# Check if Dapr components are deployed
if ! kubectl get components -n default | grep -q "learnflow-pubsub"; then
    echo "Error: Dapr pub/sub component not found"
    echo "Run 'kubectl apply -f infrastructure/kubernetes/dapr/components.yaml' first"
    exit 1
fi

echo ""
echo "Deploying all Dapr subscriptions..."
echo ""

# Deploy all subscriptions
kubectl apply -f infrastructure/kubernetes/dapr/subscriptions.yaml

echo ""
echo "Verifying subscriptions..."
kubectl get subscriptions -n default

echo ""
echo "=========================================="
echo "Dapr subscriptions deployed successfully!"
echo "=========================================="
echo ""
echo "Subscriptions:"
kubectl get subscriptions -n default -o custom-columns=NAME:.metadata.name,TOPIC:.spec.topic,SCOPES:.spec.scopes
echo ""
echo "Next steps:"
echo "1. Run './infrastructure/scripts/test-pubsub.sh' to test pub/sub messaging"
echo ""
