"""
This file contains ip restriction middleware code
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import ipaddress
import time
from collections import defaultdict

from ..core.config import settings
from ..utils.token import decode_token

class IPRestrictionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        current_time = time.time()

        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip]
            if current_time - timestamp < 60
        ]

        # Check if rate limit exceeded
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        self.request_counts[client_ip].append(current_time)
        return await call_next(request)
