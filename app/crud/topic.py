from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct

from app.crud.base import CRUDBase
from app.models.topic import Topic
from app.models.article import Article
from app.models.book import Book
from app.schemas.topic import TopicCreate, TopicUpdate

class CRUDTopic(CRUDBase[Topic, TopicCreate, TopicUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Topic]:
        '''
        get a single topic by name
        **Parameters**
        * `db`: AsyncSession instance
        * `name`: topic name
        **Returns**
        * topic instance
        '''
        query = select(self.model).filter(func.lower(self.model.name) == func.lower(name))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_counts(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[dict], int, bool]:
        '''
        get topics with counts of associated articles and books
        **Parameters**
        * `db`: AsyncSession instance
        * `skip`: number of topics to skip
        * `limit`: number of topics to return
        **Returns**
        * (list of topic instances with counts, total count, has_more flag)
        '''
        # Count query for pagination
        count_query = select(func.count()).select_from(self.model)
        total = await db.scalar(count_query)

        # Main query with counts
        query = (
            select(
                self.model,
                func.count(distinct(Article.id)).label('article_count'),
                func.count(distinct(Book.id)).label('book_count')
            )
            .outerjoin(self.model.articles)
            .outerjoin(self.model.books)
            .group_by(self.model.id)
            .offset(skip)
            .limit(limit + 1) 
        )

        result = await db.execute(query)
        items = result.all()
        
        # Check if there are more items
        has_more = len(items) > limit
        items = items[:limit]
        
        # Convert to dictionary format
        topics_with_counts = [
            {
                **row[0].__dict__,
                'article_count': row[1],
                'book_count': row[2]
            }
            for row in items
        ]
        
        return topics_with_counts, total, has_more

    async def search(
        self, 
        db: AsyncSession, 
        *, 
        keyword: str, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Topic], int, bool]:
        '''
        search topic by keyword in name or description
        **Parameters**
        * `db`: AsyncSession instance
        * `keyword`: search keyword
        * `skip`: number of topics to skip
        * `limit`: number of topics to return
        **Returns**
        * (list of topic instances, total count, has_more flag)
        '''
        filter_query = select(self.model).filter(
            self.model.name.ilike(f"%{keyword}%") | 
            self.model.description.ilike(f"%{keyword}%")
        )
        return await self.get_multi_paginated(db, skip=skip, limit=limit, filter_query=filter_query)

# Create CRUDTopic instance
topic_crud = CRUDTopic(Topic)