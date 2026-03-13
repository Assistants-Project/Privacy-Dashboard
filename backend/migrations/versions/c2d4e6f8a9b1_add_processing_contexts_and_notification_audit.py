"""add processing contexts and notification audit fields

Revision ID: c2d4e6f8a9b1
Revises: 891feebe9261
Create Date: 2026-03-11 19:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "c2d4e6f8a9b1"
down_revision = "891feebe9261"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "processing_contexts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.Uuid(), nullable=False),
        sa.Column("data_subject_user_id", sa.Integer(), nullable=False),
        sa.Column("data_subject_email", sa.String(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("application_uuid", sa.Uuid(), nullable=False),
        sa.Column("application_name", sa.String(), nullable=False),
        sa.Column("smart_home_uuid", sa.String(), nullable=False),
        sa.Column("user_smart_home_application_relation_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_smart_home_application_relation_id"],
            ["user_smart_home_application_relations.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
        sa.UniqueConstraint(
            "data_subject_user_id",
            "application_id",
            "smart_home_uuid",
            name="uq_processing_context_user_app_home",
        ),
    )

    op.add_column("requests", sa.Column("processing_context_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "requests_processing_context_id_fkey",
        "requests",
        "processing_contexts",
        ["processing_context_id"],
        ["id"],
    )

    op.execute(
        "ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'CONSENT_GRANTED'"
    )
    op.add_column("notifications", sa.Column("sender_email", sa.String(), nullable=True))
    op.add_column("notifications", sa.Column("processing_context_id", sa.Integer(), nullable=True))
    op.add_column(
        "notifications",
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.alter_column("notifications", "sender_id", existing_type=sa.Integer(), nullable=True)
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_sender_id_fkey")
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_application_id_fkey")
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_request_id_fkey")
    op.create_foreign_key(
        "notifications_sender_id_fkey",
        "notifications",
        "users",
        ["sender_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "notifications_application_id_fkey",
        "notifications",
        "applications",
        ["application_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "notifications_request_id_fkey",
        "notifications",
        "requests",
        ["request_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "notifications_processing_context_id_fkey",
        "notifications",
        "processing_contexts",
        ["processing_context_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.execute("ALTER TABLE requests DROP CONSTRAINT IF EXISTS requests_processing_context_id_fkey")
    op.drop_column("requests", "processing_context_id")

    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_processing_context_id_fkey")
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_sender_id_fkey")
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_application_id_fkey")
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_request_id_fkey")
    op.create_foreign_key(
        "notifications_sender_id_fkey",
        "notifications",
        "users",
        ["sender_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "notifications_application_id_fkey",
        "notifications",
        "applications",
        ["application_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "notifications_request_id_fkey",
        "notifications",
        "requests",
        ["request_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column("notifications", "sender_id", existing_type=sa.Integer(), nullable=False)
    op.drop_column("notifications", "payload")
    op.drop_column("notifications", "processing_context_id")
    op.drop_column("notifications", "sender_email")

    op.drop_table("processing_contexts")
