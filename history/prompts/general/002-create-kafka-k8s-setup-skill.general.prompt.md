---
id: "002"
title: Create kafka-k8s-setup Skill for Minikube Kafka Deployment
stage: general
date: 2026-03-02
surface: agent
model: Claude Opus 4.6
feature: none
branch: main
user: saifullah
command: user-request
labels: ["kafka","kubernetes","minikube","skill-creator","kafka-k8s-setup","kraft","zookeeper","devops","statefulset"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/kafka-k8s-setup/SKILL.md
  - .claude/skills/kafka-k8s-setup/scripts/deploy-kafka.sh
  - .claude/skills/kafka-k8s-setup/scripts/verify-kafka.sh
  - .claude/skills/kafka-k8s-setup/scripts/teardown-kafka.sh
  - .claude/skills/kafka-k8s-setup/manifests/namespace.yaml
  - .claude/skills/kafka-k8s-setup/manifests/storage-class.yaml
  - .claude/skills/kafka-k8s-setup/manifests/kafka-kraft.yaml
  - .claude/skills/kafka-k8s-setup/manifests/kafka-zookeeper.yaml
  - .claude/skills/kafka-k8s-setup/references/kafka-config.md
tests:
  - Bash syntax validation passed for deploy-kafka.sh
  - Bash syntax validation passed for verify-kafka.sh
  - Bash syntax validation passed for teardown-kafka.sh
---

## Prompt

create a kafka-k8s-setup skill that will deploy kafka on k8s locally on my minikube sluster. its descirpion is as follows The **`kafka-k8s-setup`** skill is designed to transform a complex, multi-step infrastructure task into a single, executable command for an AI agent (like Claude, Goose, or Codex).

Instead of you manually writing YAML files and troubleshooting connection strings, this skill provides a **standardized blueprint** for deploying a production-ready Kafka cluster on Kubernetes.

---

## Core Responsibilities

The skill automates the three critical phases of lifecycle management for a message broker:

### 1. Infrastructure Provisioning

The skill handles the deployment of the Kafka ecosystem. Since Kafka is "stateful" (it remembers data), this isn't as simple as deploying a standard web app. The skill manages:

* **StatefulSets:** Ensuring each Kafka broker has a sticky identity and its own dedicated storage.
* **StorageClasses:** Provisioning Persistent Volumes (PVs) so your data survives if a pod restarts.
* **Listeners & Services:** Setting up Internal (ClusterIP) and potentially External (LoadBalancer/NodePort) access so your apps can actually reach the brokers.

### 2. Configuration & Cluster Mode

Depending on your requirements, the skill configures how Kafka operates:

* **KRaft vs. Zookeeper:** Automating the modern KRaft (Kafka Raft) metadata mode or the traditional Zookeeper ensemble.
* **Replication Factors:** Setting how many copies of your data exist across the cluster to prevent data loss.
* **Resource Limits:** Defining CPU and Memory "fences" so Kafka doesn't crash the rest of your Kubernetes nodes.

### 3. Automated "Smoke Testing" (Verification)

A unique part of your library's structure is the `verify script`. This skill doesn't just "apply" files; it confirms the system works by:

1. Waiting for all Broker pods to reach a `Ready` state.
2. Creating a dummy "test-topic."
3. Producing a test message and consuming it back to ensure the "plumbing" is functional.

## Response snapshot

Created the `kafka-k8s-setup` skill with the following 9 files across 4 directories:

1. **`SKILL.md`** — Main skill manifest with YAML frontmatter (name, description, trigger keywords), 4 workflows (deploy, verify, teardown, Helm alternative), manifest file reference table, integration points table (app code, external access, Prometheus, Dapr), and troubleshooting quick reference with 8 common issues.

2. **`scripts/deploy-kafka.sh`** — Full deployment script with 6 automated steps: prerequisite validation (kubectl, minikube, storage addon), namespace creation, StorageClass application, Kafka deployment (KRaft or Zookeeper mode with template variable substitution), optional NodePort external access, pod readiness wait loop (300s timeout), and automatic verification. Supports `--mode`, `--brokers`, `--storage`, `--namespace`, `--external`, `--dry-run` flags.

3. **`scripts/verify-kafka.sh`** — Smoke test script with 6 checks: broker pod readiness (with timeout polling), PVC binding status, service existence, topic creation, message produce, and message consume with integrity verification (sent == received). Reports pass/fail counts with colored output. Auto-detects Kafka CLI paths across different container images (apache/kafka, bitnami/kafka).

4. **`scripts/teardown-kafka.sh`** — Cleanup script that deletes StatefulSets, Services, ConfigMaps, Secrets, PVCs, remaining pods, namespace, and StorageClass. Supports `--keep-pvcs` for data retention, `--force` to skip confirmation, and `--namespace` targeting.

5. **`manifests/namespace.yaml`** — Kafka namespace with managed-by labels.

6. **`manifests/storage-class.yaml`** — Minikube-optimized StorageClass with `k8s.io/minikube-hostpath` provisioner, allowVolumeExpansion enabled.

7. **`manifests/kafka-kraft.yaml`** — KRaft-mode StatefulSet using `apache/kafka:3.8.1` image with combined controller+broker roles, inline config generation (node ID extraction from hostname, quorum voters string construction, storage formatting with shared cluster ID), headless + ClusterIP services, readiness/liveness probes, resource limits (512Mi-1Gi), and PVC template with configurable storage. Supports template placeholders `{{NAMESPACE}}`, `{{BROKERS}}`, `{{STORAGE}}`.

8. **`manifests/kafka-zookeeper.yaml`** — Zookeeper mode with 3-node Zookeeper ensemble (bitnami/zookeeper:3.9) + Kafka broker StatefulSet (bitnami/kafka:3.8). Includes headless + client services for both ZK and Kafka, env-based configuration, resource limits, and PVC templates.

9. **`references/kafka-config.md`** — Comprehensive configuration reference covering: cluster modes (KRaft vs Zookeeper), broker config property table (dev vs prod), listener configuration, replication & durability settings, resource sizing guidelines, storage (Minikube + AWS EBS examples), security (SASL/SCRAM, TLS, ACLs), JMX monitoring metrics, client connection strings (Python, Node.js, Go, Dapr), and performance tuning (high throughput vs low latency profiles).

## Outcome

- Impact: New `kafka-k8s-setup` skill available at `.claude/skills/kafka-k8s-setup/`; enables single-command Kafka deployment on Minikube with KRaft or Zookeeper mode, automated smoke testing, and full lifecycle management (deploy/verify/teardown).
- Tests: All 3 scripts passed `bash -n` syntax validation.
- Files: 9 files created across scripts/, manifests/, and references/ directories.
- Next prompts: Run `bash scripts/deploy-kafka.sh` on a running Minikube cluster to test in practice. Consider running `/sp.adr kafka-metadata-mode` to document the KRaft vs Zookeeper decision.
- Reflection: The skill follows the established convention from k8s-foundation with SKILL.md + scripts/ + references/ structure. KRaft mode is the default as it's the modern approach (production-ready since Kafka 3.6). Template variable substitution in manifests allows dynamic broker count and storage sizing.

## Evaluation notes (flywheel)

- Failure modes observed: none — all files created and validated successfully.
- Graders run and results (PASS/FAIL): bash -n syntax check PASS (3/3 scripts).
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Test deploy against live Minikube cluster; validate KRaft storage formatting with multi-broker setup.
