from __future__ import annotations

import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str
    mistral_api_key: str
    minimax_model: str = "mistral-small-latest"

    app_env: str = "dev"
    enable_test_unlock: bool = True
    full_plan_price_rub: int = 299
    database_path: str = "./data/bot.db"
    admin_user_id: int | None = None

    @field_validator("database_path", mode="before")
    @classmethod
    def ensure_db_dir(cls, v: str) -> str:
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"

    @property
    def test_unlock_enabled(self) -> bool:
        return self.enable_test_unlock or self.is_dev


def load_config() -> Config:
    return Config()  # type: ignore[call-arg]
