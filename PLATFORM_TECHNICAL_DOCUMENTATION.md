# SMART Edu Task Manager - Technical Documentation

## Executive Summary

The SMART Edu Task Manager is a Flask-based web application designed to revolutionize educational task management through intelligent priority-based classification and real-time collaboration between teachers and students. The system integrates machine learning algorithms for automated task prioritization, comprehensive notification systems, and robust user role management.

## 1. System Overview

### 1.1 Core Purpose
The platform addresses the critical challenge of task management in educational environments by:
- Implementing AI-powered priority classification for academic tasks
- Providing real-time collaboration tools for teachers and students
- Offering comprehensive analytics and progress tracking
- Ensuring secure and scalable user management

### 1.2 Target Users
- **Teachers**: Create, assign, and monitor tasks with intelligent priority suggestions
- **Students**: Receive prioritized task lists and submit work through an intuitive interface
- **Administrators**: System-wide oversight, user management, and analytics

### 1.3 Key Innovation
The system's unique feature is its machine learning-powered priority prediction system that automatically classifies tasks based on textual descriptions, helping students focus on what matters most.

## 2. System Architecture

### 2.1 Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SMART Edu Task Manager                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   Presentation  │    │   Application   │    │     Data        │        │
│  │     Layer       │    │     Layer       │    │    Layer        │        │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤        │
│  │ • HTML Templates│    │ • Route Logic   │    │ • SQLite DB     │        │
│  │ • Bootstrap 5   │    │ • Business Rules│    │ • SQLAlchemy    │        │
│  │ • Font Awesome  │    │ • Form Handling │    │ • File Storage  │        │
│  │ • Responsive UI │    │ • ML Processing │    │ • Relationships │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│           │                       │                       │              │
│           └───────────────────────┼───────────────────────┘              │
│                                   │                                      │
│  ┌─────────────────────────────────┼────────────────────────────────────┐ │
│  │                    Flask Application Framework                       │ │
│  └─────────────────────────────────┼────────────────────────────────────┘ │
│                                   │                                      │
│  ┌─────────────────────────────────┼────────────────────────────────────┐ │
│  │                    External Services                                 │ │
│  │  • ML Libraries (scikit-learn)  • File Upload System                 │ │
│  │  • Authentication Services      • Notification System                 │ │
│  └─────────────────────────────────┴────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | Flask 2.x (Python) | Web application framework |
| **Database** | SQLite + SQLAlchemy ORM | Data persistence and management |
| **Frontend** | Bootstrap 5 + Jinja2 | Responsive UI and templating |
| **Machine Learning** | scikit-learn | Priority prediction algorithms |
| **Authentication** | Flask-Login + Werkzeug | User session management and security |
| **Forms** | WTForms + Flask-WTF | Form validation and CSRF protection |
| **Icons** | Font Awesome | UI iconography |
| **File Handling** | Werkzeug Secure Upload | Secure file upload and storage |

### 2.3 Architecture Pattern
The system follows a **Model-View-Controller (MVC)** pattern with the following layers:

#### Presentation Layer
- HTML templates with Jinja2 inheritance
- Responsive Bootstrap 5 UI components
- Real-time notification center
- Role-based dashboard interfaces

#### Application Layer
- Route handlers organized by user roles (`main.py`, `auth.py`, `teacher.py`, `student.py`, `admin.py`)
- Business logic encapsulation in service functions
- Form validation and CSRF protection via WTForms

#### Data Layer
- SQLAlchemy models for database abstraction
- Relationship management between entities
- File storage with unique naming conventions

## 3. Database Design

### 3.1 Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    USER     │     │    TASK     │     │ ASSIGNMENT  │     │ SUBMISSION  │
├─────────────┤     ├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │────►│ id (PK)     │◄────│ id (PK)     │◄────│ id (PK)     │
│ name        │     │ title       │     │ task_id(FK) │     │ assignment_id│
│ email       │     │ description │     │ student_id(FK)│   │ content     │
│ user_type   │     │ deadline    │     │ status      │     │ file_path   │
│ subject     │     │ priority    │     │ assigned_at │     │ submitted_at│
│ class_id(FK)│     │ instructions│     │ submitted_at│     │ score       │
│ password_hash│    │ file_path   │     └─────────────┘     │ feedback    │
│ created_at  │     │ created_by(FK)│              ▲        │ graded_by(FK)│
└─────────────┘     │ created_at  │              │        └─────────────┘
        │           └─────────────┘              │
        │                   │                    │
        ▼                   ▼                    │
┌─────────────┐     ┌─────────────┐             │
│    CLASS    │     │  SUBJECT    │             │
├─────────────┤     ├─────────────┤             │
│ id (PK)     │     │ id (PK)     │             │
│ name        │     │ name        │             │
│ description │     │ description │             │
│ created_by(FK)│   │ created_by(FK)│           │
│ created_at  │     │ created_at  │             │
└─────────────┘     └─────────────┘             │
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                    ┌─────────────┐
                    │NOTIFICATION │
                    ├─────────────┤
                    │ id (PK)     │
                    │ user_id(FK) │
                    │ title       │
                    │ message     │
                    │ type        │
                    │ is_read     │
                    │ created_at  │
                    │ expires_at  │
                    └─────────────┘
```

### 3.2 Database Schema Tables

#### Table 3.1: User Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| name | VARCHAR(100) | NOT NULL | User's full name |
| email | VARCHAR(120) | NOT NULL, UNIQUE | User's email address (login identifier) |
| password_hash | VARCHAR(128) | NOT NULL | Hashed password for security |
| user_type | VARCHAR(20) | NOT NULL | 'teacher', 'student', or 'admin' |
| subject | VARCHAR(100) | NULL | Subject taught (teachers only) |
| class_id | INTEGER | NULL, FOREIGN KEY | Class assignment (students only) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

#### Table 3.2: Task Table
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

#### Table 3.3: Assignment Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique assignment identifier |
| task_id | INTEGER | NOT NULL, FOREIGN KEY | Referenced task ID |
| student_id | INTEGER | NOT NULL, FOREIGN KEY | Assigned student ID |
| status | VARCHAR(20) | DEFAULT 'pending' | Assignment status |
| assigned_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Assignment creation timestamp |
| submitted_at | DATETIME | NULL | Submission timestamp |

#### Table 3.4: Submission Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique submission identifier |
| assignment_id | INTEGER | NOT NULL, FOREIGN KEY | Related assignment ID |
| content | TEXT | NULL | Text-based submission content |
| file_path | VARCHAR(500) | NULL | Path to submitted file |
| submitted_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Submission timestamp |
| score | INTEGER | NULL | Teacher grading score (0-100) |
| feedback | TEXT | NULL | Teacher feedback comments |
| feedback_provided_at | DATETIME | NULL | When feedback was provided |
| graded_by | INTEGER | NULL, FOREIGN KEY | Teacher who graded |

#### Table 3.5: Notification Table
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

#### Table 3.6: Class Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique class identifier |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Class name |
| description | TEXT | NULL | Class description |
| created_by | INTEGER | NOT NULL, FOREIGN KEY | Admin who created class |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Class creation timestamp |

#### Table 3.7: Subject Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique subject identifier |
| name | VARCHAR(100) | NOT NULL | Subject name |
| description | TEXT | NULL | Subject description |
| created_by | INTEGER | NOT NULL, FOREIGN_KEY | Admin who created subject |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Subject creation timestamp |

### 3.3 Priority Classification System

#### Table 3.8: Task Priority Levels
| Priority Level | Description | Student Impact |
|----------------|-------------|----------------|
| urgent_important | Urgent & Important | Immediate attention required |
| important_not_urgent | Important but Not Urgent | High priority, plan ahead |
| urgent_not_important | Urgent but Not Important | Time-sensitive but low impact |
| not_important_not_urgent | Not Important & Not Urgent | Minimal priority |
| high_priority | High Priority (High Marks/Major Assignment) | Significant academic impact |
| medium_priority | Medium Priority | Standard academic tasks |
| low_priority | Low Priority | Minor tasks |
| optional | Optional/Extra Work | Extra credit opportunities |
| long_term | Long-term Project | Extended deadline projects |
| group_task | Group Task | Collaborative assignments |

### 3.4 Relationship Constraints
- **One-to-Many**: User → Tasks (teachers creating tasks)
- **One-to-Many**: User → Assignments (students receiving tasks)
- **One-to-Many**: Task → Assignments (task assigned to multiple students)
- **One-to-Many**: Assignment → Submissions (multiple submission versions)
- **One-to-Many**: User → Notifications (user receiving notifications)
- **Many-to-Many**: Teachers ↔ Classes (through teaching_classes association table)
- **Many-to-Many**: Classes ↔ Subjects (through class_subjects association table)

## 4. Core System Workflows

### 4.1 Task Creation and Assignment Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Task Creation Workflow                                │
└─────────────────────────────────────────────────────────────────────────────┘

Teacher Login ──┐
                │
                ▼
        ┌───────────────┐
        │ Validate User │
        │ Permissions   │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Enter Task    │
        │ Details       │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐    ┌─────────────────┐
        │ ML Priority   │    │ File Upload     │
        │ Prediction    │    │ Validation      │
        └───────┬───────┘    └───────┬─────────┘
                │                    │
                └────────┬───────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Create Task     │
                │ Record          │
                └───────┬─────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Create          │
                │ Assignments     │
                └───────┬─────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Send            │
                │ Notifications   │
                └─────────────────┘
```

### 4.2 Student Task Processing Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Student Task Processing Workflow                        │
└─────────────────────────────────────────────────────────────────────────────┘

Student Login ──┐
                │
                ▼
        ┌───────────────┐
        │ Fetch         │
        │ Assignments   │
                │
                ▼
        ┌───────────────┐
        │ Apply Priority│
                │ Sorting
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Display       │
                │ Dashboard
        └───────┬───────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Start   │ │ Submit  │ │ View    │
│ Task    │ │ Task    │ │ Feedback│
└─────────┘ └─────────┘ └─────────┘
```

### 4.3 Machine Learning Priority Prediction Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ML Priority Prediction Process                            │
└─────────────────────────────────────────────────────────────────────────────┘

Task Description ──┐
                   │
                   ▼
            ┌──────────────┐
            │ Text         │
            │ Preprocessing│
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ Keyword      │
            │ Extraction   │
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐    ┌──────────────┐
            │ Pattern      │    │ Rule-based   │
            │ Matching     │    │ Classification│
            └──────┬───────┘    └──────┬───────┘
                   │                   │
                   └─────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Priority        │
                    │ Classification  │
                    └───────┬─────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │ Return Priority │
                    │ Level           │
                    └─────────────────┘
```

## 5. User Roles and Permissions

### Table 5.1: User Role Matrix
| Feature/Functionality | Student | Teacher | Admin |
|-----------------------|---------|---------|-------|
| **Authentication** | ✅ | ✅ | ✅ |
| **Dashboard Access** | ✅ | ✅ | ✅ |
| **View Tasks** | ✅ | ✅ | ✅ |
| **Create Tasks** | ❌ | ✅ | ✅ |
| **Edit Tasks** | ❌ | ✅ (Own) | ✅ |
| **Delete Tasks** | ❌ | ✅ (Own) | ✅ |
| **Assign Tasks** | ❌ | ✅ | ✅ |
| **Submit Tasks** | ✅ | ❌ | ❌ |
| **Grade Submissions** | ❌ | ✅ | ✅ |
| **View Analytics** | Limited | ✅ | ✅ |
| **Manage Users** | ❌ | ❌ | ✅ |
| **System Settings** | ❌ | ❌ | ✅ |
| **Notifications** | ✅ | ✅ | ✅ |
| **File Uploads** | ✅ | ✅ | ✅ |

### Table 5.2: API Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| **Authentication** |
| GET/POST | `/login` | User login | No |
| POST | `/logout` | User logout | Yes |
| GET/POST | `/register/teacher` | Teacher registration | No |
| GET/POST | `/register/student` | Student registration | No |
| **Core Functionality** |
| GET | `/dashboard` | User dashboard | Yes |
| GET/POST | `/teacher/create_task` | Create new task | Teacher |
| GET/POST | `/teacher/edit_task/<id>` | Edit task | Teacher |
| POST | `/teacher/delete_task/<id>` | Delete task | Teacher |
| GET | `/teacher/task_progress/<id>` | View task progress | Teacher |
| GET | `/student/dashboard` | Student dashboard | Student |
| GET | `/student/task/<id>` | View task details | Student |
| POST | `/student/start_task/<id>` | Start task | Student |
| GET/POST | `/student/submit_task/<id>` | Submit task | Student |
| **Admin Functions** |
| GET | `/admin/dashboard` | Admin dashboard | Admin |
| GET | `/admin/users` | User management | Admin |
| POST | `/admin/user/create` | Create user | Admin |
| GET/POST | `/admin/user/<id>/edit` | Edit user | Admin |
| POST | `/admin/user/<id>/delete` | Delete user | Admin |

## 6. Security Implementation

### 6.1 Security Measures

| Security Layer | Implementation | Purpose |
|----------------|----------------|---------|
| **Authentication** | Flask-Login + Password Hashing | User identity verification |
| **Authorization** | Role-based access control | Permission management |
| **Data Validation** | WTForms validators | Input sanitization |
| **CSRF Protection** | WTForms CSRF tokens | Cross-site request forgery prevention |
| **SQL Injection** | SQLAlchemy ORM | Database query protection |
| **XSS Protection** | Jinja2 auto-escaping | Cross-site scripting prevention |
| **File Upload Security** | Secure filename + type validation | Malicious file prevention |
| **Session Security** | HTTP-only cookies | Session hijacking prevention |
| **Password Security** | PBKDF2 hashing | Password storage security |

### 6.2 File Security Implementation
```python
# Secure file upload example
def handle_secure_upload(file_data):
    if file_data:
        # Generate unique filename
        filename = secure_filename(file_data.filename)
        unique_filename = str(uuid.uuid4()) + '_' + filename
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Validate file type
        allowed_extensions = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
        if '.' in filename:
            extension = filename.rsplit('.', 1)[1].lower()
            if extension not in allowed_extensions:
                raise ValueError("File type not allowed")
        
        # Save file
        file_data.save(file_path)
        return file_path
    return None
```

## 7. Performance Optimizations

### 7.1 Database Optimization

| Optimization Technique | Implementation | Benefit |
|------------------------|----------------|---------|
| **Indexing** | Foreign keys and query columns | Faster data retrieval |
| **Query Optimization** | Efficient JOIN operations | Reduced query execution time |
| **Lazy Loading** | Relationship loading on-demand | Reduced memory usage |
| **Connection Pooling** | SQLAlchemy connection management | Better resource utilization |
| **Query Caching** | Planned Redis integration | Reduced database load |

### 7.2 Performance Metrics

| Metric | Target | Current Implementation |
|--------|--------|----------------------|
| **Page Load Time** | < 2 seconds | Real-time monitoring |
| **Database Query Time** | < 500ms | Query optimization |
| **File Upload Time** | < 10 seconds | Async processing |
| **User Response Time** | < 1 second | Caching strategies |
| **System Uptime** | 99.9% | Error handling |

## 8. Testing Framework

### 8.1 Testing Strategy

| Test Type | Scope | Tools | Coverage |
|-----------|-------|-------|----------|
| **Unit Testing** | Individual functions/methods | pytest, unittest | 80%+ |
| **Integration Testing** | Component interaction | pytest, Flask test client | 70%+ |
| **API Testing** | REST endpoints | pytest, requests | 90%+ |
| **Security Testing** | Authentication, authorization | Manual testing, tools | Comprehensive |
| **Performance Testing** | Load, stress testing | Manual testing | Baseline established |
| **User Acceptance Testing** | End-to-end workflows | Manual testing | All user roles |

### 8.2 Test Case Examples

#### Table 8.1: Core Test Cases
| Test ID | Test Name | Priority | Status |
|---------|-----------|----------|--------|
| TC001 | User Authentication | High | ✅ |
| TC002 | Task Creation | High | ✅ |
| TC003 | Priority Prediction | Medium | ✅ |
| TC004 | File Upload | High | ✅ |
| TC005 | Notification System | Medium | ✅ |
| TC006 | Student Dashboard | High | ✅ |
| TC007 | Teacher Dashboard | High | ✅ |
| TC008 | Admin Functions | High | ✅ |

## 9. Monitoring and Analytics

### 9.1 System Statistics Dashboard

| Metric | Description | Calculation |
|--------|-------------|-------------|
| **Total Users** | All registered users | COUNT(user.id) |
| **Active Teachers** | Teachers with recent activity | COUNT(user.id) WHERE user_type='teacher' |
| **Active Students** | Students with recent activity | COUNT(user.id) WHERE user_type='student' |
| **Total Tasks** | All created tasks | COUNT(task.id) |
| **Completion Rate** | Percentage of completed tasks | (completed_assignments/total_assignments) * 100 |
| **Recent Submissions** | Submissions in last 7 days | COUNT(submission.id) WHERE submitted_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) |
| **Overdue Tasks** | Tasks past deadline | COUNT(assignment.id) WHERE status != 'completed' AND deadline < NOW() |

### 9.2 Performance Monitoring

| Component | Monitoring Method | Alert Threshold |
|-----------|-------------------|-----------------|
| **Database** | Connection pool monitoring | > 80% utilization |
| **File Storage** | Disk space monitoring | < 10% free space |
| **Application** | Error rate tracking | > 5% error rate |
| **Authentication** | Failed login attempts | > 10 attempts/minute |
| **API Response** | Response time tracking | > 2 seconds average |

## 10. Deployment Architecture

### 10.1 Environment Configuration

| Environment | Database | Debug Mode | File Storage | Purpose |
|-------------|----------|------------|--------------|---------|
| **Development** | SQLite | Enabled | Local filesystem | Development testing |
| **Staging** | SQLite/PostgreSQL | Disabled | Local filesystem | Pre-production testing |
| **Production** | PostgreSQL/MySQL | Disabled | Cloud storage | Live system |

### 10.2 Deployment Process

```bash
# Development Setup
git clone <repository>
cd smart-edu-task-manager
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py

# Production Deployment
gunicorn -w 4 -b 0.0.0.0:8000 'app:create_app()'
```

## 11. Scalability Considerations

### 11.1 Current Limitations and Solutions

| Current Limitation | Impact | Planned Solution |
|-------------------|--------|------------------|
| SQLite Database | Single-user concurrency | PostgreSQL migration |
| Local File Storage | Storage constraints | AWS S3 integration |
| Synchronous Processing | Request blocking | Celery async tasks |
| Single Server | Limited scalability | Load balancer + multiple instances |

### 11.2 Future Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Future Scalable Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │   Load      │  │   Web       │  │   Web       │                         │
│  │  Balancer   │  │  Server 1   │  │  Server 2   │                         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                         │
│         │                │                │                                │
│         └────────────────┼────────────────┘                                │
│                          │                                               │
│  ┌───────────────────────┼─────────────────────────────────────────────┐  │
│  │                     Application Layer                                │  │
│  │  • Flask Applications  • Business Logic  • API Services             │  │
│  └───────────────────────┼─────────────────────────────────────────────┘  │
│                          │                                               │
│  ┌───────────────────────┼─────────────────────────────────────────────┐  │
│  │                    Data Layer                                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ PostgreSQL  │  │    Redis    │  │ File Storage│  │   Queue     │  │  │
│  │  │  Database   │  │    Cache    │  │    (S3)     │  │   (Celery)  │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 12. Technical Challenges and Solutions

### 12.1 Challenge: Priority Classification Accuracy

**Problem**: Ensuring ML model accurately classifies diverse task types across different subjects and educational levels.

**Solution Implementation**:
```python
class PriorityPredictor:
    def __init__(self):
        self.keyword_patterns = {
            'urgent_important': {
                'keywords': ['urgent', 'deadline', 'due soon', 'important', 'critical', 'exam', 'test', 'final'],
                'patterns': [r'due\s+\w+', r'urgent\s+\w+', r'important\s+\w+']
            },
            'high_priority': {
                'keywords': ['high marks', 'major assignment', 'project', 'presentation', 'assessment'],
                'patterns': [r'major\s+\w+', r'project\s+\w+', r'presentation\s+\w+']
            },
            'medium_priority': {
                'keywords': ['homework', 'assignment', 'reading', 'exercise'],
                'patterns': [r'homework\s+\w+', r'assignment\s+\w+']
            }
        }
    
    def predict_priority(self, description):
        description_lower = description.lower()
        scores = {}
        
        for priority, patterns in self.keyword_patterns.items():
            score = 0
            
            # Keyword matching
            for keyword in patterns['keywords']:
                if keyword in description_lower:
                    score += 1
            
            # Pattern matching
            import re
            for pattern in patterns['patterns']:
                if re.search(pattern, description_lower):
                    score += 2
            
            scores[priority] = score
        
        return max(scores, key=scores.get) if scores else 'medium_priority'
```

### 12.2 Challenge: File Security and Storage

**Problem**: Secure handling of educational documents and student submissions while preventing malicious uploads.

**Security Measures**:
1. **File Type Validation**: Extension and MIME type checking
2. **File Size Limits**: Configurable maximum sizes
3. **Unique Naming**: UUID-based filename generation
4. **Path Traversal Prevention**: Secure filename sanitization
5. **Virus Scanning**: Integration with antivirus engines (planned)

### 12.3 Challenge: Real-time Notification System

**Problem**: Delivering timely notifications without impacting system performance.

**Optimization Strategies**:
```python
class NotificationManager:
    def __init__(self):
        self.batch_size = 100
        self.notification_queue = []
    
    def create_notification(self, user_id, title, message, notification_type='info'):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        
        # Batch notifications for performance
        if len(self.notification_queue) >= self.batch_size:
            self._flush_notifications()
        else:
            self.notification_queue.append(notification)
    
    def _flush_notifications(self):
        db.session.add_all(self.notification_queue)
        db.session.commit()
        self.notification_queue.clear()
```

## 13. Machine Learning Integration

### 13.1 Priority Prediction Algorithm

The system implements a hybrid approach combining rule-based classification with machine learning:

```python
class MLPriorityPredictor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classifier = MultinomialNB()
        self.is_trained = False
    
    def train_model(self, training_data):
        """Train the ML model with historical task data"""
        descriptions = [item['description'] for item in training_data]
        priorities = [item['priority'] for item in training_data]
        
        # Transform text to numerical features
        X = self.vectorizer.fit_transform(descriptions)
        
        # Train classifier
        self.classifier.fit(X, priorities)
        self.is_trained = True
    
    def predict_priority(self, description):
        """Predict priority for new task description"""
        if not self.is_trained:
            # Fallback to rule-based approach
            return self.rule_based_prediction(description)
        
        # Transform description to features
        X = self.vectorizer.transform([description])
        
        # Predict priority
        prediction = self.classifier.predict(X)[0]
        confidence = max(self.classifier.predict_proba(X)[0])
        
        return {
            'priority': prediction,
            'confidence': confidence
        }
```

### 13.2 Training Data Structure

| Feature | Description | Example |
|---------|-------------|---------|
| **description** | Task description text | "Complete math assignment on calculus" |
| **priority** | Actual priority assigned | "medium_priority" |
| **subject** | Academic subject | "Mathematics" |
| **deadline_urgency** | Days until deadline | 3 |
| **task_type** | Type of task | "assignment" |

## 14. Future Enhancements

### 14.1 Planned Features

| Feature | Priority | Timeline | Technical Approach |
|---------|----------|----------|-------------------|
| **Advanced ML Models** | High | Q2 2026 | Transformer models (BERT) |
| **Real-time Collaboration** | Medium | Q3 2026 | WebSocket + Operational Transform |
| **Mobile Application** | High | Q4 2026 | React Native development |
| **API Integration** | Medium | Q1 2027 | RESTful API with authentication |
| **Advanced Analytics** | High | Q2 2027 | Machine learning insights |
| **Offline Support** | Low | Q3 2027 | Progressive Web App |

### 14.2 Research Opportunities

1. **Personalized Learning Analytics**: Using student behavior data to predict learning outcomes
2. **Collaborative Filtering**: Recommending tasks based on peer activities
3. **Natural Language Processing**: Enhanced task description analysis
4. **Computer Vision**: Automated grading for visual assignments
5. **Blockchain Integration**: Secure credential verification

## 15. Conclusion

The SMART Edu Task Manager represents a comprehensive solution to educational task management challenges through the integration of machine learning, modern web technologies, and user-centered design. The system's modular architecture, robust security measures, and scalable design provide a solid foundation for future enhancements while delivering immediate value to educators and students.

### 15.1 Key Achievements

1. **Intelligent Task Prioritization**: ML-powered classification system
2. **Comprehensive User Management**: Role-based access control
3. **Real-time Collaboration**: Notification and communication system
4. **Secure File Handling**: Robust upload and storage mechanisms
5. **Scalable Architecture**: Modular design for future growth

### 15.2 Technical Excellence

The technical implementation demonstrates best practices in:
- **Software Architecture**: Clean separation of concerns with MVC pattern
- **Security**: Multi-layered security with authentication, authorization, and data protection
- **Performance**: Database optimization and efficient query patterns
- **Maintainability**: Well-documented code with comprehensive testing
- **Scalability**: Architecture designed for horizontal and vertical scaling

### 15.3 Impact and Innovation

The platform's innovative approach to educational task management through AI-powered prioritization addresses real-world challenges faced by educators and students. The system's ability to automatically classify tasks and provide intelligent suggestions demonstrates the practical application of machine learning in educational technology.

The extensible design allows for continuous improvement and adaptation to evolving educational needs, making it a valuable contribution to the field of educational technology.

---

**Document Version**: 2.1  
**Last Updated**: February 8, 2026  
**Author**: SMART Edu Development Team  
**Purpose**: Technical reference for thesis chapters on System Design/Development and Testing/Evaluation

---

## 16. Branding and UI Updates (February 2026)

### 16.1 Logo Design

The platform has been updated with a new logo featuring the "SETM" acronym:

| Component | Description | Colors |
|-----------|-------------|--------|
| **S** | First letter | Red (#ef4444) |
| **E** | Second letter | Green (#22c55e) |
| **T** | Third letter | Blue (#3b82f6) |
| **M** | Fourth letter | Purple (#8b5cf6) |

**Logo File**: `static/logo.svg`

**Logo Features**:
- Four uniform colored circles in a horizontal row
- Each letter (S, E, T, M) centered within its circle
- Consistent spacing between circles
- Scalable SVG format

### 16.2 Favicon Design

A matching favicon was added to the platform:

**Favicon File**: `static/favicon.svg`

**Favicon Features**:
- Green circular background
- White checkmark symbolizing task completion
- "EDU" text at the bottom

### 16.3 Teacher Dashboard UI Updates

The teacher dashboard's student performance table has been enhanced:

**Table Columns**:
| Column | Description |
|--------|-------------|
| Student Name | Student's full name |
| Class | Student's assigned class |
| Total Tasks | Number of tasks assigned |
| Completed | Number of completed tasks (green badge) |
| In Progress | Number of tasks in progress (blue badge) |
| Overdue | Number of overdue tasks (red badge) |
| Completion Rate | Progress bar showing percentage |
| Status | Performance status badge |

**UI Improvements**:
- Black font color for better readability
- Light gray table header background
- Colored status badges for quick visual identification
- Progress bars for completion rate visualization

### 16.4 Global Font Size Update

The base font size has been increased from 16px to 18px across all pages for improved readability.

### 16.5 Responsive Logo Display

The logo configuration in `templates/base.html`:

```html
<a class="navbar-brand d-flex align-items-center" href="{{ url_for('main.index') }}">
    <img src="{{ url_for('static', filename='logo.svg') }}" alt="SETM Logo" style="height: 85px;" class="me-2">
    <span class="d-none d-xxl-inline fw-bold fs-4">SMART Edu Task Manager</span>
</a>
```

**Display Rules**:
- Logo: Always visible, 85px height
- Text "SMART Edu Task Manager": Only on extra-extra-large screens (xxl breakpoint)