from sqlalchemy.orm import Session
from ..schemas.user_management import UserUpdate, UserUpdateResponse, UserListResponse
from ..models.base_user import BaseUser
from fastapi import HTTPException, status
from ..models.enums import UserTypeEnum
from typing import List

class UserManagementService:

    @staticmethod
    def update_user(db: Session, user_id: int, user: UserUpdate) -> UserUpdateResponse:
        user_data = db.query(BaseUser).filter(BaseUser.user_id == user_id).first()
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_active is not None:
            user_data.active_status = user.is_active
        if user.mfa_enabled is not None:
            user_data.mfa_enabled = user.mfa_enabled
        if user.is_email_verified is not None:
            user_data.is_email_verified = user.is_email_verified
        if user.locked_until is not None:
            user_data.locked_until = user.locked_until
            user_data.active_status = False
        elif user.locked_until is None and user_data.active_status == False:
            user_data.active_status = True
            user_data.locked_until = None
        
        try:
            db.commit()
            db.refresh(user_data)
            return UserUpdateResponse(
                success=True,
                message="User updated successfully"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user: {str(e)}"
            )
        
    @staticmethod
    def get_user_list(db: Session) -> List[UserListResponse]:
        users = db.query(BaseUser).filter(BaseUser.user_type == UserTypeEnum.user).all()
        return [
            UserListResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                mfa_enabled=user.mfa_enabled,
                is_email_verified=user.is_email_verified,
                is_active=user.active_status,
                locked_until=user.locked_until,
            ) for user in users
        ]