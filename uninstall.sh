#!/bin/bash
# Uninstallation script for pwick on Linux/Mac

set -e

echo "======================================"
echo "  pwick Uninstallation Script"
echo "======================================"
echo ""

# Check if pwick is installed
if ! python3 -m pip show pwick &> /dev/null; then
    echo "pwick is not installed."
    exit 0
fi

echo "This will uninstall pwick from your system."
read -p "Are you sure? [y/N]: " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo ""
    echo "Uninstalling pwick..."
    python3 -m pip uninstall -y pwick
    
    echo ""
    echo "✓ pwick has been uninstalled."
    echo ""
    echo "Note: Your vault files are NOT deleted."
    echo "They remain at their saved locations."
    echo ""
else
    echo "Uninstallation cancelled."
fi
