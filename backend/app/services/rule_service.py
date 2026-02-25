import logging
import time
import uuid
import json
from typing import List, Set, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from uuid import UUID

from ..models.entities.sifis.db import DbRule, DbTrigger, DbAction, DbDetail
from ..models.entities.user import User
from ..models.entities.smart_home import SmartHome
from ..models.entities.sifis.owl.trigger import Trigger
from ..models.entities.sifis.owl.action import Action
from ..models.entities.sifis.owl.rule import Rule
from ..repositories.rule_repository import RuleRepository
from ..repositories.device_repository import DeviceRepository
from ..services.owl_service import OWLService
from ..services.xacml_service import XACMLService
from ..services.dht_service import DHTService
from ..integrations.smartotum.client import SmartotumRule
from ..extensions import db
from ..exceptions import (
    WrongUserCredentialsException,
    SmartotumServiceUnavailableException,
    SmartotumTimeoutException,
)

from config import BaseConfig


class RuleService:
    """Service for handling rule business logic"""

    def __init__(self, owl_service: Optional[OWLService] = None):
        self.owl_service = owl_service
        self.rule_repo = RuleRepository()
        self.dht_service = DHTService(BaseConfig.SMARTOTUM_DHT_URL, BaseConfig.SMARTOTUM_RULE_TOPIC)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def save_rule(
        self, rule_data: Dict[str, Any], rule_type: str, smart_home: SmartHome
    ) -> int:
        """
        Save a rule to the database and post to DHT.

        For deny rules, this is treated as an all-or-nothing operation: if target resolution
        or DHT publish fails, we rollback the DB transaction and raise an exception so the
        caller returns an error to the client.
        """
        # Create DbRule with Unix timestamp in milliseconds
        timestamp = rule_data.get("timestamp")
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        self.logger.info(f"Saving rule with timestamp: {timestamp}")
        
        # Generate UUID for the rule
        rule_uuid = str(uuid.uuid4())
        
        # Format Expiration Date to YYYY-MM-DD
        expiration_date = rule_data.get("expirationDate", "")
        if expiration_date:
            try:
                expiration_date = expiration_date.replace("-", "/")
            except:
                pass
        
        db_rule = DbRule(
            smart_home_id=smart_home.id,
            type=rule_type,
            effect=rule_data.get("effect"),
            subject=rule_data.get("subject"),
            timestamp=timestamp,
            rule_uuid=rule_uuid,
            expiration_date=expiration_date
        )

        # Process trigger
        trigger_data = rule_data["trigger"]
        db_trigger = self._process_trigger_data(trigger_data, smart_home)
        
        # Process action(s) - Expand to "All Actions" for the service
        action_data = rule_data["action"]
        original_url = action_data["url"]
        
        actions_to_create = [original_url]
        
        # If OWL Service is available, find all sibling actions for the same service
        if self.owl_service:
            try:
                owl_action = self.owl_service.get_action_by_url(original_url, str(smart_home.uuid))
                if owl_action and owl_action.service:
                    for sibling in owl_action.service.actions:
                        if sibling.url != original_url:
                            actions_to_create.append(sibling.url)
            except Exception as e:
                self.logger.warning(f"Failed to expand actions via OWL: {e}")

        first_db_action = None

        for action_url in actions_to_create:
            # Create data for this action, reusing details (device target)
            current_action_data = action_data.copy()
            current_action_data["url"] = action_url
            
            db_action = self._process_action_data(current_action_data, smart_home)
            db_rule.actions.append(db_action)
            
            if not first_db_action:
                first_db_action = db_action

        # Link trigger to rule
        db_rule.triggers.append(db_trigger)
        # Actions are already appended in the loop
        return self._save_rule_with_optional_dht_publish(
            db_rule=db_rule,
            rule_data=rule_data,
            db_trigger=db_trigger,
            first_db_action=first_db_action,
            rule_uuid=rule_uuid,
            smart_home=smart_home,
        )

    def _post_rule_to_dht(self, rule_data: Dict, db_trigger: DbTrigger, db_action: DbAction, rule_uuid: str, smart_home: SmartHome) -> Tuple[List[str], str]:
        time_start = ""
        time_end = ""
        days = []
        
        for detail in rule_data["trigger"].get("details", []):
            url = detail.get("url", "").lower()
            val = detail.get("value", "")
            
            if "sifis_hour_from_detail" in url:
                time_start = val
            elif "sifis_hour_to_detail" in url:
                time_end = val
            elif "sifis_days_of_week_detail" in url:
                 if isinstance(val, list):
                    days = val
                 elif isinstance(val, str):
                    try:
                        days = json.loads(val)
                    except:
                        days = [val]


        # Derive Target Topic and UUID from Action Details
        target_topic = None
        target_uuid = None
        
        # Prefer using linked device if available
        if db_action and db_action.device:
            target_uuid = str(db_action.device.device_uuid)
            if db_action.device.topic_name:
                target_topic = db_action.device.topic_name
            else:
                raise Exception(f"Linked device has no topic_name for rule {rule_uuid}")
        else:
            action_details = rule_data.get("action", {}).get("details", [])
            for detail in action_details:
                if detail.get("type") == "entity":
                    value = detail.get("value") or {}
                    entity_url = value.get("url", "") if isinstance(value, dict) else ""
                    if entity_url:
                        # Extract UUID from URL fragment (handles "#d-<uuid>" as well)
                        entity_id = entity_url.split("#")[-1].removeprefix("d-")
                        try:
                            device = DeviceRepository.get_device_by_uuid(entity_id)
                        except Exception as e:
                            raise Exception(f"Failed to lookup selected device {entity_id}: {e}") from e

                        if device and device.topic_name:
                            target_uuid = str(device.device_uuid)
                            target_topic = device.topic_name
                        else:
                            raise Exception(f"Selected device {entity_id} not found locally or missing topic_name")
                        break

        # Format Expiration Date to YYYY/MM/DD (Smartotum format)
        expiration_date = rule_data.get("expirationDate", "") or ""
        if expiration_date:
            try:
                expiration_date = str(expiration_date).replace("-", "/")
            except:
                expiration_date = str(expiration_date)
        
        # If no explicit device is present, fan-out via ontology (location-scoped)
        if target_topic and target_uuid:
            targets = [(str(target_topic), str(target_uuid))]
        else:
            location_url, location_name = self._extract_action_location(rule_data)
            targets = self._targets_from_ontology(rule_data, smart_home, rule_uuid, location_url, location_name)

        if not smart_home or not smart_home.uuid:
            raise Exception("Missing smart_home uuid for DHT publish")
        home_uuid = str(smart_home.uuid)
        access_token = None
        try:
            from flask import request
            access_token = request.cookies.get("st_access_token")
        except Exception as e:
            raise Exception("Could not retrieve access token from request context for DHT publish") from e
        if not access_token:
            raise Exception("Access token not found in request cookies for DHT publish")
        
        published_uuids = self._publish_dht_rules_for_targets(
            base_rule_uuid=rule_uuid,
            targets=targets,
            home_uuid=home_uuid,
            access_token=access_token,
            time_start=time_start,
            time_end=time_end,
            days=days,
            expiration_date=expiration_date,
        )
        return published_uuids, access_token

    def _process_trigger_data(self, trigger_data: Dict[str, Any], smart_home: SmartHome) -> DbTrigger:
        """Process trigger data and create DbTrigger entity"""
        db_trigger = DbTrigger(url=trigger_data["url"])
        location_url = None

        for detail in trigger_data.get("details", []):
            if detail["type"] == "entity":
                entity_url = detail.get("value", {}).get("url")
                if entity_url:
                    target_uuid = entity_url.split("#")[-1].removeprefix("d-")
                    device = DeviceRepository.get_device_by_uuid(target_uuid)
                    if device:
                        db_trigger.device_id = device.device_id
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

        
        return db_trigger

    def _process_action_data(self, action_data: Dict[str, Any], smart_home: SmartHome) -> DbAction:
        """Process action data and create DbAction entity"""
        db_action = DbAction(url=action_data["url"])
        location_url = None

        for detail in action_data.get("details", []):
            if detail["type"] == "entity":
                entity_url = detail.get("value", {}).get("url")
                if entity_url:
                     target_uuid = entity_url.split("#")[-1].removeprefix("d-")
                     device = DeviceRepository.get_device_by_uuid(target_uuid)
                     if device:
                         db_action.device_id = device.device_id
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
        Delete a rule from both DHT and DB if it belongs to the specified home.
        
        Args:
            rule_id: ID of the rule to delete
            smart_home: SmartHome object
            
        Returns:
            True if rule was found and deleted, False otherwise
        """
        # Get rule before deletion to retrieve rule_uuid
        rule = self.rule_repo.get_rule_by_id_and_home(rule_id, smart_home.id)
        if not rule:
            return False
        
        # Delete from DHT first
        if rule.rule_uuid:
            try:
                from flask import request
                access_token = request.cookies.get('st_access_token')
                
                if not access_token and request.headers.get('Authorization'):
                    auth_header = request.headers.get('Authorization')
                    if auth_header.startswith('Bearer '):
                        access_token = auth_header.split(' ')[1]

                if access_token:
                    self._delete_dht_rule_with_fanout_support(rule, smart_home, access_token)
                else:
                    self.logger.warning(f"Skipping DHT deletion for rule {rule.rule_uuid}: Access token not found")
            except Exception as e:
                self.logger.warning(f"Failed to delete rule {rule.rule_uuid} from DHT: {e}")
        
        # Delete from DB
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

    def translate_rule(
        self, 
        rule_id: int, 
        smart_home: SmartHome,
        xacml_service: XACMLService
    ) -> Optional[List[str]]:
        """
        Translate rule to XACML and return the XML strings.
        """
        # 1. Get rehydrated rule
        rule = self.get_rule_by_id(rule_id, smart_home)
        if not rule:
            return None

        # 2. Translate rule
        return xacml_service.translate(rule.to_dict(), str(smart_home.uuid))

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
                expiration_date=db_rule.expiration_date,
                trigger=trigger,
                action=action,
            )

        except Exception as e:
            self.logger.error(f"Error rehydrating rule {db_rule.id}: {e}")
            return None

    def _hydrate_details(self, owl_item: Any, db_item: Any, home_uuid: str):
        """Hydroate entity/location details for a trigger or action."""
        for detail in owl_item.details:
            if detail.type == "entity" and db_item.device:
                # Reconstruct entity value from Device
                base_iri = f"http://elite.polito.it/ontologies/sifis-home.owl/{home_uuid}#"
                entity_url = f"{base_iri}{db_item.device.device_uuid}"
                
                detail.value = {
                    "url": entity_url,
                    "name": db_item.device.name,
                    "id": str(db_item.device.device_uuid)
                }
            elif detail.type == "location":
                found = False
                for db_detail in db_item.details:
                    if detail.url == db_detail.url:
                        detail.value = {
                            "name": db_detail.value,
                            "url": db_detail.value_url,
                        }
                        found = True
                        break
                
                if not found and getattr(db_item, 'device', None) and db_item.device.room:
                    # Auto-populate "Location" from linked Device Room
                    base_iri = f"http://elite.polito.it/ontologies/sifis-home.owl/{home_uuid}#"
                    room_url = f"{base_iri}Room_{db_item.device.room.room_uuid}"
                    
                    detail.value = {
                        "name": db_item.device.room.name,
                        "url": room_url
                    }
            else:
                for db_detail in db_item.details:
                    if detail.url == db_detail.url and detail.type not in [
                        "entity",
                        "location",
                        "service", 
                    ]:
                        detail.value = db_detail.value
    def sync_rules_for_home(self, home: SmartHome, smartotum_rules: List["SmartotumRule"], access_token: str = None):
        """
        Full synchronization of rules for a home:
        - Delete local rules not in Smartotum (from both DHT and DB)
        - Create local rules present in Smartotum but not locally
        - Update local rules present in both
        """
        
        # 1. Get all local rules for this home
        local_db_rules = self.rule_repo.get_rules_by_home_and_type(home, "sifis")
        local_rules_map = {r.rule_uuid: r for r in local_db_rules if r.rule_uuid}
        
        # 2. Index Smartotum rules
        smartotum_rules_map = {str(r.rule_uuid): r for r in smartotum_rules}
        
        # 3. Identify Deletions (Local but not in Smartotum)

        for rule_uuid, db_rule in local_rules_map.items():
            if rule_uuid not in smartotum_rules_map:
                if db_rule.effect == 'deny':
                    self.logger.info(f"Sync: Deleting local deny rule {rule_uuid} (not in DHT)")
                    
                    # Delete from DHT first
                    if access_token:
                        try:
                            self.dht_service.delete_rule(
                                rule_uuid=rule_uuid,
                                home_uuid=str(home.uuid),
                                access_token=access_token
                            )
                        except Exception as e:
                            self.logger.warning(f"DHT deletion failed for {rule_uuid}: {e}")
                    
                    # Delete from DB
                    self.rule_repo.delete_rule_by_id_and_home(db_rule.id, home.id)

        # 4. Identify Creations and Updates
        for rule_uuid, s_rule in smartotum_rules_map.items():
            if rule_uuid in local_rules_map:
                try:
                    self.update_rule_from_smartotum(s_rule)
                except Exception as e:
                    self.logger.error(f"Sync: Failed to update rule {rule_uuid}: {e}")
            else:
                try:
                     self.logger.info(f"Sync: Creating new rule {rule_uuid} from DHT")
                     self.create_rule_from_smartotum(home, s_rule)
                except Exception as e:
                    self.logger.error(f"Sync: Failed to create rule {rule_uuid}: {e}")

    def _determine_trigger_type_from_smartotum(self, s_rule: "SmartotumRule") -> Tuple[str, str]:
        """Determine SIFIS trigger URL and type based on Smartotum rule content"""
        namespace = "http://elite.polito.it/ontologies/sifis-home.owl"
        
        if s_rule.days and (s_rule.time_start or s_rule.time_end):
             return f"{namespace}#sifis_weekly_timer_trigger", "weekly"
        elif s_rule.time_start or s_rule.time_end:
             return f"{namespace}#sifis_every_day_trigger", "daily"
        else:
             return f"{namespace}#sifis_always_trigger", "always"

    def create_rule_from_smartotum(self, home: SmartHome, s_rule: "SmartotumRule"):
        """Create a new local rule from Smartotum DHT data"""
        try:
            # 1. Create Rule
            new_rule = DbRule(
                smart_home_id=home.id,
                type="sifis",
                rule_uuid=str(s_rule.rule_uuid),
                timestamp=int(time.time() * 1000),
                effect="deny", 
                subject="anyone",
                expiration_date=s_rule.expiration_date
            )
            
            # 2. Create Trigger (Dynamic Type)
            trigger_url, trigger_type = self._determine_trigger_type_from_smartotum(s_rule)
            db_trigger = DbTrigger(url=trigger_url)
            
            # Add Details based on type
            namespace = "http://elite.polito.it/ontologies/sifis-home.owl"
            
            if trigger_type in ["weekly", "daily"]:
                # Start Time
                if s_rule.time_start:
                    db_trigger.details.append(DbDetail(
                        url=f"{namespace}#sifis_hour_from_detail",
                        type="time",
                        value=s_rule.time_start
                    ))
                
                # End Time
                if s_rule.time_end:
                     db_trigger.details.append(DbDetail(
                        url=f"{namespace}#sifis_hour_to_detail",
                        type="time",
                        value=s_rule.time_end
                    ))
            
            if trigger_type == "weekly":
                # Days
                if s_rule.days:
                    val_str = json.dumps(s_rule.days)
                    db_trigger.details.append(DbDetail(
                        url=f"{namespace}#sifis_days_of_week_detail",
                        type="days",
                        value=val_str
                    ))

            new_rule.triggers.append(db_trigger)

            # 3. Create Actions 
            action_urls = OWLService.get_action_urls_for_device_type(s_rule.target_topic_name)
            
            if not action_urls:
                 self.logger.warning(f"No actions found for topic {s_rule.target_topic_name}, using default.")
                 action_urls = ["http://elite.polito.it/ontologies/sifis-home.owl#sifis_turn_on_lights_action"]

            for action_url in action_urls:
                db_action = DbAction(url=action_url)
                
                # Link to Device via device_id (FK)
                if s_rule.target_uuid:
                    device = DeviceRepository.get_device_by_uuid(s_rule.target_uuid)
                    if device:
                        db_action.device_id = device.device_id

                new_rule.actions.append(db_action)
            
            # Save
            self.rule_repo.save_rule(new_rule)
            self.logger.info(f"Sync: Created rule {new_rule.rule_uuid}")

        except Exception as e:
            self.logger.error(f"Sync: Failed to create rule from Smartotum {s_rule.rule_uuid}: {e}")

    def update_rule_from_smartotum(self, smartotum_rule: "SmartotumRule"):
        """Update local rule details from Smartotum DHT rule data"""
        rule = self.rule_repo.get_rule_by_uuid(str(smartotum_rule.rule_uuid))
        
        if not rule:
            return

        updated = False
        
        # Determine expected trigger type to check for mismatch
        expected_url, expected_type = self._determine_trigger_type_from_smartotum(smartotum_rule)
        
        current_trigger = rule.triggers[0] if rule.triggers else None
        
        mismatch = False
        if not current_trigger:
            mismatch = True
        else:
            if current_trigger.url != expected_url:
                 mismatch = True
        
        if mismatch:
            self.logger.info(f"Sync: Trigger type mismatch for rule {rule.rule_uuid}. Recreating trigger.")
            # Remove old triggers
            rule.triggers.clear()
            
            # Create new trigger
            db_trigger = DbTrigger(url=expected_url)
            namespace = "http://elite.polito.it/ontologies/sifis-home.owl"
            
            if expected_type in ["weekly", "daily"]:
                if smartotum_rule.time_start:
                    db_trigger.details.append(DbDetail(
                        url=f"{namespace}#sifis_hour_from_detail",
                        type="time",
                        value=smartotum_rule.time_start
                    ))
                if smartotum_rule.time_end:
                     db_trigger.details.append(DbDetail(
                        url=f"{namespace}#sifis_hour_to_detail",
                        type="time",
                        value=smartotum_rule.time_end
                    ))
            
            if expected_type == "weekly" and smartotum_rule.days:
                val_str = json.dumps(smartotum_rule.days)
                db_trigger.details.append(DbDetail(
                    url=f"{namespace}#sifis_days_of_week_detail",
                    type="days",
                    value=val_str
                ))
            
            rule.triggers.append(db_trigger)
            updated = True
        
        else:
            # Type matches, just update details
            
            for trigger in rule.triggers:
                for detail in trigger.details:
                    url = detail.url.lower()
                    
                    if "hour_from" in url or "start" in url:
                        if smartotum_rule.time_start and detail.value != smartotum_rule.time_start:
                             detail.value = smartotum_rule.time_start
                             updated = True
                    elif "hour_to" in url or "end" in url:
                         if smartotum_rule.time_end and detail.value != smartotum_rule.time_end:
                             detail.value = smartotum_rule.time_end
                             updated = True
                    elif "days_of_week" in url:
                        if smartotum_rule.days:
                             new_val = json.dumps(smartotum_rule.days)
                             if detail.value != new_val:
                                 detail.value = new_val
                                 updated = True

        # Update Actions
        action_urls = OWLService.get_action_urls_for_device_type(smartotum_rule.target_topic_name)
        
        if not action_urls:
             action_urls = ["http://elite.polito.it/ontologies/sifis-home.owl#sifis_turn_on_lights_action"]

        current_action_urls = [a.url for a in rule.actions]
        
        if len(action_urls) != len(current_action_urls) or set(action_urls) != set(current_action_urls):
             self.logger.info(f"Sync: Action mismatch for rule {rule.rule_uuid}. Recreating actions.")
             # Clear actions
             rule.actions.clear()
             
             for url in action_urls:
                 db_action = DbAction(url=url)
                 
                 # Link to Device via device_id (FK)
                 if smartotum_rule.target_uuid:
                     device = DeviceRepository.get_device_by_uuid(smartotum_rule.target_uuid)
                     if device:
                         db_action.device_id = device.device_id
                     else:
                         self.logger.warning(f"Sync: Device {smartotum_rule.target_uuid} not found locally for rule {smartotum_rule.rule_uuid}")

                 rule.actions.append(db_action)
             updated = True

        # Update Expiration Date
        if smartotum_rule.expiration_date and rule.expiration_date != smartotum_rule.expiration_date:
            rule.expiration_date = smartotum_rule.expiration_date
            updated = True

        if updated:
            self.rule_repo.save_rule(rule)
            self.logger.info(f"Sync: Updated rule {rule.rule_uuid}")
        else:
             self.logger.debug(f"Sync: No updates for rule {rule.rule_uuid}")

    def cleanup_orphaned_rules(self, smart_home: SmartHome, access_token: str = None) -> int:
        """
        Delete rules whose devices no longer exist (device_id is NULL) from both DHT and DB.
        
        Args:
            smart_home: SmartHome object
            access_token: Smartotum access token for DHT deletion (optional)
            
        Returns:
            Number of orphaned rules deleted
        """
        from ..extensions import db
        
        rules_to_delete = []  # Store tuples of (rule_id, rule_uuid)
        
        for rule in smart_home.rules:
            is_orphaned = False
            
            # Check all actions - if any action has no device, rule is orphaned
            for action in rule.actions:
                if action.device is None:
                    self.logger.info(f"Cleanup: Rule {rule.id} has action without device (action url: {action.url})")
                    is_orphaned = True
                    break
            
            if not is_orphaned:
                # Also check triggers (though most triggers are time-based)
                for trigger in rule.triggers:
                    if trigger.device_id is not None and trigger.device is None:
                        self.logger.info(f"Cleanup: Rule {rule.id} has trigger without device (trigger url: {trigger.url})")
                        is_orphaned = True
                        break
            
            if is_orphaned:
                self.logger.info(f"Cleanup: Deleting orphaned rule {rule.id} (rule_uuid: {rule.rule_uuid})")
                rules_to_delete.append((rule.id, rule.rule_uuid))
        
        # Delete orphaned rules
        deleted_count = 0
        for rule_id, rule_uuid in rules_to_delete:
            try:
                # Delete from DHT first
                if rule_uuid and access_token:
                    try:
                        self.dht_service.delete_rule(
                            rule_uuid=str(rule_uuid),
                            home_uuid=str(smart_home.uuid),
                            access_token=access_token
                        )
                    except Exception as e:
                        self.logger.warning(f"DHT deletion failed for {rule_uuid}: {e}")
                
                # Delete from DB
                self.rule_repo.delete_rule_by_id_and_home(rule_id, smart_home.id)
                deleted_count += 1
            except Exception as e:
                self.logger.error(f"Cleanup: Failed to delete orphaned rule {rule_id}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"Cleanup: Deleted {deleted_count} orphaned rule(s)")
            db.session.commit()
        
        return deleted_count

    def update_rule_locations(self, smart_home: SmartHome) -> int:
        """
        Update rule locations to match current device locations.
        
        Args:
            smart_home: SmartHome object
            
        Returns:
            Number of rules updated
        """
        from ..extensions import db
        
        updated_count = 0
        home_uuid = str(smart_home.uuid)
        
        for rule in smart_home.rules:
            rule_updated = False
            
            # Update action locations
            for action in rule.actions:
                if action.device and action.device.room:
                    # Find location detail in action.details
                    for detail in action.details:
                        if detail.type == 'location':
                            # Construct new location URL
                            new_location_url = f"http://elite.polito.it/ontologies/sifis-home.owl/{home_uuid}#location-{action.device.room.room_uuid}"
                            new_location_name = action.device.room.name
                            
                            # Update if changed
                            if detail.value_url != new_location_url:
                                self.logger.info(f"Cleanup: Updating location for rule {rule.id}, action device {action.device.name} -> {new_location_name}")
                                detail.value = new_location_name
                                detail.value_url = new_location_url
                                rule_updated = True
            
            # Update trigger locations (if applicable)
            for trigger in rule.triggers:
                if trigger.device and trigger.device.room:
                    for detail in trigger.details:
                        if detail.type == 'location':
                            new_location_url = f"http://elite.polito.it/ontologies/sifis-home.owl/{home_uuid}#location-{trigger.device.room.room_uuid}"
                            new_location_name = trigger.device.room.name
                            
                            if detail.value_url != new_location_url:
                                self.logger.info(f"Cleanup: Updating location for rule {rule.id}, trigger device {trigger.device.name} -> {new_location_name}")
                                detail.value = new_location_name
                                detail.value_url = new_location_url
                                rule_updated = True
            
            if rule_updated:
                updated_count += 1
        
        if updated_count > 0:
            self.logger.info(f"Cleanup: Updated locations for {updated_count} rule(s)")
            db.session.commit()
        
        return updated_count

    # =========================
    # Internal Helper Functions
    # =========================

    def _save_rule_with_optional_dht_publish(self, *, db_rule: DbRule, rule_data: Dict[str, Any], db_trigger: DbTrigger, first_db_action: Optional[DbAction], rule_uuid: str, smart_home: SmartHome) -> int:
        """Persist rule and (for deny) publish to DHT atomically.

        DB is committed only if DHT publishing succeeds; otherwise we rollback and raise.
        """
        session = db.session
        published_rule_uuids: List[str] = []
        access_token: Optional[str] = None

        try:
            # Save to DB but do not commit yet.
            self.rule_repo.save_rule(db_rule, commit=False)

            if rule_data.get("effect") == "deny":
                if not first_db_action:
                    raise Exception("Missing action for deny rule DHT publish")
                published_rule_uuids, access_token = self._post_rule_to_dht(
                    rule_data, db_trigger, first_db_action, rule_uuid, smart_home
                )

            session.commit()
            return db_rule.id
        except Exception as e:
            session.rollback()

            # Best-effort cleanup: if we already pushed something to DHT, try to delete it.
            try:
                if published_rule_uuids and access_token:
                    for dht_uuid in published_rule_uuids:
                        self.dht_service.delete_rule(
                            rule_uuid=str(dht_uuid),
                            home_uuid=str(smart_home.uuid),
                            access_token=access_token,
                        )
            except Exception as cleanup_exc:
                self.logger.warning(f"Failed DHT cleanup after rollback: {cleanup_exc}")

            # Preserve auth errors so the controller can return 401 (instead of turning it into a 500).
            if isinstance(e, WrongUserCredentialsException):
                raise
            # Preserve Smartotum availability errors so the controller can return 503/504.
            if isinstance(e, (SmartotumServiceUnavailableException, SmartotumTimeoutException)):
                raise
            raise Exception(f"Failed to save rule: {e}") from e

    def _extract_action_location(self, rule_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Extract selected location (url, name) from action details, if present."""
        try:
            for d in (rule_data.get("action") or {}).get("details", []) or []:
                if d.get("type") != "location":
                    continue
                v = d.get("value") or {}
                if isinstance(v, dict):
                    return v.get("url"), v.get("name")
        except Exception:
            pass
        return None, None

    def _targets_from_ontology(self, rule_data: Dict[str, Any], smart_home: SmartHome, rule_uuid: str, location_url: Optional[str], location_name: Optional[str]) -> List[Tuple[str, str]]:
        # For "Unassigned devices" we require a concrete device selection.
        if location_url:
            frag = str(location_url).split("#")[-1]
            if frag == "location-00000000-0000-0000-0000-000000000000":
                raise Exception("Location is Unassigned devices but no device/entity was selected")

        if not self.owl_service:
            raise Exception("OWL service is not available for target resolution")

        action_url = (rule_data.get("action") or {}).get("url")
        if not action_url:
            raise Exception("Missing action.url for target resolution")

        home_uuid_str = str(smart_home.uuid)
        action_obj = Action()
        action_obj.url = str(action_url)
        loc = {"name": location_name or "Entire Home", "url": location_url or ""}

        commands = self.owl_service.get_commands(action_obj, loc, home_uuid_str)
        if not commands:
            raise Exception("No compatible commands/devices found for this action/location")

        targets: List[Tuple[str, str]] = []
        seen: Set[str] = set()
        for cmd in commands:
            ent_url = (cmd.entity or {}).get("url") if hasattr(cmd, "entity") else None
            if not ent_url:
                continue
            ent_id = str(ent_url).split("#")[-1].removeprefix("d-")
            if not ent_id or ent_id in seen:
                continue
            seen.add(ent_id)

            device = DeviceRepository.get_device_by_uuid(ent_id)
            if not device or not device.topic_name:
                raise Exception(f"Device {ent_id} not found locally or missing topic_name")
            targets.append((str(device.topic_name), str(device.device_uuid)))

        if not targets:
            raise Exception("Could not determine any target device(s) for DHT publish")
        return targets

    def _publish_dht_rules_for_targets(self, *, base_rule_uuid: str, targets: List[Tuple[str, str]], home_uuid: str, access_token: str, time_start: str, time_end: str, days: List[Any], expiration_date: str) -> List[str]:
        """Publish one or multiple DHT rules and return the list of rule UUIDs published."""
        if not targets:
            raise Exception("Could not determine any target device(s) for DHT publish")

        published: List[str] = []
        base_uuid = UUID(str(base_rule_uuid))

        def payload_for(topic: str, dev_uuid: str) -> Dict[str, Any]:
            return {
                "target_topic": topic,
                "target_uuid": dev_uuid,
                "time_start": time_start,
                "time_end": time_end,
                "days": days,
                "expiration_date": expiration_date,
            }

        if len(targets) == 1:
            target_topic, target_uuid = targets[0]
            ok = self.dht_service.publish_rule(
                base_rule_uuid,
                payload_for(target_topic, target_uuid),
                home_uuid,
                access_token,
            )
            if not ok:
                raise Exception("Failed to publish rule to DHT")
            return [str(base_rule_uuid)]

        for target_topic, target_uuid in targets:
            child_uuid = str(uuid.uuid5(base_uuid, str(target_uuid)))
            ok = self.dht_service.publish_rule(
                child_uuid,
                payload_for(target_topic, target_uuid),
                home_uuid,
                access_token,
            )
            if not ok:
                # Best-effort rollback of previously published derived rules
                for prev_uuid in published:
                    try:
                        self.dht_service.delete_rule(
                            rule_uuid=str(prev_uuid),
                            home_uuid=str(home_uuid),
                            access_token=access_token,
                        )
                    except Exception as del_exc:
                        self.logger.warning(
                            f"Failed to delete DHT rule {prev_uuid} after publish failure: {del_exc}"
                        )
                raise Exception("Failed to publish derived rule to DHT")
            published.append(child_uuid)

        return published

    def _delete_dht_rule_with_fanout_support(self, rule: DbRule, smart_home: SmartHome, access_token: str) -> None:
        # If the rule doesn't have a concrete device target (typical for "Entire Home"),
        # we may have published one DHT rule per device (uuid5 fan-out). In that case,
        # delete all derived rules as well.
        has_device_target = any(a.device is not None for a in (rule.actions or []))
        if has_device_target:
            self.dht_service.delete_rule(
                rule_uuid=str(rule.rule_uuid),
                home_uuid=str(smart_home.uuid),
                access_token=access_token
            )
        else:
            try:
                base_uuid = UUID(str(rule.rule_uuid))
            except Exception:
                base_uuid = None

            # Optional location scoping (room-level fan-out)
            location_url: Optional[str] = None
            location_name: Optional[str] = None
            try:
                for act in (rule.actions or []):
                    for det in (act.details or []):
                        if det.type == "location" and det.value_url:
                            location_url = det.value_url
                            location_name = det.value
                            break
                    if location_url:
                        break
            except Exception:
                location_url = None
                location_name = None

            devices: List[Any] = []

            # Prefer OWL-based resolution if available (matches what we do in publish).
            if self.owl_service and (rule.actions or []) and str(smart_home.uuid):
                try:
                    action_obj = Action()
                    action_obj.url = str(rule.actions[0].url)
                    loc = {
                        "name": location_name or "Entire Home",
                        "url": location_url or "",
                    }
                    commands = self.owl_service.get_commands(action_obj, loc, str(smart_home.uuid))
                    uuids: Set[str] = set()
                    for cmd in commands:
                        ent_url = (cmd.entity or {}).get("url") if hasattr(cmd, "entity") else None
                        if not ent_url:
                            continue
                        ent_id = str(ent_url).split("#")[-1].removeprefix("d-")
                        if not ent_id:
                            continue
                        uuids.add(ent_id)

                    # We don't need topics here; derived UUIDs are based on the device UUID.
                    if uuids:
                        devices = [{"device_uuid": u} for u in uuids]
                except Exception as e:
                    self.logger.warning(f"OWL-based target resolution failed for DHT delete: {e}")

            if not devices:
                self.logger.warning(
                    f"Skipping derived DHT deletions for rule {rule.rule_uuid}: unable to resolve targets via OWL"
                )
                devices = []

            if base_uuid:
                for d in devices:
                    # d can be a dict (OWL path) or a Device (older path); keep both safe.
                    du = d.get("device_uuid") if isinstance(d, dict) else getattr(d, "device_uuid", None)
                    if not du:
                        continue
                    child_uuid = str(uuid.uuid5(base_uuid, str(du)))
                    try:
                        self.dht_service.delete_rule(
                            rule_uuid=child_uuid,
                            home_uuid=str(smart_home.uuid),
                            access_token=access_token
                        )
                    except Exception as e:
                        self.logger.warning(f"Failed to delete derived DHT rule {child_uuid}: {e}")

            # Also try deleting the base UUID (no-op if it was never published)
            try:
                self.dht_service.delete_rule(
                    rule_uuid=str(rule.rule_uuid),
                    home_uuid=str(smart_home.uuid),
                    access_token=access_token
                )
            except Exception as e:
                self.logger.warning(f"Failed to delete base DHT rule {rule.rule_uuid}: {e}")
