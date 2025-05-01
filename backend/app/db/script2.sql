BEGIN;
-- ENUM types
CREATE TYPE user_type_enum AS ENUM ('admin', 'super_admin', 'instructor', 'student', 'system');
CREATE TYPE attendance_status_enum AS ENUM ('present', 'absent', 'excused', 'late');
CREATE TYPE session_status_enum AS ENUM ('scheduled', 'completed', 'ongoing', 'cancelled');
CREATE TYPE verification_method_enum AS ENUM ('facial', 'manual_override');
CREATE TYPE audit_status_enum AS ENUM ('success', 'failure', 'warning', 'info');
CREATE TYPE action_type_enum AS ENUM (
    -- Authentication actions
    'sign_in', 
    'sign_out',
    'failed_login',
    'password_change',
    'password_reset',
    'mfa_setup',
    'mfa_verification',
    
    -- User management actions
    'created_user', 
    'updated_user', 
    'deleted_user',
    'locked_user',
    'unlocked_user',
    'email_verified',
    
    -- Role/permission actions
    'granted_role',
    'revoked_role',
    'granted_permission',
    'revoked_permission',
    
    -- Course actions
    'created_course',
    'updated_course',
    'deleted_course',
    'enrolled_student',
    'unenrolled_student',
    'assigned_instructor',
    'unassigned_instructor',
    
    -- Attendance actions
    'created_session',
    'started_session',
    'ended_session',
    'cancelled_session',
    'marked_attendance',
    'modified_attendance',
    
    -- Facial recognition actions
    'facial_data_submitted',
    'facial_data_validated',
    'facial_data_rejected',
    'facial_verification_success',
    'facial_verification_failure',
    
    -- System actions
    'configuration_change',
    'data_export',
    'report_generation'
);

-- Base User 
CREATE TABLE base_user (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    user_type user_type_enum NOT NULL,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    totp_secret VARCHAR(255),
    is_email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by INTEGER,
    last_activity TIMESTAMP WITHOUT TIME ZONE,
    active_status BOOLEAN DEFAULT TRUE NOT NULL,
    login_attempts INTEGER DEFAULT 0 NOT NULL,
    locked_until TIMESTAMP WITHOUT TIME ZONE,
    deleted_at TIMESTAMP WITHOUT TIME ZONE, 
    deleted_by INTEGER,

    -- Foreign Key constraints
    FOREIGN KEY (created_by) REFERENCES base_user(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (updated_by) REFERENCES base_user(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (deleted_by) REFERENCES base_user(user_id) ON DELETE RESTRICT
);

CREATE TABLE role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER NOT NULL REFERENCES base_user(user_id),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by INTEGER NOT NULL REFERENCES base_user(user_id),
    deleted_at TIMESTAMP WITHOUT TIME ZONE,
    deleted_by INTEGER REFERENCES base_user(user_id) 
);

CREATE TABLE permission (
    permission_id SERIAL PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER NOT NULL REFERENCES base_user(user_id),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by INTEGER NOT NULL REFERENCES base_user(user_id),
    deleted_at TIMESTAMP WITHOUT TIME ZONE,
    deleted_by INTEGER REFERENCES base_user(user_id)
);

-- Role permissions junction
CREATE TABLE role_permission (
    role_id INTEGER NOT NULL REFERENCES role(role_id),
    permission_id INTEGER NOT NULL REFERENCES permission(permission_id),
    granted_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    granted_by INTEGER NOT NULL REFERENCES base_user(user_id),
    revoked_at TIMESTAMP WITHOUT TIME ZONE,
    revoked_by INTEGER REFERENCES base_user(user_id),
    PRIMARY KEY (role_id, permission_id)
);

-- User roles junction table
CREATE TABLE user_role (
    user_id INTEGER NOT NULL REFERENCES base_user(user_id),
    role_id INTEGER NOT NULL REFERENCES role(role_id),
    granted_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    granted_by INTEGER NOT NULL REFERENCES base_user(user_id),
    revoked_at TIMESTAMP WITHOUT TIME ZONE,
    revoked_by INTEGER REFERENCES base_user(user_id),
    PRIMARY KEY (user_id, role_id)
);

-- Admin table - extends base_user
CREATE TABLE admin (
    admin_id INTEGER PRIMARY KEY REFERENCES base_user(user_id) ON DELETE CASCADE,
    department VARCHAR(100) NOT NULL
);

-- Instructor Table - extends base_user
CREATE TABLE instructor (
    teacher_id INTEGER PRIMARY KEY REFERENCES base_user(user_id) ON DELETE CASCADE,
    department VARCHAR(100) NOT NULL,
    qualification TEXT,
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    hire_date TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);

-- Student Table - extends base_user
CREATE TABLE student (
    student_id INTEGER PRIMARY KEY REFERENCES base_user(user_id) ON DELETE CASCADE,
    enrollment_number VARCHAR(50) UNIQUE NOT NULL,
    program VARCHAR(100) NOT NULL,
    batch_year INTEGER NOT NULL,
    graduation_year INTEGER
);

-- Course Table 
CREATE TABLE course (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    credits INTEGER NOT NULL,
    department VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER NOT NULL REFERENCES base_user(user_id),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by INTEGER NOT NULL REFERENCES base_user(user_id),
    deleted_at TIMESTAMP WITHOUT TIME ZONE,
    deleted_by INTEGER REFERENCES base_user(user_id),
    active_status BOOLEAN DEFAULT TRUE NOT NULL
);

-- Course Instructor relationship table
CREATE TABLE course_instructor (
    course_teacher_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    instructor_id INTEGER NOT NULL REFERENCES instructor(teacher_id) ON DELETE CASCADE,
    academic_term VARCHAR(20) NOT NULL,
    academic_year VARCHAR(9) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER NOT NULL REFERENCES base_user(user_id),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by INTEGER NOT NULL REFERENCES base_user(user_id),
    deleted_at TIMESTAMP WITHOUT TIME ZONE,
    deleted_by INTEGER REFERENCES base_user(user_id),
    UNIQUE(course_id, instructor_id, academic_term, academic_year)
);

-- Course student relationship table
CREATE TABLE course_student (
    course_student_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    academic_term VARCHAR(20) NOT NULL,
    academic_year VARCHAR(9) NOT NULL,
    enrollment_date TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    status VARCHAR(40) DEFAULT 'active',
    validated_at TIMESTAMP WITHOUT TIME ZONE,
    validated_by INTEGER REFERENCES base_user(user_id),
    UNIQUE(course_id, student_id, academic_term, academic_year)
);

-- Attendance Session table 
CREATE TABLE attendance_session (
    session_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    instructor_id INTEGER NOT NULL REFERENCES instructor(teacher_id) ON DELETE CASCADE,
    session_start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    session_end_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    location VARCHAR(100),
    session_type VARCHAR(50),
    status session_status_enum DEFAULT 'scheduled',
    verification_window_minutes INTEGER DEFAULT 20,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER NOT NULL REFERENCES base_user(user_id),
    deleted_at TIMESTAMP WITHOUT TIME ZONE,
    deleted_by INTEGER REFERENCES base_user(user_id),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by INTEGER NOT NULL REFERENCES base_user(user_id),
    UNIQUE(course_id, instructor_id, session_start_time, session_end_time)
);

-- attendance_record table with audit fields
CREATE TABLE attendance_record (
    record_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES attendance_session(session_id),
    student_id INTEGER REFERENCES student(student_id),
    status attendance_status_enum NOT NULL,
    verification_method verification_method_enum,
    verification_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    confidence_score DECIMAL(5, 2),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER NOT NULL REFERENCES base_user(user_id),
    UNIQUE(session_id, student_id)
);

-- Facial embeddings table
CREATE TABLE facial_embedding (
    embedding_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    encrypted_embedding BYTEA NOT NULL,
    encryption_iv BYTEA NOT NULL,
    variant_label VARCHAR(50) DEFAULT 'frontal',
    confidence_score DECIMAL(5, 2),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER NOT NULL REFERENCES base_user(user_id),
    validated_at TIMESTAMP WITHOUT TIME ZONE,
    validated_by INTEGER REFERENCES base_user(user_id),
    CHECK (confidence_score >= 0 AND confidence_score <= 100)
);

-- audit log table
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    user_id INTEGER REFERENCES base_user(user_id),
    ip_address VARCHAR(45),
    user_agent TEXT,
    action action_type_enum NOT NULL,
    action_category VARCHAR(50) NOT NULL,
    status audit_status_enum NOT NULL DEFAULT 'success',
    details TEXT
);

-- Notification table
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES base_user(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);

-- Creating the super admin user
-- Temporarily disable foreign key constraints to handle circular dependency
ALTER TABLE base_user DISABLE TRIGGER ALL;

-- Insert super admin user with NULL for created_by, updated_by
INSERT INTO base_user (
    username, 
    password_hash, 
    password_salt, 
    email, 
    full_name, 
    user_type, 
    mfa_enabled,
    is_email_verified,
    created_at,
    updated_at,
    active_status
) VALUES (
    'superadmin',
    '$2a$12$1InE4AoCzMmh3kPGsE2W6.BVT9iqXMvzYVFYy8A61tGYUef/uVyG2', -- This is a bcrypt hash for 'Admin@123' - change in production
    'randomsalt123456789',
    'superadmin@example.com',
    'Super Administrator',
    'super_admin',
    TRUE,
    TRUE,
    NOW(),
    NOW(),
    TRUE
) RETURNING user_id;

-- Create admin record for super admin
INSERT INTO admin (admin_id, department)
SELECT 
    user_id,
    'System Administration'
FROM base_user
WHERE username = 'superadmin';

-- Re-enable foreign key constraints
ALTER TABLE base_user ENABLE TRIGGER ALL;

-- Update the super admin user to reference itself for created_by and updated_by
UPDATE base_user
SET created_by = user_id, updated_by = user_id
WHERE username = 'superadmin';

-- Create basic roles
INSERT INTO role (role_name, description, created_by, updated_by)
SELECT 'Super Admin', 'Has complete control over the system', user_id, user_id
FROM base_user WHERE username = 'superadmin';

INSERT INTO role (role_name, description, created_by, updated_by)
SELECT 'Admin', 'Can manage users, courses, and view reports', user_id, user_id
FROM base_user WHERE username = 'superadmin';

INSERT INTO role (role_name, description, created_by, updated_by)
SELECT 'Instructor', 'Can manage attendance and view reports for assigned courses', user_id, user_id
FROM base_user WHERE username = 'superadmin';

INSERT INTO role (role_name, description, created_by, updated_by)
SELECT 'Student', 'Can view their own attendance and register for courses', user_id, user_id
FROM base_user WHERE username = 'superadmin';

-- Assign super admin role to the super admin user
INSERT INTO user_role (user_id, role_id, granted_by)
SELECT u.user_id, r.role_id, u.user_id
FROM base_user u, role r
WHERE u.username = 'superadmin' AND r.role_name = 'Super Admin';

COMMIT;