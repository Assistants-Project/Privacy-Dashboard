from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models.entities.sifis.db import DbRule, DbEntity, DbTrigger, DbAction
from ..models.entities.user import User


class RuleRepository:
    """Repository for rule database operations"""

    @staticmethod
    def save_rule(rule: DbRule) -> DbRule:
        """Save a rule to the database"""
        db.session.add(rule)
        db.session.commit()
        db.session.refresh(rule)
        return rule

    @staticmethod
    def get_rules_by_user_and_type(user: User, rule_type: str) -> List[DbRule]:
        """Get all rules for a user by type"""
        stmt = (
            select(DbRule)
            .where(DbRule.user_id == user.id, DbRule.type == rule_type)
            .options(
                joinedload(DbRule.triggers).joinedload(DbTrigger.entity),
                joinedload(DbRule.triggers).joinedload(DbTrigger.details),
                joinedload(DbRule.actions).joinedload(DbAction.entity),
                joinedload(DbRule.actions).joinedload(DbAction.details),
            )
        )
        return list(db.session.execute(stmt).scalars().unique().all())

    @staticmethod
    def delete_rule_by_id_and_user(rule_id: int, user_id: int) -> bool:
        """
        Delete a rule if it belongs to the specified user.
        
        Args:
            rule_id: ID of the rule to delete
            user_id: ID of the user who must own the rule
            
        Returns:
            True if rule was found and deleted, False otherwise
        """
        stmt = select(DbRule).where(
            DbRule.id == rule_id,
            DbRule.user_id == user_id
        )
        rule = db.session.execute(stmt).scalars().first()
        
        if rule:
            db.session.delete(rule)
            db.session.commit()
            return True
            
        return False

    @staticmethod
    def find_or_create_entity(url: str, user: User) -> DbEntity:
        """Find entity by URL and user or create new one"""
        entity = db.session.execute(
            select(DbEntity).where(DbEntity.url == url, DbEntity.user_id == user.id)
        ).scalar_one_or_none()

        if not entity:
            entity = DbEntity(url=url, user_id=user.id)
            db.session.add(entity)
            db.session.flush()

        return entity
