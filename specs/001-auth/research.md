# Research: Authentication & Authorization

**Feature**: 001-auth | **Date**: 2026-03-14 | **Phase**: 0 (Research)

## Research Questions

### 1. Better Auth Integration with FastAPI Backend

**Question**: How does Better Auth (frontend) integrate with FastAPI JWT backend? What's the handoff mechanism?

**Research Findings**:
- Better Auth is a TypeScript-first auth library for Next.js that handles session management, cookies, and CSRF protection on the frontend
- Better Auth can work with custom backends by configuring custom providers
- Integration pattern: Better Auth manages frontend session/cookies, FastAPI issues JWT tokens, Better Auth stores JWT in httpOnly cookies
- Better Auth provides `useSession()` hook and middleware for protecting routes
- FastAPI validates JWT on every request via dependency injection (`get_current_user`)

**Decision**: Use Better Auth as frontend session manager that stores JWT tokens issued by FastAPI. Better Auth handles cookie security, CSRF, and session state. FastAPI remains authoritative source for JWT issuance and validation.

**Rationale**: Separates concerns - Better Auth handles browser security (cookies, CSRF), FastAPI handles token logic (signing, validation, refresh). Avoids reinventing frontend auth security.

**Alternatives Considered**:
- NextAuth.js: More opinionated, harder to integrate with custom FastAPI backend
- Manual cookie management: Error-prone, security risks (XSS, CSRF)
- Better Auth chosen for flexibility with custom backends and TypeScript-first design

---

### 2. JWT Algorithm: RS256 vs HS256

**Question**: Should we use RS256 (asymmetric) or HS256 (symmetric) for JWT signing?

**Research Findings**:
- HS256: Symmetric (same secret for signing and validation), simpler, faster
- RS256: Asymmetric (private key signs, public key validates), enables distributed validation
- Kong gateway needs to validate JWTs - requires access to validation key
- Spec requirement (FR-029): "MUST use RS256 algorithm for JWT signing to enable Kong validation with public key"

**Decision**: Use RS256 (asymmetric) with private key on FastAPI, public key distributed to Kong.

**Rationale**: Kong can validate JWTs without accessing signing secret. Enables secure distributed validation. Aligns with spec requirement FR-029.

**Alternatives Considered**:
- HS256: Rejected because Kong would need signing secret (security risk)
- RS256 chosen for security and distributed validation capability

---

### 3. Password Hashing: bcrypt vs Argon2

**Question**: Which password hashing algorithm should we use?

**Research Findings**:
- bcrypt: Industry standard, well-tested, OWASP recommended, slower by design (good for passwords)
- Argon2: Winner of Password Hashing Competition (2015), more resistant to GPU attacks, configurable memory hardness
- Constitution mentions "bcrypt or Argon2" (FR-005)
- Python libraries: `bcrypt` (mature), `argon2-cffi` (actively maintained)

**Decision**: Use bcrypt for MVP, prepare for Argon2 migration.

**Rationale**: bcrypt is battle-tested, simpler to configure, sufficient for MVP security. Argon2 offers marginal security improvement but adds complexity. Can migrate later if needed.

**Alternatives Considered**:
- Argon2: Better security but more complex configuration (memory cost, parallelism)
- bcrypt chosen for simplicity and proven track record

---

### 4. HaveIBeenPwned API Integration

**Question**: How to integrate HaveIBeenPwned password breach checking? What's the API contract?

**Research Findings**:
- HaveIBeenPwned Passwords API: https://haveibeenpwned.com/API/v3#PwnedPasswords
- Uses k-anonymity model: hash password with SHA-1, send first 5 chars, receive list of matching hashes
- No rate limiting on Passwords API (as of 2026)
- Returns plain text response with hash suffixes and breach counts
- Example: `GET https://api.pwnedpasswords.com/range/21BD1` returns list like `0018A45C4D1DEF81644B54AB7F969B88D65:3`

**Decision**: Implement k-anonymity check using httpx async client. Hash password with SHA-1, send first 5 chars, check if full hash appears in response.

**Rationale**: k-anonymity protects user privacy (never sends full password hash). No rate limiting makes it suitable for production. Async httpx prevents blocking.

**Alternatives Considered**:
- Local breach database: Too large (~30GB), maintenance burden
- Skip check: Violates spec requirement FR-004
- k-anonymity API chosen for privacy and simplicity

---

### 5. Rate Limiting Storage: PostgreSQL vs Redis

**Question**: Should rate limit counters be stored in PostgreSQL or Redis?

**Research Findings**:
- Spec assumption: "Rate limiting counters are stored in PostgreSQL (not Redis) for MVP simplicity"
- PostgreSQL: Simpler (no additional service), ACID guarantees, sufficient for MVP scale
- Redis: Faster, better for high-frequency counters, requires additional service
- Constitution: "Accept for MVP; plan Redis migration if performance issues arise"

**Decision**: Use PostgreSQL for rate limit counters in MVP.

**Rationale**: Reduces operational complexity (no Redis to manage). PostgreSQL can handle 1000 concurrent requests (spec requirement). Can migrate to Redis if performance issues arise.

**Alternatives Considered**:
- Redis: Better performance but adds operational complexity
- PostgreSQL chosen for MVP simplicity per spec and constitution

---

### 6. Email Service: SMTP vs SendGrid

**Question**: Which email service should we use for verification and password reset emails?

**Research Findings**:
- SMTP: Generic protocol, works with any provider (Gmail, Mailgun, etc.), requires configuration
- SendGrid: Managed service, better deliverability, built-in templates, API-based
- Constitution mentions: "Use reputable email service (SendGrid), configure SPF/DKIM"
- Spec assumption: "Email service (SMTP or SendGrid) is configured"

**Decision**: Use SendGrid for production, SMTP (Mailhog/MailCatcher) for local development.

**Rationale**: SendGrid has better deliverability (SPF/DKIM pre-configured), reduces spam risk. SMTP for local dev avoids external dependencies during testing.

**Alternatives Considered**:
- Gmail SMTP: Rate limits, not suitable for production
- Mailgun: Similar to SendGrid but less popular
- SendGrid chosen for deliverability and constitution recommendation

---

### 7. Token Storage: Database Schema Design

**Question**: How should we structure sessions, password_reset_tokens, and email_verification_tokens tables?

**Research Findings**:
- Sessions: Need user_id, refresh_token_hash, device/user_agent, created_at, expires_at, revoked_at
- Password reset tokens: Need user_id, token_hash, created_at, expires_at, used_at
- Email verification tokens: Need user_id, token_hash, created_at, expires_at, used_at
- All tokens should store hashes (not plaintext) for security
- Need indexes on user_id for fast lookups
- Need indexes on token_hash for validation queries

**Decision**: Create three separate tables with similar structure. Store token hashes (SHA-256), not plaintext. Add indexes on user_id and token_hash.

**Rationale**: Separate tables provide clear separation of concerns. Hashing tokens prevents database breach from compromising active sessions. Indexes ensure fast lookups.

**Alternatives Considered**:
- Single tokens table with type discriminator: Harder to query, mixed concerns
- Separate tables chosen for clarity and performance

---

### 8. JWT Claims Schema for Kong Integration

**Question**: What JWT claims are required for Kong gateway validation?

**Research Findings**:
- Spec requirement (FR-028): "sub (user_id), role, email, iat, exp as minimum required claims"
- Kong JWT plugin validates: signature, exp (expiry), iat (issued at)
- Custom claims (role, email) used by downstream services for authorization
- Kong can extract claims and pass as headers to backend services

**Decision**: JWT payload structure:
```json
{
  "sub": "user_id_uuid",
  "role": "student|teacher|admin",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234568790
}
```

**Rationale**: Minimal claims reduce token size. Role claim enables RBAC. Email useful for logging/debugging. Aligns with spec FR-028.

**Alternatives Considered**:
- Include permissions array: Premature (permissions unused in MVP per spec)
- Include display_name: Unnecessary (can fetch from /api/auth/me)
- Minimal claims chosen for token size and spec alignment

---

### 9. Session Cleanup Strategy

**Question**: How should expired sessions be cleaned up from the database?

**Research Findings**:
- Spec assumption: "Session cleanup (expired sessions) is handled by scheduled job (not real-time)"
- Options: Cron job, database trigger, lazy cleanup on access
- Expired sessions don't affect security (JWT exp claim enforced), but clutter database
- PostgreSQL supports scheduled jobs via pg_cron extension

**Decision**: Implement daily cleanup job (separate script) that deletes sessions where expires_at < NOW() and revoked_at IS NOT NULL OR expires_at < NOW() - 7 days.

**Rationale**: Daily cleanup sufficient for MVP. Keeps database size manageable. Doesn't require real-time processing. Can run as cron job or Kubernetes CronJob.

**Alternatives Considered**:
- Real-time cleanup on every request: Performance overhead
- Database trigger: Complex, harder to test
- Scheduled job chosen for simplicity and testability

---

### 10. Frontend Auth State Management

**Question**: How should frontend manage auth state (logged in, user info, token refresh)?

**Research Findings**:
- Better Auth provides `useSession()` hook for accessing session state
- Better Auth handles token refresh automatically via refresh token endpoint
- Need to handle: loading state, error state, user profile data
- React Context can wrap Better Auth for app-wide state

**Decision**: Use Better Auth `useSession()` hook + custom `useAuth()` hook that wraps it with user profile fetching from /api/auth/me.

**Rationale**: Better Auth handles token mechanics. Custom hook adds user profile data. Keeps auth logic centralized and testable.

**Alternatives Considered**:
- Redux/Zustand: Overkill for auth state alone
- React Context only: Duplicates Better Auth functionality
- Better Auth + custom hook chosen for simplicity

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend Auth | Better Auth | TypeScript-first, flexible with custom backends |
| Backend Framework | FastAPI | Async, fast, OpenAPI auto-generation |
| JWT Algorithm | RS256 | Asymmetric, enables Kong validation |
| Password Hashing | bcrypt | Battle-tested, OWASP recommended |
| Password Breach Check | HaveIBeenPwned API | k-anonymity, no rate limits |
| Rate Limiting Storage | PostgreSQL | MVP simplicity, sufficient for scale |
| Email Service | SendGrid (prod), SMTP (dev) | Better deliverability, SPF/DKIM |
| Session Storage | PostgreSQL | ACID guarantees, simpler than Redis |
| Token Cleanup | Scheduled job (daily) | Simple, testable, sufficient |
| Frontend State | Better Auth + custom hook | Centralized, handles refresh automatically |

---

## Open Questions / Risks

1. **Kong JWT configuration**: Need to coordinate with F03 team on public key distribution mechanism. **Action**: Document public key endpoint in contracts/ and share with F03.

2. **HaveIBeenPwned API availability**: If API is down, password registration fails. **Mitigation**: Implement fallback to skip check with warning log (per spec assumption).

3. **Email deliverability**: Verification emails may land in spam. **Mitigation**: Use SendGrid, configure SPF/DKIM, test with multiple email providers.

4. **Token rotation race conditions**: Concurrent refresh requests could cause issues. **Mitigation**: Use database transactions and unique constraints on refresh_token_hash.

5. **Rate limiting accuracy**: PostgreSQL-based counters may have slight delays under high concurrency. **Mitigation**: Accept for MVP, monitor performance, migrate to Redis if needed.

---

## Next Steps (Phase 1)

1. Generate data-model.md with entity schemas (User, Session, PasswordResetToken, EmailVerificationToken, RateLimitCounter)
2. Generate contracts/auth-api.yaml (OpenAPI spec for all auth endpoints)
3. Generate contracts/jwt-schema.json (JWT claims schema for Kong)
4. Generate quickstart.md (setup instructions for local development)
5. Update agent context with new technologies
