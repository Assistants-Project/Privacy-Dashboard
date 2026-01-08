"""Petri Net data structures for rule analysis."""

from typing import List, Dict, Optional, Set, TYPE_CHECKING

import networkx as nx

from .place import Place, TriggerPlace, ActionPlace
from .transition import Transition
from .arc import InputArc, OutputArc

if TYPE_CHECKING:
    from ..sifis.owl.trigger import Trigger
    from ..sifis.owl.action import Action
    from ..sifis.owl.rule import Rule


class PetriNet:
    """Base Petri Net structure."""

    def __init__(self):
        self.label: str = ""
        self.places: List[Place] = []
        self.transitions: List[Transition] = []
        self.input_arcs: List[InputArc] = []
        self.output_arcs: List[OutputArc] = []

    def add_place(self, place: Place) -> None:
        """Add a place to the Petri Net."""
        if place not in self.places:
            self.places.append(place)

    def add_transition(self, transition: Transition) -> None:
        """Add a transition to the Petri Net."""
        if transition not in self.transitions:
            self.transitions.append(transition)

    def add_input_arc(self, arc: InputArc) -> None:
        """Add an input arc to the Petri Net."""
        self.input_arcs.append(arc)

    def add_output_arc(self, arc: OutputArc) -> None:
        """Add an output arc to the Petri Net."""
        self.output_arcs.append(arc)

    def get_places(self) -> List[Place]:
        """Get all places in the Petri Net."""
        return self.places

    def set_label(self, label: str) -> None:
        """Set the label for this Petri Net."""
        self.label = label

    def remove_all_tokens(self) -> None:
        """Remove all tokens from all places."""
        for place in self.places:
            try:
                tokens = place.get_tokens()
                if tokens:
                    place.remove_tokens(tokens)
            except Exception:
                pass

    def get_transitions(self) -> List[Transition]:
        """Get all transitions in the Petri Net."""
        return self.transitions

    def is_dead(self) -> bool:
        """Check if the Petri Net is in a deadlock state (no enabled transitions)."""
        for transition in self.transitions:
            if transition.enabled():
                return False
        return True


class ExtendedPetriNet(PetriNet):
    """Extended Petri Net with graph analysis capabilities."""

    def __init__(self):
        super().__init__()
        self.trigger_places: Dict["Trigger", TriggerPlace] = {}
        self.action_places: Dict["Action", ActionPlace] = {}
        self.graph: nx.DiGraph = nx.DiGraph()

    def add_trigger_place(self, place: TriggerPlace) -> None:
        """Add a trigger place if not already present."""
        if place.trigger not in self.trigger_places:
            self.trigger_places[place.trigger] = place

    def add_action_place(self, place: ActionPlace) -> None:
        """Add an action place if not already present."""
        if place.action not in self.action_places:
            self.action_places[place.action] = place

    def get_action_place(self, action: "Action") -> Optional[ActionPlace]:
        """Get the action place for a given action."""
        return self.action_places.get(action)

    def get_trigger_place(self, trigger: "Trigger") -> Optional[TriggerPlace]:
        """Get the trigger place for a given trigger."""
        return self.trigger_places.get(trigger)

    def add_graph_vertex(self, place: Place) -> None:
        """Add a vertex to the graph."""
        self.graph.add_node(place)

    def add_graph_edge(self, place1: Place, place2: Place) -> None:
        """Add an edge to the graph."""
        self.graph.add_edge(place1, place2)

    def get_graph(self) -> nx.DiGraph:
        """Get the NetworkX directed graph."""
        return self.graph

    def get_root(self, rule: "Rule") -> Optional["Trigger"]:
        """
        Get the root trigger for a rule by finding the connected component
        and returning the trigger with in-degree of 0.

        Args:
            rule: Rule to find the root for

        Returns:
            The root trigger, or None if not found
        """
        trigger_place = self.trigger_places.get(rule.trigger)
        if not trigger_place:
            return None

        # Get the connected component containing this trigger place
        if not nx.is_weakly_connected(self.graph):
            # Find the weakly connected component containing trigger_place
            for component in nx.weakly_connected_components(self.graph):
                if trigger_place in component:
                    connected_component = component
                    break
            else:
                return None
        else:
            connected_component = set(self.graph.nodes())

        # Find the root (node with in-degree 0)
        for place in connected_component:
            if self.graph.in_degree(place) == 0:
                if isinstance(place, TriggerPlace):
                    return place.get_trigger()

        return None

    def get_cycle(
        self, rule: "Rule", rules: List["Rule"]
    ) -> Optional[List[List[Place]]]:
        """
        Detect cycles in the Petri Net graph.

        Args:
            rule: Rule to check for cycles
            rules: List of all rules

        Returns:
            List of cycles (each cycle is a list of places), or None if no cycles
        """
        try:
            # Find all simple cycles using NetworkX
            cycles = list(nx.simple_cycles(self.graph))

            if not cycles:
                return None

            # Convert node lists to Place lists
            cycle_places = []
            for cycle in cycles:
                cycle_places.append(list(cycle))

            return cycle_places if cycle_places else None

        except Exception as e:
            print(f"Error detecting cycles: {e}")
            return None

    def get_simulated_rules(self, trigger: "Trigger") -> List["Rule"]:
        """
        Simulate the Petri Net starting from a trigger using token game semantics.

        This matches the Java implementation which:
        1. Removes all tokens
        2. Adds a token to the start trigger place
        3. Runs the simulation
        4. Returns the list of executed rules

        Args:
            trigger: Starting trigger

        Returns:
            List of simulated rules
        """
        from .simulation import Simulation
        from .token import Token, TokenSet

        # Remove all tokens
        self.remove_all_tokens()

        # Get the trigger place and add a token
        trigger_place = self.trigger_places.get(trigger)
        if not trigger_place:
            return []

        token = Token(trigger)
        token.set_initial_marking_expression("1")
        trigger_place.add_token(TokenSet(token))

        # Run simulation
        simulator = Simulation(self, step=False)
        simulator.run()

        # Alternatively, run with timeout like Java
        import threading

        sim_thread = threading.Thread(target=simulator.run)
        sim_thread.daemon = True
        sim_thread.start()
        sim_thread.join(timeout=1.0)  # 1 second timeout like Java

        if sim_thread.is_alive():
            simulator.set_stop(True)
            sim_thread.join(timeout=0.5)
            print("Possible loops detected")

        return simulator.get_simulated_rules()
