import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.book import book_crud
from app.models.topic import Topic
from app.schemas.book import BookCreate

async def test_get_by_isbn(db_session: AsyncSession, test_book):
    # Test get_by_isbn with existing book
    book = await book_crud.get_by_isbn(db_session, isbn=test_book.isbn)
    assert book is not None
    assert book.id == test_book.id
    assert book.isbn == test_book.isbn

    # Test get_by_isbn with non-existent ISBN
    book = await book_crud.get_by_isbn(db_session, isbn="9999999999999")
    assert book is None

async def test_get_by_author(db_session: AsyncSession):
    # Create books by different authors
    books_data = [
        {
            "title": "Book 1",
            "author": "John Smith",
            "description": "Description 1",
            "url": "http://test.com/book1",
            "cover_url": "http://test.com/cover1",
            "isbn": "1111111111111"
        },
        {
            "title": "Book 2",
            "author": "John Smith",
            "description": "Description 2",
            "url": "http://test.com/book2",
            "cover_url": "http://test.com/cover2",
            "isbn": "2222222222222"
        },
        {
            "title": "Book 3",
            "author": "Jane Doe",
            "description": "Description 3",
            "url": "http://test.com/book3",
            "cover_url": "http://test.com/cover3",
            "isbn": "3333333333333"
        }
    ]
    
    for data in books_data:
        await book_crud.create(db_session, obj_in=BookCreate(**data))

    # Test get_by_author
    books, total, has_more = await book_crud.get_by_author(
        db_session,
        author="John Smith",
        skip=0,
        limit=10
    )
    
    assert len(books) == 2
    assert all(book.author == "John Smith" for book in books)
    assert total == 2
    assert not has_more

    # Test partial name match
    books, total, has_more = await book_crud.get_by_author(
        db_session,
        author="John",
        skip=0,
        limit=10
    )
    
    assert len(books) == 2
    assert total == 2
    assert not has_more

async def test_get_by_topic(db_session: AsyncSession, test_book):
    # Create a topic and associate it with the test book
    topic = Topic(name="Test Topic", description="Test Description")
    db_session.add(topic)
    await db_session.commit()
    await db_session.refresh(topic)
    
    test_book.topics.append(topic)
    await db_session.commit()

    # Test get_by_topic
    books, total, has_more = await book_crud.get_by_topic(
        db_session,
        topic_id=topic.id,
        skip=0,
        limit=10
    )
    
    assert len(books) == 1
    assert books[0].id == test_book.id
    assert total == 1
    assert not has_more

async def test_search(db_session: AsyncSession):
    # Create books with specific content for searching
    books_data = [
        {
            "title": "Python Programming",
            "author": "Author 1",
            "description": "Guide about Python",
            "url": "http://test.com/python-book",
            "cover_url": "http://test.com/python-cover",
            "isbn": "1111111111111"
        },
        {
            "title": "JavaScript Basics",
            "author": "Author 2",
            "description": "Guide about Python and JavaScript",
            "url": "http://test.com/js-book",
            "cover_url": "http://test.com/js-cover",
            "isbn": "2222222222222"
        }
    ]
    
    for data in books_data:
        await book_crud.create(db_session, obj_in=BookCreate(**data))

    # Test search in title and description
    books, total, has_more = await book_crud.search(
        db_session,
        keyword="Python",
        skip=0,
        limit=10
    )
    
    assert len(books) == 2  # Both books contain "Python"
    assert total == 2
    assert not has_more

    # Test search with title match only
    books, total, has_more = await book_crud.search(
        db_session,
        keyword="JavaScript Basics",
        skip=0,
        limit=10
    )
    
    assert len(books) == 1
    assert books[0].title == "JavaScript Basics"
    assert total == 1
    assert not has_more

    # Test search with no results
    books, total, has_more = await book_crud.search(
        db_session,
        keyword="NonexistentKeyword",
        skip=0,
        limit=10
    )
    
    assert len(books) == 0
    assert total == 0
    assert not has_more