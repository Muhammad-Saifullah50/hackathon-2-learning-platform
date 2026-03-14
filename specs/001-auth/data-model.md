# Data Model: Authentication & Authorization

**Feature**: 001-auth | **Date**: 2026-03-14 | **Phase**: 1 (Design)

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                           users                              │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ email (VARCHAR(255), UNIQUE, NOT NULL)                      │
│ password_hash (VARCHAR(255), NOT NULL)                      │
│ role (ENUM: student, teacher, admin, NOT NULL)             │
│ display_name (VARCHAR(100), NOT NULL)                       │
│ email_verified_at (TIMESTAMP, NULL)                         │
│ mfa_enabled (BOOLEAN, DEFAULT FALSE)                        │
│ mfa_secret (VARCHAR(255), NULL)                             │
│ permissions (JSONB, NULL)                                   │
│ created_at (TIMESTAMP, NOT NULL, DEFAULT NOW())             │
│ updated_at (TIMESTAMP, NOT NULL, DEFAULT NOW())             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         sessions                             │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ user_id (UUID, FK → users.id, NOT NULL)                    │
│ refresh_token_hash (VARCHAR(255), UNIQUE, NOT NULL)         │
│ device_info (VARCHAR(500), NULL)                            │
│ user_agent (VARCHAR(500), NULL)                             │
│ ip_address (VARCHAR(45), NULL)                              │
│ created_at (TIMESTAMP, NOT NULL, DEFAULT NOW())             │
│ expires_at (TIMESTAMP, NOT NULL)                            │
│ revoked_at (TIMESTAMP, NULL)                                │
│ last_used_at (TIMESTAMP, NULL)                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  password_reset_tokens                       │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ user_id (UUID, FK → users.id, NOT NULL)                    │
│ token_hash (VARCHAR(255), UNIQUE, NOT NULL)                 │
│ created_at (TIMESTAMP, NOT NULL, DEFAULT NOW())             │
│ expires_at (TIMESTAMP, NOT NULL)                            │
│ used_at (TIMESTAMP, NULL)                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│               email_verification_tokens                      │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ user_id (UUID, FK → users.id, NOT NULL)                    │
│ token_hash (VARCHAR(255), UNIQUE, NOT NULL)                 │
│ created_at (TIMESTAMP, NOT NULL, DEFAULT NOW())             │
│ expires_at (TIMESTAMP, NOT NULL)                            │
│ used_at (TIMESTAMP, NULL)                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   rate_limit_counters                        │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ identifier (VARCHAR(255), UNIQUE, NOT NULL)                 │
│ identifier_type (ENUM: ip, email, NOT NULL)                 │
│ attempt_count (INTEGER, NOT NULL, DEFAULT 0)                │
│ lockout_until (TIMESTAMP, NULL)                             │
│ last_attempt_at (TIMESTAMP, NOT NULL, DEFAULT NOW())        │
│ created_at (TIMESTAMP, NOT NULL, DEFAULT NOW())             │
└─────────────────────────────────────────────────────────────┘
```

---

## Entity Definitions

### 1. User

**Purpose**: Represents a platform user (student, teacher, or admin) with authentication credentials and profile information.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (used for login) |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt hash of user's password (never store plaintext) |
| `role` | ENUM | NOT NULL | User role: `student`, `teacher`, or `admin` |
| `display_name` | VARCHAR(100) | NOT NULL | User's display name (shown in UI) |
| `email_verified_at` | TIMESTAMP | NULL | Timestamp when email was verified (NULL = unverified) |
| `mfa_enabled` | BOOLEAN | DEFAULT FALSE | Whether MFA is enabled (future feature, unused in MVP) |
| `mfa_secret` | VARCHAR(255) | NULL | TOTP secret for MFA (future feature, unused in MVP) |
| `permissions` | JSONB | NULL | Custom permissions beyond role (future feature, unused in MVP) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp (auto-updated on change) |

**Indexes**:
- `idx_users_email` on `email` (for login lookups)
- `idx_users_role` on `role` (for role-based queries)
- `idx_users_created_at` on `created_at` (for analytics)

**Validation Rules**:
- Email must match regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Password must be at least 8 characters with at least one non-alphanumeric character
- Password must not appear in HaveIBeenPwned breach database
- Role must be one of: `student`, `teacher`, `admin`
- Display name must be 1-100 characters

**State Transitions**:
1. **Created** → `email_verified_at = NULL`
2. **Email Verified** → `email_verified_at = <timestamp>`
3. **MFA Enabled** (future) → `mfa_enabled = TRUE`, `mfa_secret = <secret>`

---

### 2. Session

**Purpose**: Represents an active user session with refresh token for JWT renewal.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique session identifier |
| `user_id` | UUID | FOREIGN KEY → users.id, NOT NULL | User who owns this session |
| `refresh_token_hash` | VARCHAR(255) | UNIQUE, NOT NULL | SHA-256 hash of refresh token (never store plaintext) |
| `device_info` | VARCHAR(500) | NULL | Device information (e.g., "iPhone 13 Pro") |
| `user_agent` | VARCHAR(500) | NULL | Browser user agent string |
| `ip_address` | VARCHAR(45) | NULL | IP address of session creation (IPv4 or IPv6) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Session creation timestamp |
| `expires_at` | TIMESTAMP | NOT NULL | Session expiry timestamp (7 days from creation) |
| `revoked_at` | TIMESTAMP | NULL | Timestamp when session was revoked (NULL = active) |
| `last_used_at` | TIMESTAMP | NULL | Timestamp of last token refresh |

**Indexes**:
- `idx_sessions_user_id` on `user_id` (for user session lookups)
- `idx_sessions_refresh_token_hash` on `refresh_token_hash` (for token validation)
- `idx_sessions_expires_at` on `expires_at` (for cleanup job)

**Validation Rules**:
- `expires_at` must be exactly 7 days after `created_at`
- `refresh_token_hash` must be SHA-256 hash (64 hex characters)
- `revoked_at` must be NULL or >= `created_at`

**State Transitions**:
1. **Active** → `revoked_at = NULL`, `expires_at > NOW()`
2. **Revoked** → `revoked_at = <timestamp>`
3. **Expired** → `expires_at <= NOW()`
4. **Rotated** → Old session revoked, new session created with new token

---

### 3. PasswordResetToken

**Purpose**: Represents a password reset request with single-use magic link token.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique token identifier |
| `user_id` | UUID | FOREIGN KEY → users.id, NOT NULL | User requesting password reset |
| `token_hash` | VARCHAR(255) | UNIQUE, NOT NULL | SHA-256 hash of reset token (never store plaintext) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Token creation timestamp |
| `expires_at` | TIMESTAMP | NOT NULL | Token expiry timestamp (15 minutes from creation) |
| `used_at` | TIMESTAMP | NULL | Timestamp when token was used (NULL = unused) |

**Indexes**:
- `idx_password_reset_tokens_user_id` on `user_id` (for user token lookups)
- `idx_password_reset_tokens_token_hash` on `token_hash` (for token validation)
- `idx_password_reset_tokens_expires_at` on `expires_at` (for cleanup job)

**Validation Rules**:
- `expires_at` must be exactly 15 minutes after `created_at`
- `token_hash` must be SHA-256 hash (64 hex characters)
- `used_at` must be NULL or between `created_at` and `expires_at`

**State Transitions**:
1. **Created** → `used_at = NULL`, `expires_at > NOW()`
2. **Used** → `used_at = <timestamp>`
3. **Expired** → `expires_at <= NOW()`

---

### 4. EmailVerificationToken

**Purpose**: Represents an email verification request with single-use verification link token.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique token identifier |
| `user_id` | UUID | FOREIGN KEY → users.id, NOT NULL | User requesting email verification |
| `token_hash` | VARCHAR(255) | UNIQUE, NOT NULL | SHA-256 hash of verification token (never store plaintext) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Token creation timestamp |
| `expires_at` | TIMESTAMP | NOT NULL | Token expiry timestamp (24 hours from creation) |
| `used_at` | TIMESTAMP | NULL | Timestamp when token was used (NULL = unused) |

**Indexes**:
- `idx_email_verification_tokens_user_id` on `user_id` (for user token lookups)
- `idx_email_verification_tokens_token_hash` on `token_hash` (for token validation)
- `idx_email_verification_tokens_expires_at` on `expires_at` (for cleanup job)

**Validation Rules**:
- `expires_at` must be exactly 24 hours after `created_at`
- `token_hash` must be SHA-256 hash (64 hex characters)
- `used_at` must be NULL or between `created_at` and `expires_at`

**State Transitions**:
1. **Created** → `used_at = NULL`, `expires_at > NOW()`
2. **Used** → `used_at = <timestamp>`, user's `email_verified_at` updated
3. **Expired** → `expires_at <= NOW()`

---

### 5. RateLimitCounter

**Purpose**: Tracks failed login attempts for rate limiting (5 failures = 15-minute lockout).

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique counter identifier |
| `identifier` | VARCHAR(255) | UNIQUE, NOT NULL | IP address or email being rate limited |
| `identifier_type` | ENUM | NOT NULL | Type of identifier: `ip` or `email` |
| `attempt_count` | INTEGER | NOT NULL, DEFAULT 0 | Number of failed attempts |
| `lockout_until` | TIMESTAMP | NULL | Timestamp when lockout expires (NULL = not locked out) |
| `last_attempt_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Timestamp of last failed attempt |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Counter creation timestamp |

**Indexes**:
- `idx_rate_limit_counters_identifier` on `identifier` (for rate limit checks)
- `idx_rate_limit_counters_lockout_until` on `lockout_until` (for cleanup job)

**Validation Rules**:
- `identifier_type` must be one of: `ip`, `email`
- `attempt_count` must be >= 0
- `lockout_until` must be NULL or > `last_attempt_at`

**State Transitions**:
1. **Normal** → `attempt_count < 5`, `lockout_until = NULL`
2. **Locked Out** → `attempt_count >= 5`, `lockout_until = NOW() + 15 minutes`
3. **Lockout Expired** → `lockout_until <= NOW()`, reset `attempt_count = 0`
4. **Successful Login** → Reset `attempt_count = 0`, `lockout_until = NULL`

---

## Database Constraints

### Foreign Keys
- `sessions.user_id` → `users.id` (ON DELETE CASCADE)
- `password_reset_tokens.user_id` → `users.id` (ON DELETE CASCADE)
- `email_verification_tokens.user_id` → `users.id` (ON DELETE CASCADE)

### Unique Constraints
- `users.email` (prevent duplicate accounts)
- `sessions.refresh_token_hash` (prevent token reuse)
- `password_reset_tokens.token_hash` (prevent token reuse)
- `email_verification_tokens.token_hash` (prevent token reuse)
- `rate_limit_counters.identifier` (one counter per IP/email)

### Check Constraints
- `users.role IN ('student', 'teacher', 'admin')`
- `rate_limit_counters.identifier_type IN ('ip', 'email')`
- `rate_limit_counters.attempt_count >= 0`
- `sessions.expires_at > sessions.created_at`
- `password_reset_tokens.expires_at > password_reset_tokens.created_at`
- `email_verification_tokens.expires_at > email_verification_tokens.created_at`

---

## Migration Strategy

### Initial Migration (001_create_auth_tables.py)

**Order of table creation** (respects foreign key dependencies):
1. `users` (no dependencies)
2. `sessions` (depends on users)
3. `password_reset_tokens` (depends on users)
4. `email_verification_tokens` (depends on users)
5. `rate_limit_counters` (no dependencies)

**Rollback strategy**: Drop tables in reverse order to avoid foreign key violations.

---

## Data Retention Policy

| Entity | Retention Period | Cleanup Strategy |
|--------|------------------|------------------|
| `users` | Indefinite | Manual deletion via "Delete My Account" endpoint |
| `sessions` | 7 days after expiry | Daily cleanup job deletes where `expires_at < NOW() - INTERVAL '7 days'` |
| `password_reset_tokens` | 24 hours after expiry | Daily cleanup job deletes where `expires_at < NOW() - INTERVAL '24 hours'` |
| `email_verification_tokens` | 24 hours after expiry | Daily cleanup job deletes where `expires_at < NOW() - INTERVAL '24 hours'` |
| `rate_limit_counters` | 30 days after last attempt | Weekly cleanup job deletes where `last_attempt_at < NOW() - INTERVAL '30 days'` |

---

## Security Considerations

1. **Never store plaintext tokens**: All tokens (refresh, reset, verification) stored as SHA-256 hashes
2. **Never store plaintext passwords**: All passwords stored as bcrypt hashes
3. **Cascade deletes**: When user is deleted, all related sessions/tokens are automatically deleted
4. **Token uniqueness**: Unique constraints on token hashes prevent replay attacks
5. **Timestamp validation**: All token expiry checks use server-side timestamps (UTC)
6. **Rate limiting**: Separate counters for IP and email prevent bypass via VPN/proxy

---

## Performance Considerations

1. **Indexes on foreign keys**: All `user_id` columns indexed for fast joins
2. **Indexes on lookup columns**: `email`, `token_hash`, `identifier` indexed for fast validation
3. **Indexes on time columns**: `expires_at`, `created_at` indexed for cleanup jobs and analytics
4. **Composite index opportunity**: Consider `(user_id, revoked_at, expires_at)` on sessions for "active sessions" queries
5. **Cleanup job timing**: Run during low-traffic hours (e.g., 3 AM UTC) to minimize impact

---

## Future Enhancements (Out of MVP Scope)

1. **MFA support**: Use `mfa_enabled` and `mfa_secret` columns (already prepared)
2. **Granular permissions**: Use `permissions` JSONB column for fine-grained access control
3. **Session activity history**: Add `session_activities` table to track all session events
4. **Device fingerprinting**: Add `device_fingerprint` column to sessions for trusted device detection
5. **IP geolocation**: Add `country_code` column to sessions for suspicious login detection
