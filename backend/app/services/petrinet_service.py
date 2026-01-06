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
from ..models.entities.petrinet.rest_simulator import RestSimulator
from ..models.entities.petrinet.token import Token, TokenSet
from ..models.entities.sifis.owl.rule import Rule
from ..models.entities.sifis.owl.trigger import Trigger
from ..models.entities.sifis.owl.action import Action
from ..models.entities.sifis.owl.detail import Detail
from ..models.entities.sifis.owl.rule_problems import RuleProblems
from .owl_service import OWLService


class PetriNetService:
    """Service for handling Petri Net operations."""

    def __init__(self, owl_service: OWLService):
        self.owl_service = owl_service
        self.nets: Dict[str, ExtendedPetriNet] = {}
        self.simulators: Dict[str, RestSimulator] = {}
        self.logger = logging.getLogger()

    def get_net(
        self, home_uuid: str, rules: List[Rule], refresh: bool = False
    ) -> ExtendedPetriNet:
        """
        Get or build a Petri Net for a home's rules.

        Args:
            home_uuid: Home UUID to get net for
            rules: List of rules
            refresh: Force rebuild of net

        Returns:
            ExtendedPetriNet for the rules
        """
        if refresh:
            petri_net = self._build_net(home_uuid, rules)
            self.nets[home_uuid] = petri_net
            return petri_net

        petri_net = self.nets.get(home_uuid)
        if petri_net is None:
            petri_net = self._build_net(home_uuid, rules)
            self.nets[home_uuid] = petri_net

        return petri_net

    def get_rest_simulator(self, home_uuid: str) -> Optional[RestSimulator]:
        """Get the active simulator for a home."""
        return self.simulators.get(home_uuid)

    def start_rest_simulation(
        self, trigger: Trigger, rules: List[Rule], home_uuid: str
    ) -> Optional[Rule]:
        """
        Start a step-by-step simulation.
        
        Args:
            trigger: The initial trigger to fire
            rules: List of rules to simulate
            home_uuid: Home context
            
        Returns:
            The first rule executed, or None
        """
        net = self.get_net(home_uuid, rules, refresh=False)
        
        # Add the token for the simulation
        net.remove_all_tokens()
        
        trigger_place = net.get_trigger_place(trigger)
        if not trigger_place:
            self.logger.error(f"Trigger place not found for {trigger}")
            return None
            
        token = Token(trigger_place.trigger)
        token.set_initial_marking_expression("1")
        trigger_place.add_token(TokenSet(token))
        
        simulator = RestSimulator(net)
        self.simulators[home_uuid] = simulator
        
        return simulator.step()

    def step_rest_simulation(self, home_uuid: str) -> Optional[Rule]:
        """
        Execute the next step in the simulation.
        
        Args:
            home_uuid: Home context
            
        Returns:
            The next rule executed, or None
        """
        simulator = self.simulators.get(home_uuid)
        if simulator:
            return simulator.step()
        return None


    def check_rule(self, target_rule: Rule, existing_rules: List[Rule], home_uuid: str) -> Dict:
        """
        Check a rule for loops using Petri Nets.
        
        Args:
            target_rule: The rule to check
            existing_rules: List of all user's rules
            home_uuid: Home UUID string
            
        Returns:
            Dictionary containing rule problems (loops, etc.)
        """
        # Initialize RuleProblems
        rule_problems = RuleProblems()
        rule_problems.rule = target_rule

        # Prepare rules list for analysis
        rules_after = existing_rules.copy()
        
        # If target rule updates an existing one (same DB ID), remove the old version
        if target_rule.db_id:
            rules_after = [r for r in rules_after if r.db_id != target_rule.db_id]
        
        # Add the target rule to the set
        rules_after.append(target_rule)

        for existing_rule in existing_rules:
            # Skip comparing rule to itself (by ID)
            if existing_rule.db_id == target_rule.db_id:
                continue
                
            # Trigger Equality Check
            triggers_match = (
                target_rule.trigger.url == existing_rule.trigger.url
                and target_rule.trigger.details == existing_rule.trigger.details
            )
            
            if triggers_match:
                # Actions Equality Check
                actions_match = (
                    target_rule.action.url == existing_rule.action.url
                    and target_rule.action.details == existing_rule.action.details
                )
                
                if actions_match:
                    # Check Effect (Permit vs Deny)
                    if target_rule.effect == existing_rule.effect:
                        # Exact duplicate: Same T, Same A, Same E
                        rule_problems.add_redundant_rules([target_rule, existing_rule])
                    else:
                        # Conflict: Same T, Same A, Different E (Permit vs Deny)
                        rule_problems.add_inconsistent_rules([target_rule, existing_rule])



        # Build Petri Net
        net = self.get_net(home_uuid, rules_after, refresh=True)

        # Search for loops
        cycles = net.get_cycle(target_rule, rules_after)

        if cycles and len(cycles) > 0:
            for cycle in cycles:
                current_loop_rules = []
                
                # Iterate through the cycle to find Rules corresponding to transitions
                num_places = len(cycle)
                for i in range(num_places):
                    current_place = cycle[i]
                    next_place = cycle[(i + 1) % num_places] # Wrap around
                    
                    if isinstance(current_place, TriggerPlace) and isinstance(next_place, ActionPlace):
                        trigger = current_place.get_trigger()
                        action = next_place.get_action()
                        
                        # Find matching rule in existing set
                        for rule in rules_after:
                            if (rule.trigger.url == trigger.url and 
                                rule.action.url == action.url):
                                current_loop_rules.append(rule)
                                break
                
                if current_loop_rules:
                    rule_problems.add_loop(current_loop_rules)
                else:
                    # Fallback: report the target rule to alert the user if we couldn't extract rules.
                    rule_problems.add_loop([target_rule])

        return rule_problems.to_dict()
    def stop_rest_simulator(self, home_uuid: str) -> None:
        """
        Stop the simulation for a home.
        
        Args:
            home_uuid: Home context
        """
        if home_uuid in self.simulators:
            del self.simulators[home_uuid]

    def _build_net(self, home_uuid: str, rules: List[Rule]) -> ExtendedPetriNet:
        """
        Build a Petri Net from a list of rules.

        Args:
            home_uuid: Home UUID building net for
            rules: List of rules to build net from

        Returns:
            ExtendedPetriNet representing the rules
        """
        petri_net = ExtendedPetriNet()
        petri_net.set_label(home_uuid)

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


