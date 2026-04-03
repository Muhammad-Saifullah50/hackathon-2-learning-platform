# Quickstart: AI Agent Layer

## Prerequisites

- Features F01-F06 complete and deployed (auth, database, gateway, user management, sandbox, LLM provider)
- PostgreSQL database running with all prior migrations applied
- LLM provider configured and operational (verify with `POST /api/v1/llm/chat`)
- Docker sandbox running (verify with `POST /api/v1/code/execute`)

## Setup

### 1. Run the migration

```bash
cd backend
alembic upgrade head
```

This creates 6 new tables: `agent_sessions`, `routing_decisions`, `hint_progressions`, `exercises`, `exercise_submissions`, `mastery_records`.

Verify:
```bash
psql $DATABASE_URL -c "\dt agent_*"
psql $DATABASE_URL -c "\dt routing_*"
psql $DATABASE_URL -c "\dt hint_*"
psql $DATABASE_URL -c "\dt exercise*"
psql $DATABASE_URL -c "\dt mastery_*"
```

### 2. Start the backend

```bash
cd backend
uvicorn src.main:app --reload
```

Verify the agent endpoint is registered:
```bash
curl http://localhost:8000/docs | grep -i agent
# Should show /api/v1/agents/chat and related endpoints
```

### 3. Test the Triage Agent routing

```bash
# Get a valid JWT first (login via /api/v1/auth/login)
TOKEN="your_jwt_token"

# Test concept-explanation intent
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a list comprehension?", "topic": "loops"}'

# Test code-debug intent
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Why does my code say TypeError: can only concatenate str to int?", "code_snippet": "x = \"hello\" + 5"}'

# Test code-review intent
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Review my code please", "code_snippet": "def add(a,b):return a+b"}'

# Test exercise-generation intent
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me a practice exercise on functions"}'

# Test progress-summary intent
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "How am I doing in this course?"}'

# Test fallback (ambiguous intent)
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "asdfjkl"}'
```

### 4. Run the tests

```bash
cd backend
# Unit tests (triage routing, agent services, schemas)
pytest tests/unit/test_triage_routing.py -v
pytest tests/unit/test_concepts_agent.py -v
pytest tests/unit/test_debug_agent.py -v
pytest tests/unit/test_exercise_agent.py -v
pytest tests/unit/test_progress_agent.py -v
pytest tests/unit/test_agent_schemas.py -v

# Integration tests (FastAPI routes)
pytest tests/integration/test_agent_routes.py -v

# Contract tests (OpenAPI compliance)
pytest tests/contract/test_agent_api.py -v
```

### 5. Validate success criteria

| Criterion | How to Validate |
|-----------|----------------|
| SC-001: Routing < 5s | Measure time from request to first SSE event |
| SC-002: 90% classification accuracy | Run 100 test queries through triage, check intent match |
| SC-006: 100% grading accuracy | Submit known-correct/incorrect solutions, verify scores |
| SC-007: Mastery matches manual calc | Seed test data, compare agent output to hand calculation |
| SC-008: First token < 1.5s | Measure time to first SSE `token` event |
| SC-010: Fallback < 5% | Log routing decisions over 100 queries, count "general" intent |
