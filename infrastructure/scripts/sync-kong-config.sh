#!/bin/bash
set -e

echo "=========================================="
echo "Syncing Kong Configuration"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    echo "Run './infrastructure/scripts/setup-minikube.sh' first"
    exit 1
fi

# Check if Kong is running
if ! kubectl get pods -n kong -l app.kubernetes.io/name=kong | grep -q "Running"; then
    echo "Error: Kong is not running"
    echo "Run './infrastructure/scripts/deploy-kong.sh' first"
    exit 1
fi

# Check if deck is installed
if ! command -v deck &> /dev/null; then
    echo "deck CLI not found. Installing..."

    # Detect architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="arm64"
    fi

    # Download and install deck
    DECK_VERSION="v1.28.0"
    curl -sL "https://github.com/kong/deck/releases/download/${DECK_VERSION}/deck_${DECK_VERSION#v}_linux_${ARCH}.tar.gz" -o /tmp/deck.tar.gz
    tar -xzf /tmp/deck.tar.gz -C /tmp
    sudo mv /tmp/deck /usr/local/bin/
    rm /tmp/deck.tar.gz

    echo "deck installed successfully"
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

# Sync configuration
echo ""
echo "Syncing Kong configuration..."
KONG_CONFIG="infrastructure/kubernetes/kong/kong-configuration.yaml"

if [ ! -f "$KONG_CONFIG" ]; then
    echo "Error: Kong configuration not found at $KONG_CONFIG"
    exit 1
fi

deck sync \
  --kong-addr http://localhost:8001 \
  --state "$KONG_CONFIG" \
  --select-tag learnflow

echo ""
echo "=========================================="
echo "Kong configuration synced successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run './infrastructure/scripts/verify-kong.sh' to verify the configuration"
echo ""
