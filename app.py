"""
LinkedIn Analyzer Agent - Main Application Entry Point
A powerful AI-driven agent for LinkedIn data analysis and career intelligence.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path


# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from src.config import settings
from src.database import init_db
from src.middleware import setup_middleware
from src.api import api_router
from src.core.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting LinkedIn Analyzer Agent...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Additional startup tasks
    logger.info("✅ Application startup complete")
    
    yield
    
    # Cleanup tasks
    logger.info("Shutting down LinkedIn Analyzer Agent...")


# Create FastAPI application
app = FastAPI(
    title="LinkedIn Analyzer Agent",
    description="A powerful AI-driven agent for LinkedIn data analysis and career intelligence",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "LinkedIn Analyzer Agent API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/api/docs",
        "health": "/api/v1/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level=settings.LOG_LEVEL.lower()
    )
