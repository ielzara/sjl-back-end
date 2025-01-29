from typing import Optional, Tuple, List, Dict, Any
import httpx
from datetime import datetime
from pydantic import HttpUrl

from app.core.config import settings
from app.schemas.article import ArticleCreate

class GuardianNewsService:
    """Service for interacting with The Guardian API"""
    
    # Core social justice themes and action terms
    SOCIAL_JUSTICE_QUERY = (
        "("
            '("racial justice" OR "civil rights" OR "systemic racism" OR "racial discrimination" OR "racial equity") OR '
            '("economic justice" OR "income inequality" OR "wealth gap" OR "economic discrimination" OR "housing crisis") OR '
            '("environmental justice" OR "climate justice" OR "environmental racism" OR "pollution impact") OR '
            '("gender equality" OR "women\'s rights" OR "gender discrimination" OR "reproductive rights" OR "pay gap") OR '
            '("healthcare access" OR "health equity" OR "healthcare discrimination" OR "mental health crisis") OR '
            '("protest" OR "activism" OR "legislation" OR "lawsuit" OR "discrimination" OR "human rights" OR "inequality")'
        ")"
    )
    
    def __init__(self):
        self.base_url = settings.GUARDIAN_BASE_URL
        self.api_key = settings.GUARDIAN_API_KEY
        if not self.api_key:
            raise ValueError("Guardian API key not configured")

    async def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make an HTTP request to the Guardian API"""
        params['api-key'] = self.api_key
        if 'show-fields' not in params:
            params['show-fields'] = 'body,bodyText,headline,trailText,sectionName'
        
        # Add tag filters to exclude certain content types
        params['tag'] = '-type/obituaries,-type/letters'
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    def _parse_article_data(self, article_data: Dict[str, Any]) -> ArticleCreate:
        """Parse raw Guardian API article data into ArticleCreate model"""
        fields = article_data.get('fields', {})
        content = fields.get('bodyText') or fields.get('body', '')
        
        return ArticleCreate(
            title=article_data['webTitle'],
            date=datetime.fromisoformat(article_data['webPublicationDate'].replace('Z', '+00:00')).date(),
            content=content,
            source="The Guardian",
            url=str(article_data['webUrl']),
            featured=False
        )

    async def search_articles(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[List[ArticleCreate], int]:
        """Search for articles using the Guardian API"""
        params = {
            'q': query,
            'page': page,
            'page-size': page_size,
            'order-by': 'newest'
        }
        
        if from_date:
            params['from-date'] = from_date.strftime('%Y-%m-%d')
        if to_date:
            params['to-date'] = to_date.strftime('%Y-%m-%d')
            
        response_data = await self._make_request('search', params)
        guardian_response = response_data['response']
        
        articles = [
            self._parse_article_data(article_data) 
            for article_data in guardian_response['results']
        ]
        
        return articles, guardian_response['total']

    async def get_recent_social_justice_articles(
        self,
        page: int = 1,
        page_size: int = 10,
        from_date: Optional[datetime] = None,
    ) -> Tuple[List[ArticleCreate], int]:
        """Get recent articles related to social justice topics"""
        return await self.search_articles(
            query=self.SOCIAL_JUSTICE_QUERY,
            page=page,
            page_size=page_size,
            from_date=from_date
        )