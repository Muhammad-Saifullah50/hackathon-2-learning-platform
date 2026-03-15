"""create curriculum structure tables

Revision ID: 002c_curriculum_structure
Revises: 002b_user_profiles_streaks
Create Date: 2026-03-15 06:54:25.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002c_curriculum_structure'
down_revision = '002b_user_profiles_streaks'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create modules table
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_modules_order', 'modules', ['order'], unique=True)
    op.create_index('ix_modules_deleted_at', 'modules', ['deleted_at'], unique=False)

    # Create lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('content_ref', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='RESTRICT')
    )
    op.create_index('ix_lessons_module_id', 'lessons', ['module_id'], unique=False)
    op.create_index('ix_lessons_module_order', 'lessons', ['module_id', 'order'], unique=False)
    op.create_index('ix_lessons_deleted_at', 'lessons', ['deleted_at'], unique=False)

    # Create exercises table
    op.create_table(
        'exercises',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('starter_code', sa.Text(), nullable=True),
        sa.Column('content_ref', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='RESTRICT')
    )
    op.create_index('ix_exercises_lesson_id', 'exercises', ['lesson_id'], unique=False)
    op.create_index('ix_exercises_lesson_order', 'exercises', ['lesson_id', 'order'], unique=False)
    op.create_index('ix_exercises_deleted_at', 'exercises', ['deleted_at'], unique=False)

    # Create quizzes table
    op.create_table(
        'quizzes',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('questions', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='RESTRICT')
    )
    op.create_index('ix_quizzes_lesson_id', 'quizzes', ['lesson_id'], unique=False)
    op.create_index('ix_quizzes_deleted_at', 'quizzes', ['deleted_at'], unique=False)


def downgrade() -> None:
    # Drop quizzes table
    op.drop_index('ix_quizzes_deleted_at', table_name='quizzes')
    op.drop_index('ix_quizzes_lesson_id', table_name='quizzes')
    op.drop_table('quizzes')

    # Drop exercises table
    op.drop_index('ix_exercises_deleted_at', table_name='exercises')
    op.drop_index('ix_exercises_lesson_order', table_name='exercises')
    op.drop_index('ix_exercises_lesson_id', table_name='exercises')
    op.drop_table('exercises')

    # Drop lessons table
    op.drop_index('ix_lessons_deleted_at', table_name='lessons')
    op.drop_index('ix_lessons_module_order', table_name='lessons')
    op.drop_index('ix_lessons_module_id', table_name='lessons')
    op.drop_table('lessons')

    # Drop modules table
    op.drop_index('ix_modules_deleted_at', table_name='modules')
    op.drop_index('ix_modules_order', table_name='modules')
    op.drop_table('modules')
