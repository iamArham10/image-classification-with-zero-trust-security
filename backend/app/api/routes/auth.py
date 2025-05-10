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
from ...services.audit_log import add_audit_log 
from ...models.enums import ActionTypeEnum, AuditStatusEnum
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
    try:
        user = AuthService.create_user(db, user_data)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.sign_up,
            user_id=user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status = AuditStatusEnum.success,
            resource=f"User {user.user_id} {user.email} {user.username} signed up",
            details=f"User {user.user_id} from {get_client_ip(request)} signed up"
        )

        return {
            "success": True,
            "message": "User created successfully"
        }
    
    except HTTPException as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.sign_up,
            user_id=None,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User signup failed",
            details=str(e)
        )

        raise e
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.sign_up,
            user_id=None,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User signup failed",
            details=str(e)
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        user = AuthService.authenticate_user(db, 
                                            form_data.username, 
                                            form_data.password)
        
        if not user:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.login,
                user_id=None,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User login failed",
                details=f"Incorrect username or password from user {form_data.username}"
            )

            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        
        if user.mfa_enabled:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.login,
                user_id=user.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.success,
                resource=f"User {user.user_id} {user.email} {user.username} login with MFA required",
                details=f"User {user.user_id} {user.email} {user.username} from {get_client_ip(request)} logged in with MFA required"
            )

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

        add_audit_log(
            db=db,
            action=ActionTypeEnum.login,
            user_id=user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {user.user_id} {user.email} {user.username} logged in",
            details=f"User {user.user_id} {user.email} {user.username} from {get_client_ip(request)} logged in successfully"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "requires_mfa": False,
            "user_id": user.user_id,
            "is_email_verified": user.is_email_verified
        }
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.login,
            user_id=None,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User login for {form_data.username} failed",
            details=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/verify-mfa", response_model=Token)
async def verify_mfa(
    mfa_data: MFAVerify,
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        if not MFAService.verify_mfa(db, mfa_data.user_id, mfa_data.token):
            add_audit_log(
                db=db,
                action=ActionTypeEnum.mfa_verify,
                user_id=mfa_data.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User {mfa_data.user_id}  MFA verification failed",
                details=f"Invalid MFA token provided for user {mfa_data.user_id}"
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(BaseUser).filter(BaseUser.user_id == mfa_data.user_id).first()
        if not user:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.mfa_verify,
                user_id=mfa_data.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User {mfa_data.user_id}  not found",
                details=f"User {mfa_data.user_id}  not found during MFA verification"
            )

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

        add_audit_log(
            db=db,
            action=ActionTypeEnum.mfa_verify,
            user_id=user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {user.user_id} {user.email} {user.username} MFA verified",
            details=f"User {user.user_id} {user.email} {user.username} successfully verified MFA"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "requires_mfa": False,
            "user_type": user.user_type,
            "is_email_verified": user.is_email_verified
        }
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.mfa_verify,
            user_id=mfa_data.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User {mfa_data.user_id} MFA verification failed",
            details=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/send-verification-email")
async def send_verification_email(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        if current_user.is_email_verified:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.email_verify,
                user_id=current_user.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User {current_user.user_id} {current_user.email} {current_user.username} email already verified",
                details=f"User {current_user.user_id} {current_user.email} {current_user.username} attempted to verify already verified email"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        EmailService.initiate_verification(db, current_user.user_id)

        add_audit_log(
            db=db,
            action=ActionTypeEnum.email_verify,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {current_user.user_id} {current_user.email} {current_user.username} verification email sent",
            details=f"Verification email sent to user {current_user.user_id} {current_user.email} {current_user.username}"
        )

        return {"message": "Verification email sent"}
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.email_verify,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User {current_user.user_id} {current_user.email} {current_user.username} verification email failed",
            details=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/verify-email")
async def verify_email(
    email_data: EmailVerify,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Verify email with code
    """
    try:
        if current_user.is_email_verified:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.email_verify,
                user_id=current_user.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User {current_user.user_id} {current_user.email} {current_user.username} email already verified",
                details=f"User {current_user.user_id} {current_user.email} {current_user.username} attempted to verify already verified email"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        if not EmailService.verify_email(db, current_user.user_id, email_data.code):
            add_audit_log(
                db=db,
                action=ActionTypeEnum.email_verify,
                user_id=current_user.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User {current_user.user_id} {current_user.email} {current_user.username} email verification failed",
                details=f"Invalid or expired verification code provided"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.email_verify,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {current_user.user_id} {current_user.email} {current_user.username} email verified",
            details=f"User {current_user.user_id} {current_user.email} {current_user.username} successfully verified their email"
        )
        
        return {"message": "Email verified successfully"}
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.email_verify,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User {current_user.user_id} {current_user.email} {current_user.username} email verification failed",
            details=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/setup-mfa", response_model=MFASetupResponse)
async def setup_mfa(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        mfa_setup = MFAService.setup_mfa(db, current_user.user_id)
        if not mfa_setup:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.mfa_setup,
                user_id=current_user.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User {current_user.user_id} {current_user.email} {current_user.username} MFA setup failed",
                details=f"Failed to setup MFA for user {current_user.user_id} {current_user.email} {current_user.username}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to setup MFA"
            )

        add_audit_log(
            db=db,
            action=ActionTypeEnum.mfa_setup,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {current_user.user_id} {current_user.email} {current_user.username} MFA setup initiated",
            details=f"User {current_user.user_id} {current_user.email} {current_user.username} initiated MFA setup"
        )

        return mfa_setup
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.mfa_setup,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User {current_user.user_id} {current_user.email} {current_user.username} MFA setup failed",
            details=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/verify-mfa-setup")
async def verify_mfa_setup(
    mfa_data: MFAVerify,
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        if not MFAService.verify_mfa_setup(db, mfa_data.user_id, mfa_data.token):
            add_audit_log(
                db=db,
                action=ActionTypeEnum.mfa_setup,
                user_id=mfa_data.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User {mfa_data.user_id} MFA setup verification failed",
                details=f"Invalid MFA token provided for setup verification"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA token",
            )
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.mfa_setup,
            user_id=mfa_data.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {mfa_data.user_id}  MFA setup verified",
            details=f"User {mfa_data.user_id}  successfully verified MFA setup"
        )
        
        return {
            "message": "MFA setup verified successfully"
        }
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.mfa_setup,
            user_id=mfa_data.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User {mfa_data.user_id} MFA setup verification failed",
            details=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


