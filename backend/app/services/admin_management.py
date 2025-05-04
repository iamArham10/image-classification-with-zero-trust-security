from sqlalchemy.orm import Session
from app.models.base_user import BaseUser
from app.schemas.admin_management import *
from app.utils.security import *
from fastapi import HTTPException, status
from ..models.enums import UserTypeEnum

class AdminManagementService:

    @staticmethod
    def create_admin(db: Session, admin: AdminCreate) -> AdminCreateResponse:
        user = db.query(BaseUser).filter(BaseUser.username == admin.username).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists with this username"
            )
        
        user = db.query(BaseUser).filter(BaseUser.email == admin.email).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

        password_hash = get_password_hash(admin.password)
        try:
            admin = BaseUser(
                username=admin.username,
                password_hash=password_hash,
                email=admin.email,
                full_name=admin.full_name,
                user_type=UserTypeEnum.admin
            )

            db.add(admin)
            db.commit()
            db.refresh(admin)

            return AdminCreateResponse(
                success=True,
                message="Admin created successfully"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating admin: {str(e)}"
            )

    @staticmethod
    def get_admin_list(db: Session) -> List[AdminListResponse]:
        admins = db.query(BaseUser).filter(BaseUser.user_type == UserTypeEnum.admin).all()
        return [
            AdminListResponse(
                user_id=admin.user_id,
                username=admin.username,
                email=admin.email,
                full_name=admin.full_name,
                is_active=admin.active_status,
                mfa_enabled=admin.mfa_enabled,
                is_email_verified=admin.is_email_verified,
                locked_until=admin.locked_until
            ) for admin in admins
        ]
    
    @staticmethod
    def update_admin(db: Session, admin_id: int, admin: AdminUpdate) -> AdminUpdateResponse:
        admin_data = db.query(BaseUser).filter(BaseUser.user_id == admin_id).first()
        if not admin_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        if admin.is_active is not None:
            admin_data.active_status = admin.is_active
        if admin.mfa_enabled is not None:
            admin_data.mfa_enabled = admin.mfa_enabled
        if admin.is_email_verified is not None:
            admin_data.is_email_verified = admin.is_email_verified
        if admin.locked_until is not None:
            admin_data.locked_until = admin.locked_until
            admin_data.active_status = False
        elif admin.locked_until is None and admin_data.active_status == False:
            admin_data.active_status = True
            admin_data.locked_until = None

        try:
            db.commit()
            db.refresh(admin_data)
            return AdminUpdateResponse(
                success=True,
                message="Admin updated successfully"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating admin: {str(e)}"
            )