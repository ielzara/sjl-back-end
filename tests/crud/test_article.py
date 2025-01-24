import pytest
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.article import article_crud
from app.models.topic import Topic
from app.schemas.article import ArticleCreate

async def test_get_featured(db_session: AsyncSession):
    # Create some featured and non-featured articles
    featured_articles = []
    for i in range(3):
        article_data = {
            "title": f"Featured Article {i}",
            "content": f"Content {i}",
            "source": "Test Source",
            "url": f"http://test.com/featured{i}",
            "featured": True,
            "date": date(2024, 1, 23)
        }
        article = await article_crud.create(db_session, obj_in=ArticleCreate(**article_data))
        featured_articles.append(article)

    # Create non-featured article
    non_featured_data = {
        "title": "Non-Featured Article",
        "content": "Content",
        "source": "Test Source",
        "url": "http://test.com/non-featured",
        "featured": False,
        "date": date.today()
    }
    await article_crud.create(db_session, obj_in=ArticleCreate(**non_featured_data))

    # Test get_featured
    result = await article_crud.get_featured(db_session, limit=5)
    
    assert len(result) == 3
    assert all(article.featured for article in result)
    assert all(article.id in [a.id for a in featured_articles] for article in result)

async def test_get_by_date_range(db_session: AsyncSession):
    # Create articles with different dates
    base_date = date.today()
    
    for i in range(3):
        days_ago = 5 - (i * 2)  # Creates articles 5, 3, and 1 days ago
        article_date = base_date - timedelta(days=days_ago)
        
        article_data = {
            "title": f"Article {i}",
            "content": "Content",
            "source": "Test Source",
            "url": f"http://test.com/article{i}",
            "featured": False,
            "date": article_date
        }
        await article_crud.create(db_session, obj_in=ArticleCreate(**article_data))

    # Test date range query
    start_date = base_date - timedelta(days=4)
    end_date = base_date
    
    result = await article_crud.get_by_date_range(
        db_session,
        start_date=start_date,
        end_date=end_date
    )
    
    assert len(result) == 2
    assert all(start_date <= article.date <= end_date for article in result)

async def test_get_by_topic(db_session: AsyncSession, test_article):
    """Test get articles by topic functionality."""
    # Create a topic
    topic = Topic(name="Test Topic", description="Test Description")
    db_session.add(topic)
    await db_session.flush()
    
    # Associate article with topic
    print("before")
    await db_session.refresh(test_article)
    test_article.topics.append(topic)
    print("hrllo")
    await db_session.flush()
    
    # Commit changes to make them visible to next query
    await db_session.commit()
    
    # Now perform the search query
    articles, total, has_more = await article_crud.get_by_topic(
        db_session,
        topic_id=topic.id,
        skip=0,
        limit=10
    )
    
    assert len(articles) == 1
    assert articles[0].id == test_article.id
    assert total == 1
    assert not has_more

async def test_search(db_session: AsyncSession):
    # Create articles with specific content for searching
    articles_data = [
        {
            "title": "Python Programming",
            "content": "Article about Python",
            "source": "Test Source",
            "url": "http://test.com/python",
            "featured": False,
            "date": "2024-01-23T00:00:00"
        },
        {
            "title": "JavaScript Basics",
            "content": "Article about Python and JavaScript",
            "source": "Test Source",
            "url": "http://test.com/javascript",
            "featured": False,
            "date": "2024-01-23T00:00:00"
        }
    ]
    
    for data in articles_data:
        await article_crud.create(db_session, obj_in=ArticleCreate(**data))

    # Test search
    articles, total, has_more = await article_crud.search(
        db_session,
        keyword="Python",
        skip=0,
        limit=10
    )
    
    assert len(articles) == 2  # Both articles contain "Python"
    assert total == 2
    assert not has_more

    # Test search with no results
    articles, total, has_more = await article_crud.search(
        db_session,
        keyword="NonexistentKeyword",
        skip=0,
        limit=10
    )
    
    assert len(articles) == 0
    assert total == 0
    assert not has_more