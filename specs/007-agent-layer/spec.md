# Feature Specification: AI Agent Layer

**Feature Branch**: `007-agent-layer`
**Created**: 2026-04-03
**Status**: Draft
**Input**: User description: "Build the AI Agent Layer (Features 07-12): Triage Agent, Concepts Agent, Code Review Agent, Debug Agent, Exercise Agent, and Progress Agent using OpenAI Agents SDK with handoffs, single FastAPI service, SQLAlchemy sessions, and deterministic code-based triage routing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Student Asks a Question and Gets Routed to the Right Agent (Priority: P1)

A student sends a natural language question (e.g., "What is a list comprehension?", "Why am I getting a TypeError?", "Review my code please") through the tutoring interface. The system classifies the intent, routes to the appropriate specialist agent, and returns a helpful, level-appropriate response. The routing is transparent to the student — they just get a good answer.

**Why this priority**: This is the core user-facing flow. Without it, no student can interact with any AI agent. Every other agent depends on this routing working correctly.

**Independent Test**: Can be fully tested by sending sample questions of each intent type and verifying the correct agent responds with appropriate content. Delivers the ability for students to get AI-powered help.

**Acceptance Scenarios**:

1. **Given** a student asks "What is a list comprehension?", **When** the system processes the question, **Then** the Concepts Agent responds with a clear explanation and code example appropriate to the student's level.
2. **Given** a student asks "Why does my code say 'TypeError: can only concatenate str (not "int") to str'?", **When** the system processes the question, **Then** the Debug Agent responds with an explanation of the error and a progressive hint.
3. **Given** a student asks "Can you review my code?", **When** the system processes the question with attached code, **Then** the Code Review Agent responds with feedback on correctness, style, and readability.
4. **Given** a student asks "Give me a practice exercise on functions", **When** the system processes the question, **Then** the Exercise Agent generates a coding challenge with test cases.
5. **Given** a student asks "How am I doing in this course?", **When** the system processes the question, **Then** the Progress Agent responds with a summary of their mastery scores and recommendations.
6. **Given** a student asks an ambiguous question that doesn't match any specialist intent, **When** the system processes the question, **Then** a general fallback response is provided that asks for clarification.

---

### User Story 2 - Concepts Agent Explains Topics at the Right Level (Priority: P2)

A student asks about a Python concept. The system detects the student's current level (beginner, intermediate, advanced) and tailors the explanation accordingly — simple analogies and basic examples for beginners, deeper technical details for advanced students. The response includes runnable code examples and suggests follow-up questions.

**Why this priority**: Concept explanation is the most common student interaction. Getting this right with level adaptation is essential for effective learning.

**Independent Test**: Can be tested by sending the same concept question with different student levels and verifying that explanations differ in complexity and depth.

**Acceptance Scenarios**:

1. **Given** a beginner-level student asks "What is a function?", **When** the Concepts Agent responds, **Then** the explanation uses simple analogies, minimal jargon, and a basic code example.
2. **Given** an advanced-level student asks "What is a function?", **When** the Concepts Agent responds, **Then** the explanation covers first-class functions, closures, decorators, and advanced patterns.
3. **Given** any student receives a concept explanation, **When** the response completes, **Then** it includes at least one runnable code example and 2-3 suggested follow-up questions.

---

### User Story 3 - Debug Agent Provides Progressive Hints (Priority: P2)

A student is stuck on a coding error. Instead of immediately giving the answer, the Debug Agent provides a progressive hint system: first a high-level pointer, then a more specific hint, and only the full solution after the student has exhausted hints or explicitly requests it.

**Why this priority**: Progressive hints promote learning over copy-pasting. This is a key differentiator from generic AI code helpers.

**Independent Test**: Can be tested by submitting code with a known error and verifying that the first response is a hint (not the solution), and that subsequent interactions progressively reveal more detail.

**Acceptance Scenarios**:

1. **Given** a student submits code with a bug, **When** the Debug Agent analyzes it, **Then** the first response provides a high-level hint about the error category without revealing the fix.
2. **Given** a student receives a hint but is still stuck and asks for more help, **When** the Debug Agent responds again, **Then** it provides a more specific hint pointing closer to the root cause.
3. **Given** a student has received all progressive hints and is still stuck, **When** they request the solution, **Then** the Debug Agent provides the corrected code with an explanation of what was wrong.
4. **Given** a student explicitly says "I don't understand" or "I'm stuck", **When** the Debug Agent processes this, **Then** it recognizes this as a struggle trigger and adapts to a simpler explanation level.

---

### User Story 4 - Code Review Agent Analyzes Student Code (Priority: P2)

A student submits completed code for review. The Code Review Agent evaluates it for correctness, PEP 8 style compliance, efficiency, and readability — then provides constructive feedback with positive reinforcement for what was done well.

**Why this priority**: Code review teaches good habits and helps students improve beyond "just making it work." Important for learning quality.

**Independent Test**: Can be tested by submitting code with known style issues, logic bugs, and good practices, and verifying the agent identifies each correctly.

**Acceptance Scenarios**:

1. **Given** a student submits code with PEP 8 style violations, **When** the Code Review Agent analyzes it, **Then** it identifies the style issues and suggests corrections.
2. **Given** a student submits code that works but is inefficient, **When** the Code Review Agent analyzes it, **Then** it suggests a more efficient approach with explanation.
3. **Given** a student submits well-written code, **When** the Code Review Agent analyzes it, **Then** it provides positive reinforcement and minor optional improvements.
4. **Given** a student submits code with a logic bug, **When** the Code Review Agent analyzes it, **Then** it identifies the bug and explains why it produces incorrect results.

---

### User Story 5 - Exercise Agent Generates and Grades Challenges (Priority: P3)

A student or teacher requests a coding exercise on a specific topic at a specific difficulty. The system generates a challenge with a description, starter code, and test cases. When the student submits their solution, the system auto-grades it and provides feedback including partial credit.

**Why this priority**: Exercises are essential for practice and mastery measurement. Lower priority than help-seeking flows because students need to understand concepts first before practicing.

**Independent Test**: Can be tested by requesting an exercise, receiving it, submitting a solution, and verifying the grading output matches expected results.

**Acceptance Scenarios**:

1. **Given** a student requests an exercise on "loops" at "beginner" difficulty, **When** the Exercise Agent generates it, **Then** the exercise includes a clear description, starter code, and test cases appropriate for beginners.
2. **Given** a student submits a correct solution to an exercise, **When** the system grades it, **Then** it returns a full score with positive feedback.
3. **Given** a student submits a partially correct solution, **When** the system grades it, **Then** it returns partial credit with specific feedback on what passed and what failed.
4. **Given** a student submits an incorrect solution, **When** the system grades it, **Then** it returns a score of zero with feedback on which test cases failed and hints for improvement.

---

### User Story 6 - Progress Agent Summarizes Learning Progress (Priority: P3)

A student asks about their progress. The Progress Agent calculates their mastery scores across topics using the defined formula (40% exercises, 30% quizzes, 20% code quality, 10% consistency streak), identifies weak areas, and provides personalized recommendations for what to study next.

**Why this priority**: Progress tracking motivates students and guides their learning path. Important but depends on exercise/quiz data existing first.

**Independent Test**: Can be tested by seeding progress data for a test user and verifying the summary output matches expected mastery calculations.

**Acceptance Scenarios**:

1. **Given** a student has completed exercises and quizzes across multiple topics, **When** they ask for their progress, **Then** the Progress Agent returns a summary with mastery scores per topic and overall.
2. **Given** a student has weak mastery in a specific topic, **When** they ask for progress, **Then** the Progress Agent identifies the weak area and recommends specific practice.
3. **Given** a student has an active learning streak, **When** they ask for progress, **Then** the Progress Agent acknowledges the streak and encourages consistency.
4. **Given** a student has no progress data yet, **When** they ask for progress, **Then** the Progress Agent provides an encouraging onboarding message with suggested first steps.

---

### Edge Cases

- What happens when a student sends a message with no recognizable intent? → System provides a friendly general response asking the student to rephrase or choose from suggested options.
- How does the system handle a student rapidly sending many queries in succession? → Rate limiting is enforced at the gateway level (F03). The agent layer respects these limits and returns appropriate error responses.
- What happens when the LLM provider is unavailable during agent execution? → The system returns a clear error message indicating the AI service is temporarily unavailable, without exposing internal details.
- How does the system handle a student who switches topics mid-conversation? → The routing agent re-evaluates intent on each new message and routes to the appropriate specialist.
- What happens when a student submits code that exceeds the sandbox execution limits during exercise grading? → The grading system handles the timeout/error gracefully and provides feedback accordingly.
- How does the system handle conversations that span multiple agent types in a single session? → Each message is independently routed; conversation history is maintained per session so agents have context.
- What happens when a student's progress data is incomplete (e.g., has exercises but no quizzes)? → The Progress Agent calculates mastery using available data and notes which components are missing.

## Requirements *(mandatory)*

### Functional Requirements

#### Triage & Routing (F07)

- **FR-001**: System MUST classify incoming student queries into one of five intent categories: concept-explanation, code-debug, code-review, exercise-generation, progress-summary
- **FR-002**: System MUST use deterministic code-based classification (not LLM-based) to ensure routing is testable and reproducible
- **FR-003**: System MUST assign a confidence score to each classification and route to the highest-confidence specialist agent
- **FR-004**: System MUST provide a fallback general response when no intent category meets a minimum confidence threshold
- **FR-005**: System MUST log all routing decisions including intent category, confidence score, and target agent for analytics
- **FR-006**: System MUST re-evaluate intent classification on each new message in a conversation (not just the first message)

#### Concepts Agent (F08)

- **FR-007**: System MUST generate explanations of Python concepts that include at least one runnable code example
- **FR-008**: System MUST adapt explanation complexity based on the student's current level (beginner, intermediate, advanced)
- **FR-009**: System MUST suggest 2-3 follow-up questions at the end of each concept explanation
- **FR-010**: System MUST support streaming responses so students see text appear progressively rather than waiting for the full response
- **FR-011**: System MUST include visual aids (ASCII diagrams, tables, or structured formatting) when they improve understanding of the concept

#### Code Review Agent (F09)

- **FR-012**: System MUST analyze submitted code for PEP 8 style compliance and report violations with suggested fixes
- **FR-013**: System MUST analyze submitted code for logic correctness and identify bugs that produce incorrect results
- **FR-014**: System MUST provide efficiency improvement suggestions when code is functionally correct but suboptimal
- **FR-015**: System MUST provide readability improvement suggestions (naming, structure, comments)
- **FR-016**: System MUST include positive reinforcement for aspects of the code that are well-written
- **FR-017**: System MUST run static analysis tools (PEP 8 checker) before LLM analysis to provide objective style feedback

#### Debug Agent (F10)

- **FR-018**: System MUST parse Python error messages (SyntaxError, TypeError, NameError, etc.) and identify the error type, line number, and root cause
- **FR-019**: System MUST implement a progressive 3-level hint system: (1) high-level error category, (2) specific location and cause, (3) concrete fix suggestion
- **FR-020**: System MUST NOT provide the full solution until the student has exhausted all hint levels or explicitly requests it
- **FR-021**: System MUST detect common error patterns (off-by-one, wrong operator, missing colon, indentation errors) and provide pattern-specific hints
- **FR-022**: System MUST recognize struggle signals ("I don't understand", "I'm stuck", repeated failed attempts) and adapt to simpler explanations
- **FR-023**: System MUST track hint level progression per debugging session to avoid repeating hints

#### Exercise Agent (F11)

- **FR-024**: System MUST generate coding exercises based on specified topic and difficulty level (beginner, intermediate, advanced)
- **FR-025**: System MUST generate test cases for each exercise that can automatically validate student solutions
- **FR-026**: System MUST auto-grade student submissions against test cases and return pass/fail per test
- **FR-027**: System MUST support partial credit scoring based on the proportion of test cases passed
- **FR-028**: System MUST provide constructive feedback for both correct and incorrect submissions
- **FR-029**: System MUST store generated exercises in the database for reuse and teacher review
- **FR-030**: System MUST execute student solutions in the isolated code sandbox (F05) during grading

#### Progress Agent (F12)

- **FR-031**: System MUST calculate mastery scores per topic using the formula: 40% exercise completion + 30% quiz scores + 20% code quality ratings + 10% consistency streak
- **FR-032**: System MUST map mastery scores to fixed levels: Beginner (0-40%), Learning (41-70%), Proficient (71-90%), Mastered (91-100%)
- **FR-033**: System MUST generate natural language progress summaries that explain the student's current standing
- **FR-034**: System MUST identify weak areas (topics with mastery below 50%) and recommend specific practice
- **FR-035**: System MUST track and report learning streaks (consecutive days with activity)
- **FR-036**: System MUST handle incomplete data gracefully (e.g., calculate with available components and note missing data)

#### Cross-Cutting Requirements

- **FR-037**: System MUST maintain conversation session state so agents have access to conversation history within a session
- **FR-038**: System MUST persist agent interactions (intent, agent used, timestamp, session ID) for analytics and debugging
- **FR-039**: System MUST enforce the same rate limits across all agents as defined by the gateway (F03)
- **FR-040**: System MUST stream all AI-generated responses to minimize perceived latency
- **FR-041**: System MUST NOT execute user-submitted code outside the isolated sandbox (F05)
- **FR-042**: System MUST use the LLM Provider abstraction (F06) for all model calls, enabling model swapping via environment variables
- **FR-043**: System MUST require authentication for all agent endpoints — no anonymous access
- **FR-044**: System MUST return structured error responses (not raw stack traces) when any agent fails

### Key Entities

- **Agent Session**: Represents an ongoing conversation between a student and the agent system. Contains session ID, user ID, conversation history, current routing state, and active agent. Sessions persist across messages within a tutoring interaction.

- **Routing Decision**: Represents a single intent classification event. Contains the student's message, classified intent category, confidence score, selected agent, and timestamp. Used for analytics and debugging routing accuracy.

- **Hint Progression**: Tracks a student's debugging session through the progressive hint system. Contains session ID, error context, current hint level (1-3), hints already provided, and whether the solution was revealed.

- **Exercise**: Represents a coding challenge generated for practice. Contains exercise ID, topic, difficulty level, description, starter code, test cases, creator (system or teacher), and creation timestamp.

- **Exercise Submission**: Represents a student's attempt at an exercise. Contains submission ID, exercise ID, student's code, test case results (pass/fail per test), score, and timestamp.

- **Mastery Record**: Represents a student's mastery score for a specific topic. Contains user ID, topic, mastery score (0-100), mastery level (Beginner/Learning/Proficient/Mastered), component breakdown (exercises, quizzes, code quality, streak), and last updated timestamp.

- **Progress Summary**: An aggregated view of a student's learning progress across all topics. Contains overall mastery, per-topic breakdown, weak areas, streak count, and personalized recommendations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students receive a correctly routed agent response within 5 seconds of sending a message (P95, excluding LLM response time)
- **SC-002**: Intent classification achieves 90% accuracy on a test set of 100 representative student queries
- **SC-003**: Concept explanations are rated as "helpful" or "very helpful" by 80% of students in feedback surveys
- **SC-004**: Debug Agent provides useful hints (student resolves the error without seeing the full solution) in 60% of debugging sessions
- **SC-005**: Code Review Agent identifies at least 85% of PEP 8 violations and logic bugs present in test code samples
- **SC-006**: Exercise grading accuracy matches expected results 100% of the time on predefined test cases
- **SC-007**: Progress Agent mastery calculations match manually computed scores for 100% of test users
- **SC-008**: AI responses begin streaming to the student within 1.5 seconds of the request (first token latency, P95)
- **SC-009**: System handles 50 concurrent student-agent sessions without degradation in routing accuracy or response quality
- **SC-010**: Fallback routing triggers for less than 5% of student queries (indicating good intent coverage)

## Assumptions

- The LLM Provider abstraction (F06) is fully implemented and operational
- The Python code sandbox (F05) is available for exercise grading and code execution
- The database schema (F02) includes tables for progress tracking, code submissions, and exercises
- Authentication (F01) is in place and user IDs are available in request context
- Students interact with agents through a chat interface (F15, built later) that handles message display and streaming
- The OpenAI Agents SDK is available and compatible with the project's Python version
- Rate limiting is enforced at the API gateway level (F03), not within individual agents
- The 8-module Python curriculum structure is defined and topics are known to the system

## Dependencies

- **F01: Authentication & Authorization** — Required for user identification and access control
- **F02: Database Schema & Migrations** — Required for storing sessions, exercises, submissions, and progress data
- **F03: API Gateway & Service Mesh** — Required for rate limiting and request routing
- **F05: Python Code Sandbox** — Required for exercise grading and code execution within agents
- **F06: LLM Provider Abstraction Layer** — Required for all AI model calls by agents

## Out of Scope

- Building the student-facing chat UI (handled by F15: Chat Interface)
- Building the student dashboard (handled by F13: Student Dashboard)
- Building the teacher dashboard or exercise generator UI (handled by F18, F21)
- Real-time notifications for struggle alerts (handled by F22: Real-time Notifications)
- Curriculum management interface (handled by F23: Curriculum Management)
- Multi-language support beyond Python
- Voice-based agent interactions
- Custom fine-tuned models — agents use the base model configured in F06
- Inter-agent communication beyond handoffs (agents do not call each other directly)
- Agent self-improvement or learning from feedback loops

## Security Considerations

- All agent endpoints require authenticated access with valid JWT tokens
- User-submitted code is NEVER executed directly — only through the isolated sandbox (F05)
- Agent prompts must not expose system instructions, API keys, or internal configuration to students
- Conversation history must not be accessible across different user sessions
- Routing analytics logs must not contain sensitive student data (only anonymized intent categories and confidence scores)
- Rate limiting prevents abuse of agent endpoints (enforced at gateway, F03)
- LLM responses must be validated before being sent to students (guardrails against harmful or inappropriate content)
- Exercise test cases must be stored securely and not exposed to students before submission

## Clarifications

None — all critical decisions have been made based on project context, existing specifications (F01-F06), and the OpenAI Agents SDK capabilities.

## Open Questions

None — all critical decisions have been resolved. The following architectural decisions were confirmed during research and discussion:

- **Single FastAPI service** for all agents (not microservices) — aligns with project anti-pattern of "no microservices until users demand them"
- **SQLAlchemySession** for conversation persistence — leverages existing Neon PostgreSQL (F02)
- **Deterministic code-based triage routing** — satisfies AGENTS.md requirement that "Triage routing MUST be deterministic and testable"
- **OpenAI Agents SDK** with handoffs for agent orchestration — provides production-ready primitives for multi-agent workflows
- **All 6 agents in one specification** — tightly coupled through shared dependencies and orchestration layer
