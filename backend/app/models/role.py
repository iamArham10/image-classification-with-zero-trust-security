from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

class Role(Base):
    __tablename__ = 'role'
    
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String)
