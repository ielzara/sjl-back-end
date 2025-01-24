from sqlalchemy import text

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from app.crud.base import CRUDBase
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate

# Using Article model and schemas for testing base CRUD
crud_base = CRUDBase[Article, ArticleCreate, ArticleUpdate](Article)

async def test_create(db_session: AsyncSession, sample_article_data: dict):
    article_in = ArticleCreate(**sample_article_data)
    article = await crud_base.create(db_session, obj_in=article_in)
    
    assert article.title == sample_article_data["title"]
    assert article.content == sample_article_data["content"]
    assert article.id is not None

async def test_get(db_session: AsyncSession, test_article):
    article = await crud_base.get(db_session, test_article.id)
    
    assert article is not None
    assert article.id == test_article.id
    assert article.title == test_article.title

async def test_get_non_existent(db_session: AsyncSession):
    non_existent_id = 99999
    article = await crud_base.get(db_session, non_existent_id)
    
    assert article is None

async def test_get_multi_paginated(db_session: AsyncSession, test_article):
    articles, total, has_more = await crud_base.get_multi_paginated(
        db_session, skip=0, limit=10
    )
    
    assert isinstance(articles, list)
    assert total >= 1
    assert isinstance(has_more, bool)
    assert any(a.id == test_article.id for a in articles)

async def test_update(db_session: AsyncSession, test_article):
    update_data = {"title": "Updated Title"}
    updated_article = await crud_base.update(
        db_session, db_obj=test_article, obj_in=update_data
    )
    
    assert updated_article.id == test_article.id
    assert updated_article.title == "Updated Title"
    assert updated_article.content == test_article.content

async def test_delete(db_session: AsyncSession, test_article):
    article = await crud_base.remove(db_session, id=test_article.id)
    assert article.id == test_article.id
    
    deleted_article = await crud_base.get(db_session, test_article.id)
    assert deleted_article is None

@pytest.mark.parametrize(
    "skip,limit,expected_count",
    [
        (0, 5, 5),    # First page
        (5, 5, 5),    # Second page
        (0, 15, 10),  # More than total
    ]
)
async def test_pagination(db_session: AsyncSession, skip, limit, expected_count):
    # Clean up any existing data
    await db_session.execute(text("TRUNCATE TABLE articles RESTART IDENTITY CASCADE"))
    await db_session.commit()
    
    # Create 10 test articles
    for i in range(10):
        article_data = {
            "title": f"Test Article {i}",
            "content": f"Content {i}",
            "source": "Test Source",
            "url": f"http://test.com/article{i}",
            "featured": False,
            "date": date.today()
        }
        article_in = ArticleCreate(**article_data)
        await crud_base.create(db_session, obj_in=article_in)
    
    # Test pagination
    articles, total, has_more = await crud_base.get_multi_paginated(
        db_session, skip=skip, limit=limit
    )
    
    assert len(articles) <= expected_count
    assert total == 10
    assert has_more == (total > skip + limit)