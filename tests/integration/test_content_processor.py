import pytest
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from app.services.content_processor import ContentProcessor
from app.services.guardian_news import GuardianNewsService
from app.services.anthropic_service import AnthropicService, ArticleAnalysis, BookRelevance
from app.services.google_books import GoogleBooksService
from app.crud.article import article_crud
from app.crud.book import book_crud
from app.schemas.article import ArticleCreate
from app.schemas.book import BookCreate

@pytest.fixture
async def mock_services(test_session: AsyncSession):
    """Create processor with mocked services"""
    # Mock Guardian Service
    guardian = GuardianNewsService()
    guardian.get_recent_social_justice_articles = AsyncMock(return_value=(
        [ArticleCreate(
            title="Climate Justice Article",
            content="Test content about climate justice",
            source="The Guardian",
            url="http://test.com/climate-article",
            featured=False,
            date=datetime.now(UTC).date()
        )], 
        1
    ))
    
    # Mock Anthropic Service
    anthropic = AnthropicService()
    anthropic.analyze_article = AsyncMock(return_value=ArticleAnalysis(
        is_relevant=True,
        relevance_score=0.8,
        topics=["Climate Justice", "Environmental Rights"],
        keywords=["climate", "justice"],
        summary="Article about climate justice"
    ))
    anthropic.generate_book_keywords = AsyncMock(return_value=["climate justice"])
    anthropic.batch_analyze_book_relevance = AsyncMock(return_value=[
        (
            {
                "title": "Climate Justice Book",
                "author": "Test Author",
                "description": "Book about climate justice",
                "url": "http://test.com/book",
                "cover_url": "http://test.com/cover",
                "isbn": "9781234567890"
            },
            BookRelevance(relevance_score=0.9, explanation="Relevant book")
        )
    ])

    # Mock Books Service
    books = GoogleBooksService()
    books.search_books = AsyncMock(return_value=[
        BookCreate(
            title="Climate Justice Book",
            author="Test Author",
            description="Book about climate justice",
            url="http://test.com/book",
            cover_url="http://test.com/cover",
            isbn="9781234567890"
        )
    ])

    return ContentProcessor(
        db=test_session,
        guardian_service=guardian,
        anthropic_service=anthropic,
        books_service=books
    )

@pytest.mark.asyncio
async def test_full_content_flow(test_session: AsyncSession, mock_services):
    """Test the complete content processing flow"""
    # Process content
    await mock_services.process_new_content()
    
    # Check article was created
    article = await article_crud.get_by_url(test_session, url="http://test.com/climate-article")
    assert article is not None
    assert article.title == "Climate Justice Article"
    
    # Check topics were created and linked
    assert len(article.topics) == 2
    topic_names = [t.name for t in article.topics]
    assert "Climate Justice" in topic_names
    assert "Environmental Rights" in topic_names
    
    # Check book was created and linked
    book = await book_crud.get_by_isbn(test_session, isbn="9781234567890")
    assert book is not None
    assert book.title == "Climate Justice Book"
    assert len(article.books) > 0

@pytest.mark.asyncio
async def test_duplicate_article_handling(test_session: AsyncSession, mock_services):
    """Test handling of duplicate articles"""
    # Process content twice
    await mock_services.process_new_content()
    await mock_services.process_new_content()
    
    # Check only one article exists
    articles, total, _ = await article_crud.get_multi_paginated(test_session, skip=0, limit=10)
    assert total == 1  # Should not create duplicate articles