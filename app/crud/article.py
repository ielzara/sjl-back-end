from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, date

from app.crud.base import CRUDBase
from app.models.article import Article
from app.models.topic import Topic
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

    async def get_by_date_range(self, db: AsyncSession, *, start_date: date, end_date: date) -> List[Article]:
        '''
        get articles by date range
        **Parameters**
        * `db`: AsyncSession instance
        * `start_date`: start date
        * `end_date`: end date
        **Returns**
        * list of article instances
        '''
        query = select(self.model).filter(
            self.model.date >= start_date, 
            self.model.date <= end_date
        ).order_by(self.model.date.desc())

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_topic(
        self,
        db: AsyncSession,
        *,
        topic_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Article], int, bool]:
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
        statement = select(self.model).join(
            self.model.topics
        ).where(
            Topic.id == topic_id
        ).options(
            selectinload(self.model.topics)
        )
        
        return await self.get_multi_paginated(db, skip=skip, limit=limit, filter_query=statement)

    async def search(
        self, 
        db: AsyncSession, 
        *, 
        keyword: str, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Article], int, bool]:
        '''
        search article by keyword in title or content
        **Parameters**
        * `db`: AsyncSession instance
        * `keyword`: search keyword
        * `skip`: number of articles to skip
        * `limit`: number of articles to return
        **Returns**
        * (articles, total count, has_more flag)
        '''
    
        filter_query = select(self.model).filter(
            (self.model.title.ilike(f'%{keyword}%')) | 
            (self.model.content.ilike(f'%{keyword}%'))
        )

        return await self.get_multi_paginated(db, skip=skip, limit=limit, filter_query=filter_query)

# Create an instance of CRUDArticle
article_crud = CRUDArticle(Article)