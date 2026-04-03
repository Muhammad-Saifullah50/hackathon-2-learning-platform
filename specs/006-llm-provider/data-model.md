# Data Model: LLM Provider Abstraction Layer

**Feature**: 006-llm-provider
**Date**: 2026-04-03

## Summary

**No new database tables or migrations are required.** The `llm_cache` table was created in feature 002 (database-schema) and is fully ready for use. This feature only adds application-layer code that consumes the existing cache infrastructure.

## Existing Model: LLMCache

**File**: `backend/src/models/cache.py`
**Table**: `llm_cache`
**Migration**: `20260315_0655_002f_llm_cache.py`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `cache_key_hash` | VARCHAR(64) | PK, NOT NULL | SHA-256 hash of normalized prompt + model + params |
| `prompt_text` | TEXT | NOT NULL | Full prompt text (system prompt + user messages) |
| `response_text` | TEXT | NOT NULL | Complete LLM response text |
| `model` | VARCHAR(100) | NOT NULL | Model identifier (e.g., `openrouter/qwen-3.6`) |
| `token_count` | INTEGER | NOT NULL, CHECK > 0 | Total tokens used (input + output) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | When the cache entry was created |
| `last_accessed_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW(), INDEXED | Last time this entry was used as a cache hit |
| `expires_at` | TIMESTAMPTZ | NULLABLE, INDEXED | Optional expiration timestamp |

### Indexes
- `idx_llm_cache_last_accessed` on `last_accessed_at` — for cleanup queries
- `idx_llm_cache_expires_at` on `expires_at` — for expiration queries

### Existing Pydantic Schemas

**File**: `backend/src/schemas/cache.py`

| Schema | Purpose | Fields |
|--------|---------|--------|
| `LLMCacheCreate` | Create a new cache entry | `prompt`, `response`, `model`, `token_count`, `temperature`, `max_tokens`, `ttl_days` |
| `LLMCacheResponse` | Return a cached response | All model fields + timestamps |
| `CacheLookupRequest` | Request cache lookup | `prompt`, `model`, `temperature`, `max_tokens` |

### Existing Repository

**File**: `backend/src/repositories/cache_repository.py`

| Method | Purpose |
|--------|---------|
| `generate_cache_key(prompt, model, temperature, max_tokens)` | Generate SHA-256 hash from request parameters |
| `get_cached_response(cache_key_hash)` | Look up cached response by hash, check expiration, update `last_accessed_at` |
| `set_cached_response(cache_data)` | Create new cache entry with optional TTL |
| `purge_expired_cache(days_since_access)` | Delete entries not accessed in N days |

## New Application-Layer Schemas (Not Database Models)

These are Pydantic schemas for API request/response — they do NOT map to database tables.

### LlmChatRequest

**File**: `backend/src/llm/schemas.py` (new)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `system_prompt` | str | Yes | System prompt defining agent behavior |
| `messages` | list[ChatMessage] | Yes | Conversation messages |
| `temperature` | float | No (default: 0.7) | Sampling temperature (0.0–2.0) |
| `max_tokens` | int | No (default: 600) | Maximum output tokens |

### ChatMessage

**File**: `backend/src/llm/schemas.py` (new)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | str | Yes | Message role: `system`, `user`, `assistant` |
| `content` | str | Yes | Message content |

### LlmStreamResponse (SSE event)

**File**: `backend/src/llm/schemas.py` (new)

| Field | Type | Description |
|-------|------|-------------|
| `token` | str | Single token chunk (streaming events) |
| `index` | int | Token index in response |
| `done` | bool | Whether streaming is complete (final event only) |
| `model` | str | Model used (final event only) |
| `tokens` | TokenUsage | Token usage breakdown (final event only) |

### TokenUsage

**File**: `backend/src/llm/schemas.py` (new)

| Field | Type | Description |
|-------|------|-------------|
| `input` | int | Input/prompt tokens |
| `output` | int | Output/completion tokens |
| `total` | int | Total tokens used |

### LlmErrorResponse

**File**: `backend/src/llm/schemas.py` (new)

| Field | Type | Description |
|-------|------|-------------|
| `error` | str | Error type (e.g., `provider_error`, `timeout`, `invalid_request`) |
| `message` | str | Human-readable error message |
| `detail` | str | Additional context (no sensitive data) |

## Relationships

```
┌─────────────────────────────────────────────────┐
│                  LLM Service                     │
│                                                  │
│  1. Check CacheRepository.get_cached_response()  │
│     ↓ (miss)                                     │
│  2. Call LiteLLM client (streaming)             │
│     ↓                                            │
│  3. Collect full response                        │
│     ↓                                            │
│  4. CacheRepository.set_cached_response()        │
│     ↓                                            │
│  5. Stream response to client via SSE            │
└─────────────────────────────────────────────────┘
         │
         ├── depends on → CacheRepository (existing)
         ├── depends on → LLMCache model (existing)
         ├── depends on → LiteLLM client (new)
         └── consumed by → AI Agents (future features)
```

## Migration Plan

**No database migration required.** The `llm_cache` table already exists and is fully configured.
