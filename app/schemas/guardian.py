from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class GuardianArticleFields(BaseModel):
    """Fields returned by the Guardian API when show-fields parameter is used"""
    bodyText: Optional[str] = None
    body: Optional[str] = None
    headline: Optional[str] = None
    trailText: Optional[str] = None

class GuardianArticle(BaseModel):
    """Single article from Guardian API response"""
    id: str
    type: str
    sectionId: str
    sectionName: str
    webPublicationDate: datetime
    webTitle: str
    webUrl: HttpUrl
    apiUrl: HttpUrl
    fields: Optional[GuardianArticleFields] = None

class GuardianResponse(BaseModel):
    """Root response from Guardian API"""
    status: str
    total: int
    startIndex: int
    pageSize: int
    currentPage: int
    pages: int
    results: List[GuardianArticle]