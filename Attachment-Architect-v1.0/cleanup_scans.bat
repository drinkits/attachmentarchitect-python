@echo off
REM Attachment Architect - Cleanup Incomplete Scans (Windows)
REM This script removes all incomplete scans from the database

echo ========================================
echo Attachment Architect - Cleanup Scans
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

REM Check if database exists
if not exist scans\scan.db (
    echo No scan database found. Nothing to clean up.
    echo.
    pause
    exit /b 0
)

echo This will delete ALL incomplete scans from the database.
echo Completed scans will NOT be affected.
echo.
choice /C YN /N /M "Are you sure you want to continue? (Y/N): "

if errorlevel 2 (
    echo.
    echo Cleanup cancelled.
    echo.
    pause
    exit /b 0
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Cleaning up incomplete scans...
python jira_dc_scanner.py --reset

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo All incomplete scans have been removed.
echo You can now start a fresh scan with run_scan.bat
echo.
pause
