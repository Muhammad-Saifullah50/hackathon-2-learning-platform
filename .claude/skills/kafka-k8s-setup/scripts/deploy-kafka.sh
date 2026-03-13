#!/usr/bin/env bash
# deploy-kafka.sh — Deploy Apache Kafka on Kubernetes (Minikube-optimized)
# Usage: bash deploy-kafka.sh [--mode kraft|zookeeper] [--brokers N] [--storage SIZE]
#        [--namespace NS] [--external] [--dry-run] [--help]

set -euo pipefail

# ── Defaults ──
MODE="kraft"
BROKERS=3
STORAGE="5Gi"
NAMESPACE="kafka"
EXTERNAL=false
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFESTS_DIR="${SCRIPT_DIR}/../manifests"

# ── Color helpers ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }
divider() { echo ""; echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"; echo -e "  ${BLUE}$1${NC}"; echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"; }

usage() {
  cat <<'USAGE'
Usage: bash deploy-kafka.sh [OPTIONS]

Options:
  --mode kraft|zookeeper   Metadata mode (default: kraft)
  --brokers <n>            Number of broker replicas (default: 3)
  --storage <size>         PVC storage per broker (default: 5Gi)
  --namespace <ns>         Target namespace (default: kafka)
  --external               Expose brokers via NodePort
  --dry-run                Print manifests without applying
  -h, --help               Show this help

Examples:
  bash deploy-kafka.sh
  bash deploy-kafka.sh --brokers 1 --storage 2Gi
  bash deploy-kafka.sh --mode zookeeper --external
  bash deploy-kafka.sh --dry-run
USAGE
  exit 0
}

# ── Parse args ──
while [[ $# -gt 0 ]]; do
  case $1 in
    --mode)       MODE="$2"; shift 2 ;;
    --brokers)    BROKERS="$2"; shift 2 ;;
    --storage)    STORAGE="$2"; shift 2 ;;
    --namespace)  NAMESPACE="$2"; shift 2 ;;
    -n)           NAMESPACE="$2"; shift 2 ;;
    --external)   EXTERNAL=true; shift ;;
    --dry-run)    DRY_RUN=true; shift ;;
    -h|--help)    usage ;;
    *)            err "Unknown option: $1"; exit 1 ;;
  esac
done

# Validate mode
if [[ "$MODE" != "kraft" && "$MODE" != "zookeeper" ]]; then
  err "Invalid mode: $MODE (must be 'kraft' or 'zookeeper')"
  exit 1
fi

# Validate brokers
if ! [[ "$BROKERS" =~ ^[0-9]+$ ]] || [[ "$BROKERS" -lt 1 ]]; then
  err "Invalid broker count: $BROKERS (must be >= 1)"
  exit 1
fi

divider "KAFKA DEPLOYMENT — ${MODE^^} MODE"
echo ""
info "Mode:       $MODE"
info "Brokers:    $BROKERS"
info "Storage:    $STORAGE per broker"
info "Namespace:  $NAMESPACE"
info "External:   $EXTERNAL"
info "Dry-run:    $DRY_RUN"
echo ""

# ── Step 1: Validate prerequisites ──
divider "STEP 1: VALIDATING PREREQUISITES"

if ! command -v kubectl &>/dev/null; then
  err "kubectl is not installed or not in PATH"
  exit 1
fi
ok "kubectl found: $(kubectl version --client --short 2>/dev/null || kubectl version --client 2>/dev/null | head -1)"

# Check if cluster is reachable
if ! kubectl cluster-info &>/dev/null; then
  err "Cannot reach Kubernetes cluster. Is minikube running?"
  echo ""
  info "Start minikube with: minikube start"
  exit 1
fi
ok "Kubernetes cluster is reachable"

# Check if minikube (optional, for storage addon)
if command -v minikube &>/dev/null; then
  MINIKUBE_STATUS=$(minikube status --format='{{.Host}}' 2>/dev/null || echo "unknown")
  if [[ "$MINIKUBE_STATUS" == "Running" ]]; then
    ok "Minikube is running"
    # Ensure storage provisioner addon
    if minikube addons list 2>/dev/null | grep -q "storage-provisioner.*enabled"; then
      ok "Minikube storage-provisioner addon is enabled"
    else
      warn "Enabling minikube storage-provisioner addon..."
      minikube addons enable storage-provisioner 2>/dev/null || warn "Could not enable storage-provisioner (may already be available)"
    fi
  else
    warn "Minikube detected but not running (status: $MINIKUBE_STATUS)"
  fi
else
  info "Minikube not detected — assuming external cluster"
fi

# ── Step 2: Create namespace ──
divider "STEP 2: CREATING NAMESPACE"

if [[ "$DRY_RUN" == true ]]; then
  info "[dry-run] Would create namespace: $NAMESPACE"
else
  if kubectl get namespace "$NAMESPACE" &>/dev/null; then
    ok "Namespace '$NAMESPACE' already exists"
  else
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: ${NAMESPACE}
  labels:
    app.kubernetes.io/part-of: kafka
    app.kubernetes.io/managed-by: kafka-k8s-setup
EOF
    ok "Created namespace '$NAMESPACE'"
  fi
fi

# ── Step 3: Apply StorageClass ──
divider "STEP 3: STORAGE CLASS"

if [[ "$DRY_RUN" == true ]]; then
  info "[dry-run] Would apply StorageClass from manifests/storage-class.yaml"
else
  if kubectl get storageclass kafka-storage &>/dev/null; then
    ok "StorageClass 'kafka-storage' already exists"
  else
    if [[ -f "${MANIFESTS_DIR}/storage-class.yaml" ]]; then
      kubectl apply -f "${MANIFESTS_DIR}/storage-class.yaml"
      ok "Applied StorageClass 'kafka-storage'"
    else
      warn "No storage-class.yaml found; using cluster default StorageClass"
    fi
  fi
fi

# ── Step 4: Deploy Kafka ──
divider "STEP 4: DEPLOYING KAFKA (${MODE^^} MODE)"

# Generate manifests with dynamic values using sed
apply_manifest() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    err "Manifest not found: $file"
    exit 1
  fi

  # Replace placeholders in manifest
  local rendered
  rendered=$(sed \
    -e "s/{{NAMESPACE}}/${NAMESPACE}/g" \
    -e "s/{{BROKERS}}/${BROKERS}/g" \
    -e "s/{{STORAGE}}/${STORAGE}/g" \
    "$file")

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] Would apply: $file"
    echo "---"
    echo "$rendered"
    echo "---"
  else
    echo "$rendered" | kubectl apply -f -
  fi
}

if [[ "$MODE" == "kraft" ]]; then
  info "Deploying Kafka in KRaft mode (no Zookeeper needed)..."
  apply_manifest "${MANIFESTS_DIR}/kafka-kraft.yaml"
else
  info "Deploying Zookeeper ensemble + Kafka brokers..."
  apply_manifest "${MANIFESTS_DIR}/kafka-zookeeper.yaml"
fi

# Apply external service if requested
if [[ "$EXTERNAL" == true ]]; then
  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] Would create NodePort services for external access"
  else
    info "Creating NodePort services for external access..."
    for i in $(seq 0 $((BROKERS - 1))); do
      kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: kafka-external-${i}
  namespace: ${NAMESPACE}
  labels:
    app: kafka
    app.kubernetes.io/managed-by: kafka-k8s-setup
spec:
  type: NodePort
  selector:
    app: kafka
    statefulset.kubernetes.io/pod-name: kafka-${i}
  ports:
    - name: external
      port: 9094
      targetPort: 9094
      protocol: TCP
EOF
    done
    ok "Created external NodePort services"
  fi
fi

if [[ "$DRY_RUN" == true ]]; then
  echo ""
  ok "Dry-run complete — no resources were applied"
  exit 0
fi

# ── Step 5: Wait for pods ──
divider "STEP 5: WAITING FOR BROKER PODS"

info "Waiting for ${BROKERS} Kafka broker(s) to be ready (timeout: 300s)..."

TIMEOUT=300
ELAPSED=0
INTERVAL=5

while true; do
  READY_COUNT=$(kubectl get pods -n "$NAMESPACE" -l app=kafka --no-headers 2>/dev/null | grep -c "Running" || echo 0)
  if [[ "$READY_COUNT" -ge "$BROKERS" ]]; then
    break
  fi
  if [[ "$ELAPSED" -ge "$TIMEOUT" ]]; then
    err "Timeout waiting for broker pods (${READY_COUNT}/${BROKERS} ready after ${TIMEOUT}s)"
    echo ""
    info "Debug with:"
    info "  kubectl get pods -n $NAMESPACE"
    info "  kubectl describe pod kafka-0 -n $NAMESPACE"
    info "  kubectl logs kafka-0 -n $NAMESPACE"
    exit 1
  fi
  echo -ne "\r  ${READY_COUNT}/${BROKERS} brokers ready... (${ELAPSED}s elapsed)"
  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo ""
ok "All ${BROKERS} broker(s) are running"
echo ""
kubectl get pods -n "$NAMESPACE" -l app=kafka

# ── Step 6: Run verification ──
divider "STEP 6: VERIFICATION"

VERIFY_SCRIPT="${SCRIPT_DIR}/verify-kafka.sh"
if [[ -f "$VERIFY_SCRIPT" ]]; then
  info "Running smoke test..."
  bash "$VERIFY_SCRIPT" --namespace "$NAMESPACE"
else
  warn "verify-kafka.sh not found at $VERIFY_SCRIPT — skipping verification"
fi

# ── Summary ──
divider "DEPLOYMENT COMPLETE"
echo ""
ok "Kafka cluster deployed successfully!"
echo ""
info "Namespace:        $NAMESPACE"
info "Mode:             $MODE"
info "Brokers:          $BROKERS"
info "Storage:          $STORAGE per broker"
echo ""
info "Internal bootstrap servers:"
info "  kafka-headless.${NAMESPACE}.svc.cluster.local:9092"
echo ""
if [[ "$EXTERNAL" == true ]]; then
  info "External access:"
  for i in $(seq 0 $((BROKERS - 1))); do
    NODEPORT=$(kubectl get svc "kafka-external-${i}" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "pending")
    info "  kafka-${i}: $(minikube ip 2>/dev/null || echo '<node-ip>'):${NODEPORT}"
  done
  echo ""
fi
info "Useful commands:"
info "  kubectl get pods -n $NAMESPACE"
info "  kubectl logs kafka-0 -n $NAMESPACE"
info "  bash scripts/verify-kafka.sh --namespace $NAMESPACE"
info "  bash scripts/teardown-kafka.sh --namespace $NAMESPACE"
