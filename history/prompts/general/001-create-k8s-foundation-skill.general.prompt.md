---
id: "001"
title: Create k8s-foundation Skill for Cluster Health and Helm
stage: general
date: 2026-03-02
surface: agent
model: Claude Opus 4.6
feature: none
branch: main
user: saifullah
command: skill-creator (invoked via skill)
labels: ["kubernetes","helm","skill-creator","k8s-foundation","cluster-health","devops"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - /home/saifullah/.claude/skills/k8s-foundation/SKILL.md
  - /home/saifullah/.claude/skills/k8s-foundation/scripts/cluster-health.sh
  - /home/saifullah/.claude/skills/k8s-foundation/references/common-charts.md
  - /home/saifullah/.claude/skills/k8s-foundation.skill
tests:
  - Bash syntax validation passed for cluster-health.sh
  - Skill packaging validated successfully by package_skill.py
---

## Prompt

create a k8s-foundation skill usign the skill creator skill . I will use it to check cluster health and apply basic helm charts

## Response snapshot

Created the `k8s-foundation` skill via the skill-creator skill with the following components:

1. **`SKILL.md`** — Main skill manifest with workflows for cluster health sweep (12 diagnostic areas), Helm install/upgrade with values files and set overrides, release verification, and a troubleshooting quick reference table.

2. **`scripts/cluster-health.sh`** — Full diagnostic shell script covering: cluster info, node status + resource usage, namespaces, pod health (non-running, restarts), deployments (under-replicated), daemonsets, statefulsets, PVCs (unbound), services, warning events, resource quotas, limit ranges, and a summary pass/fail indicator.

3. **`references/common-charts.md`** — Curated reference for popular Helm charts: nginx-ingress, Traefik, cert-manager (with ClusterIssuer example), kube-prometheus-stack, metrics-server, Loki+Promtail, PostgreSQL, Redis, Memcached, MinIO, External Secrets Operator.

4. **`k8s-foundation.skill`** — Packaged distributable skill file.

## Outcome

- Impact: New reusable `k8s-foundation` skill available at `~/.claude/skills/k8s-foundation/`; enables rapid cluster diagnostics and Helm operations.
- Tests: Script syntax validated; skill packaging validated.
- Files: 4 files created (SKILL.md, cluster-health.sh, common-charts.md, k8s-foundation.skill).
- Next: Invoke skill with "check cluster health" or "helm install cert-manager" to test in practice.

## Evaluation notes (flywheel)

- Failure modes observed: none — skill-creator scaffolding completed without errors.
- Graders run and results: Packaging validation PASS; bash -n syntax check PASS.
- Next experiment: Test against a live cluster and iterate on output formatting.
