@echo off
REM build_exe.bat - Build standalone executable for pwick using PyInstaller
REM Works on Windows

echo === pwick Standalone Executable Build Script ===
echo.

REM Check for Python 3
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is required but not found.
    echo Please install Python 3.9 or later and try again.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Read version from VERSION file
if exist VERSION (
    set /p VERSION=<VERSION
    echo Building pwick version: %VERSION%
) else (
    echo Warning: VERSION file not found, using default version
    set VERSION=2.4.0
)
echo.

REM Create virtual environment for build if it doesn't exist
if not exist build_venv (
    echo Creating build virtual environment...
    python -m venv build_venv
    echo Build virtual environment created.
) else (
    echo Build virtual environment already exists.
)
echo.

REM Activate virtual environment
echo Activating build virtual environment...
call build_venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install PyInstaller and dependencies
echo Installing PyInstaller and pwick dependencies...
pip install pyinstaller --quiet
pip install -e . --quiet
echo Dependencies installed.
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Previous builds cleaned.
echo.

REM Build executable
echo Building standalone executable with PyInstaller...
pyinstaller pwick.spec
echo.

REM Check if build succeeded
if exist "dist\pwick.exe" (
    echo === Build Successful ===
    echo.
    echo Standalone executable created at: dist\pwick.exe
    for %%I in (dist\pwick.exe) do echo File size: %%~zI bytes
    echo.
    echo To test the executable:
    echo   dist\pwick.exe
    echo.
    echo To create an installer, you can use tools like:
    echo   - Inno Setup: https://jrsoftware.org/isinfo.php
    echo   - NSIS: https://nsis.sourceforge.io/
    echo.
) else (
    echo === Build Failed ===
    echo Executable not found in dist\ folder.
    pause
    exit /b 1
)

REM Deactivate virtual environment
call deactivate

echo Build process complete!
pause
