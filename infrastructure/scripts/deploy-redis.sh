#!/bin/bash
set -e

echo "=========================================="
echo "Deploying Redis for LearnFlow"
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

# Add Bitnami Helm repository
echo "Adding Bitnami Helm repository..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Check if Redis is already deployed
if helm list -n default | grep -q "^redis"; then
    echo "Redis is already deployed"
    echo "To upgrade: helm upgrade redis bitnami/redis -f infrastructure/kubernetes/redis/values.yaml -n default"
    exit 0
fi

# Deploy Redis
echo ""
echo "Deploying Redis..."
helm install redis bitnami/redis \
  -f infrastructure/kubernetes/redis/values.yaml \
  -n default \
  --create-namespace \
  --wait \
  --timeout 5m

# Create Redis secret for Dapr
echo ""
echo "Creating Redis secret for Dapr..."
kubectl create secret generic redis-secret \
  --from-literal=password=changeme \
  -n default \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify deployment
echo ""
echo "Verifying Redis deployment..."
kubectl get pods -l app.kubernetes.io/name=redis -n default
kubectl get svc -l app.kubernetes.io/name=redis -n default

echo ""
echo "Testing Redis connection..."
kubectl run redis-client --rm -it --restart=Never \
  --image=redis:7.2 \
  --command -- redis-cli -h redis-master.default.svc.cluster.local -a changeme ping || true

echo ""
echo "=========================================="
echo "Redis deployment complete!"
echo "=========================================="
echo ""
echo "Redis connection details:"
echo "  Host: redis-master.default.svc.cluster.local"
echo "  Port: 6379"
echo "  Password: changeme"
echo ""
echo "Next steps:"
echo "1. Run './infrastructure/scripts/deploy-kong-postgres.sh' to deploy PostgreSQL for Kong"
echo ""
