"""
This file contains authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ...db.session import get_db
from ...schemas.auth import Token, MFAVerify, MFASetupResponse, UserLogin
from ...services.auth import AuthService
from ...services.mfa import MFAService
from ...utils.token import create_access_token
from ...utils.security import get_device_info, get_client_ip
from ...core.config import settings
from ..schemas.BaseUser import BaseUser

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    User login, if mfa enabled returns mfa_enabled = True to further verify
    """
    user = AuthService.authenticate_user(db, 
                                        form_data.username, 
                                        form_data.password)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.mfa_enabled:
        return {
            "access_token": "",
            "token_type": "bearer",
            "requires_mfa": True,
            "user_id": user.user_id
        }

    context_data = {
        "user_type": user.user_type,
        "ip": get_client_ip(request),
        "device": get_device_info(request),
        "iat": datetime.utcnow().timestamp(),
        "mfa_verified": False
    }

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        subject=str(user.user_id),
        expires_delta=access_token_expires,
        context_data=context_data
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_mfa": False
    }

@router.post("/verify-mfa", response_model=Token)
async def verify_mfa(
    mfa_data: MFAVerify,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Verify mfa, returns token if successful
    """
    if not MFAService.verify_mfa(db, mfa_data.user_id, mfa_data.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(BaseUser).filter(BaseUser.user_id == mfa_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    context_data = {
        "user_type": user.user_type,
        "ip": get_client_ip(request),
        "device": get_device_info(request),
        "iat": datetime.utcnow().timestamp(),
        "mfa_verified": True
    }

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.user_id),
        expires_delta=access_token_expires,
        context_data=context_data
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_mfa": False
    }

@router.post("/setup-mfa", response_model=MFASetupResponse)
async def setup_mfa(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup mfa, returns secret and qr code
    """
    mfa_setup = MFAService.setup_mfa(db, current_user.user_id)
    if not mfa_setup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to setup MFA"
        )

    return mfa_setup

@router.post("/verify-mfa-setup")
async def verify_mfa_setup(
    mfa_data: MFAVerify,
    db: Session = Depends(get_db)
):
    """
    Verify mfa setup, Returns 'MFA setup verified successfully' if successful
    """
    if not MFAService.verify_mfa_setup(db, mfa_data.user_id, mfa_data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA token",
        )
    
    return {
        "message": "MFA setup verified successfully"
    }


