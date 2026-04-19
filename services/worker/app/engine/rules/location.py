"""
Worker — Location Rule (Impossible Travel Detection)
Detects physically impossible travel between successive transactions.

Rule: Flag if user transacts from two distant cities in an impossibly short time.
"""

import logging
import time

from app.cache.user_state import UserStateCache
from app.engine.result import RuleResult
from app.engine.rules.base import BaseRule
from shared.events import TransactionEvent
from shared.geo_data import is_impossible_travel, haversine_distance, get_city_coordinates

logger = logging.getLogger(__name__)


class LocationRule(BaseRule):
    """Checks for physically impossible travel between transactions.

    Compares the current transaction's location with the user's
    last known location from Redis. Uses haversine distance
    and maximum travel speed to determine impossibility.
    """

    @property
    def name(self) -> str:
        return "location"

    async def evaluate(
        self,
        transaction: TransactionEvent,
        cache: UserStateCache,
    ) -> RuleResult:
        # Get user's last known location
        last_location = await cache.get_last_location(transaction.user_id)

        # If no previous location data, can't evaluate
        if last_location is None:
            return RuleResult(
                rule_name=self.name,
                violated=False,
                description="No previous location data for comparison",
                details={"current_location": transaction.location},
            )

        current_city = transaction.location
        previous_city = last_location["location"]

        # Same city — no travel needed
        if current_city.lower() == previous_city.lower():
            return RuleResult(
                rule_name=self.name,
                violated=False,
                description=f"Same location: {current_city}",
                details={
                    "current_location": current_city,
                    "previous_location": previous_city,
                },
            )

        # Calculate time difference
        current_time = time.time()
        previous_time = last_location.get("timestamp")
        if previous_time is None:
            return RuleResult(
                rule_name=self.name,
                violated=False,
                description="Missing timestamp for previous location",
            )

        time_diff = current_time - previous_time

        # Check if travel is impossible
        violated = is_impossible_travel(
            previous_city,
            current_city,
            time_diff,
            max_speed_kmh=900.0,  # Max commercial flight speed
        )

        # Calculate distance for details
        coords1 = get_city_coordinates(previous_city)
        coords2 = get_city_coordinates(current_city)
        distance = 0.0
        if coords1 and coords2:
            distance = haversine_distance(coords1[0], coords1[1], coords2[0], coords2[1])

        if violated:
            logger.warning(
                f"🌍 Location violation: user={transaction.user_external_id} | "
                f"{previous_city} → {current_city} in {time_diff:.0f}s "
                f"(distance: {distance:.0f}km)"
            )

        return RuleResult(
            rule_name=self.name,
            violated=violated,
            description=(
                f"Impossible travel: {previous_city} → {current_city} "
                f"({distance:.0f}km in {time_diff:.0f}s)"
                if violated
                else f"Travel OK: {previous_city} → {current_city}"
            ),
            details={
                "previous_location": previous_city,
                "current_location": current_city,
                "distance_km": round(distance, 2),
                "time_diff_seconds": round(time_diff, 2),
                "max_speed_kmh": 900.0,
            },
        )
