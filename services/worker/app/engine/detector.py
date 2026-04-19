"""
Worker — Fraud Detector (Orchestrator)
Orchestrates all anomaly detection rules and produces a final verdict.
"""

import logging

from app.cache.user_state import UserStateCache
from app.engine.result import DetectionResult, RuleResult
from app.engine.rules.base import BaseRule
from app.engine.rules.velocity import VelocityRule
from app.engine.rules.amount import AmountRule
from app.engine.rules.location import LocationRule
from shared.constants import DEFAULT_MIN_VIOLATIONS_FOR_FRAUD
from shared.events import TransactionEvent

logger = logging.getLogger(__name__)


class FraudDetector:
    """Orchestrates anomaly detection rules and determines fraud status.

    Uses the Strategy Pattern: each rule is independent and pluggable.
    A transaction is flagged as fraud when 2 or more rules are violated.
    """

    def __init__(
        self,
        cache: UserStateCache,
        rules: list[BaseRule] | None = None,
        min_violations: int = DEFAULT_MIN_VIOLATIONS_FOR_FRAUD,
    ):
        self.cache = cache
        self.min_violations = min_violations
        self.rules = rules or [
            VelocityRule(),
            AmountRule(),
            LocationRule(),
        ]

    async def analyze(self, transaction: TransactionEvent) -> DetectionResult:
        """Run all rules against a transaction and produce a verdict.

        Args:
            transaction: The transaction event to analyze

        Returns:
            DetectionResult with fraud determination and rule details
        """
        results: list[RuleResult] = []

        for rule in self.rules:
            try:
                result = await rule.evaluate(transaction, self.cache)
                results.append(result)
            except Exception as e:
                logger.error(
                    f"❌ Rule {rule.name} failed for transaction "
                    f"{transaction.transaction_id}: {e}"
                )
                # Don't let a single rule failure break the pipeline
                results.append(
                    RuleResult(
                        rule_name=rule.name,
                        violated=False,
                        description=f"Rule evaluation error: {str(e)}",
                    )
                )

        # Count violations
        violations = [r for r in results if r.violated]
        violation_count = len(violations)
        is_fraud = violation_count >= self.min_violations

        # Determine risk level
        risk_level = self._calculate_risk_level(violation_count)

        if is_fraud:
            violated_names = [v.rule_name for v in violations]
            logger.warning(
                f"🚨 FRAUD DETECTED: transaction={transaction.transaction_id} | "
                f"user={transaction.user_external_id} | "
                f"violations={violated_names} | risk={risk_level}"
            )

        return DetectionResult(
            is_fraud=is_fraud,
            risk_level=risk_level,
            violations=results,
            total_rules_checked=len(results),
        )

    @staticmethod
    def _calculate_risk_level(violation_count: int) -> str:
        """Determine risk level based on number of violated rules."""
        if violation_count >= 3:
            return "critical"
        elif violation_count == 2:
            return "high"
        elif violation_count == 1:
            return "medium"
        return "low"
