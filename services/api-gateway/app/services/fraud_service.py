"""
API Gateway — Fraud Service
Business logic for fraud alert querying and statistics.
"""

import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fraud_alert import FraudAlert
from app.models.transaction import Transaction
from app.models.user import User

logger = logging.getLogger(__name__)


class FraudService:
    """Handles fraud alert querying and statistics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_fraud_alerts(
        self,
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        risk_level: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        user_external_id: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        """Get paginated list of fraud alerts with filters."""
        query = select(FraudAlert, Transaction, User).join(
            Transaction, FraudAlert.transaction_id == Transaction.id
        ).join(
            User, FraudAlert.user_id == User.id
        )

        count_query = select(func.count(FraudAlert.id)).join(
            Transaction, FraudAlert.transaction_id == Transaction.id
        ).join(
            User, FraudAlert.user_id == User.id
        )

        # Apply filters
        filters = []
        if start_date:
            filters.append(FraudAlert.created_at >= start_date)
        if end_date:
            filters.append(FraudAlert.created_at <= end_date)
        if risk_level:
            filters.append(FraudAlert.risk_level == risk_level)
        if is_resolved is not None:
            filters.append(FraudAlert.is_resolved == is_resolved)
        if user_external_id:
            filters.append(User.external_id == user_external_id)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        total = await self.db.scalar(count_query) or 0

        offset = (page - 1) * page_size
        query = query.order_by(FraudAlert.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        rows = result.all()

        alerts = []
        for alert, transaction, user in rows:
            alerts.append({
                "id": str(alert.id),
                "transaction_id": str(alert.transaction_id),
                "user_id": str(alert.user_id),
                "user_external_id": user.external_id,
                "risk_level": alert.risk_level,
                "violated_rules": alert.violated_rules,
                "details": alert.details,
                "amount": float(transaction.amount),
                "location": transaction.location,
                "is_resolved": alert.is_resolved,
                "resolved_at": alert.resolved_at,
                "created_at": alert.created_at,
            })

        return alerts, total

    async def get_fraud_stats(self) -> dict:
        """Get overall fraud statistics."""
        # Total alerts
        total_alerts = await self.db.scalar(
            select(func.count(FraudAlert.id))
        ) or 0

        # Active vs resolved
        active_alerts = await self.db.scalar(
            select(func.count(FraudAlert.id)).where(FraudAlert.is_resolved == False)
        ) or 0

        resolved_alerts = total_alerts - active_alerts

        # Total transactions for fraud rate
        total_transactions = await self.db.scalar(
            select(func.count(Transaction.id))
        ) or 0

        fraud_rate = 0.0
        if total_transactions > 0:
            fraud_rate = (total_alerts / total_transactions) * 100

        # Alerts by risk level
        risk_query = select(
            FraudAlert.risk_level,
            func.count(FraudAlert.id),
        ).group_by(FraudAlert.risk_level)
        risk_result = await self.db.execute(risk_query)
        alerts_by_risk = {row[0]: row[1] for row in risk_result.all()}

        # Top flagged users
        top_users_query = (
            select(User.external_id, User.total_fraud_flags, User.risk_level)
            .where(User.total_fraud_flags > 0)
            .order_by(User.total_fraud_flags.desc())
            .limit(10)
        )
        top_users_result = await self.db.execute(top_users_query)
        top_flagged_users = [
            {
                "external_id": row[0],
                "fraud_flags": row[1],
                "risk_level": row[2],
            }
            for row in top_users_result.all()
        ]

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "fraud_rate": round(fraud_rate, 2),
            "alerts_by_risk": alerts_by_risk,
            "alerts_by_rule": {},  # Will be populated with UNNEST query if needed
            "top_flagged_users": top_flagged_users,
        }

    async def get_fraud_trend(self, days: int = 7) -> list[dict]:
        """Get daily fraud alert counts and rates for the specified period.

        Returns a list of daily data points with:
        - date: The day (YYYY-MM-DD)
        - fraud_count: Number of fraud alerts that day
        - transaction_count: Total transactions that day
        - fraud_rate: Percentage of fraudulent transactions
        """
        from sqlalchemy import text

        query = text("""
            WITH date_series AS (
                SELECT generate_series(
                    (CURRENT_DATE - :days * INTERVAL '1 day')::date,
                    CURRENT_DATE::date,
                    '1 day'::interval
                )::date AS day
            ),
            daily_frauds AS (
                SELECT
                    DATE(created_at AT TIME ZONE 'UTC') AS day,
                    COUNT(*) AS fraud_count
                FROM fraud_alerts
                WHERE created_at >= CURRENT_DATE - :days * INTERVAL '1 day'
                GROUP BY DATE(created_at AT TIME ZONE 'UTC')
            ),
            daily_transactions AS (
                SELECT
                    DATE(created_at AT TIME ZONE 'UTC') AS day,
                    COUNT(*) AS tx_count
                FROM transactions
                WHERE created_at >= CURRENT_DATE - :days * INTERVAL '1 day'
                GROUP BY DATE(created_at AT TIME ZONE 'UTC')
            )
            SELECT
                ds.day,
                COALESCE(df.fraud_count, 0) AS fraud_count,
                COALESCE(dt.tx_count, 0) AS transaction_count,
                CASE
                    WHEN COALESCE(dt.tx_count, 0) > 0
                    THEN ROUND((COALESCE(df.fraud_count, 0)::numeric / dt.tx_count) * 100, 2)
                    ELSE 0
                END AS fraud_rate
            FROM date_series ds
            LEFT JOIN daily_frauds df ON ds.day = df.day
            LEFT JOIN daily_transactions dt ON ds.day = dt.day
            ORDER BY ds.day ASC
        """)

        result = await self.db.execute(query, {"days": days})
        rows = result.all()

        return [
            {
                "date": row[0].isoformat(),
                "fraud_count": row[1],
                "transaction_count": row[2],
                "fraud_rate": float(row[3]),
            }
            for row in rows
        ]
