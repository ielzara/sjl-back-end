"""
Content Processor Service

This module handles the core content processing workflow for the Social Justice Library.
It coordinates between different services to:
1. Fetch new articles from Guardian News
2. Analyze articles for social justice relevance
3. Extract topics and keywords
4. Find and analyze relevant books
5. Store everything in the database with proper relationships

The processing follows these steps:
1. Get recent articles (last 24 hours)
2. For each article:
   - Check if it's already processed
   - Analyze for social justice relevance
   - Extract and create topics
   - Generate book search keywords
   - Find relevant books
   - Create relationships between articles, books, and topics
"""

from datetime import datetime, timedelta, UTC
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.guardian_news import GuardianNewsService
from app.services.anthropic_service import AnthropicService
from app.services.google_books import GoogleBooksService
from app.crud.article import article_crud
from app.crud.book import book_crud
from app.crud.topic import topic_crud
from app.schemas.topic import TopicCreate
from app.schemas.book import BookCreate

logger = logging.getLogger(__name__)

class ContentProcessor:
    """
    Main service for processing news articles and finding relevant books.
    
    This service orchestrates the entire content processing workflow:
    - Fetches new articles from Guardian News API
    - Uses Claude AI to analyze articles for social justice relevance
    - Extracts topics and generates book search keywords
    - Searches for relevant books using Google Books API
    - Creates and maintains relationships between content in the database
    
    Attributes:
        db (AsyncSession): Database session for storing processed content
        guardian_service (GuardianNewsService): Service for fetching news articles
        anthropic_service (AnthropicService): Service for AI analysis
        books_service (GoogleBooksService): Service for finding books
    """

    def __init__(
        self,
        db: AsyncSession,
        guardian_service: GuardianNewsService,
        anthropic_service: AnthropicService,
        books_service: GoogleBooksService
    ):
        self.db = db
        self.guardian_service = guardian_service
        self.anthropic_service = anthropic_service
        self.books_service = books_service

    async def process_new_content(self) -> None:
        """
        Main function to process new articles and find related books.
        
        This function:
        1. Fetches yesterday's articles from Guardian News
        2. For each new article:
           - Analyzes it for social justice relevance
           - Creates topics based on analysis
           - Finds relevant books
           - Creates database relationships
        
        The function uses a minimum relevance score of 0.8 for both
        articles and books to ensure high-quality connections.
        
        Error Handling:
        - Skips articles that already exist in database
        - Skips articles with low relevance scores
        - Continues processing if one article fails
        - Logs all major steps and errors
        
        Database Operations:
        - Creates new articles, books, and topics
        - Creates relationships between them
        - Stores relevance explanations
        """
        # Get yesterday's articles
        from_date = datetime.now(UTC) - timedelta(days=1)
        articles, _ = await self.guardian_service.get_recent_social_justice_articles(from_date=from_date)
        logger.info(f"Found {len(articles)} articles")

        for article in articles:
            try:
                # Skip if already exists
                existing_article = await article_crud.get_by_url(self.db, url=str(article.url))
                if existing_article:
                    logger.info(f"Article already exists: {article.title}")
                    continue

                # Analyze article
                logger.info(f"Analyzing article: {article.title}")
                analysis = await self.anthropic_service.analyze_article(
                    article_text=article.content,
                    article_title=article.title
                )

                if analysis.relevance_score < 0.8:
                    logger.info(f"Article not relevant enough, skipping: {article.title}")
                    continue

                # Create article
                db_article = await article_crud.create(self.db, obj_in=article)
                logger.info(f"Created article: {db_article.title}")

                # Process topics
                for topic_name in analysis.topics:
                    topic = await topic_crud.get_by_name(self.db, name=topic_name)
                    if not topic:
                        topic = await topic_crud.create(self.db, obj_in=TopicCreate(name=topic_name))
                    await article_crud.add_topic(self.db, db_article.id, topic.id)
                    logger.info(f"Added topic to article: {topic_name}")

                # Get book recommendations
                search_terms = await self.anthropic_service.generate_book_keywords(analysis)
                if isinstance(search_terms, dict) and 'search_terms' in search_terms:
                    search_terms = search_terms['search_terms'][:5]

                # Collect all potential books first
                all_books = []
                for term in search_terms:
                    enhanced_term = f'"{term}" social justice'
                    books = await self.books_service.search_books(enhanced_term)
                    all_books.extend(books)

                # Batch analyze all books for relevance
                relevant_books = await self.anthropic_service.batch_analyze_book_relevance(
                    article_analysis=analysis,
                    books=[book.model_dump() for book in all_books],
                    min_relevance_score=0.8
                )

                # Process only the already filtered relevant books (max 5 from anthropic service)
                for book_info, relevance in relevant_books:
                    book = BookCreate(**book_info)
                    # Get or create book
                    db_book = await book_crud.get_by_isbn(self.db, isbn=book.isbn)
                    if not db_book:
                        db_book = await book_crud.create(self.db, obj_in=book)
                        logger.info(f"Created book: {db_book.title}")

                        # Add book topics
                        for topic in db_article.topics:
                            await book_crud.add_topic(self.db, db_book.id, topic.id)

                    # Link book to article with explanation
                    if not await article_crud.has_book(self.db, db_article.id, db_book.id):
                        await article_crud.add_book(
                            self.db,
                            article_id=db_article.id,
                            book_id=db_book.id,
                            relevance_explanation=relevance.explanation
                        )
                        logger.info(f"Linked book to article: {db_book.title} ({relevance.relevance_score})")

            except Exception as e:
                logger.error(f"Error processing article {article.title}: {str(e)}")
                continue