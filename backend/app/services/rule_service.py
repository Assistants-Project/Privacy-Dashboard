import logging
import time
from typing import List, Set, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from ..models.entities.sifis.db import DbRule, DbTrigger, DbAction, DbDetail
from ..models.entities.user import User
from ..models.entities.smart_home import SmartHome
from ..models.entities.sifis.owl.trigger import Trigger
from ..models.entities.sifis.owl.action import Action
from ..models.entities.sifis.owl.rule import Rule
from ..repositories.rule_repository import RuleRepository
from ..services.owl_service import OWLService
from ..services.xacml_service import XACMLService
from ..services.dht_service import DHTService
from config import BaseConfig


class RuleService:
    """Service for handling rule business logic"""

    def __init__(self, owl_service: OWLService):
        self.owl_service = owl_service
        self.rule_repo = RuleRepository()

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def save_rule(
        self, rule_data: Dict[str, Any], rule_type: str, smart_home: SmartHome
    ) -> int:
        """
        Save a rule to the database

        Args:
            rule_data: Validated dictionary (from DTO schema) containing trigger, action, effect, subject, timestamp
            rule_type: Type of rule (e.g., 'sifis')
            smart_home: SmartHome where the rule applies

        Returns:
            ID of the saved rule
        """
        # Create DbRule with Unix timestamp in milliseconds
        timestamp = rule_data.get("timestamp")
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        self.logger.info(f"Saving rule with timestamp: {timestamp}")
        
        db_rule = DbRule(
            smart_home_id=smart_home.id,
            type=rule_type,
            effect=rule_data.get("effect"),
            subject=rule_data.get("subject"),
            timestamp=timestamp,
        )

        # Process trigger
        trigger_data = rule_data["trigger"]
        db_trigger = self._process_trigger_data(trigger_data, smart_home)
        
        # Process action
        action_data = rule_data["action"]
        db_action = self._process_action_data(action_data, smart_home)

        # Link trigger and action to rule
        db_rule.triggers.append(db_trigger)
        db_rule.actions.append(db_action)

        # Save to database
        saved_rule = self.rule_repo.save_rule(db_rule)
        return saved_rule.id

    def _process_trigger_data(self, trigger_data: Dict[str, Any], smart_home: SmartHome) -> DbTrigger:
        """Process trigger data and create DbTrigger entity"""
        db_trigger = DbTrigger(url=trigger_data["url"])
        location_url = None

        for detail in trigger_data.get("details", []):
            if detail["type"] == "entity":
                entity_value = detail.get("value", {})
                if entity_value:
                    entity = self.rule_repo.find_or_create_entity(
                        entity_value["url"], smart_home
                    )
                    db_trigger.entity = entity
            elif detail["type"] == "location":
                location_value = detail.get("value", {})
                if location_value:
                    location_url = location_value.get("url")
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
            service_id = self._resolve_service_id(trigger_data, str(smart_home.uuid), is_trigger=True)
            if service_id:
                self._find_and_set_default_entity(db_trigger, service_id, smart_home, location_url)
        
        return db_trigger

    def _process_action_data(self, action_data: Dict[str, Any], smart_home: SmartHome) -> DbAction:
        """Process action data and create DbAction entity"""
        db_action = DbAction(url=action_data["url"])
        location_url = None

        for detail in action_data.get("details", []):
            if detail["type"] == "entity":
                entity_value = detail.get("value", {})
                if entity_value:
                    entity = self.rule_repo.find_or_create_entity(
                        entity_value["url"], smart_home
                    )
                    db_action.entity = entity
            elif detail["type"] == "location":
                location_value = detail.get("value", {})
                if location_value:
                    location_url = location_value.get("url")
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
            service_id = self._resolve_service_id(action_data, str(smart_home.uuid), is_trigger=False)
            if service_id:
                self._find_and_set_default_entity(db_action, service_id, smart_home, location_url)
        
        return db_action

    def _resolve_service_id(self, data: Dict[str, Any], home_uuid: str, is_trigger: bool) -> Optional[str]:
        """Resolve service ID from data or OWL"""
        service_id = data.get("service", {}).get("id")
        if not service_id:
            if is_trigger:
                owl_item = self.owl_service.get_trigger_by_url(data["url"], home_uuid)
            else:
                owl_item = self.owl_service.get_action_by_url(data["url"], home_uuid)
                
            if owl_item and owl_item.service:
                service_id = owl_item.service.id
        return service_id

    def _find_and_set_default_entity(
        self, 
        db_item: Any, 
        service_id: str, 
        smart_home: SmartHome,
        location_url: Optional[str]
    ):
        """Find default entity for service and set it on the db item"""
        entities = self.owl_service._get_entities_by_service(
            service_id, str(smart_home.uuid), location_url=location_url
        )
        if entities:
            entity = self.rule_repo.find_or_create_entity(
                entities[0]["url"], smart_home
            )
            db_item.entity = entity

    def get_rules_by_type(self, rule_type: str, smart_home: SmartHome) -> List[Rule]:
        """
        Get all rules for a home by type

        Args:
            rule_type: Type of rule (e.g., 'sifis')
            smart_home: SmartHome object

        Returns:
            List of Rule objects with populated trigger/action details
        """
        self.logger.info(
            f"Fetching rules of type '{rule_type}' for home '{str(smart_home.uuid)}'"
        )
        db_rules = self.rule_repo.get_rules_by_home_and_type(smart_home, rule_type)
        rules = []

        for db_rule in db_rules:
            try:
                rule = self._rehydrate_rule(db_rule, str(smart_home.uuid))
                if rule:
                    rules.append(rule)
            except Exception as e:
                # Log error but continue processing other rules
                self.logger.error(f"Error processing rule {db_rule.id}: {e}")
                continue

        return rules
    
    def delete_rule_by_home(self, rule_id: int, smart_home: SmartHome) -> bool:
        """
        Delete a rule if it belongs to the specified home.
        
        Args:
            rule_id: ID of the rule to delete
            smart_home: SmartHome object
            
        Returns:
            True if rule was found and deleted, False otherwise
        """
        return self.rule_repo.delete_rule_by_id_and_home(rule_id, smart_home.id)

    def verify_rule_ownership(self, rule_id: int, smart_home: SmartHome) -> bool:
        """Check if a rule exists and belongs to the home"""
        rule = self.rule_repo.get_rule_by_id_and_home(rule_id, smart_home.id)
        return rule is not None

    def get_defined_triggers_by_type(self, rule_type: str, smart_home: SmartHome) -> Set[Trigger]:
        """Get all unique triggers used in rules"""
        rules = self.get_rules_by_type(rule_type, smart_home)
        triggers = set()
        for rule in rules:
            if rule.trigger:
                triggers.add(rule.trigger)
        return triggers
        
    def get_rule_by_id(self, rule_id: int, smart_home: SmartHome) -> Optional[Rule]:
        """Get a single fully rehydrated rule by ID"""
        db_rule = self.rule_repo.get_rule_by_id_and_home(rule_id, smart_home.id)
        if not db_rule:
            return None
            
        return self._rehydrate_rule(db_rule, str(smart_home.uuid))

    def translate_and_publish_rule(
        self, 
        rule_id: int, 
        smart_home: SmartHome,
        xacml_service: XACMLService, 
        dht_service: DHTService
    ) -> bool:
        """
        Refactored: Translate rule to XACML, save to file system, and publish to DHT.
        """
        # 1. Get rehydrated rule
        rule = self.get_rule_by_id(rule_id, smart_home)
        if not rule:
            return False

        # 2. Prepare policies directory
        policies_dir = Path(BaseConfig.POLICIES_DIRECTORY)
        policies_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean existing XML files
        for file in policies_dir.glob("*.xml"):
            file.unlink()

        # 3. Translate rule
        policies_xml = xacml_service.translate(rule.to_dict(), str(smart_home.uuid))

        # 4. Save and Publish
        for i, policy_xml in enumerate(policies_xml):
            timestamp = int(datetime.now().timestamp() * 1000)
            policy_id = f"policy_{timestamp}_{i}"

            # Save to file
            policy_file = policies_dir / f"{policy_id}.xml"
            with open(policy_file, "w", encoding="utf-8") as f:
                f.write(policy_xml)

            # Publish to DHT
            pub_result = dht_service.publish_policy(policy_xml, policy_id)
            if pub_result is None:
                self.logger.warning(f"Failed to publish policy {policy_id} to DHT")
        
        return True

    def _rehydrate_rule(self, db_rule: DbRule, home_uuid: str) -> Optional[Rule]:
        """
        Helper to rehydrate a DbRule into a full Rule object using OWL data.
        """
        try:
            db_trigger = db_rule.triggers[0] if db_rule.triggers else None
            db_action = db_rule.actions[0] if db_rule.actions else None

            if not db_trigger or not db_action:
                return None

            # Get trigger from OWL
            trigger = self.owl_service.get_trigger_by_url(
                db_trigger.url, home_uuid
            )
            if not trigger:
                return None

            self._hydrate_details(trigger, db_trigger, home_uuid)

            # Get action from OWL
            action = self.owl_service.get_action_by_url(db_action.url, home_uuid)
            if not action:
                return None

            self._hydrate_details(action, db_action, home_uuid)

            # Sort details by name
            trigger.details.sort(key=lambda d: d.name)
            action.details.sort(key=lambda d: d.name)

            return Rule(
                db_id=db_rule.id,
                type=db_rule.type,
                effect=db_rule.effect,
                subject=db_rule.subject,
                timestamp=db_rule.timestamp,
                trigger=trigger,
                action=action,
            )

        except Exception as e:
            self.logger.error(f"Error rehydrating rule {db_rule.id}: {e}")
            return None

    def _hydrate_details(self, owl_item: Any, db_item: Any, home_uuid: str):
        """Hydroate entity/location details for a trigger or action."""
        for detail in owl_item.details:
            if detail.type == "entity" and db_item.entity:
                detail.value = self.owl_service.get_entity_by_url(
                    db_item.entity.url, home_uuid
                )
            elif detail.type == "location":
                for db_detail in db_item.details:
                    if detail.url == db_detail.url:
                        detail.value = {
                            "name": db_detail.value,
                            "url": db_detail.value_url,
                        }
            else:
                for db_detail in db_item.details:
                    if detail.url == db_detail.url and detail.type not in [
                        "entity",
                        "location",
                        "service", 
                    ]:
                        detail.value = db_detail.value
