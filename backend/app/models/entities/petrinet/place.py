"""Petri Net Place entities."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .petri_net import PetriNet
    from .token import TokenSet
    from ...sifis.owl.trigger import Trigger
    from ...sifis.owl.action import Action


class Place:
    """A place in a Petri Net."""

    def __init__(self, petri_net: "PetriNet"):
        self.petri_net = petri_net
        self.label: Optional[str] = None
        self.tokens: Optional["TokenSet"] = None

    def add_token(self, token_set: "TokenSet") -> None:
        """Add tokens to this place."""
        self.tokens = token_set

    def remove_tokens(self, token_set: "TokenSet") -> None:
        """Remove tokens from this place."""
        self.tokens = None

    def get_tokens(self) -> Optional["TokenSet"]:
        """Get the tokens in this place."""
        return self.tokens

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Place):
            return False
        return self.label == other.label

    def __hash__(self) -> int:
        return hash(self.label)

    def __repr__(self) -> str:
        return f"Place({self.label})"


class TriggerPlace(Place):
    """A place representing a trigger in a Petri Net."""

    def __init__(self, petri_net: "PetriNet", trigger: "Trigger"):
        super().__init__(petri_net)
        self.trigger = trigger

    def get_trigger(self) -> "Trigger":
        """Get the trigger associated with this place."""
        return self.trigger

    def __repr__(self) -> str:
        return f"TriggerPlace({self.trigger.url})"


class ActionPlace(Place):
    """A place representing an action in a Petri Net."""

    def __init__(self, petri_net: "PetriNet", action: "Action"):
        super().__init__(petri_net)
        self.action = action

    def get_action(self) -> "Action":
        """Get the action associated with this place."""
        return self.action

    def __repr__(self) -> str:
        return f"ActionPlace({self.action.url})"
