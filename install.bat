@echo off
REM Local setup script for pwick on Windows

echo ======================================
echo   pwick v1.0.0 Local Setup Script
echo ======================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not found.
    echo Please install Python 3.7 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Found Python:
python --version
echo.

REM Create virtual environment
set VENV_DIR=venv
if not exist "%VENV_DIR%" (
    echo Creating Python virtual environment in '.\%VENV_DIR%'...
    python -m venv "%VENV_DIR%"
) else (
    echo Virtual environment already exists.
)

REM Activate and install dependencies
echo Installing dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install .
deactivate

REM Create launcher script
set LAUNCHER_SCRIPT=run_pwick.bat
echo Creating launcher script '.\%LAUNCHER_SCRIPT%'...
(
    echo @echo off
    echo REM Launcher for pwick
    echo REM Activates the virtual environment and runs the application
    echo.
    echo set SCRIPT_DIR=%%~dp0
    echo call "%%SCRIPT_DIR%%venv\Scripts\activate.bat"
    echo python -m pwick
    echo deactivate
) > "%LAUNCHER_SCRIPT%"

echo.
echo ======================================
echo   Setup Complete!
echo ======================================
echo.
echo To run pwick, execute:
echo   .\%LAUNCHER_SCRIPT%
echo.
echo To remove the local environment, run:
echo   .\uninstall.bat
echo.
pause