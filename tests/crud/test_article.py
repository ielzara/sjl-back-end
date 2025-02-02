import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.article import article_crud
from app.models.topic import Topic
from app.schemas.article import ArticleCreate

@pytest.mark.asyncio
class TestArticleCRUD:
    """Test article-specific CRUD operations"""
    
    async def test_article_management(self, db: AsyncSession, test_article):
        """Test basic article operations"""
        # Test URL lookup
        article = await article_crud.get_by_url(db, url=test_article.url)
        assert article is not None
        assert article.id == test_article.id

        # Test duplicate URL prevention
        with pytest.raises(Exception):
            await article_crud.create(
                db, 
                obj_in=ArticleCreate(
                    title="Duplicate",
                    content="Test",
                    source="Test",
                    url=test_article.url,
                    featured=False,
                    date=date.today()
                )
            )

    async def test_topic_management(self, db: AsyncSession, test_article):
        """Test topic-related operations"""
        topic = Topic(name="Test Topic", description="Test Description")
        db.add(topic)
        await db.flush()
        
        # Test adding topic
        await article_crud.add_topic(db, test_article.id, topic.id)
        await db.refresh(test_article)
        
        assert len(test_article.topics) == 1
        assert test_article.topics[0].name == "Test Topic"

    async def test_book_operations(self, db: AsyncSession, test_article, test_book):
        """Test book-related operations"""
        # Test adding book
        await article_crud.add_book(
            db,
            article_id=test_article.id,
            book_id=test_book.id,
            relevance_explanation="Test relevance"
        )
        
        # Verify book was added
        has_book = await article_crud.has_book(db, test_article.id, test_book.id)
        assert has_book is True

    async def test_search(self, db: AsyncSession):
        """Test base search functionality"""
        # Create test articles
        articles_data = [
            {
                "title": "Python Programming",
                "content": "Article about Python",
                "source": "Test Source",
                "url": "http://test.com/python",
                "featured": False,
                "date": date.today()
            },
            {
                "title": "JavaScript Basics",
                "content": "Article about Python and JavaScript",
                "source": "Test Source",
                "url": "http://test.com/javascript",
                "featured": False,
                "date": date.today()
            }
        ]
        
        for data in articles_data:
            await article_crud.create(db, obj_in=ArticleCreate(**data))

        # Test search using base CRUD search
        results, total, has_more = await article_crud.search(
            db,
            keyword="Python",
            fields=['title', 'content'],
            skip=0,
            limit=10
        )
        
        assert len(results) == 2  # Both articles contain "Python"
        assert total == 2
        assert not has_more

    async def test_get_base_multi_paginated(self, db: AsyncSession):
        """Test pagination using base CRUD method"""
        # Create multiple articles
        for i in range(15):
            await article_crud.create(
                db,
                obj_in=ArticleCreate(
                    title=f"Article {i}",
                    content="Test content",
                    source="Test Source",
                    url=f"http://test.com/article{i}",
                    featured=False,
                    date=date.today()
                )
            )

        # Test first page
        articles, total, has_more = await article_crud.get_multi_paginated(
            db,
            skip=0,
            limit=10
        )
        assert len(articles) == 10
        assert total == 15
        assert has_more

        # Test last page
        articles, total, has_more = await article_crud.get_multi_paginated(
            db,
            skip=10,
            limit=10
        )
        assert len(articles) == 5
        assert total == 15
        assert not has_more