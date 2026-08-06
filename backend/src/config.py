from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str
    redis_url: str
    google_books_api_key: str
    comic_vine_api_key: str = ""
    internet_archive_base_url: str = "https://archive.org"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440   # 24 hours
    jwt_refresh_token_expire_days: int = 30

    # Admin
    admin_secret_key: str = ""  # empty = disabled; set in .env to enable superuser

    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
