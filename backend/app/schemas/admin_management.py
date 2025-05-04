from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone
from ..utils.security import is_strong_password

class AdminBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr = Field(..., max_length=100)

    @field_validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    admin_creation_token: str

    @field_validator('password')
    def validate_password(cls, v):
        if not is_strong_password(v):
            raise ValueError('Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character')
        return v

class AdminUpdate(BaseModel):
    is_active: Optional[bool] = Field(None, description="Admin account active status")
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

class AdminListResponse(BaseModel):
    user_id: Optional[int] = Field(None, description="Admin user ID")
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = Field(None, description="Admin account active status")
    mfa_enabled: Optional[bool] = Field(None, description="Multi-factor authentication status")
    is_email_verified: Optional[bool] = Field(None, description="Email verification status")
    locked_until: Optional[datetime] = Field(None, description="Account lock expiry time")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class AdminCreateResponse(BaseModel):
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., min_length=1, max_length=500, description="Response message")

class AdminUpdateResponse(AdminCreateResponse):
    pass 