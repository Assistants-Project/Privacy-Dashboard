from __future__ import annotations

from typing import Optional, Set, TYPE_CHECKING
from dataclasses import dataclass, field
from functools import total_ordering

if TYPE_CHECKING:
    from .trigger import Trigger
    from .action import Action


@total_ordering
@dataclass
class Service:
    """Service entity for OWL ontology.

    Implements comparison based on web_id for sorting services.
    """

    url: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    color: Optional[str] = None
    web_id: Optional[int] = None
    image: Optional[str] = None
    triggers: Set[Trigger] = field(default_factory=set)
    actions: Set[Action] = field(default_factory=set)

    def __lt__(self, other: "Service") -> bool:
        """Less than comparison based on web_id.

        Args:
            other: Another Service instance to compare with

        Returns:
            True if this service's web_id is less than the other's
        """
        if not isinstance(other, Service):
            return NotImplemented

        # Handle None values - treat None as smallest value
        if self.web_id is None and other.web_id is None:
            return False
        if self.web_id is None:
            return True
        if other.web_id is None:
            return False

        return self.web_id < other.web_id

    def __eq__(self, other: object) -> bool:
        """Check equality with another Service instance based on url.

        Args:
            other: Object to compare with

        Returns:
            True if both services have the same url, False otherwise
        """
        if self is other:
            return True
        if not isinstance(other, Service):
            return False
        return self.url == other.url

    def __str__(self) -> str:
        """String representation of the Service.

        Returns:
            String representation showing id and name
        """
        return f"Service [id={self.id}, name={self.name}, web_id={self.web_id}]"

    def to_dict(self) -> dict:
        """Convert Service to dictionary for JSON serialization.

        Returns:
            Dictionary with all service data, converting sets to lists
        """
        return {
            "url": self.url,
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "web_id": self.web_id,
            "image": self.image,
            "triggers": (
                [
                    t.to_dict() if hasattr(t, "to_dict") else t.__dict__
                    for t in self.triggers
                ]
                if self.triggers
                else []
            ),
            "actions": (
                [
                    a.to_dict() if hasattr(a, "to_dict") else a.__dict__
                    for a in self.actions
                ]
                if self.actions
                else []
            ),
        }
