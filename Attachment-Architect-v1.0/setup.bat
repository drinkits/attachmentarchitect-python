@echo off
REM Attachment Architect - Setup Script for Windows
REM This script sets up the Python environment and dependencies

echo ========================================
echo Attachment Architect - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/5] Python found
python --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

REM Activate virtual environment and install dependencies
echo [3/5] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Create .env file if it doesn't exist
echo [4/5] Setting up configuration...
if exist .env (
    echo .env file already exists, skipping...
) else (
    copy .env.example .env
    echo .env file created from template
    echo IMPORTANT: Edit .env file with your Jira credentials!
)
echo.

REM Create necessary directories
echo [5/5] Creating directories...
if not exist reports mkdir reports
if not exist scans mkdir scans
if not exist logs mkdir logs
echo Directories created
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Jira credentials
echo 2. (Optional) Review config.yaml settings
echo 3. Test connection: python test_connection.py
echo 4. Run scan: python jira_dc_scanner.py
echo.
echo To activate the virtual environment later, run:
echo   venv\Scripts\activate.bat
echo.
pause
