from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
import json

class Settings(BaseSettings):
    # API
    API_VERSION: str = "1.0.0"
    PROJECT_NAME: str = "Social Justice Library API"
    ENVIRONMENT: str = "development"

    # Database configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sjl_db"

    # External APIs
    AP_NEWS_API_KEY: str | None = None
    AP_NEWS_BASE_URL: str = "https://api.ap.org/v2"  
    GOOGLE_BOOKS_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

settings = Settings()
print(f"Initialized settings with DATABASE_URL: {settings.DATABASE_URL}")