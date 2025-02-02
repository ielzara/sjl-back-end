import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

async def test_get_books(client: TestClient, test_book):
    """Test getting all books"""
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert data["items"][0]["title"] == test_book.title

async def test_get_book_by_id(client: TestClient, test_book):
    """Test getting single book"""
    response = client.get(f"/api/v1/books/{test_book.id}")
    assert response.status_code == 200
    assert response.json()["title"] == test_book.title

async def test_get_book_by_isbn(client: TestClient, test_book):
    """Test getting book by ISBN"""
    response = client.get(f"/api/v1/books/isbn/{test_book.isbn}")
    assert response.status_code == 200
    assert response.json()["isbn"] == test_book.isbn

async def test_create_book(client: TestClient, book_data):
    """Test book creation"""
    response = client.post("/api/v1/books", json=book_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["isbn"] == book_data["isbn"]

async def test_update_book(client: TestClient, test_book):
    """Test book update"""
    update_data = {"title": "Updated Title"}
    response = client.put(f"/api/v1/books/{test_book.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]

async def test_delete_book(client: TestClient, test_book):
    """Test book deletion"""
    response = client.delete(f"/api/v1/books/{test_book.id}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/books/{test_book.id}").status_code == 404

@pytest.mark.asyncio
async def test_get_book_articles(client: TestClient, test_book, test_article, db: AsyncSession):
    """Test getting articles for a book"""
    from app.crud.article import article_crud
    
    # Create relationship
    await article_crud.add_book(db, test_article.id, test_book.id, "Test relevance")
    await db.commit()
    
    # Test the endpoint
    response = client.get(f"/api/v1/books/{test_book.id}/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == test_article.id

@pytest.mark.asyncio
async def test_get_book_topics(client: TestClient, test_book, test_topic, db: AsyncSession):
    """Test getting topics for a book"""
    from app.crud.book import book_crud
    
    # Create relationship
    await book_crud.add_topic(db, test_book.id, test_topic.id)
    await db.commit()
    
    # Test the endpoint
    response = client.get(f"/api/v1/books/{test_book.id}/topics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_topic.name

# Error cases
async def test_book_not_found(client: TestClient):
    response = client.get("/api/v1/books/99999")
    assert response.status_code == 404

async def test_invalid_book_data(client: TestClient):
    response = client.post("/api/v1/books", json={"title": ""})
    assert response.status_code == 422

async def test_search_and_filter(client: TestClient, test_book):
    """Test search and filter operations"""
    # Test search
    response = client.get(f"/api/v1/books?keyword={test_book.title}")
    assert response.status_code == 200
    assert response.json()["items"][0]["title"] == test_book.title
    
    # Test author filter
    response = client.get(f"/api/v1/books?author={test_book.author}")
    assert response.status_code == 200
    assert response.json()["items"][0]["author"] == test_book.author