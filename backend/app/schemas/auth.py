"""
This file contains authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from pydantic import field_validator as validator

class UserSignup(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    requires_mfa: bool = False
    user_type: str = 'guest'
    user_id: Optional[int] = None
    is_email_verified: bool = False

class MFAVerify(BaseModel):
    user_id: int
    token: str

class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class EmailVerify(BaseModel):
    code: str

class UserSignupResponse(BaseModel):
    success: bool
    message: str