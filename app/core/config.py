from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Email Deliverability Checker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: Optional[str] = None
    API_V1_PREFIX: str = "/api/v1"

    ALLOWED_ORIGINS: str = "*"

    RATE_LIMIT_FREE: int = 100
    RATE_LIMIT_BASIC: int = 5000
    RATE_LIMIT_PRO: int = 50000

    SMTP_TIMEOUT: int = 10
    SMTP_FROM_EMAIL: str = "verify@yourdomain.com"

    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()