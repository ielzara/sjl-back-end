from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.crud.base import CRUDBase
from app.models.topic import Topic
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

    async def get_with_counts(self, db: AsyncSession, *, skip: int = 0, limit: int = 10) -> List[Topic]:
        '''
        get topics with counts of associated articles and books
        **Parameters**
        * `db`: AsyncSession instance
        * `skip`: number of topics to skip
        * `limit`: number of topics to return
        **Returns**
        * list of topic instances
        '''
        query = select(self.model, func.count(distinct(Article.id)).label('article_count'), func.count(distinct(Book.id)).label('book_count')).outerjoin(self.model.articles).outerjoin(self.model.books).group_by(self.model.id).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def search(self, db: AsyncSession, *, keyword: str, skip: int = 0, limit: int = 10) -> List[Topic]:
        '''
        search topic by keyword in name or description with pagination
        **Parameters**
        * `db`: AsyncSession instance
        * `keyword`: search keyword
        * `skip`: number of topics to skip
        * `limit`: number of topics to return
        **Returns**
        * list of topic instances
        '''
        query = select(self.model).filter(self.model.name.ilike(f"%{keyword}%") | self.model.description.ilike(f"%{keyword}%")).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

# Create CRUDTopic instance
topic = CRUDTopic(Topic)