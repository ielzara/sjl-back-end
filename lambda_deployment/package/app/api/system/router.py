from fastapi import APIRouter
from app.api.system.endpoints import health, process

router = APIRouter()

# Include routers
router.include_router(health.router, prefix="/health", tags=["System"])
router.include_router(process.router, prefix="/process", tags=["System"])