"""
MCP Server — Configuration
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8001

    # ── PostgreSQL ──
    postgres_user: str = "fraud_user"
    postgres_password: str = "fraud_pass_2024"
    postgres_db: str = "fraud_detection"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # ── Redis ──
    redis_host: str = "localhost"
    redis_port: int = 6379

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
