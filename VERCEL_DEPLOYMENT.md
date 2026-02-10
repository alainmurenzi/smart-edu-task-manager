# Vercel Deployment Guide for SMART Edu Task Manager

This guide explains how to deploy the SMART Edu Task Manager application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install the Vercel CLI globally:
   ```bash
   npm install -g vercel
   ```
3. **Git Repository**: Push your code to a GitHub, GitLab, or Bitbucket repository

## Deployment Steps

### 1. Push Code to Git Repository

#### Option A: Using GitHub

1. **Create a new repository on GitHub:**
   - Go to [github.com](https://github.com) and sign in
   - Click the "+" icon in the top right corner
   - Select "New repository"
   - Name your repository (e.g., "smart-edu-task-manager")
   - Make it Public or Private as preferred
   - Click "Create repository"

2. **Initialize Git in your local project:**
   ```bash
   # Navigate to your project directory
   cd /path/to/your/SMART-Edu-Task-Manager
   
   # Initialize Git repository
   git init
   
   # Add all files to Git
   git add .
   
   # Create your first commit
   git commit -m "Initial commit: SMART Edu Task Manager ready for Vercel"
   
   # Add GitHub repository as remote (replace with your actual repository URL)
   git remote add origin https://github.com/yourusername/smart-edu-task-manager.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

#### Option B: Using GitLab

1. **Create a new repository on GitLab:**
   - Go to [gitlab.com](https://gitlab.com) and sign in
   - Click "New project"
   - Select "Create blank project"
   - Name your repository
   - Click "Create project"

2. **Push code to GitLab:**
   ```bash
   # Initialize Git repository
   git init
   
   # Add all files
   git add .
   
   # Create commit
   git commit -m "Initial commit: SMART Edu Task Manager ready for Vercel"
   
   # Add GitLab repository as remote
   git remote add origin https://gitlab.com/yourusername/smart-edu-task-manager.git
   
   # Push to GitLab
   git branch -M main
   git push -u origin main
   ```

#### Option C: Using GitHub Desktop (GUI Method)

1. **Download GitHub Desktop** from [desktop.github.com](https://desktop.github.com)
2. **Clone or create new repository:**
   - Open GitHub Desktop
   - Click "Create a New Repository on your Hard Drive"
   - Choose your project folder
   - Name it and click "Create Repository"
3. **Commit and push:**
   - Review changes in the left panel
   - Add a commit message: "Initial commit: SMART Edu Task Manager ready for Vercel"
   - Click "Commit to main"
   - Click "Publish repository" to push to GitHub

#### Option D: Using Command Line (Generic)

```bash
# If you already have a remote repository
cd /path/to/your/project
git init
git add .
git commit -m "Initial commit: SMART Edu Task Manager ready for Vercel"
git remote add origin <your-repository-url>
git push -u origin main
```

#### Verification:
After pushing, verify your code is online by visiting your repository URL. You should see all your project files including:
- `api/index.py`
- `vercel.json`
- `requirements.txt`
- All your Flask application files

### 2. Environment Variables

Before deploying, set up the following environment variables in your Vercel dashboard:

- `SECRET_KEY`: A secure random string for Flask sessions
- `DATABASE_URL`: Connection string for your cloud database (PostgreSQL recommended)

**For Local Testing:**
```bash
# Create a .env file
echo "SECRET_KEY=your-secret-key-here" > .env
echo "DATABASE_URL=postgresql://username:password@localhost/dbname" >> .env
```

**For Vercel Deployment:**
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings > Environment Variables
4. Add the required variables

### 2. Database Setup

The application is configured to use PostgreSQL in production. You have several options:

**Option A: Vercel Postgres**
1. Enable Vercel Postgres in your Vercel project
2. Copy the connection string and use it as `DATABASE_URL`

**Option B: External PostgreSQL**
- Use services like:
  - [Supabase](https://supabase.com)
  - [PlanetScale](https://planetscale.com)
  - [Railway](https://railway.app)
  - [Heroku Postgres](https://heroku.com)

**Option C: SQLite (Not Recommended for Production)**
- For development/testing, the app will fall back to SQLite
- Note: Vercel's file system is ephemeral, so data will be lost on redeploy

### 3. Deploy to Vercel

**Method 1: Using Vercel CLI**
```bash
# Login to Vercel
vercel login

# Deploy from your project directory
vercel

# Follow the prompts to set up your project
```

**Method 2: Using Git Integration**
1. Push your code to a Git repository
2. Import the repository in Vercel dashboard
3. Vercel will automatically detect the Flask app and deploy it

### 4. Post-Deployment

1. **Initialize Database**: After first deployment, run:
   ```bash
   vercel env pull .env.local
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

2. **Create Admin User**: Set up your admin user:
   ```bash
   python create_admin.py
   ```

## File Structure for Vercel

The following files have been added/modified for Vercel compatibility:

- `api/index.py`: Vercel serverless function entry point
- `vercel.json`: Vercel deployment configuration
- Updated `requirements.txt`: Added Flask-CORS and PostgreSQL support
- Updated `app/__init__.py`: Enhanced for cloud database support

## API Endpoints

The deployed application provides these API endpoints:

- `GET /`: Health check and API information
- `GET /health`: Simple health check
- `POST /auth/login`: User authentication
- `GET /admin/dashboard`: Admin dashboard data
- `GET /teacher/dashboard`: Teacher dashboard data
- `GET /student/dashboard`: Student dashboard data

## Troubleshooting

### Common Issues

1. **404 NOT_FOUND Error**
   - **Issue**: Getting 404 errors when accessing routes
   - **Solution**: Ensure the vercel.json configuration has proper routing setup
   - **Check**: Verify the api/index.py handler function is properly configured
   - **Fix**: The updated vercel.json now includes proper route handling for both /api/(.*) and /(.*) patterns

2. **Database Connection Errors**
   - Verify `DATABASE_URL` is correctly set
   - Ensure your database allows connections from Vercel's IP ranges
   - Check that PostgreSQL connection string format is correct

3. **Import Errors**
   - Check that all dependencies are in `requirements.txt`
   - Verify the Python path in `api/index.py` is correct
   - Ensure Flask-CORS and other new dependencies are installed

4. **Serverless Function Timeout**
   - **Issue**: Function execution timeout errors
   - **Solution**: Optimize database queries and reduce cold start time
   - **Fix**: The updated api/index.py uses efficient request handling

5. **Static Files Not Loading**
   - Vercel serves static files differently than traditional hosting
   - Consider using Vercel's static file serving or a CDN
   - For now, the application returns JSON responses for API routes

### Local Development

To run locally with the same configuration as Vercel:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key"
export DATABASE_URL="your-database-url"

# Run the application
python run.py
```

## Next Steps

1. **Custom Domain**: Configure a custom domain in Vercel settings
2. **Monitoring**: Set up application monitoring and logging
3. **Backup**: Implement database backup strategies
4. **Security**: Review and implement additional security measures

## Support

For issues related to:
- **Vercel Platform**: Visit [Vercel Documentation](https://vercel.com/docs)
- **Flask Application**: Check the original project documentation
- **Database Issues**: Consult your database provider's documentation