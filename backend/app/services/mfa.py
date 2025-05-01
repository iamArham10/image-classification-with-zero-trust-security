"""
This file contains multi factor authentication functions
"""
from sqlalchemy.orm import Session

from ..models.base_user import BaseUser
from ..utils.totp import (
    generate_totp_secret, 
    get_totp_uri,
    get_qr_code_image, 
    verify_totp
)

class MFAService:
    @staticmethod
    def setup_mfa(db: Session, user_id: int):
        """Setup MFA for a user"""
        user = db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
        if not user:
            return None

        # Generate TOTP secret
        secret = generate_totp_secret()
        user.totp_secret = secret
        db.commit()

        # Generate QR code
        uri = get_totp_uri(secret, user.username)
        qr_code = get_qr_code_image(uri)
        return {
            "secret": secret,
            "qr_code": qr_code
        }

    @staticmethod
    def verify_mfa_setup(db: Session, user_id: int, token: str) -> bool:
        user = db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
        if not user or not user.totp_secret:
            return False
        
        # verify token
        if verify_totp(user.totp_secret, token):
            user.mfa_enabled = True
            db.commit()
            return True
        
        return False

    @staticmethod
    def verify_mfa(db: Session, user_id: int, token: str) -> bool:
        user = db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
        if not user or not user.totp_secret or not user.mfa_enabled:
            return False
        return verify_totp(user.totp_secret, token)