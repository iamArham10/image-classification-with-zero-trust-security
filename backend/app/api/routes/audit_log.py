from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin
from app.models.base_user import BaseUser
from app.services.audit_log import get_audit_logs, add_audit_log
from app.schemas.audi_log import AuditLogResponseList
from app.models.enums import ActionTypeEnum, AuditStatusEnum
from app.utils.security import get_device_info, get_client_ip

router = APIRouter()

@router.get("/list", response_model=AuditLogResponseList)
async def list_audit_logs(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: BaseUser = Depends(get_current_admin)
):
    try:
        if not 1 <= limit <= 100:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.audit_log_retrieval,
                user_id=current_user.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"Admin {current_user.user_id} {current_user.email} {current_user.username} attempted to retrieve audit logs",
                details=f"Invalid limit value: {limit}. Must be between 1 and 100"
            )
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 100"
            )
        
        if offset < 0:
            add_audit_log(
                db=db,
                action=ActionTypeEnum.audit_log_retrieval,
                user_id=current_user.user_id,
                ip_address=get_client_ip(request),
                user_agent=get_device_info(request).get("user_agent"),
                status=AuditStatusEnum.failure,
                resource=f"Admin {current_user.user_id} {current_user.email} {current_user.username} attempted to retrieve audit logs",
                details=f"Invalid offset value: {offset}. Must be non-negative"
            )
            raise HTTPException(
                status_code=400,
                detail="Offset must be non-negative"
            )
            
        result = get_audit_logs(db, limit=limit, offset=offset)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.audit_log_retrieval,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"Admin {current_user.user_id} {current_user.email} {current_user.username} retrieved audit logs",
            details=f"Admin {current_user.user_id}, {current_user.email} successfully retrieved {limit} audit logs starting from offset {offset}"
        )
        
        return result
    except HTTPException as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.audit_log_retrieval,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id} {current_user.email} {current_user.username} failed to retrieve audit logs",
            details=str(e)
        )
        raise
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.audit_log_retrieval,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id} {current_user.email} {current_user.username} failed to retrieve audit logs",
            details=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch audit logs: {str(e)}"
        ) 