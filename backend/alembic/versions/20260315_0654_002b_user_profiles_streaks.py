"""create user_profiles and user_streaks tables

Revision ID: 002b_user_profiles_streaks
Revises: 002a_extend_users
Create Date: 2026-03-15 06:54:12.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002b_user_profiles_streaks'
down_revision = '002a_extend_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'], unique=True)
    op.create_index('ix_user_profiles_metadata_gin', 'user_profiles', ['metadata'], unique=False, postgresql_using='gin')

    # Create user_streaks table
    op.create_table(
        'user_streaks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('current_streak >= 0', name='check_current_streak_positive'),
        sa.CheckConstraint('longest_streak >= current_streak', name='check_longest_streak_valid')
    )
    op.create_index('ix_user_streaks_user_id', 'user_streaks', ['user_id'], unique=True)
    op.create_index('ix_user_streaks_last_activity', 'user_streaks', ['last_activity_date'], unique=False)


def downgrade() -> None:
    # Drop user_streaks table
    op.drop_index('ix_user_streaks_last_activity', table_name='user_streaks')
    op.drop_index('ix_user_streaks_user_id', table_name='user_streaks')
    op.drop_table('user_streaks')

    # Drop user_profiles table
    op.drop_index('ix_user_profiles_metadata_gin', table_name='user_profiles')
    op.drop_index('ix_user_profiles_user_id', table_name='user_profiles')
    op.drop_table('user_profiles')
