"""
API Gateway — Transaction ORM Model
"""

import uuid

from sqlalchemy import String, Numeric, Float, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Transaction(Base, UUIDMixin, TimestampMixin):
    """E-commerce transaction record."""

    __tablename__ = "transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3), default="TRY", server_default="TRY"
    )
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum("approved", "suspicious", "rejected", name="transaction_status"),
        default="approved",
        server_default="approved",
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSON, default=dict, server_default="{}"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    fraud_alert: Mapped["FraudAlert | None"] = relationship(
        "FraudAlert", back_populates="transaction", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount}, status={self.status})>"
        )
