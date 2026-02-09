# SMART Edu Task Manager - Setup Guide

Follow these steps to run the project on your local machine.

---

## Prerequisites

- **Python 3.8+** installed on your system
- **pip** (Python package manager)
- **Git** (optional, for cloning)

---

## Step 1: Clone or Download the Project

```bash
git clone <repository-url>
cd "SMART Edu Task Manager"
```

Or download and extract the ZIP file, then navigate to the project folder.

---

## Step 2: Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-SQLAlchemy (database ORM)
- Flask-Login (user authentication)
- Flask-WTF (form handling)
- scikit-learn, pandas, numpy (ML components)
- Other required packages

---

## Step 4: Initialize the Database

The database will be automatically created when you first run the application. The SQLite database file will be stored in the `instance/` folder.

If you need to run database migrations or create tables manually:

```bash
python run.py
```

This will:
- Create all database tables
- Start the development server

---

## Step 5: Create an Admin User (Optional)

To create an admin account for managing the system:

```bash
python create_admin.py
```

---

## Step 6: Run the Application

```bash
python run.py
```

The application will start on: **http://127.0.0.1:5000**

---

## Step 7: Access the Application

Open your web browser and navigate to:

- **Home Page**: `http://127.0.0.1:5000/`
- **Login**: `http://127.0.0.1:5000/login`

---

## User Roles

The system supports three user roles:
1. **Admin** - Manage users, classes, subjects, and view analytics
2. **Teacher** - Create tasks, assign to students, review submissions
3. **Student** - View assigned tasks, submit work, track progress

---

## Project Structure Overview

```
├── app/                 # Flask application modules
├── models/              # Database models
├── templates/           # HTML templates
├── static/              # CSS and static files
├── uploads/             # File uploads directory
├── ml/                  # Machine learning components
├── instance/            # SQLite database
├── run.py               # Application entry point
└── requirements.txt     # Python dependencies
```

---

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `run.py`:
```python
app.run(debug=True, port=5001)
```

### Database Issues
To reset the database:
1. Delete `instance/smart_edu.db`
2. Run `python run.py` again

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## Additional Resources

- [README.md](README.md) - Project overview
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Technical architecture
- [DATABASE_DESIGN.md](DATABASE_DESIGN.md) - Database schema details
- [PLATFORM_TECHNICAL_DOCUMENTATION.md](PLATFORM_TECHNICAL_DOCUMENTATION.md) - Full documentation
