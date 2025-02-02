
import pytest
from datetime import datetime, date
from unittest.mock import Mock, AsyncMock

from app.services.content_processor import ContentProcessor
from app.services.guardian_news import GuardianNewsService
from app.services.anthropic_service import AnthropicService, ArticleAnalysis, BookRelevance
from app.services.google_books import GoogleBooksService
from app.schemas.article import ArticleCreate
from app.schemas.book import BookCreate

@pytest.fixture
def mock_guardian():
    mock = AsyncMock(spec=GuardianNewsService)
    
    # Mock article data
    article = ArticleCreate(
        title="Test Article",
        date=date.today(),
        content="Test content about social justice",
        source="The Guardian",
        url="https://test.com/article1",
        featured=False
    )
    
    mock.get_recent_social_justice_articles.return_value = ([article], 1)
    return mock

@pytest.fixture
def mock_anthropic():
    mock = AsyncMock(spec=AnthropicService)
    
    # Mock article analysis
    analysis = ArticleAnalysis(
        is_relevant=True,
        relevance_score=0.8,
        topics=["racial justice", "education"],
        keywords=["systemic racism", "education reform"],
        summary="Article about racial justice in education"
    )
    mock.analyze_article.return_value = analysis
    
    # Mock book keywords
    mock.generate_book_keywords.return_value = ["racial justice education"]
    
    # Mock book relevance
    book_relevance = BookRelevance(
        relevance_score=0.9,
        explanation="This book provides historical context"
    )
    mock.batch_analyze_book_relevance.return_value = [
        ({"title": "Test Book", "author": "Author", "description": "Description",
          "url": "https://test.com/book1", "cover_url": "https://test.com/cover1",
          "isbn": "1234567890"}, book_relevance)
    ]
    return mock

@pytest.fixture
def mock_books():
    mock = AsyncMock(spec=GoogleBooksService)
    
    # Mock book data
    book = BookCreate(
        title="Test Book",
        author="Author",
        description="Description",
        url="https://test.com/book1",
        cover_url="https://test.com/cover1",
        isbn="1234567890"
    )
    mock.search_books.return_value = [book]
    return mock

@pytest.fixture
async def processor(mock_guardian, mock_anthropic, mock_books, db):
    return ContentProcessor(
        db=db,
        guardian_service=mock_guardian,
        anthropic_service=mock_anthropic,
        books_service=mock_books
    )

@pytest.mark.asyncio
async def test_process_new_content_success(processor, db):
    """Test successful processing of new content"""
    await processor.process_new_content()
    
    # Verify article was fetched
    processor.guardian_service.get_recent_social_justice_articles.assert_called_once()
    
    # Verify article was analyzed
    processor.anthropic_service.analyze_article.assert_called_once()
    
    # Verify books were searched and analyzed
    processor.books_service.search_books.assert_called_once()
    processor.anthropic_service.batch_analyze_book_relevance.assert_called_once()

@pytest.mark.asyncio
async def test_skip_existing_article(processor, db, article_data):
    """Test that existing articles are skipped"""
    # Process same content twice
    await processor.process_new_content()
    await processor.process_new_content()
    
    # Verify article was only analyzed once
    assert processor.anthropic_service.analyze_article.call_count == 1

@pytest.mark.asyncio
async def test_skip_irrelevant_article(processor):
    """Test that irrelevant articles are skipped"""
    # Make the article irrelevant
    analysis = ArticleAnalysis(
        is_relevant=True,
        relevance_score=0.5,  # Below 0.7 threshold
        topics=[],
        keywords=[],
        summary=""
    )
    processor.anthropic_service.analyze_article.return_value = analysis
    
    await processor.process_new_content()
    
    # Verify no books were searched
    processor.books_service.search_books.assert_not_called()

@pytest.mark.asyncio
async def test_error_handling(processor):
    """Test that errors are handled gracefully"""
    # Make article analysis raise an error
    processor.anthropic_service.analyze_article.side_effect = Exception("API Error")
    
    # Should not raise error
    await processor.process_new_content()
    
    # Verify we tried to analyze
    processor.anthropic_service.analyze_article.assert_called_once()