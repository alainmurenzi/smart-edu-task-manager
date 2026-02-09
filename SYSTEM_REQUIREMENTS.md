# SMART Edu Task Manager - System Requirements Document

## Document Information

| Field | Value |
|-------|-------|
| **Document Title** | System Requirements Specification (SRS) |
| **Version** | 1.0 |
| **Last Updated** | February 8, 2026 |
| **Author** | SMART Edu Development Team |
| **Project** | SMART Edu Task Manager |

---

## 1. Introduction

### 1.1 Purpose

The purpose of this System Requirements Specification document is to define the complete set of functional and non-functional requirements for the SMART Edu Task Manager web application. This document serves as a comprehensive reference for developers, testers, and stakeholders throughout the software development lifecycle.

### 1.2 Scope

The SMART Edu Task Manager is a web-based educational task management system designed to facilitate communication and task tracking between teachers and students. The system incorporates intelligent task prioritization using machine learning algorithms to help students focus on high-priority assignments.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| **SETM** | SMART Edu Task Manager |
| **ML** | Machine Learning |
| **ORM** | Object-Relational Mapping |
| **FK** | Foreign Key |
| **PK** | Primary Key |
| **UI** | User Interface |
| **UX** | User Experience |
| **CSS** | Cascading Style Sheets |
| **API** | Application Programming Interface |
| **JWT** | JSON Web Token |
| **UUID** | Universally Unique Identifier |
| **SQL** | Structured Query Language |
| **CSV** | Comma-Separated Values |

### 1.4 References

1. SMART Edu Task Manager - System Architecture Document
2. SMART Edu Task Manager - Database Design Document
3. SMART Edu Task Manager - Technical Documentation
4. Bootstrap 5 Documentation
5. Flask Framework Documentation
6. SQLAlchemy ORM Documentation

---

## 2. Overall Description

### 2.1 Product Perspective

The SMART Edu Task Manager is a standalone web application built using Flask (Python) as the backend framework and SQLite as the database management system. The application follows a three-tier architecture consisting of:

- **Presentation Layer**: HTML templates with Jinja2 templating, Bootstrap 5 CSS framework, Font Awesome icons
- **Application Layer**: Flask routes, business logic, form validation, ML processing
- **Data Layer**: SQLite database with SQLAlchemy ORM, file storage system

### 2.2 Product Features

The system provides the following core features:

#### For Administrators
- User management (create, read, update, delete)
- System-wide analytics and reporting
- Notification system management
- Task oversight and monitoring
- Contact message management
- Forum moderation capabilities

#### For Teachers
- Task creation with detailed descriptions
- Task assignment to students or classes
- Automatic priority classification using ML
- Student progress monitoring
- Submission review and grading
- Forum participation

#### For Students
- Dashboard with prioritized task list
- Task status management (start, submit)
- File submission capabilities
- Notification center
- Class forum participation
- Performance tracking

### 2.3 User Classes and Characteristics

| User Class | Description | Technical Proficiency |
|------------|-------------|----------------------|
| **Administrator** | System management personnel | Intermediate |
| **Teacher** | Educators who create and manage tasks | Beginner to Intermediate |
| **Student** | Learners who receive and complete tasks | Beginner |

### 2.4 Operating Environment

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10/11, macOS, Linux |
| **Web Browser** | Chrome (recommended), Firefox, Edge, Safari |
| **Python Version** | 3.10 or higher |
| **Database** | SQLite 3.35.5 or higher |
| **Server** | Flask Development Server (Development) / Gunicorn (Production) |

### 2.5 Design and Implementation Constraints

1. **Language Constraint**: Application must be implemented in Python using Flask framework
2. **Database Constraint**: Must use SQLite for data persistence
3. **ORM Constraint**: Must use SQLAlchemy for database operations
4. **Frontend Constraint**: Must use Bootstrap 5 for responsive design
5. **Template Constraint**: Must use Jinja2 templating engine
6. **Authentication Constraint**: Must use Flask-Login for session management
7. **Form Constraint**: Must use WTForms for form handling

### 2.6 User Documentation

The following documentation is provided:
- System Architecture Document
- Database Design Document
- Technical Documentation
- Setup Guide
- API Documentation (inline)

---

## 3. Functional Requirements

### 3.1 User Management Requirements

#### REQ-UM-001: User Registration

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-UM-001 |
| **Priority** | High |
| **Description** | Users must be able to register with the system |
| **Preconditions** | User is not authenticated |
| **Basic Flow** | 1. User navigates to registration page<br>2. User fills registration form<br>3. System validates input<br>4. System creates user account<br>5. User redirected to login |
| **Alternative Flows** | Email already registered → Display error message |
| **Postconditions** | User account is created in database |

#### REQ-UM-002: User Authentication

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-UM-002 |
| **Priority** | High |
| **Description** | Users must be able to log in securely |
| **Preconditions** | User has valid account credentials |
| **Basic Flow** | 1. User navigates to login page<br>2. User enters credentials<br>3. System validates credentials<br>4. System creates session<br>5. User redirected to dashboard |
| **Alternative Flows** | Invalid credentials → Display error message<br>Account disabled → Display error message |
| **Postconditions** | User session is active |

#### REQ-UM-003: Session Management

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-UM-003 |
| **Priority** | High |
| **Description** | System must maintain user sessions securely |
| **Preconditions** | User is authenticated |
| **Basic Flow** | 1. User accesses protected resource<br>2. System verifies session<br>3. Access granted or denied |
| **Postconditions** | Session timeout after 30 minutes of inactivity |

#### REQ-UM-004: User Logout

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-UM-004 |
| **Priority** | Medium |
| **Description** | Users must be able to log out |
| **Preconditions** | User is authenticated |
| **Basic Flow** | 1. User clicks logout<br>2. System destroys session<br>3. User redirected to home page |
| **Postconditions** | User session is terminated |

### 3.2 Task Management Requirements

#### REQ-TM-001: Task Creation

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-TM-001 |
| **Priority** | High |
| **Description** | Teachers must be able to create tasks |
| **Preconditions** | User is authenticated as teacher |
| **Basic Flow** | 1. Teacher navigates to create task page<br>2. Teacher fills task form<br>3. System validates input<br>4. ML predicts priority<br>5. Teacher submits form<br>6. Task is saved to database |
| **Postconditions** | Task is created with assigned students/classes |

#### REQ-TM-002: Task Editing

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-TM-002 |
| **Priority** | Medium |
| **Description** | Teachers must be able to edit their tasks |
| **Preconditions** | User is authenticated as task creator |
| **Basic Flow** | 1. Teacher opens task edit page<br>2. Teacher modifies task details<br>3. System validates changes<br>4. Teacher submits form<br>5. Task is updated |
| **Postconditions** | Task details are modified |

#### REQ-TM-003: Task Deletion

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-TM-003 |
| **Priority** | Medium |
| **Description** | Teachers must be able to delete their tasks |
| **Preconditions** | User is authenticated as task creator |
| **Basic Flow** | 1. Teacher confirms deletion<br>2. System removes task<br>3. Related assignments are deleted |
| **Postconditions** | Task and related data are removed |

#### REQ-TM-004: Task Assignment

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-TM-004 |
| **Priority** | High |
| **Description** | Tasks must be assignable to students |
| **Preconditions** | Task is created |
| **Basic Flow** | 1. Teacher selects students or class<br>2. System creates assignment records<br>3. Notifications are sent |
| **Postconditions** | Students receive task assignments |

#### REQ-TM-005: ML Priority Prediction

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-TM-005 |
| **Priority** | Medium |
| **Description** | System must predict task priority automatically |
| **Preconditions** | Task description is provided |
| **Basic Flow** | 1. Teacher enters task description<br>2. ML model analyzes text<br>3. Priority suggestion is displayed<br>4. Teacher can override suggestion |
| **Postconditions** | Priority field is auto-populated |

### 3.3 Student Task Management Requirements

#### REQ-SM-001: Task Dashboard

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-SM-001 |
| **Priority** | High |
| **Description** | Students must see their tasks on dashboard |
| **Preconditions** | User is authenticated as student |
| **Basic Flow** | 1. Student accesses dashboard<br>2. System retrieves assignments<br>3. Tasks are displayed sorted by priority and deadline |
| **Postconditions** | Task list is displayed |

#### REQ-SM-002: Start Task

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-SM-002 |
| **Priority** | High |
| **Description** | Students must be able to start a task |
| **Preconditions** | Assignment status is 'pending' |
| **Basic Flow** | 1. Student clicks start task<br>2. System updates status to 'in_progress'<br>3. Timer begins |
| **Postconditions** | Assignment status is updated |

#### REQ-SM-003: Submit Task

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-SM-003 |
| **Priority** | High |
| **Description** | Students must be able to submit completed tasks |
| **Preconditions** | Assignment status is 'in_progress' |
| **Basic Flow** | 1. Student accesses submit page<br>2. Student uploads file or enters content<br>3. System validates submission<br>4. Student confirms submission<br>5. Submission is saved |
| **Postconditions** | Assignment status is 'completed', submission record created |

### 3.4 Notification Requirements

#### REQ-NT-001: Task Assignment Notification

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-NT-001 |
| **Priority** | High |
| **Description** | Students must receive notifications for new tasks |
| **Preconditions** | Task is assigned to student |
| **Basic Flow** | 1. System creates notification<br>2. Notification is linked to student<br>3. Student sees notification in dashboard |
| **Postconditions** | Notification is available in student's notification center |

#### REQ-NT-002: Deadline Reminder

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-NT-002 |
| **Priority** | Medium |
| **Description** | Students must receive deadline reminders |
| **Preconditions** | Task deadline is approaching |
| **Basic Flow** | 1. System checks deadlines daily<br>2. Notification is created for upcoming deadlines<br>3. Student receives notification |
| **Postconditions** | Deadline reminder is sent |

### 3.5 Forum Requirements

#### REQ-FR-001: Class Forum

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-FR-001 |
| **Priority** | Medium |
| **Description** | Students and teachers must have class forums |
| **Preconditions** | User is authenticated |
| **Basic Flow** | 1. User accesses class forum<br>2. User can view messages<br>3. User can post new messages |
| **Postconditions** | Forum displays messages |

#### REQ-FR-002: Teachers Forum

| Attribute | Value |
|-----------|-------|
| **ID** | REQ-FR-002 |
| **Priority** | Low |
| **Description** | Teachers must have a private forum |
| **Preconditions** | User is authenticated as teacher |
| **Basic Flow** | 1. Teacher accesses teachers forum<br>2. Teacher can post and view messages |
| **Postconditions** | Forum displays messages |

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

| Requirement ID | Requirement | Target Value |
|----------------|-------------|--------------|
| NFR-PERF-001 | Page load time | < 2 seconds |
| NFR-PERF-002 | Database query time | < 500ms |
| NFR-PERF-003 | File upload time | < 10 seconds |
| NFR-PERF-004 | User response time | < 1 second |
| NFR-PERF-005 | Concurrent users | 50+ simultaneous users |

### 4.2 Security Requirements

| Requirement ID | Requirement | Implementation |
|----------------|-------------|----------------|
| NFR-SEC-001 | Password hashing | PBKDF2 with salt |
| NFR-SEC-002 | Session management | Flask-Login with secure cookies |
| NFR-SEC-003 | SQL injection prevention | SQLAlchemy ORM |
| NFR-SEC-004 | XSS prevention | Jinja2 auto-escaping |
| NFR-SEC-005 | CSRF protection | WTForms CSRF tokens |
| NFR-SEC-006 | File upload validation | Extension and MIME type checking |
| NFR-SEC-007 | Authorization | Role-based access control |

### 4.3 Reliability Requirements

| Requirement ID | Requirement | Target Value |
|----------------|-------------|--------------|
| NFR-REL-001 | System uptime | 99.5% |
| NFR-REL-002 | Data backup | Daily automated backups |
| NFR-REL-003 | Error handling | Graceful degradation |
| NFR-REL-004 | Recovery time | < 1 hour |

### 4.4 Availability Requirements

- System available 24/7 (excluding maintenance windows)
- Planned maintenance scheduled during low-usage periods
- Error notifications sent to administrators
- Automatic recovery from common errors

### 4.5 Maintainability Requirements

- Modular code structure
- Comprehensive inline documentation
- Database schema documentation
- API endpoint documentation
- Unit test coverage > 70%

### 4.6 Portability Requirements

- Compatible with Windows, macOS, Linux
- Works with modern web browsers
- No platform-specific code
- Configuration files for easy deployment

---

## 5. Interface Requirements

### 5.1 User Interfaces

#### 5.1.1 Login Page

| Element | Requirement |
|---------|-------------|
| Email input | Required, email validation |
| Password input | Required, masked characters |
| Login button | Submits form |
| Register link | Navigates to registration |
| Forgot password link | (Planned feature) |

#### 5.1.2 Registration Page

| Element | Requirement |
|---------|-------------|
| Name input | Required, max 100 characters |
| Email input | Required, unique, email validation |
| Password input | Required, min 8 characters |
| Confirm password | Required, must match password |
| User type selector | Teacher or Student |
| Register button | Submits form |
| Login link | Navigates to login |

#### 5.1.3 Teacher Dashboard

| Element | Requirement |
|---------|-------------|
| Welcome message | Displays teacher name |
| Classes overview | Lists assigned classes and subjects |
| Student performance table | Shows all students and their progress |
| Create task button | Navigates to task creation |
| Task list | Shows tasks created by teacher |

#### 5.1.4 Student Dashboard

| Element | Requirement |
|---------|-------------|
| Welcome message | Displays student name |
| Class information | Shows assigned class |
| Task list | Shows prioritized tasks |
| Task progress | Visual indicator of completion |
| Submit task button | Available for in-progress tasks |
| Notification bell | Shows unread notifications |

### 5.2 Hardware Interfaces

No specific hardware interfaces required. System runs on standard web server infrastructure.

### 5.3 Software Interfaces

| Interface | Purpose | Protocol |
|-----------|---------|----------|
| Web Browser | Frontend display | HTTP/HTTPS |
| SQLite Database | Data persistence | SQL |
| File System | File storage | Local filesystem |
| Email Server | (Planned) Email notifications | SMTP |

### 5.4 Communication Interfaces

| Interface | Protocol | Format |
|-----------|----------|--------|
| HTTP | Web communication | HTML/JSON |
| JSON | API responses | REST |
| WebSocket | (Planned) Real-time notifications | ws:// |

---

## 6. Data Requirements

### 6.1 Data Models

#### User Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| name | VARCHAR(100) | NOT NULL | User's full name |
| email | VARCHAR(120) | NOT NULL, UNIQUE | Email address |
| password_hash | VARCHAR(128) | NOT NULL | Hashed password |
| user_type | VARCHAR(20) | NOT NULL | 'teacher' or 'student' |
| subject | VARCHAR(100) | NULL | Teaching subject (teachers) |
| class_name | VARCHAR(100) | NULL | Student's class (students) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation time |

#### Task Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NOT NULL | Task description |
| deadline | DATETIME | NOT NULL | Due date and time |
| priority | VARCHAR(50) | NOT NULL | Priority level |
| instructions | TEXT | NULL | Additional instructions |
| file_path | VARCHAR(500) | NULL | Task file path |
| created_by | INTEGER | NOT NULL, FK | Creating teacher |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation time |

### 6.2 Data Storage

| Data Type | Storage Location | Format |
|-----------|-----------------|--------|
| User data | SQLite database | Relational |
| Task data | SQLite database | Relational |
| Assignment data | SQLite database | Relational |
| Submission files | /uploads/ directory | File system |
| Task files | /uploads/ directory | File system |

### 6.3 Data Recovery

- Daily automated database backups
- Weekly file system backups
- Recovery point objective (RPO): 24 hours
- Recovery time objective (RTO): 1 hour

---

## 7. Logical Database Requirements

### 7.1 Entity Relationships

```
USER (1) ──► (N) TASK
  │                    │
  │                    ▼
  │              (N) ASSIGNMENT ◄─── (N) USER (student)
  │                    │
  │                    ▼
  │              (N) SUBMISSION
  │
  ▼
(N) NOTIFICATION
```

### 7.2 Database Constraints

| Constraint Type | Description |
|-----------------|-------------|
| Primary Keys | All tables have primary key (id) |
| Foreign Keys | Relational integrity maintained |
| Unique Constraints | User email must be unique |
| Check Constraints | User type values restricted |
| Not Null | Required fields marked as NOT NULL |

---

## 8. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| Assignment | Link between a task and a student |
| Priority | Task urgency classification |
| Submission | Student's completed work for a task |
| Notification | System-generated message for users |
| Forum | Online discussion platform |

### B. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | February 8, 2026 | SMART Edu Development Team | Initial document creation |

---

**End of Document**
