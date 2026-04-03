# Feature Specification: LLM Provider Abstraction Layer

**Feature Branch**: `006-llm-provider`
**Created**: 2026-04-03
**Status**: Draft
**Input**: User description: "LLM Provider Abstraction Layer using LiteLLM with PostgreSQL caching and streaming responses. Initial model: Qwen 3.6 via OpenRouter. Models swappable via env vars. System prompts as Python constants. Kong handles rate limiting. Return error on failure, no auto-fallback."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Agent Sends a Prompt and Receives a Streaming Response (Priority: P1)

An AI agent (Concepts, Debug, Code Review, etc.) calls the LLM service with a system prompt and user message, and receives a token-by-token streaming response via FastAPI `StreamingResponse`. The model provider is configured entirely via environment variables.

**Why this priority**: This is the core functionality. Without it, no AI agent can communicate with any LLM. Every other feature depends on this working.

**Independent Test**: Can be fully tested by calling the `/api/llm/chat` endpoint with a test prompt and verifying streaming chunks are returned. Delivers the ability for any agent to get AI responses.

**Acceptance Scenarios**:

1. **Given** LiteLLM is configured with OpenRouter API key and `openrouter/qwen-3.6` model, **When** an agent sends a chat request with system prompt and user message, **Then** the response streams back token-by-token via SSE.
2. **Given** a valid request is made, **When** the response completes, **Then** the full response is cached in the PostgreSQL `llm_cache` table with a hash of the prompt.
3. **Given** the same prompt is sent twice, **When** the second request is made, **Then** the cached response is returned immediately without calling the LLM provider.

---

### User Story 2 - Swap LLM Model via Environment Variable (Priority: P2)

A developer changes the `LLM_MODEL` environment variable from `openrouter/qwen-3.6` to another model (e.g., `openai/gpt-4o-mini`) and the system uses the new model without any code changes.

**Why this priority**: The entire purpose of this feature is provider flexibility. If swapping models requires code changes, we've failed the abstraction goal.

**Independent Test**: Can be fully tested by changing the `LLM_MODEL` env var, restarting the service, and verifying the new model responds to requests.

**Acceptance Scenarios**:

1. **Given** the system is running with `openrouter/qwen-3.6`, **When** a developer changes `LLM_MODEL` to `openai/gpt-4o-mini` and restarts, **Then** all subsequent requests use the new model without code changes.
2. **Given** `LLM_API_KEY` and `LLM_BASE_URL` are set correctly for the chosen provider, **When** a request is made, **Then** LiteLLM routes to the correct provider automatically.

---

### User Story 3 - LLM Request Fails Gracefully with Error (Priority: P3)

When the LLM provider is unreachable, returns an error, or times out, the system returns a clear error response to the calling agent without crashing or hanging.

**Why this priority**: Failures will happen (rate limits, outages, bad keys). The system must fail gracefully so agents can handle errors appropriately.

**Independent Test**: Can be fully tested by providing an invalid API key or simulating a timeout, and verifying a structured error response is returned.

**Acceptance Scenarios**:

1. **Given** an invalid API key is configured, **When** a request is made, **Then** a 502 error with a clear message is returned (not a raw stack trace).
2. **Given** the LLM provider times out (>30s), **When** a request is made, **Then** a 504 timeout error is returned.
3. **Given** the LLM provider returns an error response, **When** a request is made, **Then** the error is logged (without sensitive data) and a structured error is returned to the caller.

---

### Edge Cases

- What happens when the prompt exceeds the model's context window? → System MUST reject with a clear error before sending to the provider.
- How does the system handle concurrent requests hitting the cache simultaneously? → Use database-level upsert (`ON CONFLICT`) to avoid duplicate cache writes.
- What happens when the PostgreSQL cache is unavailable? → The request MUST still go through to the LLM provider (cache is optional, not a hard dependency).
- How are streaming errors handled mid-response? → If streaming fails partway through, the connection MUST close cleanly and the partial response MUST NOT be cached.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use LiteLLM as the unified LLM client, configured via environment variables (`LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL`)
- **FR-002**: System MUST support response streaming via FastAPI `StreamingResponse` with SSE format
- **FR-003**: System MUST cache complete LLM responses in the PostgreSQL `llm_cache` table using a SHA-256 hash of the full prompt as the key
- **FR-004**: System MUST check the cache before calling the LLM provider and return cached responses when available
- **FR-005**: System MUST return a structured error response (not raw stack traces) when the LLM provider fails, times out, or returns an error
- **FR-006**: System MUST enforce a 30-second timeout on all LLM requests
- **FR-007**: System MUST track token usage (input tokens, output tokens, total tokens) per request
- **FR-008**: System MUST support system prompts defined as Python constants/functions (no YAML/JSON prompt files)
- **FR-009**: System MUST NOT implement rate limiting at the FastAPI layer (Kong handles this at the gateway)
- **FR-010**: System MUST NOT implement auto-fallback to alternative models on failure
- **FR-011**: System MUST log all LLM requests and responses at DEBUG level (with sensitive data redacted)
- **FR-012**: System MUST reject prompts that exceed the configured maximum input token limit (1,200 tokens)

### Key Entities

- **LLM Request**: Contains system prompt, user message(s), model config, and optional parameters (max_tokens, temperature). Generates a SHA-256 hash for cache lookup.
- **LLM Response**: Contains the generated text, token usage (input/output/total), model used, and timestamp. Stored in cache on completion.
- **LLM Cache Entry** (existing `llm_cache` table from F02): `prompt_hash` (PK, SHA-256), `response` (text), `model` (string), `token_count` (int), `created_at` (timestamp).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A streaming LLM response completes within 30 seconds end-to-end (P95) under normal provider conditions
- **SC-002**: Cached responses return within 50ms (P95), demonstrating cache effectiveness over live LLM calls
- **SC-003**: Swapping the LLM model requires zero code changes — only environment variable updates
- **SC-004**: All LLM provider failures return structured error responses within 2 seconds (no hanging requests)
- **SC-005**: Token usage is accurately tracked and logged for every request (verified by comparing LiteLLM token counts against logged values)
