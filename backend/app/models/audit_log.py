from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
from .enums import ActionTypeEnum, AuditStatusEnum

class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    log_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    user_id = Column(Integer, ForeignKey('base_user.user_id', ondelete='SET NULL'))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    action = Column(Enum(ActionTypeEnum), nullable=False)
    resource = Column(String(100))
    status = Column(Enum(AuditStatusEnum), nullable=False, default=AuditStatusEnum.success)
    details = Column(Text)
   
