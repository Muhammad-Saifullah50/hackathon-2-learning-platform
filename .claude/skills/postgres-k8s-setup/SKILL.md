---
name: postgres-k8s-setup
description: Deploy and manage PostgreSQL on Kubernetes (Minikube) with automated provisioning, configuration, and verification. Use when the user asks to: (1) Deploy PostgreSQL on Kubernetes or Minikube, (2) Set up a PostgreSQL database locally for development on K8s, (3) Configure PostgreSQL with persistent volumes, resource limits, and authentication, (4) Verify PostgreSQL is running and healthy on K8s, (5) Connect to PostgreSQL from applications inside and outside the cluster, (6) Tear down or clean up a PostgreSQL deployment, (7) Troubleshoot PostgreSQL pod issues on Kubernetes. Triggers: "setup postgres", "deploy postgres", "postgres on k8s", "postgres on kubernetes", "postgres minikube", "postgresql cluster setup", "install postgresql", "postgres helm", "verify postgres", "teardown postgres", "remove postgres", "postgres k8s", "postgres statefulset", "deploy postgresql", "postgresql on kubernetes", "setup postgresql".
---

# PostgreSQL on Kubernetes (Minikube) Setup

This skill automates the deployment of PostgreSQL on Kubernetes (Minikube) for local development environments. It provides a complete solution for setting up PostgreSQL with proper persistence, configuration, and verification.

## Prerequisites

- Minikube installed and running
- kubectl configured with valid kubeconfig
- Bash 4+ installed
- Optional: Helm 3+ for advanced deployments

## Deployment Workflow

### 1. Basic Deployment

To deploy PostgreSQL with default settings:

```bash
bash scripts/deploy-postgres.sh
```

### 2. Advanced Deployment Options

```bash
bash scripts/deploy-postgres.sh --database myapp --password secret123 --storage 10Gi --external
```

Options:
- `--replicas <n>` — Number of PostgreSQL replicas (default: 1)
- `--storage <size>` — PVC storage size per replica (default: 5Gi)
- `--namespace <ns>` — Target namespace (default: postgres)
- `--password <pass>` — PostgreSQL superuser password (default: postgres)
- `--database <db>` — Default database name (default: appdb)
- `--user <user>` — PostgreSQL superuser name (default: postgres)
- `--external` — Expose PostgreSQL via NodePort for external access
- `--dry-run` — Print manifests without applying
- `--help` — Show usage

### 3. Verification

After deployment, verify the installation:

```bash
bash scripts/verify-postgres.sh
```

Options:
- `--namespace <ns>` — Target namespace (default: postgres)
- `--timeout <s>` — Timeout in seconds for pod readiness (default: 120)
- `--help` — Show usage

### 4. Teardown

To remove PostgreSQL from the cluster:

```bash
bash scripts/teardown-postgres.sh
```

Options:
- `--namespace <ns>` — Target namespace (default: postgres)
- `--keep-pvcs` — Delete pods/services but retain PVCs and data
- `--force` — Skip confirmation prompt
- `--help` — Show usage

## Helm Deployment (Alternative)

For users preferring Helm:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Single instance (dev)
helm install postgresql bitnami/postgresql \
  --namespace postgres --create-namespace \
  --set auth.postgresPassword=postgres \
  --set auth.database=appdb \
  --set primary.persistence.size=5Gi \
  --set primary.resources.requests.memory=256Mi \
  --set primary.resources.requests.cpu=250m
```

## Connection Details

Once deployed, PostgreSQL can be accessed with:

- **Internal**: `postgresql://postgres:<password>@postgres.postgres.svc.cluster.local:5432/appdb`
- **External (NodePort)**: `minikube service postgres-external --namespace postgres --url`
- **Port-forward**: `kubectl port-forward svc/postgres 5432:5432 -n postgres`

## Configuration Reference

For detailed PostgreSQL configuration tuning (memory, WAL, resource sizing, security, monitoring, backup), see [references/postgres-config.md](references/postgres-config.md).