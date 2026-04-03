---
id: "0001"
title: "specify-agent-layer"
stage: spec
date: 2026-04-03
surface: opencode-cli
model: qwen3.6-plus-free
feature: 007-agent-layer
branch: 007-agent-layer
user: saifullah
command: /sp.specify
labels: [spec, agent-layer, openai-agents-sdk]
links:
  spec: specs/007-agent-layer/spec.md
  ticket: FEATURES.md#f07-f12
  adr: history/adr/ (pending - multi-agent architecture decision)
  pr: (pending)
files:
  - specs/007-agent-layer/spec.md
  - specs/007-agent-layer/checklists/requirements.md
tests:
  - (none yet - tests will be defined in /sp.tasks)
---

## Prompt

Build features 7 through 12 (the Agent Layer) as a single specification. The agents will be built using the OpenAI Agents SDK. Research using the context7-efficient skill, then discuss, and then write the specifications.

Key architectural decisions confirmed during discussion:
- Single FastAPI service for all agents (not microservices)
- SQLAlchemySession for conversation persistence (leverages existing Neon PostgreSQL)
- Deterministic code-based triage routing (satisfies AGENTS.md requirement for testable routing)
- OpenAI Agents SDK with handoffs for agent orchestration
- All 6 agents in one specification (tightly coupled through shared dependencies)

## Response snapshot

Created comprehensive specification for the AI Agent Layer (F07-F12) covering:
- 6 user stories with acceptance scenarios (P1-P3 prioritized)
- 44 functional requirements across 7 categories (Triage, Concepts, Code Review, Debug, Exercise, Progress, Cross-Cutting)
- 7 key entities defined
- 10 measurable success criteria
- Edge cases, assumptions, dependencies, security considerations documented
- Quality checklist: all items passed

## Outcome

- Impact: Complete specification for all 6 AI tutoring agents, ready for technical planning phase
- Tests: Will be defined in /sp.tasks phase
- Files: spec.md (comprehensive), checklists/requirements.md (all passed)
- Next prompts: /sp.plan to create technical implementation plan
- Reflection: Spec covers all agent interactions without leaking implementation details; references to F01-F06 are appropriate cross-feature dependencies

## Evaluation notes (flywheel)

- Failure modes observed: None — spec validated cleanly against all checklist items
- Graders run and results (PASS/FAIL): Not applicable at spec phase
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.plan to generate technical architecture
