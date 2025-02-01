import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.article import article_crud
from app.crud.topic import topic_crud
from app.crud.book import book_crud
from app.schemas.article import ArticleCreate
from app.schemas.topic import TopicCreate

@pytest.mark.asyncio
async def test_article_operations(test_session: AsyncSession):
    """Test article CRUD operations"""
    # Create article
    article_data = ArticleCreate(
        title="Test Article",
        content="Test content",
        source="Test Source",
        url="http://test.com/article1",
        featured=False,
        date=date.today()
    )
    
    # Test create
    article = await article_crud.create(test_session, obj_in=article_data)
    assert article.id is not None
    assert article.title == "Test Article"
    
    # Test get by URL
    article_by_url = await article_crud.get_by_url(test_session, url="http://test.com/article1")
    assert article_by_url is not None
    assert article_by_url.id == article.id

@pytest.mark.asyncio
async def test_topic_relationship(test_session: AsyncSession):
    """Test article and topic relationship"""
    # Create article with unique URL
    article = await article_crud.create(
        test_session,
        obj_in=ArticleCreate(
            title="Test Article with Topic",
            content="Test content",
            source="Test Source",
            url="http://test.com/article-with-topic",
            featured=False,
            date=date.today()
        )
    )
    
    # Create topic with unique name
    topic = await topic_crud.create(
        test_session,
        obj_in=TopicCreate(
            name="Environmental Justice Topic",
            description="Test Description"
        )
    )
    
    # Link article to topic
    await article_crud.add_topic(test_session, article.id, topic.id)
    
    # Verify relationship
    articles, total, has_more = await article_crud.get_by_topic(
        test_session, 
        topic_id=topic.id
    )
    assert total == 1
    assert articles[0].id == article.id