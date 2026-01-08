from typing import Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ..db import DbTrigger, DbAction


@dataclass
class Detail:
    """Detail entity for OWL ontology.

    Represents a detail that can be associated with triggers or actions,
    containing information about parameters, values, and alternatives.
    """

    url: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[Any] = None
    trigger: Optional["DbTrigger"] = None
    action: Optional["DbAction"] = None
    alternatives: List[Any] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        """Check equality with another Detail instance.

        Args:
            other: Object to compare with

        Returns:
            True if both details are equal, False otherwise
        """
        if self is other:
            return True
        if not isinstance(other, Detail):
            return False
        return self.url == other.url and self.value == other.value

    def __str__(self) -> str:
        """String representation of the Detail.

        Returns:
            String representation showing name and value
        """
        return f"Detail [name={self.name}, value={self.value}]"

    def to_dict(self) -> dict:
        """Convert Detail to dictionary for JSON serialization.

        Returns:
            Dictionary with all detail data
        """
        return {
            "url": self.url,
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "alternatives": self.alternatives if self.alternatives else [],
        }
