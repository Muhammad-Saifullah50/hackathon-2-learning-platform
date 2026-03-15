"""seed curriculum with 8 Python modules

Revision ID: 002g_seed_curriculum
Revises: 002f_llm_cache
Create Date: 2026-03-15 06:55:17.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002g_seed_curriculum'
down_revision = '002f_llm_cache'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert 8 Python curriculum modules
    op.execute("""
        INSERT INTO modules (title, description, "order") VALUES
        ('Basics', 'Variables, Data Types, Input/Output, Operators, Type Conversion', 1),
        ('Control Flow', 'Conditionals (if/elif/else), For Loops, While Loops, Break/Continue', 2),
        ('Data Structures', 'Lists, Tuples, Dictionaries, Sets', 3),
        ('Functions', 'Defining Functions, Parameters, Return Values, Scope', 4),
        ('OOP', 'Classes & Objects, Attributes & Methods, Inheritance, Encapsulation', 5),
        ('Files', 'Reading/Writing Files, CSV Processing, JSON Handling', 6),
        ('Errors', 'Try/Except, Exception Types, Custom Exceptions, Debugging', 7),
        ('Libraries', 'Installing Packages, Working with APIs, Virtual Environments', 8);
    """)


def downgrade() -> None:
    # Delete seeded modules
    op.execute("""
        DELETE FROM modules WHERE "order" IN (1, 2, 3, 4, 5, 6, 7, 8);
    """)
