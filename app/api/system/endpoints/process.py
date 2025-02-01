from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.services.content_processor import ContentProcessor
from app.services.guardian_news import GuardianNewsService
from app.services.anthropic_service import AnthropicService
from app.services.google_books import GoogleBooksService
from app.crud.article import article_crud
from app.crud.topic import topic_crud
from app.crud.book import book_crud

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process")
async def trigger_content_processing(db: AsyncSession = Depends(get_db)):
    """Trigger content processing pipeline manually"""
    try:
        logger.info("Starting content processing...")
        
        # Create services
        processor = ContentProcessor(
            db=db,
            guardian_service=GuardianNewsService(),
            anthropic_service=AnthropicService(),
            books_service=GoogleBooksService()
        )
        
        # Get counts before processing
        before_articles, total_before, _ = await article_crud.get_multi_paginated(db, skip=0, limit=100)
        logger.info(f"Articles before processing: {total_before}")
        
        # Process content
        await processor.process_new_content()
        
        # Get counts after processing
        after_articles, total_after, _ = await article_crud.get_multi_paginated(db, skip=0, limit=100)
        topics, total_topics, _ = await topic_crud.get_multi_paginated(db, skip=0, limit=100)
        books, total_books, _ = await book_crud.get_multi_paginated(db, skip=0, limit=100)
        
        # Log results
        logger.info(f"Articles after processing: {total_after}")
        logger.info(f"Total topics: {total_topics}")
        logger.info(f"Topics: {[t.name for t in topics]}")
        logger.info(f"Total books: {total_books}")
        logger.info(f"Books: {[b.title for b in books]}")
        
        return {
            "status": "success",
            "message": "Content processing completed",
            "stats": {
                "articles_before": total_before,
                "articles_after": total_after,
                "total_topics": total_topics,
                "total_books": total_books
            }
        }

    except Exception as e:
        logger.error(f"Error in content processing: {str(e)}", exc_info=True)
        await db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }