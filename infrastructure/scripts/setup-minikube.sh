#!/bin/bash
set -e

echo "=========================================="
echo "Setting up Minikube cluster for LearnFlow"
echo "=========================================="

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "Error: minikube is not installed"
    echo "Install with: curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    echo "Install with: curl -LO \"https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\" && sudo install kubectl /usr/local/bin/kubectl"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is not running"
    echo "Start Docker and try again"
    exit 1
fi

# Check if minikube is already running
if minikube status &> /dev/null; then
    echo "Minikube is already running"
    minikube status
    exit 0
fi

echo "Starting Minikube cluster..."
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.28.0

echo ""
echo "Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server

echo ""
echo "Verifying cluster..."
kubectl cluster-info
kubectl get nodes

echo ""
echo "=========================================="
echo "Minikube cluster setup complete!"
echo "=========================================="
echo ""
echo "Cluster info:"
kubectl get nodes -o wide
echo ""
echo "Next steps:"
echo "1. Run 'minikube tunnel' in a separate terminal (keep it running)"
echo "2. Run './infrastructure/scripts/deploy-redis.sh' to deploy Redis"
echo ""
