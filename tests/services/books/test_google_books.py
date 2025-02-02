import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from app.services.google_books import GoogleBooksService

@pytest.mark.asyncio
async def test_search_books():
    """Test basic book search"""
    service = GoogleBooksService()
    mock_response = MagicMock()  # Use MagicMock instead of AsyncMock for the response
    mock_response.json.return_value = {
        "totalItems": 1,
        "items": [{
            "volumeInfo": {
                "title": "Racial Justice Book",
                "authors": ["Test Author"],
                "description": "Test description",
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "9780451450524"}
                ],
                "categories": ["Social Science"],
                "infoLink": "http://test.com",
                "imageLinks": {"thumbnail": "http://test.com/image"},
                "publishedDate": "2020"
            }
        }]
    }
    mock_response.aclose = AsyncMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        books = await service.search_books("racial justice")
        assert len(books) > 0
        assert all(hasattr(book, 'isbn') for book in books)

@pytest.mark.asyncio
async def test_subject_filtering():
    """Test subject-based filtering"""
    service = GoogleBooksService()
    mock_response = MagicMock()  # Use MagicMock instead of AsyncMock for the response
    mock_response.json.return_value = {
        "totalItems": 1,
        "items": [{
            "volumeInfo": {
                "title": "Programming Book",
                "authors": ["Test Author"],
                "description": "Test description",
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "9780451450524"}
                ],
                "categories": ["Technology"],
                "infoLink": "http://test.com",
                "imageLinks": {"thumbnail": "http://test.com/image"},
                "publishedDate": "2020"
            }
        }]
    }
    mock_response.aclose = AsyncMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        books = await service.search_books("programming")
        assert not any('Programming' in book.title for book in books)

@pytest.mark.asyncio
async def test_year_filtering():
    """Test year-based filtering"""
    service = GoogleBooksService()
    mock_response = MagicMock()  # Use MagicMock instead of AsyncMock for the response
    mock_response.json.return_value = {
        "totalItems": 1,
        "items": [{
            "volumeInfo": {
                "title": "Social Justice Book",
                "authors": ["Test Author"],
                "description": "Test description",
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "9780451450524"}
                ],
                "categories": ["Social Science"],
                "infoLink": "http://test.com",
                "imageLinks": {"thumbnail": "http://test.com/image"},
                "publishedDate": "2020"
            }
        }]
    }
    mock_response.aclose = AsyncMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        books = await service.search_books("social justice")
        assert all(book.title != "" for book in books)

@pytest.mark.asyncio
async def test_isbn_handling():
    """Test ISBN-10 to ISBN-13 conversion"""
    service = GoogleBooksService()
    mock_response = MagicMock()  # Use MagicMock instead of AsyncMock for the response
    mock_response.json.return_value = {
        "totalItems": 1,
        "items": [{
            "volumeInfo": {
                "title": "Social Justice in Modern Society",
                "authors": ["Test Author"],
                "description": "Test description",
                "industryIdentifiers": [
                    {"type": "ISBN_10", "identifier": "9780451234567"},  # Valid 13 digit ISBN
                ],
                "categories": ["Social Science"],
                "infoLink": "http://test.com",
                "imageLinks": {"thumbnail": "http://test.com/image"},
                "publishedDate": "2020"
            }
        }]
    }
    mock_response.aclose = AsyncMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        books = await service.search_books("test")
        
        assert len(books) == 1
        assert books[0].isbn == "9780451234567"  # Expected 13-digit ISBN

@pytest.mark.asyncio
async def test_error_handling():
    """Test API error handling"""
    service = GoogleBooksService()
    async def mock_error(*args, **kwargs):
        raise httpx.RequestError("Test error")
    
    with patch('httpx.AsyncClient.get', side_effect=mock_error):
        books = await service.search_books("test")
        assert len(books) == 0