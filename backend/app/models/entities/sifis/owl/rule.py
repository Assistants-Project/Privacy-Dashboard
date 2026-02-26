from typing import List, Optional
from dataclasses import dataclass, field

from .trigger import Trigger
from .action import Action


@dataclass
class Rule:
    """Rule entity for OWL ontology."""

    db_id: Optional[int] = None
    rule_uuid: Optional[str] = None
    consent_uuid: Optional[str] = None
    trigger: Optional[Trigger] = None
    action: Optional[Action] = None
    parents: List["Rule"] = field(default_factory=list)
    timestamp: Optional[int] = None
    type: Optional[str] = None
    effect: Optional[str] = None
    subject: Optional[str] = None
    expiration_date: Optional[str] = None

    def __eq__(self, other: object) -> bool:
        """Check equality with another Rule instance.

        Args:
            other: Object to compare with

        Returns:
            True if both rules are equal, False otherwise
        """
        if self is other:
            return True
        if not isinstance(other, Rule):
            return False
        return (
            self.action == other.action
            and self.db_id == other.db_id
            and self.effect == other.effect
            and self.consent_uuid == other.consent_uuid
            and self.parents == other.parents
            and self.subject == other.subject
            and self.timestamp == other.timestamp
            and self.trigger == other.trigger
            and self.type == other.type
        )

    def __hash__(self) -> int:
        """Hash implementation for Rule.

        Returns:
            Hash value for the rule
        """
        return hash(
            (
                self.db_id,
                self.rule_uuid,
                self.consent_uuid,
                self.effect,
                self.subject,
                self.timestamp,
                self.type,
                self.trigger.url if self.trigger else None,
                self.action.url if self.action else None,
            )
        )

    def __str__(self) -> str:
        """String representation of the Rule.

        Returns:
            String showing subject, effect, trigger and action
        """
        trigger_url = self.trigger.url if self.trigger else "None"
        action_url = self.action.url if self.action else "None"
        return f"{self.subject} {self.effect} ---> {trigger_url}\t{action_url}"

    def to_dict(self) -> dict:
        """Convert Rule to dictionary for JSON serialization.

        Returns:
            Dictionary with all rule data
        """
        return {
            "db_id": self.db_id,
            "rule_uuid": self.rule_uuid,
            "consent_uuid": self.consent_uuid,
            "type": self.type,
            "effect": self.effect,
            "subject": self.subject,
            "timestamp": self.timestamp,
            "expirationDate": self.expiration_date,
            "trigger": self.trigger.to_dict() if self.trigger else None,
            "action": self.action.to_dict() if self.action else None,
            "parents": [p.to_dict() for p in self.parents] if self.parents else [],
        }
