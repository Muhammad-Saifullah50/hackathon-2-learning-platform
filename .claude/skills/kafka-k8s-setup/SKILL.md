---
name: kafka-k8s-setup
description: >
  Deploy and manage Apache Kafka on Kubernetes (Minikube) with automated provisioning, configuration, and verification.
  Use when the user asks to:
  (1) Deploy Kafka on Kubernetes or Minikube,
  (2) Set up a Kafka cluster locally for development,
  (3) Configure Kafka with KRaft or Zookeeper mode,
  (4) Verify Kafka is running and healthy on K8s,
  (5) Tear down or clean up a Kafka deployment,
  (6) Troubleshoot Kafka broker issues on Kubernetes.
  Triggers: "setup kafka", "deploy kafka", "kafka on k8s", "kafka on kubernetes", "kafka minikube",
  "kafka cluster setup", "install kafka", "kafka kraft", "kafka zookeeper", "verify kafka",
  "teardown kafka", "remove kafka", "kafka k8s", "kafka statefulset".
---

# kafka-k8s-setup

Deploy a production-ready Apache Kafka cluster on Kubernetes (optimized for Minikube) with automated provisioning, smoke testing, and lifecycle management.

## Prerequisites

- `kubectl` configured with a valid kubeconfig
- `minikube` running (or any Kubernetes cluster)
- Bash 4+ installed
- Optional: `helm` v3+ (for Helm-based deployment alternative)

Verify prerequisites:

```bash
kubectl cluster-info
minikube status
```

## Workflows

### 1. Deploy Kafka Cluster (Full Setup)

Run the bundled deployment script:

```bash
bash scripts/deploy-kafka.sh
```

Options:
- `--mode kraft` — Use KRaft metadata mode (default, no Zookeeper needed)
- `--mode zookeeper` — Use traditional Zookeeper ensemble
- `--brokers <n>` — Number of Kafka broker replicas (default: 3)
- `--storage <size>` — PVC storage size per broker (default: 5Gi)
- `--namespace <ns>` — Target namespace (default: kafka)
- `--external` — Expose brokers via NodePort for external access
- `--dry-run` — Print manifests without applying
- `--help` — Show usage

The script performs these steps in order:
1. Validates prerequisites (kubectl, minikube status)
2. Creates the target namespace
3. Applies StorageClass (if needed for Minikube)
4. Deploys the Kafka cluster (KRaft or Zookeeper mode)
5. Waits for all broker pods to reach Ready state
6. Runs the verification script automatically

**Examples:**

```bash
# Default: 3-broker KRaft cluster
bash scripts/deploy-kafka.sh

# Single broker for lightweight dev
bash scripts/deploy-kafka.sh --brokers 1 --storage 2Gi

# Zookeeper mode with external access
bash scripts/deploy-kafka.sh --mode zookeeper --external

# Dry-run to inspect manifests
bash scripts/deploy-kafka.sh --dry-run
```

### 2. Verify Kafka Cluster

Run the verification script independently:

```bash
bash scripts/verify-kafka.sh
```

Options:
- `--namespace <ns>` — Target namespace (default: kafka)
- `--topic <name>` — Test topic name (default: smoke-test)
- `--timeout <s>` — Timeout in seconds for pod readiness (default: 120)
- `--help` — Show usage

The verification performs:
1. Checks all broker pods are in `Ready` state
2. Checks PVCs are `Bound`
3. Creates a test topic (`smoke-test`)
4. Produces a test message
5. Consumes the test message back
6. Verifies message integrity (sent == received)
7. Cleans up the test topic
8. Reports overall pass/fail status

### 3. Tear Down Kafka Cluster

Remove all Kafka resources:

```bash
bash scripts/teardown-kafka.sh
```

Options:
- `--namespace <ns>` — Target namespace (default: kafka)
- `--keep-pvcs` — Delete pods/services but retain PVCs and data
- `--force` — Skip confirmation prompt
- `--help` — Show usage

### 4. Deploy via Helm (Alternative)

For users preferring Helm:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# KRaft mode (Bitnami Kafka 3.7+)
helm install kafka bitnami/kafka \
  --namespace kafka --create-namespace \
  --set kraft.enabled=true \
  --set zookeeper.enabled=false \
  --set controller.replicaCount=3 \
  --set controller.persistence.size=5Gi \
  --set controller.resources.requests.memory=512Mi \
  --set controller.resources.requests.cpu=250m

# Zookeeper mode
helm install kafka bitnami/kafka \
  --namespace kafka --create-namespace \
  --set kraft.enabled=false \
  --set zookeeper.enabled=true \
  --set zookeeper.replicaCount=3 \
  --set broker.replicaCount=3 \
  --set broker.persistence.size=5Gi
```

**Key Helm values:**
- `kraft.enabled` — KRaft mode (true) vs Zookeeper mode (false)
- `controller.replicaCount` — Number of KRaft controller/broker nodes
- `controller.persistence.size` — PVC size per node
- `listeners.client.protocol` — PLAINTEXT (dev) or SASL_SSL (prod)
- `metrics.jmx.enabled` — Expose JMX metrics for Prometheus
- `provisioning.topics` — Auto-create topics on startup

## Manifest Files

The `manifests/` directory contains raw Kubernetes YAML:

| File | Description |
|---|---|
| `namespace.yaml` | Kafka namespace |
| `storage-class.yaml` | StorageClass for Minikube PV provisioning |
| `kafka-kraft.yaml` | KRaft-mode StatefulSet + Services (combined controllers/brokers) |
| `kafka-zookeeper.yaml` | Zookeeper ensemble + Kafka broker StatefulSet + Services |

Apply manually if needed:

```bash
kubectl apply -f manifests/namespace.yaml
kubectl apply -f manifests/storage-class.yaml
kubectl apply -f manifests/kafka-kraft.yaml    # OR kafka-zookeeper.yaml
```

## Integration Points

| Integration | How to connect |
|---|---|
| **Application code** | Bootstrap servers: `kafka-0.kafka-headless.kafka.svc.cluster.local:9092,kafka-1.kafka-headless.kafka.svc.cluster.local:9092,kafka-2.kafka-headless.kafka.svc.cluster.local:9092` |
| **External access (NodePort)** | `minikube service kafka-external --namespace kafka --url` |
| **Prometheus/Grafana** | Enable JMX exporter; scrape `kafka-jmx-metrics:5556` |
| **Dapr Pub/Sub** | Configure Dapr component with `brokers: kafka-headless.kafka.svc.cluster.local:9092` |

## Configuration Reference

For detailed Kafka configuration tuning (replication, retention, resource limits, security), see [references/kafka-config.md](references/kafka-config.md).

## Troubleshooting Quick Reference

| Symptom | Diagnostic command | Common fix |
|---|---|---|
| Broker pod `CrashLoopBackOff` | `kubectl logs kafka-0 -n kafka --previous` | Check memory limits, storage, config errors |
| Broker pod `Pending` | `kubectl describe pod kafka-0 -n kafka` | Insufficient resources or PVC not binding |
| PVC `Pending` | `kubectl describe pvc data-kafka-0 -n kafka` | Check StorageClass, Minikube storage addon |
| Topic creation fails | `kubectl exec kafka-0 -n kafka -- kafka-topics.sh --list --bootstrap-server localhost:9092` | Broker not fully ready, check logs |
| Consumer can't connect | `kubectl get svc -n kafka` | Verify service endpoints, check listener config |
| Controller election stuck | `kubectl logs kafka-0 -n kafka \| grep -i "quorum"` | Ensure all controller pods are running |
| Under-replicated partitions | `kubectl exec kafka-0 -n kafka -- kafka-topics.sh --describe --under-replicated-partitions --bootstrap-server localhost:9092` | Check broker health, disk space |
| Zookeeper not connecting | `kubectl logs zookeeper-0 -n kafka` | Check ZK ensemble health, verify 2181 port |
