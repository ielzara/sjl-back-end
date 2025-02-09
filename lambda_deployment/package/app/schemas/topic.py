from pydantic import field_validator, constr
from app.schemas.base import BaseSchema, BaseDBSchema

class TopicBase(BaseSchema):
    '''Base schema for Topic with shared attributes'''
    name: constr(min_length=1, max_length=100, strip_whitespace=True)
    description: str | None = None

class TopicCreate(TopicBase):
    '''Schema for creating a new topic'''
    pass

class TopicUpdate(BaseSchema):
    '''Schema for updating an existing topic'''
    name: str | None = None
    description: str | None = None

class TopicDB(TopicBase, BaseDBSchema):
    '''Schema for reading a topic from the database'''
    pass