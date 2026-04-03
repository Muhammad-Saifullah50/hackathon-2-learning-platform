# Implementation Plan: LLM Provider Abstraction Layer

**Branch**: `006-llm-provider` | **Date**: 2026-04-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-llm-provider/spec.md`

## Summary

Build an LLM provider abstraction layer using LiteLLM as the unified client, enabling any AI agent to send prompts and receive streaming responses. The system uses the existing `llm_cache` table (model, schema, repository, and migration already implemented) for response caching via SHA-256 prompt hashing. Model selection is entirely environment-driven — swapping models requires zero code changes. Initial model: `openrouter/qwen-3.6` via OpenRouter.

## Technical Context

**Language/Version**: Python 3.13 (active `.venv/`)
**Primary Dependencies**: LiteLLM (new), FastAPI 0.109.0, Pydantic 2.5.3, SQLAlchemy 2.0.25
**Storage**: Neon PostgreSQL (existing `llm_cache` table — no new migration needed)
**Testing**: pytest + pytest-asyncio + httpx async client
**Target Platform**: Linux server (Kubernetes deployment)
**Project Type**: Web application (backend FastAPI service)
**Performance Goals**: Streaming first token < 1.2s, full response < 30s, cached response < 50ms (P95)
**Constraints**: 1,200 input token limit, 600 output token limit, 30s timeout, no auto-fallback, Kong handles rate limiting
**Scale/Scope**: Single FastAPI service, 6 AI agents will consume this layer

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| Repository Pattern | ✅ PASS | Uses existing `CacheRepository` — no new repo needed |
| LLM Provider Abstraction | ✅ PASS | LiteLLM provides unified client; factory via env var |
| Prompt Template Management | ✅ PASS | System prompts as Python constants/functions per spec |
| No business logic in routes | ✅ PASS | Service layer handles all LLM logic |
| Streaming (not sync) | ✅ PASS | FastAPI `StreamingResponse` with SSE (streaming-only, no blocking endpoint) |
| Auth by default | ✅ PASS | Both endpoints require JWT via `get_current_user` dependency |
| No hardcoded provider | ✅ PASS | All config via `LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL` env vars |
| Security (no secrets logged) | ✅ PASS | DEBUG logging with API key redaction |
| Formatting (black + isort) | ✅ PASS | Already configured in pyproject.toml |
| Google-style docstrings | ✅ PASS | All business logic functions will have them |
| FastAPI route summary/description | ✅ PASS | All routes will include metadata |

## Project Structure

### Documentation (this feature)

```text
specs/006-llm-provider/
├── spec.md              # Feature specification (exists)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (confirms existing llm_cache model)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI contract for LLM endpoints)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config.py                          # ADD: LLM settings (LLM_MODEL, LLM_API_KEY, etc.)
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py                      # LiteLLM client wrapper with streaming + timeout
│   │   ├── service.py                     # LlmService (orchestrates cache check → LLM call → cache write)
│   │   ├── prompts.py                     # System prompts as Python constants
│   │   └── schemas.py                     # Request/response Pydantic schemas for LLM endpoints
│   ├── api/
│   │   └── v1/
│   │       └── llm.py                     # POST /api/v1/llm/chat (streaming), POST /api/v1/llm/cache/lookup
│   ├── repositories/
│   │   └── cache_repository.py            # EXISTS — no changes needed
│   ├── models/
│   │   └── cache.py                       # EXISTS — no changes needed
│   ├── schemas/
│   │   └── cache.py                       # EXISTS — no changes needed
│   ├── dependencies.py                    # ADD: get_llm_service dependency
│   └── main.py                            # ADD: LLM router registration
├── tests/
│   ├── unit/
│   │   ├── test_llm_client.py             # LiteLLM client wrapper tests
│   │   ├── test_llm_prompts.py            # Prompt constant tests
│   │   └── test_llm_service.py            # Service layer tests (mocked LiteLLM)
│   ├── integration/
│   │   └── test_llm_routes.py             # Route tests (mocked LiteLLM + test DB)
│   └── contract/
│       └── test_llm_api.py                # API contract validation tests
└── requirements.txt                       # ADD: litellm
```

**Structure Decision**: Backend-only feature (no frontend work). Follows existing architecture: routes → service → client → repository. The `llm_cache` table, model, schema, and repository already exist from F02 and require no changes.

## Phase 0: Research Summary

### LiteLLM Selection Rationale
- **Unified interface**: Single `litellm.acompletion()` call works with 100+ providers
- **Streaming support**: Native async streaming via `litellm.acompletion(stream=True)`
- **Token tracking**: Returns usage metadata (input/output/total tokens) automatically
- **Model swapping**: Change model via string parameter — no code changes needed
- **OpenRouter support**: `openrouter/qwen-3.6` works out of the box with `OPENAI_API_KEY` set to OpenRouter key

### Alternatives Considered
| Option | Rejected Because |
|--------|-----------------|
| Direct OpenAI SDK | Locks us to OpenAI-compatible providers only |
| LangChain | Overkill — we only need completion + streaming, not chains/agents |
| Custom provider interface | Reinventing LiteLLM — more maintenance, less provider coverage |

### Existing Infrastructure to Reuse
- `LLMCache` model (`src/models/cache.py`) — fully implemented
- `CacheRepository` (`src/repositories/cache_repository.py`) — get/set/purge operations ready
- `LLMCacheCreate`, `LLMCacheResponse`, `CacheLookupRequest` schemas — ready
- `get_cache_repository()` dependency — ready
- Alembic migration for `llm_cache` table — already applied

### New Dependencies
| Package | Purpose |
|---------|---------|
| `litellm` | Unified LLM client with streaming + token tracking |

### Environment Variables (New)
| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | `openrouter/qwen-3.6` | LiteLLM model identifier |
| `LLM_API_KEY` | *(required)* | API key for the configured provider |
| `LLM_BASE_URL` | `https://openrouter.ai/api/v1` | Base URL for the provider (OpenRouter default) |
| `LLM_MAX_INPUT_TOKENS` | `1200` | Maximum input tokens before rejection |
| `LLM_MAX_OUTPUT_TOKENS` | `600` | Maximum output tokens per response |
| `LLM_TIMEOUT_SECONDS` | `30` | Timeout for LLM requests |
| `LLM_TEMPERATURE` | `0.7` | Default temperature for completions |
| `LLM_CACHE_TTL_DAYS` | `30` | Cache entry TTL in days |

## Data Model

**No new database tables or migrations needed.** The `llm_cache` table from F02 covers all caching requirements:

| Column | Type | Notes |
|--------|------|-------|
| `cache_key_hash` | VARCHAR(64) PK | SHA-256 of normalized prompt + model + params |
| `prompt_text` | TEXT | Full prompt text (system + user messages) |
| `response_text` | TEXT | Complete LLM response |
| `model` | VARCHAR(100) | Model identifier used (e.g., `openrouter/qwen-3.6`) |
| `token_count` | INTEGER | Total tokens used |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `last_accessed_at` | TIMESTAMPTZ | Last cache hit timestamp |
| `expires_at` | TIMESTAMPTZ | Optional expiration |

## API Contracts

### POST `/api/v1/llm/chat`
Streaming endpoint for AI agents to send prompts and receive token-by-token responses.

**Request Body**:
```json
{
  "system_prompt": "You are a Python tutor...",
  "messages": [{"role": "user", "content": "What is a list comprehension?"}],
  "temperature": 0.7,
  "max_tokens": 600
}
```

**Response**: `text/event-stream` (SSE format)
```
data: {"token": "A", "index": 0}
data: {"token": " list", "index": 1}
...
data: {"done": true, "model": "openrouter/qwen-3.6", "tokens": {"input": 45, "output": 120, "total": 165}}
```

### POST `/api/v1/llm/cache/lookup`
Check if a prompt is cached before calling the LLM.

**Request Body**:
```json
{
  "system_prompt": "You are a Python tutor...",
  "messages": [{"role": "user", "content": "What is a list comprehension?"}],
  "temperature": 0.7,
  "max_tokens": 600
}
```

**Response** (200 if cached, 404 if not):
```json
{
  "cached": true,
  "response": "A list comprehension is...",
  "model": "openrouter/qwen-3.6",
  "token_count": 165
}
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| LiteLLM dependency | Need multi-provider support with single interface | Direct OpenAI SDK would lock us to one provider; custom abstraction duplicates LiteLLM |
| Separate LLM service layer | Cache check → LLM call → cache write is multi-step orchestration | Putting logic in routes violates constitution (no business logic in routes) |
