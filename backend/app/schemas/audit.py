from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AuditStatusEnum(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"

class ActionTypeEnum(str, Enum):
    # Authentication actions
    SIGN_IN = "sign_in"
    SIGN_OUT = "sign_out"
    FAILED_LOGIN = "failed_login"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    MFA_SETUP = "mfa_setup"
    MFA_VERIFICATION = "mfa_verification"

    # User management actions
    CREATED_USER = "created_user"
    UPDATED_USER = "updated_user"
    DELETED_USER = "deleted_user"
    LOCKED_USER = "locked_user"
    UNLOCKED_USER = "unlocked_user"
    EMAIL_VERIFIED = "email_verified"
    
    # Role/Permission actions
    
    
