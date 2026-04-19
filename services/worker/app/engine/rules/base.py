"""
Worker — Base Rule (Strategy Pattern)
All anomaly detection rules must implement this interface.
"""

from abc import ABC, abstractmethod

from app.cache.user_state import UserStateCache
from app.engine.result import RuleResult
from shared.events import TransactionEvent


class BaseRule(ABC):
    """Abstract base class for anomaly detection rules.

    Each rule evaluates a single aspect of a transaction
    and returns a RuleResult indicating whether the rule was violated.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this rule."""
        ...

    @abstractmethod
    async def evaluate(
        self,
        transaction: TransactionEvent,
        cache: UserStateCache,
    ) -> RuleResult:
        """Evaluate the rule against a transaction.

        Args:
            transaction: The incoming transaction event
            cache: User state cache for historical data lookups

        Returns:
            RuleResult indicating whether the rule was violated
        """
        ...
