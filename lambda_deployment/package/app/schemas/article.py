from datetime import datetime
from typing import Optional, List
from pydantic import HttpUrl, field_validator, constr

from app.schemas.base import BaseSchema, BaseDBSchema
from app.schemas.book import BookDB

class ArticleBase(BaseSchema):
    '''Base schema for Article with shared attributes'''
    title: constr(min_length=1, strip_whitespace=True)
    content: constr(min_length=1, strip_whitespace=True)
    source: constr(min_length=1, strip_whitespace=True)
    url: HttpUrl
    featured: bool = False
    date: datetime
    main_image_url: Optional[HttpUrl] = None
    main_image_alt: Optional[str] = None
    main_image_caption: Optional[str] = None
    main_image_credit: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None

    @field_validator('title', 'content', 'source')
    def validate_non_empty_string(cls, v: str) -> str:
        """Validate that strings are not just whitespace"""
        if not v.strip():
            raise ValueError("String cannot be empty or contain only whitespace")
        return v

class ArticleCreate(ArticleBase):
    '''Schema for creating a new article'''
    pass

class ArticleUpdate(ArticleBase):
    '''Schema for updating an existing article - all fields are optional'''
    title: Optional[constr(min_length=1, strip_whitespace=True)] = None
    content: Optional[constr(min_length=1, strip_whitespace=True)] = None
    source: Optional[constr(min_length=1, strip_whitespace=True)] = None
    url: Optional[HttpUrl] = None
    featured: Optional[bool] = None
    date: Optional[datetime] = None 

class ArticleResponse(ArticleBase, BaseDBSchema):
    """Schema for article responses without relationships"""
    pass

class ArticleDB(ArticleBase, BaseDBSchema):
    '''Schema for reading an article from the database'''
    books: List[BookDB] = []