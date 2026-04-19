"""
Shared constants for the Fraud Detection Platform.
Defines queue names, exchange names, and routing keys used across services.
"""

# ──────────────────────────────────────────
# RabbitMQ Exchange Names
# ──────────────────────────────────────────
EXCHANGE_TRANSACTIONS = "fdp.transactions"
EXCHANGE_ALERTS = "fdp.alerts"
EXCHANGE_DLX = "fdp.dlx"

# ──────────────────────────────────────────
# RabbitMQ Queue Names
# ──────────────────────────────────────────
QUEUE_TRANSACTION_PROCESS = "fdp.transaction.process"
QUEUE_FRAUD_ALERTS = "fdp.fraud.alerts"
QUEUE_DLQ_TRANSACTION = "fdp.dlq.transaction"

# ──────────────────────────────────────────
# Routing Keys
# ──────────────────────────────────────────
ROUTING_KEY_TRANSACTION_CREATED = "transaction.created"
ROUTING_KEY_DLQ_TRANSACTION = "dlq.transaction"

# ──────────────────────────────────────────
# Redis Key Prefixes
# ──────────────────────────────────────────
REDIS_PREFIX_USER_TRANSACTIONS = "user:{user_id}:transactions"
REDIS_PREFIX_USER_AVG_AMOUNT = "user:{user_id}:avg_amount"
REDIS_PREFIX_USER_TX_AMOUNTS = "user:{user_id}:tx_amounts"
REDIS_PREFIX_USER_LAST_LOCATION = "user:{user_id}:last_location"

# ──────────────────────────────────────────
# Anomaly Detection Defaults
# ──────────────────────────────────────────
DEFAULT_VELOCITY_WINDOW_SECONDS = 60
DEFAULT_VELOCITY_MAX_TRANSACTIONS = 5
DEFAULT_AMOUNT_MULTIPLIER = 3.0
DEFAULT_AMOUNT_WINDOW_HOURS = 24
DEFAULT_MIN_VIOLATIONS_FOR_FRAUD = 2
