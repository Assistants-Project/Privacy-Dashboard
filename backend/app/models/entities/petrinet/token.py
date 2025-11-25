"""Petri Net Token entities."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...sifis.owl.trigger import Trigger


class Token:
    """A token in a Petri Net."""

    def __init__(self, value: Any):
        self.value = value
        self.initial_marking_expression: str = ""

    def set_initial_marking_expression(self, expression: str) -> None:
        """Set the initial marking expression for this token."""
        self.initial_marking_expression = expression

    def __repr__(self) -> str:
        return f"Token({self.value})"


class TokenSet:
    """A set of tokens."""

    def __init__(self, token: Token):
        self.token = token

    def get_token(self) -> Token:
        """Get the token in this set."""
        return self.token

    def __repr__(self) -> str:
        return f"TokenSet({self.token})"
