from typing import List, Dict, Optional
import json
from anthropic import Anthropic
from pydantic import BaseModel
from app.core.config import settings


class ArticleAnalysis(BaseModel):
    """Model for article analysis results"""
    is_relevant: bool
    relevance_score: float  # 0.0 to 1.0
    topics: List[str]
    keywords: List[str]
    summary: str


class BookRelevance(BaseModel):
    """Model for book relevance results"""
    relevance_score: float  # 0.0 to 1.0
    explanation: str


class AnthropicService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    async def analyze_article(self, article_text: str, article_title: str) -> ArticleAnalysis:
        """
        Analyze an article to determine its relevance to social justice topics
        and extract key information.
        """
        prompt = f"""Analyze this article for social justice relevance and provide key information:

Title: {article_title}

Article text:
{article_text}

Analyze the article's relevance to social justice topics and provide:
1. Whether the article is relevant to social justice issues (true/false)
2. A relevance score (0.0-1.0) indicating how strongly it relates to social justice topics
3. Specific social justice topics mentioned or relevant to the article
4. Key terms and concepts that would make good search terms for finding related educational books
5. A brief summary focusing on the social justice aspects

# Response format should be valid JSON:
{{
    "is_relevant": boolean,
    "relevance_score": float,
    "topics": list[str],
    "keywords": list[str],
    "summary": str
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            return ArticleAnalysis(**result)
            
        except json.JSONDecodeError:
            text = response.content[0].text
            try:
                # Look for JSON between triple backticks if present
                import re
                json_match = re.search(r"```json\n(.*?\n)```", text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    return ArticleAnalysis(**result)
            except:
                pass
            
            raise ValueError(f"Failed to parse Claude response: {text}")

    async def generate_book_keywords(self, article_analysis: ArticleAnalysis) -> List[str]:
        """
        Generate keywords for book search based on article analysis.
        """
        prompt = f"""Based on this article analysis, generate search terms for finding relevant educational books:

Article Information:
Topics: {article_analysis.topics}
Keywords: {article_analysis.keywords}
Summary: {article_analysis.summary}

Generate 5-10 specific search terms that would be effective for finding educational books about these topics.
Consider academic terms, historical events, key concepts, and influential authors.
Return the search terms as a JSON array of strings."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    async def analyze_book_relevance(
        self,
        article_analysis: ArticleAnalysis,
        book_info: Dict[str, str]
    ) -> BookRelevance:
        """
        Analyze how relevant a book is to an article and explain why.
        """
        prompt = f"""Analyze this book's relevance to the article's social justice topics:

Article Topics: {article_analysis.topics}
Article Keywords: {article_analysis.keywords}
Article Summary: {article_analysis.summary}

Book Title: {book_info.get('title')}
Author: {book_info.get('author')}
Description: {book_info.get('description')}

Provide a JSON response with:
- relevance_score: float 0.0-1.0 indicating how well the book provides context for understanding the article's topics
- explanation: clear explanation of why and how the book is relevant to understanding the article's issues"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=750,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )

        result = json.loads(response.content[0].text)
        return BookRelevance(**result)

    async def batch_analyze_book_relevance(
        self,
        article_analysis: ArticleAnalysis,
        books: List[Dict[str, str]],
        min_relevance_score: float = 0.6
    ) -> List[tuple[Dict[str, str], BookRelevance]]:
        """
        Analyze multiple books for relevance.
        Returns list of (book_info, relevance) tuples sorted by relevance score.
        """
        relevant_books = []
        
        for book in books:
            relevance = await self.analyze_book_relevance(article_analysis, book)
            if relevance.relevance_score >= min_relevance_score:
                relevant_books.append((book, relevance))
        
        relevant_books.sort(key=lambda x: x[1].relevance_score, reverse=True)
        return relevant_books