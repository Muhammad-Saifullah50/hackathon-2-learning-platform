---
id: "0003"
title: "Generate tasks for agent layer"
stage: tasks
date: "2026-04-03"
surface: cli
model: qwen3.6-plus-free
feature: 007-agent-layer
branch: 007-agent-layer
user: saifullah
command: /sp.tasks
labels: [tasks, agent-layer, implementation]
links:
  spec: specs/007-agent-layer/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - specs/007-agent-layer/tasks.md
tests:
  - N/A (task generation phase, no code changes yet)
---

## Prompt

use the /sp.tasks command from .claude/commands to generate acrtionable rtaskjs

## Response snapshot

Executed the /sp.tasks command workflow for feature 007-agent-layer (AI Agent Layer). Loaded all design documents (plan.md, spec.md, research.md, data-model.md, contracts/agent-api.yaml, quickstart.md) and generated a comprehensive tasks.md with 72 actionable tasks organized into 9 phases:

- **Phase 1 (Setup)**: 7 tasks — directory structure, package files, test file scaffolding
- **Phase 2 (Foundational)**: 13 tasks — SQLAlchemy models, Pydantic schemas, Alembic migration, 4 repositories, BaseAgent abstract class, enhanced prompts, router registration
- **Phase 3 (US1 - P1)**: 16 tasks — TriageAgent routing, 5 agent service stubs, unified chat endpoint, session endpoint, auth, error handling, tests
- **Phase 4 (US2 - P2)**: 4 tasks — level-adapted concept explanations, enhanced prompts, topic handling
- **Phase 5 (US3 - P2)**: 7 tasks — progressive hint state machine, error parsing, hint generation, struggle detection, hints advance endpoint
- **Phase 6 (US4 - P2)**: 4 tasks — code review with static analysis, PEP 8 checking, positive reinforcement
- **Phase 7 (US5 - P3)**: 7 tasks — exercise generation, grading with DockerSandbox, submission endpoint, partial credit
- **Phase 8 (US6 - P3)**: 7 tasks — mastery calculation (40/30/20/10), level mapping, weak area detection, progress endpoint, no-data handling
- **Phase 9 (Polish)**: 7 tasks — contract tests, index verification, formatting, full test suite, quickstart validation

Key decisions: Tests included for all user stories (constitution requires TDD for critical paths). Tasks follow strict checklist format with IDs, [P] markers, [US] labels, and exact file paths. MVP scope defined as US1 only (36 tasks).

## Outcome

- Impact: Complete, actionable task list for implementing all 6 AI tutoring agents with clear dependencies, parallel opportunities, and incremental delivery strategy
- Tests: Task list includes test tasks for all 6 user stories (T021-T023, T037, T041, T048, T052, T059, T066)
- Files: 1 new file — specs/007-agent-layer/tasks.md (72 tasks)
- Next prompts: /sp.implement to begin implementation, starting with Phase 1 Setup
- Reflection: Organized by user story priority (P1→P2→P3) so each phase delivers independently testable value. Foundational phase (Phase 2) is the critical path — 13 tasks that block everything else.

## Evaluation notes (flywheel)

- Failure modes observed: None — task generation phase only
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): 0003
- Next experiment (smallest change to try): None — ready for implementation
