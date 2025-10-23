@echo off
REM Setup script for Jira Data Center Attachment Analysis Tool
REM Windows version

echo ========================================
echo Jira DC Attachment Analysis Tool Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found
python --version

REM Create virtual environment
echo.
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

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Create directories
echo.
echo [5/5] Creating directories...
if not exist logs mkdir logs
if not exist scans mkdir scans
if not exist reports mkdir reports

REM Copy environment template
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo ========================================
    echo IMPORTANT: Edit .env file with your Jira credentials
    echo ========================================
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Jira credentials
echo 2. Run: python jira_dc_scanner.py
echo.
echo To activate the virtual environment later:
echo   venv\Scripts\activate.bat
echo.
pause
