"""Application configuration settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Service Catalogue API"
    environment: Literal["dev", "test", "prod"] = "dev"
    database_url: str = "sqlite+pysqlite:///./svc_catalogue.db"
    auth_token: str = "change-me"
    log_level: str = "INFO"
    csv_max_rows: int = 10_000

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
