from typing import Any, Optional, List
from dataclasses import dataclass, field


# Forward references for database models
# These should be imported from your actual database models if they exist
# Example: from app.models.entities import Dbtrigger, Dbaction


@dataclass
class Detail:
    """Detail entity for OWL ontology.
    
    Represents a detail that can be associated with triggers or actions,
    containing information about parameters, values, and alternatives.
    """
    
    URL: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[Any] = None
    trigger: Optional[Any] = None  # Replace 'Any' with Dbtrigger type when available
    action: Optional[Any] = None   # Replace 'Any' with Dbaction type when available
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
        return self.URL == other.URL and self.value == other.value
    
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
            'URL': self.URL,
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'alternatives': self.alternatives if self.alternatives else []
        }
