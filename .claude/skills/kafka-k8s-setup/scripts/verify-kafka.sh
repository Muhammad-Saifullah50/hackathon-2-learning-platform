#!/usr/bin/env bash
# verify-kafka.sh — Smoke-test a Kafka cluster on Kubernetes
# Usage: bash verify-kafka.sh [--namespace <ns>] [--topic <name>] [--timeout <s>] [--help]

set -euo pipefail

# ── Defaults ──
NAMESPACE="kafka"
TEST_TOPIC="smoke-test"
TIMEOUT=120

# ── Color helpers ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[ OK ]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
divider() { echo ""; echo -e "${BLUE}──────────────────────────────────────────────────────────────${NC}"; echo -e "  ${BLUE}$1${NC}"; echo -e "${BLUE}──────────────────────────────────────────────────────────────${NC}"; }

usage() {
  cat <<'USAGE'
Usage: bash verify-kafka.sh [OPTIONS]

Options:
  --namespace <ns>    Target namespace (default: kafka)
  --topic <name>      Test topic name (default: smoke-test)
  --timeout <s>       Timeout for pod readiness in seconds (default: 120)
  -h, --help          Show this help

The verification performs:
  1. Checks all broker pods are Ready
  2. Checks PVCs are Bound
  3. Creates a test topic
  4. Produces a test message
  5. Consumes and verifies the message
  6. Cleans up the test topic
USAGE
  exit 0
}

# ── Parse args ──
while [[ $# -gt 0 ]]; do
  case $1 in
    --namespace) NAMESPACE="$2"; shift 2 ;;
    -n)          NAMESPACE="$2"; shift 2 ;;
    --topic)     TEST_TOPIC="$2"; shift 2 ;;
    --timeout)   TIMEOUT="$2"; shift 2 ;;
    -h|--help)   usage ;;
    *)           echo "Unknown option: $1"; exit 1 ;;
  esac
done

PASSED=0
FAILED=0
TOTAL=0

check() {
  TOTAL=$((TOTAL + 1))
  local description="$1"
  shift
  if "$@" &>/dev/null; then
    ok "$description"
    PASSED=$((PASSED + 1))
    return 0
  else
    fail "$description"
    FAILED=$((FAILED + 1))
    return 1
  fi
}

divider "KAFKA CLUSTER VERIFICATION"
echo ""
info "Namespace: $NAMESPACE"
info "Timeout:   ${TIMEOUT}s"
echo ""

# ── Check 1: Broker pods ──
divider "CHECK 1: BROKER POD STATUS"

# Wait for pods to be ready
info "Waiting for broker pods to be ready..."
ELAPSED=0
INTERVAL=5

while true; do
  TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=kafka --no-headers 2>/dev/null | wc -l)
  READY_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=kafka --no-headers 2>/dev/null | grep -c "Running" || echo 0)

  if [[ "$TOTAL_PODS" -gt 0 && "$READY_PODS" -eq "$TOTAL_PODS" ]]; then
    break
  fi

  if [[ "$ELAPSED" -ge "$TIMEOUT" ]]; then
    fail "Timeout: ${READY_PODS}/${TOTAL_PODS} pods ready after ${TIMEOUT}s"
    TOTAL=$((TOTAL + 1))
    FAILED=$((FAILED + 1))
    echo ""
    kubectl get pods -n "$NAMESPACE" -l app=kafka 2>/dev/null
    echo ""
    # Continue with remaining checks anyway
    break
  fi

  echo -ne "\r  ${READY_PODS}/${TOTAL_PODS} pods ready... (${ELAPSED}s)"
  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done
echo ""

TOTAL=$((TOTAL + 1))
TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=kafka --no-headers 2>/dev/null | wc -l)
READY_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=kafka --no-headers 2>/dev/null | grep -c "Running" || echo 0)

if [[ "$TOTAL_PODS" -gt 0 && "$READY_PODS" -eq "$TOTAL_PODS" ]]; then
  ok "All ${READY_PODS} broker pod(s) are Running"
  PASSED=$((PASSED + 1))
else
  fail "Only ${READY_PODS}/${TOTAL_PODS} broker pods are Running"
  FAILED=$((FAILED + 1))
fi

kubectl get pods -n "$NAMESPACE" -l app=kafka 2>/dev/null
echo ""

# ── Check 2: PVCs ──
divider "CHECK 2: PERSISTENT VOLUME CLAIMS"

PVC_TOTAL=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
PVC_BOUND=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c "Bound" || echo 0)

TOTAL=$((TOTAL + 1))
if [[ "$PVC_TOTAL" -gt 0 && "$PVC_BOUND" -eq "$PVC_TOTAL" ]]; then
  ok "All ${PVC_BOUND} PVC(s) are Bound"
  PASSED=$((PASSED + 1))
elif [[ "$PVC_TOTAL" -eq 0 ]]; then
  warn "No PVCs found (using emptyDir or no persistence)"
  PASSED=$((PASSED + 1))  # Not a failure
else
  fail "Only ${PVC_BOUND}/${PVC_TOTAL} PVCs are Bound"
  FAILED=$((FAILED + 1))
fi

kubectl get pvc -n "$NAMESPACE" 2>/dev/null || info "No PVCs in namespace"
echo ""

# ── Check 3: Services ──
divider "CHECK 3: SERVICES"

TOTAL=$((TOTAL + 1))
if kubectl get svc -n "$NAMESPACE" -l app=kafka --no-headers 2>/dev/null | grep -q .; then
  ok "Kafka services are created"
  PASSED=$((PASSED + 1))
  kubectl get svc -n "$NAMESPACE" -l app=kafka 2>/dev/null
else
  fail "No Kafka services found"
  FAILED=$((FAILED + 1))
fi
echo ""

# ── Check 4: Topic creation ──
divider "CHECK 4: TOPIC CREATION"

# Detect which Kafka command path is available
KAFKA_EXEC="kafka-0"
KAFKA_CMD_PREFIX=""

# Try kafka-topics.sh first, then kafka-topics (no .sh, for some images)
if kubectl exec "$KAFKA_EXEC" -n "$NAMESPACE" -- which kafka-topics.sh &>/dev/null 2>&1; then
  KAFKA_CMD_PREFIX=""
  TOPICS_CMD="kafka-topics.sh"
  CONSOLE_PRODUCER="kafka-console-producer.sh"
  CONSOLE_CONSUMER="kafka-console-consumer.sh"
elif kubectl exec "$KAFKA_EXEC" -n "$NAMESPACE" -- which kafka-topics &>/dev/null 2>&1; then
  TOPICS_CMD="kafka-topics"
  CONSOLE_PRODUCER="kafka-console-producer"
  CONSOLE_CONSUMER="kafka-console-consumer"
else
  # Bitnami images use /opt/bitnami/kafka/bin/
  if kubectl exec "$KAFKA_EXEC" -n "$NAMESPACE" -- test -f /opt/bitnami/kafka/bin/kafka-topics.sh &>/dev/null 2>&1; then
    TOPICS_CMD="/opt/bitnami/kafka/bin/kafka-topics.sh"
    CONSOLE_PRODUCER="/opt/bitnami/kafka/bin/kafka-console-producer.sh"
    CONSOLE_CONSUMER="/opt/bitnami/kafka/bin/kafka-console-consumer.sh"
  else
    warn "Could not locate Kafka CLI tools in broker pod"
    TOPICS_CMD="kafka-topics.sh"
    CONSOLE_PRODUCER="kafka-console-producer.sh"
    CONSOLE_CONSUMER="kafka-console-consumer.sh"
  fi
fi

BOOTSTRAP="localhost:9092"
TEST_MESSAGE="kafka-k8s-setup-smoke-test-$(date +%s)"

TOTAL=$((TOTAL + 1))
info "Creating test topic '${TEST_TOPIC}'..."
if kubectl exec "$KAFKA_EXEC" -n "$NAMESPACE" -- \
  $TOPICS_CMD --create \
    --topic "$TEST_TOPIC" \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists \
    --bootstrap-server "$BOOTSTRAP" 2>/dev/null; then
  ok "Test topic '${TEST_TOPIC}' created"
  PASSED=$((PASSED + 1))
else
  fail "Could not create test topic '${TEST_TOPIC}'"
  FAILED=$((FAILED + 1))
fi

# ── Check 5: Produce message ──
divider "CHECK 5: PRODUCE MESSAGE"

TOTAL=$((TOTAL + 1))
info "Producing test message..."
if echo "$TEST_MESSAGE" | kubectl exec -i "$KAFKA_EXEC" -n "$NAMESPACE" -- \
  $CONSOLE_PRODUCER \
    --topic "$TEST_TOPIC" \
    --bootstrap-server "$BOOTSTRAP" 2>/dev/null; then
  ok "Test message produced"
  PASSED=$((PASSED + 1))
else
  fail "Could not produce test message"
  FAILED=$((FAILED + 1))
fi

# ── Check 6: Consume message ──
divider "CHECK 6: CONSUME MESSAGE"

TOTAL=$((TOTAL + 1))
info "Consuming test message (timeout: 10s)..."
RECEIVED=$(kubectl exec "$KAFKA_EXEC" -n "$NAMESPACE" -- \
  timeout 10 $CONSOLE_CONSUMER \
    --topic "$TEST_TOPIC" \
    --from-beginning \
    --max-messages 1 \
    --bootstrap-server "$BOOTSTRAP" 2>/dev/null || echo "")

if [[ "$RECEIVED" == *"$TEST_MESSAGE"* ]]; then
  ok "Message integrity verified (sent == received)"
  PASSED=$((PASSED + 1))
else
  fail "Message mismatch or not received"
  warn "  Sent:     $TEST_MESSAGE"
  warn "  Received: $RECEIVED"
  FAILED=$((FAILED + 1))
fi

# ── Cleanup ──
divider "CLEANUP"

info "Deleting test topic '${TEST_TOPIC}'..."
kubectl exec "$KAFKA_EXEC" -n "$NAMESPACE" -- \
  $TOPICS_CMD --delete \
    --topic "$TEST_TOPIC" \
    --bootstrap-server "$BOOTSTRAP" 2>/dev/null && ok "Test topic cleaned up" || warn "Could not delete test topic (may need manual cleanup)"

# ── Summary ──
divider "VERIFICATION SUMMARY"
echo ""
echo "  Total checks: $TOTAL"
echo -e "  ${GREEN}Passed:       $PASSED${NC}"
echo -e "  ${RED}Failed:       $FAILED${NC}"
echo ""

if [[ "$FAILED" -eq 0 ]]; then
  echo -e "  ${GREEN}✅ All checks passed — Kafka cluster is healthy!${NC}"
  exit 0
else
  echo -e "  ${RED}⚠️  ${FAILED} check(s) failed — review output above${NC}"
  exit 1
fi
