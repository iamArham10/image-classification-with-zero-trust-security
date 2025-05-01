from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.base_user import base_user
from ..utils.security import verify_password

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        base_user = db.query(BaseUser).filter(BaseUser.username == username).first()
        if not base_user:
            return None
        
        # Check if the account is locked
        if base_user.locked_until and user.locked_until > datetime.now():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked due to too many failed login attempts"
            ) 
        
        if not verify_password(password, base_user.password_hash, base_user.password_salt):
            base_user.login_attempts += 1

            if base_user.login_attempts >= 5:
                base_user.locked_until = datetime.now() + timedelta(minutes=30)

            db.commit()
            return None
        
        base_user.login_attempts = 0
        base_user.last_activity = datetime.now()
        db.commit()

        return base_user