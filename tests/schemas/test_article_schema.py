import pytest
from datetime import date
from pydantic import ValidationError
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleDB

def test_article_create_valid():
    """Test creating an article with valid data"""
    article_data = {
        "title": "Test Article",
        "content": "Test content",
        "source": "Test Source",
        "url": "https://example.com/article",
        "featured": True,
        "date": date(2024, 1, 1)
    }
    article = ArticleCreate(**article_data)
    assert article.title == article_data["title"]
    assert article.featured == article_data["featured"]

def test_article_create_invalid():
    """Test article creation with invalid data"""
    # Empty title
    with pytest.raises(ValidationError):
        ArticleCreate(
            title="",
            content="Test",
            source="Test",
            url="https://example.com",
            date=date(2024, 1, 1)
        )
    
    # Invalid URL
    with pytest.raises(ValidationError):
        ArticleCreate(
            title="Test",
            content="Test",
            source="Test",
            url="not-a-url",
            date=date(2024, 1, 1)
        )

def test_article_update():
    """Test article update schema"""
    update = ArticleUpdate(title="New Title")
    assert update.title == "New Title"
    assert update.content is None
