import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Database Configuration
    POSTGRES_HOST: str = "prod-crm-psql-postgresql-ha.prod-crm-api.svc.cluster.local"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE: str = "quality_control"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "PGbackofficeDDDDakfj9123jdmkkkbAckBack"
    POSTGRES_SCHEMA: str = "call"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Logging Configuration
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # Ignore extra fields from .env (like VITE_* variables)
    )


@lru_cache()
def get_settings():
    return Settings()
