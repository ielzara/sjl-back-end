import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/sjl_test_db"

@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        isolation_level="SERIALIZABLE"
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield engine
    finally:
        await engine.dispose()

@pytest.fixture
async def test_session(test_engine) -> AsyncSession:
    """Create test database session."""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True
    )

    async with async_session() as session:
        await session.begin()  # Start transaction
        try:
            yield session
            await session.commit()  # Commit if no errors
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()