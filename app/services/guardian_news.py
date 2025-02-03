from typing import Optional, Tuple, List, Dict, Any
import httpx
import logging
from datetime import datetime
from pydantic import HttpUrl

from app.core.config import settings
from app.schemas.article import ArticleCreate

logger = logging.getLogger(__name__)

class GuardianNewsService:
    """Service for interacting with The Guardian API"""
    
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
    
    # Titles to exclude
    EXCLUDED_TITLES = [
        "Morning Mail",
    ]
    
    def __init__(self):
        self.base_url = settings.GUARDIAN_BASE_URL
        self.api_key = settings.GUARDIAN_API_KEY
        if not self.api_key:
            raise ValueError("Guardian API key not configured")
        logger.info(f"Guardian API initialized with base_url: {self.base_url}")

    async def search_articles(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[List[ArticleCreate], int]:
        """Search for articles using the Guardian API"""
        logger.info(f"Searching Guardian API with query: {query}")
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
            
        logger.info(f"Request params: {params}")
        
        try:
            response_data = await self._make_request('search', params)
            guardian_response = response_data['response']
            
            articles = []
            for article_data in guardian_response['results']:
                try:
                    article = self._parse_article_data(article_data)
                    if article:  # Only add if article wasn't filtered out
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Skipping article due to parsing error: {str(e)}")
                    continue
            
            logger.info(f"Found {len(articles)} valid articles out of {guardian_response['total']} total")
            return articles, guardian_response['total']
        
        except Exception as e:
            logger.error(f"Error in Guardian API search: {str(e)}", exc_info=True)
            return [], 0

    async def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make an HTTP request to the Guardian API"""
        params['api-key'] = self.api_key
        if 'show-fields' not in params:
            params['show-fields'] = 'body,bodyText,headline,trailText,sectionName'
        
        params['tag'] = '-type/obituaries,-type/letters'
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            raise

    def _parse_article_data(self, article_data: Dict[str, Any]) -> Optional[ArticleCreate]:
        """
        Parse raw Guardian API data into ArticleCreate model.
        Returns None for articles that should be excluded.
        """
        try:
            title = article_data['webTitle']
            
            # Skip articles with excluded titles
            if any(title.startswith(excluded) for excluded in self.EXCLUDED_TITLES):
                logger.info(f"Skipping excluded article: {title}")
                return None
                
            fields = article_data.get('fields', {})
            content = fields.get('bodyText') or fields.get('body', '')
            
            return ArticleCreate(
                title=title,
                date=datetime.fromisoformat(article_data['webPublicationDate'].replace('Z', '+00:00')).date(),
                content=content,
                source="The Guardian",
                url=str(article_data['webUrl']),
                featured=False
            )
        except Exception as e:
            logger.error(f"Error parsing article data: {str(e)}")
            raise

    async def get_recent_social_justice_articles(
        self,
        page: int = 1,
        page_size: int = 10,
        from_date: Optional[datetime] = None,
    ) -> Tuple[List[ArticleCreate], int]:
        """Get recent articles related to social justice topics"""
        logger.info("Getting recent social justice articles")
        logger.info(f"Query: {self.SOCIAL_JUSTICE_QUERY}")
        return await self.search_articles(
            query=self.SOCIAL_JUSTICE_QUERY,
            page=page,
            page_size=page_size,
            from_date=from_date
        )