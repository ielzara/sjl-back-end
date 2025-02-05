import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI(
    title="Social Justice Library API",
    description="API for connecting news articles with relevant books",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include system routes
app.include_router(system_router, prefix="/system")
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)