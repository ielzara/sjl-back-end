import pytest
from datetime import datetime, UTC
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from app.core.database import Base, get_db
from app.main import app

# Test database setup
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/sjl_test_db"
engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
async_session = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with async_session() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def app():
    from app.main import app
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Async client fixture"""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        backend="asyncio"
    ) as ac:
        yield ac

@pytest.fixture
async def db():
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def article_data():
    return {
        "title": "Test Article",
        "content": "Test content",
        "source": "Test Source",
        "url": "http://test.com/article",
        "featured": False,
        "date": datetime.now(UTC).date().isoformat()
    }

@pytest.fixture
def book_data():
    return {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test description",
        "url": "http://test.com/book",
        "cover_url": "http://test.com/cover",
        "isbn": "9781234567890"
    }

@pytest.fixture
def topic_data():
    return {
        "name": "Test Topic",
        "description": "Test description"
    }

@pytest.fixture
async def test_article(db, article_data):
    from app.models.article import Article
    article_dict = article_data.copy()
    article_dict["date"] = datetime.fromisoformat(article_dict["date"])
    article = Article(**article_dict)
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article

@pytest.fixture
async def test_book(db, book_data):
    from app.models.book import Book
    book = Book(**book_data)
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book

@pytest.fixture
async def test_topic(db, topic_data):
    from app.models.topic import Topic
    topic = Topic(**topic_data)
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic