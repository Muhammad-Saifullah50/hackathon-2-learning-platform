# Quickstart: LLM Provider Abstraction Layer

**Feature**: 006-llm-provider
**Date**: 2026-04-03

## Prerequisites

- Python 3.13+ with `.venv/` activated
- Neon PostgreSQL database (already configured in `.env`)
- OpenRouter API key (get one from https://openrouter.ai/keys)

## Setup

### 1. Install LiteLLM dependency

```bash
cd backend
pip install litellm
# Or add to requirements.txt and run:
pip install -r requirements.txt
```

### 2. Configure environment variables

Add to `backend/.env`:

```env
# LLM Provider Configuration
LLM_MODEL=openrouter/qwen-3.6
LLM_API_KEY=sk-or-v1-your-openrouter-api-key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MAX_INPUT_TOKENS=1200
LLM_MAX_OUTPUT_TOKENS=600
LLM_TIMEOUT_SECONDS=30
LLM_TEMPERATURE=0.7
LLM_CACHE_TTL_DAYS=30
```

### 3. Update config.py

Add LLM settings to the `Settings` class in `backend/src/config.py` (see plan.md for details).

### 4. Run the server

```bash
cd backend
uvicorn src.main:app --reload
```

## Testing the Feature

### Test 1: Streaming chat endpoint

```bash
curl -X POST http://localhost:8000/api/v1/llm/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt>" \
  -d '{
    "system_prompt": "You are a helpful Python tutor.",
    "messages": [{"role": "user", "content": "What is a variable?"}]
  }' \
  -N
```

Expected: SSE stream of tokens, ending with a `done: true` event containing token usage.

### Test 2: Cache lookup endpoint

```bash
curl -X POST http://localhost:8000/api/v1/llm/cache/lookup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt>" \
  -d '{
    "system_prompt": "You are a helpful Python tutor.",
    "messages": [{"role": "user", "content": "What is a variable?"}]
  }'
```

Expected (first call): `404 Not Found` (not yet cached)
Expected (second call after chat): `200 OK` with cached response

### Test 3: Verify cache in database

```python
# Run in Python shell or test
from src.repositories.cache_repository import CacheRepository
from src.database import get_async_session

async def check_cache():
    async with get_async_session() as session:
        repo = CacheRepository(session)
        result = await repo.get_cached_response("<hash-from-lookup>")
        print(result)
```

### Test 4: Swap model via env var

1. Change `LLM_MODEL` in `.env` to a different model
2. Restart the server
3. Make a new request — it should use the new model

### Test 5: Error handling (invalid API key)

1. Set `LLM_API_KEY=invalid-key` in `.env`
2. Restart the server
3. Make a request — should return `502` with structured error (not stack trace)

## Validation Checklist

- [ ] Streaming endpoint returns SSE events with individual tokens
- [ ] Final SSE event includes `done: true` and token usage
- [ ] Cache lookup returns 404 for uncached prompts
- [ ] Cache lookup returns 200 for previously completed requests
- [ ] Cached responses return in < 50ms
- [ ] Invalid API key returns structured 502 error
- [ ] Timeout (> 30s) returns structured 504 error
- [ ] Model swap via env var works without code changes
- [ ] Token usage is logged at DEBUG level
- [ ] API key is never logged (even at DEBUG level)
