@echo off
REM Attachment Architect - Run Scan (Windows)
REM This script activates the virtual environment and runs the scanner

echo ========================================
echo Attachment Architect - Run Scan
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

echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/2] Starting scan...
echo.
python jira_dc_scanner.py %*

echo.
echo ========================================
echo Scan Complete!
echo ========================================
echo.
echo The HTML report has been generated in the reports folder.
echo Open the .html file in your browser to view the results.
echo.
pause
