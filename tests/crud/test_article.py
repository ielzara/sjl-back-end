import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.crud.article import article_crud
from app.models.topic import Topic
from app.models.associations import article_books, article_topics
from app.schemas.article import ArticleCreate
from app.models.article import Article
import logging

logger = logging.getLogger(__name__)

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
        try:
            # Create and add topic
            topic = Topic(name="Test Topic", description="Test Description")
            db.add(topic)
            await db.commit()
            
            # Log topic creation
            logger.info(f"Created topic with ID: {topic.id}")
            
            # Add topic to article
            await article_crud.add_topic(db, test_article.id, topic.id)
            
            # Verify the association exists in the database
            assoc_stmt = select(article_topics).where(
                (article_topics.c.article_id == test_article.id) &
                (article_topics.c.topic_id == topic.id)
            )
            assoc_result = await db.execute(assoc_stmt)
            assoc = assoc_result.first()
            assert assoc is not None, "Topic association not found in database"
            
            # Fetch article with topics
            stmt = select(Article).options(
                selectinload(Article.topics)
            ).where(Article.id == test_article.id)
            
            result = await db.execute(stmt)
            article = result.unique().scalar_one()
            
            # Log debug information
            logger.info(f"Article ID: {article.id}")
            logger.info(f"Topics count: {len(article.topics)}")
            if article.topics:
                logger.info(f"First topic: {article.topics[0].name}")
            
            assert len(article.topics) == 1, f"Expected 1 topic, found {len(article.topics)}"
            assert article.topics[0].name == "Test Topic"
            
        except Exception as e:
            logger.error(f"Error in test_topic_management: {str(e)}", exc_info=True)
            raise

    async def test_book_operations(self, db: AsyncSession, test_article, test_book):
        """Test book-related operations"""
        try:
            # Add book to article
            await article_crud.add_book(
                db,
                article_id=test_article.id,
                book_id=test_book.id,
                relevance_explanation="Test relevance"
            )
            
            # Verify book was added
            has_book = await article_crud.has_book(db, test_article.id, test_book.id)
            assert has_book is True
            
            # Verify relevance explanation
            rel_stmt = select(article_books.c.relevance_explanation).where(
                (article_books.c.article_id == test_article.id) &
                (article_books.c.book_id == test_book.id)
            )
            rel_result = await db.execute(rel_stmt)
            relevance = rel_result.scalar_one()
            assert relevance == "Test relevance"
            
        except Exception as e:
            logger.error(f"Error in test_book_operations: {str(e)}", exc_info=True)
            raise

    async def test_search(self, db: AsyncSession):
        """Test article search functionality"""
        try:
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

            # Test search using simple keyword search
            results, total, has_more = await article_crud.search(
                db,
                keyword="Python",
                skip=0,
                limit=10
            )
            
            assert len(results) == 2  # Both articles contain "Python"
            assert total == 2
            assert not has_more
            
        except Exception as e:
            logger.error(f"Error in test_search: {str(e)}", exc_info=True)
            raise

    async def test_get_base_multi_paginated(self, db: AsyncSession):
        """Test pagination using base CRUD method"""
        try:
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
            
        except Exception as e:
            logger.error(f"Error in test_get_base_multi_paginated: {str(e)}", exc_info=True)
            raise

    async def test_article_with_books_and_topics(self, db: AsyncSession, test_article, test_book):
        """Test full article relationships with books and topics"""
        try:
            # Create and add topic
            topic = Topic(name="Test Topic", description="Test Description")
            db.add(topic)
            await db.commit()
            logger.info(f"Created topic with ID: {topic.id}")
            
            # Add topic to article
            await article_crud.add_topic(db, test_article.id, topic.id)
            logger.info("Added topic to article")
            
            # Add book with relevance explanation
            await article_crud.add_book(
                db,
                article_id=test_article.id,
                book_id=test_book.id,
                relevance_explanation="Test relevance explanation"
            )
            logger.info("Added book to article")
            
            # Fetch the updated article with all relationships
            stmt = (
                select(Article)
                .options(
                    selectinload(Article.topics),
                    selectinload(Article.books)
                )
                .where(Article.id == test_article.id)
            )
            result = await db.execute(stmt)
            article = result.scalar_one()
            
            # Log debug information
            logger.info(f"Article ID: {article.id}")
            logger.info(f"Topics count: {len(article.topics)}")
            logger.info(f"Books count: {len(article.books)}")

            # Verify relationships
            assert len(article.topics) == 1, f"Expected 1 topic, found {len(article.topics)}"
            assert article.topics[0].name == "Test Topic"
            assert len(article.books) == 1
            assert article.books[0].id == test_book.id
            
            # Verify relevance explanation
            rel_stmt = select(article_books.c.relevance_explanation).where(
                (article_books.c.article_id == test_article.id) &
                (article_books.c.book_id == test_book.id)
            )
            rel_result = await db.execute(rel_stmt)
            relevance = rel_result.scalar_one()
            assert relevance == "Test relevance explanation"
            
        except Exception as e:
            logger.error(f"Error in test_article_with_books_and_topics: {str(e)}", exc_info=True)
            raise