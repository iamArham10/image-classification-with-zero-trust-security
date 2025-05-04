from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import Response
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_admin
from app.models.base_user import BaseUser
from app.models.image_classification import ImageClassification
from app.schemas.classification import ClassificationHistory, ClassificationResponse, ClassificationHistoryAdminResponse
from ...services.classification_service import ClassificationService
from ...services.image_storage_service import ImageStorageService
from app.services.audit_log import add_audit_log
from app.models.enums import ActionTypeEnum, AuditStatusEnum, ClassificationStatusEnum
from app.utils.security import get_device_info, get_client_ip

router = APIRouter()

@router.post("/classify", response_model=ClassificationResponse)
async def classify(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: BaseUser = Depends(get_current_user)
):
    try:
        result = await ClassificationService(db).process_image(file, current_user.user_id)
        print(result) 
        add_audit_log(
            db=db,
            action=ActionTypeEnum.image_upload,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {current_user.user_id} uploaded and classified image",
            details=f"User {current_user.user_id}, {current_user.email} successfully classified image with result: {result.top_prediction} (confidence: {result.confidence_score:.2f})"
        )
        
        return result
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.image_upload,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User {current_user.user_id} failed to classify image",
            details=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[ClassificationHistory])
async def get_history(
    request: Request,
    db: Session = Depends(get_db),
    current_user: BaseUser = Depends(get_current_user)
):
    try:
        service = ClassificationService(db)
        history = service.get_classification_history(current_user.user_id)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.classification_history,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {current_user.user_id} retrieved classification history",
            details=f"User {current_user.user_id}, {current_user.email} successfully retrieved their classification history"
        )
        
        return history
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.classification_history,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User {current_user.user_id} failed to retrieve classification history",
            details=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history-all", response_model=ClassificationHistoryAdminResponse)
async def get_all_history(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: BaseUser = Depends(get_current_admin)
):
    try:
        service = ClassificationService(db)
        history = service.get_all_classification_history(limit=limit, offset=offset)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.admin_classification_history,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"Admin {current_user.user_id} retrieved all classification history",
            details=f"Admin {current_user.user_id}, {current_user.email} successfully retrieved all classification history"
        )
        
        return history
    except HTTPException as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.admin_classification_history,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id} failed to retrieve all classification history",
            details=str(e)
        )
        raise e
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.admin_classification_history,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id} failed to retrieve all classification history",
            details=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch classification history: {str(e)}"
        )
        
@router.get("/image/{classification_id}")
async def get_image(
    request: Request,
    classification_id: int,
    db: Session = Depends(get_db),
    current_user: BaseUser = Depends(get_current_user)
):
    try:
        classification = db.query(ImageClassification).filter(
            ImageClassification.classification_id == classification_id,
            ImageClassification.user_id == current_user.user_id
        ).first()
        
        if not classification:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.image_retrieval,
                user_id=current_user.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"User {current_user.user_id} attempted to retrieve image",
                details=f"Image with ID {classification_id} not found for user {current_user.user_id}"
            )
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_data = ImageStorageService(db).get_decrypted_image(classification_id)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.image_retrieval,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"User {current_user.user_id} retrieved image",
            details=f"User {current_user.user_id}, {current_user.email} successfully retrieved image {classification_id}"
        )
        
        return Response(
            content=image_data,
            media_type="image/jpeg"
        )
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.image_retrieval,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"User {current_user.user_id} failed to retrieve image",
            details=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) 