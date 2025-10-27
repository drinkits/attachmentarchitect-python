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

REM Check for incomplete scans and auto-resume
python -c "import sqlite3, os; db='scans/scan.db'; print('RESUME:' + (sqlite3.connect(db).execute('SELECT scan_id FROM scans WHERE status=\"running\" ORDER BY start_time DESC LIMIT 1').fetchone()[0] if os.path.exists(db) else '')) if os.path.exists(db) else print('RESUME:')" > temp_resume.txt 2>nul
set /p RESUME_CHECK=<temp_resume.txt
del temp_resume.txt 2>nul

REM Extract scan_id from RESUME_CHECK
for /f "tokens=2 delims=:" %%a in ("%RESUME_CHECK%") do set RESUME_SCAN_ID=%%a

if not "%RESUME_SCAN_ID%"=="" (
    echo.
    echo ========================================
    echo INCOMPLETE SCAN DETECTED
    echo ========================================
    echo Scan ID: %RESUME_SCAN_ID%
    echo.
    echo An interrupted scan was found. Would you like to:
    echo   [R] Resume the interrupted scan
    echo   [N] Start a new scan (previous scan will remain in database)
    echo   [D] Delete the interrupted scan and start fresh
    echo.
    choice /C RND /N /M "Your choice (R/N/D): "
    
    if errorlevel 3 (
        echo.
        echo Deleting interrupted scan...
        python jira_dc_scanner.py --reset %RESUME_SCAN_ID%
        echo.
        echo Starting new scan...
        python jira_dc_scanner.py %*
    ) else if errorlevel 2 (
        echo.
        echo Starting new scan...
        python jira_dc_scanner.py %*
    ) else (
        echo.
        echo Resuming scan %RESUME_SCAN_ID%...
        python jira_dc_scanner.py --resume %RESUME_SCAN_ID% %*
    )
) else (
    python jira_dc_scanner.py %*
)

echo.
echo ========================================
echo Scan Complete!
echo ========================================
echo.
echo The HTML report has been generated in the reports folder.
echo Open the .html file in your browser to view the results.
echo.
pause
