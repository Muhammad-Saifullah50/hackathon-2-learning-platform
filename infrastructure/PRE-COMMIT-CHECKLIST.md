# Pre-Commit Security Checklist

Before committing infrastructure changes, verify:

## ✓ Completed Security Measures

### 1. .gitignore Protection
- [x] All key files (*.pem, *.key, *.pub) ignored
- [x] All environment files (.env, .env.*) ignored
- [x] All secret YAML files (*-secret.yaml) ignored
- [x] Backup files (*.backup) ignored
- [x] Database credentials (NEON_DATABASE.md) ignored
- [x] Keys directories (backend/keys/, backend/*/keys/) ignored

### 2. Hardcoded Secrets Replaced
- [x] Kong PostgreSQL password → Uses ${KONG_PG_PASSWORD:-kong}
- [x] Redis password → Uses ${REDIS_PASSWORD:-changeme}
- [x] Kong rate-limit plugin Redis password → Uses ${REDIS_PASSWORD:-changeme}
- [x] JWT public key → Placeholder with instructions to replace

### 3. Documentation Created
- [x] infrastructure/SECURITY.md - Security guidelines
- [x] infrastructure/.env.example - Template for secrets
- [x] infrastructure/.env - Local secrets file (ignored by git)

### 4. Verification Tests Passed
- [x] All secret files properly ignored by git
- [x] No hardcoded passwords in staged files
- [x] No untracked secret files will be committed

## Files Safe to Commit

The following infrastructure files are safe to commit:
- All YAML configuration files (with environment variable placeholders)
- All shell scripts (reference key paths, don't contain keys)
- Documentation files (SECURITY.md, README.md, etc.)
- .env.example (template only, no real secrets)

## Files That Will NOT Be Committed (Protected)

- backend/keys/*.pem, *.key, *.pub
- backend/auth-service/keys/*
- infrastructure/.env
- NEON_DATABASE.md
- Any *.backup files

## Next Steps After Commit

1. Team members must create their own `infrastructure/.env` from `.env.example`
2. Generate JWT keys if not present (see SECURITY.md)
3. Create Kubernetes secrets before deployment (see SECURITY.md)
4. Never share the actual `.env` file or key files via chat/email

---
Generated: 2026-03-15
Status: READY TO COMMIT ✓
