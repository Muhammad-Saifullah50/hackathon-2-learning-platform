#!/bin/bash
set -e

echo "=========================================="
echo "Comprehensive Kong Gateway Test"
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

# Get Kong pods
KONG_ADMIN_POD=$(kubectl get pods -n kong -l app.kubernetes.io/name=kong -o jsonpath='{.items[0].metadata.name}')
echo "Using Kong pod: $KONG_ADMIN_POD"

# Port-forward Kong Admin API and Proxy
echo ""
echo "Setting up port-forwards..."
kubectl port-forward -n kong "$KONG_ADMIN_POD" 8001:8001 &
ADMIN_PID=$!
kubectl port-forward -n kong "$KONG_ADMIN_POD" 8000:8000 &
PROXY_PID=$!

# Wait for port-forwards
sleep 3

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up port-forwards..."
    kill $ADMIN_PID 2>/dev/null || true
    kill $PROXY_PID 2>/dev/null || true
}
trap cleanup EXIT

# Test 1: Kong Status
echo ""
echo "=========================================="
echo "Test 1: Kong Status"
echo "=========================================="
STATUS=$(curl -s http://localhost:8001/status)
echo "$STATUS" | jq '.'

if echo "$STATUS" | jq -e '.database.reachable == true' > /dev/null; then
    echo "✓ Database reachable"
else
    echo "✗ Database not reachable"
fi

# Test 2: List Services
echo ""
echo "=========================================="
echo "Test 2: Kong Services"
echo "=========================================="
SERVICES=$(curl -s http://localhost:8001/services)
SERVICE_COUNT=$(echo "$SERVICES" | jq '.data | length')
echo "Total services: $SERVICE_COUNT"
echo "$SERVICES" | jq '.data[] | {name: .name, url: .url}'

# Test 3: List Routes
echo ""
echo "=========================================="
echo "Test 3: Kong Routes"
echo "=========================================="
ROUTES=$(curl -s http://localhost:8001/routes)
ROUTE_COUNT=$(echo "$ROUTES" | jq '.data | length')
echo "Total routes: $ROUTE_COUNT"
echo "$ROUTES" | jq '.data[] | {name: .name, paths: .paths, service: .service.name}'

# Test 4: List Plugins
echo ""
echo "=========================================="
echo "Test 4: Kong Plugins"
echo "=========================================="
PLUGINS=$(curl -s http://localhost:8001/plugins)
PLUGIN_COUNT=$(echo "$PLUGINS" | jq '.data | length')
echo "Total plugins: $PLUGIN_COUNT"
echo "$PLUGINS" | jq '.data[] | {name: .name, enabled: .enabled}'

# Test 5: Test Public Route (no auth)
echo ""
echo "=========================================="
echo "Test 5: Public Route (No Auth)"
echo "=========================================="
echo "Testing /api/auth/login (should return 404 - service not deployed yet)"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/auth/login)
echo "$RESPONSE"

# Test 6: Test Protected Route (no auth - should fail)
echo ""
echo "=========================================="
echo "Test 6: Protected Route (No Auth - Should Fail)"
echo "=========================================="
echo "Testing /api/users/me without token (should return 401)"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/users/me)
echo "$RESPONSE"

if echo "$RESPONSE" | grep -q "HTTP_CODE:401"; then
    echo "✓ JWT authentication working (401 returned)"
else
    echo "✗ JWT authentication not working"
fi

# Test 7: Test CORS
echo ""
echo "=========================================="
echo "Test 7: CORS Headers"
echo "=========================================="
echo "Testing CORS preflight request"
CORS_RESPONSE=$(curl -s -X OPTIONS http://localhost:8000/api/auth/login \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    -i)
echo "$CORS_RESPONSE"

if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
    echo "✓ CORS headers present"
else
    echo "✗ CORS headers missing"
fi

# Test 8: Test Rate Limiting Headers
echo ""
echo "=========================================="
echo "Test 8: Rate Limiting Headers"
echo "=========================================="
echo "Testing rate limit headers on public endpoint"
RATE_RESPONSE=$(curl -s -i http://localhost:8000/api/auth/login | head -20)
echo "$RATE_RESPONSE"

# Test 9: Check Upstreams
echo ""
echo "=========================================="
echo "Test 9: Kong Upstreams"
echo "=========================================="
UPSTREAMS=$(curl -s http://localhost:8001/upstreams)
UPSTREAM_COUNT=$(echo "$UPSTREAMS" | jq '.data | length')
echo "Total upstreams: $UPSTREAM_COUNT"
echo "$UPSTREAMS" | jq '.data[] | {name: .name, algorithm: .algorithm}'

# Test 10: Check Consumers
echo ""
echo "=========================================="
echo "Test 10: Kong Consumers"
echo "=========================================="
CONSUMERS=$(curl -s http://localhost:8001/consumers)
CONSUMER_COUNT=$(echo "$CONSUMERS" | jq '.data | length')
echo "Total consumers: $CONSUMER_COUNT"
echo "$CONSUMERS" | jq '.data[] | {username: .username, custom_id: .custom_id}'

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Services: $SERVICE_COUNT"
echo "Routes: $ROUTE_COUNT"
echo "Plugins: $PLUGIN_COUNT"
echo "Upstreams: $UPSTREAM_COUNT"
echo "Consumers: $CONSUMER_COUNT"
echo ""
echo "✓ Kong Gateway tests complete!"
echo ""
echo "Note: Full authentication testing requires:"
echo "1. Backend services deployed"
echo "2. Valid JWT token from auth-service"
echo ""
