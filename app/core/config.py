from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import json

class Settings(BaseSettings):
    # API
    API_VERSION: str = "1.0.0"
    PROJECT_NAME: str = "Social Justice Library API"
    ENVIRONMENT: str = "development"

    # Database configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sjl_db"

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("postgresql://") or v.startswith("postgresql+asyncpg://"):
            return v
        raise ValueError("DATABASE_URL must start with postgresql:// or postgresql+asyncpg://")

    # External APIs
    AP_NEWS_API_KEY: str | None = None
    AP_NEWS_BASE_URL: str = "https://api.ap.org/v2"  
    GOOGLE_BOOKS_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] | List[str] = ["http://localhost:3000"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Log the configuration (but mask sensitive values)
safe_settings = settings.dict()
for key in ['AP_NEWS_API_KEY', 'GOOGLE_BOOKS_API_KEY', 'CLAUDE_API_KEY']:
    if safe_settings.get(key):
        safe_settings[key] = '***'
print(f"Initialized settings: {json.dumps(safe_settings, indent=2)}")