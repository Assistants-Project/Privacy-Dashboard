"""add application title

Revision ID: 3f1a2b8c9d4e
Revises: c6ce2c6f6c4a
Create Date: 2026-02-22 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3f1a2b8c9d4e"
down_revision = "c6ce2c6f6c4a"
branch_labels = None
depends_on = None


def upgrade():
    # No-op: `title` is now defined in the initial schema migration
    # so that it is physically placed after `name` in the `applications` table.
    pass


def downgrade():
    # No-op paired with upgrade().
    pass
