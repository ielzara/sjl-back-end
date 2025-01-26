from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date

from app.crud.base import CRUDBase
from app.models.article import Article
from app.models.topic import Topic
from app.schemas.article import ArticleCreate, ArticleUpdate

class CRUDArticle(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    async def get_featured(self, db: AsyncSession, *, limit: int = 5) -> List[Article]:
        '''Get featured articles'''
        query = select(Article).filter(Article.featured == True).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_date_range(self, db: AsyncSession, *, start_date: date, end_date: date) -> List[Article]:
        '''Get articles by date range'''
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
        '''Get articles by topic with pagination'''
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
        '''Search articles by keyword in title or content'''
        filter_query = select(self.model).filter(
            (self.model.title.ilike(f'%{keyword}%')) | 
            (self.model.content.ilike(f'%{keyword}%'))
        )

        return await self.get_multi_paginated(db, skip=skip, limit=limit, filter_query=filter_query)

# Create an instance of CRUDArticle
article_crud = CRUDArticle(Article)