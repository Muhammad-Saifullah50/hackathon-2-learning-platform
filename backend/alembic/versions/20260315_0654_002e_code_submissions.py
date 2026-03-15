"""create code_submissions table

Revision ID: 002e_code_submissions
Revises: 002d_progress_tracking
Create Date: 2026-03-15 06:54:51.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002e_code_submissions'
down_revision = '002d_progress_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create code_submissions table
    op.create_table(
        'code_submissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('code_text', sa.Text(), nullable=False),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('quality_rating', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('quality_rating >= 0 AND quality_rating <= 100', name='check_quality_rating_range')
    )
    op.create_index('ix_code_submissions_user_exercise_created', 'code_submissions', ['user_id', 'exercise_id', 'created_at'], unique=False, postgresql_ops={'created_at': 'DESC'})
    op.create_index('ix_code_submissions_user_id', 'code_submissions', ['user_id'], unique=False)
    op.create_index('ix_code_submissions_created_at', 'code_submissions', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop code_submissions table
    op.drop_index('ix_code_submissions_created_at', table_name='code_submissions')
    op.drop_index('ix_code_submissions_user_id', table_name='code_submissions')
    op.drop_index('ix_code_submissions_user_exercise_created', table_name='code_submissions')
    op.drop_table('code_submissions')
