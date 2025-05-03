from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ClassificationResult(Base):
    __tablename__ = 'classification_result'
    
    result_id = Column(Integer, primary_key=True)
    classification_id = Column(Integer, ForeignKey('image_classification.classification_id', ondelete='CASCADE'), nullable=False)
    class_name = Column(String(100), nullable=False)
    confidence_score = Column(Numeric(5, 2), nullable=False)
    rank = Column(Integer, nullable=False)
