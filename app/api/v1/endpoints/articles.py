from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.article import article_crud
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleDB
from app.schemas.base import BasePaginationResponseSchema
from app.core.database import get_db

router = APIRouter()

@router.get("", response_model=BasePaginationResponseSchema[ArticleDB])
async def get_articles(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    topic_id: Optional[int] = None,
    featured: Optional[bool] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> BasePaginationResponseSchema[ArticleDB]:
    '''
    get articles with pagination and optional filters
    **Parameters**
    * `db`: AsyncSession instance
    * `skip`: number of articles to skip
    * `limit`: number of articles to return
    * `topic_id`: topic id
    * `featured`: filter by featured status
    * `keyword`: search keyword
    * `start_date`: start date
    * `end_date`: end date
    **Returns**
    * paginated response of article instances
    '''
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

    return BasePaginationResponseSchema(
        total=total,
        items=items,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/{article_id}", response_model=ArticleDB)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)) -> ArticleDB:
    '''
    get a specific article by id
    **Parameters**
    * `article_id`: article id
    * `db`: AsyncSession instance
    **Returns**
    * article instance
    '''
    article = await article_crud.get(db, id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("", response_model=ArticleDB, status_code=201)
async def create_article(article_in: ArticleCreate, db: AsyncSession = Depends(get_db)) -> ArticleDB:
    '''
    create a new article
    **Parameters**
    * `article_in`: ArticleCreate instance
    * `db`: AsyncSession instance
    **Returns**
    * article instance
    '''
    article = await article_crud.create(db, obj_in=article_in)
    return article

@router.put("/{article_id}", response_model=ArticleDB)
async def update_article(article_id: int, article_in: ArticleUpdate, db: AsyncSession = Depends(get_db)) -> ArticleDB:
    '''
    update an existing article
    **Parameters**
    * `article_id`: article id
    * `article_in`: ArticleUpdate instance
    * `db`: AsyncSession instance
    **Returns**
    * article instance
    '''
    article = await article_crud.get(db, id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    article = await article_crud.update(db, db_obj=article, obj_in=article_in)
    return article

@router.delete("/{article_id}", status_code=204)
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    '''
    delete an existing article
    **Parameters**
    * `article_id`: article id
    * `db`: AsyncSession instance
    '''
    article = await article_crud.get(db, id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await article_crud.remove(db, id=article_id)