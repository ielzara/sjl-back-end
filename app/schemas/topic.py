from typing import Optional

from app.schemas.base import BaseSchema, BaseDBSchema

class TopicBase(BaseSchema):
    '''
    Base schema for Topic with shared attributes
    '''
    name: str
    description: Optional[str] = None

class TopicCreate(TopicBase):
    '''
    Schema for creating a new topic
    '''
    pass

class TopicUpdate(BaseSchema):
    '''
    Schema for updating an existing topic - all fields are optional
    '''
    name: Optional[str] = None
    description: Optional[str] = None

class TopicDB(TopicBase, BaseDBSchema):
    '''
    Schema for reading a topic from the database (response model)
    '''
    pass

class TopicWithCountsDB(TopicDB):
    '''
    Schema for reading a topic with counts of associated articles and books
    '''
    article_count: int
    book_count: int