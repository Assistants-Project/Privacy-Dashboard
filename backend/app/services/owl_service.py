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
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.logger = self._setup_logging()

        # Cache for user locations to avoid re-loading ontology
        self._locations_cache = {}

        # Load ontology and setup reasoner
        self._initialize_ontology()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        level = self.config.get("logging", {}).get("level", "INFO")

        # Create logger
        logger = logging.getLogger(__name__)

        # Only configure if not already configured
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
        ont_config = self.config["ontology"]
        ontology_dir = Path(ont_config["directory"])
        ontology_path = ontology_dir / ont_config["sifis_file"]

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

        # Setup namespaces
        self.sifis_ns = self.onto.get_namespace(
            "http://elite.polito.it/ontologies/sifis-home.owl#"
        )
        self.eupont_ns = self.onto.get_namespace(
            "http://elite.polito.it/ontologies/eupont.owl#"
        )

        # Initialize reasoner
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

    def get_trigger_services(self) -> List[Service]:
        """Get all services that offer triggers"""
        services = []

        try:
            if not self.onto or not self.eupont_ns:
                return services

            Channel = getattr(self.eupont_ns, "Channel", None)
            if not Channel:
                return services

            for subclass in Channel.subclasses():
                temp_services = []
                has_triggers = False

                for instance in subclass.instances():
                    if getattr(instance, "offerTrigger", []):
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

    def get_action_services(self) -> List[Service]:
        """Get all services that offer actions"""
        services = []

        try:
            if not self.onto or not self.eupont_ns:
                return services

            Channel = getattr(self.eupont_ns, "Channel", None)
            if not Channel:
                return services

            for subclass in Channel.subclasses():
                temp_services = []
                has_actions = False

                for instance in subclass.instances():
                    if getattr(instance, "offerAction", []):
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
                    trigger_instance, service_id, username
                )
                triggers.append(trigger)

            return triggers

        except Exception as e:
            self.logger.error(f"Error getting triggers for service {service_id}: {e}")
            return []

    def _get_details_for_instance(
        self, instance, service_id: str, username: Optional[str] = "ptp-demo"
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
                        service_id, username
                    )
                elif detail_type == "location":
                    detail.alternatives = self._get_locations(username)
                else:
                    detail.alternatives = []

                details.append(detail)

            # Add implicit entity detail if needed
            if not has_entity_detail:
                entities = self._get_entities_by_service(service_id, username)
                if entities:
                    details.append(
                        Detail(
                            url="entity_detail",
                            id="entity_detail",
                            name="Which entity?",
                            type="entity",
                            alternatives=entities,
                        )
                    )

            return details

        except Exception as e:
            self.logger.error(f"Error getting details for {instance.name}: {e}")
            return []

    def get_trigger_details(
        self, service_id: str, trigger_id: str, username: Optional[str] = "ptp-demo"
    ) -> List[Detail]:
        """Get configuration details/parameters for a specific trigger."""
        try:
            if not self.onto or not self.sifis_ns:
                return []

            trigger_instance = getattr(self.sifis_ns, trigger_id, None)
            if not trigger_instance:
                return []

            return self._get_details_for_instance(
                trigger_instance, service_id, username
            )

        except Exception as e:
            self.logger.error(f"Error getting trigger details: {e}")
            return []

    def get_action_details(
        self, service_id: str, action_id: str, username: Optional[str] = "ptp-demo"
    ) -> List[Detail]:
        """Get configuration details/parameters for a specific action."""
        try:
            if not self.onto or not self.sifis_ns:
                return []

            action_instance = getattr(self.sifis_ns, action_id, None)
            if not action_instance:
                return []

            return self._get_details_for_instance(action_instance, service_id, username)

        except Exception as e:
            self.logger.error(f"Error getting action details: {e}")
            return []

    def _get_entities_by_service(
        self, service_id: str, username: Optional[str] = "ptp-demo"
    ) -> List[Dict]:
        """Get IoT entities/devices that provide a specific service."""
        if not username:
            return []

        try:
            # Load user world
            user_world = self._get_user_world(username)
            if not user_world:
                return []

            # Build service IRI
            service_iri = f"http://elite.polito.it/ontologies/sifis-home.owl/{username}#{service_id}"

            # Find all individuals that have this service
            entities = []
            for individual in user_world.individuals():
                services = getattr(individual, "hasService", [])
                for service in services:
                    if str(service.iri) == service_iri:
                        entities.append(
                            {
                                "url": str(individual.iri),
                                "name": self._safe_get_property(individual, "id")
                                or self._safe_get_property(individual, "name")
                                or individual.name,
                                "id": individual.name,
                            }
                        )
                        break

            return entities
        except Exception as e:
            self.logger.error(f"Error getting entities for service {service_id}: {e}")
            return []

    def _get_locations(self, username: Optional[str] = "ptp-demo") -> List[Dict]:
        """Get locations from user's ontology."""
        if not username:
            return []

        # Check cache first
        if username in self._locations_cache:
            return self._locations_cache[username]

        try:
            ont_config = self.config["ontology"]
            ontology_dir = Path(ont_config["directory"])
            user_ontology_path = ontology_dir / f"{username}.owl"

            if not user_ontology_path.exists():
                return []

            # Load user ontology in separate world
            from owlready2 import World

            user_world = World()

            # Pre-load imported ontologies to avoid web downloads
            eupont_path = ontology_dir / "eupont.owl"
            sifis_path = ontology_dir / "sifis-home.owl"

            if eupont_path.exists():
                user_world.get_ontology(f"file://{eupont_path.absolute()}").load()
            if sifis_path.exists():
                user_world.get_ontology(f"file://{sifis_path.absolute()}").load(
                    only_local=True
                )

            # Load user ontology
            user_onto = user_world.get_ontology(
                f"file://{user_ontology_path.absolute()}"
            ).load()

            # Run reasoner
            sync_reasoner_hermit(user_world, infer_property_values=True)

            # Find Location class
            Location = None
            for cls in user_world.classes():
                if cls.name == "Location":
                    Location = cls
                    break

            if not Location:
                return []

            # Get location instances
            locations = []
            for loc_instance in Location.instances(user_world):
                locations.append(
                    {
                        "url": str(loc_instance.iri),
                        "name": self._safe_get_property(loc_instance, "name")
                        or loc_instance.name,
                    }
                )

            # Cache the result
            self._locations_cache[username] = locations

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
                    action_instance, service_id, username
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

    def get_trigger_by_url(self, url: str, username: str) -> Optional[Trigger]:
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
                username,
            )

            return trigger
        except Exception as e:
            self.logger.error(f"Error getting trigger by url {url}: {e}")
            return None

    def get_action_by_url(self, url: str, username: str) -> Optional[Action]:
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
                username,
            )

            return action
        except Exception as e:
            self.logger.error(f"Error getting action by url {url}: {e}")
            return None

    def get_entity_by_url(self, url: str, username: str) -> Optional[Dict]:
        """Get IoT entity by url"""
        try:
            # Extract entity ID from url
            entity_id = url.split("#")[-1]

            # Try to find in user ontology
            user_world = self._get_user_world(username)
            if not user_world:
                return None

            # Search for the entity
            for individual in user_world.individuals():
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

    def _get_user_world(self, username: str):
        """Helper to load user world (can be cached later if needed)"""
        try:
            ont_config = self.config["ontology"]
            ontology_dir = Path(ont_config["directory"])
            user_ontology_path = ontology_dir / f"{username}.owl"

            if not user_ontology_path.exists():
                return None

            from owlready2 import World

            user_world = World()

            # Pre-load imported ontologies
            eupont_path = ontology_dir / "eupont.owl"
            sifis_path = ontology_dir / "sifis-home.owl"

            if eupont_path.exists():
                user_world.get_ontology(f"file://{eupont_path.absolute()}").load()
            if sifis_path.exists():
                user_world.get_ontology(f"file://{sifis_path.absolute()}").load(
                    only_local=True
                )

            user_world.get_ontology(f"file://{user_ontology_path.absolute()}").load()

            return user_world
        except Exception as e:
            self.logger.error(f"Error loading user world for {username}: {e}")
            return None

    def get_commands(
        self, action: Action, location: Dict, username: str
    ) -> List[Command]:
        """Get commands for an action based on location.

        This queries the user's ontology to find all commands that can reproduce the given action,
        filtering by location if specified (and not "Entire Home").

        Args:
            action: Action object
            location: Location dictionary with 'name' and 'url'
            username: Username for context

        Returns:
            List of Command objects
        """
        commands = []

        try:
            # Load user world
            user_world = self._get_user_world(username)
            if not user_world:
                self.logger.warning(f"Could not load user world for {username}")
                return commands

            # Re-run reasoner with inferences
            sync_reasoner_hermit(user_world, infer_property_values=True)

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

            # Get commands that reproduce this action (from user world)
            # Find the action in user world that corresponds to the base action
            user_action = None
            for ind in user_world.individuals():
                if str(ind.iri) == action.url:
                    user_action = ind
                    break

            if not user_action:
                self.logger.warning(f"Action {action.url} not found in user world")
                return commands

            # Get commands via reproduceBy property (direct) or allowTo property (inverse)
            reproduce_by_commands = getattr(user_action, "reproduceBy", [])

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
                        if str(entity_location.iri) != location.get("url"):
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
                    str(entity_individual.iri), username
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

            # Get the 'triggers' property from eupont namespace
            triggers_prop = getattr(self.eupont_ns, "triggers", None)
            if not triggers_prop:
                self.logger.warning("triggers property not found in ontology")
                return False

            # Get all triggers that this action can trigger (using reasoner inferences)
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
    def create_user_ontology(user_uuid: UUID) -> str:
        """
        Creates a new OWL file for the user with default locations, devices, services, and rules.
        Returns the user's Ontology IRI.
        """
        ontology_dir = OWLService._get_ontology_dir()
        users_dir = os.path.join(ontology_dir, "users")
        os.makedirs(users_dir, exist_ok=True)

        user_iri = f"{OWLService.BASE_IRI}/{user_uuid}"
        filename = f"{user_uuid}.owl"
        file_path = os.path.join(users_dir, filename)

        # 1. Load Base Ontology
        import owlready2
        if ontology_dir not in owlready2.onto_path:
            owlready2.onto_path.append(ontology_dir)
        
        base_onto = get_ontology("http://elite.polito.it/ontologies/sifis-home.owl").load()
        
        # 2. Create new ontology
        onto = get_ontology(user_iri)
        onto.imported_ontologies.append(base_onto)
        
        with onto:
            # 3. Create Content
            OWLService._create_user_individual(onto, base_onto, user_uuid)
            locations = OWLService._create_locations(onto, base_onto)
            OWLService._create_triggers(onto, base_onto)
            OWLService._create_notifications(onto, base_onto)
            OWLService._create_commands(onto, base_onto)
            OWLService._create_services(onto, base_onto)
            OWLService._create_devices(onto, base_onto, locations)

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
            
        return user_iri

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
                        # Re-raise to stop execution if needed, or continue
                        raise e
                
        return ind

    @staticmethod
    def _create_user_individual(onto, base_onto, user_uuid):
        Person = OWLService._get_class(base_onto, "Person", "http://xmlns.com/foaf/0.1/Person")
        if Person:
            Person(f"{user_uuid}", namespace=onto)

    @staticmethod
    def _create_locations(onto, base_onto):
        Location = OWLService._get_class(base_onto, "Location")
        Room = OWLService._get_class(base_onto, "Room")
        Building = OWLService._get_class(base_onto, "Building")
        
        if not Location:  return {}

        locations = {}
        
        # Default Rooms - NOTE: omitting 'name' property to prevent IRI corruption by owlready2
        rooms = ["bedroom", "livingroom", "kitchen", "bathroom", "office"]
        for room_id in rooms:
            loc_ind = OWLService._create_individual(onto, Location, f"location-{room_id}", [Room])
            locations[f"location-{room_id}"] = loc_ind
            
        # Home
        home_ind = OWLService._create_individual(onto, Location, "location-home", [Building])
        locations["location-home"] = home_ind
        
        return locations

    @staticmethod
    def _create_triggers(onto, base_onto):
        # Triggers are referenced in allowTo but defined in sifis-home.owl
        # We don't need to create them, just reference them.
        pass 

    @staticmethod
    def _create_notifications(onto, base_onto):
        TimeNotification = OWLService._get_class(base_onto, "TimeNotification")
        CloseNotification = OWLService._get_class(base_onto, "CloseNotification")
        OpenNotification = OWLService._get_class(base_onto, "OpenNotification")
        
        # Triggers (referenced by IRI)
        triggers = {
            "morning": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_morning_trigger",
            "afternoon": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_afternoon_trigger",
            "evening": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_evening_trigger",
            "night": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_night_trigger",
            "day": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_day_trigger",
            "win_open": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_windows_open_trigger",
            "win_close": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_windows_close_trigger"
        }
        
        # Helper to get trigger objects safely
        def get_trigger(key):
            iri = triggers[key]
            # Try searching in base_onto first
            res = base_onto.search_one(iri=iri)
            if not res:
                 # Try world search
                 res = onto.world.search_one(iri=iri)
            return res

        # Calendar Alarm
        allow_to_list = [
            get_trigger("morning"), get_trigger("afternoon"), 
            get_trigger("evening"), get_trigger("night"), get_trigger("day")
        ]
        # Filter out None values
        allow_to_list = [t for t in allow_to_list if t]
        
        n_cal = OWLService._create_individual(onto, TimeNotification, "n-calendar1-alarm", props={
            "id": "calendar1-alarm",
            "allowTo": allow_to_list
        })
        
        # Window Notifications
        t_win_close = get_trigger("win_close")
        t_win_open = get_trigger("win_open")
        
        OWLService._create_individual(onto, CloseNotification, "n-window_1-close", props={
            "id": "window_1-closed",
            "allowTo": [t_win_close] if t_win_close else []
        })
        OWLService._create_individual(onto, OpenNotification, "n-window_1-open", props={
            "id": "window_1-opened",
            "allowTo": [t_win_open] if t_win_open else []
        })
        OWLService._create_individual(onto, CloseNotification, "n-window_2-close", props={
            "id": "window_2-closed",
            "allowTo": [t_win_close] if t_win_close else []
        })
        OWLService._create_individual(onto, OpenNotification, "n-window_2-open", props={
            "id": "window_2-opened",
            "allowTo": [t_win_open] if t_win_open else []
        })

    @staticmethod
    def _create_commands(onto, base_onto):
        StartCommand = OWLService._get_class(base_onto, "StartCommand")
        StopCommand = OWLService._get_class(base_onto, "StopCommand")
        TurnOnCommand = OWLService._get_class(base_onto, "TurnOnCommand")
        TurnOffCommand = OWLService._get_class(base_onto, "TurnOffCommand")
        OpenCommand = OWLService._get_class(base_onto, "OpenCommand")
        CloseCommand = OWLService._get_class(base_onto, "CloseCommand")

        # Actions (referenced by IRI)
        actions = {
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
            "close_win": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_close_windows_action"
        }
        
        def get_action(key):
            iri = actions[key]
            res = base_onto.search_one(iri=iri)
            if not res:
                res = onto.world.search_one(iri=iri)
            return res

        # Helper to create list safely
        def safe_list(*args):
            return [a for a in args if a]

        # Camera Commands
        for i in range(1, 4):
            OWLService._create_individual(onto, StartCommand, f"c-camera{i}-start-audio", props={
                "id": f"camera{i}-start-audio", "type": "turn_on",
                "allowTo": safe_list(get_action("all_audio"), get_action("rec_audio"))
            })
            OWLService._create_individual(onto, StopCommand, f"c-camera{i}-stop-audio", props={
                "id": f"camera{i}-stop-audio", "type": "turn_off",
                "allowTo": safe_list(get_action("all_audio"), get_action("stop_audio"))
            })
            OWLService._create_individual(onto, StartCommand, f"c-camera{i}-start-video", props={
                "id": f"camera{i}-start-video", "type": "turn_on",
                "allowTo": safe_list(get_action("all_video"), get_action("rec_video"))
            })
            OWLService._create_individual(onto, StopCommand, f"c-camera{i}-stop-video", props={
                "id": f"camera{i}-stop-video", "type": "turn_off",
                "allowTo": safe_list(get_action("all_video"), get_action("stop_video"))
            })

        # Speaker Commands
        for i in range(1, 3):
            OWLService._create_individual(onto, StartCommand, f"c-speaker{i}-start-audio", props={
                "id": f"speaker{i}-start-audio", "type": "turn_on",
                "allowTo": safe_list(get_action("all_audio"), get_action("rec_audio"))
            })
            OWLService._create_individual(onto, StopCommand, f"c-speaker{i}-stop-audio", props={
                "id": f"speaker{i}-stop-audio", "type": "turn_off",
                "allowTo": safe_list(get_action("all_audio"), get_action("stop_audio"))
            })

        # Lamp Commands
        for i in range(1, 4):
            OWLService._create_individual(onto, TurnOnCommand, f"c-lamp_{i}-turn-on", props={
                "id": f"lamp_{i}-turn-on", "type": "turn_on",
                "allowTo": safe_list(get_action("all_light"), get_action("on_light"))
            })
            OWLService._create_individual(onto, TurnOffCommand, f"c-lamp_{i}-turn-off", props={
                "id": f"lamp_{i}-turn-off", "type": "turn_off",
                "allowTo": safe_list(get_action("all_light"), get_action("off_light"))
            })

        # Radiator Commands
        for i in range(1, 3):
            OWLService._create_individual(onto, TurnOnCommand, f"c-radiator_{i}-turn-on", props={
                "id": f"radiator_{i}-turn-on", "type": "turn_on",
                "allowTo": safe_list(get_action("all_heat"), get_action("on_heat"))
            })
            OWLService._create_individual(onto, TurnOffCommand, f"c-radiator_{i}-turn-off", props={
                "id": f"radiator_{i}-turn-off", "type": "turn_off",
                "allowTo": safe_list(get_action("all_heat"), get_action("off_heat"))
            })

        # Window Commands
        for i in range(1, 3):
            OWLService._create_individual(onto, OpenCommand, f"c-window_{i}-open", props={
                "id": f"window_{i}-open", "type": "unlock",
                "allowTo": safe_list(get_action("all_win"), get_action("open_win"))
            })
            OWLService._create_individual(onto, CloseCommand, f"c-window_{i}-close", props={
                "id": f"window_{i}-close", "type": "lock",
                "allowTo": safe_list(get_action("all_win"), get_action("close_win"))
            })

    @staticmethod
    def _create_services(onto, base_onto):
        AudioRecordingService = OWLService._get_class(base_onto, "AudioRecordingService")
        VideoRecordingService = OWLService._get_class(base_onto, "VideoRecordingService")
        LightingService = OWLService._get_class(base_onto, "LightingService")
        HeatingService = OWLService._get_class(base_onto, "HeatingService")
        FrameService = OWLService._get_class(base_onto, "FrameService")
        TimerService = OWLService._get_class(base_onto, "TimerService")

        # Camera Services
        for i in range(1, 4):
            s_audio = OWLService._create_individual(onto, AudioRecordingService, f"s-camera{i}-record-audio")
            s_video = OWLService._create_individual(onto, VideoRecordingService, f"s-camera{i}-record-video")
            
            # Link commands
            if s_audio:
                s_audio.hasCommand.append(onto[f"c-camera{i}-start-audio"])
                s_audio.hasCommand.append(onto[f"c-camera{i}-stop-audio"])
            if s_video:
                s_video.hasCommand.append(onto[f"c-camera{i}-start-video"])
                s_video.hasCommand.append(onto[f"c-camera{i}-stop-video"])

        # Speaker Services
        for i in range(1, 3):
            s_audio = OWLService._create_individual(onto, AudioRecordingService, f"s-speaker{i}-record-audio")
            if s_audio:
                s_audio.hasCommand.append(onto[f"c-speaker{i}-start-audio"])
                s_audio.hasCommand.append(onto[f"c-speaker{i}-stop-audio"])

        # Lamp Services
        for i in range(1, 4):
            s_light = OWLService._create_individual(onto, LightingService, f"s-lamp_{i}-lighting")
            if s_light:
                s_light.hasCommand.append(onto[f"c-lamp_{i}-turn-on"])
                s_light.hasCommand.append(onto[f"c-lamp_{i}-turn-off"])

        # Radiator Services
        for i in range(1, 3):
            s_heat = OWLService._create_individual(onto, HeatingService, f"s-radiator_{i}-heating")
            if s_heat:
                s_heat.hasCommand.append(onto[f"c-radiator_{i}-turn-on"])
                s_heat.hasCommand.append(onto[f"c-radiator_{i}-turn-off"])

        # Window Services
        for i in range(1, 3):
            s_frame = OWLService._create_individual(onto, FrameService, f"s-window_{i}-opening")
            if s_frame:
                s_frame.hasCommand.append(onto[f"c-window_{i}-open"])
                s_frame.hasCommand.append(onto[f"c-window_{i}-close"])
                s_frame.hasNotification.append(onto[f"n-window_{i}-open"])
                s_frame.hasNotification.append(onto[f"n-window_{i}-close"])

        # Timer Service
        s_timer = OWLService._create_individual(onto, TimerService, "s-caledar-alarm")
        if s_timer:
            s_timer.hasNotification.append(onto["n-calendar1-alarm"])

    @staticmethod
    def _create_devices(onto, base_onto, locations):
        Camera = OWLService._get_class(base_onto, "Camera")
        Lamp = OWLService._get_class(base_onto, "Lamp")
        Heater = OWLService._get_class(base_onto, "Heater")
        Speaker = OWLService._get_class(base_onto, "Speaker")
        SmartWindow = OWLService._get_class(base_onto, "SmartWindow")

        # Cameras
        # Camera 1: Living Room
        d_cam1 = OWLService._create_individual(onto, Camera, "d-camera1", props={"id": "camera-1"})
        if d_cam1:
            d_cam1.hasService.append(onto["s-camera1-record-audio"])
            d_cam1.hasService.append(onto["s-camera1-record-video"])
            d_cam1.position = [locations["location-livingroom"]]
            
        # Camera 2 & 3: Bedroom
        for i in range(2, 4):
            d_cam = OWLService._create_individual(onto, Camera, f"d-camera{i}", props={"id": f"camera-{i}"})
            if d_cam:
                d_cam.hasService.append(onto[f"s-camera{i}-record-audio"])
                d_cam.hasService.append(onto[f"s-camera{i}-record-video"])
                d_cam.position = [locations["location-bedroom"]]

        # Lamps
        # Lamp 1: Bedroom
        d_lamp1 = OWLService._create_individual(onto, Lamp, "d-lamp_1", props={"id": "lamp_1"})
        if d_lamp1:
            d_lamp1.hasService.append(onto["s-lamp_1-lighting"])
            d_lamp1.position = [locations["location-bedroom"]]
            
        # Lamp 2: Living Room
        d_lamp2 = OWLService._create_individual(onto, Lamp, "d_lamp_2", props={"id": "lamp_2"}) # Note: ptp-demo uses d_lamp_2 not d-lamp_2
        if d_lamp2:
            d_lamp2.hasService.append(onto["s-lamp_2-lighting"])
            d_lamp2.position = [locations["location-livingroom"]]
            
        # Lamp 3: Kitchen
        d_lamp3 = OWLService._create_individual(onto, Lamp, "d_lamp_3", props={"id": "lamp_3"})
        if d_lamp3:
            d_lamp3.hasService.append(onto["s-lamp_3-lighting"])
            d_lamp3.position = [locations["location-kitchen"]]

        # Radiators
        # Rad 1: Bedroom
        d_rad1 = OWLService._create_individual(onto, Heater, "d-radiator_1", props={"id": "radiator_valve_1"})
        if d_rad1:
            d_rad1.hasService.append(onto["s-radiator_1-heating"])
            d_rad1.position = [locations["location-bedroom"]]
            
        # Rad 2: Kitchen
        d_rad2 = OWLService._create_individual(onto, Heater, "d-radiator_2", props={"id": "radiator_valve_2"})
        if d_rad2:
            d_rad2.hasService.append(onto["s-radiator_2-heating"])
            d_rad2.position = [locations["location-kitchen"]]

        # Speakers
        # Speaker 1: Living Room
        d_spk1 = OWLService._create_individual(onto, Speaker, "d-speaker1", props={"id": "speaker-1"})
        if d_spk1:
            d_spk1.hasService.append(onto["s-speaker1-record-audio"])
            d_spk1.position = [locations["location-livingroom"]]
            
        # Speaker 2: Bedroom
        d_spk2 = OWLService._create_individual(onto, Speaker, "d-speaker2", props={"id": "speaker-2"})
        if d_spk2:
            d_spk2.hasService.append(onto["s-speaker2-record-audio"])
            d_spk2.position = [locations["location-bedroom"]]

        # Windows
        # Window 1: Bedroom
        d_win1 = OWLService._create_individual(onto, SmartWindow, "d-window_1", props={"id": "window_sensor_1"})
        if d_win1:
            d_win1.hasService.append(onto["s-window_1-opening"])
            d_win1.position = [locations["location-bedroom"]]
            
        # Window 2: Living Room
        d_win2 = OWLService._create_individual(onto, SmartWindow, "d-window_2", props={"id": "window_sensor_2"})
        if d_win2:
            d_win2.hasService.append(onto["s-window_2-opening"])
            d_win2.position = [locations["location-livingroom"]]
