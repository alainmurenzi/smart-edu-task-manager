# Complete Setup Guide for Running the SMART Edu Task Manager Project

This guide is designed for complete beginners with no coding experience. It will walk you through installing all necessary software and running the project step by step. The project is a web application for educational task management.

## Prerequisites
- A computer running Windows (this guide is written for Windows)
- Internet connection
- Administrator privileges on your computer (for installations)

## Step 1: Install Python

Python is the programming language used by this project.

1. Open your web browser and go to https://www.python.org/downloads/
2. Click the "Download Python" button (it should download the latest version, currently 3.12 or similar)
3. Once downloaded, run the installer file (python-3.x.x.exe)
4. **Important:** On the first screen of the installer, check the box that says "Add Python to PATH"
5. Click "Install Now" and follow the installation prompts
6. When installation is complete, click "Close"

To verify Python is installed:
- Open Command Prompt (search for "cmd" in Windows search)
- Type `python --version` and press Enter
- You should see something like "Python 3.12.0"

## Step 2: Install Visual Studio Code (VS Code)

VS Code is a free code editor that we'll use to run the project.

1. Open your web browser and go to https://code.visualstudio.com/
2. Click the "Download for Windows" button
3. Once downloaded, run the installer (VSCodeSetup.exe)
4. Follow the installation prompts (accept defaults)
5. When installation is complete, launch VS Code

## Step 3: Install Required VS Code Extensions

Extensions add functionality to VS Code.

1. Open VS Code
2. On the left sidebar, click the Extensions icon (it looks like four squares) or press Ctrl+Shift+X
3. In the search bar at the top, type "Python" and press Enter
4. Find "Python" by Microsoft and click "Install"
5. Next, search for "Kilo Code" in the extensions search bar
6. Find "Kilo Code" and click "Install"

## Step 4: Download and Open the Project

1. Obtain the project files (you should have received a ZIP file or folder containing the project)
2. If it's a ZIP file, extract it to a location you can easily find (like Desktop or Documents)
3. Open VS Code
4. Click "File" in the top menu, then "Open Folder"
5. Navigate to and select the project folder (it should be named "SMART Edu Task Manager")
6. Click "Select Folder"

## Step 5: Install Project Dependencies

The project needs additional software libraries.

1. In VS Code, look for a terminal panel at the bottom. If you don't see it, go to View > Terminal
2. In the terminal, make sure you're in the project directory (it should show the path ending with "SMART Edu Task Manager")
3. Type the following command and press Enter:
   ```
   pip install -r requirements.txt
   ```
4. Wait for the installation to complete (it may take a few minutes)

## Step 6: Run the Project

Now we'll use Kilo Code to run the project.

1. In VS Code, look for the Kilo Code chat panel. It should be accessible from the sidebar or a specific icon.
2. If you can't find it, try Ctrl+Shift+P to open the command palette, then type "Kilo Code" and select the chat option.
3. In the Kilo Code chat, type the following message:
   ```
   run this project
   ```
4. Press Enter or send the message
5. Kilo Code will execute the necessary commands to start the project

## Step 7: Access the Application

Once the project is running:

1. Open your web browser
2. Go to http://127.0.0.1:5000/ or http://localhost:5000/
3. You should see the SMART Edu Task Manager application

## Troubleshooting

- If you get errors during pip install, make sure Python is properly installed and added to PATH
- If VS Code can't find Python, restart VS Code after installing the Python extension
- If the project doesn't start, check the terminal for error messages and try again
- Make sure you're running commands from the correct directory (the project folder)

## What is Kilo Code?

Kilo Code is an AI assistant integrated into VS Code that helps you run and manage code projects. It can execute commands, install dependencies, and troubleshoot issues automatically, making it easier for beginners to work with code.

If you encounter any issues following this guide, try restarting VS Code and your computer, then follow the steps again.