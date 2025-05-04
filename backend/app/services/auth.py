from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.base_user import BaseUser 
from ..utils.security import verify_password, get_password_hash, is_strong_password
from ..schemas.auth import UserSignup
from ..models.enums import UserTypeEnum

class AuthService:
    @staticmethod
    def create_user(db: Session, user_data: UserSignup) -> BaseUser:
        existing_user = db.query(BaseUser).filter(BaseUser.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        existing_email = db.query(BaseUser).filter(BaseUser.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        if not is_strong_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character"
            )
        
        hashed_password = get_password_hash(user_data.password)
        new_user = BaseUser(
            username=user_data.username,
            password_hash=hashed_password,
            email=user_data.email,
            full_name=user_data.full_name,
            user_type=UserTypeEnum.user,
            last_activity=datetime.now(),
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        base_user = db.query(BaseUser).filter(BaseUser.username == username).first()
        if not base_user:
            return None
        
        if base_user.locked_until and base_user.locked_until > datetime.now():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked due to too many failed login attempts"
            ) 
        
        if not verify_password(password, base_user.password_hash): 
            base_user.login_attempts += 1

            if base_user.login_attempts >= 5:
                base_user.locked_until = datetime.now() + timedelta(minutes=30)

            db.commit()
            return None
        
        base_user.login_attempts = 0
        base_user.last_activity = datetime.now()
        db.commit()

        return base_user