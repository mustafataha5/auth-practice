
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL
from pydantic import Field, SecretStr


# auth-practice/backend/app/core/config.py
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    APP_NAME: str = "Auth Practice API"
    DEBUG: bool = False

    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str

    DB_HOST: str = "localhost"
    DB_PORT: int = 5433
    REDIS_URL: str = "redis://localhost:6379/0"
    # Add these fields inside Settings; keep your existing fields.
    JWT_SECRET_KEY: SecretStr = Field(
        min_length=32,
    )

    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "auth-practice"
    JWT_AUDIENCE: str = "auth-practice-api"

    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 7
    
    CSRF_ALLOWED_ORIGINS: list[str] = [
    "http://localhost:4200",
    "http://localhost:8000",
]
    # In production, use DEBUG=False and HTTPS.

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.POSTGRES_DB,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
