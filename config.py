from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    environment: str = "development"

    secret_key: str = "change-me"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    access_token_expire_minutes: int = 60

    database_url: str = "sqlite:///./pocketsmart.db"

    max_upload_mb: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()