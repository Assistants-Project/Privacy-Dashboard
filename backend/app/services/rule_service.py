import logging
from typing import List, Set, Dict, Any
import time

from ..models.entities.sifis.db import DbRule, DbTrigger, DbAction, DbDetail
from ..models.entities.user import User
from ..models.entities.sifis.owl.trigger import Trigger
from ..models.entities.sifis.owl.action import Action
from ..models.entities.sifis.owl.detail import Detail
from ..models.entities.sifis.owl.rule import Rule
from ..repositories.rule_repository import RuleRepository
from .owl_service import OWLService


class RuleService:
    """Service for handling rule business logic"""

    def __init__(self, owl_service: OWLService):
        self.owl_service = owl_service
        self.rule_repo = RuleRepository()

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def save_rule(self, rule_data: Dict[str, Any], rule_type: str, user: User) -> int:
        """
        Save a rule to the database

        Args:
            rule_data: Validated dictionary (from DTO schema) containing trigger, action, effect, subject, timestamp
            rule_type: Type of rule (e.g., 'sifis')
            user: User creating the rule

        Returns:
            ID of the saved rule
        """
        # Create DbRule with Unix timestamp in milliseconds (like Java's System.currentTimeMillis())
        timestamp = rule_data.get("timestamp")
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        self.logger.info(f"Saving rule with timestamp: {timestamp}")
        db_rule = DbRule(
            user_id=user.id,
            type=rule_type,
            effect=rule_data.get("effect"),
            subject=rule_data.get("subject"),
            timestamp=timestamp,
        )

        # Process trigger
        trigger_data = rule_data["trigger"]
        db_trigger = DbTrigger(url=trigger_data["url"])

        # Process trigger details
        for detail in trigger_data.get("details", []):
            if detail["type"] == "entity":
                entity_value = detail.get("value", {})
                if entity_value:
                    entity = self.rule_repo.find_or_create_entity(
                        entity_value["url"], user
                    )
                    db_trigger.entity = entity
            elif detail["type"] == "location":
                location_value = detail.get("value", {})
                if location_value:
                    db_detail = DbDetail(
                        url=detail.get("url"),
                        type=detail["type"],
                        value=location_value.get("name"),
                        value_url=location_value.get("url"),
                    )
                    db_trigger.details.append(db_detail)
            elif detail.get("value"):
                db_detail = DbDetail(
                    url=detail.get("url"),
                    type=detail["type"],
                    value=str(detail["value"]),
                )
                db_trigger.details.append(db_detail)

        # If no entity specified, try to find default entity for service
        if not db_trigger.entity:
            service_id = trigger_data.get("service", {}).get("id")
            if service_id:
                entities = self.owl_service._get_entities_by_service(
                    service_id, user.email
                )
                if entities:
                    entity = self.rule_repo.find_or_create_entity(
                        entities[0]["url"], user
                    )
                    db_trigger.entity = entity

        # Process action
        action_data = rule_data["action"]
        db_action = DbAction(url=action_data["url"])

        # Process action details
        for detail in action_data.get("details", []):
            if detail["type"] == "entity":
                entity_value = detail.get("value", {})
                if entity_value:
                    entity = self.rule_repo.find_or_create_entity(
                        entity_value["url"], user
                    )
                    db_action.entity = entity
            elif detail["type"] == "location":
                location_value = detail.get("value", {})
                if location_value:
                    db_detail = DbDetail(
                        url=detail.get("url"),
                        type=detail["type"],
                        value=location_value.get("name"),
                        value_url=location_value.get("url"),
                    )
                    db_action.details.append(db_detail)
            elif detail.get("value"):
                db_detail = DbDetail(
                    url=detail.get("url"),
                    type=detail["type"],
                    value=str(detail["value"]),
                )
                db_action.details.append(db_detail)

        # If no entity specified, try to find default entity for service
        if not db_action.entity:
            service_id = action_data.get("service", {}).get("id")
            if service_id:
                entities = self.owl_service._get_entities_by_service(
                    service_id, str(user.uuid)
                )
                if entities:
                    entity = self.rule_repo.find_or_create_entity(
                        entities[0]["url"], user
                    )
                    db_action.entity = entity

        # Link trigger and action to rule
        db_rule.triggers.append(db_trigger)
        db_rule.actions.append(db_action)

        # Save to database
        saved_rule = self.rule_repo.save_rule(db_rule)
        return saved_rule.id

    def get_rules_by_type(self, rule_type: str, user: User) -> List[Rule]:
        """
        Get all rules for a user by type

        Args:
            rule_type: Type of rule (e.g., 'sifis')
            user: User to get rules for

        Returns:
            List of Rule objects with populated trigger/action details
        """
        self.logger.info(
            f"Fetching rules of type '{rule_type}' for user '{user.email}'"
        )
        db_rules = self.rule_repo.get_rules_by_user_and_type(user, rule_type)
        rules = []

        for db_rule in db_rules:
            try:
                db_trigger = db_rule.triggers[0] if db_rule.triggers else None
                db_action = db_rule.actions[0] if db_rule.actions else None

                if not db_trigger or not db_action:
                    continue

                # Get trigger from OWL
                trigger = self.owl_service.get_trigger_by_url(
                    db_trigger.url, user.email
                )
                if not trigger:
                    continue

                # Populate trigger detail values
                for detail in trigger.details:
                    if detail.type == "entity" and db_trigger.entity:
                        detail.value = self.owl_service.get_entity_by_url(
                            db_trigger.entity.url, user.email
                        )
                    elif detail.type == "location":
                        for db_detail in db_trigger.details:
                            if detail.url == db_detail.url:
                                detail.value = {
                                    "name": db_detail.value,
                                    "url": db_detail.value_url,
                                }
                    else:
                        for db_detail in db_trigger.details:
                            if detail.url == db_detail.url and detail.type not in [
                                "entity",
                                "location",
                            ]:
                                detail.value = db_detail.value

                # Get action from OWL
                action = self.owl_service.get_action_by_url(db_action.url, user.email)
                if not action:
                    continue

                # Populate action detail values
                for detail in action.details:
                    if detail.type == "entity" and db_action.entity:
                        detail.value = self.owl_service.get_entity_by_url(
                            db_action.entity.url, user.email
                        )
                    elif detail.type == "location":
                        for db_detail in db_action.details:
                            if detail.url == db_detail.url:
                                detail.value = {
                                    "name": db_detail.value,
                                    "url": db_detail.value_url,
                                }
                    else:
                        for db_detail in db_action.details:
                            if detail.url == db_detail.url and detail.type not in [
                                "entity",
                                "location",
                            ]:
                                detail.value = db_detail.value

                # Sort details by name
                trigger.details.sort(key=lambda d: d.name)
                action.details.sort(key=lambda d: d.name)

                rule = Rule(
                    db_id=db_rule.id,
                    type=db_rule.type,
                    effect=db_rule.effect,
                    subject=db_rule.subject,
                    timestamp=db_rule.timestamp,
                    trigger=trigger,
                    action=action,
                )

                rules.append(rule)

            except Exception as e:
                # Log error but continue processing other rules
                print(f"Error processing rule {db_rule.id}: {e}")
                continue

        return rules
    
    def delete_rule_by_user(self, rule_id: int, user: User) -> bool:
        """
        Delete a rule if it belongs to the specified user.
        
        Args:
            rule_id: ID of the rule to delete
            user: User who must own the rule
            
        Returns:
            True if rule was found and deleted, False otherwise
        """
        return self.rule_repo.delete_rule_by_id_and_user(rule_id, user.id)

    def verify_rule_ownership(self, rule_id: int, user: User) -> bool:
        """Check if a rule exists and belongs to the user"""
        rule = self.rule_repo.get_rule_by_id_and_user(rule_id, user.id)
        return rule is not None

    def get_defined_triggers_by_type(self, rule_type: str, user: User) -> Set[Trigger]:
        """Get all unique triggers used in rules"""
        rules = self.get_rules_by_type(rule_type, user)
        triggers = set()
        for rule in rules:
            triggers.add(rule["trigger"])
        return triggers
