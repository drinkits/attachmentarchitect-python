#!/bin/bash
# Attachment Architect - Run Scan (Linux/Mac)
# This script activates the virtual environment and runs the scanner

echo "========================================"
echo "Attachment Architect - Run Scan"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./setup.sh first to set up the environment."
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure your credentials."
    echo ""
    echo "Quick fix:"
    echo "  1. cp .env.example .env"
    echo "  2. Edit .env with your Jira URL and token"
    echo ""
    exit 1
fi

echo "[1/2] Activating virtual environment..."
source venv/bin/activate

echo "[2/2] Starting scan..."
echo ""

# Check for incomplete scans and auto-resume
RESUME_SCAN_ID=""
if [ -f "scans/scan.db" ]; then
    RESUME_SCAN_ID=$(python -c "import sqlite3; conn=sqlite3.connect('scans/scan.db'); cur=conn.cursor(); cur.execute('SELECT scan_id FROM scans WHERE status=\"running\" ORDER BY start_time DESC LIMIT 1'); row=cur.fetchone(); print(row[0] if row else '')" 2>/dev/null)
    # Trim whitespace
    RESUME_SCAN_ID=$(echo "$RESUME_SCAN_ID" | xargs)
fi

if [ -n "$RESUME_SCAN_ID" ] && [ "$RESUME_SCAN_ID" != "" ]; then
    echo ""
    echo "========================================"
    echo "INCOMPLETE SCAN DETECTED"
    echo "========================================"
    echo "Scan ID: $RESUME_SCAN_ID"
    echo ""
    echo "An interrupted scan was found. Would you like to:"
    echo "  [R] Resume the interrupted scan"
    echo "  [N] Start a new scan (previous scan will remain in database)"
    echo "  [D] Delete the interrupted scan and start fresh"
    echo ""
    read -p "Your choice (R/N/D): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Dd]$ ]]; then
        echo ""
        echo "Deleting interrupted scan..."
        python jira_dc_scanner.py --reset "$RESUME_SCAN_ID"
        echo ""
        echo "Starting new scan..."
        python jira_dc_scanner.py "$@"
    elif [[ $REPLY =~ ^[Nn]$ ]]; then
        echo ""
        echo "Starting new scan..."
        python jira_dc_scanner.py "$@"
    else
        echo ""
        echo "Resuming scan $RESUME_SCAN_ID..."
        python jira_dc_scanner.py --resume "$RESUME_SCAN_ID" "$@"
    fi
else
    python jira_dc_scanner.py "$@"
fi

echo ""
echo "========================================"
echo "Scan Complete!"
echo "========================================"
echo ""
echo "The HTML report has been generated in the reports folder."
echo "Open the .html file in your browser to view the results."
echo ""
