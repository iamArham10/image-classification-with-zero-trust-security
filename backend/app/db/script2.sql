BEGIN;

-- ENUM types
CREATE TYPE user_type_enum AS ENUM ('admin', 'user', 'guest');
CREATE TYPE classification_status_enum AS ENUM ('success', 'failed', 'error');
CREATE TYPE audit_status_enum AS ENUM ('success', 'failure', 'warning', 'info');
CREATE TYPE action_type_enum AS ENUM (
    -- Authentication actions
    'sign_in',
    'sign_out',
    'failed_login',
    'password_change',
    'mfa_verification',

    -- User management actions
    'created_user',
    'updated_user',
    'deleted_user',
    'locked_user',
    'unlocked_user',

    -- Classification actions
    'image_upload',
    'image_validated',
    'image_rejected',
    'classification_success',
    'classification_failure'
);

-- User table
CREATE TABLE base_user (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    user_type user_type_enum NOT NULL,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    totp_secret VARCHAR(255),
    active_status BOOLEAN DEFAULT TRUE NOT NULL,
    login_attempts INTEGER DEFAULT 0 NOT NULL,
    locked_until TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITHOUT TIME ZONE,
    last_activity TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    is_email_verified BOOLEAN DEFAULT FALSE
);

-- Simple role system
CREATE TABLE role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- User roles junction table
CREATE TABLE user_role (
    user_id INTEGER NOT NULL REFERENCES base_user(user_id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES role(role_id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    granted_by INTEGER NOT NULL REFERENCES base_user(user_id),
    PRIMARY KEY (user_id, role_id)
);

-- Image Classification table
CREATE TABLE image_classification (
    classification_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES base_user(user_id) ON DELETE CASCADE,
    image_hash VARCHAR(64) NOT NULL,
    image_path VARCHAR(255),
    original_filename VARCHAR(255),
    file_size INTEGER NOT NULL,
    classification_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    top_prediction VARCHAR(100),
    confidence_score DECIMAL(5, 2),
    process_time_ms INTEGER,
    status classification_status_enum NOT NULL,
    ip_address VARCHAR(45)
);

-- Classification results detail table
CREATE TABLE classification_result (
    result_id SERIAL PRIMARY KEY,
    classification_id INTEGER NOT NULL REFERENCES image_classification(classification_id) ON DELETE CASCADE,
    class_name VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(5, 2) NOT NULL,
    rank INTEGER NOT NULL
);

-- Audit log for zero trust monitoring
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    user_id INTEGER REFERENCES base_user(user_id) ON DELETE SET NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    action action_type_enum NOT NULL,
    resource VARCHAR(100), -- What resource was accessed
    status audit_status_enum NOT NULL DEFAULT 'success',
    details TEXT
);

COMMIT;
