"""Application configuration using Pydantic settings."""
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    ASYNC_DATABASE_URL: str = Field(..., description="Async PostgreSQL connection string (asyncpg)")

    # JWT Configuration
    JWT_ALGORITHM: str = Field(default="RS256", description="JWT signing algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Access token expiry")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry")
    PRIVATE_KEY_PATH: str = Field(default="keys/private_key.pem", description="Path to RSA private key")
    PUBLIC_KEY_PATH: str = Field(default="keys/public_key.pem", description="Path to RSA public key")

    # Email Configuration
    SMTP_HOST: str = Field(default="localhost", description="SMTP server host")
    SMTP_PORT: int = Field(default=1025, description="SMTP server port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    SMTP_FROM_EMAIL: str = Field(default="noreply@learnflow.local", description="From email address")
    SMTP_FROM_NAME: str = Field(default="LearnFlow", description="From name")

    # Frontend URL
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Frontend URL for email links")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_MAX_ATTEMPTS: int = Field(default=5, description="Max failed login attempts")
    RATE_LIMIT_LOCKOUT_MINUTES: int = Field(default=15, description="Lockout duration in minutes")

    # HaveIBeenPwned API
    HIBP_API_URL: str = Field(
        default="https://api.pwnedpasswords.com/range/",
        description="HaveIBeenPwned API URL"
    )

    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into list."""
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    def get_private_key(self) -> str:
        """Load RSA private key from file."""
        key_path = Path(self.PRIVATE_KEY_PATH)
        if not key_path.exists():
            raise FileNotFoundError(f"Private key not found at {key_path}")
        return key_path.read_text()

    def get_public_key(self) -> str:
        """Load RSA public key from file."""
        key_path = Path(self.PUBLIC_KEY_PATH)
        if not key_path.exists():
            raise FileNotFoundError(f"Public key not found at {key_path}")
        return key_path.read_text()


# Global settings instance
settings = Settings()
