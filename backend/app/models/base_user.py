"""
This file contains base user model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..db.session import Base

class UserTypeEnum(str, enum.Enum):
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"
    SYSTEM = "system"

class BaseUser(Base):
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    user_type = Column(Enum(UserTypeEnum, name="user_type_enum"), nullable=False)

    mfa_enabled = Column(Boolean, default=False)
    totp_secret = Column(String(255))
    is_email_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("base_user.user_id", ondelete="RESTRICT"), nullable=False)

    updated_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    updated_by = Column(Integer, ForeignKey("base_user.user_id", ondelete="RESTRICT"), nullable=False)

    deleted_at = Column(DateTime(timezone=False))
    deleted_by = Column(Integer, ForeignKey("base_user.user_id", ondelete="RESTRICT"))
    
    last_activity = Column(DateTime(timezone=False), nullable=True)

    active_status = Column(Boolean, default=True, nullable=False)
    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=False), nullable=True)

    # Self-relationships
    creater = relationship("base_user", foreign_keys=[created_by], remote_side=[user_id], post_update=True, backref="created_users")
    updater = relationship("base_user", foreign_keys=[updated_by], remote_side=[user_id], post_update=True, backref="updated_users")
    deleter = relationship("base_user", foreign_keys=[deleted_by], remote_side=[user_id], post_update=True, backref="deleted_users")