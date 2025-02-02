import pytest
from pydantic import ValidationError
from app.schemas.base import BaseSchema, BaseDBSchema, PaginatedResponse

def test_base_db_schema():
    """Test BaseDBSchema"""
    class TestSchema(BaseDBSchema):
        name: str

    # Valid
    schema = TestSchema(id=1, name="test")
    assert schema.id == 1
    
    # Missing id
    with pytest.raises(ValidationError):
        TestSchema(name="test")

def test_pagination():
    """Test PaginatedResponse"""
    class TestItem(BaseSchema):
        value: int

    response = PaginatedResponse[TestItem](
        total=10,
        items=[TestItem(value=1), TestItem(value=2)],
        skip=0,
        limit=10,
        has_more=False
    )
    assert len(response.items) == 2
    assert response.total == 10
