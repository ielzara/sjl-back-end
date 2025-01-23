from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column, Mapped
from sqlalchemy import DateTime
from .config import settings

print(f"Connecting to database with URL: {settings.DATABASE_URL}")

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass
# Create database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True  # Enable automatic reconnection
)

# Create AsyncSessionLocal class
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()