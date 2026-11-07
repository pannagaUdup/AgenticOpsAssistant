from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    account_service_base_url: str = "https://accounts.example.test"


@lru_cache
def get_settings() -> Settings:
    return Settings()