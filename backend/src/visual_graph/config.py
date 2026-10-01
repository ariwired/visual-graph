from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "VisualGraph"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()