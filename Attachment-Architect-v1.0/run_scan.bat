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
set "RESUME_SCAN_ID="
if exist "scans\scan.db" (
    python -c "import sqlite3; conn=sqlite3.connect('scans/scan.db'); cur=conn.cursor(); cur.execute(\"SELECT scan_id FROM scans WHERE status='running' ORDER BY start_time DESC LIMIT 1\"); row=cur.fetchone(); print(row[0] if row else '')" > temp_resume.txt 2>nul
    if exist temp_resume.txt (
        set /p RESUME_SCAN_ID=<temp_resume.txt
        del temp_resume.txt 2>nul
    )
)

REM Trim whitespace
if defined RESUME_SCAN_ID (
    for /f "tokens=* delims= " %%a in ("%RESUME_SCAN_ID%") do set RESUME_SCAN_ID=%%a
)

REM Check if we have an incomplete scan
if not defined RESUME_SCAN_ID goto RUN_SCAN
if "%RESUME_SCAN_ID%"=="" goto RUN_SCAN

REM Show resume prompt
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
goto END

:RUN_SCAN
python jira_dc_scanner.py %*

:END
echo.
echo ========================================
echo Scan Complete!
echo ========================================
echo.
echo The HTML report has been generated in the reports folder.
echo Open the .html file in your browser to view the results.
echo.
pause
