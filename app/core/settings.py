import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_debug: bool = True

    # Railway provides DATABASE_URL automatically, fall back to individual vars
    database_url_raw: str = os.getenv("DATABASE_URL", "")
    
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = 5432
    postgres_db: str = "marlin"
    postgres_user: str = "marlin"
    postgres_password: str = "secret"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        # Use Railway's DATABASE_URL if available, otherwise construct from individual vars
        if self.database_url_raw:
            # Convert postgres:// to postgresql+asyncpg:// for SQLAlchemy async
            return self.database_url_raw.replace("postgres://", "postgresql+asyncpg://", 1)
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def debug(self) -> bool:
        return self.app_debug


@lru_cache
def get_settings() -> Settings:
    return Settings()
