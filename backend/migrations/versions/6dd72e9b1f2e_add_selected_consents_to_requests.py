"""Add selected consents to requests

Revision ID: 6dd72e9b1f2e
Revises: 30e9ede9e472
Create Date: 2026-02-10

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "6dd72e9b1f2e"
down_revision = "30e9ede9e472"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "requests",
        sa.Column(
            "selected_consents",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("requests", "selected_consents")
