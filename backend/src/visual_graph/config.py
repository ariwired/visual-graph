from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    app_name: str = "VisualGraph"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = False

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
