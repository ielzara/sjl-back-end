from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate

class CRUDArticle(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    async def get_featured(self, db: AsyncSession, *, limit: int = 5) -> List[Article]:
        '''
        get featured articles
        **Parameters**
        * `db`: AsyncSession instance
        * `limit`: number of articles to return
        **Returns**
        * list of article instances
        '''
        query = select(Article).filter(Article.featured == True).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_date_range(self, db: AsyncSession, *, start_date: datetime, end_date: datetime) -> List[Article]:
        '''
        get articles by date range
        **Parameters**
        * `db`: AsyncSession instance
        * `start_date`: start date
        * `end_date`: end date
        **Returns**
        * list of article instances
        '''
        query = select(self.model).filter(self.model.date >= start_date, self.model.date <= end_date).order_by self.model.date.desc()

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_topic(self, db: AsyncSession, *, topic_id: int, skip: int = 0, limit: int = 10) -> Tuple[List[Article], int, bool]:
        '''
        get articles by topic with pagination
        **Parameters**
        * `db`: AsyncSession instance
        * `topic_id`: topic id
        * `skip`: number of articles to skip
        * `limit`: number of articles to return
        **Returns**
        * (articles, total count, has_more flag)
        '''

        filter_query = select(self.model).join(self.model.topics).filter(Topic.id == topic_id)
        result = await self.get_milti_paginated(db. skip=skip, limit=limit, filter_query=filter_query)
        return result.scalars().all()

    async def search(self, db: AsyncSession, *, keyword: str, skip: int = 0, limit: int = 10) -> List[Article]:
        '''
        search article by keyword in title or content
        **Parameters**
        * `db`: AsyncSession instance
        * `keyword`: search keyword
        * `skip`: number of articles to skip
        * `limit`: number of articles to return
        **Returns**
        * list of article instances
        '''

        query = select(self.model).filter(self.model.title.iLike(f'%keyword%') | (self.model.content.iLike(f'%keyword%'))).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

# create an instance of CRUDArticle
article = CRUDArticle(Article)