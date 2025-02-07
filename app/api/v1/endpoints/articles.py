from typing import Optional, List, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload, joinedload, aliased
from sqlalchemy.sql import text as sql_text

from app.crud.article import article_crud
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleDB
from app.schemas.base import PaginatedResponse
from app.schemas.book import BookDB
from app.schemas.topic import TopicDB
from app.models.article import Article
from app.models.book import Book
from app.models.associations import article_books
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("", response_model=PaginatedResponse[ArticleDB])
async def get_articles(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    topic_id: Optional[int] = None,
    featured: Optional[bool] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> PaginatedResponse[ArticleDB]:
    '''Get articles with pagination and optional filters'''
    if topic_id:
        items, total, has_more = await article_crud.get_by_topic(
            db, topic_id=topic_id, skip=skip, limit=limit
        )
    elif keyword:
        items, total, has_more = await article_crud.search(
            db, keyword=keyword, skip=skip, limit=limit
        )
    elif featured:
        items = await article_crud.get_featured(db, limit=limit)
        total = len(items)
        has_more = False
    elif start_date and end_date:
        items = await article_crud.get_by_date_range(
            db, start_date=start_date, end_date=end_date
        )
        total = len(items)
        has_more = False
    else:
        items, total, has_more = await article_crud.get_multi_paginated(
            db, skip=skip, limit=limit
        )

    return PaginatedResponse(
        total=total,
        items=items,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/{article_id}", response_model=ArticleDB)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)) -> ArticleDB:
    '''Get a specific article by id'''
    article = await article_crud.get(db, id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.get("/{article_id}/books", response_model=List[BookDB])
async def get_article_books(
    article_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[BookDB]:
    '''Get all books linked to a specific article with their relevance explanations'''
    try:
        # Get associations first
        assoc_query = await db.execute(
            select(article_books).where(article_books.c.article_id == article_id)
        )
        associations = {
            row.book_id: row.relevance_explanation 
            for row in assoc_query.fetchall()
        }
        
        if not associations:
            raise HTTPException(status_code=404, detail="Article not found or has no books")
            
        # Get books
        books_query = await db.execute(
            select(Book)
            .where(Book.id.in_(associations.keys()))
        )
        books = books_query.scalars().all()
        
        # Create response with relevance explanations
        response_books = []
        for book in books:
            book_dict = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "url": book.url,
                "cover_url": book.cover_url,
                "isbn": book.isbn,
                "unique_id": book.unique_id,
                "relevance_explanation": associations[book.id]
            }
            response_books.append(BookDB(**book_dict))
        
        return response_books

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article books: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{article_id}/topics", response_model=List[TopicDB])
async def get_article_topics(
    article_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[TopicDB]:
    '''Get all topics associated with an article'''
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.topics))
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    logger.info(f"Found {len(article.topics)} topics for article {article_id}")
    return article.topics

@router.post("", response_model=ArticleDB, status_code=201)
async def create_article(article_in: ArticleCreate, db: AsyncSession = Depends(get_db)) -> ArticleDB:
    '''Create a new article'''
    try:
        data = article_in.model_dump()
        if isinstance(data['date'], str):
            data['date'] = date.fromisoformat(data['date'])
        
        article = await article_crud.create(db, obj_in=data)
        if article is None:
            raise HTTPException(status_code=500, detail="Failed to create article")
        
        return article
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{article_id}", response_model=ArticleDB)
async def update_article(article_id: int, article_in: ArticleUpdate, db: AsyncSession = Depends(get_db)) -> ArticleDB:
    '''Update an existing article'''
    article = await article_crud.get(db, id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    article = await article_crud.update(db, db_obj=article, obj_in=article_in)
    return article

@router.delete("/{article_id}", status_code=204)
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    '''Delete an existing article'''
    article = await article_crud.get(db, id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await article_crud.remove(db, id=article_id)