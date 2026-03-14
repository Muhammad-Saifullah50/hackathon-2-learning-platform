"""Rate limiting logic for authentication endpoints."""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.auth.models import IdentifierType, RateLimitCounter
from src.config import settings

# Configure logger
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for tracking failed authentication attempts."""

    def __init__(self, db: Session):
        """
        Initialize rate limiter.

        Args:
            db: Database session
        """
        self.db = db

    def check_rate_limit(self, identifier: str, identifier_type: str) -> Optional[datetime]:
        """
        Check if identifier is rate limited.

        Args:
            identifier: IP address or email to check
            identifier_type: Type of identifier ('ip' or 'email')

        Returns:
            None if not rate limited, otherwise datetime when lockout expires
        """
        counter = (
            self.db.query(RateLimitCounter)
            .filter(RateLimitCounter.identifier == identifier)
            .first()
        )

        if not counter:
            return None

        # Check if lockout is active
        if counter.lockout_until and counter.lockout_until > datetime.utcnow():
            return counter.lockout_until

        # Lockout expired, reset counter
        if counter.lockout_until and counter.lockout_until <= datetime.utcnow():
            counter.attempt_count = 0
            counter.lockout_until = None
            self.db.commit()

        return None

    def increment_failed_attempt(self, identifier: str, identifier_type: str) -> None:
        """
        Increment failed attempt counter for identifier.

        Args:
            identifier: IP address or email
            identifier_type: Type of identifier ('ip' or 'email')
        """
        counter = (
            self.db.query(RateLimitCounter)
            .filter(RateLimitCounter.identifier == identifier)
            .first()
        )

        if not counter:
            # Create new counter
            counter = RateLimitCounter(
                identifier=identifier,
                identifier_type=IdentifierType(identifier_type),
                attempt_count=1,
                last_attempt_at=datetime.utcnow(),
            )
            self.db.add(counter)
            logger.info(f"Rate limit counter created - identifier: {identifier}, type: {identifier_type}, count: 1")
        else:
            # Increment existing counter
            counter.attempt_count += 1
            counter.last_attempt_at = datetime.utcnow()

            # Apply lockout if threshold reached
            if counter.attempt_count >= settings.RATE_LIMIT_MAX_ATTEMPTS:
                counter.lockout_until = datetime.utcnow() + timedelta(
                    minutes=settings.RATE_LIMIT_LOCKOUT_MINUTES
                )
                logger.warning(
                    f"Rate limit lockout applied - identifier: {identifier}, type: {identifier_type}, "
                    f"attempts: {counter.attempt_count}, lockout_until: {counter.lockout_until}"
                )
            else:
                logger.info(
                    f"Rate limit counter incremented - identifier: {identifier}, type: {identifier_type}, "
                    f"count: {counter.attempt_count}"
                )

        self.db.commit()

    def reset_counter(self, identifier: str) -> None:
        """
        Reset rate limit counter for identifier (called on successful login).

        Args:
            identifier: IP address or email
        """
        counter = (
            self.db.query(RateLimitCounter)
            .filter(RateLimitCounter.identifier == identifier)
            .first()
        )

        if counter:
            counter.attempt_count = 0
            counter.lockout_until = None
            self.db.commit()
            logger.info(f"Rate limit counter reset - identifier: {identifier}")

    def get_remaining_lockout_seconds(self, lockout_until: datetime) -> int:
        """
        Calculate remaining lockout time in seconds.

        Args:
            lockout_until: Datetime when lockout expires

        Returns:
            Remaining seconds until lockout expires
        """
        remaining = lockout_until - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))