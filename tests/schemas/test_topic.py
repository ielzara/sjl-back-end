import pytest
from pydantic import ValidationError
from app.schemas.topic import TopicCreate, TopicUpdate, TopicDB, TopicWithCountsDB

def test_topic_create_valid():
    """Test creating a topic with valid data"""
    # Test with all fields
    topic_data = {
        "name": "Test Topic",
        "description": "This is a test topic description"
    }
    topic = TopicCreate(**topic_data)
    assert topic.name == topic_data["name"]
    assert topic.description == topic_data["description"]

    # Test with only required fields
    topic_data = {
        "name": "Test Topic"
    }
    topic = TopicCreate(**topic_data)
    assert topic.name == topic_data["name"]
    assert topic.description is None

def test_topic_create_missing_name():
    """Test topic creation fails when name is missing"""
    topic_data = {
        "description": "Test description"
    }
    with pytest.raises(ValidationError) as exc_info:
        TopicCreate(**topic_data)
    assert "name" in str(exc_info.value)

def test_topic_create_whitespace_validation():
    """Test topic creation with whitespace-only strings"""
    topic_data = {
        "name": "   ",  # Whitespace-only name
        "description": "\n\t"  # Whitespace-only description
    }
    with pytest.raises(ValidationError) as exc_info:
        TopicCreate(**topic_data)
    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert "name" in error_fields

def test_topic_update_optional_fields():
    """Test topic update with optional fields"""
    # Test with only some fields
    update_data = {
        "description": "Updated description"
    }
    topic_update = TopicUpdate(**update_data)
    assert topic_update.name is None
    assert topic_update.description == update_data["description"]

    # Test with empty update
    empty_update = TopicUpdate()
    assert empty_update.name is None
    assert empty_update.description is None

def test_topic_db_schema():
    """Test topic DB schema includes ID"""
    topic_data = {
        "id": 1,
        "name": "Test Topic",
        "description": "Test description"
    }
    topic = TopicDB(**topic_data)
    assert topic.id == topic_data["id"]
    assert topic.name == topic_data["name"]
    assert topic.description == topic_data["description"]

def test_topic_with_counts_schema():
    """Test topic with counts schema"""
    topic_data = {
        "id": 1,
        "name": "Test Topic",
        "description": "Test description",
        "article_count": 5,
        "book_count": 3
    }
    topic = TopicWithCountsDB(**topic_data)
    assert topic.id == topic_data["id"]
    assert topic.name == topic_data["name"]
    assert topic.description == topic_data["description"]
    assert topic.article_count == topic_data["article_count"]
    assert topic.book_count == topic_data["book_count"]

def test_topic_create_name_length():
    """Test topic creation with name length validation"""
    # Test with very long name
    topic_data = {
        "name": "a" * 300,  # Extremely long name
        "description": "Test description"
    }
    with pytest.raises(ValidationError) as exc_info:
        TopicCreate(**topic_data)
    assert "name" in str(exc_info.value)

def test_topic_create_invalid_types():
    """Test topic creation with invalid data types"""
    topic_data = {
        "name": 123,  # Name should be string
        "description": True  # Description should be string
    }
    with pytest.raises(ValidationError) as exc_info:
        TopicCreate(**topic_data)
    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert error_fields.intersection({"name", "description"})