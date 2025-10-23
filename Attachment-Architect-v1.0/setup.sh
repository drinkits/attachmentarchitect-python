#!/bin/bash
# Attachment Architect - Setup Script for Linux/Mac
# This script sets up the Python environment and dependencies

echo "========================================"
echo "Attachment Architect - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/5] Python found"
python3 --version
echo ""

# Create virtual environment
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
fi
echo ""

# Activate virtual environment and install dependencies
echo "[3/5] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully"
echo ""

# Create .env file if it doesn't exist
echo "[4/5] Setting up configuration..."
if [ -f ".env" ]; then
    echo ".env file already exists, skipping..."
else
    cp .env.example .env
    echo ".env file created from template"
    echo "IMPORTANT: Edit .env file with your Jira credentials!"
fi
echo ""

# Create necessary directories
echo "[5/5] Creating directories..."
mkdir -p reports scans logs
echo "Directories created"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Jira credentials"
echo "2. (Optional) Review config.yaml settings"
echo "3. Test connection: python test_connection.py"
echo "4. Run scan: python jira_dc_scanner.py"
echo ""
echo "To activate the virtual environment later, run:"
echo "  source venv/bin/activate"
echo ""
