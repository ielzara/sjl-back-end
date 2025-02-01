import pytest
from datetime import datetime, timedelta
from app.services.guardian_news import GuardianNewsService

@pytest.mark.asyncio
async def test_guardian_search_articles():
    """Test basic article search functionality"""
    service = GuardianNewsService()
    
    print("\n=== Testing Basic Article Search ===")
    
    # Search for a general term that should always return results
    articles, total = await service.search_articles(
        query="climate change",
        page=1,
        page_size=5
    )
    
    print(f"Total results found: {total}")
    print(f"Retrieved {len(articles)} articles")
    
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article.title}")
        print(f"Date: {article.date}")
        print(f"URL: {article.url}")
        print(f"Content preview: {article.content[:200]}...")
    
    assert len(articles) > 0
    assert total > 0

@pytest.mark.asyncio
async def test_guardian_social_justice_articles():
    """Test fetching social justice related articles"""
    service = GuardianNewsService()
    
    print("\n=== Testing Social Justice Articles ===")
    
    from_date = datetime.now() - timedelta(days=30)
    
    articles, total = await service.get_recent_social_justice_articles(
        page=1,
        page_size=5,
        from_date=from_date
    )
    
    print(f"Total social justice articles found: {total}")
    print(f"Retrieved {len(articles)} articles")
    
    for i, article in enumerate(articles, 1):
        print(f"\nSocial Justice Article {i}:")
        print(f"Title: {article.title}")
        print(f"Date: {article.date}")
        print(f"URL: {article.url}")
        print(f"Content preview: {article.content[:200]}...")
    
    assert len(articles) > 0
    assert total > 0