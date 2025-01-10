from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

print(f"Connecting to database with URL: {settings.DATABASE_URL}")

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True  # Enable automatic reconnection
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()