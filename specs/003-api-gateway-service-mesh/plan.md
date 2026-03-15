# Implementation Plan: API Gateway & Service Mesh Setup

**Branch**: `003-api-gateway-service-mesh` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-api-gateway-service-mesh/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy Kong API Gateway and Dapr service mesh on Kubernetes (Minikube) to enable secure API routing with JWT authentication, service-to-service communication, pub/sub messaging, and health monitoring for all backend microservices. This establishes the foundational infrastructure for the multi-agent tutoring platform.

## Technical Context

**Language/Version**: YAML/Helm 3.x (configuration), Bash (deployment scripts)
**Primary Dependencies**: Kong API Gateway 3.x, Dapr 1.13+, Kubernetes 1.28+ (Minikube), Helm 3.x, Redis 7.x (Dapr state store), PostgreSQL 15+ (Kong database)
**Storage**: PostgreSQL (Kong configuration), Redis (Dapr pub/sub and state)
**Testing**: kubectl commands, curl/httpx for API testing, Dapr CLI for service invocation testing
**Target Platform**: Kubernetes (Minikube on Linux/WSL2)
**Project Type**: Infrastructure/DevOps (Kubernetes deployment configurations)
**Performance Goals**: <50ms gateway latency (p95), <100ms service-to-service latency (p95), <2s pub/sub delivery, 100 concurrent requests
**Constraints**: Minikube resource limits, local development only (no cloud), HTTP only (no TLS), single namespace deployment
**Scale/Scope**: 11 microservices, 4 pub/sub topics, ~20 Kong routes, single-cluster deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Phase 0)

#### Architecture Patterns Compliance
✅ **PASS** - Service Mesh (Dapr) aligns with constitution's preferred stack
✅ **PASS** - API Gateway (Kong) aligns with constitution's preferred stack
✅ **PASS** - Kubernetes orchestration aligns with constitution's preferred stack
✅ **PASS** - No business logic in this infrastructure layer (routing/auth only)

#### Security Constraints Compliance
✅ **PASS** - JWT authentication enforced at gateway level (constitution requirement)
✅ **PASS** - Rate limiting configured (10 req/min per user)
✅ **PASS** - No secrets in configuration files (will use Kubernetes secrets)
✅ **PASS** - Service-to-service communication isolated within K8s network

#### Performance Standards Compliance
✅ **PASS** - Gateway latency target <50ms aligns with constitution's <150ms for non-AI APIs
✅ **PASS** - Service invocation target <100ms is reasonable for internal calls
✅ **PASS** - Pub/sub delivery <2s meets async communication needs

#### Testing Principles Compliance
⚠️ **ATTENTION** - Infrastructure testing approach needs definition in Phase 0:
  - How to test Kong routing and JWT validation?
  - How to test Dapr service invocation and pub/sub?
  - Integration tests for gateway + services?

#### Development Workflow Compliance
✅ **PASS** - Using Helm charts for reproducible deployments
✅ **PASS** - Configuration as code (YAML manifests)
✅ **PASS** - Follows GitOps principles

#### Complexity Justification
✅ **PASS** - Kong + Dapr are necessary for microservices architecture
✅ **PASS** - No over-engineering detected (using standard tools, not custom solutions)

**INITIAL GATE STATUS**: ✅ PASS (with testing strategy to be defined in Phase 0)

---

### Post-Design Check (After Phase 1)

#### Architecture Patterns Compliance
✅ **PASS** - Repository pattern not applicable (infrastructure layer)
✅ **PASS** - LLM Provider Abstraction not applicable (infrastructure layer)
✅ **PASS** - Prompt Template Management not applicable (infrastructure layer)
✅ **PASS** - Anti-patterns avoided: no business logic, no hardcoded secrets, using Helm for reproducibility

#### Security Constraints Compliance
✅ **PASS** - JWT plugin configured with RS256 algorithm and public key validation
✅ **PASS** - Request Transformer extracts user_id, role, email from JWT claims
✅ **PASS** - Rate limiting per authenticated consumer (10 req/min for students, higher for teachers)
✅ **PASS** - CORS configured with explicit allowed origins (no wildcards)
✅ **PASS** - Secrets stored in Kubernetes Secrets (redis-secret, kong-jwt-public-key)
✅ **PASS** - Service-to-service communication via Dapr (isolated within cluster)

#### Performance Standards Compliance
✅ **PASS** - Kong health checks: active (5s interval) + passive monitoring
✅ **PASS** - Dapr resiliency: retries (3 attempts), circuit breakers (5 consecutive failures)
✅ **PASS** - Redis used for Kong rate limiting and Dapr pub/sub (shared infrastructure)
✅ **PASS** - Resource limits defined: Kong (500m CPU, 512Mi RAM), Dapr sidecars configurable

#### Testing Principles Compliance
✅ **RESOLVED** - Testing strategy defined in research.md:
  - Integration tests with pytest + httpx for Kong routing and JWT validation (85% coverage target)
  - Integration tests with pytest + Dapr Python SDK for service invocation (80% coverage target)
  - Integration tests for pub/sub message delivery (80% coverage target)
  - E2E tests for full gateway + mesh flow (70% coverage target)
  - Test patterns documented with fixtures and mocking strategies

#### Development Workflow Compliance
✅ **PASS** - Helm charts for Kong and Dapr (reproducible deployments)
✅ **PASS** - Declarative configuration (kong-configuration.yaml, dapr-*.yaml)
✅ **PASS** - Deployment scripts (setup-minikube.sh, deploy-*.sh) for automation
✅ **PASS** - Quickstart guide documents full deployment process
✅ **PASS** - GitOps-ready (all configuration in version control)

#### Multi-Agent Architecture Standards
✅ **PASS** - Dapr service invocation enables agent communication
✅ **PASS** - Pub/sub topics defined for agent events (struggle-alerts, quiz-completed, code-submitted, mastery-updated)
✅ **PASS** - Dapr access control configured (only triage-agent can call other agents)
✅ **PASS** - Dead letter topics configured for failed message handling

#### Business Logic Integrity
✅ **PASS** - No business logic in infrastructure layer (routing and auth only)
✅ **PASS** - Rate limiting enforces fair usage (constitution requirement)
✅ **PASS** - Struggle detection will be handled by backend services (not gateway)

#### Complexity Justification
✅ **PASS** - Kong + Dapr are standard tools (not custom solutions)
✅ **PASS** - Configuration complexity justified by microservices architecture requirements
✅ **PASS** - No premature optimization (using defaults where appropriate)

**FINAL GATE STATUS**: ✅ PASS - All constitution requirements met. Ready for Phase 2 (Tasks).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
infrastructure/
├── kubernetes/
│   ├── kong/
│   │   ├── values.yaml           # Kong Helm chart configuration
│   │   ├── jwt-plugin.yaml       # JWT authentication plugin config
│   │   ├── rate-limit-plugin.yaml # Rate limiting plugin config
│   │   └── routes.yaml           # API route definitions
│   ├── dapr/
│   │   ├── config.yaml           # Dapr configuration
│   │   ├── components/
│   │   │   ├── pubsub.yaml       # Redis pub/sub component
│   │   │   └── statestore.yaml   # Redis state store component
│   │   └── subscriptions/
│   │       ├── struggle-alerts.yaml
│   │       ├── quiz-completed.yaml
│   │       ├── code-submitted.yaml
│   │       └── mastery-updated.yaml
│   ├── redis/
│   │   └── values.yaml           # Redis Helm chart configuration
│   └── services/
│       ├── auth-service.yaml     # Service + Deployment manifests
│       ├── user-service.yaml
│       ├── sandbox-service.yaml
│       ├── llm-service.yaml
│       ├── triage-agent.yaml
│       ├── concepts-agent.yaml
│       ├── code-review-agent.yaml
│       ├── debug-agent.yaml
│       ├── exercise-agent.yaml
│       ├── progress-agent.yaml
│       └── teacher-service.yaml
│
├── scripts/
│   ├── setup-minikube.sh         # Initialize Minikube cluster
│   ├── deploy-kong.sh            # Deploy Kong with Helm
│   ├── deploy-dapr.sh            # Deploy Dapr with Helm
│   ├── deploy-redis.sh           # Deploy Redis for Dapr
│   ├── deploy-services.sh        # Deploy all microservices
│   ├── test-gateway.sh           # Test Kong routing and auth
│   ├── test-service-mesh.sh      # Test Dapr invocation and pub/sub
│   └── teardown.sh               # Clean up all resources
│
└── docs/
    ├── kong-setup.md             # Kong deployment guide
    ├── dapr-setup.md             # Dapr deployment guide
    ├── service-mesh-patterns.md  # Service communication patterns
    └── troubleshooting.md        # Common issues and solutions

tests/
├── integration/
│   ├── test_kong_routing.py      # Test API routing through Kong
│   ├── test_jwt_validation.py    # Test JWT authentication
│   ├── test_rate_limiting.py     # Test rate limit enforcement
│   ├── test_dapr_invocation.py   # Test service-to-service calls
│   └── test_pubsub.py            # Test pub/sub messaging
└── e2e/
    └── test_full_flow.py         # End-to-end gateway + mesh test
```

**Structure Decision**: Infrastructure-focused layout with Kubernetes manifests, Helm configurations, deployment scripts, and integration tests. All configuration is declarative (YAML) and version-controlled. Scripts automate deployment to Minikube for reproducible local development.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All architectural choices align with the constitution's preferred stack and principles.
