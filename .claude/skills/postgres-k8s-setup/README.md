# PostgreSQL on Kubernetes (Minikube) Deployment Skill

This skill automates the deployment of PostgreSQL on Kubernetes (Minikube) for local development environments. It provides a complete solution for setting up PostgreSQL with proper persistence, configuration, and verification.

## Features

- Automated PostgreSQL deployment on Minikube
- Persistent volume configuration for data persistence
- Resource limits and requests for stable performance
- Secure credential management
- Verification and connectivity testing
- Clean teardown capability
- Support for external access via NodePort
- Helm chart support for advanced configurations

## Prerequisites

- Minikube installed and running
- kubectl configured with valid kubeconfig
- Bash 4+ installed
- Optional: Helm 3+ for advanced deployments

## Installation

1. Clone this skill to your Claude skills directory
2. Make the deployment script executable:
   ```bash
   chmod +x scripts/deploy-postgres.sh
   ```

## Usage

### Basic Deployment

```bash
bash scripts/deploy-postgres.sh
```

### Advanced Options

```bash
bash scripts/deploy-postgres.sh --database myapp --password secret123 --storage 10Gi --external
```

### Verification

```bash
bash scripts/verify-postgres.sh
```

### Teardown

```bash
bash scripts/teardown-postgres.sh
```