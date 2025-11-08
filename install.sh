#!/bin/bash
# Installation script for pwick on Linux/Mac
# This script sets up a local environment for pwick

set -e

VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
echo "======================================"
echo "  pwick v$VERSION Local Setup Script"
echo "======================================"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3.9 or higher."
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

# Create virtual environment
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment in './$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Activate and install dependencies
echo "Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install .
deactivate

# Create launcher script
LAUNCHER_SCRIPT="run_pwick.sh"
echo "Creating launcher script './$LAUNCHER_SCRIPT'..."
cat > "$LAUNCHER_SCRIPT" << EOL
#!/bin/bash
# Launcher for pwick
# Activates the virtual environment and runs the application

# Get the directory where the script is located
DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate virtual environment and run pwick
source "\$DIR/venv/bin/activate"
python -m pwick
deactivate
EOL

chmod +x "$LAUNCHER_SCRIPT"

echo ""
echo "✓ Setup complete!"
echo ""
echo "To run pwick, execute:"
echo "  ./$LAUNCHER_SCRIPT"
echo ""
echo "To remove the local environment, run:"
echo "  ./uninstall.sh"
echo ""