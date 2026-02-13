from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Email Deliverability Checker API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Database Settings
    DATABASE_URL: str
    
    # API Rate Limits (requests per month)
    FREE_TIER_LIMIT: int = 100
    BASIC_TIER_LIMIT: int = 5000
    PRO_TIER_LIMIT: int = 50000
    
    # RapidAPI Headers
    RAPIDAPI_PROXY_SECRET: str = ""
    RAPIDAPI_USER_HEADER: str = "X-RapidAPI-User"
    RAPIDAPI_SUBSCRIPTION_HEADER: str = "X-RapidAPI-Subscription"
    
    # SMTP Validation Settings
    SMTP_TIMEOUT: int = 10
    SMTP_CHECK_ENABLED: bool = True
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()
