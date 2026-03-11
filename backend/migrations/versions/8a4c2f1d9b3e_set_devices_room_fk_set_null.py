"""set devices.room_id FK to SET NULL on room deletion

Revision ID: 8a4c2f1d9b3e
Revises: 7c0a8a2f1c7b
Create Date: 2026-03-07 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "8a4c2f1d9b3e"
down_revision = "7c0a8a2f1c7b"
branch_labels = None
depends_on = None


def upgrade():
    # Default Postgres naming for unnamed FK constraints is "<table>_<column>_fkey".
    # Use IF EXISTS for safety across environments.
    op.execute("ALTER TABLE devices DROP CONSTRAINT IF EXISTS devices_room_id_fkey")
    op.create_foreign_key(
        "devices_room_id_fkey",
        "devices",
        "rooms",
        ["room_id"],
        ["room_id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.execute("ALTER TABLE devices DROP CONSTRAINT IF EXISTS devices_room_id_fkey")
    op.create_foreign_key(
        "devices_room_id_fkey",
        "devices",
        "rooms",
        ["room_id"],
        ["room_id"],
        ondelete="CASCADE",
    )

