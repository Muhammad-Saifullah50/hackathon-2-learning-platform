# Implementation Plan: AI Agent Layer (F07-F12)

**Branch**: `007-agent-layer` | **Date**: 2026-04-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-agent-layer/spec.md`

## Summary

Build a single FastAPI service layer that orchestrates 6 AI tutoring agents (Triage, Concepts, Code Review, Debug, Exercise, Progress) using deterministic code-based routing, the existing LLM provider abstraction (F06), and the existing code sandbox (F05). Agents communicate via well-defined interfaces with independent prompt templates, streaming responses, and SQLAlchemy-backed session/conversation persistence.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing backend)
**Primary Dependencies**: FastAPI, LiteLLM (via existing LlmClient), SQLAlchemy 2.0 (async sessions), Pydantic v2
**Storage**: Neon PostgreSQL via existing async engine — new tables for agent sessions, routing decisions, hint progression, exercises, exercise submissions, mastery records
**Testing**: pytest + httpx async client (unit + integration), matching existing backend test patterns
**Target Platform**: Linux server (Kubernetes deployment via existing infrastructure)
**Project Type**: Web application — backend API layer (frontend chat UI is out of scope, F15)
**Performance Goals**:
- Routing decision < 50ms (deterministic, no LLM call)
- AI first token (streaming): < 1.2s (P95, per constitution)
- AI full response: 30s timeout (per constitution)
- Code execution during grading: < 3s (hard limit: 8s)
**Constraints**:
- Single FastAPI service (no microservices per AGENTS.md anti-pattern)
- All LLM calls through existing LlmClient + LlmService
- All code execution through existing DockerSandbox
- All routes require auth via `get_current_user` dependency
- Rate limiting enforced at gateway (F03), agents respect limits
**Scale/Scope**: 50 concurrent student-agent sessions (SC-009), 8-module curriculum

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitution Requirement | Status | Notes |
|--------------------------|--------|-------|
| Python: black + isort formatting | PASS | Will run on all new files |
| FastAPI routes: `summary=` + `description=` | PASS | All agent endpoints will include |
| Google-style docstrings on business logic | PASS | All agent service methods |
| Repository Pattern for DB access | PASS | New repos for sessions, routing, exercises, mastery |
| LLM Provider Abstraction | PASS | All agents use existing LlmClient/LlmService |
| Auth by default via `get_current_user` | PASS | All agent routes protected |
| Streaming all AI responses | PASS | StreamingResponse + SSE for all agent outputs |
| Code sandbox isolation (F05) | PASS | Exercise grading via DockerSandbox only |
| No `exec()`/`eval()` on server | PASS | Sandbox-only execution |
| Rate limits: 10 req/min per user | PASS | Enforced at gateway (F03) |
| Latency budgets honored | PASS | Design targets match constitution budgets |
| Agent communication via interfaces | PASS | No shared state, well-defined schemas |
| Deterministic triage routing | PASS | Code-based keyword/intent matching, not LLM |
| Prompt template management | PASS | Independent prompts per agent in `llm/prompts.py` |
| DB indexes on `user_id`, `session_id`, `created_at` | PASS | Will add from day one |
| Mastery formula unchanged (40/30/20/10) | PASS | Fixed per constitution |
| Mastery levels fixed thresholds | PASS | 0-40/41-70/71-90/91-100 |
| Struggle detection triggers | PASS | All 5 triggers implemented |

## Project Structure

### Documentation (this feature)

```text
specs/007-agent-layer/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── agent-api.yaml   # OpenAPI spec for agent endpoints
└── tasks.md             # Phase 2 output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/v1/
│   │   └── agents.py                    # Agent route handlers (streaming endpoints)
│   ├── services/
│   │   └── agents/
│   │       ├── __init__.py
│   │       ├── base.py                  # BaseAgent protocol/abstract class
│   │       ├── triage.py                # Triage Agent (deterministic routing)
│   │       ├── concepts.py              # Concepts Agent
│   │       ├── code_review.py           # Code Review Agent
│   │       ├── debug.py                 # Debug Agent (progressive hints)
│   │       ├── exercise.py              # Exercise Agent (generate + grade)
│   │       └── progress.py              # Progress Agent (mastery calculation)
│   ├── repositories/
│   │   ├── agent_session_repository.py  # Agent session CRUD
│   │   ├── routing_repository.py        # Routing decision logging
│   │   ├── exercise_repository.py       # Exercise CRUD
│   │   └── mastery_repository.py        # Mastery record CRUD
│   ├── models/
│   │   ├── agent_session.py             # AgentSession, RoutingDecision, HintProgression
│   │   └── agent_exercise.py            # Exercise, ExerciseSubmission, MasteryRecord
│   ├── schemas/
│   │   └── agents.py                    # Pydantic schemas for agent requests/responses
│   └── llm/
│       └── prompts.py                   # Enhanced agent system prompts (existing, to be expanded)
├── alembic/
│   └── versions/
│       └── 20260403_xxxx_create_agent_tables.py  # Migration for new tables
└── tests/
    ├── unit/
    │   ├── test_triage_routing.py        # Deterministic routing tests
    │   ├── test_concepts_agent.py
    │   ├── test_code_review_agent.py
    │   ├── test_debug_agent.py
    │   ├── test_exercise_agent.py
    │   ├── test_progress_agent.py
    │   └── test_agent_schemas.py
    ├── integration/
    │   └── test_agent_routes.py          # FastAPI route integration tests
    └── contract/
        └── test_agent_api.py             # Contract tests against OpenAPI spec
```

**Structure Decision**: Single FastAPI service with agent services under `backend/src/services/agents/`. New models in separate files under `backend/src/models/` (agent_session.py, agent_exercise.py) to avoid bloating existing model files. Repositories follow existing pattern. Routes consolidated under a single `agents.py` v1 router with sub-paths per agent type.

## Complexity Tracking

> **No constitution violations identified.** The design uses existing patterns (Repository, LLM Provider Abstraction, Prompt Template Management) and stays within the single-service architecture mandated by AGENTS.md.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
