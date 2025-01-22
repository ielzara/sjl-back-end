from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseSchema(BaseModel):
    '''
    Base Pydantic schema with SQLAlchemy ORM config
    Allows Pydantic to read SQLAlchemy model config
    '''
    model_config = ConfigDict(from_attributes=True)

class BaseDBSchema(BaseSchema):
    '''
    Base schema for databes models with ID and timpestamps
    ''' 
    id: int
    created_at: datetime
    uodated_at: Optional[datetime] = None

class BaseCreateSchema(BaseSchema):
    '''
    Base schema for creating new items
    '''
    pass

class BaseUpdateSchema(BaseSchema):
    '''
    Base schema for updating existing items
    '''
    pass

class BasePaginationSchema(BaseSchema):
    '''
    Base schema for pagination parameters
    '''
    skip: int = 0
    limit: int = 10

class BasePaginationResponseSchema(BaseSchema, Generic[ModelType]):
    '''
    Schema for paginated response with offset and limit pagination
    '''
    total: int
    items: list[ModelType]
    skip: int
    limit: int
    has_more: bool