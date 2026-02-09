# SMART Edu Task Manager - Database Design

## Database Overview
The SMART Edu Task Manager uses SQLite as its primary database with SQLAlchemy ORM for data persistence. The database design follows a normalized structure to maintain data integrity and minimize redundancy.

## Features

### For Administrators
- System-wide user management (view, create, edit, delete users)
- Task management and oversight
- System analytics and reporting
- Notification system management
- Data export functionality
- System statistics and monitoring

### For Teachers
- Create tasks with detailed descriptions and deadlines
- Assign tasks to individual students or classes during creation
- Monitor student progress in real-time
- View comprehensive student performance overview
- Automatic priority suggestions using ML
- Review and manage student submissions

### For Students
- View assigned tasks sorted by priority and deadline
- Update task status (start, submit)
- Submit work through the platform
- Focus on high-priority tasks
- Receive notifications about assignments and updates
- Access notification center for updates

### Notification System
- Real-time in-app notifications
- System-wide announcements from admins
- Notification center with read/unread status
- Task assignment notifications
- Deadline reminders

### Machine Learning Integration
- Automatic task priority classification based on description
- Uses scikit-learn for text analysis and prediction

## Database Schema

### 1. User Table
**Purpose:** Stores all user information for teachers and students

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| name | VARCHAR(100) | NOT NULL | User's full name |
| email | VARCHAR(120) | NOT NULL, UNIQUE | User's email address (login identifier) |
| password_hash | VARCHAR(128) | NOT NULL | Hashed password for security |
| user_type | VARCHAR(20) | NOT NULL | 'teacher' or 'student' |
| subject | VARCHAR(100) | NULL | Subject taught (teachers only) |
| class_name | VARCHAR(100) | NULL | Class name (students only) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Relationships:**
- One User → Many Tasks (as creator)
- One User → Many Assignments (as student)
- One User → Many Submissions (through assignments)

### 2. Task Table
**Purpose:** Stores task details created by teachers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| title | VARCHAR(200) | NOT NULL | Task title/name |
| description | TEXT | NOT NULL | Detailed task description |
| deadline | DATETIME | NOT NULL | Task due date and time |
| priority | VARCHAR(50) | NOT NULL | Task priority level |
| instructions | TEXT | NULL | Additional instructions |
| file_path | VARCHAR(500) | NULL | Path to uploaded task file |
| created_by | INTEGER | NOT NULL, FOREIGN KEY | ID of creating teacher |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |

**Relationships:**
- Many Tasks → One User (creator)
- One Task → Many Assignments
- One Task → Many Submissions (through assignments)

**Priority Values:**
- `urgent_important` - Urgent & Important
- `important_not_urgent` - Important but Not Urgent
- `urgent_not_important` - Urgent but Not Important
- `not_important_not_urgent` - Not Important & Not Urgent
- `high_priority` - High Priority (High Marks/Major Assignment)
- `medium_priority` - Medium Priority
- `low_priority` - Low Priority
- `optional` - Optional/Extra Work
- `long_term` - Long-term Project
- `group_task` - Group Task

### 3. Assignment Table
**Purpose:** Links tasks to students (many-to-many relationship)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique assignment identifier |
| task_id | INTEGER | NOT NULL, FOREIGN KEY | Referenced task ID |
| student_id | INTEGER | NOT NULL, FOREIGN KEY | Assigned student ID |
| status | VARCHAR(20) | DEFAULT 'pending' | Assignment status |
| assigned_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Assignment creation timestamp |
| submitted_at | DATETIME | NULL | Submission timestamp |

**Relationships:**
- Many Assignments → One Task
- Many Assignments → One Student
- One Assignment → Many Submissions

**Status Values:**
- `pending` - Not started
- `in_progress` - Work in progress
- `completed` - Task submitted
- `overdue` - Past deadline (auto-calculated)

### 4. Submission Table
**Purpose:** Stores student task submissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique submission identifier |
| assignment_id | INTEGER | NOT NULL, FOREIGN KEY | Related assignment ID |
| content | TEXT | NULL | Text-based submission content |
| file_path | VARCHAR(500) | NULL | Path to submitted file |
| submitted_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Submission timestamp |

**Relationships:**
- Many Submissions → One Assignment

### 5. Notification Table
**Purpose:** Stores system and user notifications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique notification identifier |
| user_id | INTEGER | NOT NULL, FOREIGN KEY | Target user ID |
| title | VARCHAR(200) | NOT NULL | Notification title |
| message | TEXT | NOT NULL | Notification message content |
| notification_type | VARCHAR(50) | NOT NULL, DEFAULT 'info' | Type: info, success, warning, error |
| is_read | BOOLEAN | DEFAULT FALSE | Read status |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| expires_at | DATETIME | NULL | Optional expiration time |

**Relationships:**
- Many Notifications → One User

**Notification Types:**
- `info` - General information
- `success` - Success messages
- `warning` - Warning messages
- `error` - Error messages

## Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    USER     │     │    TASK     │     │ ASSIGNMENT  │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │────►│ id (PK)     │◄────│ id (PK)     │
│ name        │     │ title       │     │ task_id (FK)│
│ email       │     │ description │     │ student_id(FK)│
│ user_type   │     │ deadline    │     │ status      │
│ subject     │     │ priority    │     │ assigned_at │
│ class_name  │     │ created_by(FK)│   │ submitted_at│
│ created_at  │     │ created_at  │     └─────────────┘
└─────────────┘     └─────────────┘              │
        │                   │                    │
        ▼                   ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   TEACHER   │     │  CREATOR    │     │ SUBMISSION  │
│ (subset)    │     │ (role)      │     ├─────────────┤
├─────────────┤     └─────────────┘     │ id (PK)     │
│ user_type=  │                         │ assignment_id│
│ 'teacher'   │                         │ content      │
└─────────────┘                         │ file_path    │
                                         │ submitted_at │
┌─────────────┐                         └─────────────┘
│   STUDENT   │
│ (subset)    │
├─────────────┤
│ user_type=  │
│ 'student'   │
└─────────────┘
        │
        ▼
┌─────────────┐
│ NOTIFICATION│
├─────────────┤
│ id (PK)     │
│ user_id (FK)│
│ title       │
│ message     │
│ type        │
│ is_read     │
│ created_at  │
│ expires_at  │
└─────────────┘
```

## Database Relationships

### 1. One-to-Many Relationships
- **User → Tasks:** One teacher can create many tasks
- **User → Assignments:** One student can have many assignments
- **Task → Assignments:** One task can be assigned to many students
- **Assignment → Submissions:** One assignment can have multiple submissions (versions)
- **User → Notifications:** One user can receive many notifications

### 2. Many-to-Many Relationships
- **Teachers ↔ Students:** Through tasks and assignments
- **Tasks ↔ Students:** Through assignments

### 3. Referential Integrity
- Foreign key constraints ensure data consistency
- Cascade delete operations maintain referential integrity
- Unique constraints prevent duplicate data

## Database Indexes

### Primary Indexes
- `user.id` - Primary key
- `task.id` - Primary key
- `assignment.id` - Primary key
- `submission.id` - Primary key

### Foreign Key Indexes (for performance)
- `task.created_by` - Index on creator
- `assignment.task_id` - Index on task
- `assignment.student_id` - Index on student
- `submission.assignment_id` - Index on assignment

### Unique Indexes
- `user.email` - Unique email constraint

### Query Optimization Indexes
- `assignment.status` - For filtering by status
- `task.deadline` - For deadline queries
- `assignment.submitted_at` - For submission tracking

## Data Integrity Constraints

### 1. Check Constraints
- `user_type` must be 'teacher' or 'student'
- `priority` must be one of the defined priority values
- `status` must be one of the defined status values

### 2. Not Null Constraints
- All required fields marked as NOT NULL
- Foreign key relationships enforced

### 3. Business Rules
- Students cannot create tasks
- Teachers can only modify their own tasks
- Students can only submit to their own assignments

## File Storage Design

### File Organization
```
/uploads/
├── {uuid}_task_{original_name}    # Task files
├── {uuid}_submission_{original_name} # Submission files
└── {uuid}_user_{original_name}    # User profile files (future)
```

### File Naming Convention
- **UUID prefix:** Ensures unique filenames
- **Descriptive suffix:** Original filename for user recognition
- **Type indicator:** Task/Submission/User prefix

### Security Measures
- File type validation
- Size limits (20MB for tasks, 10MB for submissions)
- Path traversal prevention
- Unique naming to prevent conflicts

## Database Migrations

### Migration Strategy
- SQLAlchemy Alembic for schema versioning
- Version control for database changes
- Rollback capability for failed migrations

### Future Migration Considerations
- Adding notification tables
- Implementing audit logs
- Adding user preferences
- Creating report views

## Performance Considerations

### Query Optimization
- Efficient JOIN operations
- Indexed foreign keys
- Paginated results for large datasets

### Caching Strategy (Future)
- User session caching
- Task progress caching
- Database query result caching

### Scaling Preparation
- Database connection pooling
- Read replicas for reporting
- Sharding strategy for large datasets

## Backup and Recovery

### Backup Strategy
- Regular database file backups
- Incremental backup system
- File system backup for uploads

### Recovery Procedures
- Database restoration process
- File recovery procedures
- Data consistency checks

## Security Considerations

### Data Protection
- Password hashing (no plain text storage)
- SQL injection prevention (ORM usage)
- XSS protection (template escaping)

### Access Control
- Row-level security (user data isolation)
- Role-based permissions
- Session-based authentication

### Audit Trail (Future)
- User action logging
- Data modification tracking
- Security event monitoring

## Database Configuration

### SQLite Configuration
- WAL mode for better concurrency
- Foreign key enforcement enabled
- Optimized cache size

### Connection Management
- SQLAlchemy connection pooling
- Transaction management
- Connection timeout settings

## Monitoring and Maintenance

### Health Checks
- Database connectivity tests
- Table integrity verification
- Index usage analysis

### Maintenance Tasks
- Regular vacuum operations
- Index rebuilding
- Statistics updates

### Performance Monitoring
- Query execution time tracking
- Slow query identification
- Database size monitoring

---

## Additional Tables (2025-2026 Updates)

### 6. teacher_class_subjects Table
**Purpose:** Links teachers to classes and subjects they teach

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| teacher_id | INTEGER | NOT NULL, FOREIGN KEY | Teacher user ID |
| class_id | INTEGER | NOT NULL, FOREIGN KEY | Class ID |
| subject_id | INTEGER | NOT NULL, FOREIGN KEY | Subject ID |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Relationships:**
- Many teacher_class_subjects → One User (teacher)
- Many teacher_class_subjects → One Class
- Many teacher_class_subjects → One Subject

### 7. task_classes Table
**Purpose:** Links tasks to classes (many-to-many)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| task_id | INTEGER | FOREIGN KEY | Task ID |
| class_id | INTEGER | FOREIGN KEY | Class ID |

**Relationships:**
- Many task_classes → One Task
- Many task_classes → One Class

### 8. Forum Tables

#### forum_threads Table
**Purpose:** Forum discussion threads

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| title | VARCHAR(200) | NOT NULL | Thread title |
| class_id | INTEGER | FOREIGN KEY | Associated class (nullable) |
| created_by | INTEGER | FOREIGN KEY | Thread creator |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation time |

#### forum_messages Table
**Purpose:** Forum messages within threads

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| thread_id | INTEGER | FOREIGN KEY | Parent thread |
| user_id | INTEGER | FOREIGN KEY | Message author |
| content | TEXT | NOT NULL | Message content |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation time |
| updated_at | DATETIME | NULL | Last update time |

### 9. Contact Messages Table
**Purpose:** Stores contact form submissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Sender's name |
| email | VARCHAR(120) | NOT NULL | Sender's email |
| subject | VARCHAR(200) | NOT NULL | Message subject |
| message | TEXT | NOT NULL | Message content |
| is_read | BOOLEAN | DEFAULT FALSE | Read status |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Submission time |

### 10. Contact Messages Table
**Purpose:** Stores contact form submissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Sender's name |
| email | VARCHAR(120) | NOT NULL | Sender's email |
| subject | VARCHAR(200) | NOT NULL | Message subject |
| message | TEXT | NOT NULL | Message content |
| is_read | BOOLEAN | DEFAULT FALSE | Read status |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Submission time |

## Updated Entity Relationship Diagram (2026)

```
┌─────────────┐     ┌─────────────────────┐     ┌─────────────┐
│    USER     │     │ TEACHER_CLASS_      │     │    CLASS    │
├─────────────┤     │      SUBJECTS      │     ├─────────────┤
│ id (PK)     │◄────┤ id (PK)           │────►│ id (PK)     │
│ name        │     │ teacher_id (FK)    │     │ name        │
│ email       │     │ class_id (FK)      │     │ created_at  │
│ user_type   │     │ subject_id (FK)    │     └─────────────┘
│ subject     │     │ created_at         │            │
│ class_name  │     └─────────────────────┘            │
│ created_at  │              │                          │
└─────────────┘              │                          │
        │                   │                          │
        │                   ▼                          │
        │     ┌─────────────────────┐                │
        │     │      SUBJECT        │                │
        │     ├─────────────────────┤                │
        │     │ id (PK)            │                │
        │     │ name               │                │
        │     │ description         │                │
        │     └─────────────────────┘                │
        │                                            │
        ▼                                            │
┌─────────────┐     ┌─────────────┐                  │
│    TASK     │────►│ TASK_       │                  │
├─────────────┤     │  CLASSES    │                  │
│ id (PK)     │     ├─────────────┤                  │
│ title       │     │ task_id (FK)│                  │
│ description │     │ class_id (FK)│──────────────────┘
│ deadline    │     └─────────────┘
│ priority    │              │
│ created_by  │              ▼
│ created_at  │     ┌─────────────┐     ┌─────────────┐
└─────────────┘     │ ASSIGNMENT  │     │ SUBMISSION  │
        │           ├─────────────┤     ├─────────────┤
        │           │ task_id (FK)│     │ id (PK)     │
        │           │ student_id  │     │ assignment_id│
        │           │ status      │     │ content      │
        │           │ assigned_at │     │ file_path    │
        │           │ submitted_at│     │ submitted_at │
        │           └─────────────┘     └─────────────┘
        │                 │
        │                 ▼
        │           ┌─────────────┐
        │           │ NOTIFICATION│
        │           ├─────────────┤
        │           │ user_id (FK)│
        │           │ title       │
        │           │ message     │
        │           │ type        │
        │           │ is_read     │
        │           └─────────────┘
        │
        ▼
┌─────────────────────┐
│      FORUM          │
├─────────────────────┤
│ forum_threads       │
│ forum_messages      │
└─────────────────────┘
```

---

**Document Version**: 2.0  
**Last Updated**: February 8, 2026