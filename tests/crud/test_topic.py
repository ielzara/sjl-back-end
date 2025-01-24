import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.crud.topic import topic_crud
from app.models.topic import Topic
from app.schemas.topic import TopicCreate

async def test_get_by_name(db_session: AsyncSession, test_topic):
    """Test get_by_name functionality."""
    topic = await topic_crud.get_by_name(db_session, name=test_topic.name)
    
    assert topic is not None
    assert topic.name == test_topic.name
    assert topic.description == test_topic.description

async def test_get_by_name_case_insensitive(db_session: AsyncSession, test_topic):
    """Test get_by_name with case-insensitive search."""
    topic = await topic_crud.get_by_name(db_session, name=test_topic.name.upper())
    
    assert topic is not None
    assert topic.name == test_topic.name

async def test_get_by_name_not_found(db_session: AsyncSession):
    """Test get_by_name with non-existent name."""
    topic = await topic_crud.get_by_name(db_session, name="NonExistentTopic")
    
    assert topic is None

async def test_get_with_counts(db_session: AsyncSession, test_topic, test_article, test_book):
    """Test get_with_counts functionality."""
    # Associate the test article and book with the test topic
    test_topic.articles.append(test_article)
    test_topic.books.append(test_book)
    await db_session.flush()
    await db_session.refresh(test_topic)
    await db_session.commit()

    topics_with_counts, total, has_more = await topic_crud.get_with_counts(
        db_session,
        skip=0,
        limit=10
    )
    
    assert len(topics_with_counts) >= 1
    topic_data = next(t for t in topics_with_counts if t['id'] == test_topic.id)
    assert topic_data['article_count'] == 1
    assert topic_data['book_count'] == 1
    assert total >= 1
    assert isinstance(has_more, bool)

async def test_search_by_name(db_session: AsyncSession):
    """Test search functionality with name."""
    # Create test topics
    topics_data = [
        {"name": "Environmental Justice", "description": "Topics about environment"},
        {"name": "Social Equality", "description": "Topics about equality"},
        {"name": "Environmental Policy", "description": "Policy topics"}
    ]
    
    for data in topics_data:
        topic_in = TopicCreate(**data)
        await topic_crud.create(db_session, obj_in=topic_in)

    # Search for topics
    topics, total, has_more = await topic_crud.search(
        db_session,
        keyword="Environmental",
        skip=0,
        limit=10
    )
    
    assert len(topics) == 2
    assert all("Environmental" in topic.name for topic in topics)
    assert total == 2
    assert not has_more

async def test_search_by_description(db_session: AsyncSession):
    """Test search functionality with description."""
    # Create a topic with specific description
    topic_data = {
        "name": "Test Topic",
        "description": "A unique description for testing"
    }
    topic_in = TopicCreate(**topic_data)
    await topic_crud.create(db_session, obj_in=topic_in)

    # Search by description
    topics, total, has_more = await topic_crud.search(
        db_session,
        keyword="unique description",
        skip=0,
        limit=10
    )
    
    assert len(topics) == 1
    assert topics[0].description == topic_data["description"]
    assert total == 1
    assert not has_more

async def test_pagination_with_counts(db_session: AsyncSession):
    """Test pagination in get_with_counts."""
    # Create multiple topics
    for i in range(15):
        topic_data = {
            "name": f"Topic {i}",
            "description": f"Description {i}"
        }
        topic_in = TopicCreate(**topic_data)
        await topic_crud.create(db_session, obj_in=topic_in)

    # Test first page
    first_page, total, has_more = await topic_crud.get_with_counts(
        db_session,
        skip=0,
        limit=10
    )
    assert len(first_page) == 10
    assert total == 15
    assert has_more

    # Test second page
    second_page, total, has_more = await topic_crud.get_with_counts(
        db_session,
        skip=10,
        limit=10
    )
    assert len(second_page) == 5
    assert total == 15
    assert not has_more