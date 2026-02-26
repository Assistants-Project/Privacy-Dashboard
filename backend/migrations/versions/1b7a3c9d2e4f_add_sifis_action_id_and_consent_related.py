"""add sifis_action_id to available_consents and consent_uuid to dbrule

Revision ID: 1b7a3c9d2e4f
Revises: f2a4c1b7e9d0
Create Date: 2026-02-26 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1b7a3c9d2e4f"
down_revision = "f2a4c1b7e9d0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "available_consents",
        sa.Column("sifis_action_id", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "dbrule",
        sa.Column("consent_uuid", sa.Uuid(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_dbrule_smart_home_id_consent_uuid",
        "dbrule",
        ["smart_home_id", "consent_uuid"],
    )


def downgrade():
    op.drop_constraint("uq_dbrule_smart_home_id_consent_uuid", "dbrule", type_="unique")
    op.drop_column("dbrule", "consent_uuid")
    op.drop_column("available_consents", "sifis_action_id")
