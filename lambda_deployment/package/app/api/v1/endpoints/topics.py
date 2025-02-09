from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.crud.topic import topic_crud
from app.schemas.topic import TopicCreate, TopicUpdate, TopicDB
from app.schemas.base import PaginatedResponse
from app.core.database import get_db
from app.schemas.article import ArticleDB
from app.schemas.book import BookDB

router = APIRouter()

@router.get("", response_model=PaginatedResponse[TopicDB])
async def get_topics(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None
) -> PaginatedResponse[TopicDB]:
    '''Get topics with pagination'''
    if keyword:
        items, total, has_more = await topic_crud.search(
            db, keyword=keyword, skip=skip, limit=limit
        )
    else:
        items, total, has_more = await topic_crud.get_multi_paginated(
            db, skip=skip, limit=limit
        )

    return PaginatedResponse(
        total=total,
        items=items,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/{topic_id}", response_model=TopicDB)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
) -> TopicDB:
    '''Get a specific topic by id'''
    topic = await topic_crud.get(db, id=topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/{topic_id}/articles", response_model=List[ArticleDB])
async def get_topic_articles(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[ArticleDB]:
    '''Get all articles with this topic'''
    topic = await topic_crud.get(db, id=topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic.articles

@router.get("/{topic_id}/books", response_model=List[BookDB])
async def get_topic_books(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[BookDB]:
    '''Get all books with this topic'''
    topic = await topic_crud.get(db, id=topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic.books

@router.post("", response_model=TopicDB, status_code=201)
async def create_topic(
    topic_in: TopicCreate,
    db: AsyncSession = Depends(get_db)
) -> TopicDB:
    '''Create a new topic'''
    existing_topic = await topic_crud.get_by_name(db, name=topic_in.name)
    if existing_topic:
        raise HTTPException(
            status_code=400,
            detail="Topic with this name already exists"
        )
    return await topic_crud.create(db, obj_in=topic_in)