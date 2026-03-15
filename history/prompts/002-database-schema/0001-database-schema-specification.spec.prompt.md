---
id: 0001
title: Database Schema Specification
stage: spec
date: 2026-03-15
surface: agent
model: claude-sonnet-4.5
feature: 002-database-schema
branch: 002-database-schema
user: saifullah
command: /sp.specify
labels: ["database", "schema", "migrations", "alembic", "postgresql"]
links:
  spec: specs/002-database-schema/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-database-schema/spec.md
  - specs/002-database-schema/checklists/requirements.md
tests:
  - Specification quality validation (all items passed)
---

## Prompt

User requested specification for feature 002-database-schema with detailed architectural decisions:

**Feature Description**: "Database Schema & Migrations - Design and implement the complete PostgreSQL schema for users, lessons, progress, exercises, quizzes, and LLM cache with Alembic migrations"

**Key Architectural Decisions Provided**:
1. Extend existing F01 users table (not separate user_profiles) for role and core preferences
2. Create new Alembic migrations that depend on F01's migrations (never modify existing migrations)
3. Store mastery score components separately (exercise progress, quiz attempts, code submissions, streaks) and compute/cache final score in user_module_mastery table
4. LLM cache strategy: SHA-256 hash key, differentiated TTL (indefinite for curriculum, 7-30 days for exercises, no cache for student-specific), purge entries not accessed in 60+ days
5. Soft deletes with GDPR anonymization for users, lessons, exercises, quizzes
6. Hybrid curriculum approach: structure in DB (modules, lessons, exercises with ordering), content in static files/S3
7. Composite indexes on (user_id, module_id), (user_id, exercise_id), (user_id, quiz_id) from initial migration

## Response snapshot

Created comprehensive specification for F02: Database Schema & Migrations including:
- 5 prioritized user stories (P1: Student Progress Tracking, Curriculum Management, User Account Management; P2: AI Agent Response Caching, Code Submission History)
- 15 functional requirements covering schema extension, migration strategy, progress tracking, LLM caching, soft deletes, GDPR compliance, and indexing
- 12 key entities (User, User Profile, Module, Lesson, Exercise, Quiz, User Exercise Progress, User Quiz Attempt, Code Submission, User Streak, User Module Mastery, LLM Cache)
- 10 measurable success criteria (performance targets, cache efficiency, migration compatibility)
- 7 edge cases addressing data integrity, concurrent updates, and curriculum changes
- Clear assumptions, dependencies (F01), and out-of-scope items

Specification quality checklist: All items passed validation. No clarifications needed.

## Outcome

- ✅ Impact: Foundation feature specification complete, ready for planning phase
- 🧪 Tests: Specification quality validation passed (all checklist items)
- 📁 Files: spec.md, checklists/requirements.md
- 🔁 Next prompts: /sp.plan 002-database-schema
- 🧠 Reflection: User-provided architectural decisions eliminated all ambiguity, enabling complete specification without clarification questions

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Specification quality checklist - PASS (all items)
- Prompt variant (if applicable): Standard /sp.specify with detailed architectural context
- Next experiment (smallest change to try): Proceed to planning phase with /sp.plan
