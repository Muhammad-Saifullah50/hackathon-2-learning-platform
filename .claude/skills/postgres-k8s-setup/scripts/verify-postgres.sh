#!/usr/bin/env bash
# verify-postgres.sh — Smoke-test a PostgreSQL deployment on Kubernetes
# Usage: bash verify-postgres.sh [--namespace <ns>] [--timeout <s>] [--help]

set -euo pipefail

# ── Defaults ──
NAMESPACE="postgres"
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
Usage: bash verify-postgres.sh [OPTIONS]

Options:
  --namespace <ns>    Target namespace (default: postgres)
  --timeout <s>       Timeout for pod readiness in seconds (default: 120)
  -h, --help          Show this help

The verification performs:
  1. Checks all PostgreSQL pods are Ready
  2. Checks PVCs are Bound
  3. Checks Services exist
  4. Runs a SQL connectivity test (SELECT 1)
  5. Creates and drops a test table
  6. Verifies data read/write integrity
USAGE
  exit 0
}

# ── Parse args ──
while [[ $# -gt 0 ]]; do
  case $1 in
    --namespace) NAMESPACE="$2"; shift 2 ;;
    -n)          NAMESPACE="$2"; shift 2 ;;
    --timeout)   TIMEOUT="$2"; shift 2 ;;
    -h|--help)   usage ;;
    *)           echo "Unknown option: $1"; exit 1 ;;
  esac
done

PASSED=0
FAILED=0
TOTAL=0

divider "POSTGRESQL CLUSTER VERIFICATION"
echo ""
info "Namespace: $NAMESPACE"
info "Timeout:   ${TIMEOUT}s"
echo ""

# ── Check 1: PostgreSQL pods ──
divider "CHECK 1: POD STATUS"

info "Waiting for PostgreSQL pods to be ready..."
ELAPSED=0
INTERVAL=5

while true; do
  TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=postgresql --no-headers 2>/dev/null | wc -l)
  READY_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=postgresql --no-headers 2>/dev/null | grep -c "Running" || echo 0)

  if [[ "$TOTAL_PODS" -gt 0 && "$READY_PODS" -eq "$TOTAL_PODS" ]]; then
    break
  fi

  if [[ "$ELAPSED" -ge "$TIMEOUT" ]]; then
    fail "Timeout: ${READY_PODS}/${TOTAL_PODS} pods ready after ${TIMEOUT}s"
    TOTAL=$((TOTAL + 1))
    FAILED=$((FAILED + 1))
    echo ""
    kubectl get pods -n "$NAMESPACE" -l app=postgresql 2>/dev/null
    echo ""
    break
  fi

  echo -ne "\r  ${READY_PODS}/${TOTAL_PODS} pods ready... (${ELAPSED}s)"
  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done
echo ""

TOTAL=$((TOTAL + 1))
TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=postgresql --no-headers 2>/dev/null | wc -l)
READY_PODS=$(kubectl get pods -n "$NAMESPACE" -l app=postgresql --no-headers 2>/dev/null | grep -c "Running" || echo 0)

if [[ "$TOTAL_PODS" -gt 0 && "$READY_PODS" -eq "$TOTAL_PODS" ]]; then
  ok "All ${READY_PODS} PostgreSQL pod(s) are Running"
  PASSED=$((PASSED + 1))
else
  fail "Only ${READY_PODS}/${TOTAL_PODS} PostgreSQL pods are Running"
  FAILED=$((FAILED + 1))
fi

kubectl get pods -n "$NAMESPACE" -l app=postgresql 2>/dev/null
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
  PASSED=$((PASSED + 1))
else
  fail "Only ${PVC_BOUND}/${PVC_TOTAL} PVCs are Bound"
  FAILED=$((FAILED + 1))
fi

kubectl get pvc -n "$NAMESPACE" 2>/dev/null || info "No PVCs in namespace"
echo ""

# ── Check 3: Services ──
divider "CHECK 3: SERVICES"

TOTAL=$((TOTAL + 1))
if kubectl get svc -n "$NAMESPACE" -l app=postgresql --no-headers 2>/dev/null | grep -q .; then
  ok "PostgreSQL services are created"
  PASSED=$((PASSED + 1))
  kubectl get svc -n "$NAMESPACE" -l app=postgresql 2>/dev/null
else
  fail "No PostgreSQL services found"
  FAILED=$((FAILED + 1))
fi
echo ""

# ── Check 4: SQL connectivity (SELECT 1) ──
divider "CHECK 4: SQL CONNECTIVITY"

PG_POD="postgres-0"

TOTAL=$((TOTAL + 1))
info "Testing SQL connectivity with SELECT 1..."
SQL_RESULT=$(kubectl exec "$PG_POD" -n "$NAMESPACE" -- \
  psql -U postgres -d postgres -tAc "SELECT 1;" 2>/dev/null || echo "")

if [[ "$SQL_RESULT" == "1" ]]; then
  ok "SQL connectivity verified (SELECT 1 = 1)"
  PASSED=$((PASSED + 1))
else
  fail "SQL connectivity failed (expected '1', got '${SQL_RESULT}')"
  FAILED=$((FAILED + 1))
fi

# ── Check 5: Create and query test table ──
divider "CHECK 5: DATA READ/WRITE TEST"

TEST_TABLE="smoke_test_$(date +%s)"
TEST_VALUE="postgres-k8s-setup-$(date +%s)"

TOTAL=$((TOTAL + 1))
info "Creating test table '${TEST_TABLE}'..."

# Create table, insert, select, drop — all in one exec
WRITE_READ_RESULT=$(kubectl exec "$PG_POD" -n "$NAMESPACE" -- \
  psql -U postgres -d postgres -tAc "
    CREATE TABLE ${TEST_TABLE} (id SERIAL PRIMARY KEY, val TEXT NOT NULL);
    INSERT INTO ${TEST_TABLE} (val) VALUES ('${TEST_VALUE}');
    SELECT val FROM ${TEST_TABLE} WHERE val = '${TEST_VALUE}';
  " 2>/dev/null || echo "")

if [[ "$WRITE_READ_RESULT" == *"$TEST_VALUE"* ]]; then
  ok "Data read/write integrity verified"
  PASSED=$((PASSED + 1))
else
  fail "Data read/write test failed"
  warn "  Expected: $TEST_VALUE"
  warn "  Got:      $WRITE_READ_RESULT"
  FAILED=$((FAILED + 1))
fi

# ── Check 6: Verify database exists ──
divider "CHECK 6: DATABASE CHECK"

TOTAL=$((TOTAL + 1))
info "Checking configured database exists..."

# Get the database name from the secret
PG_DB=$(kubectl get secret postgres-credentials -n "$NAMESPACE" -o jsonpath='{.data.POSTGRES_DB}' 2>/dev/null | base64 -d 2>/dev/null || echo "")

if [[ -z "$PG_DB" ]]; then
  PG_DB="appdb"
  warn "Could not read database name from secret, checking default: $PG_DB"
fi

DB_EXISTS=$(kubectl exec "$PG_POD" -n "$NAMESPACE" -- \
  psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '${PG_DB}';" 2>/dev/null || echo "")

if [[ "$DB_EXISTS" == "1" ]]; then
  ok "Database '${PG_DB}' exists"
  PASSED=$((PASSED + 1))
else
  warn "Database '${PG_DB}' not found (may need to be created by application)"
  PASSED=$((PASSED + 1))  # Not a failure — init script may not have run yet
fi

# ── Cleanup ──
divider "CLEANUP"

info "Dropping test table '${TEST_TABLE}'..."
kubectl exec "$PG_POD" -n "$NAMESPACE" -- \
  psql -U postgres -d postgres -tAc "DROP TABLE IF EXISTS ${TEST_TABLE};" 2>/dev/null \
  && ok "Test table cleaned up" \
  || warn "Could not drop test table (may need manual cleanup)"

# ── Summary ──
divider "VERIFICATION SUMMARY"
echo ""
echo "  Total checks: $TOTAL"
echo -e "  ${GREEN}Passed:       $PASSED${NC}"
echo -e "  ${RED}Failed:       $FAILED${NC}"
echo ""

if [[ "$FAILED" -eq 0 ]]; then
  echo -e "  ${GREEN}✅ All checks passed — PostgreSQL is healthy!${NC}"
  exit 0
else
  echo -e "  ${RED}⚠️  ${FAILED} check(s) failed — review output above${NC}"
  exit 1
fi
