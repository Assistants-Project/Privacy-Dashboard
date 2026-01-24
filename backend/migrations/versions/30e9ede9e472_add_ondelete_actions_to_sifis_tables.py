"""Add ON DELETE actions to SIFIS tables

Revision ID: 30e9ede9e472
Revises: 137febda3b2c
Create Date: 2026-01-24

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "30e9ede9e472"
down_revision = "137febda3b2c"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("dbdetail_action_id_fkey", "dbdetail", type_="foreignkey")
    op.drop_constraint("dbdetail_trigger_id_fkey", "dbdetail", type_="foreignkey")
    op.drop_constraint("dbaction_entity_id_fkey", "dbaction", type_="foreignkey")
    op.drop_constraint("dbaction_rule_id_fkey", "dbaction", type_="foreignkey")
    op.drop_constraint("dbtrigger_entity_id_fkey", "dbtrigger", type_="foreignkey")
    op.drop_constraint("dbtrigger_rule_id_fkey", "dbtrigger", type_="foreignkey")
    op.drop_constraint("dbrule_user_id_fkey", "dbrule", type_="foreignkey")
    op.drop_constraint("dbentity_user_id_fkey", "dbentity", type_="foreignkey")

    op.create_foreign_key(
        "dbentity_user_id_fkey",
        "dbentity",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "dbrule_user_id_fkey",
        "dbrule",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "dbaction_rule_id_fkey",
        "dbaction",
        "dbrule",
        ["rule_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "dbtrigger_rule_id_fkey",
        "dbtrigger",
        "dbrule",
        ["rule_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "dbaction_entity_id_fkey",
        "dbaction",
        "dbentity",
        ["entity_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "dbtrigger_entity_id_fkey",
        "dbtrigger",
        "dbentity",
        ["entity_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "dbdetail_action_id_fkey",
        "dbdetail",
        "dbaction",
        ["action_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "dbdetail_trigger_id_fkey",
        "dbdetail",
        "dbtrigger",
        ["trigger_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("dbdetail_action_id_fkey", "dbdetail", type_="foreignkey")
    op.drop_constraint("dbdetail_trigger_id_fkey", "dbdetail", type_="foreignkey")
    op.drop_constraint("dbaction_entity_id_fkey", "dbaction", type_="foreignkey")
    op.drop_constraint("dbaction_rule_id_fkey", "dbaction", type_="foreignkey")
    op.drop_constraint("dbtrigger_entity_id_fkey", "dbtrigger", type_="foreignkey")
    op.drop_constraint("dbtrigger_rule_id_fkey", "dbtrigger", type_="foreignkey")
    op.drop_constraint("dbrule_user_id_fkey", "dbrule", type_="foreignkey")
    op.drop_constraint("dbentity_user_id_fkey", "dbentity", type_="foreignkey")

    op.create_foreign_key(
        "dbentity_user_id_fkey",
        "dbentity",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "dbrule_user_id_fkey",
        "dbrule",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "dbaction_rule_id_fkey",
        "dbaction",
        "dbrule",
        ["rule_id"],
        ["id"],
    )
    op.create_foreign_key(
        "dbtrigger_rule_id_fkey",
        "dbtrigger",
        "dbrule",
        ["rule_id"],
        ["id"],
    )
    op.create_foreign_key(
        "dbaction_entity_id_fkey",
        "dbaction",
        "dbentity",
        ["entity_id"],
        ["id"],
    )
    op.create_foreign_key(
        "dbtrigger_entity_id_fkey",
        "dbtrigger",
        "dbentity",
        ["entity_id"],
        ["id"],
    )
    op.create_foreign_key(
        "dbdetail_action_id_fkey",
        "dbdetail",
        "dbaction",
        ["action_id"],
        ["id"],
    )
    op.create_foreign_key(
        "dbdetail_trigger_id_fkey",
        "dbdetail",
        "dbtrigger",
        ["trigger_id"],
        ["id"],
    )

