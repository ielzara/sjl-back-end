from typing import Optional
from pydantic import HttpUrl, field_validator, constr

from app.schemas.base import BaseSchema, BaseDBSchema

class BookBase(BaseSchema):
    '''
    Base schema for Book with shared attributes
    '''
    title: constr(min_length=1, strip_whitespace=True)
    author: constr(min_length=1, strip_whitespace=True)
    description: constr(min_length=1, strip_whitespace=True)
    url: HttpUrl
    cover_url: HttpUrl
    isbn: str
    unique_id: str

    @field_validator('title', 'author', 'description')
    def validate_non_empty_string(cls, v: str) -> str:
        """Validate that strings are not just whitespace"""
        if not v.strip():
            raise ValueError("String cannot be empty or contain only whitespace")
        return v



class BookCreate(BookBase):
    '''
    Schema for creating a new book
    '''
    pass

class BookUpdate(BaseSchema):
    '''
    Schema for updating an existing book - all fields are optional
    '''
    title: Optional[constr(min_length=1, strip_whitespace=True)] = None
    author: Optional[constr(min_length=1, strip_whitespace=True)] = None
    description: Optional[constr(min_length=1, strip_whitespace=True)] = None
    url: Optional[HttpUrl] = None
    cover_url: Optional[HttpUrl] = None
    isbn: Optional[str] = None
    unique_id: Optional[str] = None

class BookDB(BookBase, BaseDBSchema):
    '''
    Schema for reading a book from the database (response model)
    '''
    relevance_explanation: Optional[str] = None