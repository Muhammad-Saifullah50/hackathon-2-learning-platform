# Feature Specification: Database Schema & Migrations

**Feature Branch**: `002-database-schema`
**Created**: 2026-03-15
**Status**: Draft
**Input**: User description: "Database Schema & Migrations - Design and implement the complete PostgreSQL schema for users, lessons, progress, exercises, quizzes, and LLM cache with Alembic migrations"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Student Progress Tracking (Priority: P1)

As a student, when I complete exercises, take quizzes, and submit code, the system must accurately track my progress and calculate my mastery score across all Python modules so I can see my learning journey.

**Why this priority**: This is the core data foundation for the entire learning platform. Without accurate progress tracking, students cannot see their advancement and the platform loses its primary value proposition.

**Independent Test**: Can be fully tested by creating sample student records, inserting exercise completions, quiz attempts, and code submissions, then verifying that mastery scores are calculated correctly according to the formula (40% exercises, 30% quizzes, 20% code quality, 10% streak).

**Acceptance Scenarios**:

1. **Given** a student has completed 5 exercises in Module 1, **When** the mastery score is calculated, **Then** the exercise component (40%) reflects the completion rate accurately
2. **Given** a student has taken 3 quizzes with scores 80%, 90%, 70%, **When** mastery is calculated, **Then** the quiz component (30%) reflects the average score
3. **Given** a student has a 7-day learning streak, **When** mastery is calculated, **Then** the streak component (10%) is included in the total score
4. **Given** a student's code submissions have quality ratings, **When** mastery is calculated, **Then** the code quality component (20%) reflects the average rating

---

### User Story 2 - Curriculum Content Management (Priority: P1)

As a system administrator or teacher, I need to organize Python curriculum into 8 modules with lessons and exercises so that students have a structured learning path.

**Why this priority**: Without curriculum structure in the database, there's no content for students to learn. This is foundational infrastructure that all other features depend on.

**Independent Test**: Can be fully tested by inserting the 8 Python modules (Basics, Control Flow, Data Structures, Functions, OOP, Files, Errors, Libraries) with associated lessons and exercises, then verifying that the structure is queryable and maintains proper ordering.

**Acceptance Scenarios**:

1. **Given** the 8 Python modules are defined, **When** querying modules by order, **Then** they are returned in the correct sequence
2. **Given** a module has multiple lessons, **When** querying lessons for that module, **Then** lessons are returned in the correct order with content references
3. **Given** a lesson has associated exercises, **When** querying exercises for that lesson, **Then** exercises include starter code and content references
4. **Given** curriculum content is stored in static files, **When** a lesson is retrieved, **Then** the content reference points to the correct file location

---

### User Story 3 - AI Agent Response Caching (Priority: P2)

As a system operator, I need to cache LLM responses for frequently asked curriculum questions to reduce API costs and improve response times for common queries.

**Why this priority**: LLM API calls are expensive and slow. Caching static curriculum explanations can significantly reduce operational costs while improving user experience.

**Independent Test**: Can be fully tested by generating a cache key from a prompt, storing the LLM response, then verifying that subsequent identical prompts retrieve the cached response instead of making new API calls.

**Acceptance Scenarios**:

1. **Given** a student asks "What is a Python list?", **When** the LLM responds, **Then** the response is cached with a hash of the prompt as the key
2. **Given** a cached response exists for a prompt, **When** another student asks the same question, **Then** the cached response is returned without calling the LLM API
3. **Given** a cached curriculum explanation is 30 days old, **When** it is accessed, **Then** the last_accessed_at timestamp is updated
4. **Given** a cached response has not been accessed in 60 days, **When** the cleanup job runs, **Then** the cache entry is purged

---

### User Story 4 - Code Submission History (Priority: P2)

As a teacher or debug agent, I need to access a student's complete code submission history including errors and execution results so I can identify learning patterns and provide targeted help.

**Why this priority**: Historical code submissions enable struggle detection, pattern analysis, and personalized interventions. This is critical for the AI tutoring agents to function effectively.

**Independent Test**: Can be fully tested by submitting multiple code attempts for a student (some successful, some with errors), then querying the submission history and verifying all attempts are stored with timestamps, results, and error messages.

**Acceptance Scenarios**:

1. **Given** a student submits code for an exercise, **When** the code is executed, **Then** the submission is stored with code text, execution result, timestamp, and quality rating
2. **Given** a student has made 5 failed attempts on an exercise, **When** querying submission history, **Then** all 5 attempts are returned in chronological order with error details
3. **Given** a student encounters the same error type 3 times, **When** the debug agent queries submissions, **Then** the pattern is detectable for struggle alert triggering
4. **Given** a code submission is stored, **When** retention policy is applied, **Then** submissions older than the retention period are archived or deleted

---

### User Story 5 - User Account Management (Priority: P1)

As a user (student, teacher, or admin), I need my account information, role, and preferences stored securely so I can access the platform with appropriate permissions.

**Why this priority**: User accounts are the foundation of authentication and authorization. This extends the existing F01 auth schema with role-specific data.

**Independent Test**: Can be fully tested by creating user accounts with different roles (student, teacher, admin), storing preferences, and verifying that role-based queries return the correct user sets.

**Acceptance Scenarios**:

1. **Given** a new user registers, **When** their account is created, **Then** the user record includes role, email, and timestamps
2. **Given** a student user exists, **When** querying for students only, **Then** only users with role='student' are returned
3. **Given** a user updates their preferences, **When** the preferences are saved, **Then** subsequent queries return the updated preferences
4. **Given** a user requests account deletion (GDPR), **When** soft delete is triggered, **Then** the deleted_at timestamp is set and PII fields are anonymized

---

### Edge Cases

- What happens when a student completes an exercise but the exercise is later deleted from the curriculum? (Progress records must remain intact via soft delete)
- How does the system handle mastery calculation when a student has incomplete data (e.g., no quizzes taken yet)? (Calculate based on available components, normalize weights)
- What happens when the LLM cache grows beyond storage limits? (Purge entries not accessed in 60+ days, oldest first)
- How does the system handle concurrent updates to the same user's progress from multiple agents? (Use database transactions and optimistic locking)
- What happens when a module or lesson order is changed? (Existing progress records reference by ID, not order, so they remain valid)
- How does the system handle a student's streak when they miss a day? (Streak resets to 0, but longest_streak is preserved)
- What happens when curriculum content files are moved or renamed? (Content references must be updated via migration or content management system)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST extend the existing users table from F01 with role (student/teacher/admin) and preference fields
- **FR-002**: System MUST create Alembic migration files that depend on F01's existing migrations without modifying them
- **FR-003**: System MUST store curriculum structure (8 modules, lessons, exercises) with ordering and content references to static files
- **FR-004**: System MUST track student progress components separately: exercise completions, quiz scores, code quality ratings, and streaks
- **FR-005**: System MUST store computed mastery scores in a dedicated table (user_module_mastery) with calculation timestamps
- **FR-006**: System MUST cache LLM responses using SHA-256 hash of (prompt + model + relevant_params) as the cache key
- **FR-007**: System MUST implement differentiated TTL strategies for LLM cache: indefinite for curriculum content, 7-30 days for generated exercises, no caching for student-specific feedback
- **FR-008**: System MUST store all student code submissions with code text, execution results, timestamps, and quality ratings
- **FR-009**: System MUST implement soft deletes (deleted_at timestamp) for users, lessons, exercises, and quizzes
- **FR-010**: System MUST support GDPR compliance by anonymizing PII fields (email, name) when deleted_at is set
- **FR-011**: System MUST create composite indexes on (user_id, module_id), (user_id, exercise_id), and (user_id, quiz_id) for efficient mastery queries
- **FR-012**: System MUST enforce foreign key constraints between progress tables and user/curriculum tables
- **FR-013**: System MUST track last_accessed_at for LLM cache entries to enable TTL-based purging
- **FR-014**: System MUST store user streak data (current_streak, longest_streak, last_activity_date) for mastery calculation
- **FR-015**: System MUST support querying code submissions by user, exercise, and time range for pattern analysis

### Key Entities *(include if feature involves data)*

- **User**: Represents a platform user (student, teacher, or admin) with authentication credentials, role, preferences, and soft delete support. Extends F01's existing users table.
- **User Profile**: Optional 1:1 extension of User for role-specific metadata (teacher: bio, specialization, institution; student: grade_level, learning_goals). Only created when role-specific data exists.
- **Module**: Represents one of the 8 Python curriculum modules (Basics, Control Flow, Data Structures, Functions, OOP, Files, Errors, Libraries) with title, description, and ordering.
- **Lesson**: Represents a learning unit within a module with title, order, and content reference (path to static file or S3 key).
- **Exercise**: Represents a coding challenge within a lesson with title, order, starter code, and content reference.
- **Quiz**: Represents an assessment for a lesson or module with questions and expected answers.
- **User Exercise Progress**: Tracks a student's completion status, score, and attempt count for each exercise.
- **User Quiz Attempt**: Tracks a student's quiz submissions with score and timestamp.
- **Code Submission**: Stores all student code attempts with code text, execution result (stdout, stderr, execution time), quality rating, and timestamp.
- **User Streak**: Tracks a student's learning consistency with current streak, longest streak, and last activity date.
- **User Module Mastery**: Stores computed mastery scores (0-100%) for each user-module combination with calculation timestamp.
- **LLM Cache**: Stores cached LLM responses with cache key (SHA-256 hash), prompt text, response text, model identifier, token count, creation timestamp, last accessed timestamp, and optional expiration timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Database schema supports storing progress data for 10,000+ students without performance degradation
- **SC-002**: Mastery score queries complete in under 200ms for a single student across all 8 modules
- **SC-003**: LLM cache reduces API calls by at least 40% for common curriculum questions
- **SC-004**: All database migrations execute successfully on a fresh database and on databases with existing F01 schema
- **SC-005**: Composite indexes enable efficient queries for student progress dashboards (sub-second response times)
- **SC-006**: Soft delete mechanism preserves referential integrity while supporting GDPR anonymization
- **SC-007**: Code submission history queries return results in under 500ms for students with 100+ submissions
- **SC-008**: Cache purge operations complete in under 5 minutes for databases with 100,000+ cache entries
- **SC-009**: Curriculum structure queries support rendering the full 8-module learning path in under 100ms
- **SC-010**: Database schema supports concurrent updates from multiple AI agents without deadlocks or race conditions

## Assumptions

- F01 (Authentication & Authorization) is complete and has established the base users table with id, email, hashed_password, created_at, and updated_at fields
- Alembic is already configured in the project from F01
- PostgreSQL version is 12+ with support for composite indexes and JSON fields
- Static curriculum content files will be stored in a version-controlled directory or object storage (S3/R2)
- Code execution results (stdout, stderr) are text-based and do not exceed 10KB per submission
- LLM responses for caching are text-based and do not exceed 50KB per entry
- The platform will start with a single database instance (no sharding required for MVP)
- Database backups and disaster recovery are handled by the hosting provider (Neon PostgreSQL)
- User preferences are stored as JSON fields for flexibility without schema changes
- Quality ratings for code submissions are numeric scores (0-100) assigned by the Code Review Agent

## Dependencies

- **F01 (Authentication & Authorization)**: Must be complete before F02 can extend the users table and create dependent migrations
- **Neon PostgreSQL**: Database hosting platform must be provisioned and accessible
- **Alembic**: Migration tool must be configured (assumed complete from F01)

## Out of Scope

- Database replication and sharding strategies (single instance sufficient for MVP)
- Real-time database synchronization across multiple regions
- Advanced analytics queries and data warehousing (OLAP workloads)
- Automated database performance tuning and query optimization
- Database backup and restore procedures (handled by Neon)
- Migration rollback strategies beyond Alembic's built-in downgrade functionality
- Data archival and cold storage for historical submissions older than retention period
- Multi-tenancy and data isolation for different schools or organizations
