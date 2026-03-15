#!/bin/bash
set -e

echo "=========================================="
echo "LearnFlow Infrastructure Teardown"
echo "=========================================="
echo ""
echo "This script will delete ALL infrastructure components:"
echo "  - All microservices"
echo "  - Dapr service mesh"
echo "  - Kong API Gateway"
echo "  - PostgreSQL (Kong database)"
echo "  - Redis"
echo "  - Minikube cluster (optional)"
echo ""
read -p "Are you sure you want to proceed? (yes/no) " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Teardown cancelled"
    exit 0
fi

# Step 1: Delete microservices
echo ""
echo "=========================================="
echo "Step 1: Deleting microservices"
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
    if kubectl get deployment "$service" -n default &> /dev/null; then
        echo "Deleting $service..."
        kubectl delete -f "infrastructure/kubernetes/services/${service}.yaml" --ignore-not-found=true
    fi
done

# Step 2: Delete Dapr subscriptions
echo ""
echo "=========================================="
echo "Step 2: Deleting Dapr subscriptions"
echo "=========================================="
kubectl delete -f infrastructure/kubernetes/dapr/subscriptions.yaml --ignore-not-found=true

# Step 3: Delete Dapr configuration
echo ""
echo "=========================================="
echo "Step 3: Deleting Dapr configuration"
echo "=========================================="
kubectl delete -f infrastructure/kubernetes/dapr/resiliency-full.yaml --ignore-not-found=true
kubectl delete -f infrastructure/kubernetes/dapr/configuration.yaml --ignore-not-found=true
kubectl delete -f infrastructure/kubernetes/dapr/components.yaml --ignore-not-found=true

# Step 4: Uninstall Dapr
echo ""
echo "=========================================="
echo "Step 4: Uninstalling Dapr"
echo "=========================================="
if helm list -n dapr-system | grep -q "^dapr"; then
    helm uninstall dapr -n dapr-system
    echo "Waiting for Dapr pods to terminate..."
    kubectl wait --for=delete pod -l app=dapr-operator -n dapr-system --timeout=60s || true
fi

# Delete Dapr namespace
kubectl delete namespace dapr-system --ignore-not-found=true

# Step 5: Delete Kong secrets
echo ""
echo "=========================================="
echo "Step 5: Deleting Kong secrets"
echo "=========================================="
kubectl delete secret kong-jwt-public-key -n kong --ignore-not-found=true

# Step 6: Uninstall Kong
echo ""
echo "=========================================="
echo "Step 6: Uninstalling Kong"
echo "=========================================="
if helm list -n kong | grep -q "^kong"; then
    helm uninstall kong -n kong
    echo "Waiting for Kong pods to terminate..."
    kubectl wait --for=delete pod -l app.kubernetes.io/name=kong -n kong --timeout=60s || true
fi

# Step 7: Uninstall Kong PostgreSQL
echo ""
echo "=========================================="
echo "Step 7: Uninstalling Kong PostgreSQL"
echo "=========================================="
if helm list -n kong | grep -q "^kong-postgresql"; then
    helm uninstall kong-postgresql -n kong
    echo "Waiting for PostgreSQL pods to terminate..."
    kubectl wait --for=delete pod -l app.kubernetes.io/name=postgresql -n kong --timeout=60s || true
fi

# Delete Kong namespace
kubectl delete namespace kong --ignore-not-found=true

# Step 8: Delete Redis secret
echo ""
echo "=========================================="
echo "Step 8: Deleting Redis secret"
echo "=========================================="
kubectl delete secret redis-secret -n default --ignore-not-found=true

# Step 9: Uninstall Redis
echo ""
echo "=========================================="
echo "Step 9: Uninstalling Redis"
echo "=========================================="
if helm list -n default | grep -q "^redis"; then
    helm uninstall redis -n default
    echo "Waiting for Redis pods to terminate..."
    kubectl wait --for=delete pod -l app.kubernetes.io/name=redis -n default --timeout=60s || true
fi

# Step 10: Delete persistent volume claims
echo ""
echo "=========================================="
echo "Step 10: Deleting persistent volume claims"
echo "=========================================="
kubectl delete pvc --all -n default --ignore-not-found=true
kubectl delete pvc --all -n kong --ignore-not-found=true

# Step 11: Verify cleanup
echo ""
echo "=========================================="
echo "Step 11: Verifying cleanup"
echo "=========================================="
echo ""
echo "Remaining pods in default namespace:"
kubectl get pods -n default || echo "No pods found"
echo ""
echo "Remaining pods in kong namespace:"
kubectl get pods -n kong 2>/dev/null || echo "Namespace not found (expected)"
echo ""
echo "Remaining pods in dapr-system namespace:"
kubectl get pods -n dapr-system 2>/dev/null || echo "Namespace not found (expected)"

# Step 12: Optional - Delete Minikube cluster
echo ""
echo "=========================================="
echo "Step 12: Delete Minikube cluster (optional)"
echo "=========================================="
echo ""
read -p "Do you want to delete the Minikube cluster? (yes/no) " -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Stopping Minikube..."
    minikube stop || true
    echo "Deleting Minikube cluster..."
    minikube delete
    echo "✓ Minikube cluster deleted"
else
    echo "Minikube cluster preserved"
fi

# Summary
echo ""
echo "=========================================="
echo "Teardown Complete!"
echo "=========================================="
echo ""
echo "Deleted components:"
echo "  ✓ All microservices"
echo "  ✓ Dapr service mesh"
echo "  ✓ Kong API Gateway"
echo "  ✓ PostgreSQL (Kong database)"
echo "  ✓ Redis"
echo "  ✓ All persistent volume claims"
echo ""
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "  ✓ Minikube cluster"
else
    echo "  - Minikube cluster (preserved)"
fi
echo ""
echo "To redeploy, run: ./infrastructure/scripts/deploy-all.sh"
echo ""
