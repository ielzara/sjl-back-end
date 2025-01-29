from typing import List
from dotenv import load_dotenv
import os

# Loading environment variables at the start
load_dotenv()

class Settings:
    """
    Application settings that loads and provides access to all environment variables.
    This class serves as a central configuration point for all external services
    and database connections in our application.
    """
    
    def __init__(self):
        # API Configuration
        self.API_VERSION = os.getenv("API_VERSION", "1.0.0")
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "Social Justice Library API")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # Database Configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        
        # CORS Configuration
        self.BACKEND_CORS_ORIGINS: List[str] = eval(os.getenv("BACKEND_CORS_ORIGINS", "[]"))
        
        # Guardian News API Configuration
        self.GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")
        self.GUARDIAN_BASE_URL = os.getenv("GUARDIAN_BASE_URL")
        
        # Google Books API Configuration
        self.GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
        self.GOOGLE_BOOKS_BASE_URL = os.getenv("GOOGLE_BOOKS_BASE_URL")
        
        # Anthropic API Configuration
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Creating a single instance of Settings to be used throughout the application
settings = Settings()