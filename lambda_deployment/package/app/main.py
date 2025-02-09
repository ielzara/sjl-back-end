import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.api.system.router import router as system_router
from app.api.v1.router import api_router
from app.core.config import Settings
from app.core.database import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_application() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Social Justice Library API",
        description="API for connecting news articles with relevant books",
        version="1.0.0"
    )

    # CORS configuration
    origins = [
        "http://localhost:5173",  # React local development
        os.getenv("FRONTEND_URL", ""),  # Production frontend URL
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin for origin in origins if origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(system_router, prefix="/system")
    app.include_router(api_router, prefix="/api/v1")

    return app

# Create application instance
app = get_application()

# Create handler for AWS Lambda
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)