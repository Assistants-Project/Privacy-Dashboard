# owl_service.py
import yaml
import logging
from pathlib import Path
from typing import Set, Dict, List, Optional
from owlready2 import *
from dataclasses import dataclass

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

    def get_triggers(self, service_id: str) -> List[Trigger]:
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
                    trigger_instance, service_id
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

    def get_actions(self, service_id: str) -> List[Action]:
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
                    action_instance, service_id
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
