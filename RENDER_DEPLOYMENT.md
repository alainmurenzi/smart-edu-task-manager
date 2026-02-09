# Render Deployment Guide  
====================  
  
## Prerequisites  
  
1. GitHub account  
2. Render.com account (free)  
3. Your code pushed to GitHub  
  
## Deployment Steps  
  
### Step 1: Push to GitHub  
  
```bash  
git add .  
git commit -m "Prepare for Render deployment"  
git push origin main  
```  
  
### Step 2: Create Web Service on Render  
  
1. Go to https://dashboard.render.com  
2. Click "New +" and select "Web Service"  
3. Connect your GitHub repository  
4. Configure the service:  
   - Name: smart-edu-task-manager  
   - Root Directory: SMART Edu Task Manager  
   - Runtime: Python 3  
   - Build Command: pip install -r requirements.txt  
   - Start Command: gunicorn run:app  
   - Plan: Free  
  
### Step 3: Environment Variables  
  
In Render dashboard, add environment variable:  
- Key: SECRET_KEY  
- Value: Generate a random string (use: python -c "import secrets; print(secrets.token_hex(24))")  
  
### Step 4: Deploy  
  
Click "Create Web Service" and wait for deployment.  
  
## Notes  
  
- Free tier: Service spins down after 15 min inactivity. First request after sleep takes ~30 seconds.  
- Database: Uses SQLite by default (stored in instance folder).  
- Uploads: File uploads work but are ephemeral (lost on restart). Consider cloud storage for production. 
