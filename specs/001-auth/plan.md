# Implementation Plan: Authentication & Authorization

**Branch**: `001-auth` | **Date**: 2026-03-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement secure authentication and authorization system using Better Auth (frontend) and FastAPI JWT (backend) with role-based access control. System supports user registration, email verification, login with JWT tokens (15-min access + 7-day refresh), password reset via magic links, and role-based permissions (student/teacher/admin). Includes rate limiting, password breach checking, session management, and Kong gateway integration for JWT validation.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 14+ (frontend)
**Primary Dependencies**: FastAPI, Better Auth, PyJWT, bcrypt, httpx (HaveIBeenPwned API), SQLAlchemy, Alembic
**Storage**: Neon PostgreSQL (users, sessions, password_reset_tokens, email_verification_tokens, rate_limit_counters tables)
**Testing**: pytest + httpx async client (backend integration), vitest + @testing-library/react (frontend), Playwright (E2E)
**Target Platform**: Linux server (FastAPI backend), Web browser (Next.js frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: 1000 concurrent auth requests, <150ms API response (non-AI), <500ms token refresh, <10s login flow
**Constraints**: <200ms p95 for auth endpoints, rate limiting (5 failures = 15min lockout), JWT validation by Kong gateway
**Scale/Scope**: MVP for ~1000 users, 7 user stories, 5 database tables, 10+ API endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality Standards
- ✅ Python: black + isort configured (auto-format on save + pre-commit)
- ✅ TypeScript: prettier + eslint with Next.js config
- ✅ Naming: snake_case (Python), camelCase (TS), PascalCase (components/classes)
- ✅ Documentation: Google-style docstrings for auth business logic, FastAPI route summaries

### Testing Principles
- ✅ Coverage targets: 80% FastAPI routes (auth critical), 85% database repos, 65% React components
- ✅ TDD approach: Strict TDD for auth flows (registration, login, token refresh, password reset)
- ✅ Test types: Unit (pytest/vitest), Integration (FastAPI + test DB), E2E (Playwright for login/registration flows)

### Performance Standards
- ✅ Latency budgets: <150ms FastAPI auth endpoints, <500ms token refresh, <800ms Next.js SSR
- ✅ Resource limits: Rate limiting (10 req/min per user via slowapi), DB query <40ms
- ✅ Optimization: DB indexes on user_id, email, created_at from day one

### Security Constraints (NON-NEGOTIABLE)
- ✅ Use Better Auth (NEVER build auth yourself)
- ✅ Short-lived JWTs (15 min access + 7 day refresh) - matches spec
- ✅ All FastAPI routes require auth by default via get_current_user dependency
- ✅ Rate-limit login: 5 failures → 15-minute lockout - matches spec
- ✅ NEVER use exec() or eval() (not applicable to auth feature)
- ✅ Secrets: .env.local (Next.js), .env (FastAPI), detect-secrets pre-commit hook

### Architecture Patterns
- ✅ Repository Pattern: DB access only through repos (UserRepository, SessionRepository, etc.)
- ✅ No business logic in route handlers (use service layer)
- ✅ Alembic migrations for all schema changes

### Business Logic Integrity
- ✅ Code execution sandbox constraints: Not applicable to auth feature
- ✅ Struggle detection: Not applicable to auth feature
- ✅ Mastery calculation: Not applicable to auth feature

**GATE STATUS**: ✅ PASS - All constitution requirements satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-auth/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── auth-api.yaml    # OpenAPI spec for auth endpoints
│   └── jwt-schema.json  # JWT claims schema for Kong integration
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py           # User, Session, PasswordResetToken, EmailVerificationToken, RateLimitCounter
│   │   ├── schemas.py          # Pydantic models for request/response
│   │   ├── repository.py       # UserRepository, SessionRepository, etc.
│   │   ├── service.py          # AuthService (business logic)
│   │   ├── routes.py           # FastAPI endpoints
│   │   ├── dependencies.py     # get_current_user, require_role, etc.
│   │   ├── jwt.py              # JWT encoding/decoding, RS256 key management
│   │   ├── password.py         # Password hashing, HaveIBeenPwned check
│   │   └── rate_limit.py       # Rate limiting logic
│   ├── database.py             # SQLAlchemy engine, session factory
│   └── config.py               # Settings (JWT secret, email config, etc.)
├── alembic/
│   └── versions/
│       └── 001_create_auth_tables.py
├── tests/
│   ├── unit/
│   │   ├── test_password.py
│   │   ├── test_jwt.py
│   │   └── test_rate_limit.py
│   ├── integration/
│   │   ├── test_auth_routes.py
│   │   └── test_auth_repository.py
│   └── conftest.py             # Test fixtures (test DB, test client)
└── requirements.txt

frontend/
├── src/
│   ├── lib/
│   │   └── auth.ts             # Better Auth client configuration
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   ├── PasswordResetForm.tsx
│   │   │   └── EmailVerificationBanner.tsx
│   │   └── ProtectedRoute.tsx
│   ├── app/
│   │   ├── auth/
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   ├── reset-password/page.tsx
│   │   │   └── verify-email/page.tsx
│   │   └── api/
│   │       └── auth/
│   │           └── [...betterauth]/route.ts
│   └── hooks/
│       └── useAuth.ts          # Custom hook for auth state
└── tests/
    ├── components/
    │   └── auth/
    │       ├── LoginForm.test.tsx
    │       └── RegisterForm.test.tsx
    └── e2e/
        ├── auth-registration.spec.ts
        └── auth-login.spec.ts
```

**Structure Decision**: Web application structure with separate backend/ and frontend/ directories. Backend uses FastAPI with layered architecture (models → repository → service → routes). Frontend uses Next.js App Router with Better Auth integration. Auth feature is isolated in backend/src/auth/ module for clear separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution requirements satisfied.
