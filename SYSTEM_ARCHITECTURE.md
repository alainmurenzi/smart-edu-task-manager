# SMART Edu Task Manager - System Architecture

## Overview
The SMART Edu Task Manager is a Flask-based web application that facilitates educational task management between teachers and students. The system follows a modular architecture with clear separation of concerns.

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

## Architecture Layers

### 1. Presentation Layer
**Purpose:** Handles user interface and HTTP requests
**Components:**
- **Flask Routes** (`/app/` directory)
  - `main.py` - Core application routes and dashboard logic
  - `auth.py` - Authentication and user registration
  - `teacher.py` - Teacher-specific functionality
  - `student.py` - Student-specific functionality
  - `admin.py` - Admin-specific functionality and system management
  - `notifications.py` - Notification system management

- **Templates** (`/templates/` directory)
  - HTML templates with Jinja2 templating
  - Bootstrap 5 for responsive design
  - Font Awesome for icons
  - Base template inheritance pattern

- **Static Assets** (`/static/` directory)
  - CSS styling (`style.css`)
  - JavaScript functionality (when needed)
  - Uploaded files management

### 2. Application Layer
**Purpose:** Business logic and data processing
**Components:**
- **Forms** (`app/forms.py`)
  - WTForms for form validation and handling
  - CSRF protection
  - File upload validation

- **Services**
  - ML Priority Prediction (`ml/priority_predictor.py`)
  - File upload handling
  - Email notifications (planned)
  - Report generation (planned)

### 3. Data Layer
**Purpose:** Data persistence and management
**Components:**
- **Database** (SQLite with SQLAlchemy ORM)
  - Models defined in `models/models.py`
  - Database migrations
  - Relationships and constraints

- **File Storage**
  - Local file system (`/uploads/` directory)
  - Unique file naming with UUID
  - File type validation and size limits

## System Components

### Core Modules

#### 1. Authentication System
```
User Login → Session Management → Role-based Access Control
```
- **User Types:** Teacher, Student, Admin
- **Security:** Password hashing, session management
- **Access Control:** Route-level protection with decorators

#### 2. Task Management
```
Task Creation → Assignment → Progress Tracking → Submission → Review
```
- **Task Lifecycle:** Create → Assign → Track → Submit → Review
- **Priority Classification:** ML-powered priority suggestion
- **File Management:** Task files and submission files

#### 3. Admin System
```
User Management → System Monitoring → Analytics → Data Export
```
- **System Administration:** User creation, editing, and deletion
- **Task Oversight:** System-wide task management and monitoring
- **Analytics:** System usage statistics and performance metrics
- **Notification Management:** System-wide notification creation

#### 4. Notification System
```
Notification Creation → User Targeting → Delivery → Status Tracking
```
- **In-App Notifications:** Real-time notification center
- **System Notifications:** Admin-created announcements
- **Read/Unread Status:** Notification status management
- **Notification Types:** Info, Success, Warning, Error categories

#### 5. Database Models
- **User:** Base user with role-specific fields (Teacher, Student, Admin)
- **Task:** Task details with metadata
- **Assignment:** Task-student relationship
- **Submission:** Student task submissions
- **Notification:** User notification system

### Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Templates)   │◄──►│   (Flask App)   │◄──►│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │   Business      │    │   File Storage  │
│   & Validation  │    │   Logic         │    │   (/uploads/)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Backend Framework
- **Flask 2.x** - Micro web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **WTForms** - Form handling and validation
- **Flask-WTF** - CSRF protection

### Frontend
- **Bootstrap 5** - Responsive UI framework
- **Jinja2** - Template engine
- **Font Awesome** - Icon library

### Machine Learning
- **Custom Priority Predictor** - ML-based task priority classification
- **Text Analysis** - Natural language processing for priority suggestions

### Database
- **SQLite** - Lightweight relational database
- **SQLAlchemy ORM** - Object-relational mapping

### File Handling
- **Werkzeug** - File upload handling
- **UUID** - Unique file naming
- **OS Module** - File system operations

## Security Measures

### 1. Authentication & Authorization
- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- Route protection decorators

### 2. Data Validation
- WTForms validation
- File type and size validation
- SQL injection prevention with ORM
- XSS protection with Jinja2

### 3. File Security
- Unique file naming (UUID)
- Secure file uploads
- File type restrictions
- Path traversal prevention

### 4. Session Security
- HTTP-only cookies
- Secure session configuration
- CSRF protection (configurable)

## Scalability Considerations

### Current Limitations
- SQLite database (single-user)
- Local file storage
- Synchronous request handling

### Future Improvements
- PostgreSQL/MySQL for multi-user support
- Cloud storage (AWS S3, Google Cloud)
- Caching with Redis
- Background task processing
- Horizontal scaling with load balancers

## API Design Pattern

### RESTful Endpoints
```
Authentication & Core:
GET    /dashboard         - User dashboard
GET    /login            - User login
POST   /login            - User authentication

Task Management:
GET    /create_task       - Task creation form
POST   /create_task       - Create new task
GET    /edit_task/<id>    - Edit task form
POST   /edit_task/<id>    - Update task
POST   /delete_task/<id>  - Delete task
GET    /task_progress/<id> - View task progress
GET    /review_submissions/<id> - Review submissions

Admin System:
GET    /admin             - Admin dashboard
GET    /admin/users       - User management
POST   /admin/user/create - Create new user
GET    /admin/user/<id>/edit - Edit user
POST   /admin/user/<id>/delete - Delete user
GET    /admin/analytics   - System analytics
GET    /admin/tasks       - Task oversight
POST   /admin/notifications/create - Create system notification

Notification API:
GET    /api/notifications - Get user notifications
POST   /api/notifications/mark-read/<id> - Mark notification as read
POST   /api/notifications/mark-all-read - Mark all notifications as read
```

### Response Patterns
- JSON responses for API endpoints
- HTML responses for web pages
- File downloads for attachments
- Redirects for form submissions

## Configuration Management

### Environment Variables
- `SECRET_KEY` - Application secret key
- Database connection strings
- File upload configurations
- Email server settings (future)

### Flask Configuration
- Development vs Production settings
- Debug mode control
- Static file serving
- Template directory configuration

## Monitoring & Logging

### Application Logging
- Flask built-in logging
- Custom log handlers (planned)
- Error tracking (future)
- Performance monitoring (future)

### Health Checks
- Database connectivity
- File system access
- Authentication system status

## Deployment Architecture

### Development Environment
- Local Flask development server
- SQLite database file
- Local file storage

### Production Considerations
- WSGI server (Gunicorn/uWSGI)
- Reverse proxy (Nginx)
- Database migration
- SSL/TLS termination
- Environment-specific configurations

---

## Branding and Visual Identity

### Logo Design (2026 Update)
The platform features a modern logo representing the "SETM" acronym:

| Component | Description | Color |
|-----------|-------------|--------|
| **S** | First letter | Red (#ef4444) |
| **E** | Second letter | Green (#22c55e) |
| **T** | Third letter | Blue (#3b82f6) |
| **M** | Fourth letter | Purple (#8b5cf6) |

**Logo Specifications:**
- Format: SVG (Scalable Vector Graphics)
- Location: `static/logo.svg`
- Design: Four uniform colored circles in a horizontal row
- Each letter centered within its colored circle

### Favicon
- Format: SVG
- Location: `static/favicon.svg`
- Design: Green circle with white checkmark and "EDU" text

### UI Theme Updates (2026)
- Base font size: 18px (increased from 16px for better readability)
- Table styling: Black font with light gray headers
- Status badges: Color-coded for quick visual identification
- Responsive design: Logo visible at 85px height on all screen sizes

### Teacher Dashboard Performance Table
The student performance table displays:
| Column | Description |
|--------|-------------|
| Student Name | Student's full name |
| Class | Student's assigned class |
| Total Tasks | Number of tasks assigned |
| Completed | Tasks completed (green badge) |
| In Progress | Tasks in progress (blue badge) |
| Overdue | Overdue tasks (red badge) |
| Completion Rate | Progress bar with percentage |
| Status | Performance status badge |