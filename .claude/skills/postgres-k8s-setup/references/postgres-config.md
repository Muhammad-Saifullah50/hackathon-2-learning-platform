# PostgreSQL Configuration Guide

This document provides guidance for configuring PostgreSQL in Kubernetes environments, particularly for development and testing scenarios.

## Resource Allocation

### Memory Settings

For development environments:
- Shared Buffers: 25% of total system RAM (minimum 128MB)
- Effective Cache Size: 50% of total system RAM
- Work Mem: 4-8MB per connection
- Maintenance Work Mem: 64-256MB

Example settings in postgresql.conf:
```
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### CPU Settings

- Default max_connections: 100-200 connections
- Effective CPU cores: 1-2 cores for development
- Background workers: 1-2 for typical workloads

## Storage Configuration

### Persistent Volume Claims

For development:
- Storage Class: default (for Minikube)
- Size: 5-10Gi minimum
- Access Mode: ReadWriteOnce

For production:
- Storage Class: provisioned by your cloud provider
- Size: 50Gi+ depending on data requirements
- Access Mode: ReadWriteOnce

### WAL Configuration

For development:
```
wal_level = minimal
archive_mode = off
checkpoint_completion_target = 0.5
```

For production:
```
wal_level = replica
archive_mode = on
checkpoint_completion_target = 0.9
```

## Security Settings

### Authentication

For development:
- md5 authentication (default)
- Local connections via peer authentication

For production:
- scram-sha-256 authentication
- SSL/TLS enabled
- Certificate-based authentication

### Network Security

- Listen addresses: 0.0.0.0 (for external access)
- Port: 5432
- SSL: Enabled in production

## Monitoring and Metrics

### Required Extensions

For development:
- pg_stat_statements (for query performance)
- auto_explain (for query analysis)

### Prometheus Exporter

Enable metrics with:
```bash
helm install postgres-exporter bitnami/prometheus-postgres-exporter \
  --set postgresql.password=your-password \
  --set postgresql.host=postgres-headless.postgres.svc.cluster.local
```

## Backup and Recovery

### WAL Archiving

For production environments:
```
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'
```

### Logical Backups

Use pg_dump for logical backups:
```bash
pg_dump -h postgres -U postgres -d appdb > backup.sql
```

### Physical Backups

Use rsync or tar for physical backups:
```bash
tar -czf backup.tar.gz /var/lib/postgresql/data
```

## Performance Tuning

### Connection Pooling

For development:
- pgbouncer: 10-20 connections
- max_connections: 100

For production:
- pgbouncer: 50-100 connections
- max_connections: 200+

### Query Optimization

- Enable query planner statistics
- Regular ANALYZE operations
- Index maintenance

### Maintenance Operations

Regular maintenance tasks:
- VACUUM ANALYZE
- REINDEX
- Statistics updates
