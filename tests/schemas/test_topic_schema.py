import pytest
from pydantic import ValidationError
from app.schemas.topic import TopicCreate, TopicUpdate, TopicDB

def test_topic_create_valid():
    """Test creating a topic with valid data"""
    topic_data = {
        "name": "Test Topic",
        "description": "Test description"
    }
    topic = TopicCreate(**topic_data)
    assert topic.name == topic_data["name"]
    assert topic.description == topic_data["description"]

def test_topic_name_validation():
    """Test topic name validation"""
    # Too long name
    with pytest.raises(ValidationError):
        TopicCreate(name="a" * 101)
    
    # Empty name
    with pytest.raises(ValidationError):
        TopicCreate(name="")

def test_topic_update():
    """Test topic update schema"""
    update = TopicUpdate(name="New Name")
    assert update.name == "New Name"
    assert update.description is None
