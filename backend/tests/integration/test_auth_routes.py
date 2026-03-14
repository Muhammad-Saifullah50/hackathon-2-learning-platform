"""Integration tests for authentication routes."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth.models import User


class TestUserRegistration:
    """Tests for User Story 1: New User Registration."""

    def test_register_user_success(self, client: TestClient, db: Session):
        """Test successful user registration with valid credentials."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "UniqueP@ssw0rd!2026",  # Unique password unlikely to be breached
                "display_name": "New User",
                "role": "student",
            },
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "message" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["display_name"] == "New User"
        assert data["user"]["role"] == "student"
        assert "id" in data["user"]

        # Verify user created in database
        user = db.query(User).filter(User.email == "newuser@example.com").first()
        assert user is not None
        assert user.display_name == "New User"
        assert user.role.value == "student"

    def test_register_breached_password(self, client: TestClient, db: Session):
        """Test registration rejection with breached password."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Password123!",  # Known breached password with special char
                "display_name": "New User",
                "role": "student",
            },
        )

        assert response.status_code == 422
        data = response.json()
        # FastAPI returns detail as string for HTTPException
        assert "breach" in data["detail"].lower() or "compromised" in data["detail"].lower()

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration rejection with duplicate email."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,  # Already exists
                "password": "NewPass@123",
                "display_name": "Another User",
                "role": "student",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower() or "already registered" in data["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test registration rejection with invalid email format."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass@123",
                "display_name": "New User",
                "role": "student",
            },
        )

        assert response.status_code == 422

    def test_register_weak_password(self, client: TestClient):
        """Test registration rejection with weak password."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "short",  # Too short
                "display_name": "New User",
                "role": "student",
            },
        )

        assert response.status_code == 422

    def test_register_password_no_special_char(self, client: TestClient):
        """Test registration rejection with password lacking special character."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "NoSpecialChar123",  # No special character
                "display_name": "New User",
                "role": "student",
            },
        )

        assert response.status_code == 422

    def test_register_invalid_role(self, client: TestClient):
        """Test registration rejection with invalid role."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass@123",
                "display_name": "New User",
                "role": "invalid_role",
            },
        )

        assert response.status_code == 422

    def test_register_teacher_creates_verification_token(self, client: TestClient, db: Session):
        """Test that registering as teacher creates email verification token."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "teacher@example.com",
                "password": "TeacherPass@123",
                "display_name": "New Teacher",
                "role": "teacher",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "verification email sent" in data["message"].lower() or "verify your email" in data["message"].lower()

        # Verify user created with unverified email
        user = db.query(User).filter(User.email == "teacher@example.com").first()
        assert user is not None
        assert user.email_verified_at is None


class TestUserLogin:
    """Tests for User Story 2: User Login with JWT Tokens."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login with valid credentials."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@1234",  # Password from test_user fixture
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "tokens" in data
        assert data["user"]["email"] == test_user.email
        assert data["user"]["id"] == str(test_user.id)

        # Verify tokens
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
        assert data["tokens"]["token_type"] == "bearer"
        assert data["tokens"]["expires_in"] == 900  # 15 minutes in seconds

    def test_login_invalid_credentials(self, client: TestClient, test_user: User):
        """Test login rejection with invalid credentials."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword@123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login rejection with nonexistent user."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword@123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower()

    def test_login_rate_limit(self, client: TestClient, test_user: User):
        """Test rate limiting after multiple failed login attempts."""
        # Make 5 failed login attempts
        for _ in range(5):
            client.post(
                "/api/auth/login",
                json={
                    "email": test_user.email,
                    "password": "WrongPassword@123",
                },
            )

        # 6th attempt should be rate limited
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword@123",
            },
        )

        assert response.status_code == 429
        data = response.json()
        assert "too many" in data["detail"].lower() or "rate limit" in data["detail"].lower()

    def test_refresh_token_success(self, client: TestClient, test_user: User):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@1234",
            },
        )
        assert login_response.status_code == 200
        refresh_token = login_response.json()["tokens"]["refresh_token"]

        # Refresh the token
        response = client.post(
            "/api/auth/refresh",
            json={
                "refresh_token": refresh_token,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify new tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900

    def test_refresh_token_rotation(self, client: TestClient, test_user: User):
        """Test that refresh token is rotated (old token becomes invalid)."""
        # First login to get tokens
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@1234",
            },
        )
        old_refresh_token = login_response.json()["tokens"]["refresh_token"]

        # Refresh the token
        refresh_response = client.post(
            "/api/auth/refresh",
            json={
                "refresh_token": old_refresh_token,
            },
        )
        assert refresh_response.status_code == 200
        new_refresh_token = refresh_response.json()["refresh_token"]

        # Old token should not work anymore
        response = client.post(
            "/api/auth/refresh",
            json={
                "refresh_token": old_refresh_token,
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower() or "revoked" in data["detail"].lower()

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/auth/refresh",
            json={
                "refresh_token": "invalid_token_here",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower()


class TestCurrentUserProfile:
    """Tests for User Story 7: Current User Profile Retrieval."""

    def test_get_current_user_success(self, client: TestClient, test_user: User):
        """Test successful profile retrieval with valid token."""
        # First login to get access token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@1234",
            },
        )
        access_token = login_response.json()["tokens"]["access_token"]

        # Get current user profile
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify user data
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["display_name"] == test_user.display_name
        assert data["role"] == test_user.role.value

    def test_get_current_user_no_token(self, client: TestClient):
        """Test profile retrieval without token."""
        response = client.get("/api/auth/me")

        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test profile retrieval with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower() or "token" in data["detail"].lower()

    def test_get_current_user_expired_token(self, client: TestClient, test_user: User):
        """Test profile retrieval with expired token."""
        from src.auth.jwt import encode_jwt
        from datetime import timedelta

        # Create an expired token
        payload = {
            "sub": str(test_user.id),
            "role": test_user.role.value,
            "email": test_user.email,
            "type": "access",
        }
        expired_token = encode_jwt(payload, expires_delta=timedelta(seconds=-1))

        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "expired" in data["detail"].lower()


class TestRoleBasedAccessControl:
    """Tests for User Story 5: Role-Based Access Control."""

    def test_rbac_student_forbidden(self, client: TestClient, test_user: User):
        """Test that student cannot access teacher-only endpoints."""
        # Login as student
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@1234",
            },
        )
        access_token = login_response.json()["tokens"]["access_token"]

        # Try to access teacher-only endpoint
        response = client.get(
            "/api/auth/teacher-only",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "forbidden" in data["detail"].lower() or "required roles" in data["detail"].lower()


class TestEmailVerification:
    """Tests for User Story 4: Email Verification."""

    def test_verify_email_success(self, client: TestClient, db: Session):
        """Test successful email verification with valid token."""
        from datetime import datetime, timedelta
        from src.auth.models import EmailVerificationToken
        import hashlib
        import secrets

        # Create a test user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "verify@example.com",
                "password": "UniqueVerify@2026!",
                "display_name": "Verify User",
                "role": "teacher",
            },
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["user"]["id"]

        # Create a verification token manually
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        verification_token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.add(verification_token)
        db.commit()

        # Verify email with token
        response = client.post(
            "/api/auth/email-verification/verify",
            json={"token": token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "verified" in data["message"].lower()

        # Verify user's email_verified_at is set
        user = db.query(User).filter(User.id == user_id).first()
        assert user.email_verified_at is not None

    def test_verify_email_expired_token(self, client: TestClient, db: Session):
        """Test email verification rejection with expired token."""
        from datetime import datetime, timedelta
        from src.auth.models import EmailVerificationToken
        import hashlib
        import secrets

        # Create a test user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "expired@example.com",
                "password": "UniqueExpired@2026!",
                "display_name": "Expired User",
                "role": "teacher",
            },
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["user"]["id"]

        # Create an expired verification token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Set created_at to 25 hours ago and expires_at to 1 hour ago
        created_time = datetime.utcnow() - timedelta(hours=25)
        expired_time = datetime.utcnow() - timedelta(hours=1)

        verification_token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_time,
            expires_at=expired_time,
        )
        db.add(verification_token)
        db.commit()

        # Try to verify with expired token
        response = client.post(
            "/api/auth/email-verification/verify",
            json={"token": token},
        )

        assert response.status_code == 400
        data = response.json()
        assert "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()

    def test_resend_verification_email(self, client: TestClient, db: Session):
        """Test resending verification email."""
        # Create a test user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "resend@example.com",
                "password": "UniqueResend@2026!",
                "display_name": "Resend User",
                "role": "teacher",
            },
        )
        assert register_response.status_code == 201

        # Request resend
        response = client.post(
            "/api/auth/email-verification/send",
            json={"email": "resend@example.com"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "sent" in data["message"].lower() or "email" in data["message"].lower()


class TestPasswordReset:
    """Tests for User Story 3: Password Reset via Magic Link."""

    def test_request_password_reset(self, client: TestClient, test_user: User):
        """Test password reset request."""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": test_user.email},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "email" in data["message"].lower() or "sent" in data["message"].lower()

    def test_confirm_password_reset_success(self, client: TestClient, db: Session, test_user: User):
        """Test successful password reset with valid token."""
        from datetime import datetime, timedelta
        from src.auth.models import PasswordResetToken
        import hashlib
        import secrets

        # Create a password reset token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        reset_token = PasswordResetToken(
            user_id=test_user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )
        db.add(reset_token)
        db.commit()

        # Reset password with token
        new_password = "NewSecurePass@2026!"
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": new_password,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "reset" in data["message"].lower() or "success" in data["message"].lower()

        # Verify user can login with new password
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": new_password,
            },
        )
        assert login_response.status_code == 200

    def test_confirm_password_reset_expired_token(self, client: TestClient, db: Session, test_user: User):
        """Test password reset rejection with expired token."""
        from datetime import datetime, timedelta
        from src.auth.models import PasswordResetToken
        import hashlib
        import secrets

        # Create an expired password reset token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Set created_at to 20 minutes ago and expires_at to 5 minutes ago
        created_time = datetime.utcnow() - timedelta(minutes=20)
        expired_time = datetime.utcnow() - timedelta(minutes=5)

        reset_token = PasswordResetToken(
            user_id=test_user.id,
            token_hash=token_hash,
            created_at=created_time,
            expires_at=expired_time,
        )
        db.add(reset_token)
        db.commit()

        # Try to reset password with expired token
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "NewSecurePass@2026!",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()

    def test_rbac_teacher_allowed(self, client: TestClient, test_teacher: User):
        """Test that teacher can access teacher-only endpoints."""
        # Verify teacher's email first (required for login)
        from datetime import datetime
        test_teacher.email_verified_at = datetime.utcnow()
        
        # Login as teacher
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_teacher.email,
                "password": "Teacher@1234",
            },
        )
        access_token = login_response.json()["tokens"]["access_token"]

        # Access teacher-only endpoint
        response = client.get(
            "/api/auth/teacher-only",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_rbac_admin_allowed(self, client: TestClient, test_admin: User):
        """Test that admin can access all endpoints."""
        # Verify admin's email first (required for login)
        from datetime import datetime
        test_admin.email_verified_at = datetime.utcnow()
        
        # Login as admin
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_admin.email,
                "password": "Admin@1234",
            },
        )
        access_token = login_response.json()["tokens"]["access_token"]

        # Access teacher-only endpoint (admin should have access)
        response = client.get(
            "/api/auth/teacher-only",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        # Access admin-only endpoint
        response = client.get(
            "/api/auth/admin-only",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_rbac_student_cannot_access_admin(self, client: TestClient, test_user: User):
        """Test that student cannot access admin-only endpoints."""
        # Login as student
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@1234",
            },
        )
        access_token = login_response.json()["tokens"]["access_token"]

        # Try to access admin-only endpoint
        response = client.get(
            "/api/auth/admin-only",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "forbidden" in data["detail"].lower() or "required roles" in data["detail"].lower()


class TestEmailVerification:
    """Tests for User Story 4: Email Verification."""

    def test_verify_email_success(self, client: TestClient, db: Session):
        """Test successful email verification with valid token."""
        from datetime import datetime, timedelta
        from src.auth.models import EmailVerificationToken
        import hashlib
        import secrets

        # Create a test user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "verify@example.com",
                "password": "UniqueVerify@2026!",
                "display_name": "Verify User",
                "role": "teacher",
            },
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["user"]["id"]

        # Create a verification token manually
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        verification_token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.add(verification_token)
        db.commit()

        # Verify email with token
        response = client.post(
            "/api/auth/email-verification/verify",
            json={"token": token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "verified" in data["message"].lower()

        # Verify user's email_verified_at is set
        user = db.query(User).filter(User.id == user_id).first()
        assert user.email_verified_at is not None

    def test_verify_email_expired_token(self, client: TestClient, db: Session):
        """Test email verification rejection with expired token."""
        from datetime import datetime, timedelta
        from src.auth.models import EmailVerificationToken
        import hashlib
        import secrets

        # Create a test user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "expired@example.com",
                "password": "UniqueExpired@2026!",
                "display_name": "Expired User",
                "role": "teacher",
            },
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["user"]["id"]

        # Create an expired verification token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Set created_at to 25 hours ago and expires_at to 1 hour ago
        created_time = datetime.utcnow() - timedelta(hours=25)
        expired_time = datetime.utcnow() - timedelta(hours=1)

        verification_token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_time,
            expires_at=expired_time,
        )
        db.add(verification_token)
        db.commit()

        # Try to verify with expired token
        response = client.post(
            "/api/auth/email-verification/verify",
            json={"token": token},
        )

        assert response.status_code == 400
        data = response.json()
        assert "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()

    def test_resend_verification_email(self, client: TestClient, db: Session):
        """Test resending verification email."""
        # Create a test user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "resend@example.com",
                "password": "UniqueResend@2026!",
                "display_name": "Resend User",
                "role": "teacher",
            },
        )
        assert register_response.status_code == 201

        # Request resend
        response = client.post(
            "/api/auth/email-verification/send",
            json={"email": "resend@example.com"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "sent" in data["message"].lower() or "email" in data["message"].lower()


class TestPasswordReset:
    """Tests for User Story 3: Password Reset via Magic Link."""

    def test_request_password_reset(self, client: TestClient, test_user: User):
        """Test password reset request."""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": test_user.email},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "email" in data["message"].lower() or "sent" in data["message"].lower()

    def test_confirm_password_reset_success(self, client: TestClient, db: Session, test_user: User):
        """Test successful password reset with valid token."""
        from datetime import datetime, timedelta
        from src.auth.models import PasswordResetToken
        import hashlib
        import secrets

        # Create a password reset token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        reset_token = PasswordResetToken(
            user_id=test_user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )
        db.add(reset_token)
        db.commit()

        # Reset password with token
        new_password = "NewSecurePass@2026!"
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": new_password,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "reset" in data["message"].lower() or "success" in data["message"].lower()

        # Verify user can login with new password
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": new_password,
            },
        )
        assert login_response.status_code == 200

    def test_confirm_password_reset_expired_token(self, client: TestClient, db: Session, test_user: User):
        """Test password reset rejection with expired token."""
        from datetime import datetime, timedelta
        from src.auth.models import PasswordResetToken
        import hashlib
        import secrets

        # Create an expired password reset token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Set created_at to 20 minutes ago and expires_at to 5 minutes ago
        created_time = datetime.utcnow() - timedelta(minutes=20)
        expired_time = datetime.utcnow() - timedelta(minutes=5)

        reset_token = PasswordResetToken(
            user_id=test_user.id,
            token_hash=token_hash,
            created_at=created_time,
            expires_at=expired_time,
        )
        db.add(reset_token)
        db.commit()

        # Try to reset password with expired token
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "NewSecurePass@2026!",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()



class TestSessionManagement:
    """Tests for User Story 6: Session Management & Logout."""

    def test_logout_success(self, client: TestClient, test_user: User, db: Session):
        """T094: Test successful logout from current session."""
        # Login to get access token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@1234",
            },
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["tokens"]["access_token"]

        # Logout from current session
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "logout" in data["message"].lower() or "success" in data["message"].lower()

        # Verify session is revoked in database
        from src.auth.models import Session as SessionModel
        sessions = db.query(SessionModel).filter(
            SessionModel.user_id == test_user.id,
            SessionModel.revoked_at.isnot(None)
        ).all()
        assert len(sessions) > 0

    def test_logout_all_success(self, client: TestClient, test_user: User, db: Session):
        """T095: Test successful logout from all sessions."""
        # Create multiple sessions by logging in multiple times
        tokens = []
        for _ in range(3):
            login_response = client.post(
                "/api/auth/login",
                json={
                    "email": test_user.email,
                    "password": "Test@1234",
                },
            )
            assert login_response.status_code == 200
            tokens.append(login_response.json()["tokens"]["access_token"])

        # Logout from all sessions using first token
        response = client.post(
            "/api/auth/logout-all",
            headers={"Authorization": f"Bearer {tokens[0]}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "all" in data["message"].lower() or "sessions" in data["message"].lower()

        # Verify all sessions are revoked in database
        from src.auth.models import Session as SessionModel
        active_sessions = db.query(SessionModel).filter(
            SessionModel.user_id == test_user.id,
            SessionModel.revoked_at.is_(None)
        ).all()
        assert len(active_sessions) == 0

    def test_revoked_token_rejected(self, client: TestClient, test_user: User):
        """T096: Test that revoked session token is rejected."""
        # Login to get access token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@1234",
            },
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["tokens"]["access_token"]

        # Logout (revoke session)
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_response.status_code == 200

        # Try to use revoked token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "revoked" in data["detail"].lower() or "invalid" in data["detail"].lower()


class TestKongIntegration:
    """Tests for Phase 10: Kong Integration."""

    def test_get_public_key(self, client: TestClient):
        """T105: Test public key endpoint returns valid PEM format."""
        response = client.get("/api/auth/public-key")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "public_key" in data
        assert "algorithm" in data
        assert "key_type" in data

        # Verify algorithm and key type
        assert data["algorithm"] == "RS256"
        assert data["key_type"] == "RSA"

        # Verify public key is in PEM format
        public_key = data["public_key"]
        assert "-----BEGIN PUBLIC KEY-----" in public_key
        assert "-----END PUBLIC KEY-----" in public_key
        assert len(public_key) > 100  # RSA public keys are typically 200+ chars

