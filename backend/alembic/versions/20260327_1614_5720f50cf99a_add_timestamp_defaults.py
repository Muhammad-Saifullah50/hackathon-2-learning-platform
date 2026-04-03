"""add_timestamp_defaults

Revision ID: 5720f50cf99a
Revises: 002g_seed_curriculum
Create Date: 2026-03-27 16:14:25.907353

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5720f50cf99a"
down_revision = "002g_seed_curriculum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add server defaults for timestamp columns (only for columns that exist)
    # Tables with both created_at and updated_at
    op.execute("ALTER TABLE users ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN updated_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE user_streaks ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE user_streaks ALTER COLUMN updated_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE modules ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE modules ALTER COLUMN updated_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE lessons ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE lessons ALTER COLUMN updated_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE exercises ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE exercises ALTER COLUMN updated_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE quizzes ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE quizzes ALTER COLUMN updated_at SET DEFAULT NOW()")
    op.execute(
        "ALTER TABLE user_exercise_progress ALTER COLUMN created_at SET DEFAULT NOW()"
    )
    op.execute(
        "ALTER TABLE user_exercise_progress ALTER COLUMN updated_at SET DEFAULT NOW()"
    )
    op.execute(
        "ALTER TABLE user_module_mastery ALTER COLUMN created_at SET DEFAULT NOW()"
    )
    op.execute(
        "ALTER TABLE user_module_mastery ALTER COLUMN updated_at SET DEFAULT NOW()"
    )

    # Tables with only created_at
    op.execute("ALTER TABLE code_submissions ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute(
        "ALTER TABLE email_verification_tokens ALTER COLUMN created_at SET DEFAULT NOW()"
    )
    op.execute("ALTER TABLE llm_cache ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute(
        "ALTER TABLE password_reset_tokens ALTER COLUMN created_at SET DEFAULT NOW()"
    )
    op.execute(
        "ALTER TABLE rate_limit_counters ALTER COLUMN created_at SET DEFAULT NOW()"
    )
    op.execute("ALTER TABLE sessions ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute(
        "ALTER TABLE user_quiz_attempts ALTER COLUMN created_at SET DEFAULT NOW()"
    )


def downgrade() -> None:
    # Remove server defaults for timestamp columns
    # Tables with both created_at and updated_at
    op.execute("ALTER TABLE users ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at DROP DEFAULT")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN updated_at DROP DEFAULT")
    op.execute("ALTER TABLE user_streaks ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE user_streaks ALTER COLUMN updated_at DROP DEFAULT")
    op.execute("ALTER TABLE modules ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE modules ALTER COLUMN updated_at DROP DEFAULT")
    op.execute("ALTER TABLE lessons ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE lessons ALTER COLUMN updated_at DROP DEFAULT")
    op.execute("ALTER TABLE exercises ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE exercises ALTER COLUMN updated_at DROP DEFAULT")
    op.execute("ALTER TABLE quizzes ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE quizzes ALTER COLUMN updated_at DROP DEFAULT")
    op.execute(
        "ALTER TABLE user_exercise_progress ALTER COLUMN created_at DROP DEFAULT"
    )
    op.execute(
        "ALTER TABLE user_exercise_progress ALTER COLUMN updated_at DROP DEFAULT"
    )
    op.execute("ALTER TABLE user_module_mastery ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE user_module_mastery ALTER COLUMN updated_at DROP DEFAULT")

    # Tables with only created_at
    op.execute("ALTER TABLE code_submissions ALTER COLUMN created_at DROP DEFAULT")
    op.execute(
        "ALTER TABLE email_verification_tokens ALTER COLUMN created_at DROP DEFAULT"
    )
    op.execute("ALTER TABLE llm_cache ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE password_reset_tokens ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE rate_limit_counters ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE sessions ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE user_quiz_attempts ALTER COLUMN created_at DROP DEFAULT")
