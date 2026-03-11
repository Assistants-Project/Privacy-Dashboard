"""add zip_code and country to smart_homes

Revision ID: 7c0a8a2f1c7b
Revises: 1b7a3c9d2e4f
Create Date: 2026-03-06 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c0a8a2f1c7b"
down_revision = "1b7a3c9d2e4f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("smart_homes", sa.Column("zip_code", sa.String(), nullable=True))
    op.add_column("smart_homes", sa.Column("country", sa.String(), nullable=True))


def downgrade():
    op.drop_column("smart_homes", "country")
    op.drop_column("smart_homes", "zip_code")

