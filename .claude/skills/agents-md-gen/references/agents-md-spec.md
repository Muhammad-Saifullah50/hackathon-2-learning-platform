# AGENTS.md Specification Reference

## Table of Contents
- [Origin & Governance](#origin--governance)
- [Purpose](#purpose)
- [Required Sections](#required-sections)
- [Optional Sections](#optional-sections)
- [Hierarchy Rule](#hierarchy-rule)
- [Examples by Project Type](#examples-by-project-type)

## Origin & Governance

AGENTS.md was created by OpenAI, introduced August 2025, and donated to the Agentic AI Foundation (AAIF) under Linux Foundation governance in December 2025. Adopted by 60,000+ open-source projects and all major AI coding agents: Claude Code, Cursor, GitHub Copilot, Gemini CLI, Devin, goose, Codex CLI.

## Purpose

README.md tells humans "What is this project?"
AGENTS.md tells AI agents "How should I behave in this project?"

| Humans Need          | Agents Need               |
|----------------------|---------------------------|
| Project motivation   | Build and test commands    |
| Getting started      | Code style rules           |
| Contribution guide   | Security constraints       |
| Screenshots/demos    | File organization patterns |

## Required Sections

### 1. Build & Development Commands
Exact shell commands for building, testing, linting, formatting. No ambiguity.

```markdown
## Build & Development Commands
- `pnpm install` - Install dependencies
- `pnpm run build` - Production build
- `pnpm run dev` - Start development server
- `pnpm test` - Run all tests
- `pnpm run lint` - Run linter
- `pnpm run format` - Format code
```

### 2. Code Style & Conventions
Specific, actionable rules — not vague principles.

```markdown
## Code Style
- Use TypeScript strict mode for all new code
- Maximum function length: 50 lines
- File names: kebab-case (e.g., `user-profile.tsx`)
- Use named exports, avoid default exports
- Prefer `const` over `let`; never use `var`
- Import order: external libs → internal modules → relative imports
```

### 3. Security Constraints
What agents must never do.

```markdown
## Security
- Never hardcode API keys, tokens, or secrets
- Use environment variables for all credentials
- No `eval()` or `Function()` constructors
- Never commit `.env` files
- Sanitize all user inputs before database queries
- Use parameterized queries, never string concatenation for SQL
```

### 4. Architecture & File Organization
Where code goes, how the project is structured.

```markdown
## Architecture
- All API routes go in `/src/api/`
- Database queries only through `/src/db/` layer
- Shared types in `/src/types/`
- Components follow atomic design: atoms → molecules → organisms
- Business logic in `/src/services/`, not in route handlers
```

## Optional Sections

### 5. Testing Conventions
```markdown
## Testing
- Write tests for all new features
- Test files: `*.test.ts` co-located with source
- Use `describe`/`it` blocks, not `test()`
- Mock external APIs, never call real endpoints in tests
- Minimum coverage: 80% for new code
```

### 6. Dependency & Package Management
```markdown
## Dependencies
- Package manager: pnpm (do not use npm or yarn)
- Lock file must be committed
- Justify new dependencies in PR description
- Prefer stdlib over external packages when possible
```

### 7. Git & PR Conventions
```markdown
## Git Conventions
- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- Branch naming: `feat/description`, `fix/description`
- Squash merge to main
- No force pushes to main/develop
```

### 8. Environment & Configuration
```markdown
## Environment
- Node.js >= 20.x required
- Use `.env.example` as template (never `.env` directly)
- Required env vars: DATABASE_URL, API_KEY, REDIS_URL
```

### 9. Error Handling Patterns
```markdown
## Error Handling
- Use custom error classes extending `AppError`
- All async handlers wrapped in try/catch
- Return structured error responses: `{ error: string, code: number }`
- Log errors with context (request ID, user ID)
```

### 10. Performance & Optimization Rules
```markdown
## Performance
- Database queries must use indexes
- No N+1 queries — use eager loading
- API responses cached for 60s where appropriate
- Images optimized before serving
```

### 11. Documentation Standards
```markdown
## Documentation
- JSDoc for all exported functions
- Update README.md when adding new features
- API endpoints documented in OpenAPI/Swagger
```

### 12. Deployment & CI/CD
```markdown
## Deployment
- CI runs: lint → typecheck → test → build
- Staging deploys from `develop` branch
- Production deploys from `main` via tagged releases
```

## Hierarchy Rule

The nearest AGENTS.md file takes precedence. This enables monorepo support:

```
company/
├── AGENTS.md                    ← Root: company-wide rules
├── packages/
│   ├── frontend/
│   │   ├── AGENTS.md            ← Frontend-specific (React, hooks, CSS)
│   │   └── src/
│   └── backend/
│       ├── AGENTS.md            ← Backend-specific (Express, Prisma, API)
│       └── src/
```

When an agent works on `packages/frontend/src/Button.tsx`, it reads:
1. `packages/frontend/AGENTS.md` (nearest — takes precedence)
2. `AGENTS.md` (root — company-wide rules also apply)

Subdirectory AGENTS.md files override root rules for their scope. Root rules apply universally unless explicitly overridden.

## Examples by Project Type

### Python (FastAPI + SQLAlchemy)
```markdown
# AGENTS.md

## Build & Development Commands
- `uv sync` - Install dependencies
- `uvicorn app.main:app --reload` - Start dev server
- `pytest` - Run all tests
- `pytest --cov=app` - Run tests with coverage
- `ruff check .` - Lint
- `ruff format .` - Format

## Code Style
- Python 3.12+ features allowed
- Type hints required on all function signatures
- Use Pydantic models for request/response schemas
- Async functions for all route handlers
- Follow PEP 8, enforced by ruff

## Architecture
- `app/` - Application root
- `app/api/` - Route handlers (thin layer, delegate to services)
- `app/services/` - Business logic
- `app/models/` - SQLAlchemy models
- `app/schemas/` - Pydantic schemas
- `app/core/` - Config, security, dependencies
- `alembic/` - Database migrations

## Testing
- Test files in `tests/` mirroring `app/` structure
- Use `pytest-asyncio` for async tests
- Use `httpx.AsyncClient` for API tests, not `TestClient`
- Factory fixtures in `tests/conftest.py`

## Security
- Never hardcode secrets; use `app/core/config.py` with pydantic-settings
- All endpoints require authentication unless explicitly public
- Use `Depends(get_current_user)` for auth
- SQL via SQLAlchemy ORM only — no raw SQL strings
```

### Next.js (App Router + Prisma)
```markdown
# AGENTS.md

## Build & Development Commands
- `pnpm install` - Install dependencies
- `pnpm dev` - Start dev server (port 3000)
- `pnpm build` - Production build
- `pnpm test` - Run Jest tests
- `pnpm lint` - ESLint check
- `pnpm db:push` - Push Prisma schema to database
- `pnpm db:generate` - Generate Prisma client
- `pnpm db:migrate` - Run migrations

## Code Style
- TypeScript strict mode; no `any` types
- File names: kebab-case
- Component names: PascalCase
- Use `"use client"` directive only when needed
- Prefer Server Components by default
- Named exports for components

## Architecture
- `src/app/` - Next.js App Router pages and layouts
- `src/components/` - Reusable UI components (atomic design)
- `src/lib/` - Utility functions and shared logic
- `src/server/` - Server-only code (tRPC routers, db queries)
- `prisma/` - Database schema and migrations
- `public/` - Static assets

## Security
- Server Actions for mutations; never expose DB in client components
- Environment variables via `env.mjs` with Zod validation
- CSRF protection on all form submissions
- Use `next-auth` for authentication; sessions stored server-side
```

### Go (REST API + PostgreSQL)
```markdown
# AGENTS.md

## Build & Development Commands
- `go build ./...` - Build all packages
- `go test ./...` - Run all tests
- `go test -race ./...` - Run tests with race detector
- `golangci-lint run` - Lint
- `go generate ./...` - Run code generation
- `make migrate-up` - Run database migrations

## Code Style
- Follow Effective Go and Go Code Review Comments
- Error wrapping: `fmt.Errorf("operation: %w", err)`
- No naked returns
- Interfaces defined by consumers, not producers
- Table-driven tests

## Architecture
- `cmd/` - Application entrypoints
- `internal/` - Private application code
- `internal/handler/` - HTTP handlers (thin, delegate to service)
- `internal/service/` - Business logic
- `internal/repository/` - Database access (sqlc generated)
- `internal/model/` - Domain types
- `pkg/` - Public library code
- `migrations/` - SQL migration files

## Security
- Use `sqlc` for type-safe queries; no string concatenation
- Validate all input with struct tags
- Context propagation for cancellation and timeouts
- No `log.Fatal` in library code
```

### Rust (Axum + SQLx)
```markdown
# AGENTS.md

## Build & Development Commands
- `cargo build` - Build project
- `cargo test` - Run all tests
- `cargo clippy -- -D warnings` - Lint (treat warnings as errors)
- `cargo fmt --check` - Check formatting
- `cargo fmt` - Format code
- `sqlx migrate run` - Run database migrations

## Code Style
- Use `thiserror` for error types; `anyhow` only in `main`/tests
- Prefer `impl Into<T>` over concrete types in function params
- Exhaustive match arms; no wildcard `_` unless truly needed
- `#[must_use]` on functions returning important values

## Architecture
- `src/main.rs` - Entrypoint and router setup
- `src/routes/` - Axum route handlers
- `src/services/` - Business logic
- `src/models/` - Database models and domain types
- `src/error.rs` - Application error types
- `migrations/` - SQLx migration files

## Security
- Use `sqlx` query macros for compile-time checked SQL
- Extract secrets from environment via `dotenvy`
- Never use `unwrap()` in production code; use `?` or `expect` with context
```
