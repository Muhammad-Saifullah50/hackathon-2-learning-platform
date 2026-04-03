"""create_agent_tables

Revision ID: create_agent_tables
Revises: 5720f50cf99a
Create Date: 2026-04-03

"""

import sqlalchemy as sa

from alembic import op

revision = "create_agent_tables"
down_revision = "5720f50cf99a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # AgentSession table
    op.create_table(
        "agent_sessions",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "conversation_history",
            sa.dialects.postgresql.JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column("active_agent", sa.String(30), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "status IN ('active', 'completed', 'abandoned')",
            name="check_agent_session_status",
        ),
    )
    op.create_index("idx_agent_session_user_id", "agent_sessions", ["user_id"])
    op.create_index("idx_agent_session_status", "agent_sessions", ["status"])
    op.create_index("idx_agent_session_updated_at", "agent_sessions", ["updated_at"])

    # RoutingDecision table
    op.create_table(
        "routing_decisions",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "session_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agent_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("intent", sa.String(30), nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("target_agent", sa.String(30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "intent IN ('concept-explanation', 'code-debug', 'code-review', 'exercise-generation', 'progress-summary', 'general')",
            name="check_routing_intent",
        ),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="check_routing_confidence"),
    )
    op.create_index("idx_routing_session_id", "routing_decisions", ["session_id"])
    op.create_index("idx_routing_user_id", "routing_decisions", ["user_id"])
    op.create_index("idx_routing_intent", "routing_decisions", ["intent"])
    op.create_index("idx_routing_created_at", "routing_decisions", ["created_at"])

    # HintProgression table
    op.create_table(
        "hint_progressions",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "session_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agent_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("error_context", sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column("hint_level", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "hints_provided",
            sa.dialects.postgresql.JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column("solution_revealed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("resolved", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint("hint_level BETWEEN 1 AND 3", name="check_hint_level"),
    )
    op.create_index("idx_hint_session_id", "hint_progressions", ["session_id"])
    op.create_index("idx_hint_user_id", "hint_progressions", ["user_id"])
    op.create_index("idx_hint_resolved", "hint_progressions", ["resolved"])

    # Exercise table (agent exercises)
    op.create_table(
        "exercises_agent",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("topic", sa.String(100), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("starter_code", sa.Text, nullable=True),
        sa.Column("test_cases", sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column("solution_code", sa.Text, nullable=True),
        sa.Column("creator", sa.String(20), nullable=False, server_default="system"),
        sa.Column(
            "created_by_user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="check_exercise_difficulty",
        ),
        sa.CheckConstraint("creator IN ('system', 'teacher')", name="check_exercise_creator"),
    )
    op.create_index("idx_exercise_topic", "exercises_agent", ["topic"])
    op.create_index("idx_exercise_difficulty", "exercises_agent", ["difficulty"])
    op.create_index("idx_exercise_creator", "exercises_agent", ["creator"])

    # ExerciseSubmission table
    op.create_table(
        "exercise_submissions",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "exercise_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercises_agent.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("submitted_code", sa.Text, nullable=False),
        sa.Column("test_results", sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("feedback", sa.Text, nullable=True),
        sa.Column("execution_time_ms", sa.Integer, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="check_submission_score"),
    )
    op.create_index("idx_submission_exercise_id", "exercise_submissions", ["exercise_id"])
    op.create_index("idx_submission_user_id", "exercise_submissions", ["user_id"])
    op.create_index("idx_submission_score", "exercise_submissions", ["score"])
    op.create_index("idx_submission_created_at", "exercise_submissions", ["created_at"])

    # MasteryRecord table
    op.create_table(
        "mastery_records",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("topic", sa.String(100), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("component_breakdown", sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="check_mastery_score"),
        sa.CheckConstraint(
            "level IN ('Beginner', 'Learning', 'Proficient', 'Mastered')",
            name="check_mastery_level",
        ),
    )
    op.create_index("idx_mastery_user_id", "mastery_records", ["user_id"])
    op.create_index("idx_mastery_topic", "mastery_records", ["topic"])
    op.create_index("idx_mastery_user_topic", "mastery_records", ["user_id", "topic"], unique=True)


def downgrade() -> None:
    op.drop_table("mastery_records")
    op.drop_table("exercise_submissions")
    op.drop_table("exercises_agent")
    op.drop_table("hint_progressions")
    op.drop_table("routing_decisions")
    op.drop_table("agent_sessions")
