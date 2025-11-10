#!/bin/bash
# build_exe.sh - Build standalone executable for pwick using PyInstaller
# Works on Linux and macOS

set -e

echo "=== pwick Standalone Executable Build Script ==="
echo ""

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3.9 or later and try again."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo ""

# Read version from VERSION file
if [ -f "VERSION" ]; then
    VERSION=$(cat VERSION)
    echo "Building pwick version: $VERSION"
else
    echo "Warning: VERSION file not found, using default version"
    VERSION="2.4.0"
fi
echo ""

# Create virtual environment for build if it doesn't exist
if [ ! -d "build_venv" ]; then
    echo "Creating build virtual environment..."
    python3 -m venv build_venv
    echo "Build virtual environment created."
else
    echo "Build virtual environment already exists."
fi
echo ""

# Activate virtual environment
echo "Activating build virtual environment..."
source build_venv/bin/activate
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo ""

# Install PyInstaller and dependencies
echo "Installing PyInstaller and pwick dependencies..."
pip install pyinstaller --quiet
pip install -e . --quiet
echo "Dependencies installed."
echo ""

# Check for PyInstaller spec file
if [ ! -f "pwick.spec" ]; then
    echo "Error: pwick.spec file not found."
    echo "Please ensure pwick.spec exists in the project root."
    exit 1
fi
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
echo "Previous builds cleaned."
echo ""

# Build executable
echo "Building standalone executable with PyInstaller..."
pyinstaller pwick.spec
echo ""

# Check if build succeeded
if [ -f "dist/pwick" ]; then
    echo "=== Build Successful ==="
    echo ""
    echo "Standalone executable created at: dist/pwick"
    echo "File size: $(du -h dist/pwick | cut -f1)"
    echo ""
    echo "To test the executable:"
    echo "  ./dist/pwick"
    echo ""
    echo "To install system-wide (optional):"
    echo "  sudo cp dist/pwick /usr/local/bin/"
    echo ""
else
    echo "=== Build Failed ==="
    echo "Executable not found in dist/ folder."
    exit 1
fi

# Deactivate virtual environment
deactivate

echo "Build process complete!"
