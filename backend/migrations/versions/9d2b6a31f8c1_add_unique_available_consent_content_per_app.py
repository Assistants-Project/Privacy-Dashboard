"""add unique available consent content per app

Revision ID: 9d2b6a31f8c1
Revises: 3f1a2b8c9d4e
Create Date: 2026-02-24 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "9d2b6a31f8c1"
down_revision = "3f1a2b8c9d4e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_available_consents_application_id_content",
        "available_consents",
        ["application_id", "content"],
    )


def downgrade():
    op.drop_constraint(
        "uq_available_consents_application_id_content",
        "available_consents",
        type_="unique",
    )
