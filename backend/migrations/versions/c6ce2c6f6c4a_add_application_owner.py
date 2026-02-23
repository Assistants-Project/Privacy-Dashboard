"""add application owner

Revision ID: c6ce2c6f6c4a
Revises: 5493e779314f
Create Date: 2026-02-20 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c6ce2c6f6c4a"
down_revision = "5493e779314f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "applications",
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        "fk_applications_owner_user_id_users",
        "applications",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="NO ACTION",
    )


def downgrade():
    op.drop_constraint(
        "fk_applications_owner_user_id_users",
        "applications",
        type_="foreignkey",
    )
    op.drop_column("applications", "owner_user_id")
