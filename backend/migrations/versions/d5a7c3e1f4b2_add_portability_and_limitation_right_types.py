"""add portability and limitation request right types

Revision ID: d5a7c3e1f4b2
Revises: c2d4e6f8a9b1
Create Date: 2026-03-13 16:20:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "d5a7c3e1f4b2"
down_revision = "c2d4e6f8a9b1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE righttype ADD VALUE IF NOT EXISTS 'PORTABILITY'")
    op.execute("ALTER TYPE righttype ADD VALUE IF NOT EXISTS 'LIMITATION'")


def downgrade():
    # PostgreSQL does not support removing enum labels with a simple safe downgrade.
    pass
