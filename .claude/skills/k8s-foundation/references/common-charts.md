# Common Helm Charts Reference

Quick reference for popular, production-ready Helm charts. Each entry includes the repo, install command, and recommended values to consider.

## Table of Contents

- [Ingress Controllers](#ingress-controllers)
- [TLS / Certificate Management](#tls--certificate-management)
- [Monitoring & Observability](#monitoring--observability)
- [Logging](#logging)
- [Databases](#databases)
- [Caching](#caching)
- [Storage](#storage)
- [Security](#security)

---

## Ingress Controllers

### NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.resources.requests.cpu=100m \
  --set controller.resources.requests.memory=90Mi
```

**Key values:**
- `controller.replicaCount` — HA setup (min 2 for production)
- `controller.service.type` — LoadBalancer (cloud) or NodePort (bare-metal)
- `controller.ingressClassResource.default` — set `true` to make default class
- `controller.metrics.enabled` — expose Prometheus metrics

### Traefik

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm install traefik traefik/traefik \
  --namespace traefik --create-namespace
```

**Key values:**
- `deployment.replicas` — HA setup
- `providers.kubernetesCRD.enabled` — enable CRD-based IngressRoute
- `metrics.prometheus` — Prometheus integration

---

## TLS / Certificate Management

### cert-manager

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true \
  --set replicaCount=2
```

**Key values:**
- `crds.enabled=true` — install CRDs with chart (recommended)
- `replicaCount` — HA for production
- After install, create a `ClusterIssuer` for Let's Encrypt:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: nginx
```

---

## Monitoring & Observability

### kube-prometheus-stack (Prometheus + Grafana + Alertmanager)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.adminPassword=changeme \
  --set prometheus.prometheusSpec.retention=15d \
  --set prometheus.prometheusSpec.resources.requests.memory=512Mi
```

**Key values:**
- `grafana.adminPassword` — change from default
- `prometheus.prometheusSpec.retention` — data retention period
- `prometheus.prometheusSpec.storageSpec` — persistent storage for metrics
- `alertmanager.config` — alerting routes and receivers
- `grafana.persistence.enabled=true` — persist Grafana dashboards

### metrics-server

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
helm install metrics-server metrics-server/metrics-server \
  --namespace kube-system \
  --set args={--kubelet-insecure-tls}  # only for dev/self-signed certs
```

**Key values:**
- `args` — `--kubelet-insecure-tls` for development clusters with self-signed certs
- `replicas` — HA setup for production

---

## Logging

### Loki + Promtail (Grafana Loki stack)

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install loki grafana/loki-stack \
  --namespace logging --create-namespace \
  --set grafana.enabled=false \
  --set promtail.enabled=true \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi
```

**Key values:**
- `grafana.enabled` — set `false` if using kube-prometheus-stack Grafana
- `loki.persistence.enabled` — persist log data
- `promtail.config.snippets` — custom scrape configs

---

## Databases

### PostgreSQL (Bitnami)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgresql bitnami/postgresql \
  --namespace database --create-namespace \
  --set auth.postgresPassword=changeme \
  --set primary.persistence.size=20Gi \
  --set primary.resources.requests.memory=256Mi \
  --set primary.resources.requests.cpu=250m
```

**Key values:**
- `auth.postgresPassword` — superuser password (use a Secret in production)
- `auth.database` — default database name
- `primary.persistence.size` — PVC size
- `architecture` — `standalone` or `replication`

### Redis (Bitnami)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install redis bitnami/redis \
  --namespace cache --create-namespace \
  --set auth.password=changeme \
  --set architecture=standalone \
  --set master.resources.requests.memory=128Mi
```

**Key values:**
- `architecture` — `standalone` or `replication`
- `auth.password` — Redis password
- `master.persistence.size` — PVC size

---

## Caching

### Memcached (Bitnami)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install memcached bitnami/memcached \
  --namespace cache --create-namespace \
  --set resources.requests.memory=128Mi
```

---

## Storage

### MinIO (S3-compatible object storage)

```bash
helm repo add minio https://charts.min.io/
helm repo update
helm install minio minio/minio \
  --namespace storage --create-namespace \
  --set rootUser=admin \
  --set rootPassword=changeme123 \
  --set persistence.size=50Gi \
  --set mode=standalone
```

**Key values:**
- `mode` — `standalone` or `distributed`
- `persistence.size` — storage capacity
- `resources.requests.memory` — memory allocation

---

## Security

### External Secrets Operator

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm repo update
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets --create-namespace \
  --set installCRDs=true
```

**Key values:**
- `installCRDs` — install CRDs with chart
- After install, create a `SecretStore` or `ClusterSecretStore` pointing to your secrets backend (AWS SSM, Vault, GCP SM, etc.)
