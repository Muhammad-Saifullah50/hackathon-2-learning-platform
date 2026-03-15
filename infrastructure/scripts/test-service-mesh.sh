#!/bin/bash
set -e

echo "=========================================="
echo "Comprehensive Dapr Service Mesh Test"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    exit 1
fi

# Check if Dapr is running
if ! kubectl get pods -n dapr-system -l app=dapr-operator | grep -q "Running"; then
    echo "Error: Dapr is not running"
    exit 1
fi

# Test 1: Dapr System Components
echo ""
echo "=========================================="
echo "Test 1: Dapr System Components"
echo "=========================================="
kubectl get pods -n dapr-system

OPERATOR_STATUS=$(kubectl get pods -n dapr-system -l app=dapr-operator -o jsonpath='{.items[0].status.phase}')
INJECTOR_STATUS=$(kubectl get pods -n dapr-system -l app=dapr-sidecar-injector -o jsonpath='{.items[0].status.phase}')
SENTRY_STATUS=$(kubectl get pods -n dapr-system -l app=dapr-sentry -o jsonpath='{.items[0].status.phase}')
PLACEMENT_STATUS=$(kubectl get pods -n dapr-system -l app=dapr-placement-server -o jsonpath='{.items[0].status.phase}')

echo ""
if [ "$OPERATOR_STATUS" = "Running" ]; then
    echo "✓ Dapr Operator: Running"
else
    echo "✗ Dapr Operator: $OPERATOR_STATUS"
fi

if [ "$INJECTOR_STATUS" = "Running" ]; then
    echo "✓ Dapr Sidecar Injector: Running"
else
    echo "✗ Dapr Sidecar Injector: $INJECTOR_STATUS"
fi

if [ "$SENTRY_STATUS" = "Running" ]; then
    echo "✓ Dapr Sentry: Running"
else
    echo "✗ Dapr Sentry: $SENTRY_STATUS"
fi

if [ "$PLACEMENT_STATUS" = "Running" ]; then
    echo "✓ Dapr Placement: Running"
else
    echo "✗ Dapr Placement: $PLACEMENT_STATUS"
fi

# Test 2: Dapr Components
echo ""
echo "=========================================="
echo "Test 2: Dapr Components"
echo "=========================================="
kubectl get components -n default

COMPONENTS=$(kubectl get components -n default -o json)
COMPONENT_COUNT=$(echo "$COMPONENTS" | jq '.items | length')
echo ""
echo "Total components: $COMPONENT_COUNT"
echo "$COMPONENTS" | jq -r '.items[] | "\(.metadata.name) (\(.spec.type))"'

# Test 3: Dapr Configurations
echo ""
echo "=========================================="
echo "Test 3: Dapr Configurations"
echo "=========================================="
kubectl get configurations -n default

# Test 4: Dapr Subscriptions
echo ""
echo "=========================================="
echo "Test 4: Dapr Subscriptions"
echo "=========================================="
kubectl get subscriptions -n default

SUBSCRIPTIONS=$(kubectl get subscriptions -n default -o json)
SUBSCRIPTION_COUNT=$(echo "$SUBSCRIPTIONS" | jq '.items | length')
echo ""
echo "Total subscriptions: $SUBSCRIPTION_COUNT"
echo "$SUBSCRIPTIONS" | jq -r '.items[] | "\(.metadata.name) -> \(.spec.topic) (\(.spec.scopes | join(", ")))"'

# Test 5: Service Sidecar Injection
echo ""
echo "=========================================="
echo "Test 5: Dapr Sidecar Injection"
echo "=========================================="

SERVICES=(
    "auth-service"
    "user-service"
    "triage-agent"
    "concepts-agent"
)

INJECTED=0
NOT_INJECTED=0

for service in "${SERVICES[@]}"; do
    POD=$(kubectl get pods -l app="$service" -n default -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

    if [ -z "$POD" ]; then
        echo "$service: NOT DEPLOYED"
        continue
    fi

    CONTAINERS=$(kubectl get pod "$POD" -n default -o jsonpath='{.spec.containers[*].name}')

    if echo "$CONTAINERS" | grep -q "daprd"; then
        echo "✓ $service: Dapr sidecar injected"
        ((INJECTED++))
    else
        echo "✗ $service: Dapr sidecar NOT injected"
        ((NOT_INJECTED++))
    fi
done

echo ""
echo "Sidecar injection summary: $INJECTED injected, $NOT_INJECTED not injected"

# Test 6: Dapr Health Checks
echo ""
echo "=========================================="
echo "Test 6: Dapr Sidecar Health"
echo "=========================================="

TEST_POD=$(kubectl get pods -l app=triage-agent -n default -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$TEST_POD" ]; then
    echo "Testing Dapr health on pod: $TEST_POD"
    HEALTH=$(kubectl exec -n default "$TEST_POD" -c daprd -- curl -s http://localhost:3500/v1.0/healthz 2>/dev/null || echo "failed")

    if [ "$HEALTH" = "true" ]; then
        echo "✓ Dapr sidecar healthy"
    else
        echo "✗ Dapr sidecar unhealthy: $HEALTH"
    fi
else
    echo "⚠ No pods available for health check"
fi

# Test 7: Service Invocation
echo ""
echo "=========================================="
echo "Test 7: Service Invocation"
echo "=========================================="

if [ -n "$TEST_POD" ]; then
    echo "Testing service invocation from $TEST_POD"

    # Get Dapr metadata
    echo ""
    echo "Dapr metadata:"
    kubectl exec -n default "$TEST_POD" -c daprd -- curl -s http://localhost:3500/v1.0/metadata | jq '{id: .id, components: [.components[] | .name]}'

    # Test invocation (will fail if service not deployed, but tests the mechanism)
    echo ""
    echo "Testing invocation to concepts-agent (may fail if service not deployed):"
    kubectl exec -n default "$TEST_POD" -c daprd -- curl -s -w "\nHTTP_CODE:%{http_code}\n" \
        http://localhost:3500/v1.0/invoke/concepts-agent/method/health 2>/dev/null || echo "Invocation failed (expected if services not deployed)"
else
    echo "⚠ No pods available for service invocation test"
fi

# Test 8: Pub/Sub
echo ""
echo "=========================================="
echo "Test 8: Pub/Sub Messaging"
echo "=========================================="

if [ -n "$TEST_POD" ]; then
    echo "Publishing test message to struggle-alerts topic"

    TEST_MESSAGE='{
      "student_id": "test-123",
      "error_type": "TestError",
      "message": "Test message from service mesh test",
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    }'

    PUBLISH_RESULT=$(kubectl exec -n default "$TEST_POD" -c daprd -- curl -s -w "\nHTTP_CODE:%{http_code}\n" \
        -X POST http://localhost:3500/v1.0/publish/learnflow-pubsub/struggle-alerts \
        -H "Content-Type: application/json" \
        -d "$TEST_MESSAGE" 2>/dev/null || echo "Publish failed")

    if echo "$PUBLISH_RESULT" | grep -q "HTTP_CODE:204"; then
        echo "✓ Message published successfully"
    else
        echo "✗ Message publish failed"
        echo "$PUBLISH_RESULT"
    fi

    # Check Redis for the message
    echo ""
    echo "Checking Redis for published message:"
    kubectl exec -n default redis-master-0 -- redis-cli -a changeme XLEN "learnflow-pubsub-struggle-alerts" 2>/dev/null || echo "Stream not found"
else
    echo "⚠ No pods available for pub/sub test"
fi

# Test 9: State Store
echo ""
echo "=========================================="
echo "Test 9: State Store"
echo "=========================================="

if [ -n "$TEST_POD" ]; then
    echo "Testing state store operations"

    # Save state
    echo "Saving state..."
    kubectl exec -n default "$TEST_POD" -c daprd -- curl -s -X POST \
        http://localhost:3500/v1.0/state/learnflow-statestore \
        -H "Content-Type: application/json" \
        -d '[{"key": "test-key", "value": "test-value"}]' 2>/dev/null || echo "Save failed"

    # Get state
    echo "Retrieving state..."
    STATE_VALUE=$(kubectl exec -n default "$TEST_POD" -c daprd -- curl -s \
        http://localhost:3500/v1.0/state/learnflow-statestore/test-key 2>/dev/null || echo "Get failed")

    if [ "$STATE_VALUE" = "test-value" ]; then
        echo "✓ State store working"
    else
        echo "✗ State store not working: $STATE_VALUE"
    fi

    # Delete state
    echo "Deleting state..."
    kubectl exec -n default "$TEST_POD" -c daprd -- curl -s -X DELETE \
        http://localhost:3500/v1.0/state/learnflow-statestore/test-key 2>/dev/null || echo "Delete failed"
else
    echo "⚠ No pods available for state store test"
fi

# Test 10: Resiliency Policies
echo ""
echo "=========================================="
echo "Test 10: Resiliency Policies"
echo "=========================================="

RESILIENCY=$(kubectl get resiliency -n default -o json 2>/dev/null || echo '{"items":[]}')
RESILIENCY_COUNT=$(echo "$RESILIENCY" | jq '.items | length')

if [ "$RESILIENCY_COUNT" -gt 0 ]; then
    echo "✓ Resiliency policies configured: $RESILIENCY_COUNT"
    echo "$RESILIENCY" | jq -r '.items[] | .metadata.name'
else
    echo "⚠ No resiliency policies found"
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Dapr System Components: 4/4 expected"
echo "Dapr Components: $COMPONENT_COUNT"
echo "Dapr Subscriptions: $SUBSCRIPTION_COUNT"
echo "Sidecars Injected: $INJECTED"
echo "Resiliency Policies: $RESILIENCY_COUNT"
echo ""
echo "✓ Dapr Service Mesh tests complete!"
echo ""
echo "Note: Full service invocation testing requires backend services deployed"
echo ""
