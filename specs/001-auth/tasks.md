# Tasks: Authentication & Authorization

**Input**: Design documents from `/specs/001-auth/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per TDD approach specified in constitution (strict TDD for auth flows).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure with src/auth/, tests/, alembic/ directories
- [X] T002 [P] Initialize Python virtual environment and install dependencies from requirements.txt
- [X] T003 [P] Initialize Next.js frontend project with TypeScript and Better Auth dependencies
- [X] T004 [P] Configure black, isort, and pre-commit hooks for backend
- [X] T005 [P] Configure prettier and eslint for frontend
- [X] T006 Generate RSA key pair for JWT signing (private/public keys in backend/keys/)
- [X] T007 [P] Create backend/.env template with all required environment variables
- [X] T008 [P] Create frontend/.env.local template with API URL and Better Auth config
- [X] T009 Setup Mailhog Docker container for local email testing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 Create database configuration in backend/src/database.py with SQLAlchemy engine and session factory
- [X] T011 Create settings configuration in backend/src/config.py with Pydantic BaseSettings
- [X] T012 Create Alembic migration 001_create_auth_tables.py with all 5 tables (users, sessions, password_reset_tokens, email_verification_tokens, rate_limit_counters)
- [X] T013 Run Alembic migration to create database schema
- [X] T014 [P] Create base Pydantic schemas in backend/src/auth/schemas.py for request/response models
- [X] T015 [P] Implement JWT utilities in backend/src/auth/jwt.py (encode, decode, RS256 key loading)
- [X] T016 [P] Implement password utilities in backend/src/auth/password.py (bcrypt hashing, HaveIBeenPwned check)
- [X] T017 [P] Implement rate limiting logic in backend/src/auth/rate_limit.py
- [X] T018 Create FastAPI dependency get_current_user in backend/src/auth/dependencies.py
- [X] T019 [P] Create pytest fixtures in backend/tests/conftest.py (test DB, test client, test user factory)
- [X] T020 Setup FastAPI app with CORS middleware in backend/src/main.py
- [X] T021 [P] Configure Better Auth client in frontend/src/lib/auth.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - New User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts with email, password, and role validation

**Independent Test**: Submit registration form with valid credentials and verify account creation in database. Delivers a working registration flow that can be demonstrated standalone.

### Tests for User Story 1 (TDD - Write First, Ensure FAIL)

- [X] T022 [P] [US1] Contract test for POST /api/auth/register in backend/tests/integration/test_auth_routes.py::test_register_user_success
- [X] T023 [P] [US1] Contract test for password breach rejection in backend/tests/integration/test_auth_routes.py::test_register_breached_password
- [X] T024 [P] [US1] Contract test for duplicate email rejection in backend/tests/integration/test_auth_routes.py::test_register_duplicate_email
- [X] T025 [P] [US1] Unit test for password hashing in backend/tests/unit/test_password.py::test_hash_password
- [X] T026 [P] [US1] Unit test for HaveIBeenPwned check in backend/tests/unit/test_password.py::test_check_password_breach

### Implementation for User Story 1

- [X] T027 [P] [US1] Create User model in backend/src/auth/models.py with all fields from data-model.md
- [X] T028 [P] [US1] Create EmailVerificationToken model in backend/src/auth/models.py
- [X] T029 [US1] Create UserRepository in backend/src/auth/repository.py with create_user, get_by_email methods
- [X] T030 [US1] Create EmailVerificationTokenRepository in backend/src/auth/repository.py with create_token, get_by_token_hash methods
- [X] T031 [US1] Implement AuthService.register_user in backend/src/auth/service.py (validation, breach check, user creation, email sending)
- [X] T032 [US1] Implement POST /api/auth/register endpoint in backend/src/auth/routes.py
- [X] T033 [US1] Add email sending logic for verification emails in backend/src/auth/service.py
- [X] T034 [P] [US1] Create RegisterForm component in frontend/components/auth/RegisterForm.tsx
- [X] T035 [P] [US1] Create registration page in frontend/app/auth/register/page.tsx
- [X] T036 [US1] Integrate RegisterForm with backend API endpoint

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - User Login with JWT Tokens (Priority: P1) 🎯 MVP

**Goal**: Enable registered users to log in and receive JWT tokens for authenticated access

**Independent Test**: Log in with valid credentials and verify JWT tokens are issued and accepted by protected endpoints. Delivers working authentication that can be demonstrated standalone.

### Tests for User Story 2 (TDD - Write First, Ensure FAIL)

- [X] T037 [P] [US2] Contract test for POST /api/auth/login in backend/tests/integration/test_auth_routes.py::test_login_success
- [X] T038 [P] [US2] Contract test for invalid credentials in backend/tests/integration/test_auth_routes.py::test_login_invalid_credentials
- [X] T039 [P] [US2] Contract test for rate limiting in backend/tests/integration/test_auth_routes.py::test_login_rate_limit
- [X] T040 [P] [US2] Contract test for POST /api/auth/refresh in backend/tests/integration/test_auth_routes.py::test_refresh_token_success
- [X] T041 [P] [US2] Contract test for token rotation in backend/tests/integration/test_auth_routes.py::test_refresh_token_rotation
- [X] T042 [P] [US2] Unit test for JWT encoding in backend/tests/unit/test_jwt.py::test_encode_jwt
- [X] T043 [P] [US2] Unit test for JWT decoding in backend/tests/unit/test_jwt.py::test_decode_jwt

### Implementation for User Story 2

- [X] T044 [P] [US2] Create Session model in backend/src/auth/models.py with all fields from data-model.md
- [X] T045 [P] [US2] Create RateLimitCounter model in backend/src/auth/models.py
- [X] T046 [US2] Create SessionRepository in backend/src/auth/repository.py with create_session, get_by_refresh_token_hash, revoke_session methods
- [X] T047 [US2] Create RateLimitRepository in backend/src/auth/repository.py with increment_counter, check_lockout, reset_counter methods
- [X] T048 [US2] Implement AuthService.login in backend/src/auth/service.py (credential validation, rate limiting, JWT issuance, session creation)
- [X] T049 [US2] Implement AuthService.refresh_token in backend/src/auth/service.py (token validation, rotation, session update)
- [X] T050 [US2] Implement POST /api/auth/login endpoint in backend/src/auth/routes.py
- [X] T051 [US2] Implement POST /api/auth/refresh endpoint in backend/src/auth/routes.py
- [X] T052 [P] [US2] Create LoginForm component in frontend/components/auth/LoginForm.tsx
- [X] T053 [P] [US2] Create login page in frontend/app/auth/login/page.tsx
- [X] T054 [US2] Integrate LoginForm with backend API endpoint
- [X] T055 [US2] Implement token refresh logic in Better Auth configuration in frontend/lib/auth.ts
- [X] T056 [P] [US2] Create useAuth hook in frontend/hooks/useAuth.tsx for auth state management

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 7 - Current User Profile Retrieval (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to retrieve their profile information for UI display

**Independent Test**: Call /api/auth/me with valid token and verify correct user data is returned. Delivers user profile retrieval that can be demonstrated standalone.

### Tests for User Story 7 (TDD - Write First, Ensure FAIL)

- [X] T057 [P] [US7] Contract test for GET /api/auth/me in backend/tests/integration/test_auth_routes.py::test_get_current_user_success
- [X] T058 [P] [US7] Contract test for expired token in backend/tests/integration/test_auth_routes.py::test_get_current_user_expired_token
- [X] T059 [P] [US7] Contract test for invalid token in backend/tests/integration/test_auth_routes.py::test_get_current_user_invalid_token

### Implementation for User Story 7

- [X] T060 [US7] Implement GET /api/auth/me endpoint in backend/src/auth/routes.py using get_current_user dependency
- [X] T061 [US7] Update useAuth hook to fetch user profile from /api/auth/me in frontend/hooks/useAuth.tsx
- [X] T062 [P] [US7] Create ProtectedRoute component in frontend/components/ProtectedRoute.tsx
- [X] T063 [US7] Test profile retrieval in authenticated pages

**Checkpoint**: MVP core (US1, US2, US7) is now complete and functional

---

## Phase 6: User Story 5 - Role-Based Access Control (Priority: P1) 🎯 MVP

**Goal**: Enforce role-based permissions to protect sensitive endpoints and data

**Independent Test**: Attempt to access role-restricted endpoints with different user tokens and verify 403 Forbidden responses. Delivers working authorization that can be demonstrated standalone.

### Tests for User Story 5 (TDD - Write First, Ensure FAIL)

- [X] T064 [P] [US5] Contract test for student accessing teacher endpoint in backend/tests/integration/test_auth_routes.py::test_rbac_student_forbidden
- [X] T065 [P] [US5] Contract test for admin accessing all endpoints in backend/tests/integration/test_auth_routes.py::test_rbac_admin_allowed
- [X] T066 [P] [US5] Contract test for teacher accessing own class data in backend/tests/integration/test_auth_routes.py::test_rbac_teacher_allowed

### Implementation for User Story 5

- [X] T067 [US5] Create require_role dependency in backend/src/auth/dependencies.py (checks JWT role claim)
- [X] T068 [US5] Create require_roles dependency in backend/src/auth/dependencies.py (checks multiple roles)
- [X] T069 [US5] Add role validation to protected endpoints in backend/src/auth/routes.py
- [X] T070 [US5] Test RBAC enforcement across all protected endpoints

**Checkpoint**: MVP security (RBAC) is now complete

---

## Phase 7: User Story 4 - Email Verification (Priority: P2)

**Goal**: Require teachers and admins to verify email before login, optional for students

**Independent Test**: Register as teacher/admin, receive verification email, click link, and confirm email_verified_at timestamp is set. Delivers email verification flow that can be demonstrated standalone.

### Tests for User Story 4 (TDD - Write First, Ensure FAIL)

- [X] T071 [P] [US4] Contract test for POST /api/auth/email-verification/verify in backend/tests/integration/test_auth_routes.py::test_verify_email_success
- [X] T072 [P] [US4] Contract test for expired token in backend/tests/integration/test_auth_routes.py::test_verify_email_expired_token
- [X] T073 [P] [US4] Contract test for POST /api/auth/email-verification/send in backend/tests/integration/test_auth_routes.py::test_resend_verification_email

### Implementation for User Story 4

- [X] T074 [US4] Implement AuthService.verify_email in backend/src/auth/service.py (token validation, user update)
- [X] T075 [US4] Implement AuthService.resend_verification_email in backend/src/auth/service.py
- [X] T076 [US4] Implement POST /api/auth/email-verification/verify endpoint in backend/src/auth/routes.py
- [X] T077 [US4] Implement POST /api/auth/email-verification/send endpoint in backend/src/auth/routes.py
- [X] T078 [US4] Add email verification check to login flow in backend/src/auth/service.py (block teacher/admin if unverified)
- [X] T079 [P] [US4] Create email verification page in frontend/src/app/auth/verify-email/page.tsx
- [X] T080 [P] [US4] Create EmailVerificationBanner component in frontend/src/components/auth/EmailVerificationBanner.tsx
- [X] T081 [US4] Integrate verification banner for unverified students in frontend

**Checkpoint**: Email verification backend is now complete (frontend deferred)

---

## Phase 8: User Story 3 - Password Reset via Magic Link (Priority: P2)

**Goal**: Enable users to reset forgotten passwords securely via email magic link

**Independent Test**: Request password reset, click magic link, and set new password. Delivers self-service password recovery that can be demonstrated standalone.

### Tests for User Story 3 (TDD - Write First, Ensure FAIL)

- [X] T082 [P] [US3] Contract test for POST /api/auth/password-reset/request in backend/tests/integration/test_auth_routes.py::test_request_password_reset
- [X] T083 [P] [US3] Contract test for POST /api/auth/password-reset/confirm in backend/tests/integration/test_auth_routes.py::test_confirm_password_reset_success
- [X] T084 [P] [US3] Contract test for expired token in backend/tests/integration/test_auth_routes.py::test_confirm_password_reset_expired_token

### Implementation for User Story 3

- [X] T085 [P] [US3] Create PasswordResetToken model in backend/src/auth/models.py
- [X] T086 [US3] Create PasswordResetTokenRepository in backend/src/auth/repository.py with create_token, get_by_token_hash, mark_used methods
- [X] T087 [US3] Implement AuthService.request_password_reset in backend/src/auth/service.py (token generation, email sending)
- [X] T088 [US3] Implement AuthService.confirm_password_reset in backend/src/auth/service.py (token validation, password update)
- [X] T089 [US3] Implement POST /api/auth/password-reset/request endpoint in backend/src/auth/routes.py
- [X] T090 [US3] Implement POST /api/auth/password-reset/confirm endpoint in backend/src/auth/routes.py
- [X] T091 [P] [US3] Create PasswordResetForm component in frontend/src/components/auth/PasswordResetForm.tsx
- [X] T092 [P] [US3] Create password reset request page in frontend/src/app/auth/reset-password/page.tsx
- [X] T093 [US3] Integrate password reset flow with backend API

**Checkpoint**: Password reset is now complete

---

## Phase 9: User Story 6 - Session Management & Logout (Priority: P2)

**Goal**: Enable users to securely log out from current device or all devices

**Independent Test**: Log in, call logout endpoint, and verify token is rejected on subsequent requests. Delivers session revocation that can be demonstrated standalone.

### Tests for User Story 6 (TDD - Write First, Ensure FAIL)

- [X] T094 [P] [US6] Contract test for POST /api/auth/logout in backend/tests/integration/test_auth_routes.py::test_logout_success
- [X] T095 [P] [US6] Contract test for POST /api/auth/logout-all in backend/tests/integration/test_auth_routes.py::test_logout_all_success
- [X] T096 [P] [US6] Contract test for revoked token rejection in backend/tests/integration/test_auth_routes.py::test_revoked_token_rejected

### Implementation for User Story 6

- [X] T097 [US6] Implement AuthService.logout in backend/src/auth/service.py (mark session as revoked)
- [X] T098 [US6] Implement AuthService.logout_all in backend/src/auth/service.py (revoke all user sessions)
- [X] T099 [US6] Implement POST /api/auth/logout endpoint in backend/src/auth/routes.py
- [X] T100 [US6] Implement POST /api/auth/logout-all endpoint in backend/src/auth/routes.py
- [X] T101 [US6] Add revoked session check to get_current_user dependency in backend/src/auth/dependencies.py
- [X] T102 [US6] Implement logout functionality in frontend useAuth hook in frontend/src/hooks/useAuth.ts
- [X] T103 [US6] Add logout button to frontend navigation/header

**Checkpoint**: Session management is now complete

---

## Phase 10: Kong Integration & Public Key Endpoint

**Purpose**: Enable Kong API Gateway to validate JWT tokens

- [X] T104 Implement GET /api/auth/public-key endpoint in backend/src/auth/routes.py (returns RS256 public key)
- [X] T105 Test public key endpoint returns valid PEM format
- [X] T106 Document Kong JWT plugin configuration in specs/001-auth/contracts/kong-config.md
- [X] T107 Coordinate with F03 team on public key distribution mechanism

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T108 [P] Add comprehensive logging for all auth operations in backend/src/auth/service.py
- [X] T109 [P] Create session cleanup script in backend/scripts/cleanup_sessions.py (daily job)
- [X] T110 [P] Add security headers middleware in backend/src/main.py
- [ ] T111 [P] Frontend E2E tests for registration flow in frontend/tests/e2e/auth-registration.spec.ts
- [ ] T112 [P] Frontend E2E tests for login flow in frontend/tests/e2e/auth-login.spec.ts
- [X] T113 Run quickstart.md validation (all setup steps work)
- [X] T114 Update API documentation with all endpoints
- [X] T115 Security audit: verify no secrets in logs, proper error messages
- [ ] T116 Performance testing: verify 1000 concurrent auth requests handled
- [ ] T117 [P] Add rate limiting metrics and monitoring

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (Registration) → Can start after Foundational
  - US2 (Login) → Can start after Foundational (independent of US1 but typically follows)
  - US7 (Profile) → Depends on US2 (needs authentication)
  - US5 (RBAC) → Depends on US2 (needs JWT tokens)
  - US4 (Email Verification) → Can start after US1 (extends registration)
  - US3 (Password Reset) → Can start after Foundational (independent)
  - US6 (Logout) → Depends on US2 (needs sessions)
- **Kong Integration (Phase 10)**: Can start after US2 (needs JWT implementation)
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent but typically follows US1
- **User Story 7 (P1)**: Depends on US2 (needs authentication mechanism)
- **User Story 5 (P1)**: Depends on US2 (needs JWT tokens with role claims)
- **User Story 4 (P2)**: Can start after US1 (extends registration flow)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent
- **User Story 6 (P2)**: Depends on US2 (needs session management)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Models before repositories
- Repositories before services
- Services before routes/endpoints
- Backend implementation before frontend integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes:
  - US1 and US3 can start in parallel (independent)
  - After US1 completes: US2 and US4 can start in parallel
  - After US2 completes: US5, US6, US7 can start in parallel
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Frontend and backend tasks marked [P] can run in parallel

---

## Parallel Example: User Story 2 (Login)

```bash
# Launch all tests for User Story 2 together (TDD - write first):
Task T037: "Contract test for POST /api/auth/login"
Task T038: "Contract test for invalid credentials"
Task T039: "Contract test for rate limiting"
Task T040: "Contract test for POST /api/auth/refresh"
Task T041: "Contract test for token rotation"
Task T042: "Unit test for JWT encoding"
Task T043: "Unit test for JWT decoding"

# After tests fail, launch all models together:
Task T044: "Create Session model"
Task T045: "Create RateLimitCounter model"

# Launch frontend components in parallel with backend routes:
Task T052: "Create LoginForm component"
Task T053: "Create login page"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 7, 5 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Registration)
4. Complete Phase 4: User Story 2 (Login)
5. Complete Phase 5: User Story 7 (Profile)
6. Complete Phase 6: User Story 5 (RBAC)
7. **STOP and VALIDATE**: Test MVP independently (registration → login → profile → RBAC)
8. Deploy/demo if ready

**MVP Scope**: 117 tasks total, MVP = Tasks T001-T070 (70 tasks)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T021)
2. Add User Story 1 → Test independently → Deploy/Demo (T022-T036)
3. Add User Story 2 → Test independently → Deploy/Demo (T037-T056)
4. Add User Story 7 → Test independently → Deploy/Demo (T057-T063)
5. Add User Story 5 → Test independently → Deploy/Demo (T064-T070)
6. Add User Story 4 → Test independently → Deploy/Demo (T071-T081)
7. Add User Story 3 → Test independently → Deploy/Demo (T082-T093)
8. Add User Story 6 → Test independently → Deploy/Demo (T094-T103)
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T021)
2. Once Foundational is done:
   - Developer A: User Story 1 (T022-T036)
   - Developer B: User Story 3 (T082-T093) - independent
3. After US1 completes:
   - Developer A: User Story 2 (T037-T056)
   - Developer C: User Story 4 (T071-T081) - extends US1
4. After US2 completes:
   - Developer A: User Story 7 (T057-T063)
   - Developer B: User Story 5 (T064-T070)
   - Developer C: User Story 6 (T094-T103)
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD approach: Write tests first, ensure they FAIL, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP = US1 + US2 + US7 + US5 (core auth + RBAC)
- P2 stories (US3, US4, US6) can be added incrementally after MVP
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
