from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Email Deliverability Checker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database (opcional por ahora - se usará en Fase 2)
    DATABASE_URL: Optional[str] = None
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    # Rate Limiting (for local use, RapidAPI handles this)
    RATE_LIMIT_FREE: int = 100  # per month
    RATE_LIMIT_BASIC: int = 5000
    RATE_LIMIT_PRO: int = 50000
    
    # SMTP Validation
    SMTP_TIMEOUT: int = 10
    SMTP_FROM_EMAIL: str = "verify@yourdomain.com"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # No validar si el .env no existe
        env_file_encoding = 'utf-8'
        extra = "ignore"


settings = Settings()
