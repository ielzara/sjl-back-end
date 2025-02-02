import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.book import book_crud
from app.schemas.book import BookCreate
from app.models.topic import Topic

@pytest.mark.asyncio
class TestBookCRUD:
    """Test book-specific CRUD operations"""

    async def test_isbn_operations(self, db: AsyncSession):
        """Test ISBN-related operations"""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "description": "Test Description",
            "url": "http://test.com/book",
            "cover_url": "http://test.com/cover.jpg",
            "isbn": "9781234567890"
        }
        
        # Create and verify
        book = await book_crud.create(db, obj_in=BookCreate(**book_data))
        found = await book_crud.get_by_isbn(db, isbn=book_data["isbn"])
        assert found is not None
        assert found.id == book.id
        
        # Test non-existent ISBN
        assert await book_crud.get_by_isbn(db, isbn="9999999999999") is None

    async def test_topic_associations(self, db: AsyncSession, test_book):
        """Test book-topic associations"""
        # Create and associate topic
        topic = Topic(name="Test Topic", description="Test Description")
        db.add(topic)
        await db.flush()
        
        test_book.topics.append(topic)
        await db.commit()
        
        # Test get_by_topic
        books, total, has_more = await book_crud.get_by_topic(
            db, topic_id=topic.id, skip=0, limit=10
        )
        
        assert len(books) == 1
        assert books[0].id == test_book.id
        assert total == 1

    async def test_author_search(self, db: AsyncSession):
        """Test author search functionality"""
        # Create test books
        books_data = [
            {"author": "John Smith", "title": "Book 1"},
            {"author": "John Smith", "title": "Book 2"},
            {"author": "Jane Doe", "title": "Book 3"}
        ]
        
        for i, data in enumerate(books_data):
            await book_crud.create(
                db,
                obj_in=BookCreate(
                    **data,
                    description="Test description",
                    url=f"http://test.com/book{i}",
                    cover_url=f"http://test.com/cover{i}",
                    isbn=f"978123456789{i}"
                )
            )
            
        # Test exact author match
        books, total, _ = await book_crud.get_by_author(
            db, author="John Smith", skip=0, limit=10
        )
        assert len(books) == 2
        
        # Test partial author match
        books, total, _ = await book_crud.get_by_author(
            db, author="John", skip=0, limit=10
        )
        assert len(books) == 2