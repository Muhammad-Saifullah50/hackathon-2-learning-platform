"""Repository layer for database operations."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from src.auth.models import EmailVerificationToken, PasswordResetToken, RateLimitCounter
from src.auth.models import Session as SessionModel
from src.models.user import User


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create_user(
        self,
        email: str,
        password_hash: str,
        display_name: str,
        role: str,
    ) -> User:
        """
        Create a new user.

        Args:
            email: User email address
            password_hash: Hashed password
            display_name: User display name
            role: User role (student, teacher, admin)

        Returns:
            Created User object
        """
        from src.auth.models import UserRole

        user = User(
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            role=UserRole(role),  # Convert string to enum
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email address

        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def update_email_verified(self, user_id: UUID) -> None:
        """
        Mark user email as verified.

        Args:
            user_id: User UUID
        """
        user = self.get_by_id(user_id)
        if user:
            user.email_verified_at = datetime.utcnow()
            self.db.commit()


class EmailVerificationTokenRepository:
    """Repository for EmailVerificationToken database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create_token(self, user_id: UUID, expires_hours: int = 24) -> str:
        """
        Create email verification token for user.

        Args:
            user_id: User UUID
            expires_hours: Token expiry in hours (default 24)

        Returns:
            Plain text token (not hashed)
        """
        # Generate random token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Create token record
        verification_token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
        )
        self.db.add(verification_token)
        self.db.commit()

        return token

    def get_by_token_hash(self, token: str) -> Optional[EmailVerificationToken]:
        """
        Get verification token by plain text token.

        Args:
            token: Plain text token

        Returns:
            EmailVerificationToken if found, None otherwise
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return (
            self.db.query(EmailVerificationToken)
            .filter(
                EmailVerificationToken.token_hash == token_hash,
            )
            .first()
        )

    def mark_used(self, token_id: UUID) -> None:
        """
        Mark token as used.

        Args:
            token_id: Token UUID
        """
        token = (
            self.db.query(EmailVerificationToken)
            .filter(EmailVerificationToken.id == token_id)
            .first()
        )
        if token:
            token.used_at = datetime.utcnow()
            self.db.commit()


class SessionRepository:
    """Repository for Session database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create_session(
        self,
        user_id: UUID,
        refresh_token: str,
        expires_days: int = 7,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SessionModel:
        """
        Create a new session.

        Args:
            user_id: User UUID
            refresh_token: Plain text refresh token
            expires_days: Session expiry in days (default 7)
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Created Session object
        """
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        session = SessionModel(
            user_id=user_id,
            refresh_token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(days=expires_days),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_refresh_token_hash(self, refresh_token: str) -> Optional[SessionModel]:
        """
        Get session by refresh token.

        Args:
            refresh_token: Plain text refresh token

        Returns:
            Session if found and valid, None otherwise
        """
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        return (
            self.db.query(SessionModel)
            .filter(
                SessionModel.refresh_token_hash == token_hash,
                SessionModel.revoked_at.is_(None),
                SessionModel.expires_at > datetime.utcnow(),
            )
            .first()
        )

    def revoke_session(self, session_id: UUID) -> None:
        """
        Revoke a session.

        Args:
            session_id: Session UUID
        """
        session = (
            self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
        )
        if session:
            session.revoked_at = datetime.utcnow()
            self.db.commit()

    def revoke_all_user_sessions(self, user_id: UUID) -> None:
        """
        Revoke all sessions for a user.

        Args:
            user_id: User UUID
        """
        self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id, SessionModel.revoked_at.is_(None)
        ).update({"revoked_at": datetime.utcnow()})
        self.db.commit()


class PasswordResetTokenRepository:
    """Repository for PasswordResetToken database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create_token(self, user_id: UUID, expires_minutes: int = 15) -> str:
        """
        Create password reset token for user.

        Args:
            user_id: User UUID
            expires_minutes: Token expiry in minutes (default 15)

        Returns:
            Plain text token (not hashed)
        """
        # Generate random token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Create token record
        reset_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
        )
        self.db.add(reset_token)
        self.db.commit()

        return token

    def get_by_token_hash(self, token: str) -> Optional[PasswordResetToken]:
        """
        Get password reset token by plain text token.

        Args:
            token: Plain text token

        Returns:
            PasswordResetToken if found, None otherwise
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return (
            self.db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == token_hash,
            )
            .first()
        )

    def mark_used(self, token_id: UUID) -> None:
        """
        Mark token as used.

        Args:
            token_id: Token UUID
        """
        token = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.id == token_id)
            .first()
        )
        if token:
            token.used_at = datetime.utcnow()
            self.db.commit()
