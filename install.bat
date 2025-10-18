@echo off
REM Installation script for pwick on Windows
REM This script installs pwick using pip

echo ======================================
echo   pwick v1.0.0 Installation Script
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

REM Check for pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is required but not found.
    echo Please ensure pip is installed with Python.
    pause
    exit /b 1
)

echo.
echo Installing pwick...
echo.

python -m pip install --upgrade .

if errorlevel 1 (
    echo.
    echo Installation failed!
    pause
    exit /b 1
)

echo.
echo ======================================
echo   Installation Complete!
echo ======================================
echo.
echo To run pwick, execute:
echo   pwick
echo.
echo Or use the Start Menu shortcut (if available).
echo.
echo For more information, see:
echo   README.md - Usage guide
echo   QUICKREF.md - Quick reference
echo   SECURITY.md - Security information
echo.
echo To uninstall, run:
echo   pip uninstall pwick
echo.
pause
