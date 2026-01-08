from typing import Optional
from dataclasses import dataclass


@dataclass
class Command:
    """Command entity for OWL ontology."""

    url: Optional[str] = None
    id: Optional[str] = None
    type: Optional[str] = None
    entity: Optional[dict] = None  # IoTEntity as dict

    def __eq__(self, other: object) -> bool:
        """Check equality with another Command instance based on URL.

        Args:
            other: Object to compare with

        Returns:
            True if both commands have the same URL, False otherwise
        """
        if self is other:
            return True
        if not isinstance(other, Command):
            return False
        if self.url is None:
            return other.url is None
        return self.url == other.url

    def __hash__(self) -> int:
        """Hash implementation for Command based on URL.

        Returns:
            Hash value based on URL
        """
        return hash(self.url) if self.url else 0

    def to_dict(self) -> dict:
        """Convert Command to dictionary for JSON serialization.

        Returns:
            Dictionary with all command data
        """
        return {
            "url": self.url,
            "id": self.id,
            "type": self.type,
            "entity": self.entity,
        }
