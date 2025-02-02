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
    isbn: constr(min_length=10, max_length=13, strip_whitespace=True)

    @field_validator('title', 'author', 'description')
    def validate_non_empty_string(cls, v: str) -> str:
        """Validate that strings are not just whitespace"""
        if not v.strip():
            raise ValueError("String cannot be empty or contain only whitespace")
        return v

    @field_validator('isbn')
    def validate_isbn(cls, v: str) -> str:
        """Validate ISBN format"""
        # Remove any hyphens or spaces
        isbn = ''.join(c for c in v if c.isdigit() or c.upper() == 'X')
        
        # Check if it's ISBN-10 or ISBN-13
        if len(isbn) not in (10, 13):
            raise ValueError("ISBN must be either 10 or 13 characters long")
        
        # For ISBN-10
        if len(isbn) == 10:
            # Check if first 9 characters are digits
            if not isbn[:9].isdigit():
                raise ValueError("First 9 characters of ISBN-10 must be digits")
            # Check if last character is digit or 'X'
            if not (isbn[9].isdigit() or isbn[9].upper() == 'X'):
                raise ValueError("Last character of ISBN-10 must be digit or 'X'")
        
        # For ISBN-13
        if len(isbn) == 13:
            if not isbn.isdigit():
                raise ValueError("ISBN-13 must contain only digits")
            # Check if it starts with valid prefix (978 or 979)
            if not isbn.startswith(('978', '979')):
                raise ValueError("ISBN-13 must start with 978 or 979")
        
        return isbn

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
    isbn: Optional[constr(min_length=10, max_length=13, strip_whitespace=True)] = None

class BookDB(BookBase, BaseDBSchema):
    '''
    Schema for reading a book from the database (response model)
    '''
    relevance_explanation: Optional[str] = None