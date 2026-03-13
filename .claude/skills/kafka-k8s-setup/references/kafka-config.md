# Kafka Configuration Reference

Tuning guide for Kafka on Kubernetes. Covers broker config, replication, resource sizing, security, and monitoring.

## Table of Contents

- [Cluster Modes](#cluster-modes)
- [Broker Configuration](#broker-configuration)
- [Replication & Durability](#replication--durability)
- [Resource Sizing](#resource-sizing)
- [Storage](#storage)
- [Security](#security)
- [Monitoring & JMX](#monitoring--jmx)
- [Client Connection Strings](#client-connection-strings)
- [Performance Tuning](#performance-tuning)

---

## Cluster Modes

### KRaft Mode (Recommended)

KRaft eliminates the Zookeeper dependency. Available since Kafka 3.3, production-ready since 3.6.

```properties
process.roles=broker,controller
controller.quorum.voters=0@kafka-0:9093,1@kafka-1:9093,2@kafka-2:9093
controller.listener.names=CONTROLLER
```

**Advantages:**
- Simpler architecture (no Zookeeper to manage)
- Faster controller failover
- Fewer resources required
- Better scalability

**Requirements:**
- Kafka 3.3+ (3.6+ recommended for production)
- One-time storage format with `kafka-storage.sh`

### Zookeeper Mode (Legacy)

Traditional mode using a Zookeeper ensemble for metadata.

```properties
zookeeper.connect=zookeeper-0:2181,zookeeper-1:2181,zookeeper-2:2181
```

**When to use:**
- Kafka versions < 3.3
- Existing tooling depends on Zookeeper
- Migration path: start here, migrate to KRaft later

---

## Broker Configuration

### Key Properties

| Property | Default | Recommended (Dev) | Recommended (Prod) | Description |
|---|---|---|---|---|
| `num.partitions` | 1 | 3 | 6-12 | Default partitions per topic |
| `default.replication.factor` | 1 | 1 | 3 | Default topic replication |
| `min.insync.replicas` | 1 | 1 | 2 | Min replicas for acks=all |
| `log.retention.hours` | 168 | 24 | 168-720 | How long to keep data |
| `log.segment.bytes` | 1GB | 256MB | 1GB | Log segment file size |
| `num.network.threads` | 3 | 3 | 8 | Network request threads |
| `num.io.threads` | 8 | 8 | 16 | Disk I/O threads |
| `socket.request.max.bytes` | 100MB | 100MB | 100MB | Max request size |

### Listener Configuration

```properties
# Internal only (K8s cluster access)
listeners=PLAINTEXT://:9092
advertised.listeners=PLAINTEXT://${HOSTNAME}.kafka-headless.kafka.svc.cluster.local:9092

# Internal + External (NodePort access)
listeners=PLAINTEXT://:9092,EXTERNAL://:9094
advertised.listeners=PLAINTEXT://${HOSTNAME}.kafka-headless.kafka.svc.cluster.local:9092,EXTERNAL://<node-ip>:<nodeport>
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,EXTERNAL:PLAINTEXT
```

---

## Replication & Durability

### Development (single broker)

```properties
default.replication.factor=1
min.insync.replicas=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
```

### Production (3+ brokers)

```properties
default.replication.factor=3
min.insync.replicas=2
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2
```

### Producer `acks` Settings

| Setting | Durability | Throughput | Use Case |
|---|---|---|---|
| `acks=0` | None (fire-and-forget) | Highest | Metrics, logs (loss acceptable) |
| `acks=1` | Leader only | High | General use |
| `acks=all` | All ISR replicas | Lower | Financial, critical data |

---

## Resource Sizing

### Minikube / Development

```yaml
resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: "1"
    memory: 1Gi
env:
  - name: KAFKA_HEAP_OPTS
    value: "-Xmx512m -Xms512m"
```

### Production

```yaml
resources:
  requests:
    cpu: "2"
    memory: 4Gi
  limits:
    cpu: "4"
    memory: 8Gi
env:
  - name: KAFKA_HEAP_OPTS
    value: "-Xmx4g -Xms4g"
```

**Guidelines:**
- JVM heap should be ~50% of container memory limit
- Leave room for OS page cache (important for Kafka performance)
- CPU: 1 core minimum per broker, 2-4 for production
- Monitor `GC` times; increase heap if frequent full GCs

---

## Storage

### StorageClass for Minikube

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: kafka-storage
provisioner: k8s.io/minikube-hostpath
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

### Production StorageClass (example: AWS EBS)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: kafka-storage
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

### Sizing Guidelines

| Workload | Storage per Broker | IOPS |
|---|---|---|
| Dev / testing | 2-5 Gi | Default |
| Moderate | 50-100 Gi | 3000+ |
| High-throughput | 500 Gi - 1 Ti | 6000+ |

**Formula:** `storage = (msg_size × msgs_per_sec × retention_hours × 3600) / replication_factor`

---

## Security

### SASL/SCRAM Authentication

```properties
listeners=SASL_PLAINTEXT://:9092
security.inter.broker.protocol=SASL_PLAINTEXT
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512
sasl.enabled.mechanisms=SCRAM-SHA-512
```

### TLS Encryption

```properties
listeners=SSL://:9093
ssl.keystore.location=/etc/kafka/secrets/kafka.keystore.jks
ssl.keystore.password=${SSL_KEYSTORE_PASSWORD}
ssl.key.password=${SSL_KEY_PASSWORD}
ssl.truststore.location=/etc/kafka/secrets/kafka.truststore.jks
ssl.truststore.password=${SSL_TRUSTSTORE_PASSWORD}
```

### ACL Authorization

```properties
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer
super.users=User:admin
allow.everyone.if.no.acl.found=false
```

---

## Monitoring & JMX

### Enable JMX Exporter

Add to broker container env:

```yaml
env:
  - name: KAFKA_JMX_OPTS
    value: >-
      -Dcom.sun.management.jmxremote
      -Dcom.sun.management.jmxremote.port=5555
      -Dcom.sun.management.jmxremote.authenticate=false
      -Dcom.sun.management.jmxremote.ssl=false
  - name: JMX_PORT
    value: "5555"
```

### Key Metrics to Monitor

| Metric | What it tells you |
|---|---|
| `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec` | Incoming message rate |
| `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec` | Incoming byte rate |
| `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | Data at risk |
| `kafka.server:type=ReplicaManager,name=IsrShrinksPerSec` | ISR instability |
| `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` | Unavailable partitions |
| `kafka.network:type=RequestMetrics,name=TotalTimeMs` | Request latency |
| `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` | Broker load |

### Prometheus + Grafana

Use with `kube-prometheus-stack` (see `k8s-foundation` skill):

```bash
# Install JMX exporter as sidecar or use Bitnami's built-in metrics
helm upgrade kafka bitnami/kafka \
  --namespace kafka \
  --set metrics.jmx.enabled=true \
  --set metrics.serviceMonitor.enabled=true
```

---

## Client Connection Strings

### Internal (within K8s cluster)

```
# Headless service (for StatefulSet discovery)
kafka-0.kafka-headless.kafka.svc.cluster.local:9092,
kafka-1.kafka-headless.kafka.svc.cluster.local:9092,
kafka-2.kafka-headless.kafka.svc.cluster.local:9092

# ClusterIP service (load-balanced, for simple access)
kafka.kafka.svc.cluster.local:9092
```

### External (from host machine via Minikube)

```bash
# Get NodePort URL
minikube service kafka-external-0 --namespace kafka --url

# Or manually
MINIKUBE_IP=$(minikube ip)
NODEPORT=$(kubectl get svc kafka-external-0 -n kafka -o jsonpath='{.spec.ports[0].nodePort}')
echo "${MINIKUBE_IP}:${NODEPORT}"
```

### Application Configuration Examples

**Python (confluent-kafka):**
```python
from confluent_kafka import Producer
producer = Producer({
    'bootstrap.servers': 'kafka-headless.kafka.svc.cluster.local:9092'
})
```

**Node.js (kafkajs):**
```javascript
const { Kafka } = require('kafkajs');
const kafka = new Kafka({
  brokers: ['kafka-headless.kafka.svc.cluster.local:9092']
});
```

**Go (confluent-kafka-go):**
```go
producer, _ := kafka.NewProducer(&kafka.ConfigMap{
    "bootstrap.servers": "kafka-headless.kafka.svc.cluster.local:9092",
})
```

**Dapr Component:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-headless.kafka.svc.cluster.local:9092"
    - name: authType
      value: "none"
```

---

## Performance Tuning

### High Throughput

```properties
# Broker
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576
socket.request.max.bytes=104857600

# Topic
compression.type=lz4
batch.size=65536
linger.ms=5
```

### Low Latency

```properties
# Topic
compression.type=none
batch.size=16384
linger.ms=0

# Consumer
fetch.min.bytes=1
fetch.max.wait.ms=100
```

### Compacted Topics (for state stores)

```properties
cleanup.policy=compact
min.cleanable.dirty.ratio=0.5
segment.ms=604800000
delete.retention.ms=86400000
```
