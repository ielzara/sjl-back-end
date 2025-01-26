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
        # Database connection settings
        # This URL will be used by SQLAlchemy to establish database connections
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Guardian News API settings
        # These will be used to make requests to The Guardian's content API
        self.GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")
        self.GUARDIAN_BASE_URL = os.getenv("GUARDIAN_BASE_URL")
        
        # Google Books API settings
        # These will be used to search for and retrieve book information
        self.GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
        self.GOOGLE_BOOKS_BASE_URL = os.getenv("GOOGLE_BOOKS_BASE_URL")
        
        # Claude AI API settings
        # These will be used for content analysis and book recommendations
        self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
        self.CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL")

# Creating a single instance of Settings to be used throughout the application
settings = Settings()