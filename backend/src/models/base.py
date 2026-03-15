"""Base model classes and mixins for SQLAlchemy models."""
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self):
        """Mark the record as deleted."""
        self.deleted_at = datetime.utcnow()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), nullable=False, server_default='NOW()')

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), nullable=False, server_default='NOW()', onupdate=datetime.utcnow)
