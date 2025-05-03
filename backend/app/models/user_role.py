from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class UserRole(Base):
    __tablename__ = 'user_role'
    
    user_id = Column(Integer, ForeignKey('base_user.user_id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(Integer, ForeignKey('role.role_id', ondelete='CASCADE'), primary_key=True)
    granted_at = Column(DateTime, nullable=False, default=func.now())
    granted_by = Column(Integer, ForeignKey('base_user.user_id', ondelete='SET NULL'), nullable=False)
