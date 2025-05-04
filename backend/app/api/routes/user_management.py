from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_admin, get_db
from app.schemas.user_management import (
    UserListResponse,
    UserUpdate,
    UserUpdateResponse
)
from app.services.user_management import UserManagementService
from app.services.audit_log import add_audit_log
from app.models.enums import ActionTypeEnum, AuditStatusEnum
from app.utils.security import get_device_info, get_client_ip

router = APIRouter()

@router.get("/list", response_model=List[UserListResponse])
async def list_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    try:
        result = UserManagementService.get_user_list(db)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.user_list,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"Admin {current_user.user_id}, {current_user.email} retrieved user list",
            details=f"Admin {current_user.user_id}, {current_user.email} successfully retrieved list of all users"
        )
        
        return result
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.user_list,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id}, {current_user.email} failed to retrieve user list",
            details=str(e)
        )
        raise

@router.put("/{user_id}", response_model=UserUpdateResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
 
    try:
        result = UserManagementService.update_user(db, user_id, user)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.updated_user,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"Admin {current_user.user_id}, {current_user.email} updated user {user_id}",
            details=f"Admin {current_user.user_id}, {current_user.email} successfully updated user {user_id}"
        )
        
        return result
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.updated_user,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id}, {current_user.email} failed to update user {user_id}",
            details=str(e)
        )
        raise 