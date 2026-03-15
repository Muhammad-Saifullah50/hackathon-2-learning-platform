#!/bin/bash
set -e

echo "=========================================="
echo "Deploying Dapr Service Mesh"
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

# Add Dapr Helm repository
echo "Adding Dapr Helm repository..."
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Create Dapr namespace
echo ""
echo "Creating dapr-system namespace..."
kubectl create namespace dapr-system --dry-run=client -o yaml | kubectl apply -f -

# Check if Dapr is already deployed
if helm list -n dapr-system | grep -q "^dapr"; then
    echo "Dapr is already deployed"
    echo "To upgrade: helm upgrade dapr dapr/dapr -n dapr-system"
    exit 0
fi

# Deploy Dapr
echo ""
echo "Deploying Dapr service mesh..."
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --set global.logAsJson=true \
  --set global.ha.enabled=false \
  --wait \
  --timeout 5m

# Wait for Dapr components to be ready
echo ""
echo "Waiting for Dapr components to be ready..."
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dapr-sidecar-injector -n dapr-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dapr-sentry -n dapr-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dapr-placement-server -n dapr-system --timeout=300s

# Verify deployment
echo ""
echo "Verifying Dapr deployment..."
kubectl get pods -n dapr-system
kubectl get svc -n dapr-system

echo ""
echo "=========================================="
echo "Dapr service mesh deployment complete!"
echo "=========================================="
echo ""
echo "Dapr components:"
kubectl get pods -n dapr-system -o wide
echo ""
echo "Next steps:"
echo "1. Run 'kubectl apply -f infrastructure/kubernetes/dapr/config.yaml' to apply Dapr configuration"
echo "2. Run 'kubectl apply -f infrastructure/kubernetes/dapr/resiliency.yaml' to apply resiliency policies"
echo ""
