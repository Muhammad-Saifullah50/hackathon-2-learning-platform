# Data Model: User Management

**Feature**: 004-user-management
**Date**: 2026-03-15
**Phase**: 1 - Design & Contracts

## Overview

User Management feature leverages existing database models from F02 (Database Schema). No new tables or migrations required. This document describes the data structures, relationships, and validation rules for profile management operations.

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User (users table)                                          │
│ ─────────────────────────────────────────────────────────── │
│ PK  id: UUID                                                │
│ UQ  email: String(255)                                      │
│     password_hash: String(255)                              │
│ IDX role: String(20) [student|teacher|admin]                │
│     display_name: String(100)                               │
│     email_verified_at: DateTime (nullable)                  │
│     mfa_enabled: Boolean                                    │
│     mfa_secret: String(255) (nullable)                      │
│     permissions: JSONB (nullable)                           │
│     preferences: JSONB (default: {})                        │
│     created_at: DateTime                                    │
│     updated_at: DateTime                                    │
│     deleted_at: DateTime (nullable) [SoftDeleteMixin]       │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 1:1 CASCADE
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ UserProfile (user_profiles table)                           │
│ ─────────────────────────────────────────────────────────── │
│ PK  id: UUID                                                │
│ FK  user_id: UUID → users.id (CASCADE DELETE)               │
│ UQ  user_id (unique constraint)                             │
│     bio: String (nullable, max 500 chars)                   │
│     metadata: JSONB (default: {})                           │
│     created_at: DateTime                                    │
│     updated_at: DateTime                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Session (sessions table) - F01                              │
│ ─────────────────────────────────────────────────────────── │
│ PK  id: UUID                                                │
│ FK  user_id: UUID → users.id (CASCADE DELETE)               │
│     refresh_token_hash: String                              │
│     ip_address: String (nullable)                           │
│     user_agent: String (nullable)                           │
│     expires_at: DateTime                                    │
│     revoked_at: DateTime (nullable)                         │
│     created_at: DateTime                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Related Entities (CASCADE DELETE on User deletion)          │
│ ─────────────────────────────────────────────────────────── │
│ • UserStreak (user_streaks)                                 │
│ • UserExerciseProgress (user_exercise_progress)             │
│ • UserQuizAttempt (user_quiz_attempts)                      │
│ • UserModuleMastery (user_module_mastery)                   │
│ • CodeSubmission (code_submissions)                         │
└─────────────────────────────────────────────────────────────┘
```

## Core Entities

### User (Existing - F02)

**Table**: `users`
**Source**: [backend/src/models/user.py](backend/src/models/user.py:11-40)

**Fields**:
- `id` (UUID, PK): Unique user identifier
- `email` (String(255), UNIQUE, NOT NULL, INDEXED): User email address
- `password_hash` (String(255), NOT NULL): Bcrypt hashed password
- `role` (String(20), NOT NULL, INDEXED, DEFAULT='student'): User role [student|teacher|admin]
- `display_name` (String(100), NOT NULL): User's display name (fallback to email if empty)
- `email_verified_at` (DateTime, NULLABLE): Email verification timestamp
- `mfa_enabled` (Boolean, NOT NULL, DEFAULT=False): Multi-factor authentication flag
- `mfa_secret` (String(255), NULLABLE): TOTP secret for MFA
- `permissions` (JSONB, NULLABLE): Role-specific permissions
- `preferences` (JSONB, NOT NULL, DEFAULT='{}'): User preferences (learning_pace, difficulty_level, theme)
- `created_at` (DateTime, NOT NULL): Record creation timestamp
- `updated_at` (DateTime, NOT NULL): Record last update timestamp
- `deleted_at` (DateTime, NULLABLE): Soft delete timestamp (SoftDeleteMixin)

**Constraints**:
- CHECK: `role IN ('student', 'teacher', 'admin')`
- UNIQUE: `email`
- INDEX: `email`, `role`

**Relationships**:
- `profile` (1:1 → UserProfile, CASCADE DELETE)
- `streak` (1:1 → UserStreak, CASCADE DELETE)
- `exercise_progress` (1:N → UserExerciseProgress, CASCADE DELETE)
- `quiz_attempts` (1:N → UserQuizAttempt, CASCADE DELETE)
- `module_mastery` (1:N → UserModuleMastery, CASCADE DELETE)
- `code_submissions` (1:N → CodeSubmission, CASCADE DELETE)
- `sessions` (1:N → Session, CASCADE DELETE)

**Business Rules**:
- Display name defaults to email if empty/whitespace
- Soft delete anonymizes email: `deleted_{user_id}@anonymized.local`
- Hard delete cascades to all related entities

### UserProfile (Existing - F02)

**Table**: `user_profiles`
**Source**: [backend/src/models/user.py](backend/src/models/user.py:43-57)

**Fields**:
- `id` (UUID, PK): Unique profile identifier
- `user_id` (UUID, FK → users.id, UNIQUE, NOT NULL): Associated user
- `bio` (String, NULLABLE): User biography (max 500 chars, validated in service layer)
- `metadata` (JSONB, NOT NULL, DEFAULT='{}'): Additional profile metadata (avatar_url, timezone, etc.)
- `created_at` (DateTime, NOT NULL): Record creation timestamp
- `updated_at` (DateTime, NOT NULL): Record last update timestamp

**Constraints**:
- FOREIGN KEY: `user_id` → `users.id` (ON DELETE CASCADE)
- UNIQUE: `user_id`

**Relationships**:
- `user` (N:1 → User)

**Business Rules**:
- Bio max length: 500 characters (enforced in service layer)
- Profile is optional (can be NULL for users without extended profile)
- Automatically deleted when user is deleted (CASCADE)

### UserPreferences (Embedded in User.preferences JSONB)

**Storage**: `users.preferences` JSONB field
**Source**: Research Decision 2

**Schema**:
```json
{
  "learning_pace": "normal",        // enum: slow, normal, fast
  "difficulty_level": "beginner",   // enum: beginner, intermediate, advanced
  "theme": "dark"                   // enum: dark (light mode future)
}
```

**Validation Rules**:
- `learning_pace`: ENUM ['slow', 'normal', 'fast']
- `difficulty_level`: ENUM ['beginner', 'intermediate', 'advanced']
- `theme`: ENUM ['dark'] (MVP scope)
- All fields optional (defaults applied if missing)

**Defaults**:
- `learning_pace`: 'normal'
- `difficulty_level`: 'beginner'
- `theme`: 'dark'

**Business Rules**:
- Students prompted to set preferences on first login
- Preferences can be updated anytime
- Changes reflected in AI tutor interactions immediately

## State Transitions

### User Account Lifecycle

```
┌──────────────┐
│  REGISTERED  │ (email_verified_at = NULL, deleted_at = NULL)
└──────┬───────┘
       │ verify_email()
       ▼
┌──────────────┐
│   VERIFIED   │ (email_verified_at = timestamp, deleted_at = NULL)
└──────┬───────┘
       │ soft_delete()
       ▼
┌──────────────┐
│ SOFT_DELETED │ (deleted_at = timestamp, email anonymized)
└──────────────┘

       │ hard_delete() [THIS FEATURE]
       ▼
┌──────────────┐
│   DELETED    │ (record removed from database, CASCADE to all relations)
└──────────────┘
```

### Profile Update Flow

```
┌─────────────────┐
│ User Authenticated │
└────────┬──────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ PATCH /api/profile                      │
│ { display_name, bio }                   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Validate Input (Pydantic)               │
│ - display_name: max 100 chars           │
│ - bio: max 500 chars                    │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Apply Business Rules (Service Layer)    │
│ - If display_name empty → use email     │
│ - Trim whitespace                       │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Update Database (Repository)            │
│ - User.display_name                     │
│ - UserProfile.bio                       │
│ - User.updated_at = now()               │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Return Updated Profile                  │
└─────────────────────────────────────────┘
```

### Account Deletion Flow

```
┌─────────────────┐
│ User Authenticated │
└────────┬──────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ DELETE /api/account                     │
│ { password }                            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Verify Password (bcrypt)                │
│ - Return 401 if incorrect              │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Hard Delete User (Repository)           │
│ - DELETE FROM users WHERE id = ?        │
│ - CASCADE to all related tables:        │
│   • user_profiles                       │
│   • user_streaks                        │
│   • user_exercise_progress              │
│   • user_quiz_attempts                  │
│   • user_module_mastery                 │
│   • code_submissions                    │
│   • sessions                            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Return Success (204 No Content)         │
│ - Frontend redirects to login           │
└─────────────────────────────────────────┘
```

## Validation Rules

### Display Name
- **Type**: String
- **Min Length**: 1 character (after trim)
- **Max Length**: 100 characters
- **Pattern**: Any UTF-8 characters
- **Required**: Yes (fallback to email if empty)
- **Validation**: Pydantic + Service layer
- **Error Messages**:
  - Empty: "Display name cannot be empty" (service sets to email)
  - Too long: "Display name must be 100 characters or less"

### Bio
- **Type**: String
- **Min Length**: 0 characters (optional)
- **Max Length**: 500 characters
- **Pattern**: Any UTF-8 characters (including newlines)
- **Required**: No
- **Validation**: Pydantic + Service layer
- **Error Messages**:
  - Too long: "Bio must be 500 characters or less"

### Learning Pace
- **Type**: Enum (String)
- **Allowed Values**: ['slow', 'normal', 'fast']
- **Default**: 'normal'
- **Required**: No (default applied)
- **Validation**: Pydantic Enum
- **Error Messages**:
  - Invalid: "Learning pace must be one of: slow, normal, fast"

### Difficulty Level
- **Type**: Enum (String)
- **Allowed Values**: ['beginner', 'intermediate', 'advanced']
- **Default**: 'beginner'
- **Required**: No (default applied)
- **Validation**: Pydantic Enum
- **Error Messages**:
  - Invalid: "Difficulty level must be one of: beginner, intermediate, advanced"

### Password (for account deletion)
- **Type**: String
- **Min Length**: 8 characters
- **Required**: Yes
- **Validation**: bcrypt verification against stored hash
- **Error Messages**:
  - Incorrect: "Incorrect password"
  - Missing: "Password is required to delete account"

## Data Access Patterns

### Read Operations

**Get Current User Profile**:
```sql
SELECT u.*, p.bio, p.metadata
FROM users u
LEFT JOIN user_profiles p ON u.id = p.user_id
WHERE u.id = ? AND u.deleted_at IS NULL;
```
- **Performance**: < 40ms (indexed on u.id, p.user_id)
- **Frequency**: High (every profile page load)
- **Caching**: No (data changes frequently)

**Get User Preferences**:
```sql
SELECT preferences
FROM users
WHERE id = ? AND deleted_at IS NULL;
```
- **Performance**: < 20ms (indexed on id)
- **Frequency**: High (every AI interaction)
- **Caching**: Consider Redis for AI agents (future)

**Admin User List (Paginated)**:
```sql
SELECT id, email, display_name, role, created_at
FROM users
WHERE deleted_at IS NULL
  AND (role = ? OR ? IS NULL)  -- role filter
ORDER BY created_at DESC
LIMIT 50 OFFSET ?;
```
- **Performance**: < 2s for 50 users (indexed on role, created_at)
- **Frequency**: Low (admin only)
- **Caching**: Consider Redis for admin dashboard (future)

### Write Operations

**Update Profile**:
```sql
-- Update User.display_name
UPDATE users
SET display_name = ?, updated_at = NOW()
WHERE id = ? AND deleted_at IS NULL;

-- Update UserProfile.bio (if profile exists)
UPDATE user_profiles
SET bio = ?, updated_at = NOW()
WHERE user_id = ?;

-- Or create profile if not exists
INSERT INTO user_profiles (id, user_id, bio, metadata, created_at, updated_at)
VALUES (?, ?, ?, '{}', NOW(), NOW())
ON CONFLICT (user_id) DO UPDATE SET bio = EXCLUDED.bio, updated_at = NOW();
```
- **Performance**: < 40ms (indexed on id, user_id)
- **Frequency**: Low (occasional profile updates)
- **Transaction**: Yes (both updates in single transaction)

**Update Preferences**:
```sql
UPDATE users
SET preferences = ?, updated_at = NOW()
WHERE id = ? AND deleted_at IS NULL;
```
- **Performance**: < 20ms (indexed on id)
- **Frequency**: Low (occasional preference changes)
- **Transaction**: No (single update)

**Hard Delete Account**:
```sql
-- Single DELETE with CASCADE
DELETE FROM users WHERE id = ?;

-- Cascades to:
-- - user_profiles (ON DELETE CASCADE)
-- - user_streaks (ON DELETE CASCADE)
-- - user_exercise_progress (ON DELETE CASCADE)
-- - user_quiz_attempts (ON DELETE CASCADE)
-- - user_module_mastery (ON DELETE CASCADE)
-- - code_submissions (ON DELETE CASCADE)
-- - sessions (ON DELETE CASCADE)
```
- **Performance**: < 5s (CASCADE to ~7 tables)
- **Frequency**: Very low (rare account deletions)
- **Transaction**: Yes (all deletes in single transaction)

## Indexes

### Existing Indexes (F02)
- `users.id` (PRIMARY KEY, clustered)
- `users.email` (UNIQUE INDEX)
- `users.role` (INDEX for filtering)
- `user_profiles.id` (PRIMARY KEY)
- `user_profiles.user_id` (UNIQUE INDEX, FK)

### No New Indexes Required
All queries use existing indexes. Performance targets met without additional indexing.

## Data Migration

**No migrations required** - all tables and columns exist from F02.

### Existing Data Compatibility
- Users created by F01 have `display_name` set during registration
- Users created by F01 have `preferences = '{}'` (default)
- UserProfile may not exist for all users (LEFT JOIN handles this)

### Data Seeding (Optional)
For testing, seed users with various preference combinations:
```python
# Seed script (optional)
users = [
    {"email": "student1@test.com", "role": "student", "preferences": {"learning_pace": "slow", "difficulty_level": "beginner"}},
    {"email": "student2@test.com", "role": "student", "preferences": {"learning_pace": "fast", "difficulty_level": "advanced"}},
    {"email": "teacher1@test.com", "role": "teacher", "preferences": {}},
    {"email": "admin1@test.com", "role": "admin", "preferences": {}},
]
```

## Security Considerations

### Authorization
- Users can only access their own profile (user_id from JWT token)
- Admin endpoints require `role = 'admin'` (enforced by `require_role` dependency)
- Account deletion requires password confirmation (prevents unauthorized deletion)

### Data Privacy
- Hard deletion removes all PII permanently (GDPR compliant)
- No data retention after deletion
- Soft delete (existing) anonymizes email but retains records (not used for account deletion)

### Input Sanitization
- All inputs validated by Pydantic (type, length, enum)
- SQL injection prevented by SQLAlchemy ORM (parameterized queries)
- XSS prevention: Frontend escapes user-generated content (bio, display_name)

## Performance Targets

| Operation | Target | Actual (Expected) |
|-----------|--------|-------------------|
| Get profile | < 150ms p95 | ~40ms (single JOIN) |
| Update profile | < 150ms p95 | ~40ms (2 UPDATEs) |
| Update preferences | < 150ms p95 | ~20ms (1 UPDATE) |
| Delete account | < 5s | ~2s (CASCADE to 7 tables) |
| Admin user list | < 2s | ~500ms (50 users, indexed) |

All targets met with existing schema and indexes.

## References

- [User Model](backend/src/models/user.py:11-40)
- [UserProfile Model](backend/src/models/user.py:43-57)
- [UserRepository](backend/src/repositories/user_repository.py:10-67)
- [UserProfileRepository](backend/src/repositories/user_repository.py:69-97)
- [Research Document](./research.md)
- [Feature Spec](./spec.md)
