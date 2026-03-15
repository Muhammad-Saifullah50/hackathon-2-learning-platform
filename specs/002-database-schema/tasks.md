# Tasks: Database Schema & Migrations

**Input**: Design documents from `/specs/002-database-schema/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are excluded from this implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and database infrastructure setup

- [X] T001 Verify F01 authentication migrations are applied and get latest revision ID
- [X] T002 [P] Install SQLAlchemy 2.0+, Alembic 1.13+, asyncpg, and Pydantic 2.0+ dependencies in backend/requirements.txt
- [X] T003 [P] Configure Neon PostgreSQL connection string in backend/.env
- [X] T004 Create database configuration module in backend/src/database.py with async engine and session factory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database models and migrations that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create Alembic migration 002a_extend_users to add role, preferences, deleted_at columns to users table in backend/alembic/versions/
- [X] T006 [P] Create Alembic migration 002b_user_profiles_streaks for user_profiles and user_streaks tables in backend/alembic/versions/
- [X] T007 [P] Create Alembic migration 002c_curriculum_structure for modules, lessons, exercises, quizzes tables in backend/alembic/versions/
- [X] T008 [P] Create Alembic migration 002d_progress_tracking for user_exercise_progress, user_quiz_attempts, user_module_mastery tables in backend/alembic/versions/
- [X] T009 [P] Create Alembic migration 002e_code_submissions for code_submissions table in backend/alembic/versions/
- [X] T010 [P] Create Alembic migration 002f_llm_cache for llm_cache table in backend/alembic/versions/
- [X] T011 Create Alembic migration 002g_seed_curriculum to insert 8 Python modules in backend/alembic/versions/
- [X] T012 Apply all migrations to database using alembic upgrade head
- [X] T013 [P] Create base model class with soft delete mixin in backend/src/models/base.py
- [X] T014 [P] Extend User model with role, preferences, deleted_at fields in backend/src/models/user.py
- [X] T015 [P] Create UserProfile model in backend/src/models/user.py
- [X] T016 [P] Create UserStreak model in backend/src/models/user.py
- [X] T017 [P] Create Module model in backend/src/models/curriculum.py
- [X] T018 [P] Create Lesson model in backend/src/models/curriculum.py
- [X] T019 [P] Create Exercise model in backend/src/models/curriculum.py
- [X] T020 [P] Create Quiz model in backend/src/models/curriculum.py
- [X] T021 Verify all models are importable and database schema matches migrations

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 5 - User Account Management (Priority: P1) 🎯 MVP Component

**Goal**: Extend user accounts with role-based access and preferences storage

**Independent Test**: Create user accounts with different roles (student, teacher, admin), store preferences, verify role-based queries return correct user sets, and test soft delete with PII anonymization

- [X] T022 [P] [US5] Create UserRepository class with CRUD operations in backend/src/repositories/user_repository.py
- [X] T023 [P] [US5] Implement get_by_role method in UserRepository for role-based queries in backend/src/repositories/user_repository.py
- [X] T024 [P] [US5] Implement update_preferences method in UserRepository in backend/src/repositories/user_repository.py
- [X] T025 [US5] Implement soft_delete method with PII anonymization in UserRepository in backend/src/repositories/user_repository.py
- [X] T026 [US5] Add validation for role enum (student/teacher/admin) using Pydantic schema in backend/src/schemas/user.py
- [X] T027 [US5] Add validation for preferences JSONB structure using Pydantic schema in backend/src/schemas/user.py

**Checkpoint**: User Story 5 complete - user account management with roles and preferences is functional

---

## Phase 4: User Story 2 - Curriculum Content Management (Priority: P1) 🎯 MVP Component

**Goal**: Organize Python curriculum into 8 modules with lessons and exercises

**Independent Test**: Query the 8 Python modules in order, retrieve lessons for a module with correct ordering, retrieve exercises for a lesson with starter code and content references

- [X] T028 [P] [US2] Create CurriculumRepository class in backend/src/repositories/curriculum_repository.py
- [X] T029 [P] [US2] Implement get_all_modules method with ordering in CurriculumRepository in backend/src/repositories/curriculum_repository.py
- [X] T030 [P] [US2] Implement get_lessons_by_module method with ordering in CurriculumRepository in backend/src/repositories/curriculum_repository.py
- [X] T031 [P] [US2] Implement get_exercises_by_lesson method with ordering in CurriculumRepository in backend/src/repositories/curriculum_repository.py
- [X] T032 [P] [US2] Implement get_quizzes_by_lesson method in CurriculumRepository in backend/src/repositories/curriculum_repository.py
- [X] T033 [US2] Add soft delete filtering to all curriculum queries (deleted_at IS NULL) in backend/src/repositories/curriculum_repository.py
- [X] T034 [US2] Create Pydantic schemas for Module, Lesson, Exercise, Quiz in backend/src/schemas/curriculum.py

**Checkpoint**: User Story 2 complete - curriculum structure is queryable and maintains proper ordering

---

## Phase 5: User Story 1 - Student Progress Tracking (Priority: P1) 🎯 MVP Component

**Goal**: Track student progress across exercises, quizzes, and calculate mastery scores

**Independent Test**: Create sample student records, insert exercise completions, quiz attempts, code submissions, verify mastery scores are calculated correctly according to formula (40% exercises, 30% quizzes, 20% code quality, 10% streak)

- [X] T035 [P] [US1] Create UserExerciseProgress model in backend/src/models/progress.py
- [X] T036 [P] [US1] Create UserQuizAttempt model in backend/src/models/progress.py
- [X] T037 [P] [US1] Create UserModuleMastery model with optimistic locking (version column) in backend/src/models/progress.py
- [X] T038 [P] [US1] Create ProgressRepository class in backend/src/repositories/progress_repository.py
- [X] T039 [P] [US1] Implement record_exercise_completion method in ProgressRepository in backend/src/repositories/progress_repository.py
- [X] T040 [P] [US1] Implement record_quiz_attempt method in ProgressRepository in backend/src/repositories/progress_repository.py
- [X] T041 [P] [US1] Implement update_streak method with business logic (increment/reset) in ProgressRepository in backend/src/repositories/progress_repository.py
- [X] T042 [US1] Implement calculate_mastery_score method with formula (40% exercises, 30% quizzes, 20% code quality, 10% streak) in backend/src/repositories/progress_repository.py
- [X] T043 [US1] Implement get_user_mastery_scores method to retrieve all module mastery for a user in ProgressRepository in backend/src/repositories/progress_repository.py
- [X] T044 [US1] Add optimistic locking retry logic for concurrent mastery updates in ProgressRepository in backend/src/repositories/progress_repository.py
- [X] T045 [US1] Create Pydantic schemas for UserExerciseProgress, UserQuizAttempt, UserModuleMastery in backend/src/schemas/progress.py

**Checkpoint**: User Story 1 complete - student progress tracking and mastery calculation is functional

---

## Phase 6: User Story 4 - Code Submission History (Priority: P2)

**Goal**: Store and query student code submissions with execution results for pattern analysis

**Independent Test**: Submit multiple code attempts for a student (some successful, some with errors), query submission history, verify all attempts are stored with timestamps, results, and error messages

- [X] T046 [P] [US4] Create CodeSubmission model in backend/src/models/submission.py
- [X] T047 [P] [US4] Create SubmissionRepository class in backend/src/repositories/submission_repository.py
- [X] T048 [P] [US4] Implement create_submission method in SubmissionRepository in backend/src/repositories/submission_repository.py
- [X] T049 [P] [US4] Implement get_submission_history method with pagination in SubmissionRepository in backend/src/repositories/submission_repository.py
- [X] T050 [P] [US4] Implement get_failed_attempts_count method for struggle detection in SubmissionRepository in backend/src/repositories/submission_repository.py
- [X] T051 [US4] Implement detect_error_patterns method to identify repeated error types in SubmissionRepository in backend/src/repositories/submission_repository.py
- [X] T052 [US4] Add validation for result JSONB structure (stdout, stderr, execution_time_ms, success) using Pydantic in backend/src/schemas/submission.py
- [X] T053 [US4] Create Pydantic schema for CodeSubmission in backend/src/schemas/submission.py

**Checkpoint**: User Story 4 complete - code submission history is stored and queryable for pattern analysis

---

## Phase 7: User Story 3 - AI Agent Response Caching (Priority: P2)

**Goal**: Cache LLM responses for frequently asked curriculum questions to reduce API costs

**Independent Test**: Generate cache key from prompt, store LLM response, verify subsequent identical prompts retrieve cached response, verify last_accessed_at timestamp updates, verify TTL-based purging

- [X] T054 [P] [US3] Create LLMCache model in backend/src/models/cache.py
- [X] T055 [P] [US3] Create CacheRepository class in backend/src/repositories/cache_repository.py
- [X] T056 [P] [US3] Implement generate_cache_key function using SHA-256 hash of normalized prompt + model + params in backend/src/repositories/cache_repository.py
- [X] T057 [P] [US3] Implement get_cached_response method with last_accessed_at update in CacheRepository in backend/src/repositories/cache_repository.py
- [X] T058 [P] [US3] Implement set_cached_response method with TTL strategy in CacheRepository in backend/src/repositories/cache_repository.py
- [X] T059 [US3] Implement purge_expired_cache method to delete entries not accessed in 60+ days in CacheRepository in backend/src/repositories/cache_repository.py
- [X] T060 [US3] Create Pydantic schema for LLMCache in backend/src/schemas/cache.py

**Checkpoint**: User Story 3 complete - LLM response caching is functional with TTL management

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T061 [P] Add database connection pooling configuration in backend/src/database.py
- [X] T062 [P] Create database session dependency for FastAPI in backend/src/dependencies.py
- [X] T063 [P] Add logging for all repository operations in backend/src/repositories/
- [X] T064 [P] Update CLAUDE.md with database schema completion status
- [X] T065 Verify quickstart.md instructions work end-to-end
- [X] T066 Run EXPLAIN ANALYZE on critical queries to verify index usage
- [X] T067 Document mastery calculation formula in code comments

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 5 (User Account Management) - Can start after Foundational
  - User Story 2 (Curriculum Content Management) - Can start after Foundational
  - User Story 1 (Student Progress Tracking) - Can start after Foundational
  - User Story 4 (Code Submission History) - Can start after Foundational
  - User Story 3 (AI Agent Response Caching) - Can start after Foundational
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses curriculum models but doesn't modify them)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Models before repositories
- Repositories before schemas
- Core implementation before validation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational migration creation tasks marked [P] can run in parallel (T006-T011)
- All Foundational model creation tasks marked [P] can run in parallel (T013-T020)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tasks marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all migration creation tasks together:
Task T006: "Create Alembic migration 002b_user_profiles_streaks"
Task T007: "Create Alembic migration 002c_curriculum_structure"
Task T008: "Create Alembic migration 002d_progress_tracking"
Task T009: "Create Alembic migration 002e_code_submissions"
Task T010: "Create Alembic migration 002f_llm_cache"

# Launch all model creation tasks together (after migrations applied):
Task T013: "Create base model class with soft delete mixin"
Task T014: "Extend User model with role, preferences, deleted_at"
Task T015: "Create UserProfile model"
Task T016: "Create UserStreak model"
Task T017: "Create Module model"
Task T018: "Create Lesson model"
Task T019: "Create Exercise model"
Task T020: "Create Quiz model"
```

---

## Parallel Example: User Story 1 (Student Progress Tracking)

```bash
# Launch all model creation tasks together:
Task T035: "Create UserExerciseProgress model"
Task T036: "Create UserQuizAttempt model"
Task T037: "Create UserModuleMastery model with optimistic locking"

# Launch all repository method tasks together (after models exist):
Task T039: "Implement record_exercise_completion method"
Task T040: "Implement record_quiz_attempt method"
Task T041: "Implement update_streak method"
```

---

## Implementation Strategy

### MVP First (P1 User Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 5 (User Account Management)
4. Complete Phase 4: User Story 2 (Curriculum Content Management)
5. Complete Phase 5: User Story 1 (Student Progress Tracking)
6. **STOP and VALIDATE**: Test all P1 stories independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 5 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 1 → Test independently → Deploy/Demo (MVP complete!)
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 3 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 5 (User Account Management)
   - Developer B: User Story 2 (Curriculum Content Management)
   - Developer C: User Story 1 (Student Progress Tracking)
3. Stories complete and integrate independently
4. Then proceed to P2 stories (User Story 4, User Story 3)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not explicitly requested in the specification
- All migrations must have both upgrade() and downgrade() functions
- Use optimistic locking (version column) for concurrent mastery updates
- Apply soft delete filtering (deleted_at IS NULL) to all curriculum queries
- Verify index usage with EXPLAIN ANALYZE before production deployment
