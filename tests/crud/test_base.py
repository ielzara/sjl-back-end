import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.crud.base import CRUDBase
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate

crud_base = CRUDBase[Article, ArticleCreate, ArticleUpdate](Article)

@pytest.mark.asyncio
class TestBaseCRUD:
    """Test base CRUD operations using Article model"""
    
    async def test_basic_operations(self, db: AsyncSession, article_data: dict):
        """Test create, read, update, delete operations"""
        # Create
        article = await crud_base.create(db, obj_in=ArticleCreate(**article_data))
        assert article.id is not None
        
        # Read
        db_article = await crud_base.get(db, article.id)
        assert db_article.title == article_data["title"]
        
        # Update
        updated = await crud_base.update(
            db, 
            db_obj=article, 
            obj_in={"title": "Updated Title"}
        )
        assert updated.title == "Updated Title"
        
        # Delete
        await crud_base.remove(db, id=article.id)
        assert await crud_base.get(db, article.id) is None

    async def test_pagination(self, db: AsyncSession):
        """Test pagination with multiple records"""
        # Clear existing data
        await db.execute(text("TRUNCATE TABLE articles RESTART IDENTITY CASCADE"))
        await db.commit()

        # Create test articles
        for i in range(12):  # Create 12 articles for pagination testing
            await crud_base.create(
                db, 
                obj_in=ArticleCreate(
                    title=f"Article {i}",
                    content="Test content",
                    source="Test",
                    url=f"http://test.com/{i}",
                    featured=False,
                    date=date.today()
                )
            )

        # Test pagination parameters
        test_cases = [
            {"skip": 0, "limit": 5, "expected_count": 5, "expected_has_more": True},
            {"skip": 10, "limit": 5, "expected_count": 2, "expected_has_more": False}
        ]
        
        for case in test_cases:
            articles, total, has_more = await crud_base.get_multi_paginated(
                db, 
                skip=case["skip"], 
                limit=case["limit"]
            )
            assert len(articles) == case["expected_count"]
            assert total == 12
            assert has_more == case["expected_has_more"]