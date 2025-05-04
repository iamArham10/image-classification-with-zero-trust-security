from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..db.session import get_db
from ..models.base_user import BaseUser
from ..models.enums import UserTypeEnum
from ..core.config import settings
from ..utils.security import get_client_ip, get_device_info
from typing import Optional
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Request = None,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        if request:
            token_ip = payload.get("ip") 
            current_ip = get_client_ip(request)
            if token_ip != current_ip:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="IP address mismatch, please login again",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            token_device = payload.get("device")
            current_device = get_device_info(request)
            if token_device != current_device:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Device mismatch, please login again",
                    headers={"WWW-Authenticate": "Bearer"}
                )
    except JWTError:
        raise credentials_exception
    
    user = db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.active_status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive"
        )

    user.last_activity = datetime.now()
    db.commit()

    return user 

async def get_current_active_user(current_user: BaseUser = Depends(get_current_user)):
    if not current_user.active_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is inactive"
        )
    return current_user
        
async def get_current_admin(current_user: BaseUser = Depends(get_current_user)):
    if current_user.user_type != UserTypeEnum.admin: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions"
        )
    return current_user