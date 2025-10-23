@echo off
REM Attachment Architect - Test Connection (Windows)
REM This script activates the virtual environment and tests the Jira connection

echo ========================================
echo Attachment Architect - Test Connection
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure your credentials.
    echo.
    echo Quick fix:
    echo   1. copy .env.example .env
    echo   2. Edit .env with your Jira URL and token
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Testing connection to Jira...
echo.
python test_connection.py

echo.
pause
