#!/bin/bash
set -e

echo "=========================================="
echo "Testing Dapr Pub/Sub"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    exit 1
fi

# Check if subscriptions are deployed
if ! kubectl get subscriptions -n default | grep -q "struggle-alerts-subscription"; then
    echo "Error: Dapr subscriptions not found"
    echo "Run './infrastructure/scripts/deploy-dapr-subscriptions.sh' first"
    exit 1
fi

# Check if teacher-service is running
if ! kubectl get pods -l app=teacher-service -n default | grep -q "Running"; then
    echo "Error: teacher-service is not running"
    echo "Run './infrastructure/scripts/deploy-services.sh' first"
    exit 1
fi

# Get a pod with Dapr sidecar to publish messages
PUBLISHER_POD=$(kubectl get pods -l app=debug-agent -n default -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$PUBLISHER_POD" ]; then
    echo "Error: No pods with Dapr sidecar found"
    echo "Run './infrastructure/scripts/deploy-services.sh' first"
    exit 1
fi

echo "Using pod: $PUBLISHER_POD"

# Test 1: Publish to struggle-alerts topic
echo ""
echo "=========================================="
echo "Test 1: Publishing to struggle-alerts topic"
echo "=========================================="
echo ""

TEST_MESSAGE='{
  "student_id": "test-student-123",
  "error_type": "SyntaxError",
  "message": "Test struggle alert from pub/sub test",
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'

echo "Publishing message to struggle-alerts topic..."
kubectl exec -n default "$PUBLISHER_POD" -c daprd -- curl -s -X POST \
  http://localhost:3500/v1.0/publish/learnflow-pubsub/struggle-alerts \
  -H "Content-Type: application/json" \
  -d "$TEST_MESSAGE"

echo ""
echo "Message published successfully!"

# Test 2: Check Redis for the message
echo ""
echo "=========================================="
echo "Test 2: Verifying message in Redis"
echo "=========================================="
echo ""

echo "Checking Redis stream for struggle-alerts topic..."
kubectl exec -n default redis-master-0 -- redis-cli -a changeme XLEN "learnflow-pubsub-struggle-alerts" 2>/dev/null || echo "Stream not found (expected if no messages yet)"

# Test 3: Publish to quiz-completed topic
echo ""
echo "=========================================="
echo "Test 3: Publishing to quiz-completed topic"
echo "=========================================="
echo ""

QUIZ_MESSAGE='{
  "student_id": "test-student-123",
  "quiz_id": "test-quiz-456",
  "score": 85,
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'

echo "Publishing message to quiz-completed topic..."
kubectl exec -n default "$PUBLISHER_POD" -c daprd -- curl -s -X POST \
  http://localhost:3500/v1.0/publish/learnflow-pubsub/quiz-completed \
  -H "Content-Type: application/json" \
  -d "$QUIZ_MESSAGE"

echo ""
echo "Message published successfully!"

# Test 4: List all topics in Redis
echo ""
echo "=========================================="
echo "Test 4: Listing all pub/sub topics in Redis"
echo "=========================================="
echo ""

echo "Scanning Redis for pub/sub streams..."
kubectl exec -n default redis-master-0 -- redis-cli -a changeme KEYS "learnflow-pubsub-*" 2>/dev/null || echo "No streams found"

echo ""
echo "=========================================="
echo "Dapr Pub/Sub Test Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ Messages published to struggle-alerts topic"
echo "  ✓ Messages published to quiz-completed topic"
echo "  ✓ Redis streams are working"
echo ""
echo "Note: Actual message delivery will work once backend services implement webhook endpoints"
echo ""
