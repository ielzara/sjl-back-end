import pytest
from pydantic import ValidationError
from app.schemas.book import BookCreate, BookUpdate, BookDB

def test_book_create_valid():
    """Test creating a book with valid data"""
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test description",
        "url": "https://example.com/book",
        "cover_url": "https://example.com/cover.jpg",
        "isbn": "9780451450524"
    }
    book = BookCreate(**book_data)
    assert book.title == book_data["title"]
    assert book.isbn == book_data["isbn"]

def test_book_isbn_validation():
    """Test ISBN validation"""
    # Test ISBN-10 conversion
    book = BookCreate(
        title="Test",
        author="Author",
        description="Description",
        url="https://example.com",
        cover_url="https://example.com/cover.jpg",
        isbn="0451450523"
    )
    assert len(book.isbn) == 10

    # Invalid ISBN
    with pytest.raises(ValidationError):
        BookCreate(
            title="Test",
            author="Author",
            description="Description",
            url="https://example.com",
            cover_url="https://example.com/cover.jpg",
            isbn="123"  # Invalid ISBN
        )
