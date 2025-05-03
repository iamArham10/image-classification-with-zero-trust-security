"""
This file contains authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone

from ...db.session import get_db
from ...schemas.auth import Token, MFAVerify, MFASetupResponse, UserLogin, UserSignup, UserSignupResponse, EmailVerify
from ...services.auth import AuthService
from ...services.mfa import MFAService
from ...services.email import EmailService
from ...utils.token import create_access_token
from ...utils.security import get_device_info, get_client_ip
from ...core.config import settings
from ...models.base_user import BaseUser
from ..deps import get_current_user

router = APIRouter()

@router.post("/signup", response_model=UserSignupResponse)
async def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    User signup, creates a new user account
    """
    try:
        user = AuthService.create_user(db, user_data)
        
        return {
            "success": True,
            "message": "User created successfully"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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
        "requires_mfa": False,
        "user_id": user.user_id,
        "is_email_verified": user.is_email_verified
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
        "iat": datetime.now(timezone.utc).timestamp(),
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
        "requires_mfa": False,
        "user_type": user.user_type,
        "is_email_verified": user.is_email_verified
    }

@router.post("/send-verification-email")
async def send_verification_email(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send verification email to user
    """
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    EmailService.initiate_verification(db, current_user.user_id)
    return {"message": "Verification email sent"}

@router.post("/verify-email")
async def verify_email(
    email_data: EmailVerify,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify email with code
    """
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    if not EmailService.verify_email(db, current_user.user_id, email_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    return {"message": "Email verified successfully"}

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


