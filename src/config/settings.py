"""
Application settings using pydantic-settings.

Loads configuration from environment variables and .env file.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    env: Literal["development", "staging", "production"] = "development"

    # Application
    app_name: str = "hr-policy-advisor"
    app_version: str = "0.1.0"
    debug: bool = False

    # API Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Gemini API
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-2.0-flash", description="Gemini model name")

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hr_policy"

    # HashiCorp Vault
    vault_addr: str = "http://localhost:8200"
    vault_token: str = "dev-token"

    # HITL Settings
    hitl_default_timeout_hours: int = 72
    hitl_critical_timeout_hours: int = 48

    # Agent Settings
    agent_heartbeat_interval_seconds: int = 30
    agent_max_retry_count: int = 3

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Directories
    @property
    def base_dir(self) -> Path:
        """Get the base directory of the project."""
        return Path(__file__).parent.parent.parent

    @property
    def memory_dir(self) -> Path:
        """Get the memory directory for agent logs."""
        path = self.base_dir / "memory"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
