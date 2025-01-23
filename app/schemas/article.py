from datetime import date
from typing import Optional, List
from pydantic import HttpUrl, field_validator

from app.schemas.base import BaseSchema, BaseDBSchema

class ArticleBase(BaseSchema):
    '''
    Base schema for Article with shared attributes
    '''
    title: str
    content: str
    source: str
    url: HttpUrl
    featured: bool = False
    date: date
    
    @field_validator('date', mode='before')
    def validate_date(cls, v):
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v

class ArticleCreate(ArticleBase):
    '''
    Schema for creating a new article
    '''
    pass

class ArticleUpdate(ArticleBase):
    '''
    Schema for updating an existing article - all fields are optional
    '''
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    url: Optional[HttpUrl] = None
    featured: Optional[bool] = None
    date: Optional[date] = None 

class ArticleDB(ArticleBase, BaseDBSchema):
    '''
    Schema for reading an article from the database (response model)
    '''
    pass