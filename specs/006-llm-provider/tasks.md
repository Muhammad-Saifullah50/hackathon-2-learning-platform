---

description: "Task list for LLM Provider Abstraction Layer implementation"
---

# Tasks: LLM Provider Abstraction Layer

**Input**: Design documents from `/specs/006-llm-provider/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, contracts/llm-api.yaml, quickstart.md

**Tests**: Included — TDD approach requested per constitution for core infrastructure.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`

---

## Phase 1: Setup

**Purpose**: Project initialization and LiteLLM dependency

- [x] T001 Add `litellm` to `backend/requirements.txt`
- [x] T002 [P] Add LLM environment variables to `backend/src/config.py` (LLM_MODEL, LLM_API_KEY, LLM_BASE_URL, LLM_MAX_INPUT_TOKENS, LLM_MAX_OUTPUT_TOKENS, LLM_TIMEOUT_SECONDS, LLM_TEMPERATURE, LLM_CACHE_TTL_DAYS)
- [x] T003 [P] Create `backend/src/llm/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create Pydantic request/response schemas in `backend/src/llm/schemas.py` (ChatMessage, LlmChatRequest, TokenUsage, LlmStreamResponse, LlmErrorResponse)
- [x] T005 [P] Create system prompt constants in `backend/src/llm/prompts.py` (Python constants/functions for agent-specific system prompts)
- [x] T006 Implement LiteLLM client wrapper in `backend/src/llm/client.py` (async streaming + timeout + error handling + token tracking)
- [x] T007 Implement LlmService in `backend/src/llm/service.py` (orchestrates cache check → LLM call → cache write → streaming)
- [x] T008 Add `get_llm_service` dependency in `backend/src/dependencies.py`
- [x] T009 Register LLM router in `backend/src/main.py` (include `/api/v1/llm` prefix)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - AI Agent Sends a Prompt and Receives a Streaming Response (Priority: P1) 🎯 MVP

**Goal**: AI agents can call the LLM service with system prompt and user message, receiving token-by-token streaming response via FastAPI StreamingResponse with SSE format. Includes cache check before LLM call.

**Independent Test**: Call `/api/v1/llm/chat` endpoint with a test prompt and verify streaming chunks are returned via SSE. Delivers the ability for any agent to get AI responses.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Unit test for LiteLLM client wrapper streaming in `backend/tests/unit/test_llm_client.py`
- [x] T011 [P] [US1] Unit test for LlmService cache-hit flow in `backend/tests/unit/test_llm_service.py`
- [x] T012 [P] [US1] Unit test for LlmService cache-miss + streaming flow in `backend/tests/unit/test_llm_service.py`
- [x] T013 [US1] Integration test for streaming chat endpoint in `backend/tests/integration/test_llm_routes.py`
- [x] T014 [US1] Contract test for POST `/api/v1/llm/chat` in `backend/tests/contract/test_llm_api.py`

### Implementation for User Story 1

- [x] T015 [US1] Implement streaming chat logic in LlmService (cache check → LLM call → cache write → stream tokens) in `backend/src/llm/service.py`
- [x] T016 [US1] Implement POST `/api/v1/llm/chat` route with SSE StreamingResponse in `backend/src/api/v1/llm.py`
- [x] T017 [US1] Add input token validation (reject prompts > 1,200 tokens) in `backend/src/llm/service.py`
- [x] T018 [US1] Add JWT auth requirement via `get_current_user` dependency to LLM routes in `backend/src/api/v1/llm.py`
- [x] T019 [US1] Add DEBUG logging for LLM requests/responses (with API key redaction) in `backend/src/llm/service.py`
- [x] T020 [US1] Add Google-style docstrings to all LLM service functions in `backend/src/llm/service.py`
- [x] T021 [US1] Add FastAPI route `summary=` and `description=` metadata in `backend/src/api/v1/llm.py`

**Checkpoint**: At this point, User Story 1 should be fully functional — agents can send prompts and receive streaming responses with caching

---

## Phase 4: User Story 2 - Swap LLM Model via Environment Variable (Priority: P2)

**Goal**: Developer can change `LLM_MODEL` environment variable and system uses new model without any code changes. LiteLLM handles provider routing automatically.

**Independent Test**: Change `LLM_MODEL` env var, restart service, verify new model responds to requests.

### Tests for User Story 2 ⚠️

- [x] T022 [P] [US2] Unit test for config loading with different model values in `backend/tests/unit/test_llm_service.py`
- [x] T023 [US2] Integration test verifying model swap via env var in `backend/tests/integration/test_llm_routes.py`
- [x] T024 [US2] Verify LiteLLM client reads model from config (no hardcoded model) in `backend/src/llm/client.py`
- [x] T025 [US2] Verify LlmService passes model from config to client in `backend/src/llm/service.py`
- [x] T026 [US2] Add model identifier to SSE final event (`done` event includes `model` field) in `backend/src/api/v1/llm.py`
- [x] T027 [US2] Add model to cache entry when writing response in `backend/src/llm/service.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently — streaming responses work AND model swapping requires only env var changes

---

## Phase 5: User Story 3 - LLM Request Fails Gracefully with Error (Priority: P3)

**Goal**: When LLM provider is unreachable, returns error, or times out, system returns structured error response to calling agent without crashing or hanging.

**Independent Test**: Provide invalid API key or simulate timeout, verify structured error response is returned (not raw stack trace).

### Tests for User Story 3 ⚠️

- [x] T028 [P] [US3] Unit test for invalid API key error handling in `backend/tests/unit/test_llm_client.py`
- [x] T029 [P] [US3] Unit test for timeout error handling in `backend/src/llm/client.py`
- [x] T030 [US3] Integration test for error responses in `backend/tests/integration/test_llm_routes.py`
- [x] T031 [US3] Contract test for error response schema in `backend/tests/contract/test_llm_api.py`
- [x] T032 [US3] Implement LiteLLM error handling (AuthenticationError → 502, Timeout → 504, general → 502) in `backend/src/llm/client.py`
- [x] T033 [US3] Implement streaming error handling (mid-stream failure → close cleanly, do NOT cache partial response) in `backend/src/llm/service.py`
- [x] T034 [US3] Implement structured error responses (LlmErrorResponse schema) in route handlers in `backend/src/api/v1/llm.py`
- [x] T035 [US3] Ensure no sensitive data (API keys) in error responses or logs in `backend/src/llm/service.py`
- [x] T036 [US3] Implement cache-unavailable fallback (request proceeds to LLM even if cache is down) in `backend/src/llm/service.py`

**Checkpoint**: All user stories should now be independently functional — streaming, model swapping, and graceful error handling all work

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T037 [P] Add unit tests for prompt constants in `backend/tests/unit/test_llm_prompts.py`
- [x] T038 [P] Run `black . && isort .` on all new Python files
- [x] T039 Verify all FastAPI routes have `summary=` and `description=` metadata
- [x] T040 Verify all business logic functions have Google-style docstrings
- [x] T041 Run full test suite and fix any failures
- [x] T042 Validate quickstart.md test scenarios from `specs/006-llm-provider/quickstart.md`
- [x] T043 Update API documentation with new LLM endpoints

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 streaming infrastructure
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 client + service error handling points

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Schemas before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational tasks marked [P] can run in parallel (T004, T005)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for LiteLLM client wrapper streaming in backend/tests/unit/test_llm_client.py"
Task: "Unit test for LlmService cache-hit flow in backend/tests/unit/test_llm_service.py"
Task: "Unit test for LlmService cache-miss + streaming flow in backend/tests/unit/test_llm_service.py"

# Launch all schemas and prompts together (Foundational):
Task: "Create Pydantic request/response schemas in backend/src/llm/schemas.py"
Task: "Create system prompt constants in backend/src/llm/prompts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test streaming endpoint with curl per quickstart.md
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (streaming + caching)
   - Developer B: User Story 2 (model swapping)
   - Developer C: User Story 3 (error handling)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- No database migration needed — `llm_cache` table already exists
- Rate limiting handled by Kong at gateway level — do NOT implement in FastAPI
- No auto-fallback to alternative models — return error on failure per spec
