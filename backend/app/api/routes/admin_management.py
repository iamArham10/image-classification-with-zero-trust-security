from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ...services.token import TokenRotationService
from app.api.deps import get_current_admin, get_db
from ...services.audit_log import add_audit_log
from ...models.enums import ActionTypeEnum, AuditStatusEnum
from app.schemas.admin_management import (
    AdminCreate,
    AdminCreateResponse,
    AdminListResponse,
    AdminUpdate,
    AdminUpdateResponse
)
from app.services.admin_management import AdminManagementService
from app.core.config import settings
from app.utils.security import get_device_info, get_client_ip
router = APIRouter()

@router.post("/create", response_model=AdminCreateResponse)
async def create_admin(
    admin: AdminCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    if admin.admin_creation_token != settings.ADMIN_CREATION_TOKEN:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.admin_create,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id} attempted to create admin with invalid token",
            details=f"Invalid admin creation token provided by {current_user.email} {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin creation token"
        )
    
    TokenRotationService.rotate_token()

    try:
        # create the admin
        result = AdminManagementService.create_admin(db, admin)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.created_user,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"Admin {current_user.user_id} created new admin",
            details=f"Admin {current_user.user_id}, {current_user.email} created new admin with username {admin.username}"
        )
        
        return result
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.created_user,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id}, {current_user.email} failed to create new admin",
            details=str(e)
        )
        raise

@router.get("/list", response_model=List[AdminListResponse])
async def list_admins(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    try:
        result = AdminManagementService.get_admin_list(db)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.admin_list,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"Admin {current_user.user_id}, {current_user.email} retrieved admin list",
            details=f"Admin {current_user.user_id}, {current_user.email} successfully retrieved list of all admins"
        )
        
        return result
    except Exception as e:
        add_audit_log(
            db=db,
            action=ActionTypeEnum.admin_list,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id}, {current_user.email} failed to retrieve admin list",
            details=str(e)
        )
        raise

@router.put("/{admin_id}", response_model=AdminUpdateResponse)
async def update_admin(
    admin_id: int,
    admin: AdminUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    try:
        result = AdminManagementService.update_admin(db, admin_id, admin)
        
        add_audit_log(
            db=db,
            action=ActionTypeEnum.updated_user,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.success,
            resource=f"Admin {current_user.user_id}, {current_user.email} updated admin {admin_id}",
            details=f"Admin {current_user.user_id}, {current_user.email} successfully updated admin {admin_id}"
        )
        
        return result
    except Exception as e:
        # add audit log for failed admin update
        add_audit_log(
            db=db,
            action=ActionTypeEnum.updated_user,
            user_id=current_user.user_id,
            ip_address=get_client_ip(request),
            user_agent=get_device_info(request).get("user_agent"),
            status=AuditStatusEnum.failure,
            resource=f"Admin {current_user.user_id}, {current_user.email} failed to update admin {admin_id}",
            details=str(e)
        )
        raise 