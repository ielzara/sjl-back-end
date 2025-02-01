from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, field_validator, Field

# This TypeVar is used for making our pagination response generic
ModelType = TypeVar("ModelType")

class BaseSchema(BaseModel):
    """Base schema that all other schemas inherit from.
    Configures Pydantic to work with SQLAlchemy models."""
    model_config = ConfigDict(from_attributes=True)

class BaseDBSchema(BaseSchema):
    """Schema for database models that adds ID field.
    Used for responses that include database records."""
    id: int

class PaginatedResponse(BaseSchema, Generic[ModelType]):
    """Schema for paginated responses.
    Handles both pagination parameters and the response structure."""
    total: int = Field(ge=0, description="Total number of items available")
    items: list[ModelType]
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=10, gt=0, le=100, description="Maximum number of items to return")
    has_more: bool

    @field_validator('total')
    def validate_total(cls, v: int) -> int:
        """Validate that total count is non-negative"""
        if v < 0:
            raise ValueError("Total count cannot be negative")
        return v

    @field_validator('items')
    def validate_items_count(cls, v: list[ModelType], values) -> list[ModelType]:
        """Validate that items list doesn't exceed limit"""
        limit = values.data.get('limit', 10)
        if len(v) > limit:
            raise ValueError(f"Items list exceeds limit of {limit}")
        return v