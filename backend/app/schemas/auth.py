"""
This file contains authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    requires_mfa: bool = False
    user_id: Optional[int] = None

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

