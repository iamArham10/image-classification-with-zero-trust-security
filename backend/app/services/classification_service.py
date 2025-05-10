from datetime import datetime
import hashlib
import time
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from ..models.image_classification import ImageClassification
from ..models.enums import ClassificationStatusEnum
from ..schemas.classification import ClassificationResponse, ClassificationHistory, ClassificationHistoryAdminResponse, ClassificationHistoryAdminResponseContent
from ..utils.model import classify_image
from .image_storage_service import ImageStorageService
from ..models.base_user import BaseUser

class ClassificationService:
    def __init__(self, db: Session):
        self.db = db
        self.image_storage = ImageStorageService(db)

    async def process_image(self, file: UploadFile, user_id: int) -> ClassificationResponse:
        start_time = time.time()
        
        try:
            image_bytes = await file.read()
            print(f"Read image bytes: {len(image_bytes)} bytes")  # Debug log
            
            image_hash = hashlib.sha256(image_bytes).hexdigest()
            print(f"Generated image hash: {image_hash}")  # Debug log
            
            classification = ImageClassification(
                user_id=user_id,
                image_hash=image_hash,
                original_filename=file.filename,
                file_size=len(image_bytes),
                model_used="cifar10_resnet20",
                status=ClassificationStatusEnum.failed
            )
            self.db.add(classification)
            self.db.flush()
            print(f"Created classification record with ID: {classification.classification_id}")  # Debug log
            
            # Store image first, before classification attempt
            print("Attempting to store image...")  # Debug log
            image_path = await self.image_storage.store_image(image_bytes, classification.classification_id)
            print(f"Image stored at: {image_path}")  # Debug log
            
            try:
                predictions = classify_image(image_bytes)
                top_prediction = predictions[0]
                print(f"Got predictions: {predictions}")  # Debug log
                
                classification.top_prediction = top_prediction["class"]
                classification.confidence_score = top_prediction["probability"]
                
                if top_prediction["probability"] >= 0.60:
                    classification.status = ClassificationStatusEnum.success
                else:
                    classification.status = ClassificationStatusEnum.failed
                
                process_time_ms = int((time.time() - start_time) * 1000)
                classification.process_time_ms = process_time_ms
                
                self.db.commit()
                self.db.refresh(classification) 
                return ClassificationResponse(
                    classification_id=classification.classification_id,
                    top_prediction=classification.top_prediction,
                    confidence_score=float(classification.confidence_score),
                    process_time_ms=process_time_ms,
                    classification_timestamp=classification.classification_timestamp
                )
                
            except Exception as e:
                print(f"Error in classification process: {str(e)}")  
                classification.status = ClassificationStatusEnum.error
                self.db.commit()
                raise HTTPException(status_code=500, detail=str(e))
                
        except Exception as e:
            print(f"Error in process_image: {str(e)}")  
            raise HTTPException(status_code=500, detail=str(e))

    def get_classification_history(self, user_id: int, limit: int = 10) -> List[ClassificationHistory]:

        try:
            print(f"Fetching history for user {user_id}")  
            classifications = self.db.query(ImageClassification)\
                .filter(ImageClassification.user_id == user_id)\
                .order_by(ImageClassification.classification_timestamp.desc())\
                .limit(limit)\
                .all()
            
            print(f"Found {len(classifications)} classifications")  
                
            return [
                ClassificationHistory(
                    classification_id=classification.classification_id,
                    image_hash=classification.image_hash,
                    original_filename=classification.original_filename,
                    classification_timestamp=classification.classification_timestamp,
                    top_prediction=classification.top_prediction,
                    confidence_score=float(classification.confidence_score),
                    process_time_ms=classification.process_time_ms,
                    status=classification.status.value
                ) for classification in classifications
            ]
        except Exception as e:
            print(f"Error in get_classification_history: {str(e)}")  
            raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}") 

    def get_all_classification_history(self, limit: int = 10, offset: int = 0) -> ClassificationHistoryAdminResponse:
        try:
            if not 1 <= limit <= 100:
                raise HTTPException(
                    status_code=400,
                    detail="Limit must be between 1 and 100"
                )
            
            if offset < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Offset must be non-negative"
                )

            total_count = self.db.query(ImageClassification).count()
            
            classifications = self.db.query(
                ImageClassification,
                BaseUser.username,
                BaseUser.email,
                BaseUser.user_type
            )\
                .join(BaseUser, ImageClassification.user_id == BaseUser.user_id)\
                .order_by(ImageClassification.classification_timestamp.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            content = [
                ClassificationHistoryAdminResponseContent(
                    user_name=username,
                    user_email=email,
                    user_type=user_type.value,
                    image_hash=classification.image_hash,
                    original_filename=classification.original_filename,
                    classification_id=classification.classification_id,
                    classification_timestamp=classification.classification_timestamp,
                    top_prediction=classification.top_prediction if classification.top_prediction is not None else "Unknown",
                    confidence_score=float(classification.confidence_score) if classification.confidence_score is not None else 0.0,
                    process_time_ms=classification.process_time_ms if classification.process_time_ms is not None else 0,
                    status=classification.status.value
                ) for classification, username, email, user_type in classifications
            ]
            
            return ClassificationHistoryAdminResponse(
                content=content,
                total_count=total_count
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in get_all_classification_history: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch classification history: {str(e)}"
            )
