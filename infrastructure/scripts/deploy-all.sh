#!/bin/bash
set -e

echo "=========================================="
echo "LearnFlow Infrastructure Deployment"
echo "=========================================="
echo ""
echo "This script will deploy the complete infrastructure stack:"
echo "  1. Minikube cluster"
echo "  2. Redis (shared infrastructure)"
echo "  3. PostgreSQL for Kong"
echo "  4. Kong API Gateway"
echo "  5. Dapr service mesh"
echo "  6. Dapr components and configuration"
echo "  7. JWT public key secret"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Setup Minikube
echo ""
echo "=========================================="
echo "Step 1/7: Setting up Minikube cluster"
echo "=========================================="
"$SCRIPT_DIR/setup-minikube.sh"

# Step 2: Deploy Redis
echo ""
echo "=========================================="
echo "Step 2/7: Deploying Redis"
echo "=========================================="
"$SCRIPT_DIR/deploy-redis.sh"

# Step 3: Deploy PostgreSQL for Kong
echo ""
echo "=========================================="
echo "Step 3/7: Deploying PostgreSQL for Kong"
echo "=========================================="
"$SCRIPT_DIR/deploy-kong-postgres.sh"

# Step 4: Deploy Kong
echo ""
echo "=========================================="
echo "Step 4/7: Deploying Kong API Gateway"
echo "=========================================="
"$SCRIPT_DIR/deploy-kong.sh"

# Step 5: Deploy Dapr
echo ""
echo "=========================================="
echo "Step 5/7: Deploying Dapr service mesh"
echo "=========================================="
"$SCRIPT_DIR/deploy-dapr.sh"

# Step 6: Apply Dapr configuration
echo ""
echo "=========================================="
echo "Step 6/7: Applying Dapr configuration"
echo "=========================================="
echo "Applying Dapr components..."
kubectl apply -f "$SCRIPT_DIR/../kubernetes/dapr/components.yaml"

echo ""
echo "Applying Dapr configuration..."
kubectl apply -f "$SCRIPT_DIR/../kubernetes/dapr/configuration.yaml"

echo ""
echo "Applying Dapr resiliency policies..."
kubectl apply -f "$SCRIPT_DIR/../kubernetes/dapr/resiliency-full.yaml"

echo ""
echo "Verifying Dapr components..."
kubectl get components -n default
kubectl get configurations -n default

# Step 7: Create JWT secret
echo ""
echo "=========================================="
echo "Step 7/9: Creating JWT public key secret"
echo "=========================================="
"$SCRIPT_DIR/create-jwt-secret.sh"

# Step 8: Update Kong configuration with JWT key
echo ""
echo "=========================================="
echo "Step 8/9: Updating Kong configuration with JWT key"
echo "=========================================="
"$SCRIPT_DIR/update-kong-jwt-key.sh"

# Step 9: Sync Kong configuration
echo ""
echo "=========================================="
echo "Step 9/9: Syncing Kong configuration"
echo "=========================================="
"$SCRIPT_DIR/sync-kong-config.sh"

# Verify Kong configuration
echo ""
echo "Verifying Kong configuration..."
"$SCRIPT_DIR/verify-kong.sh"

# Step 10: Deploy services
echo ""
echo "=========================================="
echo "Step 10/11: Deploying microservices"
echo "=========================================="
"$SCRIPT_DIR/deploy-services.sh"

# Step 11: Test service invocation
echo ""
echo "=========================================="
echo "Step 11/13: Testing Dapr service invocation"
echo "=========================================="
"$SCRIPT_DIR/test-service-invocation.sh"

# Step 12: Deploy Dapr subscriptions
echo ""
echo "=========================================="
echo "Step 12/13: Deploying Dapr subscriptions"
echo "=========================================="
"$SCRIPT_DIR/deploy-dapr-subscriptions.sh"

# Step 13: Test pub/sub
echo ""
echo "=========================================="
echo "Step 13/15: Testing Dapr pub/sub"
echo "=========================================="
"$SCRIPT_DIR/test-pubsub.sh"

# Step 14: Verify Kong health checks
echo ""
echo "=========================================="
echo "Step 14/15: Verifying Kong health checks"
echo "=========================================="
"$SCRIPT_DIR/verify-health-checks.sh"

# Step 15: Verify Dapr health
echo ""
echo "=========================================="
echo "Step 15/15: Verifying Dapr health"
echo "=========================================="
"$SCRIPT_DIR/verify-dapr-health.sh"

# Summary
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Infrastructure Status:"
echo ""
echo "Minikube:"
kubectl get nodes
echo ""
echo "Redis:"
kubectl get pods -l app.kubernetes.io/name=redis -n default
echo ""
echo "Kong:"
kubectl get pods -n kong -l app.kubernetes.io/name=kong
echo ""
echo "Dapr:"
kubectl get pods -n dapr-system
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Start minikube tunnel in a separate terminal:"
echo "   minikube tunnel"
echo ""
echo "2. Deploy backend services with Dapr sidecars:"
echo "   ./infrastructure/scripts/deploy-services.sh"
echo ""
echo "3. Configure Kong routes and plugins:"
echo "   ./infrastructure/scripts/sync-kong-config.sh"
echo ""
echo "4. Test the setup:"
echo "   ./infrastructure/scripts/test-gateway.sh"
echo "   ./infrastructure/scripts/test-service-mesh.sh"
echo ""
