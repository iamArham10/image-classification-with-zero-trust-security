# app/middleware/rate_limiting.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from ..core.config import settings
class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Check rate limit
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip]
            if current_time - timestamp < 60
        ]
        
        # Check if rate limit exceeded
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Add current request timestamp
        self.request_counts[client_ip].append(current_time)
        
        # Process request
        return await call_next(request)