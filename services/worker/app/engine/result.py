"""
Worker — Detection Result Model
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RuleResult:
    """Result of a single rule evaluation."""
    rule_name: str
    violated: bool
    description: str = ""
    details: dict = field(default_factory=dict)


@dataclass
class DetectionResult:
    """Aggregated result of all rule evaluations."""
    is_fraud: bool
    risk_level: str  # low, medium, high, critical
    violations: list[RuleResult] = field(default_factory=list)
    total_rules_checked: int = 0

    @property
    def violated_rule_names(self) -> list[str]:
        return [v.rule_name for v in self.violations if v.violated]

    @property
    def details(self) -> dict:
        return {
            "is_fraud": self.is_fraud,
            "risk_level": self.risk_level,
            "total_rules_checked": self.total_rules_checked,
            "violations_count": len(self.violated_rule_names),
            "violations": [
                {
                    "rule": v.rule_name,
                    "violated": v.violated,
                    "description": v.description,
                    "details": v.details,
                }
                for v in self.violations
            ],
        }
