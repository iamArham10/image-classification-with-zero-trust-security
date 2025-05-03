import enum

class UserTypeEnum(str, enum.Enum):
    admin = 'admin'
    user = 'user'
    guest = 'guest'

class ClassificationStatusEnum(str, enum.Enum):
    success = 'success'
    failed  = 'failed'
    error = 'error'

class AuditStatusEnum(str, enum.Enum):
    success = 'success'
    failure = 'failure'
    warning = 'warning'
    info = 'info'
    
class ActionTypeEnum(str, enum.Enum):
    sign_in = 'sign_in'
    sign_out = 'sign_out'
    failed_login = 'failed_login'
    password_change = 'password_change'
    mfa_verification = 'mfa_verification'

    created_user = 'created_user'
    updated_user = 'updated_user'
    deleted_user = 'deleted_user'
    locked_user = 'locked_user'
    unlocked_user = 'unlocked_user'

    image_upload = 'image_upload'
    image_validated = 'image_validated'
    image_rejected = 'image_rejected'
    classification_success = 'classification_success'
    classification_failure = 'classification_failure'
