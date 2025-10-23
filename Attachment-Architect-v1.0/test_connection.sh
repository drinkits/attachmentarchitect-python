#!/bin/bash
# Attachment Architect - Test Connection (Linux/Mac)
# This script activates the virtual environment and tests the Jira connection

echo "========================================"
echo "Attachment Architect - Test Connection"
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

echo "Activating virtual environment..."
source venv/bin/activate

echo "Testing connection to Jira..."
echo ""
python test_connection.py

echo ""
