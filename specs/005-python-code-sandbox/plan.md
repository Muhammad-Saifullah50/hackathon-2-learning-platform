# Implementation Plan: Python Code Sandbox

**Branch**: `005-python-code-sandbox` | **Date**: 2026-03-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-python-code-sandbox/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a secure Python code execution sandbox that allows students to run Python code in an isolated environment with strict resource limits (5s timeout, 50MB memory), import restrictions (standard library whitelist only), and no network/filesystem access. The sandbox must capture program output and errors, parse error messages into student-friendly format, and persist successful executions to the database for progress tracking.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0+, Pydantic 2.0+, NEEDS CLARIFICATION (sandbox execution engine)
**Storage**: Neon PostgreSQL (code_submissions table from F02)
**Testing**: pytest (unit + integration), httpx async client
**Target Platform**: Linux server (Kubernetes deployment)
**Project Type**: Web (backend microservice)
**Performance Goals**: <6s total response time (5s execution + 1s overhead), 50 concurrent executions
**Constraints**: 5s execution timeout, 50MB memory per execution, no network access, no filesystem access (except temp), standard library imports only
**Scale/Scope**: 10k+ students, ~100 code executions per student per day

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality Standards
- ✅ Python formatting: black + isort (auto-format on save + pre-commit)
- ✅ Naming: snake_case functions/variables, PascalCase classes
- ✅ Documentation: Google-style docstrings for business logic functions
- ✅ FastAPI routes: summary= and description= fields required

### Testing Principles
- ✅ FastAPI routes: 80% coverage target (execution endpoint is critical)
- ✅ Database repositories: 85% coverage (code_submissions persistence)
- ✅ TDD approach: Strict TDD for sandbox execution logic (security-sensitive)
- ✅ Integration tests: FastAPI routes against real test DB

### Performance Standards
- ✅ FastAPI response (non-AI): <150ms overhead (5s execution + <1s processing = <6s total)
- ✅ PostgreSQL query: <40ms (simple INSERT for code_submissions)
- ✅ Resource limits: 50MB RAM, 5s CPU per execution (matches constitution sandbox constraints)

### Security Constraints
- ✅ NEVER use exec() or eval() on server (constitution mandate)
- ✅ User code runs in fully isolated sandbox (Docker container or equivalent)
- ✅ All FastAPI routes require auth via get_current_user dependency
- ✅ Never log user code in raw production logs

### Architecture Patterns
- ✅ Repository Pattern: DB access only through repos (code_submissions_repository)
- ✅ Sandbox execution abstraction: Protocol-based interface for swapping implementations (Docker, Piston API, custom) following same pattern as LLM Provider Abstraction
  - Rationale: Enable swapping sandbox implementations (Docker, Piston API, custom) without changing business logic
  - Simpler alternative rejected: Direct Docker calls would lock us into one implementation and make testing harder

### Business Logic Integrity
- ✅ Code execution sandbox constraints match constitution:
  - Timeout: 5 seconds ✓
  - Memory limit: 50MB ✓
  - No file system access (except temp) ✓
  - No network access ✓
  - Standard library only ✓

### Violations Requiring Justification
None - all constitution requirements are satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/005-python-code-sandbox/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── code_submission.py          # SQLAlchemy model (exists from F02)
│   ├── repositories/
│   │   └── code_submission_repository.py  # DB access layer (exists from F02)
│   ├── services/
│   │   ├── sandbox/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Abstract sandbox interface
│   │   │   ├── docker_sandbox.py       # Docker-based implementation
│   │   │   └── error_parser.py         # Python error message parser
│   │   └── code_execution_service.py   # Business logic orchestration
│   ├── api/
│   │   └── v1/
│   │       └── code_execution.py       # FastAPI endpoint
│   └── schemas/
│       └── code_execution.py           # Pydantic request/response models
└── tests/
    ├── unit/
    │   ├── test_error_parser.py
    │   └── test_sandbox_validation.py
    ├── integration/
    │   ├── test_code_execution_api.py
    │   └── test_code_submission_repository.py
    └── fixtures/
        └── sample_code.py              # Test code samples
```

**Structure Decision**: Web application structure (backend microservice). The sandbox service integrates with existing backend infrastructure (FastAPI, SQLAlchemy models from F02, authentication from F01). Frontend integration is out of scope for this feature.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Sandbox execution abstraction (similar to Repository/LLM Provider patterns) | Enable swapping sandbox implementations (Docker, Piston API, custom) without changing business logic. Critical for testing (mock sandbox) and future flexibility. | Direct Docker calls would lock us into one implementation, make unit testing impossible (can't mock Docker daemon), and prevent future migration to managed services like Piston API. |

**Justification**: This abstraction follows the same pattern as LLM Provider Abstraction (constitution Section V) - a protocol-based interface for swapping implementations. The complexity is justified because:
1. Security testing requires mock sandbox (can't test timeout/memory limits with real Docker in CI)
2. Future migration to managed sandbox services (Piston API, AWS Lambda) must not require rewriting business logic
3. Follows established project pattern (LLM Provider Abstraction)
