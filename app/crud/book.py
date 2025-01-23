from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.book import Book
from app.models.topic import Topic
from app.schemas.book import BookCreate, BookUpdate

class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):
    async def get_by_isbn(self, db: AsyncSession, *, isbn: str) -> Optional[Book]:
        '''
        get a single book by ISBN
        **Parameters**
        * `db`: AsyncSession instance
        * `isbn`: book ISBN
        **Returns**
        * book instance
        '''
        query = select(self.model).filter(self.model.isbn == isbn)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_author(
        self, 
        db: AsyncSession, 
        *, 
        author: str, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Book], int, bool]:
        '''
        get books by author with pagination
        **Parameters**
        * `db`: AsyncSession instance
        * `author`: author name
        * `skip`: number of books to skip
        * `limit`: number of books to return
        **Returns**
        * (list of book instances, total count, has_more flag)
        '''
        filter_query = select(self.model).filter(self.model.author.ilike(f"%{author}%"))
        return await self.get_multi_paginated(db, skip=skip, limit=limit, filter_query=filter_query)

    async def get_by_topic(
        self, 
        db: AsyncSession, 
        *, 
        topic_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Book], int, bool]:
        '''
        get books by topic with pagination
        **Parameters**
        * `db`: AsyncSession instance
        * `topic_id`: topic id
        * `skip`: number of books to skip
        * `limit`: number of books to return
        **Returns**
        * (list of book instances, total count, has_more flag)
        '''
        filter_query = select(self.model).join(self.model.topics).filter(Topic.id == topic_id)
        return await self.get_multi_paginated(db, skip=skip, limit=limit, filter_query=filter_query)
    
    async def search(
        self, 
        db: AsyncSession, 
        *, 
        keyword: str, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Book], int, bool]:
        '''
        search book by keyword in title or description
        **Parameters**
        * `db`: AsyncSession instance
        * `keyword`: search keyword
        * `skip`: number of books to skip
        * `limit`: number of books to return
        **Returns**
        * (list of book instances, total count, has_more flag)
        '''
        filter_query = select(self.model).filter(
            (self.model.title.ilike(f"%{keyword}%")) | 
            (self.model.description.ilike(f"%{keyword}%"))
        )
        return await self.get_multi_paginated(db, skip=skip, limit=limit, filter_query=filter_query)


# Create CRUD instance
book_crud = CRUDBook(Book)