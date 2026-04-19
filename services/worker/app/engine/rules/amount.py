"""
Worker — Amount Rule
Detects abnormally large transaction amounts compared to user's history.

Rule: Flag if amount > 3x the user's 24-hour average.
"""

import logging

from app.cache.user_state import UserStateCache
from app.config import settings
from app.engine.result import RuleResult
from app.engine.rules.base import BaseRule
from shared.events import TransactionEvent

logger = logging.getLogger(__name__)


class AmountRule(BaseRule):
    """Checks if transaction amount is abnormally high.

    Compares the current transaction amount against the user's
    rolling average from the Redis amount list.
    """

    @property
    def name(self) -> str:
        return "amount"

    async def evaluate(
        self,
        transaction: TransactionEvent,
        cache: UserStateCache,
    ) -> RuleResult:
        multiplier = settings.amount_multiplier

        # Get user's historical average
        avg_amount = await cache.get_average_amount(transaction.user_id)

        # If no history, can't evaluate — pass the rule
        if avg_amount is None or avg_amount == 0:
            return RuleResult(
                rule_name=self.name,
                violated=False,
                description="No transaction history for comparison",
                details={"average_amount": None, "current_amount": transaction.amount},
            )

        threshold = avg_amount * multiplier
        violated = transaction.amount > threshold

        if violated:
            logger.warning(
                f"💰 Amount violation: user={transaction.user_external_id} | "
                f"amount={transaction.amount} > {threshold:.2f} "
                f"(avg={avg_amount:.2f} × {multiplier})"
            )

        return RuleResult(
            rule_name=self.name,
            violated=violated,
            description=(
                f"Amount {transaction.amount} exceeds {multiplier}x average ({avg_amount:.2f})"
                if violated
                else f"Amount OK: {transaction.amount} <= {threshold:.2f}"
            ),
            details={
                "current_amount": transaction.amount,
                "average_amount": round(avg_amount, 2),
                "threshold": round(threshold, 2),
                "multiplier": multiplier,
            },
        )
