
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.sql import func
from ..models.audit_log import AuditLog
from ..models.base_user import BaseUser
from ..schemas.audi_log import AuditLogResponseList, AuditLog as AuditLogSchema, AuditLogUserInfo
from ..models.enums import ActionTypeEnum, AuditStatusEnum

def add_audit_log(
    db: Session,
    action: ActionTypeEnum,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    resource: Optional[str] = None,
    status: AuditStatusEnum = AuditStatusEnum.success,
    details: Optional[str] = None
) -> AuditLog:

    audit_log = AuditLog(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        action=action,
        resource=resource,
        status=status,
        details=details
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log

def get_audit_logs(db: Session, limit: int, offset: int) -> AuditLogResponseList:

    total_count = db.query(AuditLog).count()
    
    audit_logs = db.query(AuditLog, BaseUser)\
        .outerjoin(BaseUser, AuditLog.user_id == BaseUser.user_id)\
        .order_by(AuditLog.timestamp.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    content = [
        AuditLogSchema(
            user_id=str(log.AuditLog.user_id) if log.AuditLog.user_id else "Unknown",
            timestamp=log.AuditLog.timestamp,
            ip_address=log.AuditLog.ip_address if log.AuditLog.ip_address else "Unknown",
            user_agent=log.AuditLog.user_agent if log.AuditLog.user_agent else "Unknown",
            action=log.AuditLog.action.value,
            resource=log.AuditLog.resource if log.AuditLog.resource else "Unknown",
            status=log.AuditLog.status.value,
            details=log.AuditLog.details if log.AuditLog.details else "No details available",
            user_info=AuditLogUserInfo(
                username=log.BaseUser.username if log.BaseUser else None,
                user_type=log.BaseUser.user_type.value if log.BaseUser else None
            ) if log.BaseUser else None
        ) for log in audit_logs
    ]
    
    return AuditLogResponseList(
        content=content,
        total_count=total_count
    )

    