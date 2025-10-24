#!/bin/bash
# Launcher for pwick
# Activates the virtual environment and runs the application

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate virtual environment and run pwick
source "$DIR/venv/bin/activate"
python -m pwick
deactivate
