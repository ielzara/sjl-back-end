from fastapi import APIRouter
from app.api.v1.endpoints import articles, books, topics

# Create the main v1 API router
api_router = APIRouter()

# Include routers for different resources
api_router.include_router(
    articles.router,
    prefix="/articles",
    tags=["Articles"]
)

api_router.include_router(
    books.router,
    prefix="/books",
    tags=["Books"]
)

api_router.include_router(
    topics.router,
    prefix="/topics",
    tags=["Topics"]
)