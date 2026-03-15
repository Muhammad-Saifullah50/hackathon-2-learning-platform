#!/bin/bash
set -e

echo "=========================================="
echo "Updating Kong Configuration with JWT Public Key"
echo "=========================================="

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

# Read the public key
PUBLIC_KEY=$(cat "$JWT_PUBLIC_KEY_PATH")

# Kong configuration file
KONG_CONFIG="infrastructure/kubernetes/kong/kong-configuration.yaml"

if [ ! -f "$KONG_CONFIG" ]; then
    echo "Error: Kong configuration not found at $KONG_CONFIG"
    exit 1
fi

# Create backup
cp "$KONG_CONFIG" "$KONG_CONFIG.backup"
echo "Created backup: $KONG_CONFIG.backup"

# Replace the placeholder with actual public key
# Using awk to replace the multi-line placeholder
awk -v key="$PUBLIC_KEY" '
BEGIN { in_key = 0 }
/rsa_public_key: \|/ {
    print
    in_key = 1
    next
}
in_key && /-----BEGIN PUBLIC KEY-----/ {
    print key
    in_key = 2
    next
}
in_key == 2 && /-----END PUBLIC KEY-----/ {
    in_key = 0
    next
}
in_key == 2 {
    next
}
!in_key {
    print
}
' "$KONG_CONFIG.backup" > "$KONG_CONFIG"

echo ""
echo "=========================================="
echo "Kong configuration updated successfully!"
echo "=========================================="
echo ""
echo "Updated file: $KONG_CONFIG"
echo "Backup file: $KONG_CONFIG.backup"
echo ""
echo "Next steps:"
echo "1. Run './infrastructure/scripts/sync-kong-config.sh' to apply the configuration to Kong"
echo ""
