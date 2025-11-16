from typing import List, Optional
from dataclasses import dataclass, field

from .detail import Detail
from .service import Service


@dataclass
class Action:
    """Action entity for OWL ontology."""

    url: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    service: Optional[Service] = None
    details: List[Detail] = field(default_factory=list)

    def add_detail(self, detail: Detail) -> None:
        """Add a detail to the action's details list.

        Args:
            detail: The Detail object to add
        """
        self.details.append(detail)

    def __eq__(self, other: object) -> bool:
        """Check equality with another Action instance.

        Args:
            other: Object to compare with

        Returns:
            True if both actions are equal, False otherwise
        """
        if self is other:
            return True
        if not isinstance(other, Action):
            return False
        return (
            self.url == other.url
            and self.details == other.details
            and self.service == other.service
        )

    def __str__(self) -> str:
        """String representation of the Action.

        Returns:
            String representation showing id and details
        """
        return f"Action [id={self.id}, details={self.details}]"

    def to_dict(self) -> dict:
        """Convert Action to dictionary for JSON serialization.
        
        Returns:
            Dictionary with all action data
        """
        return {
            'url': self.url,
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'service': self.service.to_dict() if self.service else None,
            'details': [d.to_dict() if hasattr(d, 'to_dict') else d.__dict__ for d in self.details] if self.details else []
        }
