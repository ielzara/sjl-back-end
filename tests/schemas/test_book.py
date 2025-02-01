import pytest
from pydantic import ValidationError
from app.schemas.book import BookCreate, BookUpdate, BookDB

def test_book_create_valid():
    """Test creating a book with valid data"""
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test book description",
        "url": "https://example.com/book",
        "cover_url": "https://example.com/cover.jpg",
        "isbn": "9780123456789"
    }
    book = BookCreate(**book_data)
    assert book.title == book_data["title"]
    assert book.author == book_data["author"]
    assert book.description == book_data["description"]
    assert str(book.url) == book_data["url"]
    assert str(book.cover_url) == book_data["cover_url"]
    assert book.isbn == book_data["isbn"]

def test_book_create_invalid_urls():
    """Test book creation fails with invalid URLs"""
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test book description",
        "url": "not-a-url",  # Invalid URL
        "cover_url": "also-not-a-url",  # Invalid URL
        "isbn": "9780123456789"
    }
    with pytest.raises(ValidationError) as exc_info:
        BookCreate(**book_data)
    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert error_fields.intersection({"url", "cover_url"})

def test_book_create_missing_required():
    """Test book creation fails when required fields are missing"""
    book_data = {
        "title": "Test Book",
        # Missing required fields
    }
    with pytest.raises(ValidationError) as exc_info:
        BookCreate(**book_data)
    errors = exc_info.value.errors()
    required_fields = {"author", "description", "url", "cover_url", "isbn"}
    error_fields = {error["loc"][0] for error in errors}
    assert error_fields.intersection(required_fields)

def test_book_update_optional_fields():
    """Test book update with optional fields"""
    # Test with only some fields
    update_data = {
        "title": "Updated Title",
        "author": "Updated Author"
    }
    book_update = BookUpdate(**update_data)
    assert book_update.title == update_data["title"]
    assert book_update.author == update_data["author"]
    assert book_update.description is None
    assert book_update.url is None
    assert book_update.cover_url is None
    assert book_update.isbn is None

def test_book_db_schema():
    """Test book DB schema includes ID"""
    book_data = {
        "id": 1,
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test book description",
        "url": "https://example.com/book",
        "cover_url": "https://example.com/cover.jpg",
        "isbn": "9780123456789"
    }
    book = BookDB(**book_data)
    assert book.id == book_data["id"]
    assert book.title == book_data["title"]
    assert book.author == book_data["author"]

def test_book_create_whitespace_validation():
    """Test book creation with whitespace-only strings"""
    book_data = {
        "title": "   ",  # Whitespace-only title
        "author": "\n\t",  # Whitespace-only author
        "description": " ",  # Whitespace-only description
        "url": "https://example.com/book",
        "cover_url": "https://example.com/cover.jpg",
        "isbn": "9780123456789"
    }
    with pytest.raises(ValidationError) as exc_info:
        BookCreate(**book_data)
    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert error_fields.intersection({"title", "author", "description"})

def test_book_create_isbn_validation():
    """Test book creation with invalid ISBN"""
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test book description",
        "url": "https://example.com/book",
        "cover_url": "https://example.com/cover.jpg",
        "isbn": "123"  # Invalid ISBN (too short)
    }
    with pytest.raises(ValidationError) as exc_info:
        BookCreate(**book_data)
    assert "isbn" in str(exc_info.value)

def test_book_update_invalid_url():
    """Test book update with invalid URL"""
    update_data = {
        "url": "not-a-url"
    }
    with pytest.raises(ValidationError):
        BookUpdate(**update_data)