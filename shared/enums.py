"""
Shared enumerations for the Fraud Detection Platform.
"""

from enum import Enum


class TransactionStatus(str, Enum):
    """Status of a transaction after processing."""
    APPROVED = "approved"
    SUSPICIOUS = "suspicious"
    REJECTED = "rejected"


class RiskLevel(str, Enum):
    """Risk level assigned to users or transactions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuleType(str, Enum):
    """Types of anomaly detection rules."""
    VELOCITY = "velocity"
    AMOUNT = "amount"
    LOCATION = "location"


class AlertStatus(str, Enum):
    """Status of a fraud alert."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
