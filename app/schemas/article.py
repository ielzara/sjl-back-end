from datetime import datetime
from typing import Optional, List
from pydantic import HttpUrl

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
    date: datetime

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
    date: Optional[datetime] = None

class ArticleDB(ArticleBase, BaseDBSchema):
    '''
    Schema for reading an article from the database (response model)
    '''
    pass