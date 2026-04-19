"""
API Gateway — User ORM Model
"""

import uuid
from typing import List

from sqlalchemy import String, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User profile with risk tracking."""

    __tablename__ = "users"

    external_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    risk_level: Mapped[str] = mapped_column(
        SAEnum("low", "medium", "high", "critical", name="risk_level"),
        default="low",
        server_default="low",
    )
    total_transactions: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    total_fraud_flags: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="user", lazy="selectin"
    )
    fraud_alerts: Mapped[List["FraudAlert"]] = relationship(
        "FraudAlert", back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, external_id={self.external_id}, risk={self.risk_level})>"
