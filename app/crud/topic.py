from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from sqlalchemy.exc import IntegrityError
import logging

from app.crud.base import CRUDBase
from app.models.topic import Topic
from app.models.article import Article
from app.models.book import Book
from app.schemas.topic import TopicCreate, TopicUpdate

logger = logging.getLogger(__name__)

class CRUDTopic(CRUDBase[Topic, TopicCreate, TopicUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Topic]:
        """Get a single topic by name (case-insensitive)"""
        if not name:
            return None
            
        try:
            query = select(self.model).filter(func.lower(self.model.name) == func.lower(name))
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting topic by name '{name}': {str(e)}")
            raise

    async def create(self, db: AsyncSession, *, obj_in: TopicCreate) -> Topic:
        """Create a new topic with case-insensitive name uniqueness check"""
        try:
            # Check for existing topic with same name (case insensitive)
            existing_topic = await self.get_by_name(db, name=obj_in.name)
            if existing_topic:
                raise ValueError(f"Topic with name '{obj_in.name}' already exists")

            # Create the topic
            return await super().create(db, obj_in=obj_in)
        except IntegrityError as e:
            logger.error(f"Database integrity error creating topic: {str(e)}")
            await db.rollback()
            raise ValueError("Unable to create topic due to database constraint")
        except Exception as e:
            logger.error(f"Error creating topic: {str(e)}")
            await db.rollback()
            raise

    async def update(self, db: AsyncSession, *, db_obj: Topic, obj_in: TopicUpdate) -> Topic:
        """Update topic with name uniqueness validation"""
        try:
            if obj_in.name:
                # Check for existing topic with same name (case insensitive)
                existing = await self.get_by_name(db, name=obj_in.name)
                if existing and existing.id != db_obj.id:
                    raise ValueError(f"Topic with name '{obj_in.name}' already exists")

            return await super().update(db, db_obj=db_obj, obj_in=obj_in)
        except Exception as e:
            logger.error(f"Error updating topic {db_obj.id}: {str(e)}")
            await db.rollback()
            raise

    async def get_with_counts(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[dict], int, bool]:
        """Get topics with counts of associated articles and books"""
        try:
            # Count query for pagination
            count_query = select(func.count()).select_from(self.model)
            total = await db.scalar(count_query)

            # Main query with counts
            query = (
                select(
                    self.model,
                    func.count(distinct(Article.id)).label('article_count'),
                    func.count(distinct(Book.id)).label('book_count')
                )
                .outerjoin(self.model.articles)
                .outerjoin(self.model.books)
                .group_by(self.model.id)
                .offset(skip)
                .limit(limit + 1) 
            )

            result = await db.execute(query)
            items = result.all()
            
            # Check if there are more items
            has_more = len(items) > limit
            items = items[:limit]
            
            # Convert to dictionary format with error handling for null values
            topics_with_counts = []
            for row in items:
                topic_dict = row[0].__dict__.copy()
                # Remove SQLAlchemy internal state
                topic_dict.pop('_sa_instance_state', None)
                # Add counts with null handling
                topic_dict.update({
                    'article_count': row[1] or 0,
                    'book_count': row[2] or 0
                })
                topics_with_counts.append(topic_dict)
            
            return topics_with_counts, total, has_more

        except Exception as e:
            logger.error(f"Error getting topics with counts: {str(e)}")
            raise ValueError("Unable to get topics with counts")

    # Using base search with topic-specific fields
    async def search(
        self, 
        db: AsyncSession, 
        *, 
        keyword: str, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Topic], int, bool]:
        """Search topics in name and description"""
        return await super().search(
            db,
            keyword=keyword,
            fields=['name', 'description'],
            skip=skip,
            limit=limit
        )

# Create CRUDTopic instance
topic_crud = CRUDTopic(Topic)