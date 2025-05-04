"""
This file contains email verification functions
"""
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.base_user import BaseUser
from ..core.config import settings
from .sendgrid_service import sendgrid_service

class EmailService:
    @staticmethod
    def generate_verification_code() -> str:
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def send_verification_email(email: str, code: str):
        subject = "Email Verification Code"
        content = f"""
        <html>
            <body>
                <h2>Email Verification</h2>
                <p>Your verification code is: <strong>{code}</strong></p>
                <p>This code will expire in 1 minute.</p>
                <p>If you didn't request this verification, please ignore this email.</p>
            </body>
        </html>
        """
        
        success = sendgrid_service.send_email(
            to_email=email,
            subject=subject,
            content=content
        )
        
        if not success:
            print(f"Failed to send verification email to {email}")
        else:
            print(f"Verification code {code} sent to {email}")

    @staticmethod
    def initiate_verification(db: Session, user_id: int) -> str:
        """Initiate email verification process"""
        user = db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        verification_code = EmailService.generate_verification_code()
        
        user.email_verification_code = verification_code
        user.email_verification_expires_at = datetime.now() + timedelta(minutes=1)
        db.commit()

        EmailService.send_verification_email(user.email, verification_code)

        return verification_code

    @staticmethod
    def verify_email(db: Session, user_id: int, code: str) -> bool:
        user = db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if (user.email_verification_code != code or 
            not user.email_verification_expires_at or 
            user.email_verification_expires_at < datetime.now()):
            return False

        user.is_email_verified = True
        user.email_verification_code = None
        user.email_verification_expires_at = None
        db.commit()

        return True 