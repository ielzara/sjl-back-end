from typing import Optional, Tuple, List
import httpx
from datetime import datetime

from app.core.config import settings
from app.schemas.guardian import GuardianResponse, GuardianArticle
from app.schemas.article import ArticleCreate

class GuardianNewsService:
    """Service for interacting with The Guardian API"""
    
    def __init__(self):
        """Initialize the Guardian News service with configuration"""
        self.base_url = settings.GUARDIAN_BASE_URL
        self.api_key = settings.GUARDIAN_API_KEY
        if not self.api_key:
            raise ValueError("Guardian API key not configured")

    async def _make_request(self, endpoint: str, params: dict) -> dict:
        """
        Make an HTTP request to the Guardian API
        
        Args:
            endpoint: API endpoint path
            params: Query parameters for the request
            
        Returns:
            API response as dictionary
            
        Raises:
            HTTPError: If the request fails
        """
        # Always include the API key
        params['api-key'] = self.api_key
        
        # Add fields we want to retrieve
        if 'show-fields' not in params:
            params['show-fields'] = 'body,bodyText,headline,trailText'
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=30.0  # 30 second timeout
            )
            response.raise_for_status()
            return response.json()

    async def search_articles(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        section: Optional[str] = None,
    ) -> Tuple[List[GuardianArticle], int]:
        """
        Search for articles using the Guardian API
        
        Args:
            query: Search query string
            page: Page number (1-based)
            page_size: Number of results per page
            from_date: Optional start date for filtering
            to_date: Optional end date for filtering
            section: Optional section name for filtering
            
        Returns:
            Tuple of (list of articles, total number of results)
        """
        params = {
            'q': query,
            'page': page,
            'page-size': page_size,
            'order-by': 'newest'
        }
        
        # Add optional filters
        if from_date:
            params['from-date'] = from_date.strftime('%Y-%m-%d')
        if to_date:
            params['to-date'] = to_date.strftime('%Y-%m-%d')
        if section:
            params['section'] = section
            
        response_data = await self._make_request('search', params)
        response = GuardianResponse(**response_data['response'])
        
        return response.results, response.total
    
    def convert_to_article_create(self, guardian_article: GuardianArticle) -> ArticleCreate:
        """
        Convert a Guardian API article to our internal ArticleCreate format
        
        Args:
            guardian_article: Article from Guardian API
            
        Returns:
            ArticleCreate instance ready for database insertion
        """
        # Use bodyText if available (plain text), otherwise fall back to body (HTML)
        content = guardian_article.fields.bodyText if guardian_article.fields.bodyText else guardian_article.fields.body
        
        return ArticleCreate(
            title=guardian_article.webTitle,
            date=guardian_article.webPublicationDate.date(),
            content=content or "",  # Ensure we never have None content
            source="The Guardian",
            url=str(guardian_article.webUrl),
            featured=False  # Default to not featured
        )