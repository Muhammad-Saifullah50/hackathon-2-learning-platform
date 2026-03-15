"""create llm_cache table

Revision ID: 002f_llm_cache
Revises: 002e_code_submissions
Create Date: 2026-03-15 06:55:04.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002f_llm_cache'
down_revision = '002e_code_submissions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create llm_cache table
    op.create_table(
        'llm_cache',
        sa.Column('cache_key_hash', sa.String(length=64), nullable=False),
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('cache_key_hash'),
        sa.CheckConstraint('token_count > 0', name='check_token_count_positive')
    )
    op.create_index('ix_llm_cache_last_accessed', 'llm_cache', ['last_accessed_at'], unique=False)
    op.create_index('ix_llm_cache_expires_at', 'llm_cache', ['expires_at'], unique=False)


def downgrade() -> None:
    # Drop llm_cache table
    op.drop_index('ix_llm_cache_expires_at', table_name='llm_cache')
    op.drop_index('ix_llm_cache_last_accessed', table_name='llm_cache')
    op.drop_table('llm_cache')
