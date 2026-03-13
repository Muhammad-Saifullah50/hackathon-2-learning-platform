---
name: agents-md-gen
description: "Generate AGENTS.md files for projects following the Agentic AI Foundation (AAIF) standard. Use when the user asks to: (1) create or generate an AGENTS.md file, (2) make a project AI-agent-friendly, (3) add agent instructions or agent context to a codebase, (4) onboard AI coding agents to a project, (5) create agentic documentation, or (6) update an existing AGENTS.md. Works with any language, framework, or project type. AGENTS.md tells AI coding agents how to behave in a project — build commands, code style, security constraints, architecture patterns — distinct from README.md which tells humans what a project is."
---

# AGENTS.md Generator

Generate AGENTS.md files per the AAIF standard (OpenAI, donated to Linux Foundation Dec 2025). AGENTS.md tells AI agents how to behave in a project, adopted by 60,000+ projects and all major AI coding agents.

## Workflow

### Step 1: Analyze the Project

Scan the codebase to discover:

1. **Tech stack** — Read `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml`, `build.gradle`, `Makefile`, `docker-compose.yml`, or equivalent
2. **Project structure** — Run directory listing to map folder organization
3. **Existing conventions** — Check for `.eslintrc`, `.prettierrc`, `ruff.toml`, `rustfmt.toml`, `.editorconfig`, `tsconfig.json`, `clippy.toml`, `golangci-lint.yml`, or similar config files
4. **Build/test/lint commands** — Extract from `package.json` scripts, `Makefile` targets, `Justfile`, `pyproject.toml [tool.* ]` sections, CI config files (`.github/workflows/`, `.gitlab-ci.yml`)
5. **Existing AGENTS.md** — Check if one already exists (update vs create)
6. **Existing README.md** — Extract project context, but do not duplicate README content
7. **Monorepo detection** — Check for workspaces, multiple packages, or subdirectory-specific configs

### Step 2: Ask Clarifying Questions (if needed)

If the project analysis leaves ambiguity, ask the user about:
- Preferred code style rules not captured by linter configs
- Security constraints specific to their domain
- Architecture patterns or conventions not obvious from file structure
- Testing requirements or coverage thresholds

Keep questions minimal. If configs are clear, skip this step.

### Step 3: Generate AGENTS.md

Write the file at the project root (or subdirectory for monorepos). Follow the section order below.

## Required Sections (always include)

### 1. Build & Development Commands
```markdown
## Build & Development Commands
- `<install-cmd>` - Install dependencies
- `<build-cmd>` - Production build
- `<dev-cmd>` - Start development server
- `<test-cmd>` - Run all tests
- `<lint-cmd>` - Run linter
- `<format-cmd>` - Format code
```
Extract exact commands from package manager configs, Makefiles, CI files. Include only commands that actually exist in the project.

### 2. Code Style & Conventions
```markdown
## Code Style
- <language-version-requirement>
- <naming-conventions> (file names, variables, functions, classes)
- <import-ordering-rules>
- <specific-patterns> (e.g., "prefer named exports", "no default exports")
```
Derive from linter configs, tsconfig, existing code patterns. Be specific: "File names: kebab-case" not "Use consistent naming."

### 3. Security Constraints
```markdown
## Security
- Never hardcode API keys, tokens, or secrets
- Use environment variables for all credentials
- <framework-specific-security-rules>
```
Always include the "never hardcode secrets" rule. Add framework-specific rules (e.g., "No `eval()`", "Use parameterized queries", "Sanitize user input").

### 4. Architecture & File Organization
```markdown
## Architecture
- `<dir>/` - <purpose>
- `<dir>/` - <purpose>
```
Map the actual directory structure. Describe where new code should go, not just where existing code lives.

## Optional Sections (include when relevant)

### 5. Testing Conventions
Include when the project has tests. Cover: test file naming, test framework, assertion style, coverage requirements, mocking patterns.

### 6. Dependency Management
Include when there are specific package manager rules. Cover: which package manager, lock file policy, dependency justification requirements.

### 7. Git & PR Conventions
Include when the project uses conventional commits, specific branch naming, or merge strategies. Extract from existing commit history or CI checks.

### 8. Environment & Configuration
Include when the project has env vars, config files, or specific runtime requirements. List required environment variables and how to set them.

### 9. Error Handling Patterns
Include when the project has established error handling conventions. Cover: error types, logging patterns, response formats.

### 10. Performance Rules
Include when the project has specific performance constraints. Cover: query optimization, caching rules, bundle size limits.

### 11. Documentation Standards
Include when the project requires doc comments, API docs, or changelog entries.

### 12. Deployment & CI/CD
Include when the project has specific deployment procedures or CI pipeline requirements.

## Monorepo Support

For monorepos, generate multiple AGENTS.md files following the hierarchy rule:

```
project/
├── AGENTS.md              ← Root: project-wide rules
├── packages/frontend/
│   └── AGENTS.md          ← Frontend-specific overrides
└── packages/backend/
    └── AGENTS.md          ← Backend-specific overrides
```

Root AGENTS.md: shared rules (git conventions, security, CI).
Subdirectory AGENTS.md: package-specific rules (framework conventions, testing patterns, build commands).

Subdirectory files override root rules for their scope.

## Writing Rules

1. **Be specific, not vague** — "File names: kebab-case (e.g., `user-profile.tsx`)" not "Use consistent naming"
2. **Include exact commands** — "`pnpm test`" not "run the tests"
3. **Only document real conventions** — Derive from actual configs and code, do not invent rules
4. **Keep it actionable** — Every line should tell an agent what to do or not do
5. **No project motivation** — That belongs in README.md, not AGENTS.md
6. **No tutorials** — Agents don't need "Getting Started" guides
7. **Use imperative mood** — "Use TypeScript strict mode" not "TypeScript strict mode should be used"

## Reference

For detailed specification, section examples by language/framework (Python, Next.js, Go, Rust), and the hierarchy rule: see [references/agents-md-spec.md](references/agents-md-spec.md).
