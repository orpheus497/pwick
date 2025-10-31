@echo off
REM Launcher for pwick
REM Activates the virtual environment and runs the application

set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%venv\Scripts\activate.bat"
python -m pwick
deactivate
