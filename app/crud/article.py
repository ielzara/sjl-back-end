from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.article import Article
from app.models.associations import article_topics, article_books
from app.models.book import Book
from app.crud.base import CRUDBase
from app.schemas.article import ArticleCreate, ArticleUpdate
from typing import List, Tuple, Optional
from sqlalchemy.sql import text


class CRUDArticle(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    async def get_multi_paginated(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Article], int, bool]:
        """Get multiple articles with pagination, including books with relevance explanations"""
        # Get total count
        count_stmt = select(func.count(Article.id))
        total = await db.scalar(count_stmt)
        
        # Get articles with books and their relevance explanations
        stmt = (
            select(Article)
            .options(
                selectinload(Article.topics),
                selectinload(Article.books)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Article.date.desc())
        )
        
        result = await db.execute(stmt)
        articles = result.scalars().unique().all()
        
        # For each article, fetch the book relevance explanations
        for article in articles:
            if article.books:  # Only if article has books
                rel_stmt = select(article_books).where(
                    article_books.c.article_id == article.id
                )
                rel_result = await db.execute(rel_stmt)
                relevance_map = {
                    r.book_id: r.relevance_explanation 
                    for r in rel_result.fetchall()
                }
                
                # Add relevance explanations to books
                for book in article.books:
                    book.relevance_explanation = relevance_map.get(book.id)

        has_more = total > skip + limit
        
        return articles, total, has_more

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
        # First check if article exists
        stmt = select(self.model).options(selectinload(self.model.topics)).where(self.model.id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()
        
        if not article:
            raise ValueError(f"Article {article_id} not found")
            
        # Insert into association table
        await db.execute(
            article_topics.insert().values(
                article_id=article_id,
                topic_id=topic_id
            )
        )
        await db.commit()
        
        # Refresh to update relationships
        await db.refresh(article)

    async def add_book(
        self,
        db: AsyncSession,
        article_id: int,
        book_id: int,
        relevance_explanation: str
    ) -> None:
        """Add a book to an article with relevance explanation"""
        # First check if article exists
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
        
        # Refresh to update relationships
        await db.refresh(article)

    async def has_book(self, db: AsyncSession, article_id: int, book_id: int) -> bool:
        statement = select(article_books).where(
            article_books.c.article_id == article_id,
            article_books.c.book_id == book_id
        )
        result = await db.execute(statement)
        return result.first() is not None

    async def get_by_topic(
        self,
        db: AsyncSession,
        topic_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Article], int, bool]:
        """Get articles by topic with pagination"""
        # Get total count
        count_stmt = (
            select(func.count(Article.id))
            .join(Article.topics)
            .where(article_topics.c.topic_id == topic_id)
        )
        total = await db.scalar(count_stmt)

        # Get articles
        stmt = (
            select(Article)
            .join(Article.topics)
            .where(article_topics.c.topic_id == topic_id)
            .options(selectinload(Article.topics), selectinload(Article.books))
            .offset(skip)
            .limit(limit)
            .order_by(Article.date.desc())
        )

        result = await db.execute(stmt)
        articles = result.scalars().unique().all()
        
        # Add relevance explanations
        for article in articles:
            if article.books:
                rel_stmt = select(article_books).where(
                    article_books.c.article_id == article.id
                )
                rel_result = await db.execute(rel_stmt)
                relevance_map = {
                    r.book_id: r.relevance_explanation 
                    for r in rel_result.fetchall()
                }
                
                for book in article.books:
                    book.relevance_explanation = relevance_map.get(book.id)

        has_more = total > skip + limit

        return articles, total, has_more

    async def search(
        self,
        db: AsyncSession,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Article], int, bool]:
        """Search articles by keyword with pagination"""
        # Get total count
        count_stmt = (
            select(func.count(Article.id))
            .where(Article.title.ilike(f"%{keyword}%") | Article.content.ilike(f"%{keyword}%"))
        )
        total = await db.scalar(count_stmt)

        # Get articles
        stmt = (
            select(Article)
            .where(Article.title.ilike(f"%{keyword}%") | Article.content.ilike(f"%{keyword}%"))
            .options(selectinload(Article.topics), selectinload(Article.books))
            .offset(skip)
            .limit(limit)
            .order_by(Article.date.desc())
        )

        result = await db.execute(stmt)
        articles = result.scalars().unique().all()
        
        # Add relevance explanations
        for article in articles:
            if article.books:
                rel_stmt = select(article_books).where(
                    article_books.c.article_id == article.id
                )
                rel_result = await db.execute(rel_stmt)
                relevance_map = {
                    r.book_id: r.relevance_explanation 
                    for r in rel_result.fetchall()
                }
                
                for book in article.books:
                    book.relevance_explanation = relevance_map.get(book.id)

        has_more = total > skip + limit

        return articles, total, has_more

    async def get_featured(self, db: AsyncSession, limit: int = 5) -> List[Article]:
        """Get featured articles"""
        stmt = (
            select(Article)
            .where(Article.featured == True)
            .options(selectinload(Article.topics), selectinload(Article.books))
            .limit(limit)
            .order_by(Article.date.desc())
        )

        result = await db.execute(stmt)
        articles = result.scalars().unique().all()
        
        # Add relevance explanations
        for article in articles:
            if article.books:
                rel_stmt = select(article_books).where(
                    article_books.c.article_id == article.id
                )
                rel_result = await db.execute(rel_stmt)
                relevance_map = {
                    r.book_id: r.relevance_explanation 
                    for r in rel_result.fetchall()
                }
                
                for book in article.books:
                    book.relevance_explanation = relevance_map.get(book.id)

        return articles

    async def get_by_date_range(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> List[Article]:
        """Get articles within a date range"""
        stmt = (
            select(Article)
            .where(Article.date.between(start_date, end_date))
            .options(selectinload(Article.topics), selectinload(Article.books))
            .order_by(Article.date.desc())
        )

        result = await db.execute(stmt)
        articles = result.scalars().unique().all()
        
        # Add relevance explanations
        for article in articles:
            if article.books:
                rel_stmt = select(article_books).where(
                    article_books.c.article_id == article.id
                )
                rel_result = await db.execute(rel_stmt)
                relevance_map = {
                    r.book_id: r.relevance_explanation 
                    for r in rel_result.fetchall()
                }
                
                for book in article.books:
                    book.relevance_explanation = relevance_map.get(book.id)

        return articles


article_crud = CRUDArticle(Article)