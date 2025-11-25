"""Service for building and analyzing Petri Nets from rules."""

import logging
from typing import Dict, List, Optional

from ..models.entities.petrinet import (
    ExtendedPetriNet,
    TriggerPlace,
    ActionPlace,
    Place,
    RuleTransition,
    TriggerTransition,
    CopyTransition,
    InputArc,
    OutputArc,
)
from ..models.entities.sifis.owl.rule import Rule
from ..models.entities.sifis.owl.trigger import Trigger
from ..models.entities.sifis.owl.action import Action
from ..models.entities.sifis.owl.detail import Detail
from .owl_service import OWLService


class PetriNetService:
    """Service for handling Petri Net operations."""

    def __init__(self, owl_service: OWLService):
        self.owl_service = owl_service
        self.nets: Dict[str, ExtendedPetriNet] = {}
        self.logger = logging.getLogger()

    def get_net(
        self, username: str, rules: List[Rule], refresh: bool = False
    ) -> ExtendedPetriNet:
        """
        Get or build a Petri Net for a user's rules.

        Args:
            username: Username to get net for
            rules: List of rules
            refresh: Force rebuild of net

        Returns:
            ExtendedPetriNet for the rules
        """
        if refresh:
            petri_net = self._build_net(username, rules)
            self.nets[username] = petri_net
            return petri_net

        petri_net = self.nets.get(username)
        if petri_net is None:
            petri_net = self._build_net(username, rules)
            self.nets[username] = petri_net

        return petri_net

    def _build_net(self, username: str, rules: List[Rule]) -> ExtendedPetriNet:
        """
        Build a Petri Net from a list of rules.

        Args:
            username: Username building net for
            rules: List of rules to build net from

        Returns:
            ExtendedPetriNet representing the rules
        """
        petri_net = ExtendedPetriNet()
        petri_net.set_label(username)

        # Loading unique places
        for rule in rules:
            trigger_place = TriggerPlace(petri_net, rule.trigger)
            trigger_place.label = str(rule.trigger)
            petri_net.add_trigger_place(trigger_place)
            petri_net.add_place(trigger_place)

            action_place = ActionPlace(petri_net, rule.action)
            action_place.label = str(rule.action)
            petri_net.add_action_place(action_place)
            petri_net.add_place(action_place)

        # Adding unique places to the graph
        for trigger_place in petri_net.trigger_places.values():
            petri_net.add_graph_vertex(trigger_place)
        for action_place in petri_net.action_places.values():
            petri_net.add_graph_vertex(action_place)

        # Search for trigger copies
        for trigger_place in petri_net.trigger_places.values():
            rules_by_trigger = self._get_by_trigger(rules, trigger_place.trigger)

            if len(rules_by_trigger) == 1:
                # Attach the action place directly with the unique trigger place
                rule = rules_by_trigger[0]
                action_place = petri_net.get_action_place(rule.action)

                rule_transition = RuleTransition(petri_net, rule)
                petri_net.add_transition(rule_transition)

                rule_arc1 = InputArc(petri_net, trigger_place, rule_transition)
                rule_arc1.set_evaluate_text("Token > 0")
                petri_net.add_input_arc(rule_arc1)

                rule_arc2 = OutputArc(petri_net, action_place, rule_transition)
                rule_arc2.set_execute_text(f"new {rule.action}")
                petri_net.add_output_arc(rule_arc2)

                petri_net.add_graph_edge(trigger_place, action_place)

            elif len(rules_by_trigger) > 1:
                # Create the copy transition
                copy_transition = CopyTransition(petri_net, trigger_place.trigger)
                petri_net.add_transition(copy_transition)

                copy_arc1 = InputArc(petri_net, trigger_place, copy_transition)
                copy_arc1.set_evaluate_text("Token > 0")
                petri_net.add_input_arc(copy_arc1)

                # Create copied places
                for rule in rules_by_trigger:
                    copy_place = Place(petri_net)
                    copy_place.label = f"copy_of_{rule.trigger}"
                    petri_net.add_place(copy_place)

                    # Attach the copied place to the original one
                    copy_arc2 = OutputArc(petri_net, copy_place, copy_transition)
                    copy_arc2.set_execute_text("Copy the token")
                    petri_net.add_output_arc(copy_arc2)

                    # Attach the copied place to the relative action
                    action_place = petri_net.get_action_place(rule.action)
                    rule_transition = RuleTransition(petri_net, rule)
                    petri_net.add_transition(rule_transition)

                    rule_arc1 = InputArc(petri_net, copy_place, rule_transition)
                    rule_arc1.set_evaluate_text("Token > 0")
                    petri_net.add_input_arc(rule_arc1)

                    rule_arc2 = OutputArc(petri_net, action_place, rule_transition)
                    rule_arc2.set_execute_text(f"new {rule.action}")
                    petri_net.add_output_arc(rule_arc2)

                    petri_net.add_graph_edge(trigger_place, action_place)

        # Adding trigger transitions
        for action_place in petri_net.action_places.values():
            triggered_rules = self._get_triggered_rules(rules, action_place.action)
            triggered_triggers = set(rule.trigger for rule in triggered_rules)

            if len(triggered_triggers) == 1:
                # Attach the action place directly with the triggered place
                trigger = list(triggered_triggers)[0]
                trigger_place = petri_net.get_trigger_place(trigger)

                trigger_transition = TriggerTransition(
                    petri_net, trigger, action_place.action
                )
                petri_net.add_transition(trigger_transition)

                rule_arc1 = InputArc(petri_net, action_place, trigger_transition)
                rule_arc1.set_evaluate_text("Token > 0")
                petri_net.add_input_arc(rule_arc1)

                rule_arc2 = OutputArc(petri_net, trigger_place, trigger_transition)
                rule_arc2.set_execute_text(f"new {trigger}")
                petri_net.add_output_arc(rule_arc2)

                petri_net.add_graph_edge(action_place, trigger_place)

            elif len(triggered_triggers) > 1:
                # Duplicate the action place and attach each copy to the relative triggered place
                copy_transition = CopyTransition(petri_net, action_place.action)
                petri_net.add_transition(copy_transition)

                copy_arc1 = InputArc(petri_net, action_place, copy_transition)
                copy_arc1.set_evaluate_text("Token > 0")
                petri_net.add_input_arc(copy_arc1)

                # Create copied places
                for trigger in triggered_triggers:
                    copy_place = Place(petri_net)
                    copy_place.label = f"copy_of_{action_place.action}"
                    petri_net.add_place(copy_place)

                    # Attach the copied place to the original one
                    copy_arc2 = OutputArc(petri_net, copy_place, copy_transition)
                    copy_arc2.set_execute_text("Copy the token")
                    petri_net.add_output_arc(copy_arc2)

                    # Attach the copied place to the relative trigger
                    trigger_place = petri_net.get_trigger_place(trigger)
                    trigger_transition = TriggerTransition(
                        petri_net, trigger_place.trigger, action_place.action
                    )
                    petri_net.add_transition(trigger_transition)

                    rule_arc1 = InputArc(petri_net, copy_place, trigger_transition)
                    rule_arc1.set_evaluate_text("Token > 0")
                    petri_net.add_input_arc(rule_arc1)

                    rule_arc2 = OutputArc(petri_net, trigger_place, trigger_transition)
                    rule_arc2.set_execute_text(f"new {trigger}")
                    petri_net.add_output_arc(rule_arc2)

                    petri_net.add_graph_edge(action_place, trigger_place)

        return petri_net

    def _get_by_trigger(self, ruleset: List[Rule], trigger: Trigger) -> List[Rule]:
        """
        Get all rules with a specific trigger.

        Args:
            ruleset: List of rules to search
            trigger: Trigger to match

        Returns:
            List of rules with the trigger
        """
        rules = []
        for rule in ruleset:
            if rule.trigger == trigger:
                rules.append(rule)
        return rules

    def _get_triggered_rules(self, ruleset: List[Rule], action: Action) -> List[Rule]:
        """
        Get rules that are triggered by an action.

        Args:
            ruleset: List of rules to search
            action: Action that triggers rules

        Returns:
            List of rules triggered by the action
        """
        rules = []
        for rule in ruleset:
            if action.service == rule.trigger.service:
                # Trigger and action act on the same service: possible implication

                # Check entity
                same_entity = False
                for action_detail in action.details:
                    if action_detail.type == "entity" and hasattr(
                        action_detail.value, "url"
                    ):
                        action_entity = action_detail.value
                        for trigger_detail in rule.trigger.details:
                            if trigger_detail.type == "entity" and hasattr(
                                trigger_detail.value, "url"
                            ):
                                trigger_entity = trigger_detail.value
                                if trigger_entity.url == action_entity.url:
                                    same_entity = True

                if same_entity:
                    if self.owl_service.triggers(action, rule.trigger):
                        rules.append(rule)

        return rules

    def get_parents(
        self, simulated_rule: Rule, executed_rules: List[Rule]
    ) -> List[Rule]:
        """
        Get parent rules that trigger the simulated rule.

        Args:
            simulated_rule: Rule being simulated
            executed_rules: List of already executed rules

        Returns:
            List of parent rules
        """
        rules = []
        for executed_rule in executed_rules:
            if executed_rule.action.service == simulated_rule.trigger.service:
                # Check entity
                same_entity = False
                for action_detail in executed_rule.action.details:
                    if action_detail.type == "entity" and hasattr(
                        action_detail.value, "url"
                    ):
                        action_entity = action_detail.value
                        for trigger_detail in simulated_rule.trigger.details:
                            if trigger_detail.type == "entity" and hasattr(
                                trigger_detail.value, "url"
                            ):
                                trigger_entity = trigger_detail.value
                                if trigger_entity.url == action_entity.url:
                                    same_entity = True

                if same_entity:
                    if self.owl_service.triggers(
                        executed_rule.action, simulated_rule.trigger
                    ):
                        rules.append(executed_rule)

        return rules
