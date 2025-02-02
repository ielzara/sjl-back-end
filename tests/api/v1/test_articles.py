import pytest
from fastapi.testclient import TestClient

async def test_get_articles(client: TestClient, test_article):
    """Test getting all articles"""
    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert data["items"][0]["title"] == test_article.title

async def test_get_article_by_id(client: TestClient, test_article):
    """Test getting single article"""
    response = client.get(f"/api/v1/articles/{test_article.id}")
    assert response.status_code == 200
    assert response.json()["title"] == test_article.title

async def test_create_article(client: TestClient, article_data):
    """Test article creation"""
    response = client.post("/api/v1/articles", json=article_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == article_data["title"]

async def test_get_article_topics(client: TestClient, test_article, test_topic, db):
    """Test getting article topics"""
    from app.crud.article import article_crud
    await article_crud.add_topic(db, test_article.id, test_topic.id)
    
    response = client.get(f"/api/v1/articles/{test_article.id}/topics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_topic.name

async def test_get_article_books(client: TestClient, test_article, test_book, db):
    """Test getting article books"""
    from app.crud.article import article_crud
    await article_crud.add_book(db, test_article.id, test_book.id, "Test relevance")
    
    response = client.get(f"/api/v1/articles/{test_article.id}/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == test_book.title

async def test_article_not_found(client: TestClient):
    """Test 404 error for non-existent article"""
    response = client.get("/api/v1/articles/99999")
    assert response.status_code == 404

async def test_invalid_article_data(client: TestClient):
    """Test validation error for invalid article data"""
    response = client.post("/api/v1/articles", json={"title": ""})
    assert response.status_code == 422