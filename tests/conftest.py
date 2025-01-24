import asyncio
import pytest
from typing import AsyncGenerator
from datetime import datetime, date
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.core.config import Settings
from app.core.database import Base, get_db
from app.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/sjl_test_db"

# Create async engine for tests
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

# Create async session for tests
async_session_maker = sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Using pytest-asyncio's built-in event_loop fixture
# No need to define our own event_loop fixture

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency."""
    async with async_session_maker() as session:
        yield session

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
async def test_db_setup():
    """Set up test database."""
    async with engine_test.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS article_topics CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS book_topics"))
        await conn.execute(text("DROP TABLE IF EXISTS articles"))
        await conn.execute(text("DROP TABLE IF EXISTS books"))
        await conn.execute(text("DROP TABLE IF EXISTS topics"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session for a test."""
    # Create a new engine for test
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool
    )

    # Create the tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session for test
    test_async_session = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    session = test_async_session()
    try:
        yield session
    finally:
        await session.close()
        # Drop the tables
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()

@pytest.fixture
def sample_article_data():
    """Get sample article data."""
    return {
        "title": "Test Article",
        "content": "This is a test article content",
        "source": "Test Source",
        "url": "http://test.com/article",
        "featured": False,
        "date": date.today()  # Using date instead of datetime
    }

@pytest.fixture
def sample_book_data():
    """Get sample book data."""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "description": "This is a test book description",
        "url": "http://test.com/book",
        "cover_url": "http://test.com/cover",
        "isbn": "1234567890123"
    }

@pytest.fixture
def sample_topic_data():
    """Get sample topic data."""
    return {
        "name": "Test Topic",
        "description": "This is a test topic description"
    }

@pytest.fixture
async def test_article(db_session: AsyncSession, sample_article_data: dict):
    """Create a test article."""
    from app.models.article import Article
    article = Article(**sample_article_data)
    db_session.add(article)
    await db_session.flush()
    await db_session.refresh(article)
    return article

@pytest.fixture
async def test_book(db_session: AsyncSession, sample_book_data: dict):
    """Create a test book."""
    from app.models.book import Book
    book = Book(**sample_book_data)
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    return book

@pytest.fixture
async def test_topic(db_session: AsyncSession, sample_topic_data: dict):
    """Create a test topic."""
    from app.models.topic import Topic
    topic = Topic(**sample_topic_data)
    db_session.add(topic)
    await db_session.commit()
    await db_session.refresh(topic)
    return topic

@pytest.fixture
async def client():
    """Get test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sync_client():
    """Get synchronous test client."""
    return TestClient(app)
