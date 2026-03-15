#!/bin/bash
set -e

echo "=========================================="
echo "Deploying Kong API Gateway"
echo "=========================================="

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "Error: helm is not installed"
    echo "Install with: curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash"
    exit 1
fi

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    echo "Run './infrastructure/scripts/setup-minikube.sh' first"
    exit 1
fi

# Check if PostgreSQL is running
if ! kubectl get pods -n kong -l app.kubernetes.io/name=postgresql | grep -q "Running"; then
    echo "Error: PostgreSQL for Kong is not running"
    echo "Run './infrastructure/scripts/deploy-kong-postgres.sh' first"
    exit 1
fi

# Add Kong Helm repository
echo "Adding Kong Helm repository..."
helm repo add kong https://charts.konghq.com
helm repo update

# Check if Kong is already deployed
if helm list -n kong | grep -q "^kong"; then
    echo "Kong is already deployed"
    echo "To upgrade: helm upgrade kong kong/kong -f infrastructure/kubernetes/kong/values.yaml -n kong"
    exit 0
fi

# Deploy Kong
echo ""
echo "Deploying Kong API Gateway..."
helm install kong kong/kong \
  -f infrastructure/kubernetes/kong/values.yaml \
  -n kong \
  --wait \
  --timeout 10m

# Wait for Kong to be ready
echo ""
echo "Waiting for Kong pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kong -n kong --timeout=300s

# Run Kong migrations
echo ""
echo "Running Kong database migrations..."
kubectl exec -n kong deployment/kong-kong -- kong migrations bootstrap || echo "Migrations already bootstrapped"
kubectl exec -n kong deployment/kong-kong -- kong migrations up

# Verify deployment
echo ""
echo "Verifying Kong deployment..."
kubectl get pods -n kong -l app.kubernetes.io/name=kong
kubectl get svc -n kong

# Test Kong Admin API
echo ""
echo "Testing Kong Admin API..."
KONG_ADMIN_POD=$(kubectl get pods -n kong -l app.kubernetes.io/name=kong -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n kong $KONG_ADMIN_POD -- curl -s http://localhost:8001/status | head -20

echo ""
echo "=========================================="
echo "Kong API Gateway deployment complete!"
echo "=========================================="
echo ""
echo "Kong services:"
kubectl get svc -n kong -l app.kubernetes.io/name=kong
echo ""
echo "Kong Admin API: http://localhost:8001 (use 'kubectl port-forward -n kong svc/kong-kong-admin 8001:8001')"
echo "Kong Proxy: Access via LoadBalancer (use 'minikube service -n kong kong-kong-proxy --url')"
echo ""
echo "Next steps:"
echo "1. Run './infrastructure/scripts/deploy-dapr.sh' to deploy Dapr service mesh"
echo ""
