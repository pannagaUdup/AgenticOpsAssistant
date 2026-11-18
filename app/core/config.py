from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    account_service_base_url: str = "https://accounts.example.test"
    database_url: str
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-2.5-flash-lite"
    llm_provider: str = "fake"


@lru_cache
def get_settings() -> Settings:
    return Settings()
