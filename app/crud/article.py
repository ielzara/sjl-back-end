from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.article import Article
from app.models.associations import article_topics, article_books
from app.models.book import Book
from app.crud.base import CRUDBase
from app.schemas.article import ArticleCreate, ArticleUpdate


class CRUDArticle(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    async def get_by_url(self, db: AsyncSession, url: str) -> Article:
        statement = select(Article).where(Article.url == url)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def add_topic(
        self,
        db: AsyncSession,
        article_id: int,
        topic_id: int
    ) -> None:
        """Add a topic to an article"""
        stmt = select(self.model).options(selectinload(self.model.topics)).where(self.model.id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()
        
        if not article:
            raise ValueError(f"Article {article_id} not found")
            
        await db.execute(
            article_topics.insert().values(
                article_id=article_id,
                topic_id=topic_id
            )
        )
        await db.commit()

    async def add_book(
        self,
        db: AsyncSession,
        article_id: int,
        book_id: int,
        relevance_explanation: str
    ) -> None:
        """Add a book to an article with relevance explanation"""
        stmt = select(self.model).options(selectinload(self.model.books)).where(self.model.id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()
        
        if not article:
            raise ValueError(f"Article {article_id} not found")
            
        # Use the association table directly
        await db.execute(
            article_books.insert().values(
                article_id=article_id,
                book_id=book_id,
                relevance_explanation=relevance_explanation
            )
        )
        await db.commit()

    async def has_book(self, db: AsyncSession, article_id: int, book_id: int) -> bool:
        statement = select(article_books).where(
            article_books.c.article_id == article_id,
            article_books.c.book_id == book_id
        )
        result = await db.execute(statement)
        return result.first() is not None


article_crud = CRUDArticle(Article)