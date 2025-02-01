import pytest
from datetime import date
from pydantic import ValidationError
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleDB

def test_article_create_valid():
    """Test creating an article with valid data"""
    article_data = {
        "title": "Test Article",
        "content": "This is a test article content",
        "source": "Test Source",
        "url": "https://example.com/article",
        "featured": True,
        "date": date(2024, 1, 1)
    }
    article = ArticleCreate(**article_data)
    assert article.title == article_data["title"]
    assert article.content == article_data["content"]
    assert article.source == article_data["source"]
    assert str(article.url) == article_data["url"]
    assert article.featured == article_data["featured"]
    assert article.date == article_data["date"]

def test_article_create_invalid_url():
    """Test article creation fails with invalid URL"""
    article_data = {
        "title": "Test Article",
        "content": "Content",
        "source": "Test Source",
        "url": "not-a-url",  # Invalid URL
        "featured": True,
        "date": date(2024, 1, 1)
    }
    with pytest.raises(ValidationError) as exc_info:
        ArticleCreate(**article_data)
    assert "url" in str(exc_info.value)

def test_article_create_missing_required():
    """Test article creation fails when required fields are missing"""
    article_data = {
        "title": "Test Article",
        # Missing required fields
    }
    with pytest.raises(ValidationError) as exc_info:
        ArticleCreate(**article_data)
    errors = exc_info.value.errors()
    required_fields = {"content", "source", "url", "date"}
    error_fields = {error["loc"][0] for error in errors}
    assert error_fields.intersection(required_fields)

def test_article_update_optional_fields():
    """Test article update with optional fields"""
    # Test with only some fields
    update_data = {
        "title": "Updated Title"
    }
    article_update = ArticleUpdate(**update_data)
    assert article_update.title == update_data["title"]
    assert article_update.content is None
    assert article_update.source is None
    assert article_update.url is None
    assert article_update.featured is None
    assert article_update.date is None

def test_article_db_schema():
    """Test article DB schema includes ID"""
    article_data = {
        "id": 1,
        "title": "Test Article",
        "content": "This is a test article content",
        "source": "Test Source",
        "url": "https://example.com/article",
        "featured": True,
        "date": date(2024, 1, 1)
    }
    article = ArticleDB(**article_data)
    assert article.id == article_data["id"]
    assert article.title == article_data["title"]

def test_article_create_whitespace_validation():
    """Test article creation with whitespace-only strings"""
    article_data = {
        "title": "   ",  # Whitespace-only title
        "content": "\n\t",  # Whitespace-only content
        "source": " ",  # Whitespace-only source
        "url": "https://example.com/article",
        "featured": True,
        "date": date(2024, 1, 1)
    }
    with pytest.raises(ValidationError) as exc_info:
        ArticleCreate(**article_data)
    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert error_fields.intersection({"title", "content", "source"})

def test_article_update_invalid_date():
    """Test article update with invalid date"""
    update_data = {
        "date": "not-a-date"  # Invalid date format
    }
    with pytest.raises(ValidationError):
        ArticleUpdate(**update_data)