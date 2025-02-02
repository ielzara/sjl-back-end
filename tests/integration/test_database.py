import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.article import article_crud
from app.schemas.article import ArticleCreate

@pytest.mark.asyncio
async def test_article_crud(test_session: AsyncSession):
    """Test article creation and retrieval"""
    # Create test article data
    article_data = ArticleCreate(
        title="Test Article",
        content="Test content",
        source="Test Source",
        url="http://test.com/article1",
        featured=False,
        date=date.today()
    )
    
    # Create article and immediately verify retrieval
    await article_crud.create(test_session, obj_in=article_data)
    
    # Verify we can retrieve the article by URL
    db_article = await article_crud.get_by_url(test_session, url="http://test.com/article1")
    assert db_article is not None
    assert db_article.title == "Test Article"