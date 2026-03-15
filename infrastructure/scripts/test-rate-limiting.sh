#!/bin/bash
set -e

echo "=========================================="
echo "Testing Kong Rate Limiting"
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

# Get Kong proxy URL
echo "Getting Kong proxy URL..."
KONG_PROXY_POD=$(kubectl get pods -n kong -l app.kubernetes.io/name=kong -o jsonpath='{.items[0].metadata.name}')

# Port-forward Kong proxy
echo "Setting up port-forward to Kong proxy..."
kubectl port-forward -n kong "$KONG_PROXY_POD" 8000:8000 &
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

# Test rate limiting by sending multiple requests
echo ""
echo "=========================================="
echo "Test: Sending 11 requests in 1 minute"
echo "=========================================="
echo ""
echo "Expected: First 10 requests succeed, 11th request returns 429 (Too Many Requests)"
echo ""

# Note: This test requires a valid JWT token
# For now, we'll test the endpoint without authentication to verify Kong is responding
echo "Testing Kong proxy endpoint..."

for i in {1..11}; do
    echo "Request $i:"
    RESPONSE=$(curl -s -w "\nHTTP Status: %{http_code}\n" http://localhost:8000/api/auth/login 2>&1 || echo "Request failed")
    echo "$RESPONSE"
    echo ""
    sleep 1
done

echo ""
echo "=========================================="
echo "Rate Limiting Test Complete!"
echo "=========================================="
echo ""
echo "Note: To fully test rate limiting with authentication:"
echo "1. Obtain a valid JWT token from auth-service"
echo "2. Send 11 authenticated requests to a protected endpoint"
echo "3. Verify the 11th request returns 429 Too Many Requests"
echo ""
