#!/bin/bash
set -e

echo "=========================================="
echo "Creating JWT Public Key Secret for Kong"
echo "=========================================="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not running"
    echo "Run './infrastructure/scripts/setup-minikube.sh' first"
    exit 1
fi

# Check if JWT public key exists
JWT_PUBLIC_KEY_PATH="backend/auth-service/keys/jwt_key.pub"

if [ ! -f "$JWT_PUBLIC_KEY_PATH" ]; then
    echo "Error: JWT public key not found at $JWT_PUBLIC_KEY_PATH"
    echo ""
    echo "The JWT key pair should have been created during F01 (auth-service) implementation."
    echo ""
    echo "If the key doesn't exist, generate it with:"
    echo "  mkdir -p backend/auth-service/keys"
    echo "  ssh-keygen -t rsa -b 2048 -m PEM -f backend/auth-service/keys/jwt_key -N \"\""
    echo "  openssl rsa -in backend/auth-service/keys/jwt_key -pubout -outform PEM -out backend/auth-service/keys/jwt_key.pub"
    exit 1
fi

# Check if Kong namespace exists
if ! kubectl get namespace kong &> /dev/null; then
    echo "Error: Kong namespace does not exist"
    echo "Run './infrastructure/scripts/deploy-kong.sh' first"
    exit 1
fi

# Check if secret already exists
if kubectl get secret kong-jwt-public-key -n kong &> /dev/null; then
    echo "Secret 'kong-jwt-public-key' already exists in kong namespace"
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping secret creation"
        exit 0
    fi
    echo "Deleting existing secret..."
    kubectl delete secret kong-jwt-public-key -n kong
fi

# Create secret from JWT public key
echo ""
echo "Creating Kubernetes secret from JWT public key..."
kubectl create secret generic kong-jwt-public-key \
  --from-file=public_key.pem="$JWT_PUBLIC_KEY_PATH" \
  -n kong

# Verify secret
echo ""
echo "Verifying secret..."
kubectl get secret kong-jwt-public-key -n kong
kubectl describe secret kong-jwt-public-key -n kong

echo ""
echo "=========================================="
echo "JWT public key secret created successfully!"
echo "=========================================="
echo ""
echo "Secret details:"
echo "  Name: kong-jwt-public-key"
echo "  Namespace: kong"
echo "  Key: public_key.pem"
echo ""
echo "Next steps:"
echo "1. Update Kong configuration to use this public key"
echo "2. Run './infrastructure/scripts/sync-kong-config.sh' to apply Kong routes and plugins"
echo ""
