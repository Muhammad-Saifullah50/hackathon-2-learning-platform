#!/bin/bash
set -e

echo "=========================================="
echo "Verifying Kong Configuration"
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

# Get Kong Admin API URL
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

# Check Kong status
echo ""
echo "Checking Kong status..."
curl -s http://localhost:8001/status | jq '.'

# List services
echo ""
echo "=========================================="
echo "Kong Services:"
echo "=========================================="
curl -s http://localhost:8001/services | jq '.data[] | {name: .name, url: .url, tags: .tags}'

# List routes
echo ""
echo "=========================================="
echo "Kong Routes:"
echo "=========================================="
curl -s http://localhost:8001/routes | jq '.data[] | {name: .name, paths: .paths, methods: .methods, service: .service.name}'

# List plugins
echo ""
echo "=========================================="
echo "Kong Plugins:"
echo "=========================================="
curl -s http://localhost:8001/plugins | jq '.data[] | {name: .name, enabled: .enabled, service: .service.name, route: .route.name}'

# List consumers
echo ""
echo "=========================================="
echo "Kong Consumers:"
echo "=========================================="
curl -s http://localhost:8001/consumers | jq '.data[] | {username: .username, custom_id: .custom_id}'

# List JWT credentials
echo ""
echo "=========================================="
echo "JWT Credentials:"
echo "=========================================="
curl -s http://localhost:8001/consumers/learnflow-auth/jwt | jq '.data[] | {key: .key, algorithm: .algorithm}'

# List upstreams
echo ""
echo "=========================================="
echo "Kong Upstreams:"
echo "=========================================="
curl -s http://localhost:8001/upstreams | jq '.data[] | {name: .name, algorithm: .algorithm}'

echo ""
echo "=========================================="
echo "Kong verification complete!"
echo "=========================================="
