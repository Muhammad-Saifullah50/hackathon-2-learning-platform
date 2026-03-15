#!/bin/bash
set -e

echo "=========================================="
echo "Deploying PostgreSQL for Kong"
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

# Create Kong namespace
echo "Creating Kong namespace..."
kubectl create namespace kong --dry-run=client -o yaml | kubectl apply -f -

# Check if PostgreSQL is already deployed
if helm list -n kong | grep -q "^kong-postgresql"; then
    echo "PostgreSQL for Kong is already deployed"
    echo "To upgrade: helm upgrade kong-postgresql bitnami/postgresql --set auth.username=kong --set auth.password=kong --set auth.database=kong -n kong"
    exit 0
fi

# Deploy PostgreSQL
echo ""
echo "Deploying PostgreSQL for Kong..."
helm install kong-postgresql bitnami/postgresql \
  --set auth.username=kong \
  --set auth.password=kong \
  --set auth.database=kong \
  --set primary.persistence.size=1Gi \
  --set primary.resources.limits.cpu=500m \
  --set primary.resources.limits.memory=512Mi \
  --set primary.resources.requests.cpu=250m \
  --set primary.resources.requests.memory=256Mi \
  -n kong \
  --wait \
  --timeout 5m

# Verify deployment
echo ""
echo "Verifying PostgreSQL deployment..."
kubectl get pods -l app.kubernetes.io/name=postgresql -n kong
kubectl get svc -l app.kubernetes.io/name=postgresql -n kong

echo ""
echo "Testing PostgreSQL connection..."
kubectl run postgresql-client --rm -it --restart=Never \
  --namespace kong \
  --image=bitnami/postgresql:15 \
  --env="PGPASSWORD=kong" \
  --command -- psql -h kong-postgresql.kong.svc.cluster.local -U kong -d kong -c "SELECT version();" || true

echo ""
echo "=========================================="
echo "PostgreSQL deployment complete!"
echo "=========================================="
echo ""
echo "PostgreSQL connection details:"
echo "  Host: kong-postgresql.kong.svc.cluster.local"
echo "  Port: 5432"
echo "  Database: kong"
echo "  Username: kong"
echo "  Password: kong"
echo ""
echo "Next steps:"
echo "1. Run './infrastructure/scripts/deploy-kong.sh' to deploy Kong API Gateway"
echo ""
