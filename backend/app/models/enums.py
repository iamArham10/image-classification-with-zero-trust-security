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
    sign_up = 'sign_up'
    sign_in = 'sign_in'
    login = 'login'
    sign_out = 'sign_out'
    mfa_verify = 'mfa_verify'
    mfa_setup = 'mfa_setup'
    email_verify = 'email_verify'
    password_change = 'password_change'
    mfa_verification = 'mfa_verification'

    created_user = 'created_user'
    updated_user = 'updated_user'
    deleted_user = 'deleted_user'
    locked_user = 'locked_user'
    unlocked_user = 'unlocked_user'
    admin_create = 'admin_create'
    admin_list = 'admin_list'
    user_list = 'user_list'

    image_upload = 'image_upload'
    image_validated = 'image_validated'
    image_rejected = 'image_rejected'
    image_retrieval = 'image_retrieval'
    classification_success = 'classification_success'
    classification_failure = 'classification_failure'
    classification_history = 'classification_history'
    admin_classification_history = 'admin_classification_history'

    # to insert into database
    audit_log_retrieval = 'audit_log_retrieval'
