"""
Worker — Velocity Rule
Detects when a user makes too many transactions in a short time window.

Rule: Flag if user has > 5 transactions in the last 60 seconds.
"""

import logging

from app.cache.user_state import UserStateCache
from app.config import settings
from app.engine.result import RuleResult
from app.engine.rules.base import BaseRule
from shared.events import TransactionEvent

logger = logging.getLogger(__name__)


class VelocityRule(BaseRule):
    """Checks if user is making transactions too rapidly.

    Looks at the Sorted Set in Redis to count recent transactions
    within a configurable time window.
    """

    @property
    def name(self) -> str:
        return "velocity"

    async def evaluate(
        self,
        transaction: TransactionEvent,
        cache: UserStateCache,
    ) -> RuleResult:
        window = settings.velocity_window_seconds
        max_transactions = settings.velocity_max_transactions

        # Count transactions in the time window
        count = await cache.get_recent_transaction_count(
            transaction.user_id, window
        )

        violated = count >= max_transactions

        if violated:
            logger.warning(
                f"⚡ Velocity violation: user={transaction.user_external_id} | "
                f"{count + 1} transactions in {window}s (max: {max_transactions})"
            )

        return RuleResult(
            rule_name=self.name,
            violated=violated,
            description=(
                f"User made {count + 1} transactions in {window}s "
                f"(threshold: {max_transactions})"
                if violated
                else f"Velocity OK: {count + 1}/{max_transactions} in {window}s"
            ),
            details={
                "transaction_count": count + 1,  # +1 for current
                "window_seconds": window,
                "threshold": max_transactions,
            },
        )
