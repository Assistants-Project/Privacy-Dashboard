"""Petri Net Simulation engine for token game execution."""

import time
import random
from typing import List, TYPE_CHECKING

from .transition import Transition, RuleTransition

if TYPE_CHECKING:
    from .petri_net import PetriNet
    from ...sifis.owl.rule import Rule
    from ...sifis.owl.action import Action


class Simulation:
    """
    Simulates Petri Net execution using token game semantics.

    This matches the Java Simulation class which fires transitions
    and tracks which rules are executed.
    """

    # Time delays (in seconds)
    DELAY = 0
    COMPONENT_DELAY = 0.1

    def __init__(self, net: "PetriNet", step: bool = False):
        """
        Initialize the simulation.

        Args:
            net: The Petri Net to simulate
            step: Whether to step through transitions one at a time
        """
        self.net = net
        self.step = step
        self.paused = False
        self.stop = False
        self.finished = False

        self.simulated_actions: List["Action"] = []
        self.simulated_rules: List["Rule"] = []

    def run(self) -> None:
        """Run the simulation until finished or stopped."""
        while not self.is_finished() and not self.stop:
            self.fire_transition()

        if self.stop:
            print("Simulation stopped.")
        else:
            print("Simulation reached deadlock.")

        self.finished = True

    def is_finished(self) -> bool:
        """Check if simulation has ended (deadlock or no enabled transitions)."""
        return self.net.is_dead()

    def fire_transition(self) -> None:
        """Fire a single transition from the enabled transitions."""
        # First fire all enabled rule transitions
        enabled_rule_transitions = self.enabled_rule_transition_list()
        while enabled_rule_transitions:
            transition = self.get_random_rule_transition(enabled_rule_transitions)
            rule = transition.fire_and_get_rule()
            self.simulated_actions.append(rule.action)
            self.simulated_rules.append(rule)
            enabled_rule_transitions = self.enabled_rule_transition_list()

        # Then fire other transitions
        enabled_transitions = self.enabled_transition_list()
        if enabled_transitions:
            transition = self.get_random_transition(enabled_transitions)
            transition.fire()

        self.pause_resume_simulation()

    def pause_resume_simulation(self) -> None:
        """Handle pausing/resuming of simulation."""
        if self.step and not self.stop:
            self.paused = True
            # In a real implementation, this would wait for user input
            # For now, we'll just continue
            self.paused = False
        else:
            if self.DELAY > 0:
                time.sleep(self.DELAY)

    def get_random_rule_transition(
        self, enabled_transitions: List[RuleTransition]
    ) -> RuleTransition:
        """Get a random rule transition from the enabled list."""
        return random.choice(enabled_transitions)

    def get_random_transition(
        self, enabled_transitions: List[Transition]
    ) -> Transition:
        """Get a random transition from the enabled list."""
        return random.choice(enabled_transitions)

    def enabled_transition_list(self) -> List[Transition]:
        """Get list of all enabled transitions."""
        enabled = []
        for transition in self.net.get_transitions():
            if transition.enabled():
                enabled.append(transition)
        return enabled

    def enabled_rule_transition_list(self) -> List[RuleTransition]:
        """Get list of all enabled rule transitions."""
        enabled = []
        for transition in self.net.get_transitions():
            if isinstance(transition, RuleTransition) and transition.enabled():
                enabled.append(transition)
        return enabled

    def get_simulated_rules(self) -> List["Rule"]:
        """Get the list of rules that were simulated."""
        return self.simulated_rules

    def set_stop(self, stop: bool) -> None:
        """Set the stop flag to terminate simulation."""
        self.stop = stop
