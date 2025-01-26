from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict

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
    total: int
    items: list[ModelType]
    skip: int = 0
    limit: int = 10
    has_more: bool