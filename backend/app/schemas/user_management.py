from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
from ..utils.security import is_strong_password

class UserUpdate(BaseModel):
    is_active: Optional[bool] = Field(None, description="User account active status")
    mfa_enabled: Optional[bool] = Field(None, description="Multi-factor authentication status")
    is_email_verified: Optional[bool] = Field(None, description="Email verification status")
    locked_until: Optional[datetime] = Field(None, description="Account lock expiry time")

    @field_validator('locked_until')
    def validate_locked_until(cls, v):
        if v:
            # Convert to UTC if timezone-aware, or assume UTC if naive
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)
            if v < current_time:
                raise ValueError('Lock expiry time must be in the future')
        return v
    
class UserListResponse(BaseModel):
    user_id: Optional[int] = Field(None, description="User ID")
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    mfa_enabled: Optional[bool] = Field(None, description="Multi-factor authentication status")
    is_email_verified: Optional[bool] = Field(None, description="Email verification status")
    is_active: Optional[bool] = Field(None, description="User account active status")
    locked_until: Optional[datetime] = Field(None, description="Account lock expiry time")

class UserUpdateResponse(BaseModel):
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., min_length=1, max_length=500, description="Response message")
