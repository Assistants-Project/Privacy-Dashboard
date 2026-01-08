"""Petri Net Arc entities."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .petri_net import PetriNet
    from .place import Place
    from .transition import Transition


class Arc:
    """An arc in a Petri Net."""

    def __init__(self, petri_net: "PetriNet"):
        self.petri_net = petri_net
        self.evaluate_text: str = ""
        self.execute_text: str = ""


class InputArc(Arc):
    """An arc from a place to a transition."""

    def __init__(self, petri_net: "PetriNet", place: "Place", transition: "Transition"):
        super().__init__(petri_net)
        self.place = place
        self.transition = transition

    def set_evaluate_text(self, text: str) -> None:
        """Set the evaluate text for this arc."""
        self.evaluate_text = text

    def __repr__(self) -> str:
        return f"InputArc({self.place} -> {self.transition})"


class OutputArc(Arc):
    """An arc from a transition to a place."""

    def __init__(self, petri_net: "PetriNet", place: "Place", transition: "Transition"):
        super().__init__(petri_net)
        self.place = place
        self.transition = transition

    def set_execute_text(self, text: str) -> None:
        """Set the execute text for this arc."""
        self.execute_text = text

    def __repr__(self) -> str:
        return f"OutputArc({self.transition} -> {self.place})"
