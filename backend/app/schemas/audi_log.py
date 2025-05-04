from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AuditLogUserInfo(BaseModel):
    username: Optional[str] = None
    user_type: Optional[str] = None

class AuditLog(BaseModel):
    user_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    action: str
    resource: str
    status: str
    details: str
    user_info: Optional[AuditLogUserInfo] = None

class AuditLogResponseList(BaseModel):
    content: List[AuditLog]
    total_count: int
