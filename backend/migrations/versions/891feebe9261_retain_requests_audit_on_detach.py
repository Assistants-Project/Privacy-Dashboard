"""retain requests audit on detach and consent snapshots

Revision ID: 891feebe9261
Revises: 8a4c2f1d9b3e
Create Date: 2026-03-07 15:45:36.423611

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "891feebe9261"
down_revision = "8a4c2f1d9b3e"
branch_labels = None
depends_on = None


def upgrade():
    # Keep GDPR right requests as audit records even if the DS-home-app relation is pruned.
    # We denormalize the minimal identifiers needed to query requests without joining through
    # user_smart_home_application_relations, we switch the FK behavior to SET NULL,
    # and we store selected consents as request-level snapshots.

    op.add_column(
        "requests",
        sa.Column("data_subject_user_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "requests",
        sa.Column("application_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "requests",
        sa.Column("smart_home_uuid", sa.String(), nullable=True),
    )

    # Backfill from the existing tri-relation and smart_homes table.
    op.execute(
        """
        UPDATE requests r
        SET
            data_subject_user_id = rel.user_id,
            application_id = rel.application_id,
            smart_home_uuid = sh.uuid
        FROM user_smart_home_application_relations rel
        LEFT JOIN smart_homes sh ON sh.id = rel.smart_home_id
        WHERE r.user_smart_home_application_relation_id = rel.id
        """
    )

    op.alter_column("requests", "data_subject_user_id", nullable=False)
    op.alter_column("requests", "application_id", nullable=False)
    op.alter_column("requests", "smart_home_uuid", nullable=False)

    # Make the relation pointer optional and avoid cascading deletes of requests.
    op.alter_column(
        "requests",
        "user_smart_home_application_relation_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.execute(
        "ALTER TABLE requests DROP CONSTRAINT IF EXISTS requests_user_smart_home_application_relation_id_fkey"
    )
    op.create_foreign_key(
        "requests_user_smart_home_application_relation_id_fkey",
        "requests",
        "user_smart_home_application_relations",
        ["user_smart_home_application_relation_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_requests_status_application_id",
        "requests",
        ["status", "application_id"],
        unique=False,
    )

    op.add_column(
        "requests",
        sa.Column(
            "selected_consents_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE requests r
        SET selected_consents_snapshot = (
            SELECT COALESCE(
                jsonb_agg(
                    jsonb_build_object(
                        'uuid', consent_uuid::text,
                        'content', ac.content
                    )
                ),
                '[]'::jsonb
            )
            FROM unnest(r.selected_consents) AS consent_uuid
            LEFT JOIN available_consents ac ON ac.uuid = consent_uuid
        )
        WHERE r.selected_consents IS NOT NULL
        """
    )

    op.drop_column("requests", "selected_consents")
    op.alter_column(
        "requests",
        "selected_consents_snapshot",
        new_column_name="selected_consents",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=True,
    )


def downgrade():
    op.add_column(
        "requests",
        sa.Column(
            "selected_consents_uuids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE requests
        SET selected_consents_uuids = (
            SELECT COALESCE(
                array_agg((entry->>'uuid')::uuid),
                ARRAY[]::uuid[]
            )
            FROM jsonb_array_elements(selected_consents) AS entry
        )
        WHERE selected_consents IS NOT NULL
        """
    )

    op.drop_column("requests", "selected_consents")
    op.alter_column(
        "requests",
        "selected_consents_uuids",
        new_column_name="selected_consents",
        existing_type=postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
        existing_nullable=True,
    )

    op.drop_index("ix_requests_status_application_id", table_name="requests")

    # Downgrade is destructive for audit-only requests that lost their relation.
    op.execute(
        "DELETE FROM requests WHERE user_smart_home_application_relation_id IS NULL"
    )

    op.execute(
        "ALTER TABLE requests DROP CONSTRAINT IF EXISTS requests_user_smart_home_application_relation_id_fkey"
    )
    op.create_foreign_key(
        "requests_user_smart_home_application_relation_id_fkey",
        "requests",
        "user_smart_home_application_relations",
        ["user_smart_home_application_relation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "requests",
        "user_smart_home_application_relation_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_column("requests", "smart_home_uuid")
    op.drop_column("requests", "application_id")
    op.drop_column("requests", "data_subject_user_id")
