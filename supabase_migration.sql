-- PostgreSQL Migration for SMART Edu Task Manager
-- Run this SQL in Supabase SQL Editor

-- ============================================
-- DROP EXISTING TABLES (ignore errors)
-- ============================================
BEGIN;
DROP TABLE IF EXISTS chat_message CASCADE;
DROP TABLE IF EXISTS chat_room CASCADE;
DROP TABLE IF EXISTS contact_message CASCADE;
DROP TABLE IF EXISTS notification CASCADE;
DROP TABLE IF EXISTS submission CASCADE;
DROP TABLE IF EXISTS assignment CASCADE;
DROP TABLE IF EXISTS task_classes CASCADE;
DROP TABLE IF EXISTS task CASCADE;
DROP TABLE IF EXISTS teacher_class_subjects CASCADE;
DROP TABLE IF EXISTS class_subjects CASCADE;
DROP TABLE IF EXISTS teacher_subjects CASCADE;
DROP TABLE IF EXISTS teacher_classes CASCADE;
DROP TABLE IF EXISTS subject CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS "class" CASCADE;
COMMIT;

-- ============================================
-- DROP ENUM TYPES (ignore errors)
-- ============================================
DROP TYPE IF EXISTS user_type CASCADE;
DROP TYPE IF EXISTS task_priority CASCADE;
DROP TYPE IF EXISTS assignment_status CASCADE;
DROP TYPE IF EXISTS notification_type CASCADE;
DROP TYPE IF EXISTS room_type CASCADE;
DROP TYPE IF EXISTS contact_category CASCADE;

-- ============================================
-- CREATE ENUM TYPES
-- ============================================
CREATE TYPE user_type AS ENUM ('teacher', 'student', 'admin');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE assignment_status AS ENUM ('pending', 'in_progress', 'completed', 'overdue');
CREATE TYPE notification_type AS ENUM ('info', 'success', 'warning', 'error');
CREATE TYPE room_type AS ENUM ('class', 'teacher');
CREATE TYPE contact_category AS ENUM ('general', 'support', 'bug', 'feature', 'partnership');

-- ============================================
-- CREATE TABLES
-- ============================================

-- Classes Table
CREATE TABLE "class" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects Table
CREATE TABLE subject (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    user_type user_type NOT NULL,
    subject VARCHAR(100),
    class_id INTEGER REFERENCES "class"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key for class.created_by
ALTER TABLE "class" ADD CONSTRAINT class_created_by_fkey FOREIGN KEY (created_by) REFERENCES "user"(id);
ALTER TABLE subject ADD CONSTRAINT subject_created_by_fkey FOREIGN KEY (created_by) REFERENCES "user"(id);

-- Teacher-Classes Association Table
CREATE TABLE teacher_classes (
    teacher_id INTEGER REFERENCES "user"(id),
    class_id INTEGER REFERENCES "class"(id),
    PRIMARY KEY (teacher_id, class_id)
);

-- Teacher-Subjects Association Table
CREATE TABLE teacher_subjects (
    teacher_id INTEGER REFERENCES "user"(id),
    subject_id INTEGER REFERENCES subject(id),
    PRIMARY KEY (teacher_id, subject_id)
);

-- Class-Subjects Association Table
CREATE TABLE class_subjects (
    class_id INTEGER REFERENCES "class"(id),
    subject_id INTEGER REFERENCES subject(id),
    PRIMARY KEY (class_id, subject_id)
);

-- Teacher-Class-Subjects Association Table
CREATE TABLE teacher_class_subjects (
    teacher_id INTEGER REFERENCES "user"(id),
    class_id INTEGER REFERENCES "class"(id),
    subject_id INTEGER REFERENCES subject(id),
    PRIMARY KEY (teacher_id, class_id, subject_id)
);

-- Tasks Table
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    deadline TIMESTAMP NOT NULL,
    priority VARCHAR(50) NOT NULL,
    instructions TEXT,
    file_path VARCHAR(500),
    created_by INTEGER REFERENCES "user"(id),
    assigned_teacher_id INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task-Classes Association Table
CREATE TABLE task_classes (
    task_id INTEGER REFERENCES task(id),
    class_id INTEGER REFERENCES "class"(id),
    PRIMARY KEY (task_id, class_id)
);

-- Assignments Table
CREATE TABLE assignment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES task(id),
    student_id INTEGER REFERENCES "user"(id),
    status assignment_status DEFAULT 'pending',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP
);

-- Submissions Table
CREATE TABLE submission (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignment(id),
    content TEXT,
    file_path VARCHAR(500),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER,
    feedback TEXT,
    feedback_provided_at TIMESTAMP,
    graded_by INTEGER REFERENCES "user"(id)
);

-- Notifications Table
CREATE TABLE notification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type notification_type DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Contact Messages Table
CREATE TABLE contact_message (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    category contact_category DEFAULT 'general',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Rooms Table
CREATE TABLE chat_room (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    room_type room_type NOT NULL,
    class_id INTEGER REFERENCES "class"(id),
    created_by INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Chat Messages Table
CREATE TABLE chat_message (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES chat_room(id),
    user_id INTEGER REFERENCES "user"(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- ============================================
-- CREATE INDEXES
-- ============================================
CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_type ON "user"(user_type);
CREATE INDEX idx_user_class ON "user"(class_id);
CREATE INDEX idx_class_name ON "class"(name);
CREATE INDEX idx_task_deadline ON task(deadline);
CREATE INDEX idx_task_priority ON task(priority);
CREATE INDEX idx_task_created_by ON task(created_by);
CREATE INDEX idx_assignment_task ON assignment(task_id);
CREATE INDEX idx_assignment_student ON assignment(student_id);
CREATE INDEX idx_assignment_status ON assignment(status);
CREATE INDEX idx_submission_assignment ON submission(assignment_id);
CREATE INDEX idx_notification_user ON notification(user_id);
CREATE INDEX idx_notification_unread ON notification(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_contact_read ON contact_message(is_read);
CREATE INDEX idx_contact_category ON contact_message(category);
CREATE INDEX idx_room_type ON chat_room(room_type);
CREATE INDEX idx_room_class ON chat_room(class_id);
CREATE INDEX idx_message_room ON chat_message(room_id);
CREATE INDEX idx_message_user ON chat_message(user_id);

-- ============================================
-- SAMPLE DATA
-- ============================================
INSERT INTO "user" (name, email, password_hash, user_type)
VALUES ('Admin', 'admin@smartedu.com', 'pbkdf2:sha256:260000$w7O1$hash$placeholder', 'admin')
ON CONFLICT (email) DO NOTHING;
