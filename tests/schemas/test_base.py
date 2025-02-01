import pytest
from pydantic import ValidationError
from typing import List
from app.schemas.base import BaseSchema, BaseDBSchema, PaginatedResponse

def test_base_schema():
    """Test base schema functionality"""
    class TestSchema(BaseSchema):
        name: str
        value: int

    # Test valid data
    data = {
        "name": "test",
        "value": 42
    }
    schema = TestSchema(**data)
    assert schema.name == data["name"]
    assert schema.value == data["value"]

    # Test invalid data type
    invalid_data = {
        "name": "test",
        "value": "not an integer"
    }
    with pytest.raises(ValidationError):
        TestSchema(**invalid_data)

def test_base_db_schema():
    """Test base DB schema functionality"""
    class TestDBSchema(BaseDBSchema):
        name: str

    # Test valid data with ID
    data = {
        "id": 1,
        "name": "test"
    }
    schema = TestDBSchema(**data)
    assert schema.id == data["id"]
    assert schema.name == data["name"]

    # Test missing ID
    invalid_data = {
        "name": "test"
    }
    with pytest.raises(ValidationError) as exc_info:
        TestDBSchema(**invalid_data)
    assert "id" in str(exc_info.value)

def test_paginated_response():
    """Test paginated response schema"""
    class TestItem(BaseSchema):
        name: str

    # Test valid pagination data
    items = [TestItem(name="item1"), TestItem(name="item2")]
    pagination_data = {
        "total": 10,
        "items": items,
        "skip": 0,
        "limit": 2,
        "has_more": True
    }
    response = PaginatedResponse[TestItem](**pagination_data)
    assert response.total == pagination_data["total"]
    assert len(response.items) == len(items)
    assert response.skip == pagination_data["skip"]
    assert response.limit == pagination_data["limit"]
    assert response.has_more == pagination_data["has_more"]

def test_paginated_response_invalid_params():
    """Test paginated response with invalid parameters"""
    class TestItem(BaseSchema):
        name: str

    # Test negative skip
    invalid_data = {
        "total": 10,
        "items": [TestItem(name="item1")],
        "skip": -1,  # Invalid negative skip
        "limit": 10,
        "has_more": False
    }
    with pytest.raises(ValidationError) as exc_info:
        PaginatedResponse[TestItem](**invalid_data)
    assert "skip" in str(exc_info.value)

    # Test zero/negative limit
    invalid_data["skip"] = 0
    invalid_data["limit"] = 0  # Invalid zero limit
    with pytest.raises(ValidationError) as exc_info:
        PaginatedResponse[TestItem](**invalid_data)
    assert "limit" in str(exc_info.value)

    # Test invalid total
    invalid_data["limit"] = 10
    invalid_data["total"] = -1  # Invalid negative total
    with pytest.raises(ValidationError) as exc_info:
        PaginatedResponse[TestItem](**invalid_data)
    assert "total" in str(exc_info.value)

def test_paginated_response_empty():
    """Test paginated response with empty items list"""
    class TestItem(BaseSchema):
        name: str

    pagination_data = {
        "total": 0,
        "items": [],
        "skip": 0,
        "limit": 10,
        "has_more": False
    }
    response = PaginatedResponse[TestItem](**pagination_data)
    assert response.total == 0
    assert len(response.items) == 0
    assert not response.has_more

def test_paginated_response_default_values():
    """Test paginated response with default values"""
    class TestItem(BaseSchema):
        name: str

    # Test with minimal required data
    pagination_data = {
        "total": 1,
        "items": [TestItem(name="item1")],
        "has_more": False
    }
    response = PaginatedResponse[TestItem](**pagination_data)
    assert response.skip == 0  # Default skip value
    assert response.limit == 10  # Default limit value

def test_paginated_response_type_validation():
    """Test paginated response with incorrect item types"""
    class TestItem(BaseSchema):
        name: str
        
    class DifferentItem(BaseSchema):
        value: int

    # Try to create response with wrong item type
    pagination_data = {
        "total": 1,
        "items": [DifferentItem(value=42)],  # Wrong item type
        "skip": 0,
        "limit": 10,
        "has_more": False
    }
    with pytest.raises(ValidationError):
        PaginatedResponse[TestItem](**pagination_data)

def test_base_schema_from_orm():
    """Test base schema creation from ORM-like objects"""
    class MockORMObject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class TestSchema(BaseSchema):
        name: str
        value: int
    
    # Create a mock ORM object
    orm_obj = MockORMObject(name="test", value=42)
    
    # Test schema creation from ORM object
    schema = TestSchema.model_validate(orm_obj)
    assert schema.name == "test"
    assert schema.value == 42