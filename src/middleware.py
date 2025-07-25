"""
Middleware configuration for LinkedIn Analyzer Agent
"""

import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Custom logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log incoming request
        logger.info(f"Incoming request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 3600):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: timestamps for ip, timestamps in self.clients.items()
            if timestamps and max(timestamps) > current_time - self.period
        }
        
        # Check rate limit
        if client_ip in self.clients:
            # Remove old timestamps
            self.clients[client_ip] = [
                ts for ts in self.clients[client_ip]
                if ts > current_time - self.period
            ]
            
            if len(self.clients[client_ip]) >= self.calls:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"}
                )
        else:
            self.clients[client_ip] = []
        
        # Add current timestamp
        self.clients[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response


def setup_middleware(app: FastAPI):
    """Setup all middleware for the application"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
    )
    
    # Custom logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Rate limiting middleware
    app.add_middleware(
        RateLimitMiddleware,
        calls=settings.RATE_LIMIT_REQUESTS,
        period=settings.RATE_LIMIT_WINDOW
    )
    
    logger.info("Middleware setup completed")
