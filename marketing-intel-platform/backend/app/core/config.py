from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Marketing Intelligence Platform"
    env: str = "local"

    sqlite_path: str = "./data/mi.db"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    @property
    def sqlite_url(self) -> str:
        p = Path(self.sqlite_path)
        if not p.is_absolute():
            p = (Path(__file__).resolve().parents[3] / p).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite+pysqlite:///{p}"


settings = Settings()

