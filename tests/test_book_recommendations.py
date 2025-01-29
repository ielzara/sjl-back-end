import pytest
from app.services.anthropic_service import AnthropicService, ArticleAnalysis
from app.services.google_books import GoogleBooksService
from app.core.config import settings

@pytest.mark.asyncio
async def test_book_recommendations():
    """Test the complete book recommendation flow"""
    
    # Print configuration for debugging
    print("\nAPI Configuration:")
    print(f"Google Books Base URL: {settings.GOOGLE_BOOKS_BASE_URL}")
    print(f"Google Books API Key set: {'Yes' if settings.GOOGLE_BOOKS_API_KEY else 'No'}")
    
    # Create test article analysis
    article_analysis = ArticleAnalysis(
        is_relevant=True,
        relevance_score=0.9,
        topics=[
            'environmental racism',
            'environmental justice',
            'public health disparities',
            'community activism'
        ],
        keywords=[
            'environmental racism',
            'industrial pollution',
        ],
        summary="""Article discusses environmental racism in Chicago, showing how industrial 
        development disproportionately affects low-income communities and communities of color, 
        leading to health disparities and community activism."""
    )
    
    # Get book recommendations
    books_service = GoogleBooksService()
    
    # Test individual topic searches for better results
    all_books = []
    for topic in article_analysis.topics:  # Using first two topics
        print(f"\nSearching for books about: {topic}")
        topic_books = await books_service.search_books_by_topics(
            topics=[topic],
            max_results=10
        )
        if topic_books:
            all_books.extend(topic_books)
            print(f"Found {len(topic_books)} books for topic '{topic}'")
        else:
            print(f"No books found for topic '{topic}'")
    
    if not all_books:
        print("\nNo books found! Please check:")
        print("1. Google Books API key is valid")
        print("2. Network connection is working")
        print("3. Search terms are not too restrictive")
        return
    
    print(f"\nFound {len(all_books)} total books:")
    for book in all_books:
        print(f"\nTitle: {book.title}")
        print(f"Author: {book.author}")
        print(f"ISBN: {book.isbn}")
        print(f"Description: {book.description[:200]}...")  # Truncate long descriptions
    
    # Analyze book relevance
    anthropic_service = AnthropicService()
    
    print("\nBook Relevance Analysis:")
    relevant_books = []
    for book in all_books:
        book_info = {
            "title": book.title,
            "author": book.author,
            "description": book.description
        }
        
        relevance = await anthropic_service.analyze_book_relevance(
            article_analysis=article_analysis,
            book_info=book_info
        )
        
        print(f"\nBook: {book.title}")
        print(f"Relevance Score: {relevance.relevance_score}")
        print(f"Explanation: {relevance.explanation}")
        
        # Store books with relevance for sorting
        relevant_books.append((book, relevance))
        
        # Basic assertions
        assert 0 <= relevance.relevance_score <= 1
        assert len(relevance.explanation) > 0
    
    # Sort and display final recommendations
    if relevant_books:
        print("\nFinal Recommendations (sorted by relevance):")
        sorted_books = sorted(relevant_books, key=lambda x: x[1].relevance_score, reverse=True)
        for book, relevance in sorted_books:
            print(f"\nTitle: {book.title}")
            print(f"Author: {book.author}")
            print(f"Relevance Score: {relevance.relevance_score}")
            print(f"Explanation: {relevance.explanation}")
    else:
        print("\nNo relevant books found!")