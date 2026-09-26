from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ITоднушка Monitor"
    app_env: str = "development"
    debug: bool = True

    database_url: str
    redis_url: str

    check_interval_seconds: int = 60
    request_timeout_seconds: int = 10
    check_result_retention_days: int = 30
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()