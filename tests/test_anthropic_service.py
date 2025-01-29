import pytest
from app.services.anthropic_service import AnthropicService

@pytest.mark.asyncio
async def test_analyze_article():
    """Test article analysis with a social justice related article"""
    service = AnthropicService()
    
    # Sample article about environmental justice
    title = "Community Fights Environmental Racism in Urban Development"
    content = """A low-income neighborhood in Chicago is challenging a proposed industrial development, 
    citing concerns about air pollution and public health. Local activists argue that the placement of 
    polluting industries disproportionately affects communities of color, highlighting a pattern of 
    environmental racism. The community group has gathered health data showing higher rates of 
    respiratory issues in similar neighborhoods near industrial zones. They are demanding environmental 
    impact studies and community input in the development process."""

    analysis = await service.analyze_article(content, title)
    
    print("\nAnalysis Results:")
    print(f"Is Relevant: {analysis.is_relevant}")
    print(f"Relevance Score: {analysis.relevance_score}")
    print(f"Topics: {analysis.topics}")
    print(f"Keywords: {analysis.keywords}")
    print(f"Summary: {analysis.summary}")
    
    # Basic assertions to verify response structure
    assert analysis.is_relevant is True
    assert 0 <= analysis.relevance_score <= 1
    assert len(analysis.topics) > 0
    assert len(analysis.keywords) > 0
    assert len(analysis.summary) > 0