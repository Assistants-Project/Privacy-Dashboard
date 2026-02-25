from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models.entities.sifis.db import DbRule, DbTrigger, DbAction
from ..models.entities.user import User
from ..models.entities.smart_home import SmartHome


class RuleRepository:
    """Repository for rule database operations"""

    @staticmethod
    def save_rule(rule: DbRule, *, commit: bool = True) -> DbRule:
        """Save a rule to the database.

        commit=True keeps backwards-compatible behavior (commit immediately).
        commit=False only flushes (so ids are assigned) and leaves transaction control
        to the caller (service layer).
        """
        db.session.add(rule)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(rule)
        return rule

    @staticmethod
    def get_rules_by_home_and_type(smart_home: SmartHome, rule_type: str) -> List[DbRule]:
        """Get all rules for a home by type"""
        stmt = (
            select(DbRule)
            .where(DbRule.smart_home_id == smart_home.id, DbRule.type == rule_type)
            .options(
                joinedload(DbRule.triggers).joinedload(DbTrigger.device),
                joinedload(DbRule.triggers).joinedload(DbTrigger.details),
                joinedload(DbRule.actions).joinedload(DbAction.device),
                joinedload(DbRule.actions).joinedload(DbAction.details),
            )
        )
        return list(db.session.execute(stmt).scalars().unique().all())

    @staticmethod
    def delete_rule_by_id_and_home(rule_id: int, smart_home_id: int) -> bool:
        """
        Delete a rule if it belongs to the specified home.
        
        Args:
            rule_id: ID of the rule to delete
            smart_home_id: ID of the home where the rule belongs
            
        Returns:
            True if rule was found and deleted, False otherwise
        """
        stmt = select(DbRule).where(
            DbRule.id == rule_id,
            DbRule.smart_home_id == smart_home_id
        )
        rule = db.session.execute(stmt).scalars().first()
        
        if rule:
            db.session.delete(rule)
            db.session.commit()
            return True
            
        return False

    @staticmethod
    def get_rule_by_id_and_home(rule_id: int, smart_home_id: int) -> Optional[DbRule]:
        """Get a rule by ID ensuring it belongs to the home"""
        stmt = select(DbRule).where(
            DbRule.id == rule_id,
            DbRule.smart_home_id == smart_home_id
        )
        return db.session.execute(stmt).scalars().first()

    @staticmethod
    def get_rule_by_uuid(rule_uuid: str) -> Optional[DbRule]:
        """Get a rule by its UUID"""
        stmt = select(DbRule).where(DbRule.rule_uuid == rule_uuid)
        return db.session.execute(stmt).scalars().first()
