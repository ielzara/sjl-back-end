from typing import List, Dict, Optional
import json
from anthropic import Anthropic
from pydantic import BaseModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

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

    def clean_json_string(self, text: str) -> str:
        """Clean a string to make it valid JSON"""
        # Remove any control characters
        import re
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        return text

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
            
            text = self.clean_json_string(response.content[0].text)
            try:
                result = json.loads(text)
                return ArticleAnalysis(**result)
            except json.JSONDecodeError:
                # If we can't parse it directly, try to extract JSON between backticks
                import re
                json_match = re.search(r'```json\n(.*?\n)```', text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    return ArticleAnalysis(**result)
                raise  # Re-raise if we couldn't parse JSON
                
        except Exception as e:
            raise ValueError(f"Failed to process article analysis: {str(e)}")

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

Return ONLY the search terms in a JSON object with format:
{{"search_terms": ["term1", "term2", ...]}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = self.clean_json_string(response.content[0].text)
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Return a default format if parsing fails
            return {"search_terms": []}

    async def analyze_book_relevance(
        self,
        article_analysis: ArticleAnalysis,
        book_info: Dict[str, str]
    ) -> BookRelevance:
        """
        Analyze how relevant a book is to an article and explain why.
        """
        prompt = f"""Please analyze the relevance of this book to the article's social justice topics:

Article Topics: {article_analysis.topics}
Article Keywords: {article_analysis.keywords}
Article Summary: {article_analysis.summary}

Book Title: {book_info.get('title')}
Author: {book_info.get('author')}
Description: {book_info.get('description')}

Consider:
1. How directly the book addresses the article's key themes
2. Whether the book provides historical context or theoretical frameworks
3. If the book offers practical insights or solutions
4. The book's academic/scholarly value for understanding the issues

Provide a JSON response with:
- relevance_score: float 0.0-1.0 (use 0.8-1.0 for highly relevant books, 0.6-0.7 for moderately relevant, below 0.6 for tangentially related)
- explanation: clear explanation of why and how the book is relevant to understanding the article's issues. Explanation should be very concise, no more than 2-3 sentences."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=750,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            text = self.clean_json_string(response.content[0].text)
            try:
                result = json.loads(text)
                return BookRelevance(**result)
            except json.JSONDecodeError:
                # Try extracting JSON if the response includes other text
                import re
                json_match = re.search(r'\{[^{}]*\}', text)
                if json_match:
                    result = json.loads(json_match.group(0))
                    return BookRelevance(**result)
                    
                # If all else fails, return a low relevance score
                return BookRelevance(
                    relevance_score=0.0,
                    explanation="Failed to parse relevance analysis"
                )
        except Exception as e:
            # If anything goes wrong, return a zero relevance score
            return BookRelevance(
                relevance_score=0.0,
                explanation=f"Error analyzing book relevance: {str(e)}"
            )

    async def batch_analyze_book_relevance(
        self,
        article_analysis: ArticleAnalysis,
        books: List[Dict[str, str]],
        min_relevance_score: float = 0.9
    ) -> List[tuple[Dict[str, str], BookRelevance]]:
        """
        Analyze multiple books for relevance in a single API call.
        """
        if not books:
            return []
            
        # Simplify the prompt to get cleaner JSON response
        prompt = """Analyze these books' relevance to the article topics: {topics}
        
Books to analyze:
{book_list}

Rate each book's relevance to the article topics. Return ONLY a JSON array where each object has book_title (string), relevance_score (float 0.0-1.0), and explanation (string, 3-4 sentences). Example format (explanation doesn't have to start exactly like shown):
[
    {{
        "book_title": "Example Book",
        "relevance_score": 0.9,
        "explanation": "This book directly addresses the topics in the article and provides valuable insights into the issues..." 
    }}
]""".format(
            topics=article_analysis.topics,
            book_list=json.dumps([{
                'title': book.get('title'),
                'description': book.get('description', '')[:400]
            } for book in books], indent=2)
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            text = self.clean_json_string(response.content[0].text)
            
            # Try different JSON parsing approaches
            try:
                # Try direct JSON parsing first
                analyses = json.loads(text)
            except json.JSONDecodeError:
                # Try to extract JSON array
                import re
                json_match = re.search(r'\[(.*?)\]', text, re.DOTALL)
                if json_match:
                    analyses = json.loads(f"[{json_match.group(1)}]")
                else:
                    logger.error(f"Could not parse JSON response: {text[:100]}...")
                    return []
            
            if not isinstance(analyses, list):
                logger.error("Response is not a list")
                return []

            # Match analyses back to original books
            relevant_books = []
            for book in books:
                for analysis in analyses:
                    try:
                        if (analysis.get('book_title') == book.get('title') and 
                            float(analysis.get('relevance_score', 0)) >= min_relevance_score):
                            relevance = BookRelevance(
                                relevance_score=float(analysis['relevance_score']),
                                explanation=str(analysis.get('explanation', 'No explanation provided'))
                            )
                            relevant_books.append((book, relevance))
                            break
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Error processing analysis for book {book.get('title')}: {e}")
                        continue
            
            return sorted(relevant_books, key=lambda x: x[1].relevance_score, reverse=True)[:5]

        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            return []