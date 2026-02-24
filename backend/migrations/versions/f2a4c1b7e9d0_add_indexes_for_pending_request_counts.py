"""add indexes for pending request counts

Revision ID: f2a4c1b7e9d0
Revises: 9d2b6a31f8c1
Create Date: 2026-02-24 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "f2a4c1b7e9d0"
down_revision = "9d2b6a31f8c1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_requests_status_user_smart_home_application_relation_id",
        "requests",
        ["status", "user_smart_home_application_relation_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_smart_home_application_relations_application_id",
        "user_smart_home_application_relations",
        ["application_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_user_smart_home_application_relations_application_id",
        table_name="user_smart_home_application_relations",
    )
    op.drop_index(
        "ix_requests_status_user_smart_home_application_relation_id",
        table_name="requests",
    )
