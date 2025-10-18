#!/bin/sh
# build.sh - POSIX-compliant build script for pwick
# Creates a virtual environment, installs dependencies, and provides run instructions

set -e

echo "=== pwick Build Script ==="
echo ""

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    . venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    . venv/Scripts/activate
else
    echo "Error: Could not find activation script."
    exit 1
fi
echo "Virtual environment activated."
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo ""

echo "=== Build Complete ==="
echo ""
echo "To run the application:"
echo ""
echo "  On Linux/Mac:"
echo "    source venv/bin/activate"
echo "    python -m src.pwick"
echo ""
echo "  On Windows:"
echo "    venv\\Scripts\\activate"
echo "    python -m src.pwick"
echo ""
