import pytest
from fastapi.testclient import TestClient

async def test_get_topics(client: TestClient, test_topic):
    """Test getting all topics"""
    response = client.get("/api/v1/topics")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert data["items"][0]["name"] == test_topic.name

async def test_get_topic_by_id(client: TestClient, test_topic):
    """Test getting single topic"""
    response = client.get(f"/api/v1/topics/{test_topic.id}")
    assert response.status_code == 200
    assert response.json()["name"] == test_topic.name

async def test_create_topic(client: TestClient, topic_data):
    """Test topic creation"""
    response = client.post("/api/v1/topics", json=topic_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == topic_data["name"]

async def test_create_duplicate_topic(client: TestClient, test_topic):
    """Test creating topic with duplicate name"""
    duplicate_data = {"name": test_topic.name, "description": "New description"}
    response = client.post("/api/v1/topics", json=duplicate_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

async def test_get_topic_articles(client: TestClient, test_topic, test_article, db):
    """Test getting articles for a topic"""
    from app.crud.article import article_crud
    await article_crud.add_topic(db, test_article.id, test_topic.id)
    
    response = client.get(f"/api/v1/topics/{test_topic.id}/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == test_article.title

async def test_get_topic_books(client: TestClient, test_topic, test_book, db):
    """Test getting books for a topic"""
    from app.crud.book import book_crud
    await book_crud.add_topic(db, test_book.id, test_topic.id)
    
    response = client.get(f"/api/v1/topics/{test_topic.id}/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == test_book.title

async def test_search_topics(client: TestClient, test_topic):
    """Test searching topics"""
    response = client.get(f"/api/v1/topics?keyword={test_topic.name}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert data["items"][0]["name"] == test_topic.name

async def test_topic_not_found(client: TestClient):
    """Test 404 error for non-existent topic"""
    response = client.get("/api/v1/topics/99999")
    assert response.status_code == 404

async def test_invalid_topic_data(client: TestClient):
    """Test validation error for invalid topic data"""
    invalid_data = {"name": ""}  # Empty name not allowed
    response = client.post("/api/v1/topics", json=invalid_data)
    assert response.status_code == 422