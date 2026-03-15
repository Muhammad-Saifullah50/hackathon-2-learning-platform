"""create progress tracking tables

Revision ID: 002d_progress_tracking
Revises: 002c_curriculum_structure
Create Date: 2026-03-15 06:54:38.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002d_progress_tracking'
down_revision = '002c_curriculum_structure'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_exercise_progress table
    op.create_table(
        'user_exercise_progress',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='not_started'),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='RESTRICT'),
        sa.CheckConstraint("status IN ('not_started', 'in_progress', 'completed')", name='check_exercise_status'),
        sa.CheckConstraint('score >= 0 AND score <= 100', name='check_exercise_score_range')
    )
    op.create_index('ix_user_exercise_progress_user_exercise', 'user_exercise_progress', ['user_id', 'exercise_id'], unique=True)
    op.create_index('ix_user_exercise_progress_user_id', 'user_exercise_progress', ['user_id'], unique=False)
    op.create_index('ix_user_exercise_progress_status', 'user_exercise_progress', ['status'], unique=False)

    # Create user_quiz_attempts table
    op.create_table(
        'user_quiz_attempts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('quiz_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('answers', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('score >= 0 AND score <= 100', name='check_quiz_score_range')
    )
    op.create_index('ix_user_quiz_attempts_user_id', 'user_quiz_attempts', ['user_id'], unique=False)
    op.create_index('ix_user_quiz_attempts_quiz_id', 'user_quiz_attempts', ['quiz_id'], unique=False)
    op.create_index('ix_user_quiz_attempts_user_created', 'user_quiz_attempts', ['user_id', 'created_at'], unique=False, postgresql_ops={'created_at': 'DESC'})

    # Create user_module_mastery table
    op.create_table(
        'user_module_mastery',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, server_default='0'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('score >= 0 AND score <= 100', name='check_mastery_score_range')
    )
    op.create_index('ix_user_module_mastery_user_module', 'user_module_mastery', ['user_id', 'module_id'], unique=True)
    op.create_index('ix_user_module_mastery_user_id', 'user_module_mastery', ['user_id'], unique=False)
    op.create_index('ix_user_module_mastery_updated_at', 'user_module_mastery', ['updated_at'], unique=False)


def downgrade() -> None:
    # Drop user_module_mastery table
    op.drop_index('ix_user_module_mastery_updated_at', table_name='user_module_mastery')
    op.drop_index('ix_user_module_mastery_user_id', table_name='user_module_mastery')
    op.drop_index('ix_user_module_mastery_user_module', table_name='user_module_mastery')
    op.drop_table('user_module_mastery')

    # Drop user_quiz_attempts table
    op.drop_index('ix_user_quiz_attempts_user_created', table_name='user_quiz_attempts')
    op.drop_index('ix_user_quiz_attempts_quiz_id', table_name='user_quiz_attempts')
    op.drop_index('ix_user_quiz_attempts_user_id', table_name='user_quiz_attempts')
    op.drop_table('user_quiz_attempts')

    # Drop user_exercise_progress table
    op.drop_index('ix_user_exercise_progress_status', table_name='user_exercise_progress')
    op.drop_index('ix_user_exercise_progress_user_id', table_name='user_exercise_progress')
    op.drop_index('ix_user_exercise_progress_user_exercise', table_name='user_exercise_progress')
    op.drop_table('user_exercise_progress')
