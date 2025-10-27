#!/bin/bash
# Attachment Architect - Cleanup Incomplete Scans (Linux/Mac)
# This script removes all incomplete scans from the database

echo "========================================"
echo "Attachment Architect - Cleanup Scans"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./setup.sh first to set up the environment."
    echo ""
    exit 1
fi

# Check if database exists
if [ ! -f "scans/scan.db" ]; then
    echo "No scan database found. Nothing to clean up."
    echo ""
    exit 0
fi

echo "This will delete ALL incomplete scans from the database."
echo "Completed scans will NOT be affected."
echo ""
read -p "Are you sure you want to continue? (Y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Cleanup cancelled."
    echo ""
    exit 0
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "Cleaning up incomplete scans..."
python jira_dc_scanner.py --reset

echo ""
echo "========================================"
echo "Cleanup Complete!"
echo "========================================"
echo ""
echo "All incomplete scans have been removed."
echo "You can now start a fresh scan with ./run_scan.sh"
echo ""
