"""
API Gateway — Application Configuration
Loads settings from environment variables using Pydantic Settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──
    app_name: str = "Fraud Detection Platform — API Gateway"
    api_debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ── PostgreSQL ──
    postgres_user: str = "fraud_user"
    postgres_password: str = "fraud_pass_2024"
    postgres_db: str = "fraud_detection"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # ── Redis ──
    redis_host: str = "localhost"
    redis_port: int = 6379

    # ── RabbitMQ ──
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672

    # ── Anomaly Detection ──
    velocity_window_seconds: int = 60
    velocity_max_transactions: int = 5
    amount_multiplier: float = 3.0
    amount_window_hours: int = 24

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
