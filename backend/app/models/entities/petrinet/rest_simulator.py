"""RestSimulator for step-by-step Petri Net execution."""

import random
from typing import List, Optional, TYPE_CHECKING

from .transition import Transition, RuleTransition

if TYPE_CHECKING:
    from .petri_net import PetriNet
    from ...sifis.owl.rule import Rule


class RestSimulator:
    """
    Simulator for interactive Petri Net execution.
    
    Mirrors the Java RestSimulator logic:
    - step(): executes transitions until a RuleTransition is fired
    - fire_transition(): random walk through enabled transitions
    """

    def __init__(self, net: "PetriNet"):
        self.net = net
        self.paused = False
        self.stop = False

    def step(self) -> Optional["Rule"]:
        """
        Execute a step in the simulation.
        Returns the Rule that was executed, or None if finished/deadlock.
        """
        if not self.is_finished():
            return self.fire_transition()
        return None

    def fire_transition(self) -> Optional["Rule"]:
        """
        Fire transitions until a RuleTransition is executed.
        Non-rule transitions (copy, trigger) are fired automatically.
        """
        enabled = self.enabled_transition_list()
        
        if enabled:
            t = self.get_random_transition()
            
            # if the transition is a Copy or Triggers transition -> fire anyway
            # Loop until we find a RuleTransition or run out of enabled transitions
            while not isinstance(t, RuleTransition):
                t.fire()
                
                # Check if we still have enabled transitions after firing
                if not self.enabled_transition_list():
                    return None
                
                t = self.get_random_transition()
            
            # There is a Rule transition -> fire the transition and return the activated rule
            return t.fire_and_get_rule()
            
        return None

    def is_finished(self) -> bool:
        """Checks whether the Simulation has ended"""
        return self.net.is_dead()

    def get_random_transition(self) -> Transition:
        """Returns a random transition from the enabled transition list"""
        enabled_transitions = self.enabled_transition_list()
        return random.choice(enabled_transitions)

    def enabled_transition_list(self) -> List[Transition]:
        """Returns a list of enabled transitions"""
        enabled_transitions = []
        for transition in self.net.get_transitions():
            if transition.enabled():
                enabled_transitions.append(transition)
        return enabled_transitions
