import pytest
from app.services.anthropic_service import AnthropicService, ArticleAnalysis, BookRelevance
from unittest.mock import patch, AsyncMock

@pytest.fixture
def article_analysis():
    return ArticleAnalysis(
        is_relevant=True,
        relevance_score=0.95,
        topics=['racial justice', 'educational equity', 'systemic racism'],
        keywords=['educational disparities', 'racial equity', 'school reform', 'social justice'],
        summary='Detailed analysis of systemic racism in education and its impacts on student outcomes'
    )

@pytest.fixture
def test_books():
    return [
        {
            "title": "Educational Justice in America",
            "author": "Dr. Jane Smith",
            "description": "A comprehensive examination of racial inequities in the American education system, analyzing systemic barriers and proposing evidence-based solutions for reform.",
            "isbn": "9781234567890",
            "url": "http://example.com/book1",
            "cover_url": "http://example.com/cover1.jpg"
        },
        {
            "title": "Race and Education: Breaking Barriers",
            "author": "Prof. John Johnson",
            "description": "An in-depth study of educational disparities and their intersection with racial justice, featuring case studies and practical frameworks for institutional change.",
            "isbn": "9789876543210",
            "url": "http://example.com/book2",
            "cover_url": "http://example.com/cover2.jpg"
        }
    ]

@pytest.mark.asyncio
async def test_batch_book_analysis(article_analysis, test_books):
    """Test batch processing of book relevance"""
    service = AnthropicService()
    
    # Mock the Anthropic client response
    mock_response = AsyncMock()
    mock_response.content = [{
        "text": '''[
            {
                "book_title": "Educational Justice in America",
                "relevance_score": 0.95,
                "explanation": "Directly addresses article topics with evidence-based solutions."
            },
            {
                "book_title": "Race and Education: Breaking Barriers",
                "relevance_score": 0.90,
                "explanation": "Strong focus on educational disparities and racial justice."
            }
        ]'''
    }]

    # Mock the entire Anthropic client instead of just the messages method
    with patch('anthropic.Anthropic') as MockAnthropic:
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = mock_response
        
        results = await service.batch_analyze_book_relevance(article_analysis, test_books)
        assert len(results) > 0
        for book, relevance in results:
            assert isinstance(relevance, BookRelevance)
            assert 0.8 <= relevance.relevance_score <= 1.0
            assert isinstance(relevance.explanation, str)

@pytest.mark.asyncio
async def test_relevance_threshold(article_analysis, test_books):
    """Test relevance score threshold filtering"""
    service = AnthropicService()
    results = await service.batch_analyze_book_relevance(
        article_analysis, 
        test_books,
        min_relevance_score=0.95  # High threshold
    )
    assert len(results) <= len(test_books)

@pytest.mark.asyncio
async def test_error_handling(article_analysis):
    """Test error handling with invalid book data"""
    service = AnthropicService()
    invalid_books = [{"title": ""}]  # Invalid book data
    results = await service.batch_analyze_book_relevance(article_analysis, invalid_books)
    assert len(results) == 0