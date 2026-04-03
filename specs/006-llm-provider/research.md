# Research: LLM Provider Abstraction Layer

**Feature**: 006-llm-provider
**Date**: 2026-04-03

## LiteLLM Evaluation

### Why LiteLLM
- Single `litellm.acompletion()` call works across 100+ providers (OpenAI, Anthropic, OpenRouter, Azure, etc.)
- Native async streaming via `litellm.acompletion(stream=True, acompletion=True)`
- Automatic token usage tracking in response metadata (`response.usage`)
- Model swapping is a string change — no code modifications needed
- Already handles provider-specific quirks (URL paths, auth headers, response formats)

### Key API Usage
```python
import litellm

# Non-streaming
response = await litellm.acompletion(
    model="openrouter/qwen-3.6",
    messages=[{"role": "user", "content": "Hello"}],
    api_key="sk-...",
    api_base="https://openrouter.ai/api/v1",
    max_tokens=600,
    temperature=0.7,
)
print(response.choices[0].message.content)
print(response.usage)  # ModelUsage(prompt_tokens=..., completion_tokens=..., total_tokens=...)

# Streaming
stream = await litellm.acompletion(
    model="openrouter/qwen-3.6",
    messages=[{"role": "user", "content": "Hello"}],
    api_key="sk-...",
    api_base="https://openrouter.ai/api/v1",
    stream=True,
)
async for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="")
```

### OpenRouter Integration
- OpenRouter exposes an OpenAI-compatible API at `https://openrouter.ai/api/v1`
- Model identifier: `openrouter/qwen-3.6` (LiteLLM prefix convention)
- Authentication: Bearer token via `api_key` parameter
- Supports streaming, token limits, temperature — all standard OpenAI parameters

### Error Handling
- LiteLLM raises `litellm.AuthenticationError` for invalid API keys
- Raises `litellm.Timeout` for request timeouts
- Raises `litellm.RateLimitError` for rate limit exceeded
- Raises `litellm.APIError` for provider-side errors
- All exceptions inherit from `litellm.LitellmException` — can catch base class for generic handling

## FastAPI Streaming with SSE

### Approach
Use `StreamingResponse` with `media_type="text/event-stream"` to deliver token-by-token chunks:

```python
from fastapi.responses import StreamingResponse

async def event_generator():
    async for token in llm_client.stream_completion(...):
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield f"data: {json.dumps({'done': True, 'tokens': usage})}\n\n"

return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### Why SSE over raw streaming
- Standard format, easy for clients to parse
- Built-in reconnection support
- Each chunk is a complete JSON object
- Works with Next.js `EventSource` and `fetch` with `ReadableStream`

## Token Counting Strategy

### Input Token Estimation
- LiteLLM returns `prompt_tokens` and `completion_tokens` in streaming response's final chunk
- For pre-flight validation (reject prompts > 1,200 tokens), use a lightweight estimator:
  - Simple heuristic: ~4 characters per token for English text
  - Or add `tiktoken` for precise counting (adds ~100ms overhead)
- **Decision**: Use LiteLLM's returned token counts for caching/validation. For pre-flight rejection, use character-based heuristic (~4 chars/token) as a fast approximation. If close to limit, let the provider reject it — better than adding tiktoken dependency.

## Caching Strategy

### Cache Key Generation
Existing `CacheRepository.generate_cache_key()` already handles this:
- Normalizes prompt text (strip whitespace, lowercase)
- Includes model, temperature, max_tokens in hash input
- Produces SHA-256 hash (64 char string)

### Cache Flow
1. Generate hash from request parameters
2. Check `llm_cache` table for existing entry
3. If hit: return cached response immediately (no LLM call)
4. If miss: call LLM, stream response, collect full text, write to cache
5. Streaming errors: do NOT cache partial responses

### Concurrent Request Handling
- Database-level `ON CONFLICT` upsert prevents duplicate cache writes
- Existing `CacheRepository.set_cached_response()` uses SQLAlchemy — need to add `ON CONFLICT` via `insert().on_conflict_do_nothing()` or try/except on IntegrityError

## Existing Infrastructure Audit

### What Already Exists (No Changes Needed)
- `LLMCache` model (`src/models/cache.py`) — complete with all columns and constraints
- `CacheRepository` (`src/repositories/cache_repository.py`) — get, set, purge operations
- `LLMCacheCreate`, `LLMCacheResponse`, `CacheLookupRequest` schemas (`src/schemas/cache.py`)
- `get_cache_repository()` dependency (`src/dependencies.py`)
- Alembic migration `20260315_0655_002f_llm_cache.py` — table created with indexes

### What Needs to Be Built
- LiteLLM client wrapper with streaming + timeout + error handling
- LLM service layer (orchestrates cache check → LLM call → cache write)
- System prompts as Python constants
- Request/response Pydantic schemas for LLM endpoints
- FastAPI route for streaming chat
- FastAPI route for cache lookup
- Environment configuration for LLM settings
- Dependency injection for LLM service
- Router registration in main.py

## Security Considerations

- API key stored in env var, never logged or returned in responses
- DEBUG logging redacts API key (show only first/last 4 chars)
- User prompts are stored in cache — ensure no PII is included in system prompts
- No `exec()` or `eval()` — LiteLLM is a pure HTTP client
- Rate limiting handled by Kong at gateway level (per constitution)

## Performance Considerations

- Streaming first token should arrive within 1.2s (depends on provider latency)
- Full response timeout: 30s (hard limit per constitution)
- Cached responses: PostgreSQL query < 40ms, total < 50ms
- Input token limit: 1,200 tokens (reject before calling provider)
- Output token limit: 600 tokens (pass as `max_tokens` to provider)
