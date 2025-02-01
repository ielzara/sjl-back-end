from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.book import book_crud
from app.schemas.book import BookCreate, BookUpdate, BookDB
from app.schemas.base import PaginatedResponse
from app.core.database import get_db
from app.schemas.article import ArticleDB
from app.schemas.topic import TopicDB

router = APIRouter()

@router.get("", response_model=PaginatedResponse[BookDB])
async def get_books(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    topic_id: Optional[int] = None,
    author: Optional[str] = None,
    keyword: Optional[str] = None,
) -> PaginatedResponse[BookDB]:
    '''Get books with pagination and optional filters'''
    if topic_id:
        items, total, has_more = await book_crud.get_by_topic(
            db, topic_id=topic_id, skip=skip, limit=limit
        )
    elif author:
        items, total, has_more = await book_crud.get_by_author(
            db, author=author, skip=skip, limit=limit
        )
    elif keyword:
        items, total, has_more = await book_crud.search(
            db, keyword=keyword, skip=skip, limit=limit
        )
    else:
        items, total, has_more = await book_crud.get_multi_paginated(
            db, skip=skip, limit=limit
        )

    return PaginatedResponse(
        total=total,
        items=items,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/{book_id}", response_model=BookDB)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)) -> BookDB:
    '''Get a specific book by id'''
    book = await book_crud.get(db, id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.get("/isbn/{isbn}", response_model=BookDB)
async def get_book_by_isbn(isbn: str, db: AsyncSession = Depends(get_db)) -> BookDB:
    '''Get a specific book by ISBN'''
    book = await book_crud.get_by_isbn(db, isbn=isbn)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.get("/{book_id}/articles", response_model=List[ArticleDB])
async def get_book_articles(
    book_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[ArticleDB]:
    '''Get all articles that reference this book'''
    book = await book_crud.get(db, id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.articles

@router.get("/{book_id}/topics", response_model=List[TopicDB])
async def get_book_topics(
    book_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[TopicDB]:
    '''Get all topics associated with this book'''
    book = await book_crud.get(db, id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.topics

@router.post("", response_model=BookDB, status_code=201)
async def create_book(book_in: BookCreate, db: AsyncSession = Depends(get_db)) -> BookDB:
    '''Create a new book'''
    book = await book_crud.create(db, obj_in=book_in)
    return book

@router.put("/{book_id}", response_model=BookDB)
async def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession = Depends(get_db)
) -> BookDB:
    '''Update an existing book'''
    book = await book_crud.get(db, id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    book = await book_crud.update(db, db_obj=book, obj_in=book_in)
    return book

@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    '''Delete an existing book'''
    book = await book_crud.get(db, id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    await book_crud.remove(db, id=book_id)