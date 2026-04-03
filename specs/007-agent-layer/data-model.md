# Data Model: AI Agent Layer

## AgentSession

Represents an ongoing tutoring conversation between a student and the agent system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Unique session identifier |
| user_id | UUID | FK → users.id, NOT NULL, INDEX | Owner of the session |
| status | VARCHAR(20) | NOT NULL, CHECK (status IN ('active', 'completed', 'abandoned')) | Session lifecycle state |
| conversation_history | JSONB | NOT NULL, default '[]' | Array of {role, content, timestamp} objects |
| active_agent | VARCHAR(30) | NULL | Last specialist agent that handled a message |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | Session creation time |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | Last message time |

**Indexes**: `idx_agent_session_user_id`, `idx_agent_session_status`, `idx_agent_session_updated_at`

## RoutingDecision

Represents a single intent classification event for a student message.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Unique routing event identifier |
| session_id | UUID | FK → agent_sessions.id, NOT NULL, INDEX | Associated session |
| user_id | UUID | FK → users.id, NOT NULL, INDEX | Student who sent the message |
| message | TEXT | NOT NULL | The student's original message text |
| intent | VARCHAR(30) | NOT NULL, CHECK (intent IN ('concept-explanation', 'code-debug', 'code-review', 'exercise-generation', 'progress-summary', 'general')) | Classified intent category |
| confidence | FLOAT | NOT NULL, CHECK (confidence >= 0 AND confidence <= 1) | Routing confidence score |
| target_agent | VARCHAR(30) | NOT NULL | Selected specialist agent name |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | When the routing decision was made |

**Indexes**: `idx_routing_session_id`, `idx_routing_user_id`, `idx_routing_intent`, `idx_routing_created_at`

## HintProgression

Tracks a student's debugging session through the progressive hint system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Unique hint progression identifier |
| session_id | UUID | FK → agent_sessions.id, NOT NULL, INDEX | Associated tutoring session |
| user_id | UUID | FK → users.id, NOT NULL, INDEX | Student receiving hints |
| error_context | JSONB | NOT NULL | {error_type, error_message, code_snippet, line_number} |
| hint_level | INTEGER | NOT NULL, CHECK (hint_level BETWEEN 1 AND 3), default 1 | Current hint level (1=high-level, 2=specific, 3=concrete fix) |
| hints_provided | JSONB | NOT NULL, default '[]' | Array of {level, hint_text, timestamp} objects |
| solution_revealed | BOOLEAN | NOT NULL, default false | Whether the full solution was shown |
| resolved | BOOLEAN | NOT NULL, default false | Whether the student resolved the error |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | Debug session start time |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | Last hint provided |

**Indexes**: `idx_hint_session_id`, `idx_hint_user_id`, `idx_hint_resolved`

## Exercise

Represents a coding challenge generated for practice.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Unique exercise identifier |
| topic | VARCHAR(100) | NOT NULL, INDEX | Curriculum topic (e.g., "loops", "functions") |
| difficulty | VARCHAR(20) | NOT NULL, CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')) | Difficulty level |
| description | TEXT | NOT NULL | Problem description with examples |
| starter_code | TEXT | NULL | Optional starter code template |
| test_cases | JSONB | NOT NULL | Array of {input, expected_output, assert_statement} objects |
| solution_code | TEXT | NULL | Reference solution (hidden from students) |
| creator | VARCHAR(20) | NOT NULL, default 'system', CHECK (creator IN ('system', 'teacher')) | Who created the exercise |
| created_by_user_id | UUID | FK → users.id, NULL | User who created it (if teacher) |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |

**Indexes**: `idx_exercise_topic`, `idx_exercise_difficulty`, `idx_exercise_creator`

## ExerciseSubmission

Represents a student's attempt at an exercise.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Unique submission identifier |
| exercise_id | UUID | FK → exercises.id, NOT NULL, INDEX | Exercise being attempted |
| user_id | UUID | FK → users.id, NOT NULL, INDEX | Student who submitted |
| submitted_code | TEXT | NOT NULL | The student's code |
| test_results | JSONB | NOT NULL | Array of {test_index, passed, error_message} objects |
| score | FLOAT | NOT NULL, CHECK (score >= 0 AND score <= 100) | Percentage score (0-100) |
| feedback | TEXT | NULL | Constructive feedback from Exercise Agent |
| execution_time_ms | INTEGER | NULL | Sandbox execution time in milliseconds |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | Submission timestamp |

**Indexes**: `idx_submission_exercise_id`, `idx_submission_user_id`, `idx_submission_score`, `idx_submission_created_at`

## MasteryRecord

Represents a student's mastery score for a specific topic.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Unique mastery record identifier |
| user_id | UUID | FK → users.id, NOT NULL, INDEX | Student |
| topic | VARCHAR(100) | NOT NULL, INDEX | Curriculum topic |
| score | FLOAT | NOT NULL, CHECK (score >= 0 AND score <= 100) | Overall mastery score (0-100) |
| level | VARCHAR(20) | NOT NULL, CHECK (level IN ('Beginner', 'Learning', 'Proficient', 'Mastered')) | Mapped mastery level |
| component_breakdown | JSONB | NOT NULL | {exercises: float, quizzes: float, code_quality: float, streak: float, missing_components: string[]} |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | Last calculation time |

**Indexes**: `idx_mastery_user_id`, `idx_mastery_topic`, `idx_mastery_user_topic` (composite UNIQUE)

## Relationships

```
User 1───* AgentSession
User 1───* RoutingDecision
User 1───* HintProgression
User 1───* ExerciseSubmission
User 1───* MasteryRecord
User 1───* Exercise (if teacher-created)

AgentSession 1───* RoutingDecision
AgentSession 1───* HintProgression

Exercise 1───* ExerciseSubmission
```

## State Transitions

### AgentSession
```
active → completed (student finishes tutoring session)
active → abandoned (no activity for 30 minutes)
```

### HintProgression
```
level 1 → level 2 (student asks for more help)
level 2 → level 3 (student asks for more help)
level 3 → solution_revealed=true (student requests solution)
any level → resolved=true (student fixes error)
```

### MasteryRecord
```
Score recalculated on:
- New exercise submission
- New quiz attempt
- New code quality rating
- Streak change
Level derived from score thresholds (fixed per constitution)
```
