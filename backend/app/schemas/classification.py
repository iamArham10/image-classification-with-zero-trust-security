from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ClassificationPrediction(BaseModel):
    class_name: str
    confidence_score: float
    rank: int

class ClassificationRequest(BaseModel):
    image_bytes: bytes = Field(..., description="Image bytes for classification")
    original_filename: Optional[str] = Field(None, description="Original filename of the image")

class ClassificationResponse(BaseModel):
    classification_id: int
    top_prediction: str
    confidence_score: float
    process_time_ms: int
    classification_timestamp: datetime

class ClassificationHistory(BaseModel):
    classification_id: int
    image_hash: str
    original_filename: Optional[str] = None
    classification_timestamp: datetime
    top_prediction: str
    confidence_score: Optional[float] = None
    process_time_ms: Optional[int] = None
    status: str

    class Config:
        from_attributes = True

class ClassificationHistoryAdminRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class ClassificationHistoryAdminResponseContent(BaseModel):
    user_name: str
    user_email: str
    user_type: str
    image_hash: str
    original_filename: str
    classification_id: int
    classification_timestamp: datetime
    top_prediction: str
    confidence_score: float
    process_time_ms: int
    status: str

class ClassificationHistoryAdminResponse(BaseModel):
    content: List[ClassificationHistoryAdminResponseContent]
    total_count: int



