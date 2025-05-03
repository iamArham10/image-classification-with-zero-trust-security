from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .enums import ClassificationStatusEnum

from .base import Base

class ImageClassification(Base):
    __tablename__ = 'image_classification'

    classification_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('base_user.user_id', ondelete='CASCADE'), nullable=False)
    image_hash = Column(String(64), nullable=False)
    image_path = Column(String(255))
    original_filename = Column(String(255))
    file_size = Column(Integer, nullable=False)
    classification_timestamp = Column(DateTime, nullable=False, default=func.now())
    model_used = Column(String(100), nullable=False)
    top_prediction = Column(String(100))
    confidence_score = Column(Numeric(5, 2))
    process_time_ms = Column(Integer)
    status = Column(Enum(ClassificationStatusEnum), nullable=False)
    ip_address = Column(String(45))
