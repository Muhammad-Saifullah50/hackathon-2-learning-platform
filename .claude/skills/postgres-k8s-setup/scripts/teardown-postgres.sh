#!/usr/bin/env bash
# teardown-postgres.sh — Remove all PostgreSQL resources from Kubernetes
# Usage: bash teardown-postgres.sh [--namespace <ns>] [--keep-pvcs] [--force] [--help]

set -euo pipefail

# ── Defaults ──
NAMESPACE="postgres"
KEEP_PVCS=false
FORCE=false

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

usage() {
  cat <<'USAGE'
Usage: bash teardown-postgres.sh [OPTIONS]

Options:
  --namespace <ns>   Target namespace (default: postgres)
  --keep-pvcs        Delete pods/services but retain PVCs and data
  --force            Skip confirmation prompt
  -h, --help         Show this help

This script removes:
  - All PostgreSQL StatefulSets, Deployments, Pods
  - All PostgreSQL Services (headless, external, ClusterIP)
  - All ConfigMaps and Secrets with app=postgresql label
  - All PVCs (unless --keep-pvcs)
  - The namespace (unless --keep-pvcs)
  - The postgres-storage StorageClass
USAGE
  exit 0
}

# ── Parse args ──
while [[ $# -gt 0 ]]; do
  case $1 in
    --namespace) NAMESPACE="$2"; shift 2 ;;
    -n)          NAMESPACE="$2"; shift 2 ;;
    --keep-pvcs) KEEP_PVCS=true; shift ;;
    --force)     FORCE=true; shift ;;
    -h|--help)   usage ;;
    *)           err "Unknown option: $1"; exit 1 ;;
  esac
done

echo ""
echo -e "${RED}══════════════════════════════════════════════════════════════${NC}"
echo -e "  ${RED}POSTGRESQL TEARDOWN${NC}"
echo -e "${RED}══════════════════════════════════════════════════════════════${NC}"
echo ""
info "Namespace:  $NAMESPACE"
info "Keep PVCs:  $KEEP_PVCS"
echo ""

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
  warn "Namespace '$NAMESPACE' does not exist — nothing to tear down"
  exit 0
fi

# Show what will be deleted
info "Resources in namespace '$NAMESPACE':"
echo ""
kubectl get all -n "$NAMESPACE" 2>/dev/null || info "No resources found"
echo ""

if [[ "$KEEP_PVCS" == false ]]; then
  info "PVCs that will be deleted:"
  kubectl get pvc -n "$NAMESPACE" 2>/dev/null || info "No PVCs found"
  echo ""
fi

# Confirmation
if [[ "$FORCE" == false ]]; then
  echo -e "${YELLOW}This will permanently delete all PostgreSQL resources in namespace '$NAMESPACE'.${NC}"
  if [[ "$KEEP_PVCS" == false ]]; then
    echo -e "${RED}All data in PVCs will be lost!${NC}"
  fi
  echo ""
  read -rp "Continue? [y/N]: " CONFIRM
  if [[ "${CONFIRM,,}" != "y" && "${CONFIRM,,}" != "yes" ]]; then
    info "Teardown cancelled"
    exit 0
  fi
  echo ""
fi

# ── Delete StatefulSets ──
info "Deleting StatefulSets..."
kubectl delete statefulset -n "$NAMESPACE" -l app=postgresql --ignore-not-found 2>/dev/null && ok "PostgreSQL StatefulSets deleted" || warn "No PostgreSQL StatefulSets found"

# ── Delete Deployments ──
info "Deleting Deployments..."
kubectl delete deployment -n "$NAMESPACE" -l app=postgresql --ignore-not-found 2>/dev/null && ok "PostgreSQL Deployments deleted" || true

# ── Delete Services ──
info "Deleting Services..."
kubectl delete svc -n "$NAMESPACE" -l app=postgresql --ignore-not-found 2>/dev/null && ok "PostgreSQL Services deleted" || warn "No PostgreSQL Services found"

# ── Delete ConfigMaps ──
info "Deleting ConfigMaps..."
kubectl delete configmap -n "$NAMESPACE" -l app=postgresql --ignore-not-found 2>/dev/null && ok "PostgreSQL ConfigMaps deleted" || true

# ── Delete Secrets ──
info "Deleting Secrets..."
kubectl delete secret -n "$NAMESPACE" -l app=postgresql --ignore-not-found 2>/dev/null && ok "PostgreSQL Secrets deleted" || true

# ── Delete PVCs (unless --keep-pvcs) ──
if [[ "$KEEP_PVCS" == false ]]; then
  info "Deleting PVCs..."
  kubectl delete pvc -n "$NAMESPACE" --all --ignore-not-found 2>/dev/null && ok "All PVCs deleted" || warn "No PVCs to delete"
else
  warn "Keeping PVCs (data retained)"
  kubectl get pvc -n "$NAMESPACE" 2>/dev/null || true
fi

# ── Delete remaining pods (force cleanup) ──
info "Cleaning up remaining pods..."
kubectl delete pods -n "$NAMESPACE" --all --grace-period=0 --force --ignore-not-found 2>/dev/null && ok "Remaining pods cleaned up" || true

# ── Delete namespace (unless keeping PVCs) ──
if [[ "$KEEP_PVCS" == false ]]; then
  info "Deleting namespace '$NAMESPACE'..."
  kubectl delete namespace "$NAMESPACE" --ignore-not-found 2>/dev/null && ok "Namespace '$NAMESPACE' deleted" || warn "Could not delete namespace"
else
  info "Keeping namespace '$NAMESPACE' (PVCs retained)"
fi

# ── Delete StorageClass ──
info "Checking StorageClass..."
if kubectl get storageclass postgres-storage &>/dev/null; then
  kubectl delete storageclass postgres-storage --ignore-not-found 2>/dev/null && ok "StorageClass 'postgres-storage' deleted" || warn "Could not delete StorageClass"
else
  info "No postgres-storage StorageClass to clean up"
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}TEARDOWN COMPLETE${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""
if [[ "$KEEP_PVCS" == true ]]; then
  info "PVCs and data were retained in namespace '$NAMESPACE'"
  info "To fully remove: bash teardown-postgres.sh --namespace $NAMESPACE --force"
else
  ok "All PostgreSQL resources have been removed"
fi
