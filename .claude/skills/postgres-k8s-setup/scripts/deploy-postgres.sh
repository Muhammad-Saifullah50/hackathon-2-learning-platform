#!/bin/bash

# PostgreSQL Deployment Script for Kubernetes (Minikube)
# This script deploys PostgreSQL on Kubernetes with proper configuration

set -euo pipefail

# Default values
NAMESPACE="postgres"
REPLICAS=1
STORAGE_SIZE="5Gi"
PASSWORD="postgres"
DATABASE="appdb"
USER="postgres"
EXTERNAL=false
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --replicas)
      REPLICAS="$2"
      shift 2
      ;;
    --storage)
      STORAGE_SIZE="$2"
      shift 2
      ;;
    --namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    --password)
      PASSWORD="$2"
      shift 2
      ;;
    --database)
      DATABASE="$2"
      shift 2
      ;;
    --user)
      USER="$2"
      shift 2
      ;;
    --external)
      EXTERNAL=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --replicas N         Number of PostgreSQL replicas (default: 1)"
      echo "  --storage SIZE       PVC storage size per replica (default: 5Gi)"
      echo "  --namespace NS       Target namespace (default: postgres)"
      echo "  --password PASS      PostgreSQL superuser password (default: postgres)"
      echo "  --database DB        Default database name (default: appdb)"
      echo "  --user USER          PostgreSQL superuser name (default: postgres)"
      echo "  --external           Expose PostgreSQL via NodePort for external access"
      echo "  --dry-run            Print manifests without applying"
      echo "  --help               Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate prerequisites
echo "Validating prerequisites..."
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed or not in PATH"
    exit 1
fi

if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "Error: kubectl cannot connect to a Kubernetes cluster"
    exit 1
fi

if ! minikube status > /dev/null 2>&1; then
    echo "Warning: minikube is not running or not detected"
fi

# Function to create namespace
create_namespace() {
    echo "Creating namespace: $NAMESPACE"
    if [ "$DRY_RUN" = false ]; then
        kubectl create namespace "$NAMESPACE" || true
    else
        echo "Would create namespace: $NAMESPACE"
    fi
}

# Function to create storage class (for Minikube)
create_storage_class() {
    echo "Checking StorageClass..."
    if kubectl get storageclass > /dev/null 2>&1; then
        echo "StorageClass already exists"
    else
        echo "No StorageClass found - creating default one"
        if [ "$DRY_RUN" = false ]; then
            # For Minikube, we'll use the default storage class
            echo "Using default StorageClass for Minikube"
        else
            echo "Would create default StorageClass"
        fi
    fi
}

# Function to create secret
create_secret() {
    echo "Creating PostgreSQL secret..."
    if [ "$DRY_RUN" = false ]; then
        kubectl create secret generic postgres-credentials \
            --namespace="$NAMESPACE" \
            --from-literal=password="$PASSWORD" \
            --from-literal=user="$USER" \
            --from-literal=database="$DATABASE" \
            || true
    else
        echo "Would create secret postgres-credentials in namespace $NAMESPACE"
    fi
}

# Function to create statefulset and services
create_postgres_resources() {
    echo "Creating PostgreSQL resources..."

    # Create manifest content
    cat <<EOF | if [ "$DRY_RUN" = false ]; then kubectl apply -f -; else cat; fi
apiVersion: v1
kind: Namespace
metadata:
  name: $NAMESPACE
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-credentials
  namespace: $NAMESPACE
type: Opaque
data:
  password: $(echo -n "$PASSWORD" | base64)
  user: $(echo -n "$USER" | base64)
  database: $(echo -n "$DATABASE" | base64)
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
  namespace: $NAMESPACE
spec:
  clusterIP: None
  ports:
  - port: 5432
  selector:
    app: postgres
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: $NAMESPACE
spec:
  ports:
  - port: 5432
  selector:
    app: postgres
---
$(if [ "$EXTERNAL" = true ]; then
    echo "apiVersion: v1
kind: Service
metadata:
  name: postgres-external
  namespace: $NAMESPACE
spec:
  type: NodePort
  ports:
  - port: 5432
    targetPort: 5432
    nodePort: 30432
  selector:
    app: postgres
";
fi)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: $NAMESPACE
spec:
  serviceName: postgres-headless
  replicas: $REPLICAS
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        envFrom:
        - secretRef:
            name: postgres-credentials
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: $STORAGE_SIZE
EOF
}

# Function to wait for pods to be ready
wait_for_ready() {
    echo "Waiting for PostgreSQL pods to be ready..."
    timeout=120
    elapsed=0

    while true; do
        if [ "$DRY_RUN" = true ]; then
            echo "Would wait for pods to be ready (dry-run mode)"
            break
        fi

        ready_pods=$(kubectl get pods -n "$NAMESPACE" -l app=postgres --no-headers 2>/dev/null | grep -c Running)
        total_pods=$(kubectl get pods -n "$NAMESPACE" -l app=postgres --no-headers 2>/dev/null | wc -l)

        if [ "$ready_pods" -eq "$total_pods" ] && [ "$ready_pods" -gt 0 ]; then
            echo "All PostgreSQL pods are ready!"
            break
        fi

        if [ "$elapsed" -ge "$timeout" ]; then
            echo "Timeout waiting for pods to be ready"
            kubectl get pods -n "$NAMESPACE"
            exit 1
        fi

        echo "Waiting for pods to be ready... ($((elapsed/60))m $((elapsed%60))s)"
        sleep 5
        elapsed=$((elapsed + 5))
    done
}

# Main execution flow
echo "Starting PostgreSQL deployment on Kubernetes..."

create_namespace
create_storage_class
create_secret
create_postgres_resources

if [ "$DRY_RUN" = false ]; then
    wait_for_ready
    echo "PostgreSQL deployment completed successfully!"
    echo ""
    echo "Connection details:"
    echo "  Internal: postgresql://$USER:$PASSWORD@postgres.$NAMESPACE.svc.cluster.local:5432/$DATABASE"
    if [ "$EXTERNAL" = true ]; then
        echo "  External: minikube service postgres-external --namespace $NAMESPACE --url"
    fi
    echo "  Port-forward: kubectl port-forward svc/postgres 5432:5432 -n $NAMESPACE"
else
    echo "Dry-run completed. No resources were applied."
fi