#!/bin/bash
# Setup script for Jira Data Center Attachment Analysis Tool
# Linux/Mac version

set -e

echo "========================================"
echo "Jira DC Attachment Analysis Tool Setup"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/5] Python found"
python3 --version

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created successfully"
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "[4/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo ""
echo "[5/5] Creating directories..."
mkdir -p logs
mkdir -p scans
mkdir -p reports

# Copy environment template
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "========================================"
    echo "IMPORTANT: Edit .env file with your Jira credentials"
    echo "========================================"
else
    echo ".env file already exists"
fi

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Jira credentials"
echo "2. Run: python jira_dc_scanner.py"
echo ""
echo "To activate the virtual environment later:"
echo "  source venv/bin/activate"
echo ""
