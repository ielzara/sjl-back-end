from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.book import Book
from app.models.topic import Topic
from app.models.associations import book_topics
from app.schemas.book import BookCreate, BookUpdate

class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):
    async def get_by_isbn(self, db: AsyncSession, *, isbn: str) -> Optional[Book]:
        """Get a single book by ISBN"""
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
        """Get books by author with pagination"""
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
        """Get books by topic with pagination"""
        filter_query = select(self.model).join(self.model.topics).filter(Topic.id == topic_id)
        return await self.get_multi_paginated(db, skip=skip, limit=limit, filter_query=filter_query)

    async def add_topic(
        self, 
        db: AsyncSession, 
        book_id: int, 
        topic_id: int
    ) -> None:
        """Add a topic to a book
        
        First checks if the association already exists to avoid duplicates
        """
        # Check if association already exists
        existing = await db.execute(
            select(book_topics).where(
                (book_topics.c.book_id == book_id) & 
                (book_topics.c.topic_id == topic_id)
            )
        )
        if not existing.first():
            await db.execute(
                book_topics.insert().values(
                    book_id=book_id,
                    topic_id=topic_id
                )
            )
            await db.commit()

    # Using base search with book-specific fields
    async def search(
        self, 
        db: AsyncSession, 
        keyword: str, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Book], int, bool]:
        """Search books in title, author, and description"""
        return await super().search(
            db,
            keyword=keyword,
            fields=['title', 'author', 'description'],
            skip=skip,
            limit=limit
        )

# Create CRUD instance
book_crud = CRUDBook(Book)