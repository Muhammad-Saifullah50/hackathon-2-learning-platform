# Tasks: User Management

**Input**: Design documents from `/specs/004-user-management/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not explicitly requested in the feature specification, so test tasks are excluded.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify existing database models (User, UserProfile) from F02 in backend/src/models/user.py
- [x] T002 Verify existing repositories (UserRepository, UserProfileRepository) from F02 in backend/src/repositories/user_repository.py
- [x] T003 Verify existing auth dependencies (get_current_user, require_role) from F01 in backend/src/auth/dependencies.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Pydantic enums (LearningPace, DifficultyLevel) in backend/src/schemas/user_profile.py
- [x] T005 [P] Create ProfileUpdateRequest schema in backend/src/schemas/user_profile.py
- [x] T006 [P] Create PreferencesUpdateRequest schema in backend/src/schemas/user_profile.py
- [x] T007 [P] Create AccountDeleteRequest schema in backend/src/schemas/user_profile.py
- [x] T008 [P] Create ProfileResponse schema in backend/src/schemas/user_profile.py
- [x] T009 Create UserProfileService class with __init__ method in backend/src/services/user_profile_service.py
- [x] T010 Create TypeScript API client types (ProfileResponse, LearningPace, DifficultyLevel) in frontend/src/lib/api/profile.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View and Update Personal Profile (Priority: P1) 🎯 MVP

**Goal**: Enable users to view and update their display name and bio

**Independent Test**: Authenticate as any user, navigate to profile page, view current information, update display name/bio, verify changes persist after page refresh

### Implementation for User Story 1

- [x] T011 [P] [US1] Implement get_profile method in UserProfileService in backend/src/services/user_profile_service.py
- [x] T012 [P] [US1] Implement update_profile method with display_name fallback logic in backend/src/services/user_profile_service.py
- [x] T013 [US1] Implement GET /api/profile endpoint in backend/src/api/routes/profile.py
- [x] T014 [US1] Implement PATCH /api/profile endpoint in backend/src/api/routes/profile.py
- [x] T015 [US1] Register profile router in backend/src/main.py
- [x] T016 [P] [US1] Implement getProfile API client function in frontend/src/lib/api/profile.ts
- [x] T017 [P] [US1] Implement updateProfile API client function in frontend/src/lib/api/profile.ts
- [x] T018 [US1] Create ProfileForm component with validation in frontend/src/components/ProfileForm.tsx
- [x] T019 [US1] Create profile page with ProfileForm in frontend/src/app/settings/page.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Configure Learning Preferences (Priority: P1)

**Goal**: Enable students to set learning pace and difficulty level for personalized tutoring

**Independent Test**: Authenticate as a student, set learning pace and difficulty level, save preferences, verify AI agents adapt responses accordingly

### Implementation for User Story 2

- [x] T020 [US2] Implement update_preferences method in UserProfileService in backend/src/services/user_profile_service.py
- [x] T021 [US2] Implement PATCH /api/preferences endpoint in backend/src/api/routes/profile.py
- [x] T022 [US2] Implement updatePreferences API client function in frontend/src/lib/api/profile.ts
- [x] T023 [US2] Create PreferencesForm component with enum dropdowns in frontend/src/components/PreferencesForm.tsx
- [x] T024 [US2] Create preferences page with PreferencesForm in frontend/src/app/settings/page.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Delete Account (Priority: P2)

**Goal**: Enable users to permanently delete their account and all data (GDPR compliance)

**Independent Test**: Create test account, add profile data and learning progress, initiate account deletion, confirm deletion, verify all user data is permanently removed from database

### Implementation for User Story 3

- [x] T025 [US3] Implement hard_delete_account method with password verification and CASCADE delete in backend/src/services/user_profile_service.py
- [x] T026 [US3] Implement DELETE /api/account endpoint with password confirmation in backend/src/api/routes/profile.py
- [x] T027 [US3] Implement deleteAccount API client function in frontend/src/lib/api/profile.ts
- [x] T028 [US3] Create AccountDeleteDialog component with password input in frontend/src/components/AccountDeleteDialog.tsx
- [x] T029 [US3] Integrate AccountDeleteDialog into profile page in frontend/src/app/settings/page.tsx

**Checkpoint**: All user stories 1-3 should now be independently functional

---

## Phase 6: User Story 4 - Admin User Management (Priority: P3)

**Goal**: Enable admins to view all users with pagination and role filtering

**Independent Test**: Authenticate as admin user, view user list, apply role filters, verify pagination works correctly with large user datasets

### Implementation for User Story 4

- [x] T030 [US4] Create admin router file in backend/src/api/routes/admin.py
- [x] T031 [US4] Implement GET /api/admin/users endpoint with pagination and role filtering in backend/src/api/routes/admin.py
- [x] T032 [US4] Register admin router in backend/src/main.py
- [x] T033 [P] [US4] Create AdminUserListResponse type in frontend/src/lib/api/profile.ts
- [x] T034 [P] [US4] Implement listUsers API client function in frontend/src/lib/api/profile.ts
- [x] T035 [US4] Create UserList component with pagination and role filter in frontend/src/components/UserList.tsx
- [x] T036 [US4] Create admin users page with UserList in frontend/src/app/users/page.tsx

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T037 [P] Add error handling and user feedback messages across all profile forms
- [x] T038 [P] Add loading states to all API calls in frontend components
- [x] T039 [P] Verify display_name fallback logic works correctly (empty string → email)
- [x] T040 [P] Verify CASCADE delete removes all related data (profile, progress, sessions)
- [x] T041 Validate all endpoints match OpenAPI contracts in contracts/profile.openapi.yaml and contracts/admin.openapi.yaml
- [x] T042 Run quickstart.md validation to ensure implementation guide is accurate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1 (different endpoints/forms)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2 (different endpoint)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3 (admin-only feature)

### Within Each User Story

- Backend service methods before API routes
- API routes before frontend API client
- Frontend API client before components
- Components before pages
- Story complete before moving to next priority

### Parallel Opportunities

- All Foundational schema tasks (T005-T008) can run in parallel
- Within US1: T011 and T012 can run in parallel (different methods), T016 and T017 can run in parallel
- Within US4: T033 and T034 can run in parallel
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All Polish tasks (T037-T040) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch service methods together:
Task: "Implement get_profile method in UserProfileService"
Task: "Implement update_profile method with display_name fallback logic"

# Launch API client functions together:
Task: "Implement getProfile API client function"
Task: "Implement updateProfile API client function"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View/Update Profile)
4. Complete Phase 4: User Story 2 (Learning Preferences)
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Profile management!)
3. Add User Story 2 → Test independently → Deploy/Demo (Preferences!)
4. Add User Story 3 → Test independently → Deploy/Demo (Account deletion!)
5. Add User Story 4 → Test independently → Deploy/Demo (Admin management!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Profile)
   - Developer B: User Story 2 (Preferences)
   - Developer C: User Story 3 (Account Deletion)
   - Developer D: User Story 4 (Admin Management)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All database models and repositories already exist from F02 (no migrations needed)
- All auth dependencies already exist from F01 (JWT, role checks)
- Display name fallback (empty → email) handled in service layer
- Hard deletion uses SQLAlchemy CASCADE (configured in F02 models)
- Admin endpoints require admin role via require_role(['admin']) dependency
