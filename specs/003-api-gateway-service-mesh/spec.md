# Feature Specification: API Gateway & Service Mesh Setup

**Feature Branch**: `003-api-gateway-service-mesh`
**Created**: 2026-03-15
**Status**: Draft
**Input**: User description: "003-api-gateway-service-mesh"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure API Access with JWT Authentication (Priority: P1)

As a frontend application, I need all API requests to be authenticated and routed through a central gateway so that only authorized users can access backend services.

**Why this priority**: This is the foundation for all API communication. Without secure routing and authentication, no other features can function safely.

**Independent Test**: Can be fully tested by sending authenticated and unauthenticated requests to any backend service through Kong and verifying JWT validation works correctly. Delivers immediate security value.

**Acceptance Scenarios**:

1. **Given** a valid JWT token in the request header, **When** the frontend sends a request to `/api/users/me`, **Then** Kong validates the token and routes the request to the user service
2. **Given** an invalid or expired JWT token, **When** the frontend sends a request to any API endpoint, **Then** Kong returns 401 Unauthorized without forwarding to backend services
3. **Given** no JWT token in the request, **When** the frontend sends a request to a protected endpoint, **Then** Kong returns 401 Unauthorized
4. **Given** a valid JWT token with role "student", **When** the request is made to a teacher-only endpoint, **Then** Kong returns 403 Forbidden

---

### User Story 2 - Service-to-Service Communication via Dapr (Priority: P1)

As a backend microservice, I need to communicate with other services through Dapr so that service discovery, retries, and observability are handled automatically.

**Why this priority**: Enables the microservices architecture. All agents and services depend on reliable inter-service communication.

**Independent Test**: Can be tested by deploying two services with Dapr sidecars and verifying they can invoke each other using Dapr service invocation. Delivers decoupled service communication.

**Acceptance Scenarios**:

1. **Given** the triage-agent service needs to call the concepts-agent, **When** it uses Dapr service invocation, **Then** the request is routed correctly and a response is received
2. **Given** a service publishes a "struggle-alert" event to Dapr pub/sub, **When** the teacher-service subscribes to this topic, **Then** the teacher-service receives the event
3. **Given** a target service is temporarily unavailable, **When** a service invokes it via Dapr, **Then** Dapr automatically retries with exponential backoff
4. **Given** multiple instances of a service are running, **When** another service invokes it via Dapr, **Then** Dapr load balances the request across instances

---

### User Story 3 - Rate Limiting for API Protection (Priority: P2)

As a platform operator, I need API rate limiting to prevent abuse and ensure fair resource usage across all users.

**Why this priority**: Protects the platform from abuse but not critical for initial functionality. Can be added after basic routing works.

**Independent Test**: Can be tested by sending multiple rapid requests from a single user and verifying rate limits are enforced. Delivers resource protection.

**Acceptance Scenarios**:

1. **Given** a user has made 10 requests in the last minute, **When** they make an 11th request, **Then** Kong returns 429 Too Many Requests
2. **Given** a user has been rate limited, **When** they wait 60 seconds and retry, **Then** the request succeeds
3. **Given** two different users making requests, **When** one user hits the rate limit, **Then** the other user's requests continue to work normally

---

### User Story 4 - Health Monitoring and Service Discovery (Priority: P2)

As a platform operator, I need health checks for all services so that I can detect failures and ensure system reliability.

**Why this priority**: Important for production readiness but not blocking initial development. Services can run without health checks initially.

**Independent Test**: Can be tested by deploying services with health endpoints and verifying Kong/Dapr can detect unhealthy services. Delivers operational visibility.

**Acceptance Scenarios**:

1. **Given** all services are running normally, **When** Kong checks service health, **Then** all services report healthy status
2. **Given** a service becomes unresponsive, **When** Kong performs health checks, **Then** Kong stops routing traffic to that service instance
3. **Given** a service recovers from failure, **When** it starts responding to health checks, **Then** Kong resumes routing traffic to it
4. **Given** Dapr sidecars are deployed, **When** querying Dapr health endpoints, **Then** each sidecar reports its health status

---

### User Story 5 - Pub/Sub Event Distribution (Priority: P1)

As a backend service, I need to publish and subscribe to events asynchronously so that services can react to important system events without tight coupling.

**Why this priority**: Critical for features like struggle alerts and notifications. Enables event-driven architecture from the start.

**Independent Test**: Can be tested by publishing events to Dapr topics and verifying subscribers receive them. Delivers asynchronous communication capability.

**Acceptance Scenarios**:

1. **Given** the debug-agent detects a student struggling, **When** it publishes a "struggle-alert" event, **Then** the teacher-service receives the alert within 2 seconds
2. **Given** a student completes a quiz, **When** the exercise-agent publishes a "quiz-completed" event, **Then** the progress-agent receives it and updates mastery scores
3. **Given** multiple services subscribe to the same topic, **When** an event is published, **Then** all subscribers receive the event
4. **Given** a subscriber is temporarily offline, **When** it comes back online, **Then** it receives events published during its downtime (if configured for message persistence)

---

### Edge Cases

- What happens when Kong gateway itself becomes unavailable? (All API requests fail; need monitoring and alerting)
- How does the system handle a Dapr sidecar crash? (Service becomes unreachable; Kubernetes should restart the sidecar)
- What happens when rate limit is reached during critical operations? (User receives 429 error; frontend should implement retry with backoff)
- How does the system handle circular service invocations? (Dapr has built-in circuit breakers; should be configured with timeouts)
- What happens when a pub/sub message cannot be delivered after retries? (Message goes to dead letter queue; needs monitoring)
- How does Kong handle malformed JWT tokens? (Returns 401 with error details; should not crash)
- What happens when a service takes longer than expected to respond? (Dapr timeout triggers; calling service receives timeout error)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deploy Kong API Gateway on Kubernetes (Minikube) with JWT authentication plugin configured
- **FR-002**: System MUST validate JWT tokens on all API requests before routing to backend services
- **FR-003**: System MUST route API requests to appropriate backend microservices based on URL path patterns
- **FR-004**: System MUST enforce rate limiting of 10 requests per minute per authenticated user
- **FR-005**: System MUST deploy Dapr sidecars alongside all backend microservices
- **FR-006**: System MUST enable service-to-service communication exclusively through Dapr service invocation
- **FR-007**: System MUST provide Dapr pub/sub capability for asynchronous event distribution
- **FR-008**: System MUST support the following pub/sub topics: struggle-alerts, quiz-completed, code-submitted, mastery-updated
- **FR-009**: System MUST expose health check endpoints for Kong gateway and all backend services
- **FR-010**: System MUST handle CORS requests from the frontend application
- **FR-011**: System MUST add user_id and role claims from JWT to request headers when forwarding to backend services
- **FR-012**: System MUST log all gateway requests with timestamp, user_id, endpoint, and response status
- **FR-013**: System MUST return appropriate HTTP status codes (401 for unauthorized, 403 for forbidden, 429 for rate limited, 503 for service unavailable)
- **FR-014**: System MUST support the following microservices: auth-service, user-service, sandbox-service, llm-service, triage-agent, concepts-agent, code-review-agent, debug-agent, exercise-agent, progress-agent, teacher-service
- **FR-015**: System MUST configure Dapr with automatic retries and exponential backoff for failed service invocations
- **FR-016**: System MUST deploy all components using Helm charts for reproducible deployments
- **FR-017**: System MUST configure Kong routes for the following path patterns: /api/auth/*, /api/users/*, /api/sandbox/*, /api/agents/*, /api/teacher/*
- **FR-018**: System MUST support local development on Minikube with full Kong and Dapr functionality

### Key Entities

- **API Gateway (Kong)**: Central entry point for all API requests; handles authentication, rate limiting, and routing to backend services
- **Service Mesh (Dapr)**: Provides service-to-service communication, pub/sub messaging, state management, and observability for microservices
- **Microservice**: Independent backend service with Dapr sidecar; communicates with other services exclusively through Dapr
- **JWT Token**: Authentication credential containing user_id and role claims; validated by Kong on every request
- **Pub/Sub Topic**: Named channel for asynchronous event distribution; services publish events and subscribe to topics of interest
- **Health Endpoint**: HTTP endpoint exposed by each service returning health status; used by Kong and Kubernetes for service health monitoring
- **Route**: Kong configuration mapping URL path patterns to backend service addresses

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All API requests are authenticated and routed through Kong gateway with JWT validation completing in under 50ms
- **SC-002**: Services can invoke each other through Dapr with end-to-end latency under 100ms for 95% of requests
- **SC-003**: Pub/sub events are delivered to all subscribers within 2 seconds of publication
- **SC-004**: Rate limiting correctly blocks requests exceeding 10 per minute per user with 100% accuracy
- **SC-005**: System correctly handles 100 concurrent API requests without errors or timeouts
- **SC-006**: Health checks detect service failures within 10 seconds and stop routing traffic to unhealthy instances
- **SC-007**: All 11 microservices can be deployed to Minikube and communicate successfully through the service mesh
- **SC-008**: Unauthorized requests (missing or invalid JWT) are rejected with 401 status before reaching backend services
- **SC-009**: Kong gateway uptime exceeds 99.9% during normal operations
- **SC-010**: Service-to-service communication failures trigger automatic retries with exponential backoff

## Assumptions *(optional)*

- Minikube is already installed and configured on the development machine
- kubectl is installed and configured to communicate with Minikube
- Helm 3.x is installed for deploying Kong and Dapr
- Backend microservices expose standard HTTP endpoints for health checks (e.g., /health or /healthz)
- JWT tokens are issued by the auth-service (F01) and contain user_id and role claims
- All services run in the same Kubernetes namespace for simplified service discovery
- Dapr uses Redis as the default state store and message broker (deployed in Minikube)
- Kong database mode is used (PostgreSQL) rather than DB-less mode for easier configuration management
- Frontend application is configured to include JWT token in Authorization header for all API requests
- Services are designed to be stateless to support horizontal scaling

## Dependencies *(optional)*

- **F01 (Authentication & Authorization)**: Provides JWT token generation and validation logic; Kong needs to understand the JWT format and signing key
- **Kubernetes/Minikube**: Required infrastructure for deploying Kong, Dapr, and all microservices
- **Helm**: Package manager for deploying Kong and Dapr with proper configurations
- **Redis**: Required by Dapr for pub/sub message broker and state store
- **PostgreSQL**: Required by Kong for storing gateway configuration (routes, plugins, consumers)

## Out of Scope *(optional)*

- Advanced Kong plugins (request transformation, response caching, API analytics)
- Distributed tracing with Zipkin or Jaeger (basic logging only)
- Prometheus metrics collection and Grafana dashboards (health checks only)
- Multi-cluster or multi-region deployments (Minikube single-cluster only)
- API versioning strategies (all services use /api/v1 implicitly)
- Advanced Dapr features (actors, bindings, configuration management)
- SSL/TLS termination at Kong (HTTP only for local development)
- Custom error pages or error response transformation
- API documentation generation (Swagger/OpenAPI)
- Load testing or performance benchmarking
- Disaster recovery or backup strategies
- Production deployment to cloud Kubernetes (AWS EKS, GCP GKE, Azure AKS)

## Non-Functional Requirements *(optional)*

### Performance
- Gateway request processing latency: < 50ms (p95)
- Service-to-service invocation latency: < 100ms (p95)
- Pub/sub message delivery latency: < 2 seconds
- System supports 100 concurrent requests without degradation

### Reliability
- Gateway uptime: 99.9%
- Automatic retry on transient failures (3 attempts with exponential backoff)
- Circuit breaker triggers after 5 consecutive failures
- Health checks every 10 seconds with 3-failure threshold

### Security
- All API requests require valid JWT authentication
- JWT tokens validated before routing to backend services
- Rate limiting prevents abuse (10 req/min per user)
- Service-to-service communication isolated within Kubernetes network
- No external network access from backend services (except LLM service)

### Scalability
- Kong gateway can scale horizontally (multiple replicas)
- Each microservice can scale independently
- Dapr handles service discovery automatically as services scale
- Pub/sub supports multiple subscribers per topic

### Observability
- All gateway requests logged with user_id, endpoint, status, timestamp
- Health endpoints for all services
- Dapr provides built-in metrics endpoints
- Failed requests logged with error details

## Open Questions *(optional)*

None - all requirements are clear based on the discussion with the user.
