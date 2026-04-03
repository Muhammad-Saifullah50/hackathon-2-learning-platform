---
description: "Task list for Python Code Sandbox implementation"
---

# Tasks: Python Code Sandbox

**Input**: Design documents from `/specs/005-python-code-sandbox/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included as per feature specification requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `tests/` at repository root
- Paths adjusted based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create sandbox service directory structure in backend/src/services/sandbox/
- [X] T002 [P] Set up environment variables for sandbox configuration in .env.example
- [X] T003 [P] Install Docker Python client library (docker) as dependency

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement base sandbox interface protocol in backend/src/services/sandbox/base.py
- [X] T005 [P] Implement Docker-based sandbox implementation in backend/src/services/sandbox/docker_sandbox.py
- [X] T006 [P] Implement error parser for Python errors in backend/src/services/sandbox/error_parser.py
- [X] T007 Create Pydantic schemas for code execution in backend/src/schemas/code_execution.py
- [X] T008 Verify existing CodeSubmission model and repository from F02 are ready for use

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Execute Safe Python Code (Priority: P1) 🎯 MVP

**Goal**: Allow students to execute Python code in an isolated environment and return results

**Independent Test**: Can be fully tested by submitting valid Python code (e.g., `print("Hello World")`) and verifying that program output contains the expected text, execution completes within timeout, and no system resources are compromised.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Contract test for POST /api/v1/code-execution in tests/contract/test_code_execution_api.py
- [X] T010 [P] [US1] Integration test for successful code execution in tests/integration/test_code_execution_api.py

### Implementation for User Story 1

- [X] T011 [US1] Implement code execution service in backend/src/services/code_execution_service.py
- [X] T012 [US1] Create FastAPI endpoint for code execution in backend/src/api/v1/code_execution.py
- [X] T013 [US1] Add authentication dependency to code execution endpoint
- [X] T014 [US1] Connect endpoint to execution service and sandbox implementation

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Enforce Resource Limits (Priority: P1)

**Goal**: Enforce strict resource limits (5s timeout, 50MB memory) to prevent denial of service

**Independent Test**: Can be tested by submitting code with infinite loops or large memory allocations and verifying that execution terminates within 5 seconds and memory usage never exceeds 50MB.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [X] T015 [P] [US2] Integration test for timeout enforcement in tests/integration/test_resource_limits.py
- [X] T016 [P] [US2] Integration test for memory limit enforcement in tests/integration/test_resource_limits.py

### Implementation for User Story 2

- [X] T017 [US2] Configure Docker container resource limits in docker_sandbox.py
- [X] T018 [US2] Add timeout handling to code execution service
- [X] T019 [US2] Add memory usage tracking and reporting to execution results

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Restrict Dangerous Operations (Priority: P1)

**Goal**: Block dangerous operations (file system access, network calls, process spawning) and provide educational feedback

**Independent Test**: Can be tested by submitting code that imports blocked modules (e.g., system access modules) or attempts restricted operations, and verifying that execution fails with a clear explanation of what's not allowed and why.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [X] T020 [P] [US3] Unit test for import validation in tests/unit/test_sandbox_validation.py
- [X] T021 [P] [US3] Integration test for blocked import handling in tests/integration/test_security_restrictions.py

### Implementation for User Story 3

- [X] T022 [P] [US3] Implement AST-based import validation in backend/src/services/sandbox/import_validator.py
- [X] T023 [US3] Update Docker sandbox to enforce network restrictions
- [X] T024 [US3] Update error parser to provide educational feedback for blocked operations
- [X] T025 [US3] Update code execution service to validate imports before execution

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Store Successful Executions (Priority: P2)

**Goal**: Persist successful code executions to database for progress tracking and analytics

**Independent Test**: Can be tested by executing valid code, then verifying that the submission record exists with correct code, output, execution time, and timestamp.

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

- [X] T026 [P] [US4] Integration test for successful code submission persistence in tests/integration/test_code_submission_repository.py
- [X] T027 [P] [US4] Integration test for failed execution non-persistence in tests/integration/test_code_submission_repository.py

### Implementation for User Story 4

- [X] T028 [US4] Update code execution service to persist successful executions using CodeSubmissionRepository
- [X] T029 [US4] Add validation to only persist successful executions (status = "success")
- [X] T030 [US4] Update API response to include code_submission_id for successful executions

---

## Phase 7: User Story 5 - Parse and Simplify Error Messages (Priority: P2)

**Goal**: Convert Python tracebacks to student-friendly error messages with explanations

**Independent Test**: Can be tested by submitting code with common errors (SyntaxError, TypeError, NameError) and verifying that the returned error message is simplified, highlights the relevant line, and provides beginner-friendly context.

### Tests for User Story 5 (OPTIONAL - only if tests requested) ⚠️

- [X] T031 [P] [US5] Unit test for error parsing in tests/unit/test_error_parser.py
- [X] T032 [P] [US5] Integration test for error message simplification in tests/integration/test_error_handling.py

### Implementation for User Story 5

- [X] T033 [US5] Enhance error parser to handle multiple error types with student-friendly messages
- [X] T034 [US5] Update code execution service to use enhanced error parsing
- [X] T035 [US5] Update API endpoint to return improved error messages

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T036 [P] Add comprehensive logging to sandbox execution for monitoring
- [X] T037 [P] Add validation for code length limits (10,000 characters max)
- [X] T038 Add input/output sanitization to prevent XSS in error messages
- [X] T039 [P] Add monitoring metrics for execution times and success rates
- [X] T040 Add cleanup procedures for temporary files and containers
- [X] T041 Run quickstart.md validation to ensure all functionality works as expected

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 functionality
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US1 functionality
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US1 for execution functionality
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Depends on US1 for error handling

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for POST /api/v1/code-execution in tests/contract/test_code_execution_api.py"
Task: "Integration test for successful code execution in tests/integration/test_code_execution_api.py"

# Launch implementation tasks for User Story 1 together:
Task: "Implement code execution service in backend/src/services/code_execution_service.py"
Task: "Create FastAPI endpoint for code execution in backend/src/api/v1/code_execution.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
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
