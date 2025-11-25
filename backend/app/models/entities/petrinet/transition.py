"""Petri Net Transition entities."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .petri_net import PetriNet
    from ...sifis.owl.rule import Rule
    from ...sifis.owl.trigger import Trigger
    from ...sifis.owl.action import Action


class Transition:
    """A transition in a Petri Net."""

    def __init__(self, petri_net: "PetriNet"):
        self.petri_net = petri_net
        self.label: str = ""

    def enabled(self) -> bool:
        """Check if this transition is enabled (can fire)."""
        # A transition is enabled if all its input places have tokens
        for arc in self.petri_net.input_arcs:
            if arc.transition == self:
                if not arc.place.get_tokens():
                    return False
        return True

    def fire(self) -> None:
        """Fire this transition (move tokens from input to output places)."""
        # Remove tokens from input places
        for arc in self.petri_net.input_arcs:
            if arc.transition == self:
                tokens = arc.place.get_tokens()
                if tokens:
                    arc.place.remove_tokens(tokens)

        # Add tokens to output places
        for arc in self.petri_net.output_arcs:
            if arc.transition == self:
                # Get token from first input place or create new one
                from .token import Token, TokenSet

                token = Token(None)
                arc.place.add_token(TokenSet(token))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transition):
            return False
        return self.label == other.label

    def __hash__(self) -> int:
        return hash(self.label)

    def __repr__(self) -> str:
        return f"Transition({self.label})"


class RuleTransition(Transition):
    """A transition representing a rule."""

    def __init__(self, petri_net: "PetriNet", rule: "Rule"):
        super().__init__(petri_net)
        self.rule = rule
        self.label = f"rule_{rule.db_id}"

    def get_rule(self) -> "Rule":
        """Get the rule associated with this transition."""
        return self.rule

    def fire_and_get_rule(self) -> "Rule":
        """Fire this transition and return the associated rule."""
        self.fire()
        return self.rule

    def __repr__(self) -> str:
        return f"RuleTransition({self.rule})"


class TriggerTransition(Transition):
    """A transition that triggers another place."""

    def __init__(self, petri_net: "PetriNet", trigger: "Trigger", action: "Action"):
        super().__init__(petri_net)
        self.trigger = trigger
        self.action = action
        self.label = f"trigger_{trigger.url}_from_{action.url}"

    def __repr__(self) -> str:
        return f"TriggerTransition({self.trigger.url} from {self.action.url})"


class CopyTransition(Transition):
    """A transition that copies tokens to multiple places."""

    def __init__(self, petri_net: "PetriNet", source):
        super().__init__(petri_net)
        self.source = source
        if hasattr(source, "url"):
            self.label = f"copy_{source.url}"
        else:
            self.label = f"copy_{str(source)}"

    def __repr__(self) -> str:
        return f"CopyTransition({self.label})"
