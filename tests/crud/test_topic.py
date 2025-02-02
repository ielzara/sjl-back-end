import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.topic import topic_crud
from app.schemas.topic import TopicCreate

@pytest.mark.asyncio
class TestTopicCRUD:
    """Test topic-specific CRUD operations"""

    async def test_name_operations(self, db: AsyncSession):
        """Test name-related operations"""
        # Create test topic
        topic_data = {"name": "Test Topic", "description": "Test Description"}
        topic = await topic_crud.create(db, obj_in=TopicCreate(**topic_data))
        
        # Test exact match
        found = await topic_crud.get_by_name(db, name="Test Topic")
        assert found is not None
        assert found.id == topic.id
        
        # Test case-insensitive match
        found = await topic_crud.get_by_name(db, name="TEST TOPIC")
        assert found is not None
        assert found.id == topic.id
        
        # Test non-existent
        assert await topic_crud.get_by_name(db, name="NonExistent") is None

    async def test_uniqueness_constraint(self, db: AsyncSession):
        """Test topic name uniqueness"""
        topic_data = {"name": "Unique Topic", "description": "Test"}
        await topic_crud.create(db, obj_in=TopicCreate(**topic_data))
        
        # Try creating duplicate (case-insensitive)
        with pytest.raises(ValueError):
            await topic_crud.create(
                db, 
                obj_in=TopicCreate(name="UNIQUE TOPIC", description="Test")
            )

    async def test_get_with_counts(self, db: AsyncSession, test_article, test_book):
        """Test retrieving topics with association counts"""
        # Create topic and associate with article and book
        topic = await topic_crud.create(
            db, 
            obj_in=TopicCreate(name="Count Test", description="Test")
        )
        
        # Add associations
        test_article.topics.append(topic)
        test_book.topics.append(topic)
        await db.commit()
        
        # Test counts
        topics, total, has_more = await topic_crud.get_with_counts(
            db, skip=0, limit=10
        )
        
        topic_data = next(t for t in topics if t['id'] == topic.id)
        assert topic_data['article_count'] == 1
        assert topic_data['book_count'] == 1

    async def test_search(self, db: AsyncSession):
        """Test topic search functionality"""
        # Create test topics
        topics = [
            {"name": "Environmental Justice", "description": "Environment topics"},
            {"name": "Social Justice", "description": "Social topics"},
            {"name": "Environmental Policy", "description": "Policy topics"}
        ]
        
        for data in topics:
            await topic_crud.create(db, obj_in=TopicCreate(**data))
            
        # Test search in name
        results, total, _ = await topic_crud.search(
            db, keyword="Environmental", skip=0, limit=10
        )
        assert len(results) == 2
        
        # Test search in description
        results, total, _ = await topic_crud.search(
            db, keyword="Social", skip=0, limit=10
        )
        assert len(results) == 1