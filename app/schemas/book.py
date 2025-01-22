from typing import Optional
from pydantic import HttpUrl

from app.schemas.base import BaseSchema, BaseDBSchema

class BookBase(BaseSchema):
    '''
    Base schema for Book with shared attributes
    '''
    title: str
    author: str
    description: str
    url: HttpUrl
    cover_url: HttpUrl
    isbn: str

class BookCreate(BookBase):
    '''
    Schema for creating a new book
    '''
    pass

class BookUpdate(BaseSchema):
    '''
    Schema for updating an existing book - all fields are optional
    '''
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    cover_url: Optional[HttpUrl] = None
    isbn: Optional[str] = None

class BookDB(BookBase, BaseDBSchema):
    '''
    Schema for reading a book from the database (response model)
    '''
    pass
