"""extend users table with preferences and deleted_at

Revision ID: 002a_extend_users
Revises: c768d74c6e9c
Create Date: 2026-03-15 06:54:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002a_extend_users'
down_revision = 'c768d74c6e9c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add preferences JSONB column to users table
    op.add_column('users', sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'))

    # Add deleted_at timestamp column for soft deletes
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # Create indexes
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'], unique=False)
    op.create_index('ix_users_preferences_gin', 'users', ['preferences'], unique=False, postgresql_using='gin')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_users_preferences_gin', table_name='users')
    op.drop_index('ix_users_deleted_at', table_name='users')

    # Drop columns
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'preferences')
