#!/bin/bash
# Installation script for pwick on Linux/Mac
# This script installs pwick system-wide or in user space

set -e

echo "======================================"
echo "  pwick v1.0.0 Installation Script"
echo "======================================"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip is required but not found."
    echo "Please install pip for Python 3."
    exit 1
fi

echo ""
echo "Choose installation type:"
echo "1) User installation (recommended, no sudo required)"
echo "2) System-wide installation (requires sudo)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "Installing pwick for current user..."
        python3 -m pip install --user --upgrade .
        
        # Add user bin to PATH if not already there
        USER_BIN="$HOME/.local/bin"
        if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
            echo ""
            echo "Note: $USER_BIN is not in your PATH."
            echo "Add this line to your ~/.bashrc or ~/.profile:"
            echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
            echo ""
        fi
        
        echo ""
        echo "✓ Installation complete!"
        echo ""
        echo "To run pwick, execute:"
        echo "  pwick"
        echo ""
        ;;
    2)
        echo ""
        echo "Installing pwick system-wide..."
        sudo python3 -m pip install --upgrade .
        
        echo ""
        echo "✓ Installation complete!"
        echo ""
        echo "To run pwick, execute:"
        echo "  pwick"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo "For more information, see:"
echo "  README.md - Usage guide"
echo "  QUICKREF.md - Quick reference"
echo "  SECURITY.md - Security information"
echo ""
echo "To uninstall, run:"
echo "  pip3 uninstall pwick"
echo ""
