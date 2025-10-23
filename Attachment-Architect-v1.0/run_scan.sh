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
python jira_dc_scanner.py "$@"

echo ""
echo "========================================"
echo "Scan Complete!"
echo "========================================"
echo ""
echo "The HTML report has been generated in the reports folder."
echo "Open the .html file in your browser to view the results."
echo ""
