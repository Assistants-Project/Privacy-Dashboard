from typing import List, Set, Optional
from dataclasses import dataclass, field

from .rule import Rule
from .trigger import Trigger


@dataclass
class RuleProblems:
    """Container for rule validation problems and execution results."""

    rule: Optional[Rule] = None
    loops: Set[tuple] = field(default_factory=set)
    redundant_rules: Set[tuple] = field(default_factory=set)
    inconsistent_rules: Set[tuple] = field(default_factory=set)
    executed_rules: List[Rule] = field(default_factory=list)
    start_trigger: Optional[Trigger] = None

    def add_loop(self, rules: List[Rule]) -> None:
        """Add a loop to the problems set.

        Args:
            rules: List of rules forming a loop
        """
        # Convert list to tuple for set storage (lists aren't hashable)
        self.loops.add(tuple(rules))

    def add_redundant_rules(self, rules: List[Rule]) -> None:
        """Add redundant rules to the problems set.

        Args:
            rules: List of redundant rules
        """
        self.redundant_rules.add(tuple(rules))

    def add_inconsistent_rules(self, rules: List[Rule]) -> None:
        """Add inconsistent rules to the problems set.

        Args:
            rules: List of inconsistent rules
        """
        self.inconsistent_rules.add(tuple(rules))

    def contains_inconsistency(self, inconsistent: List[Rule]) -> bool:
        """Check if an inconsistency already exists in the problems.

        Args:
            inconsistent: List of rules to check

        Returns:
            True if the inconsistency is already tracked, False otherwise
        """
        if not self.inconsistent_rules:
            return False

        for inconsistency in self.inconsistent_rules:
            inconsistency_list = list(inconsistency)
            if all(rule in inconsistency_list for rule in inconsistent):
                return True

        return False

    def contains_redundancy(self, redundant: List[Rule]) -> bool:
        """Check if a redundancy already exists in the problems.

        Args:
            redundant: List of rules to check

        Returns:
            True if the redundancy is already tracked, False otherwise
        """
        if not self.redundant_rules:
            return False

        for redundancy in self.redundant_rules:
            redundancy_list = list(redundancy)
            if all(rule in redundancy_list for rule in redundant):
                return True

        return False

    def add_executed_rule(self, rule: Rule) -> None:
        """Add a rule to the executed rules list.

        Args:
            rule: Rule that was executed
        """
        self.executed_rules.append(rule)

    def to_dict(self) -> dict:
        """Convert RuleProblems to dictionary for JSON serialization.

        Returns:
            Dictionary with all problem data
        """
        return {
            "rule": self.rule.to_dict() if self.rule else None,
            "loops": (
                [[r.to_dict() for r in loop] for loop in self.loops]
                if self.loops
                else None
            ),
            "redundantRules": (
                [[r.to_dict() for r in rules] for rules in self.redundant_rules]
                if self.redundant_rules
                else None
            ),
            "inconsistentRules": (
                [[r.to_dict() for r in rules] for rules in self.inconsistent_rules]
                if self.inconsistent_rules
                else None
            ),
            "executedRules": (
                [r.to_dict() for r in self.executed_rules]
                if self.executed_rules
                else None
            ),
            "startTrigger": (
                self.start_trigger.to_dict() if self.start_trigger else None
            ),
        }
