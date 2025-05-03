"""
This file contains middleware for session management
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import jwt

from ..core.config import settings
from ..utils.token import decode_token
from ..db.session import SessionLocal
from ..models.base_user import BaseUser

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # if authentication endpoint, skip session check
        if request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)
        
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer"):
            return await call_next(request)
        
        token = authorization.replace("Bearer", "")

        try:
            payload = decode_token(token)
            user_id = int(payload.get("sub"))

            request_ip = request.client.host
            if "ip" in payload and payload["ip"] != request_ip:
                return HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="IP address mismatch"
                )

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
                    if inactivity_time > timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Session expired due to inactivity"
                        )
                
                user.last_activity = datetime.now()
                db.commit()
            finally:
                db.close()
        except jwt.PyJWTError:
            pass

        return await call_next(request)
            
