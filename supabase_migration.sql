-- PostgreSQL Migration for SMART Edu Task Manager
-- Run this SQL in Supabase SQL Editor

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUM TYPES
-- ============================================
DO $$ BEGIN
    CREATE TYPE user_type AS ENUM ('teacher', 'student', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE assignment_status AS ENUM ('pending', 'in_progress', 'completed', 'overdue');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM ('info', 'success', 'warning', 'error');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE room_type AS ENUM ('class', 'teacher');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE contact_category AS ENUM ('general', 'support', 'bug', 'feature', 'partnership');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- TABLES
-- ============================================

-- Users Table
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    user_type user_type NOT NULL,
    subject VARCHAR(100),
    class_id INTEGER REFERENCES "class"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS idx_user_type ON "user"(user_type);
CREATE INDEX IF NOT EXISTS idx_user_class ON "user"(class_id);

-- Classes Table
CREATE TABLE IF NOT EXISTS "class" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES "user"(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_class_name ON "class"(name);

-- Subjects Table
CREATE TABLE IF NOT EXISTS subject (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES "user"(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teacher-Classes Association Table
CREATE TABLE IF NOT EXISTS teacher_classes (
    teacher_id INTEGER REFERENCES "user"(id) NOT NULL,
    class_id INTEGER REFERENCES "class"(id) NOT NULL,
    PRIMARY KEY (teacher_id, class_id)
);

-- Teacher-Subjects Association Table
CREATE TABLE IF NOT EXISTS teacher_subjects (
    teacher_id INTEGER REFERENCES "user"(id) NOT NULL,
    subject_id INTEGER REFERENCES subject(id) NOT NULL,
    PRIMARY KEY (teacher_id, subject_id)
);

-- Class-Subjects Association Table
CREATE TABLE IF NOT EXISTS class_subjects (
    class_id INTEGER REFERENCES "class"(id) NOT NULL,
    subject_id INTEGER REFERENCES subject(id) NOT NULL,
    PRIMARY KEY (class_id, subject_id)
);

-- Teacher-Class-Subjects Association Table
CREATE TABLE IF NOT EXISTS teacher_class_subjects (
    teacher_id INTEGER REFERENCES "user"(id) NOT NULL,
    class_id INTEGER REFERENCES "class"(id) NOT NULL,
    subject_id INTEGER REFERENCES subject(id) NOT NULL,
    PRIMARY KEY (teacher_id, class_id, subject_id)
);

-- Tasks Table
CREATE TABLE IF NOT EXISTS task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    deadline TIMESTAMP NOT NULL,
    priority VARCHAR(50) NOT NULL,
    instructions TEXT,
    file_path VARCHAR(500),
    created_by INTEGER REFERENCES "user"(id) NOT NULL,
    assigned_teacher_id INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_task_deadline ON task(deadline);
CREATE INDEX IF NOT EXISTS idx_task_priority ON task(priority);
CREATE INDEX IF NOT EXISTS idx_task_created_by ON task(created_by);

-- Task-Classes Association Table
CREATE TABLE IF NOT EXISTS task_classes (
    task_id INTEGER REFERENCES task(id) NOT NULL,
    class_id INTEGER REFERENCES "class"(id) NOT NULL,
    PRIMARY KEY (task_id, class_id)
);

-- Assignments Table
CREATE TABLE IF NOT EXISTS assignment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES task(id) NOT NULL,
    student_id INTEGER REFERENCES "user"(id) NOT NULL,
    status assignment_status DEFAULT 'pending',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_assignment_task ON assignment(task_id);
CREATE INDEX IF NOT EXISTS idx_assignment_student ON assignment(student_id);
CREATE INDEX IF NOT EXISTS idx_assignment_status ON assignment(status);

-- Submissions Table
CREATE TABLE IF NOT EXISTS submission (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignment(id) NOT NULL,
    content TEXT,
    file_path VARCHAR(500),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER,
    feedback TEXT,
    feedback_provided_at TIMESTAMP,
    graded_by INTEGER REFERENCES "user"(id)
);

CREATE INDEX IF NOT EXISTS idx_submission_assignment ON submission(assignment_id);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type notification_type DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notification_user ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_unread ON notification(user_id, is_read) WHERE is_read = FALSE;

-- Contact Messages Table
CREATE TABLE IF NOT EXISTS contact_message (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    category contact_category DEFAULT 'general',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contact_read ON contact_message(is_read);
CREATE INDEX IF NOT EXISTS idx_contact_category ON contact_message(category);

-- Chat Rooms Table
CREATE TABLE IF NOT EXISTS chat_room (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    room_type room_type NOT NULL,
    class_id INTEGER REFERENCES "class"(id),
    created_by INTEGER REFERENCES "user"(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_room_type ON chat_room(room_type);
CREATE INDEX IF NOT EXISTS idx_room_class ON chat_room(class_id);

-- Chat Messages Table
CREATE TABLE IF NOT EXISTS chat_message (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES chat_room(id) NOT NULL,
    user_id INTEGER REFERENCES "user"(id) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_message_room ON chat_message(room_id);
CREATE INDEX IF NOT EXISTS idx_message_user ON chat_message(user_id);

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Create a sample admin user (password: admin123)
-- Note: The password hash is generated with werkzeug.security
INSERT INTO "user" (name, email, password_hash, user_type)
VALUES ('Admin', 'admin@smartedu.com', 'pbkdf2:sha256:260000$w7O1$hash$placeholder', 'admin')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- FUNCTIONS & TRIGGERS (Optional)
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================
-- ROW LEVEL SECURITY (Optional - for Supabase)
-- ============================================

ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE task ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignment ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification ENABLE ROW LEVEL SECURITY;

-- Note: RLS policies should be configured based on your security requirements
