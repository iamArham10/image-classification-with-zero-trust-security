"""
This file contains security middleware for the application
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import time
from collections import defaultdict
import jwt

from ..core.config import settings
from ..utils.token import decode_token
from ..db.session import SessionLocal
from ..models.base_user import BaseUser

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests_per_minute = settings.RATE_LIMIT_PER_MINUTE
        self.request_counts = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip security checks for auth endpoints
        if request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)

        # Rate limiting
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old requests
        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip]
            if current_time - timestamp < 60
        ]
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        self.request_counts[client_ip].append(current_time)

        # Session management
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer"):
            return await call_next(request)
        
        token = authorization.replace("Bearer", "").strip()

        try:
            payload = decode_token(token)
            user_id = int(payload.get("sub"))

            # IP validation
            request_ip = request.client.host
            if "ip" in payload and payload["ip"] != request_ip:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="IP address mismatch"
                )

            # User session validation
            db = SessionLocal()
            try:
                user = db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found"
                    )

                if user.last_activity:
                    inactivity_time = datetime.now() - user.last_activity
                    if inactivity_time > timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Session expired due to inactivity"
                        )
                
                user.last_activity = datetime.now()
                db.commit()
            finally:
                db.close()
        except jwt.PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return await call_next(request) 