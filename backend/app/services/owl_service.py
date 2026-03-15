# owl_service.py
import os
import yaml
import logging
from pathlib import Path
from typing import Set, Dict, List, Optional
from uuid import UUID
from owlready2 import *
from dataclasses import dataclass
from flask import current_app

from ..models.entities.sifis.owl.action import Action
from ..models.entities.sifis.owl.command import Command
from ..models.entities.sifis.owl.service import Service
from ..models.entities.sifis.owl.trigger import Trigger
from ..models.entities.sifis.owl.detail import Detail


class OWLService:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        self._locations_cache = {}
        self._initialize_ontology()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        level = self.config.get("LOGGING_LEVEL", "INFO")

        logger = logging.getLogger(__name__)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, level))

        return logger

    def _initialize_ontology(self):
        """Load ontology and initialize reasoner"""
        ontology_dir = Path(self.config.get("ONTOLOGY_DIRECTORY", "app/ontologies/"))
        ontology_path = ontology_dir / self.config.get("ONTOLOGY_SIFIS_FILE", "sifis-home.owl")

        if not ontology_path.exists():
            raise FileNotFoundError(
                f"Ontology file not found: {ontology_path.absolute()}"
            )

        self.logger.info(f"Loading ontology from: {ontology_path}")

        # Load with isolated world to handle imports properly
        from owlready2 import World

        world = World()

        # Pre-load EU-PONT ontology
        eupont_path = ontology_dir / "eupont.owl"
        if eupont_path.exists():
            world.get_ontology(f"file://{eupont_path.absolute()}").load()

        # Load SIFIS ontology
        ontology_iri = f"file://{ontology_path.absolute()}"
        self.onto = world.get_ontology(ontology_iri).load(only_local=True)
        self.world = world

        self.sifis_ns = self.onto.get_namespace(
            "http://elite.polito.it/ontologies/sifis-home.owl#"
        )
        self.eupont_ns = self.onto.get_namespace(
            "http://elite.polito.it/ontologies/eupont.owl#"
        )

        self._setup_reasoner()

        self.logger.info("Ontology initialized successfully")

    def _setup_reasoner(self):
        """Initialize HermiT reasoner with precomputed inferences"""
        self.logger.info("Initializing HermiT reasoner with precomputed inferences")

        # Use the world if available, otherwise the ontology
        target = self.world if hasattr(self, "world") else self.onto

        if hasattr(self, "world"):
            sync_reasoner_hermit(target, infer_property_values=True)
        else:
            with target:
                sync_reasoner_hermit(infer_property_values=True)

    def get_trigger_services(self, home_uuid: Optional[str] = None) -> List[Service]:
        """Get all services that offer triggers, optionally filtered by home capabilities"""
        services = []

        try:
            if not self.onto or not self.eupont_ns:
                return services
            
            # Setup filtering if home_uuid is provided
            allowed_uris = set()
            if home_uuid:
                home_world = self._get_home_world(str(home_uuid))
                if home_world:
                    # Collect all allowTo targets from all individuals in the home
                    for ind in home_world.individuals():
                        # allowTo is an ObjectProperty, so it returns a list of individuals
                        allowed_targets = getattr(ind, "allowTo", [])
                        for target in allowed_targets:
                            # Use .iri to get the full URI string
                            if hasattr(target, "iri"):
                                allowed_uris.add(str(target.iri))

            Channel = getattr(self.eupont_ns, "Channel", None)
            if not Channel:
                return services

            for subclass in Channel.subclasses():
                temp_services = []
                has_triggers = False

                for instance in subclass.instances():
                    offered_triggers = getattr(instance, "offerTrigger", [])
                    if offered_triggers:
                        # If filtering is enabled, check if any offered trigger is in the allowed set
                        if home_uuid:
                            is_allowed = False
                            for trigger in offered_triggers:
                                if str(trigger.iri) in allowed_uris:
                                    is_allowed = True
                                    break
                            if not is_allowed:
                                continue

                        has_triggers = True
                        temp_services.append(
                            self._create_service_from_instance(instance, "Triggers")
                        )

                if has_triggers:
                    services.extend(temp_services)

            return services

        except Exception as e:
            self.logger.error(f"Error getting trigger services: {e}")
            return []

    def get_action_services(self, home_uuid: Optional[str] = None) -> List[Service]:
        """Get all services that offer actions, optionally filtered by home capabilities"""
        services = []

        try:
            if not self.onto or not self.eupont_ns:
                return services

            # Setup filtering if home_uuid is provided
            allowed_uris = set()
            if home_uuid:
                home_world = self._get_home_world(str(home_uuid))
                if home_world:
                     # Collect all allowTo targets from all individuals in the home
                    for ind in home_world.individuals():
                        allowed_targets = getattr(ind, "allowTo", [])
                        for target in allowed_targets:
                            if hasattr(target, "iri"):
                                allowed_uris.add(str(target.iri))

            Channel = getattr(self.eupont_ns, "Channel", None)
            if not Channel:
                return services

            for subclass in Channel.subclasses():
                temp_services = []
                has_actions = False

                for instance in subclass.instances():
                    offered_actions = getattr(instance, "offerAction", [])
                    if offered_actions:
                         # If filtering is enabled, check if any offered action is in the allowed set
                        if home_uuid:
                            is_allowed = False
                            for action in offered_actions:
                                if str(action.iri) in allowed_uris:
                                    is_allowed = True
                                    break
                            if not is_allowed:
                                continue

                        has_actions = True
                        temp_services.append(
                            self._create_service_from_instance(instance, "Actions")
                        )

                if has_actions:
                    services.extend(temp_services)

            return services

        except Exception as e:
            self.logger.error(f"Error getting action services: {e}")
            return []

    def get_triggers(self, service_id: str, username: Optional[str] = None) -> List[Trigger]:
        """Get all triggers for a specific service"""
        triggers = []

        try:
            if not self.onto or not self.sifis_ns:
                return triggers

            service_instance = getattr(self.sifis_ns, service_id, None)
            if not service_instance:
                return triggers

            service = self._create_service_from_instance(service_instance, "Triggers")
            offered_triggers = getattr(service_instance, "offerTrigger", [])

            for trigger_instance in offered_triggers:
                trigger_name = (
                    self._safe_get_property(trigger_instance, "label")
                    or self._safe_get_property(trigger_instance, "name")
                    or trigger_instance.name
                )

                trigger = Trigger(
                    url=str(trigger_instance.iri),
                    id=trigger_instance.name,
                    name=trigger_name,
                    description=self._safe_get_property(
                        trigger_instance, "description"
                    ),
                    service=service,
                )

                trigger.details = self._get_details_for_instance(
                    trigger_instance, service_id, is_action=False
                )
                triggers.append(trigger)

            return triggers

        except Exception as e:
            self.logger.error(f"Error getting triggers for service {service_id}: {e}")
            return []

    def _get_details_for_instance(
        self, instance, service_id: str, is_action: bool = False, home_uuid: Optional[str] = None
    ) -> List[Detail]:
        """Get configuration details/parameters for a trigger or action instance."""
        details = []

        try:
            offered_details = getattr(instance, "offerDetail", [])
            has_entity_detail = False

            for detail_instance in offered_details:
                detail_name = (
                    self._safe_get_property(detail_instance, "name")
                    or detail_instance.name
                )
                detail_type = self._safe_get_property(detail_instance, "type")

                detail = Detail(
                    url=str(detail_instance.iri),
                    id=detail_instance.name,
                    name=detail_name,
                    type=detail_type,
                )

                if detail_type == "entity":
                    has_entity_detail = True
                    detail.alternatives = self._get_entities_by_service(
                        service_id, home_uuid=home_uuid
                    )
                elif detail_type == "location":
                    # Do not filter locations by action capability.
                    # We allow selecting any room (or Entire Home) and decide applicability later.
                    detail.alternatives = self._get_locations(home_uuid=home_uuid, action_id=None)
                else:
                    detail.alternatives = []

                details.append(detail)

            # Add implicit entity detail if needed
            if not has_entity_detail:
                entities = self._get_entities_by_service(service_id, home_uuid=home_uuid)
                if entities:
                    details.append(
                        Detail(
                            url="entity_detail",
                            id="entity_detail",
                            name="Device",
                            type="entity",
                            alternatives=entities,
                        )
                    )

            return details

        except Exception as e:
            self.logger.error(f"Error getting details for {instance.name}: {e}")
            return []

    def get_trigger_details(
        self, service_id: str, trigger_id: str, home_uuid: Optional[str] = None
    ) -> List[Detail]:
        """Get configuration details/parameters for a specific trigger."""
        try:
            if not self.onto or not self.sifis_ns:
                return []

            trigger_instance = getattr(self.sifis_ns, trigger_id, None)
            if not trigger_instance:
                return []

            return self._get_details_for_instance(
                trigger_instance, service_id, is_action=False, home_uuid=home_uuid
            )

        except Exception as e:
            self.logger.error(f"Error getting trigger details: {e}")
            return []

    def get_action_details(
        self, service_id: str, action_id: str, home_uuid: Optional[str] = None
    ) -> List[Detail]:
        """Get configuration details/parameters for a specific action."""
        try:
            if not self.onto or not self.sifis_ns:
                return []

            action_instance = getattr(self.sifis_ns, action_id, None)
            if not action_instance:
                return []

            return self._get_details_for_instance(
                action_instance, service_id, is_action=True, home_uuid=home_uuid
            )

        except Exception as e:
            self.logger.error(f"Error getting action details: {e}")
            return []

    def _get_entities_by_service(
        self,
        service_id: str,
        home_uuid: Optional[str] = None,
        location_url: Optional[str] = None,
    ) -> List[Dict]:
        """Get IoT entities/devices that provide a specific service."""
        if not home_uuid:
            return []

        try:
            # Load home world
            home_world = self._get_home_world(home_uuid)
            if not home_world:
                return []

            # Determine Service Class from service_id (generic mapping)

            service_class_name = None
            for key, cls_name in self.SERVICE_CLASS_MAPPING.items():
                if key in service_id:
                    service_class_name = cls_name
                    break
            
            # Find all individuals that have a service of this type
            entities = []
            
            # Prepare device name mapping for user-friendly display
            device_name_map = {}
            try:
                from ..models.entities.smart_home import SmartHome
                home = SmartHome.query.filter_by(uuid=home_uuid).first()
                if home:
                    # Map device UUID (string) to Name - use device_uuid not device_id
                    device_name_map = {str(d.device_uuid): d.name for d in home.devices}
            except Exception as e:
                self.logger.warning(f"Failed to load device names from DB: {e}")

            # If we found a mapping, use class-based lookup
            if service_class_name:
                 ServiceClass = self._get_class(self.onto, service_class_name)
                 
                 # Get IRI of the service class for robust comparison
                 service_class_iri = ServiceClass.iri if ServiceClass else None
                 
                 if service_class_iri:
                     for individual in home_world.individuals():
                         # Check services
                         services = getattr(individual, "hasService", [])
                         has_service = False
                         for s in services:
                             # Check if any of the classes in s.is_a matches the ServiceClass IRI
                             for cls in s.is_a:
                                 if hasattr(cls, 'iri') and cls.iri == service_class_iri:
                                     has_service = True
                                     break
                             if has_service:
                                 break
                         
                         if has_service:
                             # Get Location
                             positions = getattr(individual, "position", [])
                             loc_iri = str(positions[0].iri) if positions else None
                             
                             # Filter by location if requested
                             if location_url and loc_iri != location_url:
                                 continue
                             
                             # Determine Name
                             ind_name = individual.name
                             device_uuid = ind_name.removeprefix("d-") if ind_name.startswith("d-") else ind_name
                             
                             friendly_name = device_name_map.get(device_uuid)
                             
                             final_name = friendly_name or ind_name
                                 
                             entities.append(
                                 {
                                     "url": str(individual.iri),
                                     "name": final_name,
                                     "id": individual.name,
                                     "location_url": loc_iri,
                                 }
                             )
            
            # Fallback to direct IRI matching (for specific services or backwards compat)
            else:
                service_iri = f"http://elite.polito.it/ontologies/sifis-home.owl/{home_uuid}#{service_id}"
                for individual in home_world.individuals():
                    services = getattr(individual, "hasService", [])
                    for service in services:
                        if str(service.iri) == service_iri:
                            # If location filtering is requested, check position
                            positions = getattr(individual, "position", [])
                            loc_iri = str(positions[0].iri) if positions else None
                            
                            if location_url and loc_iri != location_url:
                                continue
    
                            entities.append(
                                {
                                    "url": str(individual.iri),
                                    "name": self._safe_get_property(individual, "id")
                                    or self._safe_get_property(individual, "name")
                                    or individual.name,
                                    "id": individual.name,
                                    "location_url": loc_iri
                                }
                            )
                            break

            return entities
        except Exception as e:
            self.logger.error(f"Error getting entities for service {service_id}: {e}")
            return []

    def _get_locations(self, home_uuid: Optional[str] = None, action_id: Optional[str] = None) -> List[Dict]:
        """Get locations from home's ontology, optionally filtered by Action/Trigger capability (allowTo)."""
        if not home_uuid:
            return []

        # Check cache with composite key
        cache_key = (home_uuid, action_id)
        if cache_key in self._locations_cache:
            return self._locations_cache[cache_key]

        try:
            ontology_dir = Path(self._get_ontology_dir())
            home_ontology_path = ontology_dir / "homes" / f"{home_uuid}.owl"

            if not home_ontology_path.exists():
                return []

            # Load home ontology in separate world
            from owlready2 import World

            home_world = World()

            # Pre-load imported ontologies to avoid web downloads
            eupont_path = ontology_dir / "eupont.owl"
            sifis_path = ontology_dir / "sifis-home.owl"

            if eupont_path.exists():
                home_world.get_ontology(f"file://{eupont_path.absolute()}").load()
            if sifis_path.exists():
                home_world.get_ontology(f"file://{sifis_path.absolute()}").load(
                    only_local=True
                )

            # Load home ontology
            home_onto = home_world.get_ontology(
                f"file://{home_ontology_path.absolute()}"
            ).load()

            # Run reasoner
            sync_reasoner_hermit(home_world, infer_property_values=True)

            # Find Location class
            Location = None
            for cls in home_world.classes():
                if cls.name == "Location":
                    Location = cls
                    break

            if not Location:
                return []

            # Filter Logic: If action_id is provided, find valid location IRIs via object traversal
            valid_location_iris = set()
            should_filter = False
            
            if action_id:
                should_filter = True
                
                # Resolve Action IRI
                action_iri = None
                candidates = list(home_world.search(iri=f"*{action_id}"))
                if candidates:
                    action_iri = candidates[0].iri

                # Helper to safely get list of values
                def get_props(obj, prop_name):
                     vals = getattr(obj, prop_name, [])
                     if vals and not isinstance(vals, list):
                         return [vals]
                     return vals

                # Iterate through all individuals to find devices allowing this action
                for ind in home_world.individuals():
                    # Get Services of the Device
                    services = get_props(ind, "hasService")
                    if not services:
                        services = get_props(ind, "eupont_hasService")

                    is_device_valid = False
                    for service in services:
                        # Get Commands of the Service
                        commands = get_props(service, "hasCommand")
                        if not commands:
                            commands = get_props(service, "eupont_hasCommand")
                            
                        for cmd in commands:
                            # Get allowTo of the Command
                            allowed_targets = get_props(cmd, "allowTo")
                            if not allowed_targets:
                                allowed_targets = get_props(cmd, "eupont_allowTo")
                                
                            for target in allowed_targets:
                                t_iri = str(getattr(target, 'iri', ''))
                                t_name = str(getattr(target, 'name', ''))
                                
                                if action_iri and t_iri == action_iri:
                                    is_device_valid = True
                                elif t_name == action_id or t_iri.endswith(f"#{action_id}"):
                                    is_device_valid = True
                                
                                if is_device_valid:
                                    break
                            if is_device_valid:
                                break
                        if is_device_valid:
                            break
                    
                    if is_device_valid:
                        positions = get_props(ind, "position")
                        if not positions:
                            positions = get_props(ind, "eupont_position")
                            
                        for pos in positions:
                            if hasattr(pos, "iri"):
                                valid_location_iris.add(str(pos.iri))
                                        
            # Get location instances
            locations = []
            for loc_instance in Location.instances(home_world):
                loc_iri = str(loc_instance.iri)
                frag = loc_iri.split("#")[-1]
                
                # Apply Filter
                if should_filter and loc_iri not in valid_location_iris:
                    continue

                display_name = self._safe_get_property(loc_instance, "name") or loc_instance.name
                if frag == "location-home":
                    display_name = "Entire Home"

                locations.append(
                    {
                        "url": loc_iri,
                        "name": display_name,
                    }
                )

            # Cache the result
            self._locations_cache[cache_key] = locations

            return locations

        except Exception as e:
            self.logger.error(f"Error getting locations: {e}")
            return []

    def _safe_get_property(self, instance, property_name: str) -> Optional[str]:
        """Safely get string property from instance with localized literal support."""
        try:
            # Search for the property in the ontology world
            props = list(self.onto.world.search(iri=f"*#{property_name}"))
            if props:
                prop = props[0]
                values = prop._get_values_for_individual(instance)

                if values:
                    # Prefer English localized literals
                    for val in values:
                        if hasattr(val, "lang") and val.lang == "en":
                            return str(val)
                    # Fall back to any localized literal
                    for val in values:
                        if hasattr(val, "lang"):
                            return str(val)
                    # Fall back to first value
                    return str(values[0])

            # Fallback: direct attribute access
            value = getattr(instance, property_name, None)
            if value and isinstance(value, list):
                return str(value[0]) if value else None
            elif value:
                return str(value)

            return None

        except Exception as e:
            self.logger.debug(f"Error getting property {property_name}: {e}")
            return None

    @staticmethod
    def _safe_set_localized_property(onto, instance, property_name: str, value: str, lang: str = "en"):
        """Safely set a localized property on an instance using Owlready's internal API.
        
        This method avoids conflicts with Owlready's special handling of 'name' as an IRI identifier.
        """
        try:
            # Search for the property in the ontology world
            props = list(onto.world.search(iri=f"*#{property_name}"))
            if props:
                prop = props[0]
                # Use internal Owlready API to set the value with language tag
                from owlready2 import locstr
                localized_value = locstr(value, lang)
                # Set the value by directly assigning the list
                setattr(instance, prop.python_name, [localized_value])
                return True
            return False
        except Exception as e:
            print(f"Error setting property {property_name} on {instance}: {e}")
            return False

    def get_actions(self, service_id: str, username: Optional[str] = None) -> List[Action]:
        """Get all actions for a specific service"""
        actions = []

        try:
            if not self.onto or not self.sifis_ns:
                return actions

            service_instance = getattr(self.sifis_ns, service_id, None)
            if not service_instance:
                return actions

            service = self._create_service_from_instance(service_instance, "Actions")
            offered_actions = getattr(service_instance, "offerAction", [])

            for action_instance in offered_actions:
                # Try label first (standard RDF), then name, then fall back to ID
                action_name = (
                    self._safe_get_property(action_instance, "label")
                    or self._safe_get_property(action_instance, "name")
                    or action_instance.name
                )

                action = Action(
                    url=str(action_instance.iri),
                    id=action_instance.name,
                    name=action_name,
                    description=self._safe_get_property(action_instance, "description"),
                    service=service,
                )

                action.details = self._get_details_for_instance(
                    action_instance, service_id, is_action=True
                )
                actions.append(action)

            return actions

        except Exception as e:
            self.logger.error(f"Error getting actions for service {service_id}: {e}")
            return []

    def _create_service_from_instance(self, instance, suffix: str = "") -> Service:
        """Helper method to create Service object from ontology instance"""
        # Try to get human-readable name from ontology first
        name = self._safe_get_property(instance, "name")

        # If no name in ontology, use the instance ID
        if not name:
            name = instance.name

        # Add suffix if provided
        if suffix:
            name = f"{name} {suffix}"

        return Service(
            url=str(instance.iri),
            id=instance.name,
            name=name,
            web_id=self._safe_get_int_property(instance, "id"),
            color=self._safe_get_property(instance, "color"),
            image=self._safe_get_property(instance, "image"),
        )

    def _safe_get_int_property(self, instance, property_name: str) -> Optional[int]:
        """Safely get integer property from instance"""
        try:
            value = getattr(instance, property_name, [])
            if isinstance(value, list) and len(value) > 0:
                return int(value[0]) if value[0] is not None else None
            elif value:
                return int(value)
            return None
        except (ValueError, TypeError, IndexError):
            return None

    def get_trigger_by_url(self, url: str, home_uuid: str) -> Optional[Trigger]:
        """Get trigger by url"""
        try:
            # Extract trigger ID from url
            trigger_id = url.split("#")[-1]
            trigger_instance = getattr(self.sifis_ns, trigger_id, None)

            if not trigger_instance:
                return None

            trigger_name = (
                self._safe_get_property(trigger_instance, "name")
                or trigger_instance.name
            )
            service_instance = getattr(trigger_instance, "isOfChannel", [None])[0]

            trigger = Trigger(
                url=url,
                id=trigger_id,
                name=trigger_name,
                description=self._safe_get_property(trigger_instance, "description"),
            )

            if service_instance:
                trigger.service = self._create_service_from_instance(
                    service_instance, "Triggers"
                )

            trigger.details = self._get_details_for_instance(
                trigger_instance,
                service_instance.name if service_instance else "",
                is_action=False,
                home_uuid=home_uuid
            )

            return trigger
        except Exception as e:
            self.logger.error(f"Error getting trigger by url {url}: {e}")
            return None

    def get_action_by_url(self, url: str, home_uuid: str) -> Optional[Action]:
        """Get action by url"""
        try:
            # Extract action ID from url
            action_id = url.split("#")[-1]
            action_instance = getattr(self.sifis_ns, action_id, None)

            if not action_instance:
                return None

            action_name = (
                self._safe_get_property(action_instance, "name") or action_instance.name
            )
            service_instance = getattr(action_instance, "isOfChannel", [None])[0]

            action = Action(
                url=url,
                id=action_id,
                name=action_name,
                description=self._safe_get_property(action_instance, "description"),
            )

            if service_instance:
                action.service = self._create_service_from_instance(
                    service_instance, "Actions"
                )

            action.details = self._get_details_for_instance(
                action_instance,
                service_instance.name if service_instance else "",
                is_action=True,
                home_uuid=home_uuid
            )

            return action
        except Exception as e:
            self.logger.error(f"Error getting action by url {url}: {e}")
            return None

    def get_entity_by_url(self, url: str, home_uuid: str) -> Optional[Dict]:
        """Get IoT entity by url"""
        try:
            # Extract entity ID from url
            entity_id = url.split("#")[-1]

            # Try to find in home ontology
            home_world = self._get_home_world(home_uuid)
            if not home_world:
                return None

            # Search for the entity
            for individual in home_world.individuals():
                if str(individual.iri) == url:
                    return {
                        "url": url,
                        "name": self._safe_get_property(individual, "name")
                        or individual.name,
                        "id": entity_id,
                    }

            return None
        except Exception as e:
            self.logger.error(f"Error getting entity by url {url}: {e}")
            return None

    def _get_home_world(self, home_uuid: str):
        """Load home world"""
        try:
            ontology_dir = Path(self._get_ontology_dir())
            home_ontology_path = ontology_dir / "homes" / f"{home_uuid}.owl" 
                       
            if not home_ontology_path.exists():
                return None

            from owlready2 import World

            home_world = World()

            # Pre-load imported ontologies
            eupont_path = ontology_dir / "eupont.owl"
            sifis_path = ontology_dir / "sifis-home.owl"

            if eupont_path.exists():
                home_world.get_ontology(f"file://{eupont_path.absolute()}").load()
            if sifis_path.exists():
                home_world.get_ontology(f"file://{sifis_path.absolute()}").load(
                    only_local=True
                )

            home_world.get_ontology(f"file://{home_ontology_path.absolute()}").load()

            return home_world
        except Exception as e:
            self.logger.error(f"Error loading user world for {home_uuid}: {e}")
            return None

    def get_commands(
        self, action: Action, location: Dict, home_uuid: str
    ) -> List[Command]:
        """Get commands for an action based on location.

        This queries the home's ontology to find all commands that can reproduce the given action,
        filtering by location if specified (and not "Entire Home").

        Args:
            action: Action object
            location: Location dictionary with 'name' and 'url'
            home_uuid: Home UUID for context

        Returns:
            List of Command objects
        """
        commands = []

        try:
            # Load home world
            home_world = self._get_home_world(home_uuid)
            if not home_world:
                return commands

            # Re-run reasoner with inferences
            sync_reasoner_hermit(home_world, infer_property_values=True)

            # Find the action individual in the base ontology
            action_individual = None
            for ind in self.onto.individuals():
                if str(ind.iri) == action.url:
                    action_individual = ind
                    break

            if not action_individual:
                self.logger.warning(
                    f"Could not find action individual for {action.url}"
                )
                return commands

            # Get commands that reproduce this action (from home world)
            # Find the action in home world that corresponds to the base action
            home_action = None
            for ind in home_world.individuals():
                if str(ind.iri) == action.url:
                    home_action = ind
                    break

            if not home_action:
                self.logger.warning(f"Action {action.url} not found in home world")
                return commands

            # Get commands via reproduceBy or allowTo
            reproduce_by_commands = getattr(home_action, "reproduceBy", [])

            # Fallback: Search for commands via allowTo
            if not reproduce_by_commands or len(reproduce_by_commands) < 2:
                manual_commands = []
                for ind in home_world.individuals():
                    if ind == home_action: continue
                    allow_to = getattr(ind, "allowTo", [])
                    
                    # Compare by IRI strings to be safe
                    for allowed_action in allow_to:
                        if str(allowed_action.iri) == str(home_action.iri):
                            manual_commands.append(ind)
                            break
                
                # Merge lists avoiding duplicates
                for cmd in manual_commands:
                    if cmd not in reproduce_by_commands:
                        reproduce_by_commands.append(cmd)
            
            for command_individual in reproduce_by_commands:
                # Get the service this command belongs to
                command_services = getattr(command_individual, "commandIsOfService", [])
                if not command_services:
                    continue

                command_service = command_services[0]

                # Get the entity that has this service
                entities_with_service = getattr(command_service, "isOfEntity", [])
                if not entities_with_service:
                    continue

                entity_individual = entities_with_service[0]

                # Check location filter
                if location and location.get("name") != "Entire Home":
                    entity_locations = getattr(entity_individual, "position", [])
                    if entity_locations:
                        entity_location = entity_locations[0]
                        # Compare fragments (IDs) to avoid base URL/UUID mismatch
                        loc_id = str(entity_location.iri).split("#")[-1]
                        target_id = location.get("url", "").split("#")[-1]
                        
                        if loc_id != target_id:
                            # Entity not in specified location, skip
                            continue

                # Create Command object
                command = Command()

                # Set url (short form without namespace)
                command.url = command_individual.name

                # Get command properties
                command_id_values = getattr(command_individual, "id", [])
                if command_id_values:
                    command.id = (
                        str(command_id_values[0])
                        if isinstance(command_id_values, list)
                        else str(command_id_values)
                    )

                # Get type property by searching all properties
                command.type = None
                for prop in command_individual.get_properties():
                    if "type" in str(prop.iri).lower():
                        values = prop[command_individual]
                        if values:
                            command.type = (
                                str(values[0])
                                if isinstance(values, list)
                                else str(values)
                            )
                            break

                # Get entity details
                command.entity = self.get_entity_by_url(
                    str(entity_individual.iri), home_uuid
                )

                commands.append(command)

            return commands

        except Exception as e:
            self.logger.error(f"Error getting commands: {e}", exc_info=True)
            return commands

    def triggers(self, action: Action, trigger: Trigger) -> bool:
        """
        Check if an action can trigger a specific trigger using OWL reasoning.

        Uses the reasoner to query the 'triggers' object property from the ontology
        to determine if the given action can cause the trigger to fire.

        Args:
            action: Action to check
            trigger: Trigger to check

        Returns:
            True if action triggers the trigger, False otherwise
        """
        try:
            # Get action individual from ontology
            action_id = action.url.split("#")[-1]
            action_individual = getattr(self.sifis_ns, action_id, None)

            if not action_individual:
                return False

            triggers_prop = getattr(self.eupont_ns, "triggers", None)
            if not triggers_prop:
                return False

            # Get all triggers for this action
            triggered_individuals = getattr(action_individual, "triggers", [])

            # Check if the given trigger is in the list
            for triggered in triggered_individuals:
                if str(triggered.iri) == trigger.url:
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error checking if action triggers trigger: {e}")
            return False

    def equals_ml(self, action1: Action, action2: Action) -> bool:
        """
        Check if two actions are equivalent at the machine learning level.
        This checks if actions have the same effect/behavior.

        Args:
            action1: First action
            action2: Second action

        Returns:
            True if actions are equivalent, False otherwise
        """
        try:
            # Simple check: compare action URLs and types
            if action1.url == action2.url:
                return True

            # Extract action IDs
            action1_id = action1.url.split("#")[-1]
            action2_id = action2.url.split("#")[-1]

            action1_individual = getattr(self.sifis_ns, action1_id, None)
            action2_individual = getattr(self.sifis_ns, action2_id, None)

            if not action1_individual or not action2_individual:
                return False

            # Check if they have the same features
            action1_features = set(
                str(f) for f in getattr(action1_individual, "hasFeature", [])
            )
            action2_features = set(
                str(f) for f in getattr(action2_individual, "hasFeature", [])
            )

            # If features match, actions are equivalent
            if action1_features and action2_features:
                return action1_features == action2_features

            # Check types
            action1_types = set(
                str(t).lower() for t in getattr(action1_individual, "type", [])
            )
            action2_types = set(
                str(t).lower() for t in getattr(action2_individual, "type", [])
            )

            if action1_types and action2_types:
                return action1_types == action2_types

            # Check names as last resort
            if action1.name == action2.name:
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error checking if actions are equal: {e}")
            return False

    # ========================================
    # User OWL File Generation Methods (Static)
    # ========================================
    # New static methods follow
    BASE_IRI = "http://elite.polito.it/ontologies/sifis-home.owl"
    EUPONT_IRI = "http://elite.polito.it/ontologies/eupont.owl"
    
    @staticmethod
    def _get_ontology_dir() -> str:
        """Returns the absolute path to the ontologies directory."""
        return os.path.join(current_app.root_path, "ontologies")

    @staticmethod
    def create_home_ontology(home_uuid: str) -> str:
        """
        Creates a new OWL file for the Smart Home with its specific locations, devices, and rules.
        Returns the Home's Ontology IRI.
        """
        from app.models.entities.smart_home import SmartHome
        
        # Fetch Home from DB
        home = SmartHome.query.filter_by(uuid=str(home_uuid)).first()
        if not home:
            raise ValueError(f"SmartHome with UUID {home_uuid} not found")

        ontology_dir = OWLService._get_ontology_dir()
        homes_dir = os.path.join(ontology_dir, "homes")
        os.makedirs(homes_dir, exist_ok=True)

        home_iri = f"{OWLService.BASE_IRI}/{home_uuid}"
        filename = f"{home_uuid}.owl"
        file_path = os.path.join(homes_dir, filename)

        # 1. Load Base Ontology
        import owlready2
        if ontology_dir not in owlready2.onto_path:
            owlready2.onto_path.append(ontology_dir)
        
        base_onto = get_ontology("http://elite.polito.it/ontologies/sifis-home.owl").load()
        
        # 2. Create new ontology
        onto = get_ontology(home_iri)
        onto.imported_ontologies.append(base_onto)
        
        with onto:
            # 3. Create Content
            OWLService._create_home_individuals(onto, base_onto, home)
            locations = OWLService._create_locations(onto, base_onto, home)


            OWLService._create_dynamic_devices(onto, base_onto, home, locations)

        # 4. Save to file
        onto.save(file=file_path)
        
        # 5. Post-processing to enforce serialization format matching ptp-demo.owl
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Fix prefixes
        content = content.replace('xmlns:eupo="', 'xmlns:eupont="')
        content = content.replace('eupo:', 'eupont:')
        content = content.replace('xmlns:sifi="', 'xmlns:sifis-home="')
        content = content.replace('sifi:', 'sifis-home:')
        
        # Fix property rendering (remove rdf:datatype)
        import re
        content = re.sub(r'<sifis-home:type[^>]*>([^<]+)</sifis-home:type>', r'<eupont:type>\1</eupont:type>', content)
        content = re.sub(r'<sifis-home:id[^>]*>([^<]+)</sifis-home:id>', r'<sifis-home:id>\1</sifis-home:id>', content)

        # Fix Serialization Style: Typed Node -> Generic Node
        ns_map = {
            "eupont": "http://elite.polito.it/ontologies/eupont.owl#",
            "sifis-home": "http://elite.polito.it/ontologies/sifis-home.owl#"
        }

        def replace_typed_node(match):
            prefix = match.group(1)
            class_name = match.group(2)
            attributes = match.group(3)
            
            if prefix in ns_map:
                full_iri = f"{ns_map[prefix]}{class_name}"
                return f'<owl:NamedIndividual{attributes}>\n  <rdf:type rdf:resource="{full_iri}"/>'
            return match.group(0)

        # Convert Typed Nodes (Classes start with Uppercase) to Generic Nodes
        content = re.sub(r'<(eupont|sifis-home):([A-Z]\w+)([^>]*)>', replace_typed_node, content)
        content = re.sub(r'</(eupont|sifis-home):([A-Z]\w+)>', '</owl:NamedIndividual>', content)

        # Remove redundant implicit type
        content = content.replace('<rdf:type rdf:resource="http://www.w3.org/2002/07/owl#NamedIndividual"/>', '')
        
        # Cleanup empty lines
        content = re.sub(r'\n\s*\n', '\n', content)

        with open(file_path, 'w') as f:
            f.write(content)
            
        return home_iri

    @staticmethod
    def _get_class(base_onto, class_name, iri=None):
        """Helper to safely get a class from the ontology."""
        # Try direct access
        cls = getattr(base_onto, class_name, None)
        if cls: return cls
        
        # Try searching in world
        if iri:
            if '#' in iri:
                base_iri, fragment = iri.split('#', 1)
                cls = base_onto.world.get_ontology(base_iri)[fragment]
            elif '/' in iri:
                base_iri, fragment = iri.rsplit('/', 1)
                cls = base_onto.world.get_ontology(base_iri + '/')[fragment]
            
            if cls: return cls
            
        # Try searching by name in classes
        for cls in base_onto.classes():
            if cls.name == class_name:
                return cls
                
        # Try EUPont explicitly
        eupont = base_onto.world.get_ontology(OWLService.EUPONT_IRI)
        if eupont:
            cls = getattr(eupont, class_name, None)
            if cls: return cls
            
        return None

    @staticmethod
    def _create_individual(onto, class_obj, name, types=None, props=None):
        """Helper to create an individual safely with properties."""
        if not class_obj:
            return None
            
        ind = onto[name]
        if ind is None:
            ind = class_obj(name, namespace=onto)
        
        if types:
            for t in types:
                if t: ind.is_a.append(t)
        
        if props:
            for prop_name, prop_value in props.items():
                # Find property
                prop = None
                
                # Helper to check if object is a property
                def is_prop(obj):
                    return hasattr(obj, 'python_name') and hasattr(obj, 'iri')

                # Try direct lookup on ontology
                if hasattr(onto, prop_name):
                    candidate = getattr(onto, prop_name)
                    if is_prop(candidate):
                        prop = candidate

                # Try lookup on imported ontologies
                if not prop:
                    for imported in onto.imported_ontologies:
                        if hasattr(imported, prop_name):
                            candidate = getattr(imported, prop_name)
                            if is_prop(candidate):
                                prop = candidate
                                break
                
                # Special handling for known properties if not found by name
                if not prop:
                    if prop_name == "id":
                        # Look for data property 'id'
                        prop = onto.world.search_one(iri="*#id", type=None) # type=None to find any entity
                        # Filter to ensure it's a property
                        if not is_prop(prop):
                             # Try specific known IRI
                             prop = onto.world.get_ontology("http://elite.polito.it/ontologies/sifis-home.owl").search_one(iri="*#id")

                    elif prop_name == "name":
                        prop = onto.world.get_ontology("http://elite.polito.it/ontologies/sifis-home.owl").search_one(iri="*#name")
                    elif prop_name == "allowTo":
                        prop = onto.world.get_ontology("http://elite.polito.it/ontologies/eupont.owl").search_one(iri="*#allowTo")
                    elif prop_name == "type":
                        # Use eupont:type specifically, not sifis-home:type
                        prop = onto.world.get_ontology("http://elite.polito.it/ontologies/eupont.owl").search_one(iri="http://elite.polito.it/ontologies/eupont.owl#type")

                if prop and hasattr(prop, 'python_name'):
                    try:
                        # Handle list vs single value
                        if isinstance(prop_value, list):
                            setattr(ind, prop.python_name, prop_value)
                        else:
                            setattr(ind, prop.python_name, [prop_value])
                    except Exception as e:
                        print(f"Error assigning property {prop_name} ({prop}) to {name}: {e}")
                
        return ind

    @staticmethod
    def _create_home_individuals(onto, base_onto, home):
        """Create individuals for all users in the home."""
        Person = OWLService._get_class(base_onto, "Person", "http://xmlns.com/foaf/0.1/Person")
        if not Person:
            return

        # Add all owners
        for user_home in home.owned_by_users:
            user = user_home.user
            if user.uuid:
                 Person(f"{user.uuid}", namespace=onto)

    @staticmethod
    def _create_locations(onto, base_onto, home):
        Location = OWLService._get_class(base_onto, "Location")
        Room = OWLService._get_class(base_onto, "Room")
        Building = OWLService._get_class(base_onto, "Building")
        
        if not Location:  return {}

        locations = {}
        
        # Get the sifis-home ontology and the name property
        sifis_home_onto = onto.world.get_ontology("http://elite.polito.it/ontologies/sifis-home.owl")
        name_prop = sifis_home_onto.search_one(iri="http://elite.polito.it/ontologies/sifis-home.owl#name")
        
        # Alias the 'name' property to 'sifis_name' to avoid conflict with Owlready's built-in .name attribute (IRI).
        if name_prop:
            name_prop.python_name = "sifis_name"
        
        # Import locstr for localized strings
        from owlready2 import locstr
        
        # Create Home Individual
        home_ind = OWLService._create_individual(onto, Location, "location-home", [Building])
        if home_ind and home.name and name_prop:
            home_ind.sifis_name = [locstr(home.name, "en")]
            
        locations["location-home"] = home_ind
        
       # Dynamic Rooms from DB
        for room in home.rooms:
            if not room.room_uuid: continue
            
            loc_id = f"location-{room.room_uuid}"
            loc_ind = OWLService._create_individual(onto, Location, loc_id, [Room])
            
            # Set name using the ALIASED property 'sifis_name' with language tag
            if loc_ind and room.name and name_prop:
                loc_ind.sifis_name = [locstr(room.name, "en")]
                
            locations[loc_id] = loc_ind
            
            # Map by ID as well for easy lookup
            locations[str(room.room_id)] = loc_ind
        
        return locations

 

    @staticmethod
    def _create_dynamic_devices(onto, base_onto, home, locations):
        """
        Dynamically create devices, services, and commands based on DB models.
        Infers device capabilities/class from the device name.
        """
        # 1. Get Classes
        Camera = OWLService._get_class(base_onto, "Camera")
        Lamp = OWLService._get_class(base_onto, "Lamp")
        Heater = OWLService._get_class(base_onto, "Heater")
        Speaker = OWLService._get_class(base_onto, "Speaker")
        SmartWindow = OWLService._get_class(base_onto, "SmartWindow")
        SmartBlind = OWLService._get_class(base_onto, "SmartBlind")
        SmartDoor = OWLService._get_class(base_onto, "SmartDoor")
        AirConditioner = OWLService._get_class(base_onto, "AirConditioner")
        AntiIntrusionSystem = OWLService._get_class(base_onto, "AntiIntrusionSystem")
        Appliance = OWLService._get_class(base_onto, "Appliance")
        
        # Service Classes
        AudioRecordingService = OWLService._get_class(base_onto, "AudioRecordingService")
        VideoRecordingService = OWLService._get_class(base_onto, "VideoRecordingService")
        LightingService = OWLService._get_class(base_onto, "LightingService")
        HeatingService = OWLService._get_class(base_onto, "HeatingService")
        CoolingService = OWLService._get_class(base_onto, "CoolingService")
        SecurityService = OWLService._get_class(base_onto, "SecurityService")
        ApplianceService = OWLService._get_class(base_onto, "ApplianceService")
        FrameService = OWLService._get_class(base_onto, "FrameService")
        TimerService = OWLService._get_class(base_onto, "TimerService")
        
        # Command Classes
        StartCommand = OWLService._get_class(base_onto, "StartCommand")
        StopCommand = OWLService._get_class(base_onto, "StopCommand")
        TurnOnCommand = OWLService._get_class(base_onto, "TurnOnCommand")
        TurnOffCommand = OWLService._get_class(base_onto, "TurnOffCommand")
        OpenCommand = OWLService._get_class(base_onto, "OpenCommand")
        CloseCommand = OWLService._get_class(base_onto, "CloseCommand")
        
        # Notification Classes
        TimeNotification = OWLService._get_class(base_onto, "TimeNotification")
        CloseNotification = OWLService._get_class(base_onto, "CloseNotification")
        OpenNotification = OWLService._get_class(base_onto, "OpenNotification")

    # ========================================
    # Device Mapping Configuration
    # ========================================
    
    SERVICE_CLASS_MAPPING = {
        "light": "LightingService",
        "video": "VideoRecordingService",
        "camera": "VideoRecordingService",
        "audio": "AudioRecordingService",
        "heat": "HeatingService",
        "hvac": "HeatingService",
        "fan_coil": "HeatingService",
        "cooling": "CoolingService",
        "ac": "CoolingService",
        "window": "FrameService",
        "shutter": "FrameService",
        "blind": "FrameService",
        "door": "FrameService",
        "gate": "FrameService",
        "siren": "SecurityService",
        "security": "SecurityService",
        "power": "ApplianceService",
        "switch": "ApplianceService",
        "appliance": "ApplianceService",
    }

    SIFIS_ACTIONS = {
        "all_audio": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_audio_actions",
        "rec_audio": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_record_audio_action",
        "stop_audio": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_stop_record_audio_action",
        "all_video": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_video_actions",
        "rec_video": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_record_video_action",
        "stop_video": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_stop_record_video_action",
        "all_light": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_lighting_actions",
        "on_light": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_turn_on_lights_action",
        "off_light": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_turn_off_lights_action",
        "all_heat": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_heating_actions",
        "on_heat": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_turn_on_heating_action",
        "off_heat": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_turn_off_heating_action",
        "all_win": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_windows_actions",
        "open_win": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_open_windows_action",
        "close_win": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_close_windows_action",
        "all_cool": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_cooling_actions",
        "on_cool": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_enable_cooling_action",
        "off_cool": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_disable_cooling_action",
        "all_sec": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_security_actions",
        "on_sec": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_enable_security_action",
        "off_sec": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_disable_security_action",
        "all_app": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_appliance_actions",
        "on_app": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_turn_on_appliance_action",
        "off_app": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_turn_off_appliance_action",
        "all_door": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_all_doors_actions",
        "open_door": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_open_doors_action",
        "close_door": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_close_doors_action",
    }

    SIFIS_TRIGGERS = {
         "win_open": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_windows_open_trigger",
         "win_close": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_windows_close_trigger",
         "morning": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_morning_trigger",
         "afternoon": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_afternoon_trigger",
         "evening": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_evening_trigger",
         "night": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_night_trigger",
         "day": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_day_trigger"
    }

    DEVICE_TYPE_MAPPING = {
         # Lighting
         "domo_light": ("Lamp", "LightingService", ["TurnOnCommand", "TurnOffCommand"], 
                        [("all_light", "on_light"), ("all_light", "off_light")]),
         "domo_light_dimmable": ("Lamp", "LightingService", ["TurnOnCommand", "TurnOffCommand"],
                                 [("all_light", "on_light"), ("all_light", "off_light")]),
         "domo_rgbw_light": ("Lamp", "LightingService", ["TurnOnCommand", "TurnOffCommand"],
                             [("all_light", "on_light"), ("all_light", "off_light")]),
         
         # Camera 
         "domo_camera": ("Camera", "VideoRecordingService", ["StartCommand", "StopCommand"],
                         [("all_video", "rec_video"), ("all_video", "stop_video")]),
         
         # Cooling (AC unit)
         "domo_ac_unit": ("AirConditioner", "CoolingService", ["TurnOnCommand", "TurnOffCommand"],
                          [("all_cool", "on_cool"), ("all_cool", "off_cool")]),
                          
         # Heating
         "domo_floor_valve": ("Heater", "HeatingService", ["TurnOnCommand", "TurnOffCommand"],
                              [("all_heat", "on_heat"), ("all_heat", "off_heat")]),
         "domo_fan_coil": ("Heater", "HeatingService", ["TurnOnCommand", "TurnOffCommand"],
                           [("all_heat", "on_heat"), ("all_heat", "off_heat")]),
         "domo_ble_valve": ("Heater", "HeatingService", ["TurnOnCommand", "TurnOffCommand"],
                            [("all_heat", "on_heat"), ("all_heat", "off_heat")]),
                          
         # Windows / Shutters
         "domo_roller_shutter": ("SmartBlind", "FrameService", ["OpenCommand", "CloseCommand"],
                                 [("all_win", "open_win"), ("all_win", "close_win")]),

         # Doors / Gates
         "domo_garage_gate": ("SmartDoor", "FrameService", ["OpenCommand", "CloseCommand"],
                              [("all_door", "open_door"), ("all_door", "close_door")]),
                                 
         # Switches / Plugs / Generic Appliances
         "domo_switch": ("Appliance", "ApplianceService", ["TurnOnCommand", "TurnOffCommand"],
                         [("all_app", "on_app"), ("all_app", "off_app")]),
         "domo_generic_output": ("Appliance", "ApplianceService", ["TurnOnCommand", "TurnOffCommand"],
                                 [("all_app", "on_app"), ("all_app", "off_app")]),

         # Security
         "domo_siren": ("AntiIntrusionSystem", "SecurityService", ["TurnOnCommand", "TurnOffCommand"],
                        [("all_sec", "on_sec"), ("all_sec", "off_sec")]),
                         
         # Sensors 
         "domo_window_sensor": ("Sensor", "SmartEnvironmentService", [], [], ["OpenNotification", "CloseNotification"], ["win_open", "win_close"]),
         "domo_ble_contact": ("Sensor", "SmartEnvironmentService", [], []),
         "domo_ble_thermometer": ("Sensor", "SmartEnvironmentService", [], []),
    }

    @staticmethod
    def get_action_urls_for_device_type(topic_name: str) -> List[str]:
        """
        Get the specific action IRIs (e.g., TurnOn, TurnOff) associated with a device topic.
        Used for mapping DHT rules to SIFIS actions.
        """
        if not topic_name:
            return []
            
        mapping = OWLService.DEVICE_TYPE_MAPPING.get(topic_name)
        if not mapping:
            return []

        if len(mapping) < 4:
            return []
            
        action_keys_list = mapping[3] 
        
        action_urls = set()
        for keys_tuple in action_keys_list:
            iri = None
            generic_key = None
            specific_key = None

            if len(keys_tuple) >= 1:
                generic_key = keys_tuple[0]
            if len(keys_tuple) >= 2:
                specific_key = keys_tuple[1]
            
            # Prefer generic action (e.g. "all_video") if available and mapped
            if generic_key:
                iri = OWLService.SIFIS_ACTIONS.get(generic_key)
            
            # Fallback to specific action if generic not found or maps to nothing
            if not iri and specific_key:
                iri = OWLService.SIFIS_ACTIONS.get(specific_key)
                
            if iri:
                action_urls.add(iri)
                    
        return list(action_urls)

    @staticmethod
    def _create_dynamic_devices(onto, base_onto, home, locations):
        """
        Dynamically create devices, services, and commands based on DB models.
        Infers device capabilities/class from the device name.
        """
        
        def get_action(key):
            iri = OWLService.SIFIS_ACTIONS.get(key)
            if not iri: return None
            res = base_onto.search_one(iri=iri)
            if not res: res = onto.world.search_one(iri=iri)
            return res

        def get_trigger(key):
            iri = OWLService.SIFIS_TRIGGERS.get(key)
            if not iri: return None
            res = base_onto.search_one(iri=iri)
            if not res: res = onto.world.search_one(iri=iri)
            return res
            
        def safe_list(*args):
             return [a for a in args if a]

        # 3. Global System Services 
        TimerService = OWLService._get_class(base_onto, "TimerService")
        TimeNotification = OWLService._get_class(base_onto, "TimeNotification")
        
        # Assuming one global timer for now
        s_timer = OWLService._create_individual(onto, TimerService, "s-calendar-alarm")
        if s_timer:
            # Create notification with ALL time-based triggers
            t_moments = [get_trigger(k) for k in ["morning", "afternoon", "evening", "night", "day"]]
            t_moments = [t for t in t_moments if t]
            
            # Add weekly timer trigger
            weekly_timer_trigger = base_onto.search_one(iri="http://elite.polito.it/ontologies/sifis-home.owl#sifis_weekly_timer_trigger")
            if not weekly_timer_trigger:
                weekly_timer_trigger = onto.world.search_one(iri="http://elite.polito.it/ontologies/sifis-home.owl#sifis_weekly_timer_trigger")
            if weekly_timer_trigger:
                t_moments.append(weekly_timer_trigger)
            
            OWLService._create_individual(onto, TimeNotification, "n-calendar1-alarm", props={
                "id": "calendar1-alarm",
                "allowTo": t_moments
            })
            s_timer.hasNotification.append(onto["n-calendar1-alarm"])

        # 4. Iterate DB Devices
        for device in home.devices:
            d_name = device.name.lower()
            d_uuid = str(device.device_uuid)
            d_topic = device.topic_name if device.topic_name else f"topic-{d_uuid}"

            matched_config = OWLService.DEVICE_TYPE_MAPPING.get(d_topic)
            d_ind = None
            if matched_config:
                # Unpack config with optional notification support (backwards compatible)
                d_class_str, s_class_str, cmd_class_strs, action_keys_list, *rest = matched_config
                notif_class_strs = rest[0] if len(rest) > 0 else []
                trigger_keys_list = rest[1] if len(rest) > 1 else []
                
                DevClass = OWLService._get_class(base_onto, d_class_str) or OWLService._get_class(onto, d_class_str)
                if not DevClass: DevClass = OWLService._get_class(base_onto, "IoTEntity")

                # Use device UUID for unique ID instead of topic (which is shared by all devices of same type)
                d_ind = OWLService._create_individual(onto, DevClass, f"d-{d_uuid}", props={"id": str(d_uuid)})
                
                if d_ind:
                     ServClass = OWLService._get_class(base_onto, s_class_str)
                     if ServClass:
                         # Use device UUID for unique service ID
                         s_ind = OWLService._create_individual(onto, ServClass, f"s-{d_uuid}", 
                                                               props={"id": f"s-{d_uuid}", "isOfEntity": [d_ind]})
                         if s_ind:
                             d_ind.hasService.append(s_ind)
                             
                             # 1. Create Commands (Actions)
                             for idx, cmd_str in enumerate(cmd_class_strs):
                                 CmdClass = OWLService._get_class(base_onto, cmd_str)
                                 if CmdClass and idx < len(action_keys_list):
                                      allow_keys = action_keys_list[idx]
                                      allow_iris = safe_list(get_action(allow_keys[0]), get_action(allow_keys[1]))
                                      
                                      cmd_type = "turn_on" if "On" in cmd_str or "Start" in cmd_str or "Open" in cmd_str else "turn_off"
                                      
                                      # Use device UUID for unique command ID
                                      c_ind = OWLService._create_individual(onto, CmdClass, f"c-{d_uuid}-{idx}",
                                          props={
                                              "id": f"{d_uuid}-cmd-{idx}",
                                              "type": cmd_type,
                                              "allowTo": allow_iris,
                                              "commandIsOfService": [s_ind]
                                          })
                                      s_ind.hasCommand.append(c_ind)

                             # 2. Create Notifications (Triggers)
                             for idx, notif_str in enumerate(notif_class_strs):
                                 NotifClass = OWLService._get_class(base_onto, notif_str)
                                 if NotifClass and idx < len(trigger_keys_list):
                                     trig_key = trigger_keys_list[idx]
                                     trig_iri = get_trigger(trig_key)
                                     
                                     if trig_iri:
                                         n_ind = OWLService._create_individual(onto, NotifClass, f"n-{d_uuid}-{idx}",
                                            props={
                                                "id": f"{d_uuid}-notif-{idx}",
                                                "allowTo": [trig_iri],
                                                "isOfService": [s_ind]
                                            })
                                         s_ind.hasNotification.append(n_ind)

            # Link Location
            if d_ind and device.room_id:
                loc_ind = locations.get(str(device.room_id))
                if loc_ind:
                    d_ind.position = [loc_ind]
