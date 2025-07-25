"""
Database configuration and initialization
"""

import asyncio
import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

logger = logging.getLogger(__name__)

# Database engines
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite for development
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    async_engine = None
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = None
else:
    # PostgreSQL for production
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Async engine for high-performance operations
    ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    async_engine = create_async_engine(ASYNC_DATABASE_URL)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Base class for SQLAlchemy models
Base = declarative_base()
metadata = MetaData()


async def init_db():
    """Initialize database tables"""
    try:
        if async_engine:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def get_db() -> SessionLocal:
    """Get database session (sync)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (async)"""
    if not AsyncSessionLocal:
        raise RuntimeError("Async database not configured")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.engine = engine
        self.async_engine = async_engine
        self.session_factory = SessionLocal
        self.async_session_factory = AsyncSessionLocal
    
    def get_session(self):
        """Get synchronous database session"""
        return self.session_factory()
    
    async def get_async_session(self):
        """Get asynchronous database session"""
        if not self.async_session_factory:
            raise RuntimeError("Async database not configured")
        return self.async_session_factory()
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            if self.async_engine:
                async with self.async_engine.begin() as conn:
                    await conn.execute("SELECT 1")
            else:
                with self.engine.begin() as conn:
                    conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
