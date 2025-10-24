#!/bin/bash
# Uninstallation script for pwick on Linux/Mac

set -e

echo "======================================"
echo "  pwick Uninstallation Script"
echo "======================================"
echo ""

echo "This will remove the local pwick environment (the 'venv' directory and launcher script)."
read -p "Are you sure? [y/N]: " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo ""
    echo "Removing local environment..."
    rm -rf venv
    rm -f run_pwick.sh
    
    echo ""
    echo "✓ pwick local environment has been removed."
    echo ""
    echo "Note: Your vault files are NOT deleted."
    echo "They remain at their saved locations."
    echo ""
else
    echo "Uninstallation cancelled."
fi