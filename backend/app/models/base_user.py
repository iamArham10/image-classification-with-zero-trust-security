from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
from .enums import UserTypeEnum
# Import UserRole to reference its columns
from .user_role import UserRole

class BaseUser(Base):
    __tablename__ = 'base_user'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(Text, nullable=False)
    user_type = Column(Enum(UserTypeEnum), nullable=False)
    mfa_enabled = Column(Boolean, default=False)
    totp_secret = Column(String(255))
    last_activity = Column(DateTime)
    active_status = Column(Boolean, nullable=False, default=True)
    login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=func.now())
    is_email_verified = Column(Boolean, nullable=False, default=False)
    email_verification_code = Column(String(6))
    email_verification_expires_at = Column(DateTime)
